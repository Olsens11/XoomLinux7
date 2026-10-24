#!/usr/bin/env bash
set -euo pipefail
umask 022
B=/home/xoomdev/xoom-linux-rom
SRC=/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v08-WIFI-TRACE
DST=/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v08-WIFI-TRACE-DEBUG
MK=/home/xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg
test -s "$SRC/zImage-stingray-usb-appended-dtb.bin"
test -s "$B/phase1-v08/phase1-initramfs.cpio.gz"
mkdir -p "$DST"
CMD="androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=4 printk.time=1 rdinit=/init brcmfmac.debug=2"
python3 "$MK" --kernel "$SRC/zImage-stingray-usb-appended-dtb.bin" --ramdisk "$B/phase1-v08/phase1-initramfs.cpio.gz" --pagesize 2048 --base 0x10000000 --kernel_offset 0x00008000 --ramdisk_offset 0x01000000 --second_offset 0x00f00000 --tags_offset 0x00000100 --cmdline "$CMD" --output "$DST/MZ600-stingray-diagnostic-v08-WIFI-TRACE-DEBUG-TEMPBOOT-ONLY.img"
python3 - "$SRC" "$DST" <<'PY'
import hashlib,struct,sys
from pathlib import Path
src,dst=map(Path,sys.argv[1:])
orig=(src/'MZ600-stingray-diagnostic-v08-WIFI-TRACE-TEMPBOOT-ONLY.img').read_bytes()
assert hashlib.sha256(orig).hexdigest()=='6cc15a94eb4a300ff25c7c49866668e8b6fd709d3e678367694c74a4de613fd5'
newpath=dst/'MZ600-stingray-diagnostic-v08-WIFI-TRACE-DEBUG-TEMPBOOT-ONLY.img'
new=newpath.read_bytes()
assert new[:8]==orig[:8]==b'ANDROID!'
page=2048
kl,ka,rl,ra,s,sa,ta,pg,dt,unused=struct.unpack_from('<10I',new,8)
assert pg==2048 and s==0 and dt==0 and ka==0x10008000
kl_old,ka_old,rl_old,ra_old,*rest=struct.unpack_from('<10I',orig,8)
assert kl_old==kl and rl_old==rl and ka_old==ka and ra_old==ra
assert new[page:page+kl]==orig[page:page+kl]
ramoff=page+((kl+page-1)//page)*page
assert new[ramoff:ramoff+rl]==orig[ramoff:ramoff+rl]
assert len(new)==len(orig)<8*1024*1024
assert new[64:576].split(b'\0')[0].decode().endswith('brcmfmac.debug=2')
m=hashlib.sha1()
for blob in (new[page:page+kl],new[ramoff:ramoff+rl],b'',b''):
 m.update(blob);m.update(struct.pack('<I',len(blob)))
assert new[576:596]==m.digest()
assert new!=orig
print('V08 DEBUG TEMPBOOT VERIFIED: SAME KERNEL/DTB/RAMDISK, CMDLINE ONLY CHANGE')
print('IMAGE_BYTES',len(new),'SHA256',hashlib.sha256(new).hexdigest())
print('BOOT_COMMANDLINE',new[64:576].split(b'\0')[0].decode())
PY
