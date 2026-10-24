#!/usr/bin/env bash
set -euo pipefail
umask 022
B=/home/xoomdev/xoom-linux-rom
SRC=$B/linux-src
OUT=$B/build-wingray-gcc14-initramfs
TOOLS=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin
CROSS=$TOOLS/arm-none-linux-gnueabihf-
INIT=$B/phase1/phase1-initramfs.cpio.gz
LOG=$B/build-wingray-gcc14-initramfs.log
test -s "$INIT" && gzip -t "$INIT"
test -x "${CROSS}gcc"
mkdir -p "$OUT"
cp "$B/tegra20-wingray-phase1.config" "$OUT/.config"
cd "$SRC"
export ARCH=arm CROSS_COMPILE="$CROSS"
./scripts/config --file "$OUT/.config" --set-str INITRAMFS_SOURCE "$INIT"
./scripts/config --file "$OUT/.config" --enable BLK_DEV_INITRD --disable NEON
make O="$OUT" olddefconfig
echo '=== CRITICAL CONFIG ==='
grep -E '^(CONFIG_INITRAMFS_SOURCE|CONFIG_BLK_DEV_INITRD|CONFIG_RD_GZIP|# CONFIG_NEON|CONFIG_ARM_APPENDED_DTB|CONFIG_ARM_ATAG_DTB_COMPAT)=' "$OUT/.config" || true
grep -q "CONFIG_INITRAMFS_SOURCE=\"$INIT\"" "$OUT/.config"
grep -q '^# CONFIG_NEON is not set' "$OUT/.config"
echo "=== BUILDING KERNEL WITH INTERNAL INITRAMFS ==="
echo "Log at $LOG"
make -j6 O="$OUT" nvidia/tegra20-motorola-wingray.dtb zImage > "$LOG" 2>&1 || { echo 'BUILD FAILED:';grep -n -A4 -B3 -E '(error:|Error [0-9]|fatal error)' "$LOG" | tail -65;tail -30 "$LOG";exit 1; }
echo '=== BUILT ==='
for f in "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dtb" "$OUT/usr/initramfs_inc_data"; do
 test -s "$f"
 stat -c '%n %s bytes' "$f"
 sha256sum "$f"
done
cmp "$INIT" "$OUT/usr/initramfs_inc_data"
echo 'PASS: kernel internal ramfs byte-identical to standalone verified ramfs'
echo 'NO BOOTLOADER OR STORAGE ACTIONS'
