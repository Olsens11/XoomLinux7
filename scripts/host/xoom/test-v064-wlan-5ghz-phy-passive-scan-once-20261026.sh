#!/usr/bin/env bash
# MZ600 internal Debian: check PHY 5GHz support, conditionally passive scan.
# No reboot, association or RF-setting changes; always reverse-unload driver.
set -Eeuo pipefail
export SYSTEMD_PAGER=cat PAGER=cat
K='7.0.0-next-20260422+'
FACTORY='/sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address'
PHY='/run/mz600-v064-5ghz-phy-discovered-20261026-private.txt'
RAW='/run/mz600-v064-5ghz-passive-discovered-20261026-private.txt'
STATE=INIT
say() { printf '%s\n' "$*"; }
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  say "MZ600_5G_CLEANUP_BEGIN rc=$rc state=$STATE"
  if [[ -d /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set dev wlan0 down
    say "MZ600_5G_LINK_DOWN_RC=$?"
  fi
  for m in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 10s modprobe -r "$m" 2>&1
    say "MZ600_5G_UNLOAD_""$m""_RC=$?"
  done
  sleep 1
  if [[ ! -d /sys/class/net/wlan0 ]] && ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    say 'MZ600_5G_CLEANUP_VERIFIED_NO_WLAN0_NO_BRCM'
    case "$STATE" in
      SCAN_PASS) say 'MZ600_5G_PASSIVE_SCAN_AND_CLEANUP_PHYSICAL_PASS' ;;
      UNSUPPORTED) say 'MZ600_5G_NO_PHY_CHANNELS_SCAN_SKIPPED_CLEAN' ;;
      SCAN_FAILED) say 'MZ600_5G_SCAN_FAILED_CLEANED' ;;
      *) say "MZ600_5G_BOUNDED_END_""$STATE""_CLEAN" ;;
    esac
  else
    say 'MZ600_5G_CLEANUP_INCOMPLETE_DO_NOT_PROCEED'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say 'MZ600_5G_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 ]] || { say 'ABORT_NO_ROOT'; exit 1; }
[[ "$(uname -r)" == "$K" ]] || { say 'ABORT_WRONG_KERNEL'; exit 1; }
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || { say 'ABORT_NOT_INTERNAL_P8'; exit 1; }
[[ "$(cat /etc/debian_version)" == 12.15 ]] || { say 'ABORT_NOT_BOOKWORM_12_15'; exit 1; }
[[ -r "$FACTORY" && "$(wc -c < "$FACTORY")" == 6 ]] || { say 'ABORT_FACTORY_MAC_MISSING'; exit 1; }
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || { say 'ABORT_NO_BCM4329_SDIO'; exit 1; }
[[ ! -e "$PHY" && ! -e "$RAW" ]] || { say 'ABORT_PRIOR_PRIVATE_CAPTURE_EXISTS'; exit 1; }
[[ ! -d /sys/class/net/wlan0 ]] || { say 'ABORT_WLAN0_ALREADY_ACTIVE'; exit 1; }
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|hci_uart|bluetooth) ' /proc/modules || { say 'ABORT_RADIO_MODULES_ALREADY_PRESENT'; exit 1; }
for svc in wpa_supplicant NetworkManager iwd; do
  if systemctl -q is-active "$svc.service"; then say "ABORT_AUTO_NETWORK_MANAGER_$svc"; exit 1; fi
done
for binary in iw modprobe ip timeout awk grep sha256sum; do
  command -v "$binary" >/dev/null || { say "ABORT_MISSING_TOOL_$binary"; exit 1; }
