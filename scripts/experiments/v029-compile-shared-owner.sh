#!/usr/bin/env bash
# v029 compile-only; no Xoom device access, no boot image, no flash.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
BASE=/home/xoomdev/xoom-linux-rom
SRC="$BASE/linux-src"
OUT="$BASE/phase1-v029-shared-owner/build"
CROSS="$BASE/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
mkdir -p "$OUT"
cp "$BASE/build-wingray-gcc14-initramfs/.config" "$OUT/.config"
"$SRC/scripts/config" --file "$OUT/.config" --enable POWER_SEQUENCING
make -s -C "$SRC" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" olddefconfig
grep '^CONFIG_POWER_SEQUENCING=y$' "$OUT/.config"
make -s -j2 -C "$SRC" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" prepare modules_prepare
make -s -j2 -C "$SRC" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" drivers/power/sequencing/core.o
make -j2 -C "$SRC" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" M="$REPO/src/chip" stingray-bcm4329-pwrseq.o
echo BCM4329_V029_COMPILE_ONLY_PASS_NO_DEVICE_ACCESS
