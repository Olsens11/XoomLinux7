#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
K=$B/linux-src
O=$B/build-wingray-gcc14-initramfs
V=$B/phase1-v14
export ARCH=arm CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
cd "$K"
grep -Fx "CONFIG_INITRAMFS_SOURCE=\"$V/phase1-initramfs.cpio.gz\"" "$O/.config"
grep -Fx 'CONFIG_EXTRA_FIRMWARE="regulatory.db regulatory.db.p7s"' "$O/.config"
make -j2 O="$O" zImage nvidia/tegra20-motorola-stingray-usbdiag.dtb > "$B/build-stingray-v14-final.log" 2>&1 || { tail -n 80 "$B/build-stingray-v14-final.log";exit 1; }
cmp "$V/phase1-initramfs.cpio.gz" "$O/usr/initramfs_inc_data"
sha256sum "$V/phase1-initramfs.cpio.gz" "$O/usr/initramfs_inc_data" "$O/arch/arm/boot/zImage"
stat -c 'ZIMAGE_BYTES=%s' "$O/arch/arm/boot/zImage"
echo V14_FINAL_KERNEL_EMBEDS_HOTSWAPPABLE_MODULES_AND_ROOTFS
