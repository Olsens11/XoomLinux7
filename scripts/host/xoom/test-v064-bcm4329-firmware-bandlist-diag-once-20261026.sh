#!/usr/bin/env bash
# MZ600 internal Debian p8 only, count-only firmware enumeration diagnostic.
# Uses a SHA-pinned /run brcmfmac.ko, WITHOUT updating /lib/modules or boot.
# No scan, link UP, association, RF power/country override or reboot.
set -Eeuo pipefail
export SYSTEMD_PAGER=cat PAGER=cat
K='7.0.0-next-20260422+'
MODULE='/run/mz600-v064-bandlist-diag-once.ko'
SHA='1d38b1446a631c8d9ceaa82edb5b981b53288410a2d7bc88d0dc00f24c8e5444'
ORIG='9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb'
BASE='/lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko'
STATE='PREFLIGHT'
done_flag=0
say() { printf '%s\n' "$*"; }
cleanup() {
  ret=$?
  trap - EXIT INT TERM
  set +e
  say "MZ600_5G_FW_DIAG_CLEANUP_BEGIN ret=$ret state=$STATE"
  if [[ -e /sys/class/net/wlan0 ]]; then
    timeout -k 2s 7s ip link set dev wlan0 down
    say "MZ600_5G_FW_DIAG_LINK_DOWN_RC=$?"
  fi
  for m in brcmfmac-wcc brcmfmac brcmutil; do
    timeout -k 2s 10s modprobe -r "$m" 2>&1
    say "MZ600_5G_FW_DIAG_UNLOAD_""$m""_RC=$?"
  done
  sleep 1
  if [[ ! -e /sys/class/net/wlan0 ]] && ! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; then
    say 'MZ600_5G_FW_DIAG_DRIVER_TEARDOWN_VERIFIED'
    if (( done_flag == 1 )); then
      say 'MZ600_5G_FW_DIAG_RESULTS_CAPTURED_AND_CLEANED'
    fi
  else
    say 'MZ600_5G_FW_DIAG_CLEANUP_INCOMPLETE'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say 'MZ600_5G_FW_DIAG_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 ]] || { say 'DIAG_REFUSE_NONROOT'; exit 1; }
[[ "$(uname -r)" == "$K" ]] || { say 'DIAG_REFUSE_KERNEL'; exit 1; }
[[ "$(findmnt -n -o SOURCE,FSTYPE /)" == '/dev/mmcblk0p8 ext4' ]] || { say 'DIAG_REFUSE_ROOT_PARTITION'; exit 1; }
[[ "$(cat /etc/debian_version)" == 12.15 ]] || { say 'DIAG_REFUSE_DEBIAN'; exit 1; }
[[ "$(stat -c %s "$MODULE")" == 341760 ]] || { say 'DIAG_REFUSE_SIZE'; exit 1; }
printf '%s  %s\n' "$SHA" "$MODULE" | sha256sum -c - || { say 'DIAG_REFUSE_DIAGNOSTIC_SHA'; exit 1; }
printf '%s  %s\n' "$ORIG" "$BASE" | sha256sum -c - || { say 'DIAG_REFUSE_INSTALLED_BASELINE_CHANGED'; exit 1; }
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || { say 'DIAG_REFUSE_NO_SDIO'; exit 1; }
[[ -f /sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address ]] || { say 'DIAG_REFUSE_FACTORY_MAC'; exit 1; }
[[ ! -e /sys/class/net/wlan0 ]] || { say 'DIAG_REFUSE_WLAN0_ALREADY_UP'; exit 1; }
! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|hci_uart|bluetooth) ' /proc/modules || { say 'DIAG_REFUSE_RADIO_MODULES_ALREADY_LOADED'; exit 1; }
for svc in wpa_supplicant NetworkManager iwd; do
  ! systemctl -q is-active "$svc.service" || { say "DIAG_REFUSE_ACTIVE_NETWORK_SERVICE_$svc"; exit 1; }
done
! dmesg | grep -q MZ600_5G_DIAG_BANDLIST || { say 'DIAG_REFUSE_OLD_MARKERS_ALREADY_IN_RING'; exit 1; }
command -v insmod >/dev/null || exit 1
command -v iw >/dev/null || exit 1
say 'MZ600_5G_FW_DIAG_ALL_PREFLIGHT_PASS'
STATE='LOADING'
timeout -k 2s 12s modprobe brcmutil
say 'MZ600_5G_FW_DIAG_BRCMUTIL_LOAD_RC0'
timeout -k 2s 20s insmod "$MODULE"
say 'MZ600_5G_FW_DIAG_EXACT_RAM_MODULE_INSERT_RC0'
timeout -k 2s 12s modprobe brcmfmac-wcc
say 'MZ600_5G_FW_DIAG_WCC_MODULE_LOAD_RC0'
STATE='ENUMERATION'
for n in $(seq 1 30); do
  if [[ -e /sys/class/net/wlan0 ]]; then break; fi
  sleep .3
done
if [[ -e /sys/class/net/wlan0 ]]; then
  say 'MZ600_5G_FW_DIAG_WLAN0_PRESENT'
  PHY="$(iw dev wlan0 info | awk '$1=="wiphy" {print $2;exit}')"
  if [[ "$PHY" =~ ^[0-9]+$ ]]; then
    say "MZ600_5G_FW_DIAG_WIPHY_INDEX=$PHY"
    iw phy "phy$PHY" info | awk '/MHz \[/ {if (($2+0)>=5000 && ($2+0)<6000) f++} END {printf "MZ600_5G_FW_DIAG_ADVERTISED_5G_CHANNELS=%d\n",f+0}'
  else
    say 'MZ600_5G_FW_DIAG_WIPHY_UNRESOLVED'
  fi
else
  say 'MZ600_5G_FW_DIAG_WLAN0_NOT_CREATED'
fi
sleep 1
say 'MZ600_5G_FW_DIAG_KERNEL_FIRMWARE_MESSAGES_BEGIN'
dmesg | grep -E 'MZ600_5G_DIAG_(BANDLIST|CHANSPECS|WIPHY)' | tail -9 || true
say 'MZ600_5G_FW_DIAG_KERNEL_FIRMWARE_MESSAGES_END'
done_flag=1
STATE='RESULTS_CAPTURED'
exit 0
