#!/bin/bash
set -u
B=/home/xoomdev/xoom-linux-rom
echo ====KERNEL_CONF====
grep -E '(CONFIG_(BLK_DEV_INITRD|RD_GZIP|INITRAMFS_SOURCE|INITRAMFS_FORCE|INITRAMFS_COMPRESSION|BINFMT_ELF|DEVTMPFS|ARM_APPENDED_DTB|ARM_ATAG_DTB_COMPAT|DECOMPRESS_GZIP|ZLIB_INFLATE))' "$B/build-wingray/.config" || true
echo ====INITRAMFS====
gzip -t "$B/phase1/phase1-initramfs.cpio.gz" && gzip -dc "$B/phase1/phase1-initramfs.cpio.gz" | cpio -itv 2>/dev/null
echo ====BUILTIN====
ls -lh "$B/artifacts/xoom-wingray-phase1-diagnostic-UNTESTED.img" "$B/phase1/phase1-initramfs.cpio.gz"
echo ====BOOTPARAM====
grep -R -n -m3 -E 'check access for rdinit|initrd_start|initrd_end|parse_tag_initrd2' "$B/linux-src/init" "$B/linux-src/arch/arm/kernel" 2>/dev/null | head -35
