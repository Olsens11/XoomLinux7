#!/usr/bin/env python3
"""Rebuild clean Linux v06 with the exact radio USB filesystem EMBEDDED.

Corrects external rdinit/initramfs uncertainty in physical v06: kernel clearly
executed and enumerated eMMC but could not find /init in initial rootfs.

This is an offline build. Original working v04, v06 external, original eMMC and
all factory OS partitions remain unchanged. NEVER flash boot.
"""
import os, pathlib, subprocess, shutil, struct, hashlib, json, gzip, tempfile
P=pathlib.Path
BASE=P("/home/xoomdev/xoom-linux-rom")
WORK=BASE/"clean-wifi-bt-usb-20261025"
SRC=WORK/"linux"
BLD=WORK/"build"
OUT=WORK/"artifacts-embedded-v061"
ART=WORK/"artifacts"
V06=ART/"MZ600-CLEAN-WIFI-BT-USB-v06-RAM-ONLY-UNTESTED.img"
RAW=ART/"v06-private-radio-usb.cpio.gz"
PIN="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
CC=BASE/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
assert os.geteuid()!=0
def run(*args,**kwargs):
 print("RUN"," ".join(map(str,args)),flush=True)
 subprocess.run(list(map(str,args)),check=True,**kwargs)
def sha(b):return hashlib.sha256(b).hexdigest()
assert V06.is_file() and RAW.is_file()
assert sha(V06.read_bytes())=="c8240c65bf43064b82acec516ffc863e819db314e6f5fa0033586241390e00e9"
assert sha(RAW.read_bytes())=="a1d215790758808666314ca2e6a7cc55b91464ed241fcd6d0ad3168679ed6f41"
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip()==PIN
OUT.mkdir(parents=True,exist_ok=True)
# Re-serialize with Linux kernel's OWN gen_init_cpio tool (not custom packer).
# The source archive contains character device nodes; extracting these on a
# non-root build host is invalid. Extract regular files to a tempdir and
# encode dirs and special devices by their original cpio mode/rdev metadata.
import stat
def read_entries(blob):
 entries=[];pos=0
 while True:
  assert blob[pos:pos+6]==b"070701",(pos,blob[pos:pos+6])
  f=[int(blob[pos+6+j*8:pos+14+j*8],16) for j in range(13)]
  nstart=pos+110
  name=blob[nstart:nstart+f[11]-1].decode()
  ds=(nstart+f[11]+3)//4*4
  data=blob[ds:ds+f[6]]
  pos=(ds+f[6]+3)//4*4
  if name=="TRAILER!!!":break
  entries.append((name,f,data))
 return entries
original_entries=read_entries(gzip.decompress(RAW.read_bytes()))
assert len(original_entries)==26
gencpio=BLD/"usr/gen_init_cpio"
assert gencpio.is_file()
with tempfile.TemporaryDirectory(prefix="xoom-v061-kernel-cpio-") as t:
 td=P(t)
 listing=[]
 for name,f,data in original_entries:
  clean=name.removeprefix("./")
  assert clean and not clean.startswith("/") and ".." not in clean.split("/")
  mode=f[1];uid=f[2];gid=f[3];perms=f"{mode & 0o7777:04o}"
  target="/"+clean
  if stat.S_ISDIR(mode):
   listing.append(f"dir {target} {perms} {uid} {gid}")
  elif stat.S_ISREG(mode):
   path=td/clean
   path.parent.mkdir(parents=True,exist_ok=True)
   path.write_bytes(data)
   listing.append(f"file {target} {path} {perms} {uid} {gid}")
  elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
   k="c" if stat.S_ISCHR(mode) else "b"
   listing.append(f"nod {target} {perms} {uid} {gid} {k} {f[9]} {f[10]}")
  elif stat.S_ISLNK(mode):
   listing.append(f"slink {target} {data.decode()} {perms} {uid} {gid}")
  else:raise RuntimeError(f"Unexpected inode type for {name}")
 assert any(x.startswith("nod /dev/console ") for x in listing)
 assert any(x.startswith("nod /dev/null ") for x in listing)
 assert any(x.startswith("file /init ") for x in listing)
 manifest=td/"initramfs.list"
 manifest.write_text("\n".join(listing)+"\n")
 generated=subprocess.run([str(gencpio),str(manifest)],capture_output=True,check=True).stdout
 assert generated[:6]==b"070701"
 cpio_files=read_entries(generated)
 assert len(cpio_files)==len(original_entries)
 files={n.removeprefix("./"):data for n,f,data in cpio_files}
 orig={n.removeprefix("./"):data for n,f,data in original_entries}
 assert files==orig, "CPIO payload changed; refuse embedding"
 assert next(f[1] for n,f,data in cpio_files if n=="init")&0o111
 out=gzip.compress(generated,compresslevel=9,mtime=0)
 embsrc=OUT/"v061-linux-gen_init_cpio-private.cpio.gz"
 embsrc.write_bytes(out)
 assert len(out)>500000
