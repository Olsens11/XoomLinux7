#!/usr/bin/env bash
# Generate a TEST-image rootfs overlay; does not modify the reference Debian root.
set -euo pipefail
(( $# == 1 )) || { echo "Usage: $0 NEW_OUTPUT_DIRECTORY" >&2; exit 2; }
out="$1"
[[ ! -e "$out" ]] || { echo "Refusing to overwrite existing output" >&2; exit 2; }
mkdir -p "$out/usr/local/bin" "$out/etc/ssh/sshd_config.d" "$out/etc/NetworkManager/conf.d" "$out/etc/systemd/system/getty@tty1.service.d" "$out/var/lib/xoom"
touch "$out/.xoom-disposable-test-rootfs-overlay"
cat > "$out/usr/local/bin/xoom-wifi" <<'EOF'
#!/bin/sh
# First-boot Wi-Fi frontend for NetworkManager on an offline-provisioned image.
set -eu
case "${1:-connect}" in
connect|menu)
 if ! command -v nmtui >/dev/null 2>&1; then
  echo "nmtui missing. Install the offline Bookworm armhf NetworkManager bundle." >&2
  exit 1
 fi
 if ! systemctl -q is-active NetworkManager; then
  echo "NetworkManager not active. Use serial recovery or the OS's network mode control." >&2
  exit 1
 fi
 exec nmtui connect
 ;;
status)
 if command -v nmcli >/dev/null 2>&1 && systemctl -q is-active NetworkManager; then
  nmcli -f GENERAL.STATE,GENERAL.CONNECTION device show wlan0 || :
  nmcli -f IN-USE,SSID,SIGNAL,SECURITY device wifi list ifname wlan0 || :
 else
  command -v wpa_cli >/dev/null 2>&1 && wpa_cli -i wlan0 status || :
  command -v networkctl >/dev/null 2>&1 && networkctl status wlan0 --no-pager || :
 fi
 ip -br address show wlan0 || :
 ip route show default || :
 ;;
scan)
 if command -v nmcli >/dev/null 2>&1 && systemctl -q is-active NetworkManager; then
  exec nmcli device wifi list ifname wlan0 --rescan yes
 fi
 exec iw dev wlan0 scan
 ;;
help|-h|--help)
 echo "Usage: xoom-wifi [connect|status|scan]";;
*)
 echo "Unknown subcommand. Try: xoom-wifi help" >&2
 exit 2;;
esac
EOF
cat > "$out/usr/local/bin/xoom-net-check" <<'EOF'
#!/bin/sh
# Diagnostics never change link or connection state.
set -u
echo '=== USB and screen consoles ==='
ls -l /dev/ttyGS0 /dev/tty0 /dev/tty1 /dev/fb0 2>&1 || :
echo '=== Wi-Fi ==='
ip -br link show wlan0 || :
ip -br addr show wlan0 || :
ip route show default || :
echo '=== Network manager ==='
systemctl --no-pager --plain is-active NetworkManager systemd-networkd 'wpa_supplicant@wlan0' 2>/dev/null || :
echo '=== Name resolution ==='
getent ahostsv4 debian.org || :
echo '=== ICMP (3s timeout, optional) ==='
command -v ping >/dev/null 2>&1 && ping -n -c 1 -W 3 1.1.1.1 || :
echo '=== Firmware and platform display ==='
ls -l /lib/firmware/brcm/brcmfmac4329-sdio.bin /lib/firmware/brcm/brcmfmac4329-sdio.txt /sys/class/graphics/fb0 /sys/class/drm 2>&1 || :
EOF
cat > "$out/usr/local/bin/xoom-console-check" <<'EOF'
#!/bin/sh
# Does not start display services or modify hardware.
echo '=== Kernel VT and framebuffer ==='
cat /proc/fb 2>/dev/null || :
ls -l /dev/tty0 /dev/tty1 /dev/fb0 2>&1 || :
echo '=== DRM devices ==='
ls -l /dev/dri /sys/class/drm 2>&1 || :
echo '=== Console gettys ==='
systemctl --no-pager status getty@tty1 serial-getty@ttyGS0 2>&1 | tail -40 || :
echo '=== Input events ==='
cat /proc/bus/input/devices 2>/dev/null | grep -E '^(N:|H:)' || :
echo '=== Boot arguments ==='
cat /proc/cmdline
EOF
chmod 0755 "$out/usr/local/bin/"*
cat > "$out/etc/ssh/sshd_config.d/60-xoom-test-root-policy.conf" <<'EOF'
# Local console password login is allowed for disposable prototypes only.
# Never allow remote root password login, especially with temporary passwords.
PermitRootLogin no
PasswordAuthentication no
EOF
cat > "$out/etc/NetworkManager/conf.d/20-xoom-firstboot.conf" <<'EOF'
[main]
# Do not create credentials at image build time. nmtui saves them on device.
# Ownership belongs to NetworkManager, not systemd-networkd.
[device]
wifi.scan-rand-mac-address=no
EOF
cat > "$out/etc/systemd/system/getty@tty1.service.d/10-xoom-local-screen.conf" <<'EOF'
[Service]
# Leave readable login prompt on the framebuffer if display driver binds.
TTYVTDisallocate=no
EOF
cat > "$out/var/lib/xoom/firstboot-safety.txt" <<'EOF'
Disposable build. No factory Wi-Fi SSID, PSK, country-code override or
MAC address is embedded. On-screen keyboard / touch input remains an OPEN gate.
Preserve COM9 ttyGS0 as an independent rescue console.
EOF
echo "XOOM_FIRSTBOOT_OVERLAY_CREATED $out"
find "$out" -type f -print | LC_ALL=C sort
