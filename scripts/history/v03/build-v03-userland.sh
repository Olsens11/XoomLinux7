#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
V=$B/phase1-v03
CC=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc
test -x "$CC"
"$CC" -std=gnu11 -Wall -Wextra -Werror -Os -fno-builtin -fno-stack-protector -fno-pie -fno-pic -fomit-frame-pointer -marm -mcpu=cortex-a9 -mfpu=vfpv3-d16 -mfloat-abi=hard -nostdlib -static -Wl,-e,_start -Wl,--build-id=none -s -o "$V/init" "$V/init.c"
echo ===ARM_ATTRIBUTES===
readelf -A "$V/init" | tail -30
if readelf -A "$V/init" | grep -i -E '(NEON|Advanced.SIMD)';then echo "NEON ABI UNEXPECTED";exit 2;fi
file "$V/init"
sha256sum "$V/init"
python3 "$B/phase1/pack-initramfs.py" --init "$V/init" --output "$V/phase1-initramfs.cpio.gz"
gzip -t "$V/phase1-initramfs.cpio.gz"
command -v qemu-arm >/dev/null
qemu-arm -cpu cortex-a9,neon=off "$V/init"
echo "V03 BUILD AND NONPID1 SELFTEST PASSED, DEVICES UNTOUCHED"
