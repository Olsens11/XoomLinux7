#!/usr/bin/env bash
# Create a disposable ext4 *regular file*, NEVER format a physical disk.
set -euo pipefail
(( $# == 2 )) || { echo "Usage: $0 DISPOSABLE_ROOTFS NEW_PRIVATE_IMAGE_PATH" >&2; exit 2; }
(( EUID == 0 )) || { echo "Requires host WSL root for device nodes/ownership"; exit 2; }
root="$(realpath "$1")";target="$2"
base=/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025
[[ "$root" == "$base"/test-debian-root-* ]] || { echo "REFUSE unsafe source"; exit 2; }
[[ -f "$root/.xoom-disposable-test-rootfs" && -f "$root/.xoom-firstboot-installed" ]] || { echo "REFUSE incomplete root"; exit 2; }
[[ "$target" == "$base"/XoomLinux7-test-root-* && "$target" == *.img ]] || { echo "REFUSE unsafe image path"; exit 2; }
[[ ! -e "$target" && ! -e "$target.partial" ]] || { echo "REFUSE overwrite"; exit 2; }
partial="$target.partial"
echo "DISPOSABLE_EXT4_FILE_CREATE_START"
truncate -s 2147483648 "$partial"
[[ -f "$partial" && ! -b "$partial" ]] || { echo "Target not regular file"; exit 2; }
mkfs.ext4 -q -F -L XOOMTEST -d "$root" "$partial"
e2fsck -fn "$partial" > "$target.fsck.txt" 2>&1 || { cat "$target.fsck.txt"; echo "OFFLINE_EXT4_CHECK_FAILED";exit 1; }
mv "$partial" "$target"
sha256sum "$target" > "$target.sha256"
echo "DISPOSABLE_EXT4_FILE_BUILD_PASS"
cat "$target.sha256"
echo "NOT FOR FLASHING TO INTERNAL P8: image is 2GiB vs existing 1GiB BigPart p8"
