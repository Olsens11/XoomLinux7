#!/usr/bin/env python3
"""Offline Xoom MZ600 v06.3: add user-supplied BCM4329B1 HCD to v06.2.

Private firmware input is mandatory but is NEVER committed. Keeps kernel
sources, device tree, diagnostic /init, Wi-Fi/BT modules and boot cmdline
byte-for-byte equivalent to v06.2; only new CPIO payload is the HCD.

Never flashes/boots/contacts target.
"""
import hashlib,gzip,struct,os,stat,subprocess,tempfile,json
from pathlib import Path
B=Path("/home/xoomdev/xoom-linux-rom")
W=B/"clean-wifi-bt-usb-20261025"
BLD=W/"build";SRC=W/"linux";BASE=W/"artifacts-embedded-v062"
OUT=W/"artifacts-embedded-v063";OUT.mkdir(exist_ok=True)
FIRM=B/"private-firmware/BCM4329B1.hcd"
FIRM_SHA="7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c"
BASEIMG=BASE/"MZ600-CLEAN-WIFI-BT-USB-v062-WCC-UNLOAD-RAM-ONLY-UNTESTED.img"
BASEIMG_SHA="bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8"
BASECPIO=BASE/"v062-embedded-radio-private.cpio.gz"
CC=B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
PIN="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
def sha(b):return hashlib.sha256(b).hexdigest()
def run(*args,**kw):
 print("RUN"," ".join(map(str,args)),flush=True)
 subprocess.run([str(x) for x in args],check=True,**kw)
