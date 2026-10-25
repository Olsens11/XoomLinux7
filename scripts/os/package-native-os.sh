#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
# Package a normal Linux rootfs + non-installed Android-format boot image.
# Intentionally contains NO fastboot/flash/dd-of-device commands.
set -euo pipefail
[[ $# -eq 1 ]] || { echo "usage: $0 /path/to/staged-bookworm-armhf-rootfs" >&2; exit 2; }
ROOT="$(readlink -f "$1")"
[[ "$ROOT" == */bookworm-armhf-root && -s "$ROOT/etc/debian_version" ]] || {
    echo "Invalid staging rootfs" >&2; exit 1;
}
[[ "$(id -u)" == 0 ]] || { echo "Packaging ext4 ownership requires root" >&2; exit 1; }
B="${XOOM_BUILD_ROOT:-/home/xoomdev/xoom-linux-rom}"
O="${XOOM_OS_KERNEL_OUT:-$B/os-build/kernel}"
OUT="${XOOM_OS_ARTIFACTS:-$B/os-build/artifacts}"
MK="${XOOM_MKBOOTIMG:-/home/xoomdev/xoom-build/android-7.1/out/host/linux-x86/bin/mkbootimg}"
REL="$(cat "$O/include/config/kernel.release")"
DTB="$O/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
KERNEL="$O/arch/arm/boot/zImage"
# No owner-less or boot-unusable system image may be published as an install candidate.
grep -q '^xoom:' "$ROOT/etc/passwd" || { echo "No owner login provisioned" >&2; exit 1; }
if ! grep -q '^xoom:\\$6\\
    echo "Missing native kernel or modules. Build + install modules first" >&2; exit 1;
}
[[ -x "$MK" || -f "$MK" ]] || { echo "mkbootimg not found" >&2; exit 1; }

# The installed system MUST be provisioned with owner credentials before
# writing to any eMMC partition. This packager cannot provision passwords.
mkdir -p "$OUT"
cat "$KERNEL" "$DTB" > "$OUT/zImage-stingray-with-dtb"
truncate -s 768M "$OUT/xoom-linux-system.ext4"
mkfs.ext4 -F -L xoom-root -b 4096 -d "$ROOT" "$OUT/xoom-linux-system.ext4" > "$OUT/mkfs.log" 2>&1

: > "$OUT/empty-ramdisk"
CMDLINE='androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=4 root=PARTLABEL=system rootfstype=ext4 rootwait rw init=/sbin/init'
python3 "$MK" \
    --kernel "$OUT/zImage-stingray-with-dtb" \
    --ramdisk "$OUT/empty-ramdisk" \
    --pagesize 2048 --base 0x10000000 \
    --kernel_offset 0x00008000 --ramdisk_offset 0x01000000 \
    --second_offset 0x00f00000 --tags_offset 0x00000100 \
    --cmdline "$CMDLINE" \
    --output "$OUT/xoom-linux-boot.img"
[[ "$(stat -c %s "$OUT/xoom-linux-boot.img")" -le 8388608 ]] || {
    echo "Boot image exceeds 8MiB engineering target; verify real BOOT partition" >&2; exit 1;
}
# Check contents without mount/loopback, using filesystem metadata readers.
dumpe2fs -h "$OUT/xoom-linux-system.ext4" 2>/dev/null | grep -E 'Filesystem volume name|Block count|Block size'
file "$OUT/xoom-linux-boot.img"
sha256sum "$OUT/xoom-linux-system.ext4" "$OUT/xoom-linux-boot.img" \
    "$KERNEL" "$DTB" > "$OUT/SHA256SUMS"

cat > "$OUT/NOT_INSTALLED.txt" <<'EOF'
These are OFFLINE, UNINSTALLED candidate OS images.
The Android 'system' (p8) and 'boot' partitions are NOT modified.
STOP before installation:
 - Confirm actual replacement Xoom and exact GPT partition GUIDs/sizes.
 - Back up original Android system/boot and verify backups off-device.
 - Provision a unique owner login and test USB serial-getty path.
 - Verify Motorola ATAG factory MAC is present and works during normal OS boot.
 - Obtain explicit user authorization for the exact named persistent writes.
 - Keep original TWRP recovery, data and protected first Xoom untouched.
No hardware mods, scans, RF association, or flashing in this build.
EOF
echo "OFFLINE_OS_PACKAGE_PASS release=$REL target=PARTLABEL:system rootfs=768MiB"
echo "NO PARTITIONS MODIFIED; inspect $OUT/SHA256SUMS"
 "$ROOT/etc/shadow"; then
    echo "Local owner password not provisioned; refusing OS package" >&2
    exit 1
fi
[[ -L "$ROOT/etc/systemd/system/getty.target.wants/serial-getty@ttyGS0.service" ]] || {
    echo "USB serial-getty missing" >&2; exit 1;
}
# Remove x86 build-only QEMU helper from the final ARM filesystem, never from
# the host machine; its role is completed at this point.
rm -f "$ROOT/usr/bin/qemu-arm-static"
rm -rf "$ROOT/debootstrap"
[[ -s "$KERNEL" && -s "$DTB" && -f "$ROOT/lib/modules/$REL/modules.dep" ]] || {
    echo "Missing native kernel or modules. Build + install modules first" >&2; exit 1;
}
[[ -x "$MK" || -f "$MK" ]] || { echo "mkbootimg not found" >&2; exit 1; }

# The installed system MUST be provisioned with owner credentials before
# writing to any eMMC partition. This packager cannot provision passwords.
mkdir -p "$OUT"
cat "$KERNEL" "$DTB" > "$OUT/zImage-stingray-with-dtb"
truncate -s 768M "$OUT/xoom-linux-system.ext4"
mkfs.ext4 -F -L xoom-root -b 4096 -d "$ROOT" "$OUT/xoom-linux-system.ext4" > "$OUT/mkfs.log" 2>&1

: > "$OUT/empty-ramdisk"
CMDLINE='androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=4 root=PARTLABEL=system rootfstype=ext4 rootwait rw init=/sbin/init'
python3 "$MK" \
    --kernel "$OUT/zImage-stingray-with-dtb" \
    --ramdisk "$OUT/empty-ramdisk" \
    --pagesize 2048 --base 0x10000000 \
    --kernel_offset 0x00008000 --ramdisk_offset 0x01000000 \
    --second_offset 0x00f00000 --tags_offset 0x00000100 \
    --cmdline "$CMDLINE" \
    --output "$OUT/xoom-linux-boot.img"
[[ "$(stat -c %s "$OUT/xoom-linux-boot.img")" -le 8388608 ]] || {
    echo "Boot image exceeds 8MiB engineering target; verify real BOOT partition" >&2; exit 1;
}
# Check contents without mount/loopback, using filesystem metadata readers.
dumpe2fs -h "$OUT/xoom-linux-system.ext4" 2>/dev/null | grep -E 'Filesystem volume name|Block count|Block size'
file "$OUT/xoom-linux-boot.img"
sha256sum "$OUT/xoom-linux-system.ext4" "$OUT/xoom-linux-boot.img" \
    "$KERNEL" "$DTB" > "$OUT/SHA256SUMS"

cat > "$OUT/NOT_INSTALLED.txt" <<'EOF'
These are OFFLINE, UNINSTALLED candidate OS images.
The Android 'system' (p8) and 'boot' partitions are NOT modified.
STOP before installation:
 - Confirm actual replacement Xoom and exact GPT partition GUIDs/sizes.
 - Back up original Android system/boot and verify backups off-device.
 - Provision a unique owner login and test USB serial-getty path.
 - Verify Motorola ATAG factory MAC is present and works during normal OS boot.
 - Obtain explicit user authorization for the exact named persistent writes.
 - Keep original TWRP recovery, data and protected first Xoom untouched.
No hardware mods, scans, RF association, or flashing in this build.
EOF
echo "OFFLINE_OS_PACKAGE_PASS release=$REL target=PARTLABEL:system rootfs=768MiB"
echo "NO PARTITIONS MODIFIED; inspect $OUT/SHA256SUMS"
