#!/usr/bin/env bash
# ONE-SHOT LAB: original HRI39 passive channel36 WLC_SCAN50 + count-only SCAN_RESULTS51.
# User-approved single passive RF scan ONLY on permitted NO_IR channel36; no probe/association/flash.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
F='/lib/firmware/brcm/brcmfmac4329-sdio.bin'
N='/lib/firmware/brcm/brcmfmac4329-sdio.txt'
M='/run/mz600-v064-legacy-singlepassive5g-v7.ko'
O="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
V='/run/mz600-hri39-v7-passive-scan-cal-20261026.txt'
OEM_FW='/run/mz600-hri39-original-fw-only-20261026.bin'
ONCE='/run/mz600-hri39-v7-passive-singlechannel-scan-20261026.attempted'
PRIVATE='/run/mz600-hri39-v7-passive-scan-private-20261026'
SF='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
SN='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
SM='ca2dbbf1131a44515b724b38f3ce3a7e7a6b8a7712ecceea404c833aa0f3ffec'
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
  say "MZ600_PASSIVE_V7_CLEANUP_BEGIN prior_rc=$rc state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set dev wlan0 down
    say "MZ600_PASSIVE_V7_LINK_DOWN_RC=$?"
  fi
  for mod in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 12s modprobe -r "$mod" >/dev/null 2>&1
    say "MZ600_PASSIVE_V7_UNLOAD_""$mod""_RC=$?"
  done
  if mountpoint -q "$N"; then
    if hash_ok "$SV" "$N"; then
      timeout -k 2s 12s umount "$N"
      say "MZ600_PASSIVE_V7_UNMOUNT_RC=$?"
    else
      say 'MZ600_PASSIVE_V7_UNEXPECTED_OVERLAY_STOP'
    fi
  fi
  if mountpoint -q "$F"; then
    if hash_ok "$OEM_SHA" "$F"; then
      timeout -k 2s 12s umount "$F"
      say "MZ600_PASSIVE_V7_FIRMWARE_UNMOUNT_RC=$?"
    else
      say "MZ600_PASSIVE_V7_UNEXPECTED_FIRMWARE_MOUNT_STOP"
    fi
  fi
  rm -f "$PRIVATE.stdout" "$PRIVATE.stderr"
  sleep 1
  if ! mountpoint -q "$N" && ! mountpoint -q "$F" && hash_ok "$SN" "$N" &&
     hash_ok "$SF" "$F" && hash_ok "$SO" "$O" &&
     [[ ! -e /sys/class/net/wlan0 ]] &&
     ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    say 'MZ600_PASSIVE_V7_ORIGINAL_FILES_AND_RADIO_RESTORED'
    if (( FINISHED == 1 )); then
      say 'MZ600_PASSIVE_V7_READBACK_A_B_PHYSICAL_PASS_CLEAN'
    fi
  else
    say 'MZ600_PASSIVE_V7_RESTORE_INCOMPLETE_STOP'
  fi
}
say 'MZ600_PASSIVE_V7_PREFLIGHT_BEGIN'
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
say 'MZ600_PASSIVE_V7_BASELINE_SHA_PASS'
awk 'NR == 71 { print "ccode=US"; print "regrev=69" } { print }' "$N" > "$V"
[[ "$(stat -c %s "$V")" == 1569 ]] && hash_ok "$SV" "$V" || {
  say 'REFUSE_VARIANT_SHA'; exit 1;
}
say 'MZ600_PASSIVE_V7_CALIBRATION_RECONSTRUCTION_SHA_PASS'
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
: > "$ONCE"
before="$(dmesg | grep -c 'MZ600_LEGACY_SCAN_LAB_RESULT51' || true)"
STATE=OVERLAY
timeout -k 2s 12s mount --bind "$V" "$N"
mountpoint -q "$N" && hash_ok "$SV" "$N" || {
  say 'REFUSE_MOUNT_OVERLAY_SHA'; exit 2;
}
timeout -k 2s 12s mount --bind "$OEM_FW" "$F"
mountpoint -q "$F" && hash_ok "$OEM_SHA" "$F" || {
  say "MZ600_PASSIVE_V7_IMAGE_OVERLAY_FAILED"; exit 2;
}
say 'MZ600_PASSIVE_V7_OEM_FIRMWARE_AND_COUNTRY_REV_IN_RAM_AT_BOOT'
STATE=LOADING
timeout -k 2s 14s modprobe brcmutil
say 'MZ600_PASSIVE_V7_BRCMUTIL_RC0'
timeout -k 2s 22s insmod "$M"
say 'MZ600_PASSIVE_V7_DIAGNOSTIC_RC0'
set +e
timeout -k 3s 35s modprobe brcmfmac-wcc
wcc_rc=$?
set -e
say "MZ600_PASSIVE_V7_WCC_LOAD_RC=$wcc_rc"
STATE=OBSERVE
for i in $(seq 1 30); do
  [[ -e /sys/class/net/wlan0 ]] && break
  sleep .35
done
if [[ -e /sys/class/net/wlan0 ]]; then
  say 'MZ600_PASSIVE_V7_WLAN0_PRESENT'
  phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2; exit}')"
  if [[ "$phy" =~ ^[0-9]+$ ]]; then
    say "MZ600_PASSIVE_V7_DYNAMIC_PHY=$phy"
    iw phy "phy$phy" info | awk '/MHz \[/ {if (($2+0)>=5000 && ($2+0)<6000) n++} END {printf "MZ600_PASSIVE_V7_PHY_5GHZ_FREQ_COUNT=%d\n",n+0}'
  fi
else
  say 'MZ600_PASSIVE_V7_WLAN0_NOT_CREATED'
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
timeout -k 3s 26s iw dev wlan0 scan passive freq 5180 > "$PRIVATE.stdout" 2> "$PRIVATE.stderr"
scan_rc=$?
set -e
say "ONE_CHANNEL_PASSIVE_IW_SCAN_RC=$scan_rc"
after="$(dmesg | grep -c 'MZ600_LEGACY_SCAN_LAB_RESULT51' || true)"
say "MZ600_PASSIVE_V7_COUNTRY_LOGS_BEFORE=$before AFTER=$after"
if (( after <= before )); then
  say "MZ600_PASSIVE_V7_FIRMWARE_COUNTRY_LOG_NOT_REACHED"
else
  say 'MZ600_PASSIVE_V7_FIRMWARE_DIAGNOSTICS_BEGIN'
  dmesg | grep -E 'MZ600_LEGACY_SCAN_LAB_(START|COMMAND50_RC|RESULT51)' | tail -3
  say 'MZ600_PASSIVE_V7_FIRMWARE_DIAGNOSTICS_END'
fi
say 'MZ600_PASSIVE_V7_RELEVANT_INIT_LOGS_BEGIN'
dmesg | grep -Ei 'brcmf.*(firmware|f2|sdio|timeout|failed|chip|version)' | tail -9 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[redacted]/g' || true
say 'MZ600_PASSIVE_V7_RELEVANT_INIT_LOGS_END'
if (( scan_rc != 0 )) || (( after <= before )); then
  say 'LEGACY_PASSIVE_SCAN_PROOF_INCOMPLETE'; exit 3;
fi
FINISHED=1
STATE=OBSERVATION_COMPLETE
exit 0
