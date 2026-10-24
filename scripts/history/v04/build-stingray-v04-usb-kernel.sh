#!/bin/bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
OUT=$B/build-wingray-gcc14-initramfs
SRC=$B/linux-src
ARCHIVE=$B/phase1-v04/phase1-initramfs.cpio.gz
export ARCH=arm CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
test -s "$ARCHIVE"
gzip -t "$ARCHIVE"
cd "$SRC"
./scripts/config --file "$OUT/.config" --set-str INITRAMFS_SOURCE "$ARCHIVE"
./scripts/config --file "$OUT/.config" --enable USB_G_SERIAL --enable USB_CHIPIDEA_UDC --enable USB_CHIPIDEA_TEGRA
make O="$OUT" olddefconfig
grep -Fx "CONFIG_INITRAMFS_SOURCE=\"$ARCHIVE\"" "$OUT/.config"
grep -Fx '# CONFIG_NEON is not set' "$OUT/.config"
grep -Fx 'CONFIG_USB_G_SERIAL=y' "$OUT/.config"
grep -Fx 'CONFIG_USB_CHIPIDEA_UDC=y' "$OUT/.config"
grep -Fx 'CONFIG_USB_CHIPIDEA_TEGRA=y' "$OUT/.config"
echo '=== USB GADGET CONFIG ==='
grep -E 'CONFIG_USB_G_SERIAL=|CONFIG_USB_F_ACM=|CONFIG_USB_U_SERIAL=|CONFIG_USB_CHIPIDEA_TEGRA=' "$OUT/.config"
echo '=== KERNEL AND USB DEVICE TREE BUILD ==='
make -j2 O="$OUT" nvidia/tegra20-motorola-stingray-usbdiag.dtb zImage > "$B/build-stingray-v04.log" 2>&1 || {
 tail -n 75 "$B/build-stingray-v04.log"
 exit 1
}
cmp "$ARCHIVE" "$OUT/usr/initramfs_inc_data"
echo 'V04 EMBEDDED INITRAMFS EXACT MATCH'
sha256sum "$ARCHIVE" "$OUT/usr/initramfs_inc_data" "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
stat -c '%n %s bytes' "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
echo 'KERNEL V04 BUILD COMPLETE; NO DEVICE WRITES'
