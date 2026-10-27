#!/usr/bin/env bash
# 2012 Broadcom BCM4329 firmware-only A/B, Normal cfg80211 scans; read-only firmware UP and MPC snapshots; no installation.
# Inputs (RAM): candidate .bin and new ABI-matched V30 firmware UP/MPC read-only diagnostic .ko.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
F='/lib/firmware/brcm/brcmfmac4329-sdio.bin'
N='/lib/firmware/brcm/brcmfmac4329-sdio.txt'
O="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
WI="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko"
BW='31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80' 
FW='/run/mz600-v30-oem2012.bin'
MOD='/run/mz600-v30-escan-event69.ko'
WC='/run/mz600-v30d-matched-wcc.ko'
CW='6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d' 
# Owner parameters: one bitmask configuration and one unique trial identity.
MASK="${1:-}"
TRIAL="${2:-}"
ONCE="/run/mz600-v30-eventmask-${MASK}-trial-${TRIAL}.attempted"
BF='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
BN='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
BO='9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb'
CF='5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834'
CM='c064cd5c23c50d423e1c09be106e61633bdf35ef57046d00f211e10659223738'
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
    msg "MZ600_V30_PREFLIGHT_STOP_NO_STATE_CHANGED rc=$rc"
    exit "$rc"
  fi
  msg "MZ600_V30_CLEANUP_START rc=$rc state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set wlan0 down >/dev/null 2>&1
    msg "MZ600_V30_LINK_DOWN_RC=$?"
  fi
  for mod in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 12s modprobe -r "$mod" >/dev/null 2>&1
    msg "MZ600_V30_UNLOAD_$mod=$?"
  done
  if mountpoint -q "$WI"; then
    if oksha "$CW" "$WI"; then
      timeout -k 2s 12s umount "$WI"
      msg "MZ600_V30_UMOUNT_MATCHED_WCC_RC=$?"
    else
      msg 'MZ600_V30_UNEXPECTED_WCC_OVERLAY_HASH_REFUSE_UNMOUNT'
    fi
  fi
  if mountpoint -q "$F"; then
    if oksha "$CF" "$F"; then
      timeout -k 2s 12s umount "$F"
      msg "MZ600_V30_UMOUNT_FIRMWARE_RC=$?"
    else
      msg 'MZ600_V30_UNEXPECTED_OVERLAY_HASH_REFUSE_BLIND_UNMOUNT'
    fi
  fi
  if ! mountpoint -q "$F" && ! mountpoint -q "$N" &&
     ! mountpoint -q "$WI" && oksha "$BW" "$WI" &&
     oksha "$BF" "$F" && oksha "$BN" "$N" && oksha "$BO" "$O" &&
     [[ ! -e /sys/class/net/wlan0 ]] &&
     ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    msg 'MZ600_V30_ORIGINAL_FILES_AND_RADIO_RESTORED'
  else
    msg 'MZ600_V30_ROLLBACK_UNVERIFIED_STOP'
    rc=91
  fi
  if (( PASS == 1 && rc == 0 )); then
    msg "MZ600_V30_SINGLE_PASSIVE_SCAN_ATTEMPT_AND_CLEANUP mask=$MASK trial=$TRIAL"
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
msg 'MZ600_V30_PREFLIGHT_START'
if [[ ! "$MASK" =~ ^(0|[1-9][0-9]{0,2})$ ]] || (( MASK > 1 )) ||
   [[ ! "$TRIAL" =~ ^[A-Za-z0-9_-]{1,24}$ ]]; then
  msg 'MZ600_V30_BAD_MASK_OR_TRIAL'
  exit 9