# Save original v06 external-ramdisk config/zImage and isolate them from
# the embedded variant before updating kernel output for one-variable test.
original_config=ART/"kernel.config"
assert original_config.is_file()
snapshot=OUT/"v06-original-external-kernel.config"
if not snapshot.exists(): shutil.copyfile(original_config,snapshot)
original_z=BLD/"arch/arm/boot/zImage"
assert original_z.is_file()
shutil.copyfile(original_z,OUT/"v06-original-external-kernel-zImage")
config=SRC/"scripts/config"
run(config,"--file",BLD/".config",
    "--enable","BLK_DEV_INITRD","--enable","RD_GZIP",
    "--set-str","INITRAMFS_SOURCE",str(embsrc),
    "--enable","INITRAMFS_COMPRESSION_GZIP")
env={**os.environ,"ARCH":"arm","CROSS_COMPILE":str(CC)}
run("make","-s","-C",SRC,f"O={BLD}","olddefconfig",env=env)
cfg=(BLD/".config").read_text()
assert f'CONFIG_INITRAMFS_SOURCE="{embsrc}"' in cfg
assert "CONFIG_BLK_DEV_INITRD=y" in cfg
assert "CONFIG_RD_GZIP=y" in cfg
log=OUT/"embedded-kernel-build.log"
with log.open("w") as f:
 try:run("make","-C",SRC,f"O={BLD}","-j6","zImage",env=env,stdout=f,stderr=subprocess.STDOUT)
 except subprocess.CalledProcessError:
  print("EMBEDDED_BUILD_FAILED\n"+"\n".join(log.read_text().splitlines()[-90:]),flush=True)
  raise
k=original_z.read_bytes()
dt=(BLD/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes()
assert sha(dt)==sha((WORK/"artifacts"/"zImage-with-stingray-wifi-bt.dtb").read_bytes()[-len(dt):])
embedded_usr=BLD/"usr/initramfs_data.cpio.gz"
assert embedded_usr.is_file(), "no generated built-in initramfs"
c=embedded_usr.read_bytes()
assert c.startswith(b"\x1f\x8b")
assert len(gzip.decompress(c))>1000000
assert b"070701"==gzip.decompress(c)[:6]
assert b"./init\x00" in gzip.decompress(c)[:20000] or b"init\x00" in gzip.decompress(c)[:20000]
baseline=V06.read_bytes()
page=2048
header=bytearray(baseline[:page])
kl,ka,rl,ra,ss,sa,ta,pg,ds,unused=struct.unpack_from("<10I",header,8)
assert (ka,ra,pg)==(0x10008000,0x11000000,2048)
kernel=k+dt
struct.pack_into("<I",header,8,len(kernel))
struct.pack_into("<I",header,16,0)   # NO external ramdisk handoff required
h=hashlib.sha1()
for part in (kernel,b"",b"",b""):
 h.update(part);h.update(struct.pack("<I",len(part)))
header[576:596]=h.digest()
boot=bytes(header)+kernel+b"\0"*(-len(kernel)%page)
assert len(boot)<=8388608,f"BUILTIN_IMAGE_EXCEEDS_8MB {len(boot)}"
outfile=OUT/"MZ600-CLEAN-WIFI-BT-USB-v061-BUILTIN-INITRAMFS-RAM-ONLY-UNTESTED.img"
outfile.write_bytes(boot)
manifest={
 "status":"OFFLINE ONLY - NO PHYSICAL BOOT",
 "image_name":outfile.name,"image_size":len(boot),"image_sha256":sha(boot),
 "kernel_dtb_bytes":len(kernel),"kernel_dtb_sha256":sha(kernel),
 "kernel_source":"original upstream source commit + previously-proven MAC ATAG patch, exact original v06 DTS",
 "change_from_v06":"GNU-cpio reserialize and embedded initramfs instead of external ramdisk; WiFi BT USB identical binaries",
 "external_ramdisk_bytes":0,"embedded_archive_sha256":sha(c),
 "embedded_archive_uncompressed_bytes":len(gzip.decompress(c)),
 "compiled_init_exists_in_embed":True,
 "risk":"never flash; radio bringup disabled by default; no OS or SD mounts; no bootloader writes"}
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("V061_BUILTIN_INITRAMFS_OFFLINE_PASS",len(boot),sha(boot),flush=True)
print("STOCK_V04_AND_V06_UNMODIFIED_EXTERNAL_IMAGES_PRESERVED",flush=True)
