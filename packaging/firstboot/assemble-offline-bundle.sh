#!/usr/bin/env bash
# Create a transportable, OFFLINE, NON-SECRET prototype connectivity bundle.
# Does not contain root password, router Wi-Fi credentials or BCM4329 firmware.
set -euo pipefail
[[ $# == 4 ]] || { echo "Usage: $0 ROOT_OVERLAY NETWORK_DEBS HOST_TOOLS NEW_ARCHIVE.tar.gz" >&2; exit 2; }
overlay="$(realpath "$1")"; net="$(realpath "$2")"; host="$(realpath "$3")"; archive="$4"
[[ ! -e "$archive" ]] || { echo "Refusing existing archive" >&2; exit 2; }
[[ -f "$net/SHA256SUMS" && -f "$host/SHA256SUMS" ]] || { echo "Missing SHA manifests" >&2; exit 2; }
(cd "$net/archives" && sha256sum -c ../SHA256SUMS > /dev/null)
(cd "$host" && sha256sum -c SHA256SUMS > /dev/null)
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
mkdir -p "$temp/firstboot-offline/debs"
cp -a "$overlay" "$temp/firstboot-offline/root-overlay"
cp -a "$host" "$temp/firstboot-offline/windows-com9"
cp "$net/SHA256SUMS" "$net/packages-resolved.tsv" "$temp/firstboot-offline/"
cp "$net/archives/"*.deb "$temp/firstboot-offline/debs/"
(
 cd "$temp/firstboot-offline/debs"
 sha256sum -c ../SHA256SUMS > /dev/null
)
cat > "$temp/firstboot-offline/README-FIRST.txt" <<'EOF'
Prototype XoomLinux7 OS-only connectivity kit.
No device passwords, Wi-Fi/router secrets, or proprietary Broadcom firmware.
Debian Bookworm armhf .deb files are downloaded, NOT installed in an image.
Apply only to an isolated, correctly provisioned disposable ARMhf rootfs,
using the audited source instructions in packaging/firstboot/README.md.
Use NetworkManager exclusively instead of systemd-networkd+interface WPA.
On-device screen getty is provisional until DRM/framebuffer verified.
The Surface Windows COM9 tool remains a separate host-side application.
EOF
tar -C "$temp" -czf "$archive" firstboot-offline
sha256sum "$archive" > "$archive.sha256"
echo "FIRSTBOOT_OFFLINE_NONPRIVATE_ARCHIVE_PASS $(stat -c%s "$archive") bytes"
cat "$archive.sha256"
