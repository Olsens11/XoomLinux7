#!/usr/bin/env python3
"""Offline v06: existing proven USB v034 lab + default v04 dashboard with BT row.

Uses EXACT freshly-built modules of isolated upstream clean Linux kernel, and
the user's existing PRIVATE RAM-only firmware and calibration. Does not run
modifications on Xoom, eMMC, SD or radio. Builds a boot image, NEVER flashes.
"""
from pathlib import Path
import subprocess,hashlib,gzip,io,struct,json,os
B=Path("/home/xoomdev/xoom-linux-rom")
PROJECT=B/"clean-upstream-usb-20261025/project"
WORK=B/"clean-wifi-bt-usb-20261025"
OBJ=WORK/"build"
OUT=WORK/"artifacts"
SRC=PROJECT/"src/diag-init/phase1-v034/init.c"
V04=PROJECT/"src/diag-init/phase1-v04/init.c"
CPIO=B/"phase1-v033/phase1-v033-initramfs.cpio.gz"
KERNEL=OUT/"zImage-with-stingray-wifi-bt.dtb"
TOOLCHAIN=B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc"
assert all(x.is_file() for x in (SRC,V04,CPIO,KERNEL,TOOLCHAIN))
OUT.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
s=SRC.read_text()
a=V04.read_text()
# Reuse exact screen design from physically successful no-SD v04 USB build.
i=a.index("static void dashboard(unsigned long seconds){")
j=a.index("static void framebuffer(void){",i)
display=a[i:j]
display=display.replace('text(42,y,"BATTERY",2,white);',
  'text(42,y,"BLUETOOTH",2,white);\n'
  ' text(290,y,present("/sys/class/bluetooth/hci0")?"HCI0 ACTIVE":"NOT ACTIVE",2,amber);y+=step;\n'
  ' text(42,y,"BATTERY",2,white);')
assert '"BLUETOOTH"' in display
assert 'static void dashboard(' not in s
# v034's original touch-grid is still accessible through separate USB command.
# Default display is the original verified dashboard; no touch impacts it.
marker="#define GRID_COLS 8"
assert s.count(marker)==1
s=s.replace(marker,"static int dashboard_mode=1;\n"+marker,1)
marker="static void framebuffer(void){"
assert s.count(marker)==1
s=s.replace(marker,display+"\n"+marker,1)
assert s.count("grid_scene();")>=1
s=s.replace("grid_scene();", "grid_scene();\n dashboard(0);",1)
marker="if(screen)grid_uptime(seconds);"
assert s.count(marker)==1
s=s.replace(marker,"if(screen){if(dashboard_mode)dashboard(seconds);else grid_uptime(seconds);}",1)
marker="static void grid_touch_update(int rawx,int rawy,int down){"
assert s.count(marker)==1
s=s.replace(marker,marker+"\n if(dashboard_mode)return;",1)
marker='else if(equals(cmd,"GRID")){'
assert s.count(marker)==1
s=s.replace(marker,'''else if(equals(cmd,"GRID SHOW")){dashboard_mode=0;grid_scene();usb_send("GRID ENABLED\\\\r\\\\n");}
 else if(equals(cmd,"GRID HIDE")){dashboard_mode=1;dashboard(0);usb_send("DASHBOARD ENABLED\\\\r\\\\n");}
 '''+marker,1)
# Allow only WCC vendor module in same already-enforced fixed-path RAM upload.
marker='}else if(p[0]==\\'F\\' && p[1]==\\'I\\' && p[2]==\\'R\\' && p[3]==\\'M\\' &&'
assert s.count(marker)==1
s=s.replace(marker,''' }else if(p[0]=='W' && p[1]=='C' && p[2]=='C' && p[3]==' '){
  upl_target="/run/brcmfmac-wcc.ko";type=p+4;
 '''+marker,1)
(OUT/"v06-dashboard-bt-wifi-usb-init.c").write_text(s)
def run(args):
 print("RUN"," ".join(map(str,args)),flush=True)
 subprocess.run(list(map(str,args)),check=True)
