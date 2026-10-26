#!/usr/bin/env bash
# V12B owner-operated NEW one-shot: observe numeric firmware RX/event26 stages.
# User-approved single passive RF scan ONLY on permitted NO_IR channel36; no probe/association/flash.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
F='/lib/firmware/brcm/brcmfmac4329-sdio.bin'
N='/lib/firmware/brcm/brcmfmac4329-sdio.txt'
M='/run/mz600-v064-legacy-v12b-event26-rx-gates-20261026.ko'
O="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
V='/run/mz600-hri39-v12b-scan-cal-20261026.txt'
OEM_FW='/run/mz600-hri39-original-fw-only-20261026.bin'
ONCE='/run/mz600-hri39-v12b-event26-mask-20261026.attempted'
PRIVATE='/run/mz600-hri39-v12b-mask-private-20261026'
SF='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
SN='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
SM='48bf1d3f5cc163f33419e3ebddaa4b50067096e6c1954ced578568c86c75f5b6'
SO='9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb'
SV='6de236d4d097f4996e1fef31d538757bfd9f4024cbcf2ade8bbaa97c040e53c4'
OEM_SHA='7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a'
STATE=PREFLIGHT
FINISHED=0
say() { printf '%s\n' "$*"; }
hash_ok() { printf '%s  %s\n' "$1" "$2" | sha256sum -c - >/dev/null 2>&1; }
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  say "MZ600_PASSIVE_V12B_CLEANUP_BEGIN prior_rc=$rc state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set dev wlan0 down
    say "MZ600_PASSIVE_V12B_LINK_DOWN_RC=$?"
  fi
  for mod in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 12s modprobe -r "$mod" >/dev/null 2>&1
    say "MZ600_PASSIVE_V12B_UNLOAD_""$mod""_RC=$?"
  done
  if mountpoint -q "$N"; then
    if hash_ok "$SV" "$N"; then
      timeout -k 2s 12s umount "$N"
      say "MZ600_PASSIVE_V12B_UNMOUNT_RC=$?"
    else
      say 'MZ600_PASSIVE_V12B_UNEXPECTED_OVERLAY_STOP'
    fi
  fi
  if mountpoint -q "$F"; then
    if hash_ok "$OEM_SHA" "$F"; then
      timeout -k 2s 12s umount "$F"
      say "MZ600_PASSIVE_V12B_FIRMWARE_UNMOUNT_RC=$?"
    else
      say "MZ600_PASSIVE_V12B_UNEXPECTED_FIRMWARE_MOUNT_STOP"
    fi
  fi
  rm -f "$PRIVATE.stdout" "$PRIVATE.stderr"
  sleep 1
  if ! mountpoint -q "$N" && ! mountpoint -q "$F" && hash_ok "$SN" "$N" &&
     hash_ok "$SF" "$F" && hash_ok "$SO" "$O" &&
     [[ ! -e /sys/class/net/wlan0 ]] &&
     ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    say 'MZ600_PASSIVE_V12B_ORIGINAL_FILES_AND_RADIO_RESTORED'
    if (( FINISHED == 1 )); then
      say 'MZ600_PASSIVE_V12B_READBACK_A_B_PHYSICAL_PASS_CLEAN'
    fi
  else
    say 'MZ600_PASSIVE_V12B_RESTORE_INCOMPLETE_STOP'
  fi
}
say 'MZ600_PASSIVE_V12B_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 && "$(uname -r)" == "$K" ]] || exit 1
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || exit 1
[[ "$(cat /etc/debian_version)" == '12.15' ]] || exit 1
[[ ! -e "$V" && ! -e "$ONCE" && ! -e "$PRIVATE.stdout" && ! -e "$PRIVATE.stderr" ]] || { say 'REFUSE_VARIANT_ALREADY_TESTED'; exit 1; }
! mountpoint -q "$N" && ! mountpoint -q "$F" || exit 1
[[ ! -e /sys/class/net/wlan0 ]] || exit 1
[[ -e /sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address ]] || exit 1
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || exit 1
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|bluetooth|hci_uart) ' /proc/modules || exit 1
for srv in NetworkManager wpa_supplicant iwd; do
  ! systemctl is-active --quiet "$srv.service" || exit 1
