#!/usr/bin/env bash
# 2012 Broadcom BCM4329 firmware-only A/B, Single owner-authorized passive 2412 MHz/CH1 scan; no installation.
# Inputs (RAM): candidate .bin and previously ABI-matched passive-wiphy .ko.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
F='/lib/firmware/brcm/brcmfmac4329-sdio.bin'
N='/lib/firmware/brcm/brcmfmac4329-sdio.txt'
O="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
FW='/run/mz600-v15-oem2012.bin'
MOD='/run/mz600-v15-escan-event69.ko'
ONCE='/run/mz600-v15-2012-passive-2412-escan-20261026.attempted'
BF='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
BN='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
BO='9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb'
CF='5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834'
CM='8ab54acbb204aeab49bdbf2ef4265fc40c8454e8a5c07ba57d11028105c719f4'
STATE=PREFLIGHT
PASS=0
ARMED=0
msg() { printf '%s\n' "$*"; }
oksha() { printf '%s  %s\n' "$1" "$2" | sha256sum -c - >/dev/null 2>&1; }
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  if (( ARMED == 0 )); then
    msg "MZ600_V15_PREFLIGHT_STOP_NO_STATE_CHANGED rc=$rc"
    exit "$rc"
  fi
  msg "MZ600_V15_CLEANUP_START rc=$rc state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set wlan0 down >/dev/null 2>&1
    msg "MZ600_V15_LINK_DOWN_RC=$?"
  fi
  for mod in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 12s modprobe -r "$mod" >/dev/null 2>&1
    msg "MZ600_V15_UNLOAD_$mod=$?"
  done
  if mountpoint -q "$F"; then
    if oksha "$CF" "$F"; then
      timeout -k 2s 12s umount "$F"
      msg "MZ600_V15_UMOUNT_FIRMWARE_RC=$?"
    else
      msg 'MZ600_V15_UNEXPECTED_OVERLAY_HASH_REFUSE_BLIND_UNMOUNT'
    fi
  fi
  if ! mountpoint -q "$F" && ! mountpoint -q "$N" &&
     oksha "$BF" "$F" && oksha "$BN" "$N" && oksha "$BO" "$O" &&
     [[ ! -e /sys/class/net/wlan0 ]] &&
     ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    msg 'MZ600_V15_ORIGINAL_FILES_AND_RADIO_RESTORED'
  else
    msg 'MZ600_V15_ROLLBACK_UNVERIFIED_STOP'
    rc=91
  fi
  if (( PASS == 1 && rc == 0 )); then
    msg 'MZ600_V15_SINGLE_PASSIVE_SCAN_ATTEMPT_AND_CLEANUP'
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
msg 'MZ600_V15_PREFLIGHT_START'
[[ "$(id -u)" == 0 && "$(uname -r)" == "$K" ]] || exit 10
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || exit 11
[[ "$(cat /etc/debian_version)" == '12.15' ]] || exit 12
[[ ! -e "$ONCE" && ! -e /sys/class/net/wlan0 ]] || exit 13
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || exit 14
[[ -e /sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address ]] || exit 15
! mountpoint -q "$F" && ! mountpoint -q "$N" || exit 16
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|bluetooth|hci_uart) ' /proc/modules || exit 17
for srv in NetworkManager wpa_supplicant iwd; do
  ! systemctl is-active --quiet "$srv.service" || exit 18
done
oksha "$BF" "$F" && oksha "$BN" "$N" && oksha "$BO" "$O" &&
  oksha "$CF" "$FW" && oksha "$CM" "$MOD" || {
  msg 'MZ600_V15_PRECHECK_HASH_FAIL'
  exit 19
}
[[ "$(stat -c %s "$FW")" == 264140 &&
   "$(stat -c %s "$MOD")" == 344536 ]] || exit 20
msg 'MZ600_V15_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED'
LOG_LINE_BEFORE="$(dmesg | wc -l)"
: > "$ONCE"
ARMED=1
STATE=FIRMWARE_OVERLAY
timeout -k 2s 12s mount --bind "$FW" "$F"
mountpoint -q "$F" && oksha "$CF" "$F" || exit 21
msg 'MZ600_V15_TEMP_2012_FIRMWARE_OVERLAY_PASS'
STATE=MODULE_LOAD
timeout -k 2s 14s modprobe brcmutil
timeout -k 2s 22s insmod "$MOD"
set +e
timeout -k 3s 35s modprobe brcmfmac-wcc
wcc_rc=$?
set -e
msg "MZ600_V15_WCC_LOAD_RC=$wcc_rc"
STATE=OBSERVE
for i in $(seq 1 20); do
  [[ -e /sys/class/net/wlan0 ]] && break
  sleep .35
