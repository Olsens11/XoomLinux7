#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$root/upstream/linux"
rev=2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3
if [ ! -d "$src/.git" ]; then
  mkdir -p "$root/upstream"
  git clone --filter=blob:none https://github.com/xoom-linux/linux.git "$src"
fi
git -C "$src" fetch --filter=blob:none origin "$rev"
git -C "$src" checkout --detach "$rev"
actual="$(git -C "$src" rev-parse HEAD)"
test "$actual" = "$rev" || { echo 'ERROR wrong upstream revision' >&2; exit 1; }
echo "Pinned upstream source: $src $actual"