fi
msg "MZ600_V30_CONFIG mask=$MASK trial=$TRIAL"
[[ "$(id -u)" == 0 && "$(uname -r)" == "$K" ]] || exit 10
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || exit 11
[[ "$(cat /etc/debian_version)" == '12.15' ]] || exit 12
[[ ! -e "$ONCE" && ! -e /sys/class/net/wlan0 ]] || exit 13
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || exit 14
[[ -e /sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address ]] || exit 15
! mountpoint -q "$F" && ! mountpoint -q "$N" || exit 16
! mountpoint -q "$WI" && oksha "$BW" "$WI" || exit 16
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules || exit 17
# Loaded but inactive BT stack is preserved (no BT service/HCI traffic).
! systemctl is-active --quiet bluetooth.service || exit 17
if [[ -d /sys/class/bluetooth/hci0 ]]; then
  if hciconfig hci0 2>/dev/null | grep -Fq 'UP RUNNING'; then
    msg 'MZ600_V30_STOP_BT_HCI_ACTIVE'
    exit 17
  fi
fi
msg 'MZ600_V30_QUIESCENT_BT_STACK_PRESERVED'
for srv in NetworkManager wpa_supplicant iwd; do
  ! systemctl is-active --quiet "$srv.service" || exit 18
done
oksha "$BF" "$F" && oksha "$BN" "$N" && oksha "$BO" "$O" &&
  oksha "$BW" "$WI" && oksha "$CF" "$FW" &&
  oksha "$CM" "$MOD" && oksha "$CW" "$WC" || {
  msg 'MZ600_V30_PRECHECK_HASH_FAIL'
  exit 19
}
[[ "$(stat -c %s "$FW")" == 264140 &&
   "$(stat -c %s "$MOD")" == 353372 && "$(stat -c %s "$WC")" == 5892 ]] || exit 20
msg 'MZ600_V30_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED'
KMSG_MARKER="MZ600_V30_${TRIAL}_${MASK}_KMSG_BEGIN"
printf "<6>%s\n" "$KMSG_MARKER" > /dev/kmsg
dmesg | grep -Fq "$KMSG_MARKER" || exit 40
: > "$ONCE"
ARMED=1
STATE=FIRMWARE_OVERLAY
timeout -k 2s 12s mount --bind "$FW" "$F"
mountpoint -q "$F" && oksha "$CF" "$F" || exit 21
msg 'MZ600_V30_TEMP_2012_FIRMWARE_OVERLAY_PASS'
STATE=WCC_OVERLAY
timeout -k 2s 12s mount --bind "$WC" "$WI"
mountpoint -q "$WI" && oksha "$CW" "$WI" || exit 24
msg 'MZ600_V30_TEMP_MATCHED_WCC_OVERLAY_PASS'
STATE=MODULE_LOAD
timeout -k 2s 14s modprobe brcmutil
# Selector is one-shot only; module automatically rotates scan IDs.
timeout -k 2s 22s insmod "$MOD" mz600_extra_events=0 mz600_terminal_owner=1 mz600_request_sync_id=4660 mz600_generation=1
actual="$(cat /sys/module/brcmfmac/parameters/mz600_generation)"
expected=Y
if [[ "$actual" != "$expected" ]]; then
  msg "MZ600_V30_MASK_READBACK_FAIL requested=$MASK actual=$actual"
  exit 22
fi
[[ "$(cat /sys/module/brcmfmac/parameters/mz600_extra_events)" == "0" ]] || exit 22
[[ "$(cat /sys/module/brcmfmac/parameters/mz600_terminal_owner)" == "Y" ]] || exit 22
msg "MZ600_V30_GENERATION_SWITCH_ENABLED=1"
msg "MZ600_V30_MASK_READBACK_PASS mask=$MASK"
set +e
timeout -k 3s 35s modprobe brcmfmac-wcc
wcc_rc=$?
set -e
msg "MZ600_V30_WCC_LOAD_RC=$wcc_rc"
(( wcc_rc == 0 )) || { msg 'MZ600_V30_STOP_MATCHED_WCC_LOAD_FAIL'; exit 29; }
msg 'MZ600_V30_MATCHED_COMPANION_MODULE_LOADED_SHA_PASS' 
STATE=OBSERVE
for i in $(seq 1 20); do
  [[ -e /sys/class/net/wlan0 ]] && break
  sleep .35
