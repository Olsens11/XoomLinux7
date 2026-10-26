#!/usr/bin/env bash
# First guarded 5GHz PASSIVE scan with BCM4329 OEM legacy no-IR band fallback.
# NO ACTIVE SCAN/ASSOCIATION; only verified passive channels 36 40 44 48.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
F='/lib/firmware/brcm/brcmfmac4329-sdio.bin'
N='/lib/firmware/brcm/brcmfmac4329-sdio.txt'
M='/run/mz600-v064-legacy-passive-only-wiphy-v5.ko'
O="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
V='/run/mz600-hri39-5ghz-passive-scan-cal-20261026.txt'
PRIVATE_SCAN='/run/mz600-hri39-5ghz-passive-scan-output-private-20261026.txt'
OEM_FW='/run/mz600-hri39-original-fw-only-20261026.bin'
ONCE='/run/mz600-hri39-5ghz-passive-scan-20261026.attempted'
SF='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
SN='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
SM='ff19d91726f406468d6cc9516d43a851f6a7a22d403259094ae376041671db29'
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
  say "MZ600_HRI39_SCAN_CLEANUP_BEGIN prior_rc=$rc state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set dev wlan0 down
    say "MZ600_HRI39_SCAN_LINK_DOWN_RC=$?"
  fi
  for mod in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 12s modprobe -r "$mod" >/dev/null 2>&1
    say "MZ600_HRI39_SCAN_UNLOAD_""$mod""_RC=$?"
  done
  if mountpoint -q "$N"; then
    if hash_ok "$SV" "$N"; then
      timeout -k 2s 12s umount "$N"
      say "MZ600_HRI39_SCAN_UNMOUNT_RC=$?"
    else
      say 'MZ600_HRI39_SCAN_UNEXPECTED_OVERLAY_STOP'
    fi
  fi
  if mountpoint -q "$F"; then
    if hash_ok "$OEM_SHA" "$F"; then
      timeout -k 2s 12s umount "$F"
      say "MZ600_HRI39_SCAN_FIRMWARE_UNMOUNT_RC=$?"
    else
      say "MZ600_HRI39_SCAN_UNEXPECTED_FIRMWARE_MOUNT_STOP"
    fi
  fi
  sleep 1
  if ! mountpoint -q "$N" && ! mountpoint -q "$F" && hash_ok "$SN" "$N" &&
     hash_ok "$SF" "$F" && hash_ok "$SO" "$O" &&
     [[ ! -e /sys/class/net/wlan0 ]] &&
     ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    say 'MZ600_HRI39_SCAN_ORIGINAL_FILES_AND_RADIO_RESTORED'
    if (( FINISHED == 1 )); then
      say 'MZ600_HRI39_SCAN_READBACK_A_B_PHYSICAL_PASS_CLEAN'
    fi
  else
    say 'MZ600_HRI39_SCAN_RESTORE_INCOMPLETE_STOP'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say 'MZ600_HRI39_SCAN_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 && "$(uname -r)" == "$K" ]] || exit 1
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || exit 1
[[ "$(cat /etc/debian_version)" == '12.15' ]] || exit 1
[[ ! -e "$V" && ! -e "$ONCE" && ! -e "$PRIVATE_SCAN" ]] || { say 'REFUSE_PREVIOUS_TEST_OR_PRIVATE_SCAN_FILE_EXISTS'; exit 1; }
! mountpoint -q "$N" && ! mountpoint -q "$F" || exit 1
[[ ! -e /sys/class/net/wlan0 ]] || exit 1
[[ -e /sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address ]] || exit 1
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || exit 1
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|bluetooth|hci_uart) ' /proc/modules || exit 1
for srv in NetworkManager wpa_supplicant iwd; do
  ! systemctl is-active --quiet "$srv.service" || exit 1
done
hash_ok "$SF" "$F" && hash_ok "$SN" "$N" && hash_ok "$SO" "$O" && hash_ok "$SM" "$M" && hash_ok "$OEM_SHA" "$OEM_FW" && [[ "$(stat -c %s "$OEM_FW")" == 261317 ]] && iw reg get | grep -q '^country 00:' || {
  say 'REFUSE_BASELINE_SHA'; exit 1;
}
say 'MZ600_HRI39_SCAN_BASELINE_SHA_PASS'
awk 'NR == 71 { print "ccode=US"; print "regrev=69" } { print }' "$N" > "$V"
[[ "$(stat -c %s "$V")" == 1569 ]] && hash_ok "$SV" "$V" || {
  say 'REFUSE_VARIANT_SHA'; exit 1;
}
say 'MZ600_HRI39_SCAN_CALIBRATION_RECONSTRUCTION_SHA_PASS'
: > "$ONCE"
before="$(dmesg | grep -c 'MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK' || true)"
STATE=OVERLAY
timeout -k 2s 12s mount --bind "$V" "$N"
mountpoint -q "$N" && hash_ok "$SV" "$N" || {
  say 'REFUSE_MOUNT_OVERLAY_SHA'; exit 2;
}
timeout -k 2s 12s mount --bind "$OEM_FW" "$F"
mountpoint -q "$F" && hash_ok "$OEM_SHA" "$F" || {
  say "MZ600_HRI39_SCAN_IMAGE_OVERLAY_FAILED"; exit 2;
}
say 'MZ600_HRI39_SCAN_OEM_FIRMWARE_AND_COUNTRY_REV_IN_RAM_AT_BOOT'
STATE=LOADING
timeout -k 2s 14s modprobe brcmutil
say 'MZ600_HRI39_SCAN_BRCMUTIL_RC0'
timeout -k 2s 22s insmod "$M"
say 'MZ600_HRI39_SCAN_DIAGNOSTIC_RC0'
set +e
timeout -k 3s 35s modprobe brcmfmac-wcc
wcc_rc=$?
set -e
say "MZ600_HRI39_SCAN_WCC_LOAD_RC=$wcc_rc"
STATE=OBSERVE
for i in $(seq 1 30); do
  [[ -e /sys/class/net/wlan0 ]] && break
  sleep .35
