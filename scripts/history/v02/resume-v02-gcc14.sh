#!/usr/bin/env bash
set -euo pipefail
BASE=/home/xoomdev/xoom-linux-rom
OUT=$BASE/build-wingray-gcc14-initramfs
SRC=$BASE/linux-src
CROSS=$BASE/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
export ARCH=arm CROSS_COMPILE="$CROSS"
cd "$SRC"
echo "RETRY CRASHED OBJECT SINGLE-THREADED"
make -j1 O="$OUT" net/ipv4/ip_tunnel.o
echo "RESUME KERNEL BUILD AT TWO JOBS"
make -j2 O="$OUT" nvidia/tegra20-motorola-wingray.dtb zImage > "$BASE/build-wingray-gcc14-resume.log" 2>&1 || {
 echo "FAILED, last diagnostics:"
 grep -n -A7 -B2 -E 'error:|Error [0-9]|fatal error' "$BASE/build-wingray-gcc14-resume.log" | tail -55 || true
 tail -n 25 "$BASE/build-wingray-gcc14-resume.log"
 exit 1
}
echo "SUCCESS"
for f in "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dtb" "$OUT/usr/initramfs_inc_data"; do stat -c '%n %s bytes' "$f"; sha256sum "$f"; done
cmp "$BASE/phase1/phase1-initramfs.cpio.gz" "$OUT/usr/initramfs_inc_data"
echo "EMBEDDED_INITRAMFS_MATCH_OK"
