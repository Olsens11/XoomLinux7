#!/usr/bin/env bash
# Replacement MZ600 ONLY: install six SHA-pinned official Bookworm D-Bus packages.
# Xoom /run tar bundle already received on COM9, physical SHA verified.
# Does not reboot, flash p7, change Wi-Fi/BT firmware, or load radio modules.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
ARCHIVE='/run/mz600-bookworm-dbus6-matched-offline-20261026.tar.gz'
SHA='5b59275308ffe4993783bb8f4e566e290e34246d03da3ba1af8255aabb252e4e'
BYTES=606850
STAGE='/run/mz600-bookworm-dbus6-install-stage-20261026'
INSTALL_STARTED=0
fail() { printf 'DBUS6_INSTALL_ABORT: %s\n' "$*" >&2; exit 1; }
on_exit() {
  code=$?
  if (( code != 0 )); then
    printf 'DBUS6_INSTALL_EXIT=%d; dpkg_execution_started=%d; inspect dpkg and stage; do not rerun blindly\n' "$code" "$INSTALL_STARTED" >&2
  fi
}
trap on_exit EXIT
echo 'MZ600_DBUS6_OFFLINE_INSTALL_PREFLIGHT_START'
[[ "$(id -u)" == 0 ]] || fail 'not root'
[[ "$(uname -r)" == "$K" ]] || fail 'wrong running kernel'
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || fail 'not internal ext4 p8'
[[ "$(cat /etc/debian_version)" == '12.15' ]] || fail 'wrong Debian release'
[[ "$(dpkg --print-architecture)" == 'armhf' ]] || fail 'not Debian armhf'
[[ ! -e "$STAGE" && ! -L "$STAGE" ]] || fail 'staging path already exists'
[[ -f "$ARCHIVE" && ! -L "$ARCHIVE" ]] || fail 'RAM archive missing/unsafe'
[[ "$(stat -c %s "$ARCHIVE")" == "$BYTES" ]] || fail 'unexpected RAM bundle size'
printf '%s  %s\n' "$SHA" "$ARCHIVE" | sha256sum -c - || fail 'RAM archive hash changed'
[[ "$(df -Pk / | awk 'NR==2 {print $4}')" -gt 131072 ]] || fail 'too little p8 free space'
for tool in tar dpkg dpkg-deb sha256sum grep awk cmp mkdir; do
  command -v "$tool" >/dev/null || fail "missing tool $tool"
done
[[ -z "$(dpkg --audit)" ]] || fail 'dpkg already has errors; investigate first'
for p in dbus dbus-bin dbus-daemon dbus-session-bus-common dbus-system-bus-common libexpat1; do
  if dpkg -s "$p" 2>/dev/null | grep -q '^Status: install ok installed$'; then
    fail "unexpected preinstalled package: $p"
  fi
done
[[ "$(tar -tzf "$ARCHIVE" | wc -l)" == 6 ]] || fail 'wrong tar member count'
expected="$(printf '%s\n' \
'dbus6/dbus_1.14.10-1~deb12u1_armhf.deb' \
'dbus6/dbus-bin_1.14.10-1~deb12u1_armhf.deb' \
'dbus6/dbus-daemon_1.14.10-1~deb12u1_armhf.deb' \
'dbus6/dbus-session-bus-common_1.14.10-1~deb12u1_all.deb' \
'dbus6/dbus-system-bus-common_1.14.10-1~deb12u1_all.deb' \
'dbus6/libexpat1_2.5.0-1+deb12u2_armhf.deb')"
[[ "$(tar -tzf "$ARCHIVE")" == "$expected" ]] || fail 'nonallowlisted archive path'
echo 'MZ600_DBUS6_RAMPKG_AND_DEPENDENCY_PREFLIGHT_PASS'

mkdir -m 0700 "$STAGE"
tar -xzf "$ARCHIVE" -C "$STAGE" --no-same-owner
D="$STAGE/dbus6"
[[ -d "$D" && "$(find "$D" -type f | wc -l)" == 6 ]] || fail 'extraction count mismatch'
[[ "$(find "$STAGE" -type l | wc -l)" == 0 ]] || fail 'archive contains symlink'
(
  cd "$D"
  printf '%s  %s\n' \
  319e1802a831f3f3921a1751afe948173bf4d04c402356e2560828649e262b58 'dbus_1.14.10-1~deb12u1_armhf.deb' \
  d2dd421c4c18ea67a7c4184bf31f73fd16a580048ed4b7b483eeb5886c79e8d3 'dbus-bin_1.14.10-1~deb12u1_armhf.deb' \
  8238913c664752e69b4c0f2fdb0a4208808ad02fcaa90661ab80bd1f4440fd96 'dbus-daemon_1.14.10-1~deb12u1_armhf.deb' \
  b19cb8e3581d6b09ff3f46fee23de2813811353228c666c9d1ad885598062e43 'dbus-session-bus-common_1.14.10-1~deb12u1_all.deb' \
  2111d3d0c98ac68ee973274058447e6fab1c359fec1d4bb195f5fcc5833a19e2 'dbus-system-bus-common_1.14.10-1~deb12u1_all.deb' \
  e1cbf8b00e34295cd92865747abf80999218b6511ddc68daffd6b0e5f9fe0d63 'libexpat1_2.5.0-1+deb12u2_armhf.deb' | sha256sum -c -
) || fail 'APT metadata matched inner hashes FAILED'
[[ "$(dpkg-deb -f "$D/dbus-daemon_1.14.10-1~deb12u1_armhf.deb" Package)" == 'dbus-daemon' ]] || fail 'wrong binary package'
echo 'MZ600_DBUS6_SIX_PACKAGES_INDIVIDUAL_SHA_PASS'
INSTALL_STARTED=1
DEBIAN_FRONTEND=noninteractive dpkg -i \
 "$D/dbus-bin_1.14.10-1~deb12u1_armhf.deb" \
 "$D/dbus-session-bus-common_1.14.10-1~deb12u1_all.deb" \
 "$D/libexpat1_2.5.0-1+deb12u2_armhf.deb" \
 "$D/dbus-daemon_1.14.10-1~deb12u1_armhf.deb" \
 "$D/dbus-system-bus-common_1.14.10-1~deb12u1_all.deb" \
 "$D/dbus_1.14.10-1~deb12u1_armhf.deb"
[[ -z "$(dpkg --audit)" ]] || fail 'dpkg postinstall audit not clean'
for p in dbus dbus-bin dbus-daemon dbus-session-bus-common dbus-system-bus-common libexpat1; do
  dpkg -s "$p" | grep -q '^Status: install ok installed$' || fail "not configured: $p"
done
echo 'MZ600_DBUS6_OFFLINE_DPKG_6_OF_6_PHYSICAL_PASS'
echo 'MZ600_DBUS6_PACKAGE_INSTALL_COMPLETE_NO_WIFI_RESTART'
