#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
OUT=$B/build-wingray-gcc14-initramfs
SRC=$B/linux-src
ARCHIVE=$B/phase1-v06/phase1-initramfs.cpio.gz
export ARCH=arm CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
test -s "$ARCHIVE"
gzip -t "$ARCHIVE"
cd "$SRC"
./scripts/config --file "$OUT/.config" --set-str INITRAMFS_SOURCE "$ARCHIVE"
make O="$OUT" olddefconfig
grep -Fx "CONFIG_INITRAMFS_SOURCE=\"$ARCHIVE\"" "$OUT/.config"
grep -Fx "# CONFIG_NEON is not set" "$OUT/.config"
grep -Fx "CONFIG_USB_G_SERIAL=y" "$OUT/.config"
grep -Fx "CONFIG_USB_CHIPIDEA_TEGRA=y" "$OUT/.config"
echo "BUILDING V06 USB TOUCH AND GUARDED POWER DIAGNOSTIC"
make -j2 O="$OUT" nvidia/tegra20-motorola-stingray-usbdiag.dtb zImage > "$B/build-stingray-v06.log" 2>&1 || { tail -n 80 "$B/build-stingray-v06.log";exit 1; }
cmp "$ARCHIVE" "$OUT/usr/initramfs_inc_data"
echo "V06 KERNEL INITRAMFS BYTE MATCH CONFIRMED"
sha256sum "$ARCHIVE" "$OUT/usr/initramfs_inc_data" "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
stat -c "%n %s bytes" "$OUT/arch/arm/boot/zImage"
echo "V06 KERNEL BUILD PASSED, NO DEVICE WRITES"