done
[[ -s /lib/firmware/brcm/brcmfmac4329-sdio.bin && -s /lib/firmware/brcm/brcmfmac4329-sdio.txt ]] || { say 'ABORT_NO_BCM4329_FW'; exit 1; }
[[ "$(readlink -f /lib/firmware/regulatory.db)" == '/usr/lib/firmware/regulatory.db-upstream' ]] || { say 'ABORT_NO_SIGNED_REGDB'; exit 1; }
[[ "$(readlink -f /lib/firmware/regulatory.db.p7s)" == '/usr/lib/firmware/regulatory.db.p7s-upstream' ]] || { say 'ABORT_NO_SIGNED_REGDB_SIGNATURE'; exit 1; }
iw reg get | grep -q '^country 00:' || { say 'ABORT_UNEXPECTED_WORLD_REGDOM'; exit 1; }
say 'MZ600_5G_PREFLIGHT_PASS'
STATE=DRIVER_LOAD
timeout -k 3s 30s modprobe brcmfmac-wcc
say 'MZ600_5G_WCC_MODULE_LOAD_RC0'
for n in $(seq 1 30); do
  [[ -d /sys/class/net/wlan0 ]] && break
  sleep .4
done
[[ -d /sys/class/net/wlan0 ]] || { say 'MZ600_5G_WLAN0_MISSING'; exit 2; }
say 'MZ600_5G_WLAN0_PRESENT'
# Linux ieee80211 PHY indices are dynamic across driver rebinds.
PHY_ID="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2;exit}')"
[[ "$PHY_ID" =~ ^[0-9]+$ ]] || { say 'MZ600_5G_ACTIVE_PHY_ID_NOT_DETECTED'; exit 4; }
say "MZ600_5G_DYNAMIC_WIPHY_INDEX=$PHY_ID"
iw phy "phy$PHY_ID" info > "$PHY"
say "MZ600_5G_PHY_PRIVATE_SHA256=$(sha256sum "$PHY" | awk '{print $1}')"
say 'MZ600_5G_PHY_CHANNEL_QUERY_BEGIN'
FREQS=''
FREQ_COUNT=0
for pair in '5180 36' '5200 40' '5220 44' '5240 48'; do
  set -- $pair
  freq="$1"
  chan="$2"
  line="$(grep -F "$freq MHz [" "$PHY" | head -n 1 || true)"
  if [[ -n "$line" && "$line" != *disabled* ]]; then
    FREQS="$FREQS $freq"
    FREQ_COUNT=$((FREQ_COUNT+1))
    say "MZ600_5G_PHY_CH_""$chan""_AVAILABLE"
  else
    say "MZ600_5G_PHY_CH_""$chan""_NOT_AVAILABLE"
  fi
done
total="$(awk '/MHz \[/ { if ($2+0 >= 5000 && $2+0 < 6000) count++ } END {print count+0}' "$PHY")"
say "MZ600_5G_PHY_TOTAL_5000_6000_MHZ_ENTRIES=$total"
if (( FREQ_COUNT == 0 )); then
  STATE=UNSUPPORTED
  say 'MZ600_5G_NO_ENABLED_NONDFS_LOW_BAND_CHANNELS'
  exit 0
fi
say "MZ600_5G_PASSIVE_SCAN_FREQ_COUNT=$FREQ_COUNT"
STATE=SCAN_STARTED
timeout -k 2s 10s ip link set wlan0 up
say 'MZ600_5G_LINK_UP_RC0'
set -- $FREQS
set +e
timeout -k 3s 38s iw dev wlan0 scan freq "$@" passive > "$RAW" 2>&1
scan_rc=$?
set -e
say "MZ600_5G_PASSIVE_SCAN_RC=$scan_rc"
say "MZ600_5G_PRIVATE_SCAN_BYTES=$(wc -c < "$RAW")"
say "MZ600_5G_PRIVATE_SCAN_SHA256=$(sha256sum "$RAW" | awk '{print $1}')"
if (( scan_rc != 0 )); then
  STATE=SCAN_FAILED
  exit 3
fi
count="$(grep -c '^BSS ' "$RAW" || true)"
say "MZ600_5G_PASSIVE_SCAN_BSS_COUNT=$count"
awk '/^[[:space:]]*freq:/ { if ($2+0>=5000 && $2+0<6000) f[$2]++ } END {for (k in f) print "MZ600_5G_RETURNED_FREQ_MHZ=" k " BSS=" f[k]}' "$RAW" | sort
STATE=SCAN_PASS
exit 0
