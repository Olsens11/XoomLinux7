#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
D=$B/firmware-reference-v07
mkdir -p "$D/regdb-release-2026-09-03"
cd "$D/regdb-release-2026-09-03"
curl -fLsS --retry 2 --max-time 30 -o wireless-regdb-2026.09.03.tar.xz https://www.kernel.org/pub/software/network/wireless-regdb/wireless-regdb-2026.09.03.tar.xz
tar -tJf wireless-regdb-2026.09.03.tar.xz | grep -E '(^|/)(regulatory.db|regulatory.db.p7s|README)$'
tar -xJf wireless-regdb-2026.09.03.tar.xz
find . -name 'regulatory.db*' -type f -printf '%p %s bytes\n'
sha256sum wireless-regdb-2026.09.03.tar.xz
