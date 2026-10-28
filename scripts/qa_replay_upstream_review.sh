#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# XoomLinux7: replay review-form DT + Wi-Fi source; never touches a tablet.
# Required: KERNEL_REPO, CONFIG_BASE, OUT_ROOT, CROSS_COMPILE.
set -euo pipefail
P="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE=2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3
: "${KERNEL_REPO:?set KERNEL_REPO to an existing Linux kernel Git repository}"
: "${CONFIG_BASE:?set CONFIG_BASE to a proven kernel .config}"
: "${OUT_ROOT:?set OUT_ROOT to a NEW isolated directory}"
: "${CROSS_COMPILE:?set CROSS_COMPILE to ARM compiler prefix}"
test ! -e "$OUT_ROOT" || { echo "Refusing existing OUT_ROOT: $OUT_ROOT" >&2; exit 2; }
test -f "$CONFIG_BASE"
test -x "${CROSS_COMPILE}gcc"
git -C "$KERNEL_REPO" cat-file -e "$BASE^{commit}"
mkdir -p "$OUT_ROOT"
exec > >(tee "$OUT_ROOT/replay.log") 2>&1
echo "REPLAY_BEGIN $(date -u +%FT%TZ)"
echo "PROJECT_COMMIT $(git -C "$P" rev-parse HEAD)"
echo "BASE $BASE"
W="$OUT_ROOT/source"
O="$OUT_ROOT/build"
git -C "$KERNEL_REPO" worktree add --detach "$W" "$BASE"
mkdir "$O"
cp "$CONFIG_BASE" "$O/.config"
git -C "$W" config user.name "XoomLinux7 unsigned review replay"
git -C "$W" config user.email "rfc-build@invalid.example"
style_open=0
apply_series() {
 local dir="$1" file patch
 while IFS= read -r file || test -n "$file"; do
   case "$file" in ""|\#*) continue ;; esac
   patch="$dir/$file"
   test -f "$patch"
   echo "PATCH $(basename "$patch")"
   sha256sum "$patch"
   git -C "$W" am "$patch"
   if ! git -C "$W" diff HEAD^ HEAD --check; then
     echo "DIFF_CHECK_OPEN $file"; style_open=1
   fi
   if ! "$W/scripts/checkpatch.pl" --no-tree --no-signoff --strict "$patch" > "$O/checkpatch-$file.txt" 2>&1; then
     echo "CHECKPATCH_OPEN $file"
     tail -5 "$O/checkpatch-$file.txt"
     style_open=1
   fi
   echo "COMMIT $(git -C "$W" rev-parse HEAD)"
   if test "$dir" = "$P/patches/upstream/review-wifi-four-logical-20261028"; then
     echo "WIFI_PREFIX_BUILD_START $(git -C "$W" rev-parse --short HEAD)"
     make -C "$W" O="$O" ARCH=arm CROSS_COMPILE="$CROSS_COMPILE" -j8 drivers/net/wireless/broadcom/brcm80211/brcmfmac/
     echo "WIFI_PREFIX_BUILD_PASS $(git -C "$W" rev-parse --short HEAD)"
   fi
 done < "$dir/series"
}
apply_series "$P/patches/upstream/review-stingray-dt-20261028"
make -C "$W" O="$O" ARCH=arm CROSS_COMPILE="$CROSS_COMPILE" olddefconfig
make -C "$W" O="$O" ARCH=arm CROSS_COMPILE="$CROSS_COMPILE" -j8 dtbs
echo "DT_BUILD_PASS"
apply_series "$P/patches/upstream/review-wifi-four-logical-20261028"
make -C "$W" O="$O" ARCH=arm CROSS_COMPILE="$CROSS_COMPILE" -j8 zImage dtbs modules
echo "FULL_BUILD_PASS"
git -C "$W" log -7 --format='%h %s' > "$OUT_ROOT/applied-commits.txt"
for name in arch/arm/boot/zImage arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dtb arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dtb drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko; do
 sha256sum "$O/$name"
done > "$OUT_ROOT/artifacts.sha256"
cat "$OUT_ROOT/applied-commits.txt"
cat "$OUT_ROOT/artifacts.sha256"
echo "REPLAY_SOURCE_PASS $(date -u +%FT%TZ)"
if test "$style_open" -ne 0; then
 echo "REPLAY_STYLE_OPEN: an inherited or new style issue remains; no submission clearance"
 exit 4
fi
echo "REPLAY_STYLE_PASS"
