#!/usr/bin/env python3
"""v06.2 one-variable USB tool fix: unload WCC before brcmfmac/brcmutil.

Unchanged pinned clean upstream kernel (except recompressed built-in initramfs),
DTB, Wi-Fi/BT modules and PRIVATE firmware. Works offline ONLY. Never flash.
"""
from pathlib import Path
import os,struct,gzip,hashlib,subprocess,tempfile,stat,shutil,io,difflib,json
B=Path("/home/xoomdev/xoom-linux-rom")
W=B/"clean-wifi-bt-usb-20261025"
BLD=W/"build"
K=W/"linux"
ORIG=W/"artifacts"
PREV=W/"artifacts-embedded-v061"
OUT=W/"artifacts-embedded-v062"
OUT.mkdir(exist_ok=True)
UPSTREAM="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
COMPILER=B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc"
PREFIX=B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args,**kw):
 print("RUN"," ".join(map(str,args)),flush=True)
 subprocess.run(list(map(str,args)),check=True,**kw)
assert os.geteuid()!=0
assert subprocess.check_output(["git","-C",str(K),"rev-parse","HEAD"],text=True).strip()==UPSTREAM
oldsrc=(ORIG/"v06-dashboard-bt-wifi-usb-init.c").read_bytes()
assert sha(oldsrc)=="d137f9b067e31e1a1505c90048b25a5590d63850613aa3a24a43883bfd98a8ca"
base=oldsrc.decode("utf-8")
start=base.index("static void wifi_stop(void){")
end=base.index("static void wifi_start(void){",start)
before=base[start:end]
assert before.count('SYS_delete_module')==2
assert 'brcmfmac_wcc' not in before
fix=r'''static void wifi_stop(void){
 if(upl_fd>=0){usb_send("STOP DENIED DURING UPLOAD\r\n");return;}
 /* brcmfmac_wcc holds a reference to brcmfmac, which holds brcmutil.
  * Delete in exact reverse dependency order. Do not report success if any
  * module remains busy: kernel delete_module(O_NONBLOCK) returns -EAGAIN.
  */
 long w=sc6(SYS_delete_module,(long)"brcmfmac_wcc",O_NONBLOCK,0,0,0,0);
 usb_send("WCC_STOP rc ");send_int((int32_t)w);usb_send("\r\n");
 if(w<0 && w!=-2){usb_send("WIFI_STOP ABORTED: WCC MODULE BUSY\r\n");return;}
 long a=sc6(SYS_delete_module,(long)"brcmfmac",O_NONBLOCK,0,0,0,0);
 usb_send("WIFI_STOP brcmfmac_rc ");send_int((int32_t)a);usb_send("\r\n");
 if(a<0 && a!=-2){usb_send("WIFI_STOP PARTIAL: BRCMFMAC BUSY\r\n");return;}
 long b=sc6(SYS_delete_module,(long)"brcmutil",O_NONBLOCK,0,0,0,0);
 usb_send("WIFI_STOP brcmutil_rc ");send_int((int32_t)b);usb_send("\r\n");
 if(b<0 && b!=-2){usb_send("WIFI_STOP PARTIAL: BRCMUTIL BUSY\r\n");return;}
 wifi_on=0;
 usb_send("WIFI_STOP ORDERED UNLOAD COMPLETE (CHECK WIFI_STATUS)\r\n");
}
'''
updated=base[:start]+fix+base[end:]
assert updated.count("static void wifi_stop(void){")==1
assert 'SYS_delete_module,(long)"brcmfmac_wcc"' in updated
assert updated[:start]==base[:start] and updated[start+len(fix):]==base[end:]
delta="".join(difflib.unified_diff(base.splitlines(keepends=True),updated.splitlines(keepends=True),
  fromfile="a/artifacts/v06-dashboard-bt-wifi-usb-init.c",
  tofile="b/artifacts/v06-dashboard-bt-wifi-usb-init.c"))
(OUT/"v062-WCC-unload-order-lab-only.patch").write_text(delta)
src=OUT/"v062-usb-init.c";src.write_text(updated)
binary=OUT/"init"
flags=["-std=gnu11","-Wall","-Wextra","-Werror","-Os","-fno-builtin",
"-fno-stack-protector","-fno-pie","-fno-pic","-fomit-frame-pointer",
"-marm","-mcpu=cortex-a9","-mfpu=vfpv3-d16","-mfloat-abi=hard",
"-nostdlib","-static","-Wl,-e,_start","-Wl,--build-id=none","-s"]
run([COMPILER,*flags,"-o",binary,src])
readelf=subprocess.check_output(["readelf","-A",str(binary)],text=True)
assert "NEON" not in readelf and "Advanced.SIMD" not in readelf
run(["qemu-arm","-cpu","cortex-a9,neon=off",binary])
def unpack(blob):
 pos=0;out=[]
 while True:
  assert blob[pos:pos+6]==b"070701"
  f=[int(blob[pos+6+j*8:pos+14+j*8],16) for j in range(13)]
  nstart=pos+110
  name=blob[nstart:nstart+f[11]-1].decode()
  datastart=(nstart+f[11]+3)//4*4
  data=blob[datastart:datastart+f[6]]
  pos=(datastart+f[6]+3)//4*4
  if name=="TRAILER!!!":return out
  out.append((name,f,data))