done
iw reg get | grep -q '^country 00:' || { say 'REFUSE_REGULATORY_WORLD_CHANGED'; exit 1; }
hash_ok "$SF" "$F" && hash_ok "$SN" "$N" && hash_ok "$SO" "$O" && hash_ok "$SM" "$M" && hash_ok "$OEM_SHA" "$OEM_FW" && [[ "$(stat -c %s "$OEM_FW")" == 261317 ]] || {
  say 'REFUSE_BASELINE_SHA'; exit 1;
}
say 'MZ600_PASSIVE_V12B_BASELINE_SHA_PASS'
awk 'NR == 71 { print "ccode=US"; print "regrev=69" } { print }' "$N" > "$V"
[[ "$(stat -c %s "$V")" == 1569 ]] && hash_ok "$SV" "$V" || {
  say 'REFUSE_VARIANT_SHA'; exit 1;
}
say 'MZ600_PASSIVE_V12B_CALIBRATION_RECONSTRUCTION_SHA_PASS'
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
: > "$ONCE"
before="$(dmesg | grep -c 'MZ600_LEGACY_SCAN_LAB_RESULT51' || true)"
mask_before="$(dmesg | grep -c 'MZ600_LEGACY_EVENT26_MASK_READBACK' || true)"
path_before="$(dmesg | grep -c 'MZ600_V12B_EVENT_RX stage=' || true)"
STATE=OVERLAY
timeout -k 2s 12s mount --bind "$V" "$N"
mountpoint -q "$N" && hash_ok "$SV" "$N" || {
  say 'REFUSE_MOUNT_OVERLAY_SHA'; exit 2;
}
timeout -k 2s 12s mount --bind "$OEM_FW" "$F"
mountpoint -q "$F" && hash_ok "$OEM_SHA" "$F" || {
  say "MZ600_PASSIVE_V12B_IMAGE_OVERLAY_FAILED"; exit 2;
}
say 'MZ600_PASSIVE_V12B_OEM_FIRMWARE_AND_COUNTRY_REV_IN_RAM_AT_BOOT'
STATE=LOADING
timeout -k 2s 14s modprobe brcmutil
say 'MZ600_PASSIVE_V12B_BRCMUTIL_RC0'
timeout -k 2s 22s insmod "$M"
say 'MZ600_PASSIVE_V12B_DIAGNOSTIC_RC0'
set +e
timeout -k 3s 35s modprobe brcmfmac-wcc
wcc_rc=$?
set -e
say "MZ600_PASSIVE_V12B_WCC_LOAD_RC=$wcc_rc"
STATE=OBSERVE
for i in $(seq 1 30); do
  [[ -e /sys/class/net/wlan0 ]] && break
  sleep .35
done
if [[ -e /sys/class/net/wlan0 ]]; then
  say 'MZ600_PASSIVE_V12B_WLAN0_PRESENT'
  phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2; exit}')"
  if [[ "$phy" =~ ^[0-9]+$ ]]; then
    say "MZ600_PASSIVE_V12B_DYNAMIC_PHY=$phy"
    iw phy "phy$phy" info | awk '/MHz \[/ {if (($2+0)>=5000 && ($2+0)<6000) n++} END {printf "MZ600_PASSIVE_V12B_PHY_5GHZ_FREQ_COUNT=%d\n",n+0}'
  fi
else
  say 'MZ600_PASSIVE_V12B_WLAN0_NOT_CREATED'
fi
# Strict fail-closed channel 36 gate: supported by firmware and cfg80211,
# actually enabled, and marked no-initiating-radiation.
freqline="$(iw phy "phy$phy" info | grep -E '5180(\.0)? MHz \[36\]' | head -1 || true)"
[[ -n "$freqline" && "$freqline" == *"no IR"* &&
   "$freqline" != *"disabled"* && "$freqline" != *"radar"* ]] || {
   say 'NO_CHANNEL36_PASSIVE_NOIR_GATE_REFUSE_SCAN'; exit 3;
}
say 'CHANNEL36_NOIR_NONDISABLED_VERIFIED'
timeout -k 3s 12s ip link set dev wlan0 up
say 'ONE_CHANNEL_PASSIVE_IW_SCAN_BEGIN_5180'
set +e
timeout -k 3s 26s iw dev wlan0 scan freq 5180 passive > "$PRIVATE.stdout" 2> "$PRIVATE.stderr"
scan_rc=$?
set -e
say "ONE_CHANNEL_PASSIVE_IW_SCAN_RC=$scan_rc"
# Only publish integer count, never BSSID/SSID/IE bytes.
iw_bss_count="$(grep -c '^BSS ' "$PRIVATE.stdout" || true)"
say "MZ600_V12B_USERSPACE_IW_BSS_LINES=$iw_bss_count"
say "IW_STDERR_BYTES=$(wc -c < "$PRIVATE.stderr")"
if grep -qi 'Invalid parameters' "$PRIVATE.stderr"; then
  say 'IW_ERROR_CATEGORY=USERSPACE_INVALID_PARAMETERS'
