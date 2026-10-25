#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
#
# Validate candidate Linux patches WITHOUT modifying either the kernel checkout
# or target device. Reviewed patches remain RFC until a real contributor signs.
set -euo pipefail
upstream="${1:?Usage: $0 /path/to/pristine/linux [revision]}"
pin="${2:-2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
test -x "$upstream/scripts/checkpatch.pl"
test -x "$upstream/scripts/get_maintainer.pl"
actual="$(git -C "$upstream" rev-parse HEAD)"
test "$actual" = "$pin" || { echo "ERROR: source base does not match expected commit" >&2; exit 2; }
test -z "$(git -C "$upstream" status --porcelain)" || { echo "ERROR: pristine tree is dirty" >&2; exit 2; }

files=(
  "$here/patches/upstream/rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch"
)
for patch in "${files[@]}"; do
 test -s "$patch"
 echo "=== $(basename "$patch") ==="
 git -C "$upstream" apply --check "$patch"
 echo "CLEAN_UPSTREAM_APPLY_PASS"
 # checkpatch intentionally fails for unsigned RFC; DO NOT auto-add another
 # person's DCO signoff. Preserve the full output for review.
 if perl "$upstream/scripts/checkpatch.pl" --no-tree --terse "$patch"; then
   echo "CHECKPATCH_PASS"
 else
   echo "CHECKPATCH_NOT_CLEAN: review errors; unsigned RFC requires real DCO"
 fi
 echo "Suggested maintainers (recheck at submission time):"
 perl "$upstream/scripts/get_maintainer.pl" --no-rolestats --no-git --no-git-fallback "$patch"
done
echo "AUDIT_COMPLETE_NO_PATCH_APPLIED_NO_DEVICE_ACCESS"