done
if [[ -e /sys/class/net/wlan0 ]]; then
  say 'MZ600_HRI39_SCAN_WLAN0_PRESENT'
  phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2; exit}')"
  if [[ "$phy" =~ ^[0-9]+$ ]]; then
    say "MZ600_HRI39_SCAN_DYNAMIC_PHY=$phy"
    iw phy "phy$phy" info | awk '/MHz \[/ {if (($2+0)>=5000 && ($2+0)<6000) {n++;if($0 ~ /no IR/) no++;else if($0 !~ /disabled/) unsafe++;print "MZ600_HRI39_SCAN_5GHZ_CHANNEL=" $0}} END {printf "MZ600_HRI39_SCAN_PHY_5GHZ_FREQ_COUNT=%d NO_IR=%d NOT_DISABLED_NO_IR_MISSING=%d\n",n+0,no+0,unsafe+0}'
  say 'MZ600_HRI39_SCAN_REGULATORY_REGION_BEGIN'
  iw reg get | head -30
  say 'MZ600_HRI39_SCAN_REGULATORY_REGION_END'
  fi
else
  say 'MZ600_HRI39_SCAN_WLAN0_NOT_CREATED'
fi
say 'MZ600_HRI39_SCAN_CHANNEL_REGULATORY_GATE_BEGIN'
if [[ ! -e /sys/class/net/wlan0 ]]; then
  say 'MZ600_HRI39_SCAN_REFUSE_NO_WLAN0'
  exit 4
fi
phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2; exit}')"
[[ "$phy" =~ ^[0-9]+$ ]] || { say 'MZ600_HRI39_SCAN_REFUSE_PHY'; exit 4; }
PHYINFO="$(iw phy "phy$phy" info)"
for f in 5180 5200 5220 5240; do
  ln="$(printf '%s\n' "$PHYINFO" | grep -F "$f MHz [" | head -n 1 || true)"
  if [[ -z "$ln" || "$ln" == *disabled* || "$ln" != *'(no IR)'* || "$ln" == *radar* ]]; then
    say "MZ600_HRI39_SCAN_REFUSE_CHANNEL_$f"
    exit 4
  fi
  say "MZ600_HRI39_SCAN_PASSIVE_CHAN_$f_NO_IR_VERIFIED"
done
say 'MZ600_HRI39_SCAN_CHANNEL_REGULATORY_GATE_PASS'
timeout -k 2s 10s ip link set dev wlan0 up
say 'MZ600_HRI39_SCAN_LINK_UP_RC0'
set +e
timeout -k 3s 42s iw dev wlan0 scan freq 5180 5200 5220 5240 passive > "$PRIVATE_SCAN" 2>&1
scan_rc=$?
set -e
say "MZ600_HRI39_SCAN_PASSIVE_SCAN_RC=$scan_rc"
say "MZ600_HRI39_SCAN_PRIVATE_BYTES=$(wc -c < "$PRIVATE_SCAN")"
say "MZ600_HRI39_SCAN_PRIVATE_SHA256=$(sha256sum "$PRIVATE_SCAN" | awk '{print $1}')"
if (( scan_rc == 0 )); then
  bss="$(grep -c '^BSS ' "$PRIVATE_SCAN" || true)"
  say "MZ600_HRI39_SCAN_BSS_COUNT=$bss"
  awk '/^[[:space:]]*freq:/ { if ($2+0 >= 5000 && $2+0 < 6000) f[$2]++ } END {for (k in f) print "MZ600_HRI39_SCAN_RETURNED_FREQ_MHZ=" k " BSS_COUNT=" f[k]}' "$PRIVATE_SCAN" | sort
else
  say 'MZ600_HRI39_SCAN_NONZERO_PASSIVE_SCAN_EXIT_NO_ASSOCIATION'
fi
sleep 1
after="$(dmesg | grep -c 'MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK' || true)"
say "MZ600_HRI39_SCAN_COUNTRY_LOGS_BEFORE=$before AFTER=$after"
if (( after <= before )); then
  say "MZ600_HRI39_SCAN_FIRMWARE_COUNTRY_LOG_NOT_REACHED"
else
  say 'MZ600_HRI39_SCAN_FIRMWARE_DIAGNOSTICS_BEGIN'
  dmesg | grep -E 'MZ600_5G_DIAG_(COUNTRY_READ|BANDLIST|CHANSPECS|WIPHY|LEGACY_VALID_CHANNELS)|MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK' | tail -6
  say 'MZ600_HRI39_SCAN_FIRMWARE_DIAGNOSTICS_END'
fi
say 'MZ600_HRI39_SCAN_RELEVANT_INIT_LOGS_BEGIN'
dmesg | grep -Ei 'brcmf.*(firmware|f2|sdio|timeout|failed|chip|version)' | tail -9 | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[redacted]/g' || true
say 'MZ600_HRI39_SCAN_RELEVANT_INIT_LOGS_END'
FINISHED=1
STATE=OBSERVATION_COMPLETE
exit 0
