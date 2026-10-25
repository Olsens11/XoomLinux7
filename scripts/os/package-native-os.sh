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
# Do not release an image with an unprovisioned or locked login.
grep -q '^xoom:' "$ROOT/etc/passwd" || { echo "Missing owner login" >&2; exit 1; }
if ! grep -Fq 'xoom:$6$' "$ROOT/etc/shadow"; then
    echo "Owner password is not provisioned: cannot package bootable OS" >&2
    exit 1
fi
[[ -L "$ROOT/etc/systemd/system/getty.target.wants/serial-getty@ttyGS0.service" ]] || {
    echo "USB serial getty not enabled" >&2; exit 1;
}
# QEMU is a *host* ARM emulator used during rootfs staging, not part of the OS.
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

: > "$OUT/empty-ramdisk"
# Normal, direct ext4 root. GPT uses PARTLABEL; MBR microSD uses PARTUUID.
# A PARTUUID is accepted only when explicitly selected for the target card.
if [[ -n "${XOOM_LINUX_ROOT_PARTUUID:-}" ]]; then
    [[ "$XOOM_LINUX_ROOT_PARTUUID" =~ ^[[:xdigit:]]{8}-0[1-4]$ ]] || {
        echo "Invalid DOS-MBR PARTUUID; expected 8 hex digits + -01..-04" >&2; exit 1;
    }
    ROOT_SPEC="PARTUUID=${XOOM_LINUX_ROOT_PARTUUID,,}"
else
    ROOT_PARTLABEL="${XOOM_LINUX_ROOT_PARTLABEL:-xoom-linux}"
    [[ "$ROOT_PARTLABEL" =~ ^[a-zA-Z0-9_-]{1,32}$ ]] || {
        echo "Invalid Linux GPT label" >&2; exit 1;
    }
    case "${ROOT_PARTLABEL,,}" in
        system|userdata|data|cache|boot|recovery|misc)
            echo "Refusing Android partition as native Linux root" >&2; exit 1;;
    esac
    ROOT_SPEC="PARTLABEL=$ROOT_PARTLABEL"
fi
# Exactly one Linux mount entry, with no Android root-device aliases.
python3 - "$ROOT/etc/fstab" "$ROOT_SPEC" <<'PY'
import pathlib, re, sys
p, target = pathlib.Path(sys.argv[1]), sys.argv[2]
lines = p.read_text().splitlines()
hits = [i for i,l in enumerate(lines)
        if re.match(r'^(?:PARTLABEL|PARTUUID)=[^\\s]+\\s+/\\s+ext4\\s+',l)]
if len(hits)!=1:
    raise SystemExit("Expected exactly one staged ext4 root entry; abort")
lines[hits[0]] = target + " / ext4 errors=remount-ro 0 1"
p.write_text("\\n".join(lines)+"\\n")
PY
grep -Fq "$ROOT_SPEC / ext4 " "$ROOT/etc/fstab" ||
    { echo "Root fstab selector mismatch" >&2; exit 1; }
# Build AFTER updating /etc/fstab, so the packed ext4 image has the same selector as boot.
truncate -s 768M "$OUT/xoom-linux-root.ext4"
mkfs.ext4 -F -L xoom-root -b 4096 -d "$ROOT" "$OUT/xoom-linux-root.ext4" > "$OUT/mkfs.log" 2>&1
CMDLINE="androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=4 root=$ROOT_SPEC rootfstype=ext4 rootwait rw init=/sbin/init"
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
dumpe2fs -h "$OUT/xoom-linux-root.ext4" 2>/dev/null | grep -E 'Filesystem volume name|Block count|Block size'
file "$OUT/xoom-linux-boot.img"
sha256sum "$OUT/xoom-linux-root.ext4" "$OUT/xoom-linux-boot.img" \
    "$KERNEL" "$DTB" > "$OUT/SHA256SUMS"

cat > "$OUT/NOT_INSTALLED.txt" <<'EOF'
These are OFFLINE, UNINSTALLED candidate OS images.
Android system, userdata, boot, recovery partitions are NOT modified.
STOP before installation:
 - Confirm exact media ID, partition table (GPT or DOS MBR), target PARTUUID/PARTLABEL, size and whether overwriting existing data is authorized.
 - Preserve Android system/userdata entirely; back up original Android boot and any to-be-modified partition off-device.
 - Provision a unique owner login and test USB serial-getty path.
 - Verify Motorola ATAG factory MAC is present and works during normal OS boot.
 - Obtain explicit user authorization for the specific microSD/ext4 root partition and any later eMMC boot write.
 - Keep original TWRP recovery, data and protected first Xoom untouched.
No hardware mods, scans, RF association, or flashing in this build.
EOF
echo "OFFLINE_OS_PACKAGE_PASS release=$REL target=$ROOT_SPEC rootfs=768MiB"
echo "NO PARTITIONS MODIFIED; inspect $OUT/SHA256SUMS"
