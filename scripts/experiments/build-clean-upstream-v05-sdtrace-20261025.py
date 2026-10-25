#!/usr/bin/env python3
"""Build a read-only kernel baseline with SD-only early diagnostic journal.

Kernel zImage + appended DTB are copied byte-for-byte from the clean upstream
USB baseline; only the external CPIO /init changes. NEVER FLASH. No target
is connected or touched by this offline build.
"""
from pathlib import Path
import hashlib, gzip, io, json, os, struct, subprocess

B = Path("/home/xoomdev/xoom-linux-rom")
PROJECT = Path("/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project")
WORK = B / "clean-upstream-usb-20261025"
BASE = WORK / "artifacts"
OUT = WORK / "artifacts-sdlog-v05"
OUT.mkdir(exist_ok=True)
V04_SRC = (PROJECT / "src/diag-init/phase1-v04/init.c").read_bytes()
assert hashlib.sha256(V04_SRC).hexdigest() == "aaed4a0ec02ceefcc8ff89e5da89029c4ca84193bebffc28909032cb698782e2"
KERNEL = (BASE / "zImage-with-stingray-usb.dtb").read_bytes()
assert len(KERNEL) == 7860816
INITRAMFS = gzip.decompress((BASE / "phase1-v04-usb-readonly.cpio.gz").read_bytes())

LOGGER = r'''
/*
 * SD-ONLY rescue breadcrumb: write bounded kernel-ring snapshots to external
 * SD AFTER verifying /sys/block/mmcblkN/device/type is SD AND size is exactly
 * the existing test card capacity. NEVER mount Android /boot,/system,/data,
 * /cache, or write to any MMC-type device. This is diagnostic-only userspace,
 * not upstream kernel code and not the final USB tool.
 * Snapshot files alternate for resilience to interrupted writes.
 */
#define DIAG_SYS_MKDIR 39
#define DIAG_SYS_FSYNC 118
#define DIAG_O_CREAT 0x40
#define DIAG_O_TRUNC 0x200
static int diag_active = 0, diag_failed = 0, diag_num = 0;
static const char *diag_snapshot[2] = {
 "/xoomsd/XOOM-USB-BOOT-DIAG-A.log", "/xoomsd/XOOM-USB-BOOT-DIAG-B.log"
};
static int diag_starts(const char *data, const char *prefix) {
 while(*prefix) if(*data++ != *prefix++) return 0;
 return 1;
}
static int diag_file_starts(const char *path, const char *prefix) {
 char data[48];
 long fd=openf(path,O_RDONLY);
 if(fd<0)return 0;
 long n=readf(fd,data,sizeof(data)-1);
 closef(fd);
 if(n<0)return 0;
 data[n]=0;
 return diag_starts(data,prefix);
}
static void diag_try_sd(void) {
 /* The exact SD capacity is from prior user-authorized physical inspection;
  * this matching threshold deliberately rejects internal eMMC. */
 static const char *types[]={"/sys/block/mmcblk0/device/type",
                              "/sys/block/mmcblk1/device/type",
                              "/sys/block/mmcblk2/device/type"};
 static const char *sizes[]={"/sys/block/mmcblk0/size",
                              "/sys/block/mmcblk1/size",
                              "/sys/block/mmcblk2/size"};
 static const char *devs[]={"/dev/mmcblk0p1","/dev/mmcblk1p1","/dev/mmcblk2p1"};
 if(diag_active||diag_failed)return;
 for(int i=0;i<3;i++){
  if(!diag_file_starts(types[i],"SD") ||
     !diag_file_starts(sizes[i],"61067264\n"))continue;
  long dir=sc6(DIAG_SYS_MKDIR,(long)"/xoomsd",0700,0,0,0,0);
  (void)dir;
  long rc=mountf(devs[i],"/xoomsd","ext4",MS_NOSUID|MS_NODEV);
  if(rc<0){echo("xoom-diag: external SD ext4 mount failed\n");return;}
  diag_active=1;
  echo("xoom-diag: EXTERNAL_SD_LOGGING_ACTIVE, no internal mounts\n");
  return;
 }
}
static void diag_snapshot_ring(unsigned long secs){
 if(!diag_active)return;
 static char kern[32768];
 long n=sc6(SYS_syslog,3,(long)kern,sizeof(kern),0,0,0);
 if(n<=0){echo("xoom-diag: syslog failed\n");return;}
 long fd=sc6(SYS_open,(long)diag_snapshot[diag_num&1],
   O_WRONLY|DIAG_O_CREAT|DIAG_O_TRUNC,0600,0,0,0);
 if(fd<0){echo("xoom-diag: write failed; external SD only\n");diag_failed=1;return;}
 const char head[]="XOOM CLEAN LINUX 7 v05 EXTERNAL SD BREADCRUMB\n";
 const char phase[]="KERNEL RING SNAPSHOT (private; contains hardware IDs)\n";
 writef(fd,head,sizeof(head)-1);
 writef(fd,phase,sizeof(phase)-1);
 writef(fd,utoa(secs),slen(utoa(secs)));
 writef(fd,"\n",1);
 if(n>(long)sizeof(kern))n=sizeof(kern);
 long done=0;
 while(done<n) {
  long k=writef(fd,kern+done,n-done);
  if(k<=0){echo("xoom-diag: short write\n");break;}
  done+=k;
 }
 long ok=sc6(DIAG_SYS_FSYNC,fd,0,0,0,0,0);
 closef(fd);
 if(ok<0)echo("xoom-diag: fsync failed\n");
 diag_num++;
}
'''
src=V04_SRC.decode("utf-8")
anchor="static void run_init(void){"
assert src.count(anchor)==1
src=src.replace(anchor,LOGGER+"\n"+anchor,1)
anchor2="   if(fbfd<0)framebuffer();\n   if(screen)dashboard(seconds);"
assert src.count(anchor2)==1
src=src.replace(anchor2,
    '   if(seconds<=90 && !diag_active && !diag_failed)diag_try_sd();\n'
    '   if(diag_active)diag_snapshot_ring(seconds);\n'+anchor2,1)