done
if [[ -e /sys/class/net/wlan0 ]]; then
  msg 'MZ600_V30_WLAN0_PRESENT'
  phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2;exit}')"
  if [[ "$phy" =~ ^[0-9]+$ ]]; then
    iw phy "phy$phy" info | awk '/MHz \[/ {if(($2+0)>=2400&&($2+0)<2500)n2++;if(($2+0)>=5000&&($2+0)<6000){n5++;if($0~/no IR/)no++;if($0~/disabled/)off++}}END{printf "MZ600_V30_PHY_2G=%d PHY_5G_TOTAL=%d PHY_5G_NO_IR=%d PHY_5G_DISABLED=%d\n",n2+0,n5+0,no+0,off+0}'
  fi
else
  msg 'MZ600_V30_WLAN0_ABSENT'
fi
msg 'MZ600_V30_FIRMWARE_BAND_DIAGNOSTICS_BEGIN'
msg "MZ600_V30_KMSG_MARKER=$KMSG_MARKER"
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen' | grep -E 'MZ600_5G_DIAG_(BANDLIST|CHANSPECS|WIPHY|LEGACY_VALID_CHANNELS)|MZ600_V30_LEGACY_VALID_CHANNEL_FALLBACK|Firmware: BCM4329|brcmf_construct_chaninfo.*error|brcmf_bus_started.*failed' | tail -14 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[private-mac]/g' || true
msg 'MZ600_V30_FIRMWARE_BAND_DIAGNOSTICS_END'
# The driver no longer limits channel, SSIDs, probe mode or NO_IR state.
# cfg80211 validates regulatory permissions; avoid hardcoded per-band policy.
[[ -e /sys/class/net/wlan0 && "$phy" =~ ^[0-9]+$ ]] || {
 msg 'MZ600_V30_STOP_NO_WLAN_OR_WIPHY'
 exit 30
}
msg 'MZ600_V30_NATIVE_CFG80211_SCAN_POLICY'

STATE=PASSIVE_SCAN
set +e
timeout -k 2s 8s ip link set wlan0 up >/dev/null 2>&1
up_rc=$?
set -e
msg "MZ600_V30_LINK_UP_RC=$up_rc"
(( up_rc == 0 )) || exit 32
# Two ordinary scans in one module. Preserve firmware-state evidence on failure.
fail_seen=0
scan_successes=0
last_ms=0
last_bss=0
for seq in 1 2; do
  SCAN_OUTPUT="/run/mz600-v30-private-iw-results-$seq.txt"
  [[ ! -e "$SCAN_OUTPUT" ]] || exit 33
  msg "MZ600_V30_SEQ_BEGIN idx=$seq"
  start_ms="$(date +%s%3N)"
  set +e
  timeout -k 3s 24s iw dev wlan0 scan > "$SCAN_OUTPUT" 2>&1
  scan_rc=$?
  set -e
  end_ms="$(date +%s%3N)"
  n_bss="$(grep -c '^BSS ' "$SCAN_OUTPUT" || true)"
  msg "MZ600_V30_SEQ_SCAN idx=$seq iw_rc=$scan_rc elapsed_ms=$((end_ms-start_ms)) bss=$n_bss"
  if ((scan_rc != 0 )); then
    failmsg="$(head -n 2 "$SCAN_OUTPUT" | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[private-mac]/g' | tr '\n' ' ' | cut -c1-180)"
    msg "MZ600_V30_IW_SCAN_FAILURE idx=$seq rc=$scan_rc reason=$failmsg"
  fi
  rm -f "$SCAN_OUTPUT"
  if (( scan_rc != 0 )); then
    fail_seen=1
    break
  fi
  if (( n_bss == 0 )); then
    fail_seen=1
    break
  fi
  scan_successes=$((scan_successes+1))
  last_ms=$((end_ms-start_ms))
  last_bss=$n_bss
  sleep 4
