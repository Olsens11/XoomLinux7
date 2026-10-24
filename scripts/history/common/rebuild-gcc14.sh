#!/usr/bin/env bash
# Offline kernel rebuild using the STANDALONE ARM toolchain; never accesses hardware.
set -euo pipefail
BASE=/home/xoomdev/xoom-linux-rom
SRC="$BASE/linux-src"
OUT="$BASE/build-wingray-gcc14"
CROSS="$BASE/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
test -x "${CROSS}gcc" || { echo "Standalone compiler missing" >&2; exit 2; }
test -s "$BASE/tegra20-wingray-phase1.config" || { echo "Missing reviewed config" >&2; exit 2; }
mkdir -p "$OUT"
cp "$BASE/tegra20-wingray-phase1.config" "$OUT/.config"
cd "$SRC"
export ARCH=arm CROSS_COMPILE="$CROSS"
make O="$OUT" olddefconfig
grep -q '^# CONFIG_NEON is not set' "$OUT/.config" || { echo "NEON configuration check failed" >&2; exit 2; }
echo "Building Xoom Wingray with standalone Arm GNU Toolchain 14.3 (NOT flashable)"
make -j4 O="$OUT" nvidia/tegra20-motorola-wingray.dtb zImage
for f in "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dtb"; do
  test -s "$f"; stat -c '%n %s bytes' "$f"; sha256sum "$f"
done
echo "BUILD ONLY. NO DEVICE, FLASH OR BOOT IMAGE OPERATIONS."