elif grep -qi 'command failed' "$PRIVATE.stderr"; then
  say 'IW_ERROR_CATEGORY=NETLINK_COMMAND_FAILED'
  grep -oE '\(-[0-9]+\)' "$PRIVATE.stderr" | head -1 | sed 's/^/IW_NETLINK_NEGATIVE_ERRNO=/' || true
elif grep -qi 'Operation not permitted' "$PRIVATE.stderr"; then
  say 'IW_ERROR_CATEGORY=OPERATION_NOT_PERMITTED'
elif grep -qi 'Network is down' "$PRIVATE.stderr"; then
  say 'IW_ERROR_CATEGORY=NETWORK_DOWN'
elif [[ -s "$PRIVATE.stderr" ]]; then
  say 'IW_ERROR_CATEGORY=OTHER_PRIVATE_STDERR_NOT_DISPLAYED'
else
  say 'IW_ERROR_CATEGORY=EMPTY_STDERR'
fi
after="$(dmesg | grep -c 'MZ600_LEGACY_SCAN_LAB_RESULT51' || true)"
validated="$(dmesg | grep -c 'MZ600_LEGACY_BSS108_VALIDATION' || true)"
events="$(dmesg | grep -c 'MZ600_LEGACY_SCAN_EVENT26' || true)"
say "MZ600_V12B_BSS108_VALIDATION_LOG_LINES=$validated"
say "MZ600_V12B_LEGACY_EVENT26_LOG_LINES=$events"
say "MZ600_PASSIVE_V12B_COUNTRY_LOGS_BEFORE=$before AFTER=$after"
if (( after <= before )); then
  say "MZ600_PASSIVE_V12B_FIRMWARE_COUNTRY_LOG_NOT_REACHED"
else
  say 'MZ600_PASSIVE_V12B_FIRMWARE_DIAGNOSTICS_BEGIN'
  dmesg | grep -E 'MZ600_LEGACY_(SCAN_LAB_(START|COMMAND50_RC|RESULT51)|BSS108_VALIDATION|SCAN_EVENT26|CFG80211_BSS_INFORM)' | tail -7
  say 'MZ600_PASSIVE_V12B_FIRMWARE_DIAGNOSTICS_END'
fi
say 'MZ600_PASSIVE_V12B_RELEVANT_INIT_LOGS_BEGIN'
dmesg | grep -Ei 'brcmf.*(firmware|f2|sdio|timeout|failed|chip|version)' | tail -9 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[redacted]/g' || true
say 'MZ600_PASSIVE_V12B_RELEVANT_INIT_LOGS_END'
v108_last="$(dmesg | grep 'MZ600_LEGACY_BSS108_VALIDATION' | tail -1 || true)"
# v12b asks ONE new firmware-mask question. No requirement for populated
# BSS: empty scans are possible and do not establish scan completion.
mask_after="$(dmesg | grep -c 'MZ600_LEGACY_EVENT26_MASK_READBACK' || true)"
mask_last="$(dmesg | grep 'MZ600_LEGACY_EVENT26_MASK_READBACK' | tail -1 || true)"
say "MZ600_V12B_MASK_LOGS_BEFORE=$mask_before AFTER=$mask_after"
if (( mask_after <= mask_before )) || [[ -z "$mask_last" ]]; then
  say 'MZ600_V12B_MASK_READBACK_MISSING_IN_CURRENT_ATTEMPT'; exit 4;
fi
# Marker contains numeric rc/mask bits only; network identifiers never logged.
say "$mask_last"
say 'MZ600_V12B_MASK_OBSERVATION_RECORDED'
path_after="$(dmesg | grep -c 'MZ600_V12B_EVENT_RX stage=' || true)"
say "MZ600_V12B_PATH_LOGS_BEFORE=$path_before AFTER=$path_after"
if (( path_after < path_before + 2 )); then
  say 'MZ600_V12B_EVENT_PATH_START_OR_TIMEOUT_MISSING'; exit 6;
fi
say 'MZ600_V12B_EVENT_PATH_NUMERIC_COUNTERS_BEGIN'
dmesg | grep 'MZ600_V12B_EVENT_RX stage=' | tail -2
say 'MZ600_V12B_EVENT_PATH_NUMERIC_COUNTERS_END'
say 'MZ600_V12B_EVENT_PATH_OBSERVATION_RECORDED'
if (( scan_rc != 0 )); then
  say 'MZ600_V12B_SCAN_REQUEST_FAILED_SAFE_RESTORE'; exit 5;
fi
FINISHED=1
STATE=EVENT_RX_OBSERVATION_COMPLETE
exit 0
