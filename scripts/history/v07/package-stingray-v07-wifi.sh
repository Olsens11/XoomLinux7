#!/bin/bash
set -euo pipefail
umask 022
B=/home/xoomdev/xoom-linux-rom
V=$B/phase1-v07
O=$B/build-wingray-gcc14-initramfs
DEST=/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v07-WIFI
MK=/home/xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg
K=$O/arch/arm/boot/zImage
DTB=$O/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb
RAM=$V/phase1-initramfs.cpio.gz
mkdir -p "$DEST"
cmp "$RAM" "$O/usr/initramfs_inc_data"
cat "$K" "$DTB" > "$DEST/zImage-stingray-usb-appended-dtb.bin"
cp "$K" "$DEST/zImage"
cp "$DTB" "$DEST/tegra20-motorola-stingray-usbdiag.dtb"
cp "$RAM" "$DEST/phase1-initramfs.cpio.gz"
cp "$V/init" "$DEST/init-freestanding-armv7-noNEON"
cp "$V/init.c" "$DEST/init-v07-source.c"
cp "$O/.config" "$DEST/kernel-v07.config"
cp "$B/linux-src/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dts" "$DEST/tegra20-motorola-stingray-usbdiag.dts"
CMD="androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=4 printk.time=1 rdinit=/init"
python3 "$MK" --kernel "$DEST/zImage-stingray-usb-appended-dtb.bin" --ramdisk "$RAM" --pagesize 2048 --base 0x10000000 --kernel_offset 0x00008000 --ramdisk_offset 0x01000000 --second_offset 0x00f00000 --tags_offset 0x00000100 --cmdline "$CMD" --output "$DEST/MZ600-stingray-diagnostic-v07-WIFI-TEMPBOOT-ONLY.img"
python3 - "$DEST" <<'PY'
from pathlib import Path
import json,hashlib,struct,gzip,sys
p=Path(sys.argv[1])
i=p/"MZ600-stingray-diagnostic-v07-WIFI-TEMPBOOT-ONLY.img"
d=i.read_bytes()
assert d[:8]==b"ANDROID!"
v=struct.unpack_from("<10I",d,8)
kl,ka,rl,ra,s,sa,ta,page,dt,unused=v
assert (ka,ra,sa,ta,page)==(0x10008000,0x11000000,0x10f00000,0x10000100,2048)
assert s==0 and dt==0
assert len(d)<=8*1024*1024
combined=(p/"zImage-stingray-usb-appended-dtb.bin").read_bytes()
assert kl==len(combined)
assert d[page:page+kl]==combined
ro=page+((kl+page-1)//page)*page
r=d[ro:ro+rl]
assert r==(p/"phase1-initramfs.cpio.gz").read_bytes()
assert gzip.decompress(r)[:6]==b"070701"
fdt=(p/"tegra20-motorola-stingray-usbdiag.dtb").read_bytes()
assert fdt[:4]==bytes.fromhex("d00dfeed") and combined.endswith(fdt)
m=hashlib.sha1()
for blob in (combined,r,b"",b""): m.update(blob);m.update(struct.pack("<I",len(blob)))
assert d[576:596]==m.digest()
cmd=d[64:576].split(b"\0")[0].decode()
assert "rdinit=/init" in cmd and "modelno=MZ600" in cmd
config=(p/"kernel-v07.config").read_text()
assert 'CONFIG_USB_G_SERIAL=y' in config
assert 'CONFIG_USB_CHIPIDEA_TEGRA=y' in config
assert 'CONFIG_USB_F_ACM=y' in config
dtst=(p/"tegra20-motorola-stingray-usbdiag.dts").read_text()
assert 'compatible = "nvidia,tegra20-udc"' in dtst
assert 'dr_mode = "peripheral"' in dtst
files=[]
for path in sorted(p.iterdir()):
 if path.is_file():
  b=path.read_bytes()
  files.append(dict(name=path.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(p/"MANIFEST.json").write_text(json.dumps({"device":"MZ600 Stingray v07 native upstream brcmfmac BCM4329 read-only SDIO firmware probe experiment","source_commit":"2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3","deployment":"temporary fastboot boot only; DO NOT FLASH","verified_offline":True,"files":files},indent=2)+"\n")
print("V07 IMAGE SHA256",hashlib.sha256(d).hexdigest())
print("V07 IMAGE SIZE",len(d))
print("BOOT HEADER HASH, KERNEL, DTB, INITRAMFS, CONFIG VERIFIED. NO DEVICE WRITES.")
PY
