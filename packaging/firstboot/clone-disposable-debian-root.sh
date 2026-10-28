#!/usr/bin/env bash
# Prepare a new local WSL test rootfs only; no tablets or mounted block devices.
set -euo pipefail
(( $# == 2 )) || { echo "Usage: $0 ORIGINAL_REFERENCE_DIR NEW_EMPTY_ROOTFS_PATH" >&2; exit 2; }
(( EUID == 0 )) || { echo "Must run as root within dedicated build WSL" >&2; exit 2; }
src="$(realpath "$1")"
new="$2"
[[ -f "$src/etc/debian_version" && -f "$src/var/lib/dpkg/status" ]] || { echo "Invalid Debian reference"; exit 2; }
[[ ! -e "$new" ]] || { echo "Refuse existing destination"; exit 2; }
parent="$(realpath "$(dirname "$new")")"
[[ "$parent" == /home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025 ]] || { echo "Destination outside private WSL build workspace"; exit 2; }
[[ "$src" != "$parent"/* && "$src" != "$new" ]] || { echo "Refuse reference overlap"; exit 2; }
echo "COPY_REFERENCE_START"
mkdir -m 0755 "$new"
rsync -aHAX --numeric-ids --one-file-system "$src/" "$new/"
touch "$new/.xoom-disposable-test-rootfs"
test -e "$new/var/lib/dpkg/status" && test -e "$new/etc/shadow"
echo "ROOTFS_PRIVATE_CLONE_PASS $(du -sh "$new" | cut -f1)"