assert "diag_snapshot_ring(seconds);" in src
srcfile=OUT/"v05-sdlog-init.c"
srcfile.write_text(src)
CC=B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc"
INIT=OUT/"init"
flags=["-std=gnu11","-Wall","-Wextra","-Werror","-Os","-fno-builtin",
       "-fno-stack-protector","-fno-pie","-fno-pic","-fomit-frame-pointer",
       "-marm","-mcpu=cortex-a9","-mfpu=vfpv3-d16","-mfloat-abi=hard",
       "-nostdlib","-static","-Wl,-e,_start","-Wl,--build-id=none","-s"]
subprocess.run([str(CC),*flags,"-o",str(INIT),str(srcfile)],check=True)
readelf=subprocess.run(["readelf","-A",str(INIT)],capture_output=True,text=True,check=True).stdout
assert "NEON" not in readelf and "Advanced.SIMD" not in readelf
subprocess.run(["qemu-arm","-cpu","cortex-a9,neon=off",str(INIT)],check=True)
assert INIT.read_bytes()[:4]==b"\x7fELF"

def parse_cpio(blob):
    off=0
    result=[]
    while True:
        assert blob[off:off+6]==b"070701"
        fields=[int(blob[off+6+i*8:off+14+i*8],16) for i in range(13)]
        namestart=off+110
        name=blob[namestart:namestart+fields[11]-1].decode()
        datastart=(namestart+fields[11]+3)//4*4
        data=blob[datastart:datastart+fields[6]]
        off=(datastart+fields[6]+3)//4*4
        if name=="TRAILER!!!":break
        result.append((name,fields,data))
    return result
entries=parse_cpio(INITRAMFS)
assert sum(1 for n,_,_ in entries if n=="init")==1
buf=io.BytesIO()
def put(name,fields,data):
    f=list(fields)
    f[6]=len(data)
    f[11]=len(name.encode())+1
    buf.write(b"070701"+b"".join(("%08X"%x).encode() for x in f))
    buf.write(name.encode()+b"\x00")
    buf.write(b"\0"*(-buf.tell()%4))
    buf.write(data)
    buf.write(b"\0"*(-buf.tell()%4))
for name,fields,data in entries:
    if name=="init": data=INIT.read_bytes()
    put(name,fields,data)
put("TRAILER!!!",[len(entries)+1,0,0,0,1,0,0,0,0,0,0,11,0],b"")
compressed=gzip.compress(buf.getvalue(),compresslevel=9,mtime=0)
assert gzip.decompress(compressed)[:6]==b"070701"
RAM=OUT/"v05-sdlog-initramfs.cpio.gz"
RAM.write_bytes(compressed)
old=BASE/"MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img"
original=old.read_bytes()
assert hashlib.sha256(original).hexdigest()=="da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b"
kl,ka,rl,ra,ss,sa,ta,page,ds,zero=struct.unpack_from("<10I",original,8)
assert (kl,ka,ra,ss,sa,ta,page,ds)==(len(KERNEL),0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
assert original[page:page+kl] == KERNEL
assert original[page+((kl+page-1)//page)*page:page+((kl+page-1)//page)*page+rl] == (BASE/"phase1-v04-usb-readonly.cpio.gz").read_bytes()
header=bytearray(original[:page])
struct.pack_into("<I",header,16,len(compressed))
h=hashlib.sha1()
for piece in (KERNEL,compressed,b"",b""):
    h.update(piece)
    h.update(struct.pack("<I",len(piece)))
header[576:596]=h.digest()
payload=bytes(header)+KERNEL+b"\0"*((-len(KERNEL))%page)+compressed+b"\0"*((-len(compressed))%page)
assert len(payload)<=8388608, "ROM image exceeds 8 MiB boot limit"
assert payload[:8]==b"ANDROID!"
IMAGE=OUT/"MZ600-CLEAN-UPSTREAM-V05-SD-BREADCRUMB-RAM-ONLY.img"
IMAGE.write_bytes(payload)
sha=lambda blob:hashlib.sha256(blob).hexdigest()
manifest={
 "purpose":"earlyboot SD-ONLY breadcrumbs, kernel and DTB identical to clean v04",
 "provenance":"xoom-linux 2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3",
 "kernel_dtb_sha256":sha(KERNEL),
 "kernel_identical_to_v04":True,
 "userland_v04_sha256":sha(V04_SRC),
 "userland_v05_sha256":sha(src.encode()),
 "external_sd_writes":"only SD card exactly 61067264 sectors, matched /sys/block/.../device/type SD; alternating two XOOM-USB-BOOT-DIAG logs in ext4 root",
 "emmc_or_android_writes":"NEVER",
 "status":"OFFLINE BUILT NOT PHYSICALLY TESTED",
 "image":IMAGE.name,
 "image_bytes":len(payload),
 "image_sha256":sha(payload),
 "initramfs_sha256":sha(compressed)}
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("V05_EXACT_CLEAN_KERNEL_SDLOG_CPIO_BUILD_PASS", IMAGE, len(payload),sha(payload),flush=True)