done
msg "MZ600_V30_IW_NATIVE_SCAN_RC=$fail_seen ELAPSED_MS=$last_ms"
msg "MZ600_V30_USERSPACE_BSS_COUNT=$last_bss"
msg "MZ600_V30_SCAN_SUITE_RESULT completed=$scan_successes failure=$fail_seen"
msg 'MZ600_V30_FW_STATE_NUMERIC_TRACE_BEGIN'
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen' |
  grep -E 'MZ600_V30_(FW_STATE|MPC_SET|NEW_SCAN_GENERATION|SCAN_REQUEST_SYNC|TERMINAL_SYNC|TERMINAL_GENERATION_ACCEPT|SCAN_COMPLETION|ESCAN_SET_RC)' | tail -n 100 || true
msg 'MZ600_V30_FW_STATE_NUMERIC_TRACE_END'
msg 'MZ600_V30_FRESH_SCAN_KERNEL_EVENTS_BEGIN'
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen' |
  grep -E 'MZ600_V30_|brcmf_run_escan: error|brcmf_cfg80211_scan: scan error|brcmf_inform_bss: Version|brcmf_escan_timeout: timer expired' |
  tail -140 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[private-mac]/g' || true
msg 'MZ600_V30_FRESH_SCAN_KERNEL_EVENTS_END'
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen && /MZ600_V30_FWEH_(DROP|ADMIT|WORKER|DISPATCH)/ {if($0~/FWEH_DROP/)drop++;if($0~/FWEH_ADMIT/)admit++;if($0~/FWEH_WORKER/)worker++;if($0~/FWEH_DISPATCH/)dispatch++;if($0~/status=0 /)term++} END {printf "MZ600_V30_DELIVERY_STAGE_COUNTS drop=%d admitted=%d worker=%d dispatch=%d stage_terminal_mentions=%d\n",drop+0,admit+0,worker+0,dispatch+0,term+0}'

dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen && /MZ600_V30_FWEH_INGRESS code=/ {split($0,a,"code=");split(a[2],b," "); if(b[1]~/^[0-9]+$/) n[b[1]]++} END {for(k in n)printf "MZ600_V30_RX_EVENT_COUNT code=%s count=%d\n",k,n[k]}' | sort -V
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen && /MZ600_V30_ALT_EVENT code=/ {total++; if($0~/status=0 /) ok++} END {printf "MZ600_V30_ALTERNATIVE_EVENT_COUNTS total=%d success_status=%d\n",total+0,ok+0}'
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen && /MZ600_V30_BSS_META / {num++;if($0~/hidden=1 /) hidden++;if($0~/ie_bounds_ok=0 /) malformed++;if($0~/ctl_ch=36 /) ch36++} END {printf "MZ600_V30_METADATA_COUNTS total=%d hidden=%d malformed=%d ctl_ch36=%d\n",num+0,hidden+0,malformed+0,ch36+0}'
msg 'MZ600_V30_ALL_COMPLETION_PATHS_SUMMARY_END'
dmesg | awk -v marker="$KMSG_MARKER" 'index($0,marker){seen=1;next} seen && /MZ600_V30_EVENT69 status=/ {if($0 ~ /status=0 /)success++;else if($0 ~ /status=8 /)partial++;else other++} END {printf "MZ600_V30_EVENT69_STATUS_COUNTS success=%d partial=%d other=%d\n",success+0,partial+0,other+0}'

msg 'MZ600_V30_NO_ASSOCIATION_OR_DIRECTED_SSID'
if ((fail_seen != 0)); then
  msg 'MZ600_V30_SCAN_SUITE_FAILED_NUMERIC_TRACE_PRESERVED'
  exit 38
fi
PASS=1
STATE=OBSERVATION_COMPLETE
exit 0

