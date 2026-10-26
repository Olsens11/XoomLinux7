#!/usr/bin/env bash
# Experimental MZ600 Debian p8: WLAN driver, wlan0, ONE passive scan,
# then clean up WCC -> brcmfmac -> brcmutil. No reboot or association.
set -Eeuo pipefail
export SYSTEMD_PAGER=cat PAGER=cat
K='7.0.0-next-20260422+'
FACTORY='/sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address'
RAW='/run/mz600-v064-wifi-passive-scan-20261026-private.txt'
FINISHED=0
CLEAN=0
say() { printf '%s\n' "$*"; }
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  say "MZ600_WIFI_BOUNDED_CLEANUP_BEGIN rc=$rc"
  if [[ -d /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set dev wlan0 down
    say "MZ600_WIFI_LINK_DOWN_REQUESTED rc=$?"
  fi
  for m in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 10s modprobe -r "$m" 2>&1
    say "MZ600_WIFI_UNLOAD_$m rc=$?"
  done
  sleep 1
  if [[ ! -e /sys/class/net/wlan0 ]] && ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    CLEAN=1
    say 'MZ600_WIFI_BOUNDED_CLEANUP_VERIFIED_DRIVER_UNLOADED_WLAN0_ABSENT'
  else
    say 'MZ600_WIFI_CLEANUP_INCOMPLETE_CHECK_MODULES_BEFORE_FURTHER_TESTS'
  fi
  if (( FINISHED == 1 && CLEAN == 1 )); then
    say 'MZ600_WIFI_PASSIVE_SCAN_BOUNDED_TEST_FINAL_PASS'
  else
    say "MZ600_WIFI_BOUNDED_TEST_END rc=$rc finished=$FINISHED cleaned=$CLEAN"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say 'MZ600_WIFI_BOUNDED_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 ]] || { say 'ABORT_NOT_ROOT'; exit 1; }
[[ "$(uname -r)" == "$K" ]] || { say 'ABORT_KERNEL_MISMATCH'; exit 1; }
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || { say 'ABORT_ROOT_NOT_P8_EXT4'; exit 1; }
[[ "$(cat /etc/debian_version)" == 12.15 ]] || { say 'ABORT_DEBIAN_RELEASE'; exit 1; }
[[ -r "$FACTORY" && "$(wc -c < "$FACTORY")" == 6 ]] || { say 'ABORT_FACTORY_FDT_MAC_MISSING'; exit 1; }
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || { say 'ABORT_BCM4329_SDIO_UNAVAILABLE'; exit 1; }
[[ ! -e /sys/class/net/wlan0 ]] || { say 'ABORT_WLAN0_ALREADY_PRESENT'; exit 1; }
[[ ! -e "$RAW" ]] || { say 'ABORT_PRIVATE_SCAN_FILE_ALREADY_EXISTS'; exit 1; }
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|hci_uart|bluetooth) ' /proc/modules || { say 'ABORT_RADIO_MODULE_ALREADY_ACTIVE'; exit 1; }
for svc in wpa_supplicant NetworkManager iwd; do
  if systemctl -q is-active "$svc.service"; then say "ABORT_NETWORK_MANAGER_ACTIVE_$svc"; exit 1; fi
done
for binary in modprobe timeout iw ip awk grep wc sha256sum; do command -v "$binary" >/dev/null || { say "ABORT_MISSING_$binary"; exit 1; }; done
[[ -s /lib/firmware/brcm/brcmfmac4329-sdio.bin ]] || { say 'ABORT_FIRMWARE_MISSING'; exit 1; }
[[ -s /lib/firmware/brcm/brcmfmac4329-sdio.txt ]] || { say 'ABORT_NVRAM_MISSING'; exit 1; }
[[ "$(readlink -f /lib/firmware/regulatory.db)" == '/usr/lib/firmware/regulatory.db-upstream' ]] || { say 'ABORT_REGDB_ALTERNATIVE'; exit 1; }
[[ "$(readlink -f /lib/firmware/regulatory.db.p7s)" == '/usr/lib/firmware/regulatory.db.p7s-upstream' ]] || { say 'ABORT_REGDB_SIGNATURE_ALTERNATIVE'; exit 1; }
iw reg get | grep -q '^country 00:' || { say 'ABORT_UNEXPECTED_GLOBAL_REGDOM'; exit 1; }
say 'MZ600_WIFI_BOUNDED_PREFLIGHT_PASS'
say 'MZ600_WIFI_DRIVER_LOAD_BEGIN'
timeout -k 3s 30s modprobe brcmfmac-wcc
say 'MZ600_WIFI_WCC_MODPROBE_RC0'
for n in $(seq 1 30); do
  if [[ -d /sys/class/net/wlan0 ]]; then break; fi
  sleep 0.4
done
[[ -d /sys/class/net/wlan0 ]] || { say 'MZ600_WIFI_WLAN0_NOT_PRESENT'; exit 2; }
say 'MZ600_WIFI_WLAN0_PHYSICAL_PRESENT'
grep -q '^0$' /sys/class/net/wlan0/addr_assign_type || { say 'MZ600_WIFI_ADDR_NOT_PERMANENT'; exit 3; }
say 'MZ600_WIFI_ADDR_ASSIGN_TYPE_PERMANENT_PASS'
for m in brcmfmac_wcc brcmfmac brcmutil; do
  grep -q "^$m " /proc/modules || { say "MZ600_WIFI_MODULE_MISSING_$m"; exit 4; }
done
say 'MZ600_WIFI_ALL_3_DRIVER_MODULES_LIVE'
PHY='/run/mz600-v064-phy0-info-20261026-private.txt'
iw phy phy0 info > "$PHY" || { say 'MZ600_WIFI_PHY_INFO_FAILED'; exit 5; }
for chan in 1 6 11; do
  grep -q "\[$chan\]" "$PHY" || { say "MZ600_WIFI_PHY_CHANNEL_UNVERIFIED_$chan"; exit 6; }
done
say 'MZ600_WIFI_PHY_2G_CHANNELS_1_6_11_PRESENT'
timeout -k 2s 10s ip link set dev wlan0 up
say 'MZ600_WIFI_WLAN0_LINK_UP_REQUEST_SUCCESS'
say 'MZ600_WIFI_PASSIVE_SCAN_2G_START'
set +e
timeout -k 3s 35s iw dev wlan0 scan freq 2412 2437 2462 passive > "$RAW" 2>&1
scan_rc=$?
set -e
say "MZ600_WIFI_PASSIVE_SCAN_COMMAND_RC=$scan_rc"
say "MZ600_WIFI_SCAN_PRIVATE_BYTES=$(wc -c < "$RAW")"
say "MZ600_WIFI_SCAN_PRIVATE_SHA256=$(sha256sum "$RAW" | awk '{print $1}')"
if (( scan_rc != 0 )); then
  say 'MZ600_WIFI_PASSIVE_SCAN_ERROR_PRIVATE_LOG_ONLY'
  exit 7
fi
count="$(grep -c '^BSS ' "$RAW" || true)"
say "MZ600_WIFI_PASSIVE_SCAN_BSS_COUNT=$count"
awk '/^[[:space:]]*freq:/ {f[$2]++} END {for (k in f) if (k=="2412" || k=="2437" || k=="2462") print "MZ600_WIFI_PASSIVE_FREQ=" k " BSS=" f[k]}' "$RAW" | sort
say 'MZ600_WIFI_PASSIVE_SCAN_PHYSICAL_SUCCESS'
FINISHED=1
exit 0
