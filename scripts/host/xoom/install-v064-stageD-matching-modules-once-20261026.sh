#!/usr/bin/env bash
# Experimental replacement Motorola Xoom MZ600 ONLY.
# User-operated ROOT console on the already-running, verified Stage-D Debian.
# Scoped to installation of the ABI-exact 114-module SAFE gzip archive.
# Does NOT flash boot, format partitions, load a radio driver, or reboot.
set -Eeuo pipefail

K='7.0.0-next-20260422+'
BASE='/lib/modules'
OLD="$BASE/7.0.0-next-20260422"
TARGET="$BASE/$K"
A='/run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz'
HASH='5e051de2a1cf9875414886966a1ff00cf3ec5ba038b0688e7f7750ea2594a409'
EXPECTED_BYTES=2798775
STAGE=''
COMMITTED=0

fail() { printf 'MZ600_MODULE_INSTALL_ABORT: %s\n' "$*" >&2; exit 1; }
on_exit() {
  rc=$?
  if (( rc != 0 )); then
    printf 'INSTALL_EXIT=%d; existing boot and legacy module tree not targeted.\n' "$rc" >&2
    if [[ -n "$STAGE" && -d "$STAGE" ]]; then
      printf 'NEW_STAGING_RETAINED_FOR_REVIEW=%s\n' "$STAGE" >&2
    fi
    if (( COMMITTED == 1 )); then
      printf 'NEW_MODULE_TREE_WAS_MOVED; inspect depmod state, do not rerun blindly.\n' >&2
    fi
  fi
}
trap on_exit EXIT

printf '%s\n' 'MZ600_V064_SAFE_GZIP_INSTALL_PREFLIGHT_BEGIN'
[[ "$(id -u)" == 0 ]] || fail 'UID is not root'
[[ "$(uname -r)" == "$K" ]] || fail 'running kernel release differs'
[[ "$(findmnt -n -o SOURCE /)" == '/dev/mmcblk0p8' ]] || fail 'root is not internal p8'
[[ "$(findmnt -n -o FSTYPE /)" == 'ext4' ]] || fail 'root is not ext4'
[[ "$(cat /etc/debian_version)" == '12.15' ]] || fail 'unexpected Debian version'
[[ "$(cat /sys/class/block/mmcblk0p8/start)" == 118784 ]] || fail 'unexpected p8 start'
[[ "$(cat /sys/class/block/mmcblk0p8/size)" == 2097152 ]] || fail 'unexpected p8 size'
[[ "$(cat /sys/class/block/mmcblk0p7/size)" == 16384 ]] || fail 'unexpected p7 geometry'
[[ "$(blkid -s UUID -o value /dev/mmcblk0p8)" == 'c2fb0167-7143-4186-b284-c86d6c09ea64' ]] || fail 'p8 filesystem UUID mismatch'
[[ -d "$OLD" ]] || fail 'legacy module directory missing'
[[ ! -e "$TARGET" && ! -L "$TARGET" ]] || fail 'matching module target already exists'
[[ -f "$A" && ! -L "$A" ]] || fail 'safe gzip archive not present'
[[ "$(stat -c %s "$A")" == "$EXPECTED_BYTES" ]] || fail 'safe gzip byte count differs'
for command in sha256sum tar gzip find wc mktemp mv depmod modprobe sync; do
  command -v "$command" >/dev/null || fail "missing tool: $command"
done
printf '%s  %s\n' "$HASH" "$A" | sha256sum -c - || fail 'safe gzip SHA256 differs'
free_kib="$(df -Pk / | awk 'NR==2 {print $4}')"
[[ "$free_kib" =~ ^[0-9]+$ ]] || fail 'could not read free disk space'
(( free_kib >= 131072 )) || fail 'insufficient free space (require >=128 MiB)'
entries="$(tar -tzf "$A" | wc -l)"
[[ "$entries" -eq 189 ]] || fail 'safe gzip tar entry count differs'
printf 'KERNEL=%s ROOT=/dev/mmcblk0p8 EXT4 FREE_KIB=%s TAR_ENTRIES=%s\n' "$K" "$free_kib" "$entries"

printf '%s\n' 'INSPECT_PREVIOUS_XZ_FAILURE_STAGING_NO_DELETE:'
find "$BASE" -mindepth 1 -maxdepth 1 -type d -name '.stage-v064-*' -print -exec du -sh -- '{}' \;
printf '%s\n' 'EXISTING_MODULE_DIRECTORIES_NO_DELETE:'
find "$BASE" -mindepth 1 -maxdepth 1 -print
printf '%s\n' 'MZ600_V064_PREFLIGHT_PASS'

STAGE="$(mktemp -d "$BASE/.stage-v064-gzip.XXXXXXXX")"
[[ -d "$STAGE" && "$STAGE" == "$BASE"/.stage-v064-gzip.* ]] || fail 'cannot create safe staging directory'
printf 'NEW_STAGING_PATH=%s\n' "$STAGE"
tar -xzf "$A" -C "$STAGE" --strip-components=3 --no-same-owner || fail 'gzip extraction failed'
num_modules="$(find "$STAGE" -type f -name '*.ko' | wc -l)"
num_links="$(find "$STAGE" -type l | wc -l)"
num_special="$(find "$STAGE" \( -type b -o -type c -o -type p -o -type s \) | wc -l)"
[[ "$num_modules" -eq 114 ]] || fail 'extracted module count differs'
[[ "$num_links" -eq 0 ]] || fail 'extracted symlink detected'
[[ "$num_special" -eq 0 ]] || fail 'extracted special file detected'
[[ -s "$STAGE/modules.dep" && -s "$STAGE/modules.order" ]] || fail 'missing module metadata'
BRCM="$STAGE/kernel/drivers/net/wireless/broadcom/brcm80211"
[[ -s "$BRCM/brcmutil/brcmutil.ko" ]] || fail 'missing brcmutil'
[[ -s "$BRCM/brcmfmac/brcmfmac.ko" ]] || fail 'missing brcmfmac'
[[ -s "$BRCM/brcmfmac/wcc/brcmfmac-wcc.ko" ]] || fail 'missing brcmfmac-wcc'
[[ ! -e "$TARGET" && ! -L "$TARGET" ]] || fail 'target appeared while staging'
printf 'MZ600_V064_STAGING_VERIFIED_MODULES=%s LINKS=%s SPECIAL=%s\n' "$num_modules" "$num_links" "$num_special"

mv -T -- "$STAGE" "$TARGET" || fail 'atomic versioned directory move failed'
COMMITTED=1
STAGE=''
printf '%s\n' 'MZ600_V064_MATCHED_MODULES_ATOMIC_MOVE_PASS'
depmod -a "$K" || fail 'depmod failed; inspect installed tree, do not rerun blindly'
sync
[[ "$(find "$TARGET" -type f -name '*.ko' | wc -l)" -eq 114 ]] || fail 'post-depmod count mismatch'
printf '%s\n' 'MZ600_V064_DEPMOD_PASS'
modprobe -n -v brcmfmac || fail 'dry-run brcmfmac dependency resolution failed'
modprobe -n -v brcmfmac-wcc || fail 'dry-run WCC dependency resolution failed'
printf '%s\n' 'MZ600_V064_MODULE_DRY_RUN_PASS_NO_RADIO_LOAD'
printf '%s\n' 'MZ600_V064_MODULE_INSTALL_COMPLETE_ABI_114'
