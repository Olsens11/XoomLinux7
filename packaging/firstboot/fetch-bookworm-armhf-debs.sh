#!/usr/bin/env bash
# Fetch signed Debian Bookworm armhf .deb dependencies into a NEW private directory.
# Neither apt nor dpkg is run against the live system or the reference rootfs.
set -euo pipefail
[[ $# == 2 ]] || { echo "Usage: $0 EXISTING_BOOKWORM_ARMHF_REFERENCE_ROOT NEW_OUTPUT_DIR" >&2; exit 2; }
src="$(realpath "$1")"
out="$2"
[[ -f "$src/var/lib/dpkg/status" && -f "$src/etc/debian_version" ]] || { echo "Reference root is not a Debian rootfs" >&2; exit 2; }
[[ ! -e "$out" ]] || { echo "Refusing existing output directory" >&2; exit 2; }
key="$src/usr/share/keyrings/debian-archive-keyring.gpg"
[[ -s "$key" ]] || { echo "Debian archive signing key not found" >&2; exit 2; }
mkdir -p "$out/lists/partial" "$out/archives/partial"
out="$(realpath "$out")"
cat > "$out/sources.list" <<EOF
deb [arch=armhf signed-by=$key] https://deb.debian.org/debian bookworm main
deb [arch=armhf signed-by=$key] https://deb.debian.org/debian bookworm-updates main
deb [arch=armhf signed-by=$key] https://security.debian.org/debian-security bookworm-security main
EOF
mapfile -t packages < <(grep -vE '^([[:space:]]*#|[[:space:]]*$)' "$(dirname "$0")/packages.bookworm-armhf.txt")
opts=(
 -o "Dir::Etc::sourcelist=$out/sources.list"
 -o "Dir::Etc::sourceparts=-"
 -o "Dir::State::status=$src/var/lib/dpkg/status"
 -o "Dir::State::lists=$out/lists"
 -o "Dir::State::extended_states=$out/extended_states"
 -o "Dir::Cache::archives=$out/archives"
 -o "APT::Architecture=armhf"
 -o "APT::Architectures=armhf"
 -o "Debug::NoLocking=true"
 -o "APT::Get::AllowUnauthenticated=false"
)
echo "OFFLINE_DEBIAN_BUNDLE_BEGIN reference=$src output=$out"
apt-get "${opts[@]}" update > "$out/apt-update.log" 2>&1 || { tail -50 "$out/apt-update.log"; exit 1; }
apt-get "${opts[@]}" -s --no-install-recommends install "${packages[@]}" > "$out/apt-simulate.log" 2>&1 || { tail -65 "$out/apt-simulate.log"; exit 1; }
apt-get "${opts[@]}" -y --download-only --no-install-recommends install "${packages[@]}" > "$out/apt-download.log" 2>&1 || { tail -65 "$out/apt-download.log"; exit 1; }
shopt -s nullglob
debs=("$out"/archives/*.deb)
(( ${#debs[@]} > 0 )) || { echo "No .deb files downloaded"; exit 1; }
: > "$out/SHA256SUMS"
: > "$out/packages-resolved.tsv"
for deb in "${debs[@]}"; do
 arch="$(dpkg-deb -f "$deb" Architecture)"
 [[ "$arch" == armhf || "$arch" == all ]] || { echo "Wrong architecture $arch: $deb" >&2; exit 1; }
 (cd "$out/archives" && sha256sum "$(basename "$deb")") >> "$out/SHA256SUMS"
 printf '%s\t%s\t%s\t%s\n' "$(dpkg-deb -f "$deb" Package)" "$(dpkg-deb -f "$deb" Version)" "$arch" "$(basename "$deb")" >> "$out/packages-resolved.tsv"
done
(cd "$out/archives" && sha256sum -c "../SHA256SUMS" > "$out/sha256-verify.log")
echo "OFFLINE_DEBIAN_BUNDLE_PASS packages=${#debs[@]} bytes=$(du -sb "$out/archives" | cut -f1)"
echo "No packages were installed into $src or the host."
