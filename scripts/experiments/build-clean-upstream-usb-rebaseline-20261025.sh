#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Minimal upstream kernel + existing Xoom v04 read-only USB tool; NO DEVICE ACCESS.
set -euo pipefail
umask 022
B=/home/xoomdev/xoom-linux-rom
REPO=/home/xoomdev/projects/XoomLinux7
UPSTREAM=$B/linux
PIN=2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3
WORK=$B/clean-upstream-usb-20261025
SRC=$WORK/linux
OUT=$WORK/build
DEST=$WORK/artifacts
CC_PREFIX=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
MKBOOT=$HOME/../xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg
# mkbootimg lives in the established xoom-build directory.
MKBOOT=/home/xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg
RAM=$B/phase1-v04/phase1-initramfs.cpio.gz
V04SRC=$REPO/src/diag-init/phase1-v04/init.c
[[ $(id -u) -ne 0 ]] || { echo "Refuse root build" >&2; exit 2; }
[[ -d $UPSTREAM/.git ]] || { echo "Upstream checkout missing" >&2; exit 2; }
[[ $(git -C "$UPSTREAM" rev-parse HEAD) == "$PIN" ]] || { echo "Upstream pinned commit missing" >&2; exit 2; }
[[ -z $(git -C "$UPSTREAM" status --porcelain) ]] || { echo "Original upstream checkout dirty: STOP" >&2; exit 2; }
[[ -s $RAM && -s $V04SRC && -x $CC_PREFIX"gcc" && -x $MKBOOT ]] || { echo "Missing toolchain, USB tool, cpio, or mkbootimg" >&2; exit 2; }
gzip -t "$RAM"
mkdir -p "$WORK" "$DEST"
if [[ ! -d $SRC/.git && ! -f $SRC/.git ]]; then
  git -C "$UPSTREAM" worktree add --detach "$SRC" "$PIN"
fi
[[ $(git -C "$SRC" rev-parse HEAD) == "$PIN" ]] || { echo "Wrong worktree revision" >&2; exit 2; }

# No WLAN/BT changes, no MAC patch and no clock changes in this control image.
# Only a board model+USB UDC DTS derivative and its build target are added.
python3 - "$SRC" <<'PY'
from pathlib import Path
import sys
src=Path(sys.argv[1])
up=(src/'arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dts').read_text()
txt=up
repl=[
 ('model = "Motorola Xoom (Wingray)";','model = "Motorola Xoom (Stingray MZ600 minimal USB diagnostic)";'),
 ('compatible = "motorola,wingray", "motorola,xoom", "nvidia,tegra20";',
  'compatible = "motorola,stingray", "motorola,xoom", "nvidia,tegra20";'),
 ('usb@c5000000 {\n\t\tcompatible = "nvidia,tegra20-ehci"; \n\t\tstatus = "okay";\n\t\tdr_mode = "otg";',
  'usb@c5000000 {\n\t\tcompatible = "nvidia,tegra20-udc";\n\t\tstatus = "okay";\n\t\tdr_mode = "peripheral";'),
 ('usb-phy@c5000000 {\n\t\tstatus = "okay";\n\t\tdr_mode = "otg";',
  'usb-phy@c5000000 {\n\t\tstatus = "okay";\n\t\tdr_mode = "peripheral";'),
]
for old,new in repl:
    if txt.count(old) != 1: raise SystemExit(f"Board source anchor unexpected ({txt.count(old)}): {old[:75]}")
    txt=txt.replace(old,new,1)
dts=src/'arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts'
preamble="// XoomLinux7 isolated clean-upstream USB-only test. NOT an upstream source patch.\n"
if dts.exists() and dts.read_text() != preamble+txt: raise SystemExit("Staged board DTS differs: stop")
dts.write_text(preamble+txt)
mk=src/'arch/arm/boot/dts/nvidia/Makefile'
m=mk.read_text()
old='\ttegra20-motorola-wingray.dtb \\\n'
new='\ttegra20-motorola-wingray.dtb \\\n\ttegra20-motorola-stingray-clean-usb.dtb \\\n'
if new not in m:
    if m.count(old)!=1: raise SystemExit("Makefile anchor not unique")
    mk.write_text(m.replace(old,new,1))
print("ISOLATED_DTS_PASS BOARD_ONLY_USB_DELTA=4",flush=True)
PY

