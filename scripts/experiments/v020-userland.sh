#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
V=$B/phase1-v20
REPO=/home/xoomdev/projects/XoomLinux7-mmc-on-demand
mkdir -p "$V"
cp "$REPO/src/diag-init/phase1-v20/init.c" "$V/init.c"
CC=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc
"$CC" -std=gnu11 -Wall -Wextra -Werror -Os -fno-builtin -fno-stack-protector -fno-pie -fno-pic -fomit-frame-pointer -marm -mcpu=cortex-a9 -mfpu=vfpv3-d16 -mfloat-abi=hard -nostdlib -static -Wl,-e,_start -Wl,--build-id=none -s -o "$V/init" "$V/init.c"
echo '=== ARM CPU ATTRIBUTES ==='
readelf -A "$V/init"
if readelf -A "$V/init" | grep -i -E 'NEON|Advanced.SIMD';then echo 'UNEXPECTED NEON';exit 2;fi
file "$V/init"
sha256sum "$V/init"
# RAM rootfs packing is done by scripts/build/v15-initramfs.py after module validation.

qemu-arm -cpu cortex-a9,neon=off "$V/init"
echo 'V20 NO-NEON NONPID1 SELFTEST PASSED; NO DEVICE WRITES'
