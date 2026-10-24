#!/bin/bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
V=$B/phase1-v034
mkdir -p "$V"
CC=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc
"$CC" -std=gnu11 -Wall -Wextra -Werror -Os -fno-builtin -fno-stack-protector -fno-pie -fno-pic -fomit-frame-pointer -marm -mcpu=cortex-a9 -mfpu=vfpv3-d16 -mfloat-abi=hard -nostdlib -static -Wl,-e,_start -Wl,--build-id=none -s -o "$V/init" "$REPO/src/diag-init/phase1-v034/init.c"
file "$V/init"
if readelf -A "$V/init" | grep -i -e NEON -e Advanced.SIMD;then exit 1;fi
qemu-arm -cpu cortex-a9,neon=off "$V/init"
echo V034_HCI_IOCTL_BY_VALUE_NO_NEON_SELFTEST_PASS
