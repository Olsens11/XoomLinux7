#!/bin/bash
set -u
B=/home/xoomdev/xoom-linux-rom
echo ====USR_MAKEFILE====
sed -n '1,220p' "$B/linux-src/usr/Makefile"
echo ====INITRAMFS_SOURCE_SUPPORT====
grep -n -A12 -B6 'config INITRAMFS_SOURCE\|config INITRAMFS_FORCE\|config INITRAMFS_COMPRESSION' "$B/linux-src/usr/Kconfig" | head -140
echo ====ATAGS_COMPAT====
sed -n '85,175p' "$B/linux-src/arch/arm/kernel/atags_compat.c"
echo ====ABI_AND_TARGET====
ls -lh "$B/build-wingray-gcc14/.config" "$B/phase1/phase1-initramfs.cpio.gz" 2>/dev/null || true
