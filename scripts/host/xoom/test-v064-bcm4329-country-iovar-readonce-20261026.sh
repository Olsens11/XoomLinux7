#!/usr/bin/env bash
# Read ONLY current BCM4329 firmware effective country iovar + band/chanspecs.
# One-time RAM-only diagnostic, no NVRAM overlay, country setting, scan or boot.
set -Eeuo pipefail
K='7.0.0-next-20260422+'
F='/lib/firmware/brcm/brcmfmac4329-sdio.bin'
N='/lib/firmware/brcm/brcmfmac4329-sdio.txt'
M='/run/mz600-v064-countryread-diag-once.ko'
O="/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
SF='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
SN='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
SM='fadd9d0242ddd693392a59c83725d184f2a325cdbe87d96b31a510776c6bb352'
SO='9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb'
STATE=PREFLIGHT
COMPLETE=0
say() { printf '%s\n' "$*"; }
hash_ok() { printf '%s  %s\n' "$1" "$2" | sha256sum -c - >/dev/null 2>&1; }
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  say "MZ600_COUNTRY_CLEANUP_BEGIN prior_rc=$rc state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 8s ip link set dev wlan0 down
    say "MZ600_COUNTRY_LINK_DOWN_RC=$?"
  fi
  for mod in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 12s modprobe -r "$mod" >/dev/null 2>&1
    say "MZ600_COUNTRY_UNLOAD_""$mod""_RC=$?"
  done
  sleep 1
  if [[ ! -e /sys/class/net/wlan0 ]] &&
     ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules &&
     hash_ok "$SO" "$O" && hash_ok "$SN" "$N" && hash_ok "$SF" "$F" &&
     ! mountpoint -q "$N"; then
    say 'MZ600_COUNTRY_ORIGINAL_FW_NVRAM_MODULES_AND_WLAN_RESTORED'
    if (( COMPLETE == 1 )); then
      say 'MZ600_COUNTRY_READ_ONLY_DIAG_PASS_AND_CLEAN'
    fi
  else
    say 'MZ600_COUNTRY_CLEANUP_INCOMPLETE_STOP'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say 'MZ600_COUNTRY_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 ]] || exit 1
[[ "$(uname -r)" == "$K" ]] || exit 1
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || exit 1
[[ "$(cat /etc/debian_version)" == '12.15' ]] || exit 1
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || exit 1
[[ -e /sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address ]] || exit 1
[[ ! -e /sys/class/net/wlan0 ]] || exit 1
! mountpoint -q "$N" || exit 1
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|hci_uart|bluetooth) ' /proc/modules || exit 1
for service in NetworkManager wpa_supplicant iwd; do
  ! systemctl is-active --quiet "$service.service" || exit 1
done
hash_ok "$SO" "$O" && hash_ok "$SN" "$N" && hash_ok "$SF" "$F" && hash_ok "$SM" "$M" || {
  say 'MZ600_COUNTRY_REFUSE_HASH_MISMATCH'; exit 1;
}
before="$(dmesg | grep -c 'MZ600_5G_DIAG_COUNTRY_READ' || true)"
say 'MZ600_COUNTRY_PREFLIGHT_PASS_IDENTICAL_BASELINE'
STATE=LOADING
timeout -k 2s 12s modprobe brcmutil
say 'MZ600_COUNTRY_BRCMUTIL_INSERT_RC0'
timeout -k 2s 20s insmod "$M"
say 'MZ600_COUNTRY_RAM_DIAGNOSTIC_INSERT_RC0'
timeout -k 2s 20s modprobe brcmfmac-wcc
say 'MZ600_COUNTRY_WCC_INSERT_RC0'
STATE=OBSERVING
for i in $(seq 1 30); do
  [[ -e /sys/class/net/wlan0 ]] && break
  sleep .35
done
[[ -e /sys/class/net/wlan0 ]] || {
  say 'MZ600_COUNTRY_NO_WLAN0'; exit 2;
}
say 'MZ600_COUNTRY_WLAN0_PRESENT'
phy="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2; exit}')"
if [[ "$phy" =~ ^[0-9]+$ ]]; then
  say "MZ600_COUNTRY_DYNAMIC_PHY=$phy"
  iw phy "phy$phy" info | awk '/MHz \[/ {if (($2+0)>=5000 && ($2+0)<6000) n++} END {printf "MZ600_COUNTRY_PHY_5GHZ_FREQ_COUNT=%d\n",n+0}'
fi
sleep 1
after="$(dmesg | grep -c 'MZ600_5G_DIAG_COUNTRY_READ' || true)"
say "MZ600_COUNTRY_IOVAR_COUNT_BEFORE=$before AFTER=$after"
if (( after <= before )); then
  say 'MZ600_COUNTRY_MISSING_FRESH_FW_READ'; exit 3
fi
say 'MZ600_COUNTRY_FIRMWARE_DIAGNOSTICS_BEGIN'
dmesg | grep -E 'MZ600_5G_DIAG_(COUNTRY_READ|BANDLIST|CHANSPECS|WIPHY)' | tail -4
say 'MZ600_COUNTRY_FIRMWARE_DIAGNOSTICS_END'
COMPLETE=1
STATE=CAPTURED
exit 0