done
if [[ -e /sys/class/net/wlan0 ]]; then
  msg 'MZ600_V15_WLAN0_PRESENT'
  phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2;exit}')"
  if [[ "$phy" =~ ^[0-9]+$ ]]; then
    iw phy "phy$phy" info | awk '/MHz \[/ {if(($2+0)>=2400&&($2+0)<2500)n2++;if(($2+0)>=5000&&($2+0)<6000){n5++;if($0~/no IR/)no++;if($0~/disabled/)off++}}END{printf "MZ600_V15_PHY_2G=%d PHY_5G_TOTAL=%d PHY_5G_NO_IR=%d PHY_5G_DISABLED=%d\n",n2+0,n5+0,no+0,off+0}'
  fi
else
  msg 'MZ600_V15_WLAN0_ABSENT'
fi
msg 'MZ600_V15_FIRMWARE_BAND_DIAGNOSTICS_BEGIN'
msg "MZ600_V15_DMESG_LINES_BEFORE=$LOG_LINE_BEFORE"
dmesg | awk -v first="$LOG_LINE_BEFORE" 'NR>first' | grep -E 'MZ600_5G_DIAG_(BANDLIST|CHANSPECS|WIPHY|LEGACY_VALID_CHANNELS)|MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK|Firmware: BCM4329|brcmf_construct_chaninfo.*error|brcmf_bus_started.*failed' | tail -14 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[private-mac]/g' || true
msg 'MZ600_V15_FIRMWARE_BAND_DIAGNOSTICS_END'
# Strictly one permitted frequency: 2412 MHz (2.4 GHz ch1), non-DFS NO_IR.
[[ -e /sys/class/net/wlan0 && "$phy" =~ ^[0-9]+$ ]] || {
  msg 'MZ600_V15_STOP_NO_WLAN_OR_WIPHY'
  exit 30
}
ch1="$(iw phy "phy$phy" info | grep -F '2412 MHz [1]' | head -1)"
if [[ "$ch1" != *'no IR'* || "$ch1" == *disabled* || "$ch1" == *radar* ]]; then
  msg 'MZ600_V15_STOP_CHANNEL1_MUST_BE_NO_IR_NOT_DISABLED_NONDFS'
  exit 31
fi
msg 'MZ600_V15_CHANNEL1_NO_IR_NONDFS_PASS'
# All other scan selections are rejected independently inside v15 module.
STATE=PASSIVE_SCAN
set +e
timeout -k 2s 8s ip link set wlan0 up >/dev/null 2>&1
up_rc=$?
set -e
msg "MZ600_V15_LINK_UP_RC=$up_rc"
(( up_rc == 0 )) || exit 32
SCAN_OUTPUT='/run/mz600-v15-private-iw-results.txt'
[[ ! -e "$SCAN_OUTPUT" ]] || exit 33
start_ms="$(date +%s%3N)"
set +e
timeout -k 3s 24s iw dev wlan0 scan freq 2412 passive > "$SCAN_OUTPUT" 2>&1
scan_rc=$?
set -e
end_ms="$(date +%s%3N)"
msg "MZ600_V15_IW_PASSIVE_CH1_RC=$scan_rc ELAPSED_MS=$((end_ms-start_ms))"
n_bss="$(grep -c '^BSS ' "$SCAN_OUTPUT" || true)"
msg "MZ600_V15_USERSPACE_BSS_COUNT=$n_bss"
# Never print nearby SSID/BSSID names or MAC, even on failure.
if grep -q 'command failed' "$SCAN_OUTPUT"; then
  msg 'MZ600_V15_IW_REPORTED_COMMAND_FAILURE'
fi
rm -f "$SCAN_OUTPUT"
msg 'MZ600_V15_FRESH_SCAN_KERNEL_EVENTS_BEGIN'
dmesg | awk -v first="$LOG_LINE_BEFORE" 'NR>first' |
  grep -E 'MZ600_V15_|brcmf_run_escan: error|brcmf_cfg80211_scan: scan error|brcmf_inform_bss: Version|brcmf_escan_timeout: timer expired' |
  tail -36 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[private-mac]/g' || true
msg 'MZ600_V15_FRESH_SCAN_KERNEL_EVENTS_END'
dmesg | awk -v first="$LOG_LINE_BEFORE" 'NR>first && /MZ600_V15_EVENT69 status=/ {if($0 ~ /status=0 /)success++;else if($0 ~ /status=8 /)partial++;else other++} END {printf "MZ600_V15_EVENT69_STATUS_COUNTS success=%d partial=%d other=%d\n",success+0,partial+0,other+0}'

msg 'MZ600_V15_NO_ASSOCIATION_OR_DIRECTED_SSID'
PASS=1
STATE=OBSERVATION_COMPLETE
exit 0