export ARCH=arm CROSS_COMPILE=$CC_PREFIX
mkdir -p "$OUT"
if [[ ! -f $OUT/.config ]]; then
  make -s -C "$SRC" O="$OUT" tegra_next_defconfig
fi
"$SRC/scripts/config" --file "$OUT/.config" \
  --enable ARM_APPENDED_DTB --enable ARM_ATAG_DTB_COMPAT \
  --enable USB_GADGET --enable USB_CHIPIDEA_UDC --enable USB_CHIPIDEA_TEGRA \
  --enable USB_G_SERIAL --enable USB_F_ACM --enable USB_U_SERIAL \
  --enable DEVTMPFS --enable DEVTMPFS_MOUNT \
  --enable PSTORE --enable PSTORE_RAM --enable PSTORE_CONSOLE \
  --disable IIO_ST_HUB_DRIVERS \
  --disable NEON --set-str INITRAMFS_SOURCE ""
make -s -C "$SRC" O="$OUT" olddefconfig
for item in \
  'CONFIG_ARM_APPENDED_DTB=y' \
  'CONFIG_ARM_ATAG_DTB_COMPAT=y' \
  'CONFIG_USB_G_SERIAL=y' \
  'CONFIG_USB_CHIPIDEA_UDC=y' \
  'CONFIG_USB_CHIPIDEA_TEGRA=y' \
  '# CONFIG_NEON is not set' \
  'CONFIG_INITRAMFS_SOURCE=""'; do
  grep -Fx "$item" "$OUT/.config" || { echo "Missing config $item" >&2; exit 3; }
done
make -C "$SRC" O="$OUT" -j6 zImage nvidia/tegra20-motorola-stingray-clean-usb.dtb
K=$OUT/arch/arm/boot/zImage
DTB=$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb
test -s "$K" && test -s "$DTB"
cat "$K" "$DTB" > "$DEST/zImage-with-stingray-usb.dtb"
cp "$OUT/.config" "$DEST/kernel.config"
cp "$RAM" "$DEST/phase1-v04-usb-readonly.cpio.gz"
cp "$DTB" "$DEST/tegra20-motorola-stingray-clean-usb.dtb"
cp "$V04SRC" "$DEST/v04-usb-tool-source.c"
IMAGE=$DEST/MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img
python3 "$MKBOOT" --kernel "$DEST/zImage-with-stingray-usb.dtb" \
    --ramdisk "$RAM" --pagesize 2048 \
    --base 0x10000000 --kernel_offset 0x00008000 \
    --ramdisk_offset 0x01000000 --second_offset 0x00f00000 \
    --tags_offset 0x00000100 \
    --cmdline 'androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=7 printk.time=1 rdinit=/init' \
    --output "$IMAGE"
python3 - "$IMAGE" "$K" "$DTB" "$RAM" "$DEST" <<'PY'
from pathlib import Path
import hashlib,struct,gzip,sys,json
i,k,dtb,ram,out=map(Path,sys.argv[1:])
d=i.read_bytes()
assert d[:8]==b'ANDROID!'
kl,ka,rl,ra,ss,sa,ta,page,ds,unused=struct.unpack_from('<10I',d,8)
kernel=k.read_bytes()+dtb.read_bytes()
assert (ka,ra,ss,sa,ta,page,ds)==(0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
assert d[page:page+kl]==kernel and kl==len(kernel)
off=page+((kl+page-1)//page)*page
assert d[off:off+rl]==ram.read_bytes()
assert gzip.decompress(ram.read_bytes())[:6]==b'070701'
assert len(d)<=8388608
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'upstream_commit':'2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3',
 'baseline':'exact upstream kernel with only Stingray identity and USB0 peripheral DT derivative',
 'usb_tool':'existing v04 read-only diagnostic /init, no Wi-Fi commands',
 'device_actions':'NONE; RAM-only temporary image NOT BOOT-TESTED',
 'factory_eMMC':'UNCHANGED', 'usb_boot_image':i.name,
 'files':{p.name:{'size':p.stat().st_size,'sha256':sha(p)} for p in (i,k,dtb,ram)}}
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('UPSTREAM_CLEAN_USB_IMAGE_BUILD_PASS',i,'bytes',len(d),'sha256',sha(i),flush=True)
PY
echo 'NO DEVICE WRITES. DO NOT FLASH IMAGE. AB test only after physical user recovery.'
