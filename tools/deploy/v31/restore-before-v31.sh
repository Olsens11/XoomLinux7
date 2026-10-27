#!/bin/bash
# Owner-run rollback ONLY from the exact verified provisional V31 installation.
set -Eeuo pipefail
K=7.0.0-next-20260422+
D=/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac
O=$D/brcmfmac.ko
W=$D/wcc/brcmfmac-wcc.ko
F=/lib/firmware/brcm/brcmfmac4329-sdio.bin
N=/lib/firmware/brcm/brcmfmac4329-sdio.txt
B=/var/lib/xoomlinux7/backup-v31-before-install
OPT=/etc/modprobe.d/xoom-bcm4329-v31-lab.conf
check() { printf '%s  %s\n' "$1" "$2" | sha256sum --check --status -; }
stop() { echo "STOP: $*" >&2; exit 1; }
[[ $(id -u) == 0 && $(uname -r) == "$K" ]] || stop 'root or kernel mismatch'
[[ $(findmnt -n -o SOURCE,FSTYPE /) == '/dev/mmcblk0p8 ext4' ]] || stop 'wrong root'
for f in "$O" "$W" "$F" "$N"; do ! mountpoint -q "$f" || stop 'unexpected overlay'; done
check 9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb "$B/brcmfmac.ko" || stop 'old core backup mismatch'
check 31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80 "$B/brcmfmac-wcc.ko" || stop 'old WCC backup mismatch'
check d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93 "$B/brcmfmac4329-sdio.bin" || stop 'old firmware backup mismatch'
check a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb "$N" || stop 'NVRAM changed'
check c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8 "$O" || stop 'installed core is not known V31'
check 6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d "$W" || stop 'installed WCC is not known V31'
check 5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834 "$F" || stop 'installed firmware is not known V31'
[[ -f $OPT ]] || stop 'lab modprobe options absent'
echo 'V31_ROLLBACK_PREFLIGHT_PASS'
[[ $@ == --restore ]] || { echo 'No changes. Run explicitly with --restore'; exit 0; }
[[ ! -e /sys/class/net/wlan0/carrier ||
   $(cat /sys/class/net/wlan0/carrier) == 0 ]] || stop 'Wi-Fi connected; disconnect first'
wpa_cli -i wlan0 terminate >/dev/null 2>&1 || true
ip link set wlan0 down >/dev/null 2>&1 || true
timeout -k 2s 15s modprobe -r brcmfmac-wcc || stop 'WCC busy; no file changes'
timeout -k 2s 15s modprobe -r brcmfmac || stop 'core busy; no file changes'
cp -a "$B/brcmfmac.ko" "$O"
cp -a "$B/brcmfmac-wcc.ko" "$W"
cp -a "$B/brcmfmac4329-sdio.bin" "$F"
rm -f "$OPT"
depmod -a "$K"
check 9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb "$O" || stop 'restored core SHA mismatch'
check 31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80 "$W" || stop 'restored WCC SHA mismatch'
check d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93 "$F" || stop 'restored firmware SHA mismatch'
timeout -k 2s 25s modprobe brcmfmac
timeout -k 2s 25s modprobe brcmfmac-wcc
sync
echo 'V31_ORIGINAL_P8_WIFI_STACK_RESTORED'
echo "Verified backups kept under $B"
