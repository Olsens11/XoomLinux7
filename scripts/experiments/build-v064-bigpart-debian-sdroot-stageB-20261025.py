#!/usr/bin/env python3
"""OFFLINE ONLY: BigPart-aware Linux7 + previously physically verified Debian SD-root boot.

Preserves the exact old Debian SD boot private cmdline and external ramdisk,
but uses pinned independently validated v064 BigPart kernel. No hardware
access, no partition writes, no flash. Requires independently recorded SHA.
"""
import hashlib, json, os, re, shutil, struct, subprocess
from pathlib import Path
B=Path("/home/xoomdev/xoom-linux-rom")
W=B/"clean-wifi-bt-usb-20261025"
SRC=W/"v064-bigpart-linux"
ORIG_BUILD=W/"v064-bigpart-build"
BUILD=W/"v064-bigpart-debian-sdroot-build"
OUT=W/"artifacts-embedded-v064-bigpart-debian-sdroot-stageB"
OLD_BOOT=B/"os-build/earlyboot-diagnostic-20261025/xoom-linux7-SDROOT-nonempty-ramdisk-TEMPBOOT.img"
OLD_SHA="c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c"
ROOT_IMAGE=B/"os-build/artifacts/xoom-linux-root.ext4"
ROOT_SHA="0aafdddccf58c5259007f272fb7878c417006629f5cb678c6d5e0f361ef8376e"
STAGE_A= W/"artifacts-embedded-v064-bigpart-stageA/MZ600-V064-BIGPART-GPT-READONLY-STAGE-A-TEMPBOOT.img"
STAGE_A_SHA="626e33972bff4bcb6d4bfad895397b7ff28343a781322fad68cb96836ed94cf6"
PIN="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
CC=str(B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-")
def sha(data):return hashlib.sha256(data).hexdigest()
def filehash(path):return sha(path.read_bytes())
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def run(*cmd,env=None):
 print("RUN", " ".join(map(str,cmd)),flush=True)
 subprocess.run([str(x) for x in cmd],check=True,env=env)
def roundup(n,page):return (n+page-1)//page*page
require(os.geteuid()!=0,"no sudo/root")
require(not OUT.exists() and not BUILD.exists(),"refuse overwrite old candidate")
require(OLD_BOOT.is_file() and filehash(OLD_BOOT)==OLD_SHA,"previous SD-boot SHA mismatch")
require(ROOT_IMAGE.is_file() and ROOT_IMAGE.stat().st_size==805306368 and filehash(ROOT_IMAGE)==ROOT_SHA,"Debian ext4 image mismatch")
require(STAGE_A.is_file() and filehash(STAGE_A)==STAGE_A_SHA,"stage-A kernel starting hash mismatch")
require(subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip()==PIN,"kernel provenance mismatch")
old=OLD_BOOT.read_bytes()
require(old[:8]==b"ANDROID!","boot magic")
klen,kaddr,rlen,raddr,secondlen,secondaddr,tags,page,dt_size,unused=struct.unpack_from("<10I",old,8)
require(page==2048 and klen>4000000 and rlen>0 and secondlen==0 and len(old)<8388608,"bad legacy boot")
cmdline=old[64:576].split(b"\0",1)[0]
require(b"root=PARTUUID=" in cmdline and b"rootwait" in cmdline and b"init=/sbin/init" in cmdline,"not the verified SD-root boot cmdline")
start=page+roundup(klen,page)
ramdisk=old[start:start+rlen]
require(ramdisk[:2]==b"\x1f\x8b" and len(ramdisk)==rlen,"old external gzip ramdisk missing")
require(not old[start+roundup(rlen,page):].strip(b"\0"),"unexpected trailing boot data")
# Copy the qualified v064 build tree, retaining the original stage-A output
# and its config untouched. Build only incremental delta of empty embedded CPIO.
run("cp","-a","--reflink=auto",ORIG_BUILD,BUILD)
run(SRC/"scripts/config","--file",BUILD/".config","--set-str","INITRAMFS_SOURCE","")
env={**os.environ,"ARCH":"arm","CROSS_COMPILE":CC}
run("make","-s","-C",SRC,f"O={BUILD}","olddefconfig",env=env)
config=(BUILD/".config").read_text()
require("CONFIG_MOTOROLA_XOOM_BIGPART=y" in config and 'CONFIG_INITRAMFS_SOURCE=""' in config,"config mismatch")
OUT.mkdir()
log=OUT/"compile.log"
with log.open("w") as f:
 proc=subprocess.run(["make","-C",str(SRC),f"O={BUILD}","-j6","zImage","dtbs"],env=env,stdout=f,stderr=subprocess.STDOUT)
if proc.returncode:
 print("FAILED\n"+"\n".join(log.read_text().splitlines()[-60:]),flush=True)
 raise RuntimeError("stage B build failed")
kernel= (BUILD/"arch/arm/boot/zImage").read_bytes()
dtb=(BUILD/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes()
require(dtb[:4]==bytes.fromhex("d00dfeed") and dtb== (W/"v064-bigpart-build/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes(),"DTB changed unexpectedly")
bootkernel=kernel+dtb
header=bytearray(old[:page])
struct.pack_into("<I",header,8,len(bootkernel))
struct.pack_into("<I",header,16,len(ramdisk))
idsha=hashlib.sha1()
for part in (bootkernel,ramdisk,b"",b""):
 idsha.update(part);idsha.update(struct.pack("<I",len(part)))
header[576:596]=idsha.digest()
image=bytes(header)+bootkernel+b"\0"*(roundup(len(bootkernel),page)-len(bootkernel))+ramdisk+b"\0"*(roundup(len(ramdisk),page)-len(ramdisk))
require(len(image)<=8388608,"image exceeds 8MiB boot bound")
require(image[:8]==b"ANDROID!" and image[64:576]==old[64:576],"boot layout or private root selector mutated")
out=OUT/"MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img"
out.write_bytes(image)
info={
 "class":"OFFLINE ONLY - NEVER FLASH. Requires same SD card physically present. No filesystem installed.",
 "upstream_git_commit":PIN,"bigpart_stageA_sha256":STAGE_A_SHA,
 "previous_proven_sdroot_boot_sha256":OLD_SHA,"previous_debian_root_ext4_sha256":ROOT_SHA,
 "new_image_bytes":len(image),"new_image_sha256":sha(image),
 "new_kernel_plus_dtb_bytes":len(bootkernel),"external_ramdisk_bytes":len(ramdisk),
 "config_sha256":sha(config.encode()),"embedded_initramfs_source_empty":True,
 "root_selector_preserved_from_private_proven_boot":True,
 "private_partuuid_not_logged":True,"all_10_bigpart_geometry_validation_preserved":True,
 "no_device_access_no_partition_writes":True
}
(OUT/"MANIFEST.json").write_text(json.dumps(info,indent=2)+"\n")
print("V064_BIGPART_SDBOOT_STAGE_B_OFFLINE_PASS",len(image),sha(image),flush=True)
print("NO_DEVICE_ACCESS NO_BOOT_TEST NO_FORMAT NO_FLASH",flush=True)
