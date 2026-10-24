#!/bin/bash
set -euo pipefail
BASE=/home/xoomdev/xoom-linux-rom
OUT=$BASE/build-wingray-gcc14-initramfs
SRC=$BASE/linux-src
ARCHIVE=$BASE/phase1-v03/phase1-initramfs.cpio.gz
CROSS=$BASE/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
export ARCH=arm CROSS_COMPILE="$CROSS"
test -s "$ARCHIVE"
gzip -t "$ARCHIVE"
cd "$SRC"
./scripts/config --file "$OUT/.config" --set-str INITRAMFS_SOURCE "$ARCHIVE"
make O="$OUT" olddefconfig
grep -Fx "CONFIG_INITRAMFS_SOURCE=\"$ARCHIVE\"" "$OUT/.config"
grep -Fx '# CONFIG_NEON is not set' "$OUT/.config"
echo "BUILDING V03 REVISED ZIMAGE (NO DEVICE WRITES)"
make -j2 O="$OUT" nvidia/tegra20-motorola-stingray.dtb zImage > "$BASE/build-stingray-v03.log" 2>&1 || {
 tail -n 55 "$BASE/build-stingray-v03.log"
 exit 1
}
cmp "$ARCHIVE" "$OUT/usr/initramfs_inc_data"
echo "V03 BUILTIN INITRAMFS VERIFIED"
sha256sum "$ARCHIVE" "$OUT/usr/initramfs_inc_data" "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dtb"
stat -c '%n %s bytes' "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dtb"
echo "V03 KERNEL BUILD COMPLETED"
