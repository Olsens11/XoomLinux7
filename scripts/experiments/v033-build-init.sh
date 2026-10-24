#!/bin/bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
CC=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc
V=$B/phase1-v033
"$CC" -std=gnu11 -Wall -Wextra -Werror -Os -fno-builtin -fno-stack-protector -fno-pie -fno-pic -fomit-frame-pointer -marm -mcpu=cortex-a9 -mfpu=vfpv3-d16 -mfloat-abi=hard -nostdlib -static -Wl,-e,_start -Wl,--build-id=none -s -o "$V/init" "$(cd "$(dirname "$0")/../.." && pwd)/src/diag-init/phase1-v033/init.c"
file "$V/init"
readelf -A "$V/init"
if readelf -A "$V/init" | grep -i -e NEON -e Advanced.SIMD; then echo FAILED_NEON; exit 1; fi
qemu-arm -cpu cortex-a9,neon=off "$V/init"
echo V033_NO_NEON_INIT_SELFTEST_PASS