legacy=(PREV/"v061-linux-gen_init_cpio-private.cpio.gz").read_bytes()
assert sha(legacy)=="55002fc3be2379b35b7ddbe90cb21aa280610b5feb6cddb0d154ae71bb51ffbf"
entries=unpack(gzip.decompress(legacy))
assert len(entries)==26
before_payload={n.lstrip("./"):data for n,f,data in entries}
assert before_payload["init"]==(ORIG/"init").read_bytes()
gencpio=BLD/"usr/gen_init_cpio"
assert gencpio.is_file()
with tempfile.TemporaryDirectory(prefix="xoom-v062-initramfs-") as td:
 root=Path(td);listing=[]
 for name,fields,data in entries:
  safe=name.removeprefix("./")
  assert safe and not safe.startswith("/") and ".." not in safe.split("/")
  mode,uid,gid=fields[1],fields[2],fields[3]
  perm=f"{mode&0o7777:04o}"
  if stat.S_ISDIR(mode):listing.append(f"dir /{safe} {perm} {uid} {gid}")
  elif stat.S_ISREG(mode):
   p=root/safe
   p.parent.mkdir(parents=True,exist_ok=True)
   p.write_bytes(binary.read_bytes() if safe=="init" else data)
   listing.append(f"file /{safe} {p} {perm} {uid} {gid}")
  elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
   letter="c" if stat.S_ISCHR(mode) else "b"
   listing.append(f"nod /{safe} {perm} {uid} {gid} {letter} {fields[9]} {fields[10]}")
  elif stat.S_ISLNK(mode):
   listing.append(f"slink /{safe} {data.decode()} {perm} {uid} {gid}")
  else:raise RuntimeError(f"unknown mode for {name}")
 listingFile=root/"entry.list"
 listingFile.write_text("\n".join(listing)+"\n")
 raw=subprocess.check_output([str(gencpio),str(listingFile)])
 assert raw[:6]==b"070701"
 gen=unpack(raw)
 assert len(gen)==len(entries)
 gen_payload={n.lstrip("./"):data for n,f,data in gen}
 for name in before_payload:
  if name!="init":assert gen_payload[name]==before_payload[name],name
 assert gen_payload["init"]==binary.read_bytes()
 new=gzip.compress(raw,compresslevel=9,mtime=0)
 archive=OUT/"v062-embedded-radio-private.cpio.gz";archive.write_bytes(new)
 assert gzip.decompress(new)==raw
# kernel build changes only CONFIG_INITRAMFS_SOURCE path and resultant /init
config=K/"scripts/config"
run([config,"--file",BLD/".config","--set-str","INITRAMFS_SOURCE",archive,
     "--enable","BLK_DEV_INITRD","--enable","RD_GZIP",
     "--enable","INITRAMFS_COMPRESSION_GZIP"])
env={**os.environ,"ARCH":"arm","CROSS_COMPILE":str(PREFIX)}
run(["make","-s","-C",K,f"O={BLD}","olddefconfig"],env=env)
cfg=(BLD/".config").read_text()
assert f'CONFIG_INITRAMFS_SOURCE="{archive}"' in cfg
log=OUT/"v062-kernel-rebuild.log"
with log.open("w") as f:
 try:run(["make","-C",K,f"O={BLD}","-j6","zImage"],env=env,stdout=f,stderr=subprocess.STDOUT)
 except subprocess.CalledProcessError:
  print("KERNEL_BUILD_ERROR\n"+"\n".join(log.read_text().splitlines()[-60:]),flush=True);raise
assert (BLD/"usr/initramfs_inc_data").read_bytes()==archive.read_bytes()
kernel=(BLD/"arch/arm/boot/zImage").read_bytes()
dt=(BLD/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes()
original=PREV/"MZ600-CLEAN-WIFI-BT-USB-v061-BUILTIN-INITRAMFS-RAM-ONLY-UNTESTED.img"
assert sha(original.read_bytes())=="b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a"
prev=original.read_bytes();pg=2048
assert dt==prev[pg+struct.unpack_from("<I",prev,8)[0]-len(dt):pg+struct.unpack_from("<I",prev,8)[0]]
imgKernel=kernel+dt
h=bytearray(prev[:pg])
struct.pack_into("<I",h,8,len(imgKernel));struct.pack_into("<I",h,16,0)
digest=hashlib.sha1()
for data in (imgKernel,b"",b"",b""):digest.update(data);digest.update(struct.pack("<I",len(data)))
h[576:596]=digest.digest()
result=bytes(h)+imgKernel+b"\0"*(-len(imgKernel)%pg)
assert len(result)<=8388608 and result[:8]==b"ANDROID!"
out=OUT/"MZ600-CLEAN-WIFI-BT-USB-v062-WCC-UNLOAD-RAM-ONLY-UNTESTED.img"
out.write_bytes(result)
manifest={
 "status":"OFFLINE VALIDATED ONLY. NOT PHYSICALLY TESTED",
 "parent_image":"v061 embedded, physical RAM boot/WIFI_START PASS",
 "upstream":UPSTREAM,"change":"one userspace /init function: WIFI_STOP unloads WCC, brcmfmac, brcmutil in dependency order",
 "lab_patch_name":"v062-WCC-unload-order-lab-only.patch",
 "new_init_sha256":sha(binary.read_bytes()),"prior_init_sha256":sha(before_payload["init"]),
 "other_25_initramfs_entries_byte_identical":True,
 "kernel_DTB_byte_identical":True,
 "input_v061_image_sha256":sha(prev),
 "new_builtin_cpio_sha256":sha(archive.read_bytes()),
 "image_sha256":sha(result),"image_bytes":len(result),
 "kernel_dtb_sha256":sha(imgKernel),
 "never_flash_or_write_eMMC":True}
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("V062_OFFLINE_BUILT_AND_VERIFIED",len(result),sha(result),flush=True)
print("NO_DEVICE_ACCESS_NO_FLASH",flush=True)
