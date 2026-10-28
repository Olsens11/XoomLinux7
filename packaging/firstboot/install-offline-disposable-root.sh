#!/usr/bin/env bash
# Offline Debian armhf firstboot installer. Only for freshly marked WSL COPY.
set -euo pipefail
(( $# == 3 )) || { echo "Usage: $0 DISPOSABLE_ROOTFS OFFLINE_DEBS ROOTFS_OVERLAY" >&2; exit 2; }
(( EUID == 0 )) || { echo "Requires root in dedicated WSL build, not tablet" >&2; exit 2; }
root="$(realpath "$1")"; net="$(realpath "$2")"; overlay="$(realpath "$3")"
[[ "$root" == /home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/test-debian-root-* ]] || { echo "Refuse unsafe target";exit 2; }
[[ -f "$root/.xoom-disposable-test-rootfs" && -f "$root/var/lib/dpkg/status" && -f "$overlay/.xoom-disposable-test-rootfs-overlay" ]] || { echo "Refuse unmarked root/overlay";exit 2; }
[[ -f "$net/SHA256SUMS" && -f "$net/sources.list" ]] || { echo "Incomplete signed Debian package bundle";exit 2; }
[[ ! -e "$root/.xoom-firstboot-installed" ]] || { echo "Already provisioned";exit 2; }
(cd "$net/archives" && sha256sum -c ../SHA256SUMS >/dev/null)
echo "SIGNED_OFFLINE_BUNDLE_HASH_PASS"
mkdir -p "$root/var/lib/apt/lists/partial" "$root/var/cache/apt/archives/partial"
rsync -a --exclude='partial/' "$net/lists/" "$root/var/lib/apt/lists/"
rsync -a --include='*.deb' --exclude='*' "$net/archives/" "$root/var/cache/apt/archives/"
# The staged signing-key reference is host-absolute; translate into target.
sed "s#signed-by=[^]]*#signed-by=/usr/share/keyrings/debian-archive-keyring.gpg#g" "$net/sources.list" > "$root/etc/apt/sources.list"
mkdir -p "$root/etc/apt/apt.conf.d"
printf '%s\n' 'APT::Get::AllowUnauthenticated "false";' > "$root/etc/apt/apt.conf.d/85-xoom-offline-authenticated"
if [[ -e "$root/usr/sbin/policy-rc.d" ]]; then echo "Refuse existing policy-rc.d";exit 2;fi
printf '#!/bin/sh\nexit 101\n' > "$root/usr/sbin/policy-rc.d"
chmod 755 "$root/usr/sbin/policy-rc.d"
mapfile -t packages < <(grep -vE '^([[:space:]]*#|[[:space:]]*$)' "$(dirname "$0")/packages.bookworm-armhf.txt")
echo "SIMULATE_OFFLINE_DPKG_INSTALL"
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get -s --no-download --no-install-recommends install "${packages[@]}" > "$root/var/log/xoom-firstboot-apt-simulate.log"
echo "INSTALL_OFFLINE_DPKG_START"
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get -y --no-download --no-install-recommends install "${packages[@]}" > "$root/var/log/xoom-firstboot-apt-install.log" 2>&1 || {
 tail -n 45 "$root/var/log/xoom-firstboot-apt-install.log" | sed -E 's/(password|psk|ssid).*/[redacted]/Ig'
 echo "OFFLINE_INSTALL_FAILED; test root incomplete" >&2;exit 1; }
rm "$root/usr/sbin/policy-rc.d"
rsync -a --exclude='.xoom-disposable-test-rootfs-overlay' "$overlay/" "$root/"
# Deliberately remove any inherited historical WPA network secrets on NEW test root.
# Do not change the reference rootfs; no SSIDs/PSKs shipped in generic test image.
if [[ -f "$root/etc/wpa_supplicant/wpa_supplicant-wlan0.conf" ]];then
 mv "$root/etc/wpa_supplicant/wpa_supplicant-wlan0.conf" "$root/var/lib/xoom/inherited-wpa-wlan0.PRIVATE.DISABLED"
 chmod 0600 "$root/var/lib/xoom/inherited-wpa-wlan0.PRIVATE.DISABLED"
fi
systemctl --root="$root" disable systemd-networkd.service wpa_supplicant@wlan0.service >/dev/null 2>&1 || :
systemctl --root="$root" enable NetworkManager.service systemd-timesyncd.service getty@tty1.service serial-getty@ttyGS0.service > "$root/var/log/xoom-firstboot-enabled.log" 2>&1
test -x "$root/usr/bin/nmtui" && test -x "$root/usr/bin/nmcli" && test -x "$root/usr/bin/ping" && test -x "$root/usr/bin/curl"
test -x "$root/usr/local/bin/xoom-wifi" && test -x "$root/usr/local/bin/xoom-console-check"
grep -qx "PermitRootLogin no" "$root/etc/ssh/sshd_config.d/60-xoom-test-root-policy.conf"
grep -qx "PasswordAuthentication no" "$root/etc/ssh/sshd_config.d/60-xoom-test-root-policy.conf"
touch "$root/.xoom-firstboot-installed"
echo "OFFLINE_FIRSTBOOT_TEST_ROOT_INSTALL_PASS"
