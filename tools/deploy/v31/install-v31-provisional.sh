#!/bin/bash
# PROVISIONAL: exact tested V31 module, WCC and private OEM firmware, p8 only.
# Never embed credentials or proprietary firmware in the public repository.
set -Eeuo pipefail
K=7.0.0-next-20260422+
ROOT=/lib/modules/$K/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac
CORE=$ROOT/brcmfmac.ko
WCC=$ROOT/wcc/brcmfmac-wcc.ko
FW=/lib/firmware/brcm/brcmfmac4329-sdio.bin
NV=/lib/firmware/brcm/brcmfmac4329-sdio.txt
STAGE=/run/xoom-v31-install
BACKUP=/var/lib/xoomlinux7/backup-v31-before-install
OPT=/etc/modprobe.d/xoom-bcm4329-v31-lab.conf
original_core=9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb
original_wcc=31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80
original_fw=d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93
original_nv=a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb
new_core=c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8
new_wcc=6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d
new_fw=5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834
checksha() { printf '%s  %s\n' "$1" "$2" | sha256sum -c --status -; }
stop() { printf 'STOP: %s\n' "$*" >&2; exit 1; }
mode=--check
if (( $# > 0 )); then mode=$1; fi
[[ $mode == --check || $mode == --apply ]] || stop 'use --check or --apply'
[[ $(id -u) == 0 && $(uname -r) == "$K" ]] || stop 'unexpected user or kernel'
[[ $(findmnt -n -o SOURCE,FSTYPE /) == '/dev/mmcblk0p8 ext4' ]] || stop 'unexpected root filesystem'
[[ ! -e $BACKUP && ! -e $OPT ]] || stop 'a backup/config already exists; refuse overwrite'
for f in "$CORE" "$WCC" "$FW" "$NV"; do
  [[ -f $f ]] || stop "missing $f"
  ! mountpoint -q "$f" || stop "unexpected bind mount: $f"
done
checksha "$original_core" "$CORE" || stop 'original driver SHA mismatch'
checksha "$original_wcc" "$WCC" || stop 'original WCC SHA mismatch'
checksha "$original_fw" "$FW" || stop 'original firmware SHA mismatch'
checksha "$original_nv" "$NV" || stop 'original NVRAM SHA mismatch'
checksha "$new_core" "$STAGE/brcmfmac.ko" || stop 'missing/bad staged V31 core'
checksha "$new_wcc" "$STAGE/brcmfmac-wcc.ko" || stop 'missing/bad staged V31 WCC'
checksha "$new_fw" "$STAGE/brcmfmac4329-sdio.bin" || stop 'missing/bad staged OEM firmware'
modinfo -F vermagic "$STAGE/brcmfmac.ko" | grep -Fq "$K " || stop 'wrong module ABI'
[[ $(stat -c %s "$STAGE/brcmfmac.ko") == 354392 ]] || stop 'bad core size'
[[ -d /sys/bus/sdio/devices/mmc2:0001:1 ]] || stop 'BCM4329 not present'
[[ ! -d /sys/class/bluetooth/hci0 ]] ||
  ! hciconfig hci0 2>/dev/null | grep -Fq 'UP RUNNING' || stop 'Bluetooth active'
[[ ! -e /sys/class/net/wlan0/carrier ||
   $(cat /sys/class/net/wlan0/carrier) == 0 ]] || stop 'active Wi-Fi carrier'
echo 'V31_INSTALL_PREFLIGHT_PASS'
[[ $mode == --apply ]] || { echo 'NO_CHANGES: rerun explicitly with --apply'; exit 0; }
df -Pk /var/lib | awk 'NR==2{exit !($4>5000)}' || stop 'not enough space for backup'
install -d -m 0700 "$BACKUP"
cp -a "$CORE" "$BACKUP/brcmfmac.ko"
cp -a "$WCC" "$BACKUP/brcmfmac-wcc.ko"
cp -a "$FW" "$BACKUP/brcmfmac4329-sdio.bin"
cp -a "$NV" "$BACKUP/brcmfmac4329-sdio.txt"
checksha "$original_core" "$BACKUP/brcmfmac.ko" || stop 'backup failed'
checksha "$original_wcc" "$BACKUP/brcmfmac-wcc.ko" || stop 'backup failed'
checksha "$original_fw" "$BACKUP/brcmfmac4329-sdio.bin" || stop 'backup failed'
checksha "$original_nv" "$BACKUP/brcmfmac4329-sdio.txt" || stop 'backup failed'
echo 'ORIGINALS_BACKUP_VERIFIED'
# After backup, do not overwrite unless both modules can be unloaded.
wpa_cli -i wlan0 terminate >/dev/null 2>&1 || true
ip link set wlan0 down >/dev/null 2>&1 || true
timeout -k 2s 15s modprobe -r brcmfmac-wcc || stop 'WCC busy; originals still intact'
timeout -k 2s 15s modprobe -r brcmfmac || stop 'core busy; originals still intact'
armed=1
rollback() {
  rc=$?
  trap - EXIT
  if (( rc != 0 )) && (( armed == 1 )); then
    echo 'INSTALL_FAILED: attempting file rollback' >&2
    modprobe -r brcmfmac-wcc brcmfmac >/dev/null 2>&1 || true
    cp -a "$BACKUP/brcmfmac.ko" "$CORE"
    cp -a "$BACKUP/brcmfmac-wcc.ko" "$WCC"
    cp -a "$BACKUP/brcmfmac4329-sdio.bin" "$FW"
    rm -f "$OPT"
    depmod -a "$K" || true
    if checksha "$original_core" "$CORE" && checksha "$original_wcc" "$WCC" &&
       checksha "$original_fw" "$FW"; then echo 'ROLLBACK_FILES_VERIFIED';
    else echo 'ROLLBACK_FAILED: preserve serial access, inspect manually' >&2; fi
  fi
  exit "$rc"
}
trap rollback EXIT
install -m 0644 "$STAGE/brcmfmac.ko" "$CORE.new"
install -m 0644 "$STAGE/brcmfmac-wcc.ko" "$WCC.new"
install -m 0644 "$STAGE/brcmfmac4329-sdio.bin" "$FW.new"
mv "$CORE.new" "$CORE"
mv "$WCC.new" "$WCC"
mv "$FW.new" "$FW"
checksha "$new_core" "$CORE" && checksha "$new_wcc" "$WCC" &&
  checksha "$new_fw" "$FW" || stop 'copied hashes mismatch'
cat > "$OPT" <<'OPTIONS'
# Temporary V31 laboratory scan-completion options.
# Replace with a clean series-derived module after connectivity tests.
options brcmfmac mz600_extra_events=0 mz600_terminal_owner=1 mz600_request_sync_id=4660 mz600_generation=1
OPTIONS
chmod 0644 "$OPT"
depmod -a "$K"
timeout -k 2s 22s modprobe brcmfmac || stop 'new core failed to load'
timeout -k 2s 22s modprobe brcmfmac-wcc || stop 'new WCC failed to load'
[[ -d /sys/module/brcmfmac_wcc ]] || stop 'WCC not loaded'
[[ $(cat /sys/module/brcmfmac/parameters/mz600_terminal_owner) == Y ]] || stop 'owner route not enabled'
[[ $(cat /sys/module/brcmfmac/parameters/mz600_generation) == Y ]] || stop 'scan generation not enabled'
checksha "$original_nv" "$NV" || stop 'NVRAM changed'
armed=0
trap - EXIT
sync
echo 'V31_PROVISIONAL_P8_INSTALL_PASS'
echo "Backups retained: $BACKUP"
echo 'No network was joined and no boot/kernel image was flashed.'