def cpio_entries(blob):
 pos=0;entries=[]
 while True:
  assert blob[pos:pos+6]==b"070701",(pos,"bad newc")
  f=[int(blob[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
  ns=pos+110;name=blob[ns:ns+f[11]-1].decode()
  ds=(ns+f[11]+3)//4*4
  data=blob[ds:ds+f[6]]
  pos=(ds+f[6]+3)//4*4
  if name=="TRAILER!!!":return entries
  entries.append((name.removeprefix("./"),f,data))
assert os.geteuid()!=0
assert FIRM.is_file() and FIRM.stat().st_size==17332
assert sha(FIRM.read_bytes())==FIRM_SHA
assert sha(BASEIMG.read_bytes())==BASEIMG_SHA
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip()==PIN
# Vendor HCD wire syntax: LE opcode16, payload_len8, payload. No identity
# guarantee from syntax alone, only a structural pass.
b=FIRM.read_bytes();off=0;cmds=0
while off<len(b):
 assert off+3<=len(b)
 opcode,n=struct.unpack_from("<HB",b,off);off+=3
 assert opcode in (0xfc4c,0xfc4e)
 assert off+n<=len(b)
 off+=n;cmds+=1
assert cmds==98 and off==len(b)
old=cpio_entries(gzip.decompress(BASECPIO.read_bytes()))
assert len(old)==26
oldfiles={name:(f,data) for name,f,data in old}
assert "init" in oldfiles and "lib/firmware/brcm" in oldfiles
assert "lib/firmware/brcm/BCM4329B1.hcd" not in oldfiles
native=BLD/"usr/gen_init_cpio"
assert native.is_file()
with tempfile.TemporaryDirectory(prefix="xoom-v063-hcd-") as t:
 root=Path(t);listing=[]
 for name,f,data in old:
  assert name and not name.startswith("/") and ".." not in name.split("/")
  mode,uid,gid=f[1],f[2],f[3];perm=f"{mode&0o7777:04o}"
  if stat.S_ISDIR(mode):listing.append(f"dir /{name} {perm} {uid} {gid}")
  elif stat.S_ISREG(mode):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
   listing.append(f"file /{name} {p} {perm} {uid} {gid}")
  elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
   listing.append(f"nod /{name} {perm} {uid} {gid} {'c' if stat.S_ISCHR(mode) else 'b'} {f[9]} {f[10]}")
  elif stat.S_ISLNK(mode):listing.append(f"slink /{name} {data.decode()} {perm} {uid} {gid}")
  else:raise RuntimeError("unsupported CPIO entry "+name)
 # Only new entry is the user-supplied, hash-verified candidate HCD.
 listing.append(f"file /lib/firmware/brcm/BCM4329B1.hcd {FIRM} 0644 0 0")
 manifest=root/"initramfs.list";manifest.write_text("\n".join(listing)+"\n")
 raw=subprocess.check_output([str(native),str(manifest)])
 newfiles={n:(f,data) for n,f,data in cpio_entries(raw)}
 assert len(newfiles)==27
 assert set(newfiles)==set(oldfiles)|{"lib/firmware/brcm/BCM4329B1.hcd"}
 for name,(f,data) in oldfiles.items():
  nmeta,nblob=newfiles[name]
  assert nblob==data and nmeta[1:4]==f[1:4],name
 assert newfiles["lib/firmware/brcm/BCM4329B1.hcd"][1]==b
 compressed=gzip.compress(raw,compresslevel=9,mtime=0)
 CPIO=OUT/"v063-private-bcm4329b1-firmware.cpio.gz"
 CPIO.write_bytes(compressed)
assert sha(gzip.decompress(CPIO.read_bytes()))==sha(raw)
# Single configuration item changed, other kernel config retained.
cfgbefore=(BLD/".config").read_text()
fromline=next(x for x in cfgbefore.splitlines() if x.startswith("CONFIG_INITRAMFS_SOURCE="))
assert "v062" in fromline
run(SRC/"scripts/config","--file",BLD/".config","--set-str","INITRAMFS_SOURCE",CPIO)
env={**os.environ,"ARCH":"arm","CROSS_COMPILE":str(CC)}
run("make","-s","-C",SRC,f"O={BLD}","olddefconfig",env=env)
cfgafter=(BLD/".config").read_text()
assert cfgafter.replace(f'CONFIG_INITRAMFS_SOURCE="{CPIO}"',fromline)==cfgbefore
log=OUT/"kernel-rebuild.log"
with log.open("w") as fh:
 try:run("make","-C",SRC,f"O={BLD}","-j6","zImage",env=env,stdout=fh,stderr=subprocess.STDOUT)
 except subprocess.CalledProcessError:
  print("BUILD_FAILED:\n"+"\n".join(log.read_text().splitlines()[-80:]),flush=True);raise
assert (BLD/"usr/initramfs_inc_data").read_bytes()==CPIO.read_bytes()
z=(BLD/"arch/arm/boot/zImage").read_bytes()
dt=(BLD/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes()
prev=BASEIMG.read_bytes();page=2048;oldlen=struct.unpack_from("<I",prev,8)[0]
assert oldlen>len(dt) and prev[page+oldlen-len(dt):page+oldlen]==dt
kernel=z+dt
header=bytearray(prev[:page]);struct.pack_into("<I",header,8,len(kernel));struct.pack_into("<I",header,16,0)
idsha=hashlib.sha1()
for part in (kernel,b"",b"",b""):idsha.update(part);idsha.update(struct.pack("<I",len(part)))
header[576:596]=idsha.digest()
img=bytes(header)+kernel+b"\0"*(-len(kernel)%page)
assert len(img)<=8388608,("image too large",len(img))
OUTIMG=OUT/"MZ600-CLEAN-WIFI-BT-USB-v063-HCD-RAM-ONLY-UNTESTED.img"
OUTIMG.write_bytes(img)
assert OUTIMG.read_bytes()[:8]==b"ANDROID!"
rec={"status":"OFFLINE ONLY. PHYSICAL BOOT & HCD COMPATIBILITY UNTESTED",
     "base_image_sha256":BASEIMG_SHA,"upstream_git_commit":PIN,
     "changed_only":"new initramfs member lib/firmware/brcm/BCM4329B1.hcd, all old payloads unchanged",
     "private_vendor_firmware_name":"BCM4329B1.hcd","private_vendor_firmware_sha256":FIRM_SHA,
     "private_vendor_firmware_bytes":len(b),"private_vendor_firmware_hci_commands":cmds,
     "image_name":OUTIMG.name,"image_bytes":len(img),"image_sha256":sha(img),
     "kernel_dtb_sha256":sha(kernel),"kernel_dtb_bytes":len(kernel),
     "ramdisk_external_bytes":0,"image_contains_firmware_do_not_publish":True,
     "no_device_access_no_flash":True}
(OUT/"MANIFEST.json").write_text(json.dumps(rec,indent=2)+"\n")
print("V063_PRIVATE_HCD_OFFLINE_PASS",len(img),sha(img),flush=True)
print("DO_NOT_PUBLISH_BINARY_THIS_IS_USER_SUPPLIED_FIRMWARE",flush=True)