INIT=OUT/"init"
flags=["-std=gnu11","-Wall","-Wextra","-Werror","-Os","-fno-builtin",
"-fno-stack-protector","-fno-pie","-fno-pic","-fomit-frame-pointer",
"-marm","-mcpu=cortex-a9","-mfpu=vfpv3-d16","-mfloat-abi=hard",
"-nostdlib","-static","-Wl,-e,_start","-Wl,--build-id=none","-s"]
run([TOOLCHAIN,*flags,"-o",INIT,OUT/"v06-dashboard-bt-wifi-usb-init.c"])
readelf=subprocess.check_output(["readelf","-A",str(INIT)],text=True)
assert "NEON" not in readelf and "Advanced.SIMD" not in readelf
run(["qemu-arm","-cpu","cortex-a9,neon=off",str(INIT)])
# WCC request_module helper: the kernel expects /sbin/modprobe.
# This tiny ARM ELF handles ONLY brcmfmac-wcc and only the fixed /wifi path.
# No shell, no arbitrary host-provided module path or command execution.
MODPROBE=r'''
static long call(long n,long a,long b,long c){
 register long r0 asm("r0")=a,r1 asm("r1")=b,r2 asm("r2")=c,r7 asm("r7")=n;
 asm volatile("svc 0":"+r"(r0):"r"(r1),"r"(r2),"r"(r7):"memory","cc");
 return r0;
}
static int eq(const char *a,const char *b){while(*a&&*b&&*a==*b){a++;b++;}return *a==*b;}
static int main0(unsigned long *sp){
 int n=(int)*sp;char **v=(char**)(sp+1);
 if(n<2||n>24)return 1;
 int ok=0;
 for(int i=1;i<n;i++)if(eq(v[i],"brcmfmac-wcc"))ok=1;
 if(!ok)return 2;
 long fd=call(5,(long)"/run/brcmfmac-wcc.ko",0,0);
 if(fd<0)fd=call(5,(long)"/wifi/brcmfmac-wcc.ko",0,0);
 if(fd<0)return 3;
 long result=call(379,fd,(long)"",0);
 call(6,fd,0,0);
 return (result==0 || result==-17)?0:4;
}
__attribute__((naked,noreturn))void _start(void){
 asm volatile("mov r0, sp\\n bl main0\\n mov r7, #1\\n svc 0\\n 1: b 1b");
}
'''
(OUT/"modprobe-wcc.c").write_text(MODPROBE)
MP=OUT/"modprobe"
run([TOOLCHAIN,*flags,"-o",MP,OUT/"modprobe-wcc.c"])
assert "NEON" not in subprocess.check_output(["readelf","-A",str(MP)],text=True)
# Test the executable does not load modules on the host; it should exit
# nonzero without matching arguments. Its successful path is not QEMU-tested.
t=subprocess.run(["qemu-arm","-cpu","cortex-a9,neon=off",str(MP)],capture_output=True,timeout=10)
assert t.returncode!=0
def cpio_entries(data):
 result=[];pos=0
 while True:
  assert data[pos:pos+6]==b"070701"
  fields=[int(data[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
  start=pos+110
  name=data[start:start+fields[11]-1].decode()
  content=(start+fields[11]+3)//4*4
  blob=data[content:content+fields[6]]
  pos=(content+fields[6]+3)//4*4
  if name=="TRAILER!!!":break
  result.append((name,fields,blob))
 return result
entries=cpio_entries(gzip.decompress(CPIO.read_bytes()))
assert len(entries)==23 and sum(n=="init" for n,f,d in entries)==1
# Repackage from exact private v033 reference firmware without publishing
# proprietary contents, user-specific bytes, or replacing the stock kernel.
mapped={
 "init":INIT.read_bytes(),
 "wifi/brcmfmac.ko":(OBJ/"drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko").read_bytes(),
 "wifi/brcmutil.ko":(OBJ/"drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko").read_bytes(),
}
btmodules={
 "bt/bluetooth.ko":"net/bluetooth/bluetooth.ko",
 "bt/btbcm.ko":"drivers/bluetooth/btbcm.ko",
 "bt/hci_uart.ko":"drivers/bluetooth/hci_uart.ko",
 "bt/ecc.ko":"crypto/ecc.ko",
 "bt/ecdh_generic.ko":"crypto/ecdh_generic.ko",
 "bt/cmac.ko":"crypto/cmac.ko",
}
for dest,rel in btmodules.items():
 path=OBJ/rel
 assert path.is_file(),f"Missing clean BT module {rel}"
 mapped[dest]=path.read_bytes()
wcc=(OBJ/"drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko").read_bytes()
assert wcc[:4]==b"\x7fELF"
names={x[0] for x in entries}
assert set(mapped).issubset(names)
for name,f,data in entries:
 if name in mapped:data=mapped[name]
 if name=="init": assert b"XOOM LINUX" in data
def emit(name,fields,data):
 f=list(fields);f[6]=len(data);f[11]=len(name.encode())+1
 out.write(b"070701"+b"".join(("%08X"%n).encode() for n in f))
 out.write(name.encode()+b"\0")
 out.write(b"\0"*(-out.tell()%4));out.write(data);out.write(b"\0"*(-out.tell()%4))
out=io.BytesIO()
for name,f,data in entries:
 emit(name,f,mapped.get(name,data))
def add(name,data,mode,uid=0):
 # cpio newc mode, nlink, mtime, inode deliberately fixed for reproducible cpio
 fields=[1000+len(name),mode,uid,0,1,0,len(data),0,0,0,0,len(name)+1,0]
 emit(name,fields,data)
add("wifi/brcmfmac-wcc.ko",wcc,0o100644)
add("sbin",b"",0o040755)
add("sbin/modprobe",MP.read_bytes(),0o100755)
emit("TRAILER!!!",[len(entries)+1005,0,0,0,1,0,0,0,0,0,0,11,0],b"")
ram=gzip.compress(out.getvalue(),compresslevel=9,mtime=0)
assert len(cpio_entries(gzip.decompress(ram)))==len(entries)+3
(OUT/"v06-private-radio-usb.cpio.gz").write_bytes(ram)
kernel=KERNEL.read_bytes()
# Legacy Android-format boot container from frozen baseline; only new
# source-built compressed zImage/DTB + private initramfs change, no flash.
baseline=(B/"clean-upstream-usb-20261025/artifacts/MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img").read_bytes()
assert sha(baseline)=="da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b"
page=2048
hdr=bytearray(baseline[:page])
assert hdr[:8]==b"ANDROID!"
struct.pack_into("<I",hdr,8,len(kernel))
struct.pack_into("<I",hdr,16,len(ram))
hash0=hashlib.sha1()
for section in (kernel,ram,b"",b""):
 hash0.update(section);hash0.update(struct.pack("<I",len(section)))
hdr[576:596]=hash0.digest()
blob=bytes(hdr)+kernel+b"\0"*(-len(kernel)%page)+ram+b"\0"*(-len(ram)%page)
if len(blob)>8388608:
 raise RuntimeError(f"BOOT_IMAGE_TOO_LARGE={len(blob)} bytes; keep v04 baseline untouched. Need smaller clean config.")
IMAGE=OUT/"MZ600-CLEAN-WIFI-BT-USB-v06-RAM-ONLY-UNTESTED.img"
IMAGE.write_bytes(blob)
manifest={
 "status":"OFFLINE ONLY - NO PHYSICAL BOOT","upstream":"xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3",
 "board_source":"exact stable no-SD v04 DTB source, with per-device ATAG WLAN MAC kernel bridge",
 "config":"earlier physically proven OS reference config on unmodified upstream, not current v04 config",
 "usb":"known v034 USB protocol + verified v04 default dashboard with Wi-Fi AND Bluetooth rows",
 "wireless":"original brcmfmac + brcmutil + wcc modules; WCC kernel request_module ELF helper; explicit start only",
 "bluetooth":"earlier v034 opt-in BT commands and clean-source dependent modules; dashboard hci0 detection",
 "radio":"NO RF SCAN/ASSOCIATION; no default module activation; firmware and NVRAM private only",
 "factory":"no eMMC, SD, bootloader writes or flashes",
 "bytes":len(blob),"sha256":sha(blob),"kernel_sha256":sha(kernel),
 "ramdisk_sha256":sha(ram),"usb_init_sha256":sha(INIT.read_bytes())}
(OUT/"v06-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("CLEAN_WIFI_BT_USB_V06_OFFLINE_IMAGE_PASS",len(blob),sha(blob),flush=True)
