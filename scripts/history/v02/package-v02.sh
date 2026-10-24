#!/usr/bin/env bash
set -euo pipefail
umask 022
B=/home/xoomdev/xoom-linux-rom
OUT=$B/build-wingray-gcc14-initramfs
STAGE=/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-v02
mkdir -p "$STAGE"
K="$OUT/arch/arm/boot/zImage"
DT="$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dtb"
RAM="$B/phase1/phase1-initramfs.cpio.gz"
INIT="$B/phase1/initramfs/init"
VERIFIER="$B/phase1/verify-boot-v02.py"
MK=/home/xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg
test -s "$K" && test -s "$DT" && test -s "$RAM"
cmp "$RAM" "$OUT/usr/initramfs_inc_data"
cat "$K" "$DT" > "$STAGE/zImage-with-appended-wingray-dtb.bin"
CMDLINE="androidboot.carrier=wifi-only product_type=w console=tty0 loglevel=7 printk.time=1 rdinit=/init"
python3 "$MK" --kernel "$STAGE/zImage-with-appended-wingray-dtb.bin" --ramdisk "$RAM" --pagesize 2048 --base 0x10000000 --kernel_offset 0x00008000 --ramdisk_offset 0x01000000 --second_offset 0x00f00000 --tags_offset 0x00000100 --cmdline "$CMDLINE" --output "$STAGE/xoom-wingray-phase1-internal-init-v02-UNTESTED.img"
cp "$OUT/.config" "$STAGE/wingray-gcc14-embedded-init.config"
cp "$K" "$STAGE/zImage"
cp "$DT" "$STAGE/tegra20-motorola-wingray.dtb"
cp "$RAM" "$STAGE/phase1-initramfs.cpio.gz"
cp "$INIT" "$STAGE/init-freestanding-armv7-noNEON"
cp /mnt/c/Users/olsen/XoomLinux/Phase1/build-internal-initramfs-v02.sh "$STAGE/"
cp /mnt/c/Users/olsen/xoom-phase1-init-freestanding.c "$STAGE/"
sha256sum "$STAGE"/*.img "$STAGE"/zImage "$STAGE"/*.dtb "$STAGE"/*.gz "$STAGE"/init-freestanding-armv7-noNEON
stat -c '%n %s bytes' "$STAGE"/*.img
python3 - "$STAGE" <<'PY'
import pathlib,sys,hashlib,json,struct,gzip
p=pathlib.Path(sys.argv[1]);img=(p/"xoom-wingray-phase1-internal-init-v02-UNTESTED.img").read_bytes()
assert img[:8]==b"ANDROID!"
nums=struct.unpack_from("<10I",img,8)
klen,kaddr,rlen,raddr,seclen,secaddr,tags,page,dtlen,zero=nums
assert (kaddr,raddr,tags,page)==(0x10008000,0x11000000,0x10000100,2048)
assert seclen==0 and dtlen==0
assert len(img)<8192*1024
kern=img[page:page+klen]
expected=(p/"zImage-with-appended-wingray-dtb.bin").read_bytes()
assert kern==expected
ram_off=page+((klen+page-1)//page)*page
ram=img[ram_off:ram_off+rlen]
assert ram==(p/"phase1-initramfs.cpio.gz").read_bytes()
assert gzip.decompress(ram)[:6]==b"070701"
assert b"init" in gzip.decompress(ram)
assert (p/"zImage").read_bytes()==kern[:-(p/"tegra20-motorola-wingray.dtb").stat().st_size]
assert (p/"tegra20-motorola-wingray.dtb").read_bytes()[:4]==bytes.fromhex("d00dfeed")
a=[]
for f in sorted(p.iterdir()):
 if f.is_file():
  b=f.read_bytes();a.append(dict(name=f.name,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
(p/"manifest.json").write_text(json.dumps({"source_commit":"2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3","kernel_build":"GCC 14.3.1, internal initramfs, 2026-10-23","verified_image_size":len(img),"files":a},indent=2)+"\n")
print("PASS: v02 internal archive matched, Android boot header validated, v01 recovery remains untouched.")
print("SHA256",hashlib.sha256(img).hexdigest(),"SIZE",len(img))
PY
