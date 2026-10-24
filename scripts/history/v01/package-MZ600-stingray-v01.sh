#!/usr/bin/env bash
# MZ600 Stingray RAM-only diagnostic kernel image.
# BOOT partition on target will NOT be touched; user has broken volume-down.
set -euo pipefail
umask 022
B=/home/xoomdev/xoom-linux-rom
D=/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v01
K=$B/build-wingray-gcc14-initramfs/arch/arm/boot/zImage
DT=$B/build-wingray-gcc14-initramfs/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dtb
RAM=$B/phase1/phase1-initramfs.cpio.gz
EMBEDDED=$B/build-wingray-gcc14-initramfs/usr/initramfs_inc_data
MK=/home/xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg
mkdir -p "$D"
test -s "$K" && test -s "$DT" && test -s "$RAM" && test -s "$MK"
cmp "$RAM" "$EMBEDDED"
cat "$K" "$DT" > "$D/stingray-zImage-appended-dtb.bin"
cp "$DT" "$D/tegra20-motorola-stingray.dtb"
cp "$B/linux-src/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dts" "$D/tegra20-motorola-stingray.dts"
cp "$B/phase1/initramfs/init-freestanding" "$D/init-freestanding-armv7-noNEON"
cp "$RAM" "$D/phase1-initramfs.cpio.gz"
cp /mnt/c/Users/olsen/XoomLinux/Phase1/create-stingray-derivative.py "$D/"
cp /mnt/c/Users/olsen/XoomLinux/Phase1/build-internal-initramfs-v02.sh "$D/"
CMD='androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=4 printk.time=1 rdinit=/init'
python3 "$MK" --kernel "$D/stingray-zImage-appended-dtb.bin" --ramdisk "$RAM" --pagesize 2048 --base 0x10000000 --kernel_offset 0x00008000 --ramdisk_offset 0x01000000 --second_offset 0x00f00000 --tags_offset 0x00000100 --cmdline "$CMD" --output "$D/MZ600-stingray-RAM-only-diagnostic-NOT-FLASHABLE-UNTIL-VERIFIED.img"
python3 - "$D" <<'PY'
from pathlib import Path
import sys,hashlib,struct,gzip,json
p=Path(sys.argv[1]);i=p/'MZ600-stingray-RAM-only-diagnostic-NOT-FLASHABLE-UNTIL-VERIFIED.img'
b=i.read_bytes()
assert b[:8]==b'ANDROID!'
v=struct.unpack_from('<10I',b,8)
klen,kaddr,rlen,raddr,seclen,secondaddr,tags,page,dtlen,_=v
assert (kaddr,raddr,secondaddr,tags,page)==(0x10008000,0x11000000,0x10f00000,0x10000100,2048)
assert not seclen and not dtlen
assert klen==len((p/'stingray-zImage-appended-dtb.bin').read_bytes())
assert b[page:page+klen]==(p/'stingray-zImage-appended-dtb.bin').read_bytes()
ramoff=page+(klen+page-1)//page*page
ram=b[ramoff:ramoff+rlen]
assert ram==(p/'phase1-initramfs.cpio.gz').read_bytes()
assert gzip.decompress(ram).startswith(b'070701')
assert len(b)<8*1024*1024 and len(b)<12*1024*1024
assert (p/'tegra20-motorola-stingray.dtb').read_bytes()[:4]==bytes.fromhex('d00dfeed')
d=hashlib.sha1()
for x in (b[page:page+klen],ram,b'',b''):
 d.update(x);d.update(struct.pack('<I',len(x)))
assert b[576:596]==d.digest()
cmdline=b[64:576].split(b'\0')[0].decode()
assert 'rdinit=/init' in cmdline and 'modelno=MZ600' in cmdline
files=[]
for f in p.iterdir():
 if f.is_file():
  z=f.read_bytes()
  files.append(dict(name=f.name,size=len(z),sha256=hashlib.sha256(z).hexdigest()))
(p/'manifest.json').write_text(json.dumps({'device':'Motorola Xoom MZ600 (Stingray)','target_serial':'170061C243805617','mode':'experimental RAM-only recovery-slot test; BOOT kept stock','source_commit':'2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3','files':files},indent=2)+'\n')
print('PACKAGING CHECKS PASSED')
print('FILE',i,'BYTES',len(b),'SHA256',hashlib.sha256(b).hexdigest())
print('DTB SHA256',hashlib.sha256((p/'tegra20-motorola-stingray.dtb').read_bytes()).hexdigest())
print('KERNEL CMDLINE',cmdline)
PY
