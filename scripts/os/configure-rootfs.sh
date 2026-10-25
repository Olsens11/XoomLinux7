#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
# Populate a *staging directory* containing Debian armhf, not an eMMC partition.
set -euo pipefail
[[ $# -eq 2 ]] || { echo "usage: $0 /path/to/armhf-rootfs /path/to/verified-brcmfmac4329-sdio.bin" >&2; exit 2; }
[[ "$(id -u)" == 0 ]] || { echo "Root required to preserve staged rootfs permissions" >&2; exit 1; }
ROOT="$(readlink -f "$1")"
FW="$(readlink -f "$2")"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
EXPECTED_FW_SHA=d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93
[[ -f "$ROOT/etc/debian_version" && -e "$ROOT/sbin/init" ]] || { echo "Not a completed Debian root filesystem" >&2; exit 1; }
[[ "$(sha256sum "$FW" | cut -d' ' -f1)" == "$EXPECTED_FW_SHA" ]] || { echo "Wi-Fi firmware SHA mismatch" >&2; exit 1; }
NVRAM="$REPO/configs/os/brcmfmac4329-sdio.stingray-calibration-no-identity.txt"
[[ -f "$NVRAM" ]] || exit 1
[[ "$(stat -c %s "$NVRAM")" -eq 1550 ]] || { echo "Unverified board calibration length" >&2; exit 1; }
EXPECTED_CAL_SHA=a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb
[[ "$(sha256sum "$NVRAM" | cut -d' ' -f1)" == "$EXPECTED_CAL_SHA" ]] || {
    echo "Board calibration differs from physically qualified 1550-byte reference" >&2; exit 1;
}
if grep -Eqi '^[[:space:]]*(macaddr|ccode|regrev)[[:space:]]*=' "$NVRAM"; then
    echo "Refusing public shared-MAC/regulatory NVRAM" >&2
    exit 1
fi
[[ "$ROOT" == */bookworm-armhf-root ]] || {
    echo "Refusing to modify an unexpected rootfs path: $ROOT" >&2; exit 1;
}
install -d "$ROOT/etc/modprobe.d" "$ROOT/etc/systemd/system" \
  "$ROOT/usr/local/libexec" "$ROOT/lib/firmware/brcm" "$ROOT/etc/network"
install -m 644 "$FW" "$ROOT/lib/firmware/brcm/brcmfmac4329-sdio.bin"
install -m 644 "$NVRAM" "$ROOT/lib/firmware/brcm/brcmfmac4329-sdio.txt"
install -m 644 "$REPO/configs/os/mz600-brcmfmac-autoload.conf" \
  "$ROOT/etc/modprobe.d/mz600-brcmfmac.conf"
install -m 644 "$REPO/configs/os/mz600-wlan.service" \
  "$ROOT/etc/systemd/system/mz600-wlan.service"
install -m 755 "$REPO/scripts/os/check-factory-wlan-mac.sh" \
  "$ROOT/usr/local/libexec/xoom-check-factory-wlan-mac"
install -m 644 "$REPO/configs/os/fstab" "$ROOT/etc/fstab"
printf '%s\n' "xoom-mz600" > "$ROOT/etc/hostname"
cat > "$ROOT/etc/hosts" <<'EOF'
127.0.0.1 localhost
127.0.1.1 xoom-mz600
::1 localhost ip6-localhost ip6-loopback
EOF
# USB is the LOCAL ACCESS PATH: g_serial stays built into the kernel;
# systemd's normal serial-getty accepts logins on /dev/ttyGS0.
systemctl --root="$ROOT" enable serial-getty@ttyGS0.service
systemctl --root="$ROOT" enable mz600-wlan.service

# Do not auto-connect to an AP, scan or transmit until the owner qualifies
# the actual per-device MAC, calibration, and regulatory domain.
echo 'auto lo' > "$ROOT/etc/network/interfaces"
echo 'iface lo inet loopback' >> "$ROOT/etc/network/interfaces"
cat > "$ROOT/etc/motd" <<'EOF'
Xoom Linux 7 — installed OS build
USB login: /dev/ttyGS0 (host virtual COM port)
Wi-Fi requires verified Motorola per-device MAC in the Wi-Fi DT node.
EOF

echo "STAGED_OS_ROOTFS_CONFIGURED $ROOT"
echo "WLAN_FW_SHAFIXED=$EXPECTED_FW_SHA"
echo "NO DEVICE PARTITIONS ALTERED"
echo "LOGIN ACCOUNT/SECRET PROVISIONING REQUIRED BEFORE DEPLOYMENT"
