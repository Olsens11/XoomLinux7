#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
P=$B/firmware-reference-v07
R=$P/regdb-release-2026-09-03/wireless-regdb-2026.09.03
test -s "$R/regulatory.db"
test -s "$R/regulatory.db.p7s"
openssl cms -inform DER -in "$R/regulatory.db.p7s" -cmsout -print > "$P/regdb-signer-info.txt"
grep -m 8 -e issuer -e subject -e sha256 -e signerInfos "$P/regdb-signer-info.txt" || true
cp "$R/regulatory.db" "$P/regulatory.db"
cp "$R/regulatory.db.p7s" "$P/regulatory.db.p7s"
sha256sum "$P/regulatory.db" "$P/regulatory.db.p7s"
stat -c '%n %s bytes' "$P/regulatory.db" "$P/regulatory.db.p7s"
echo 'REGDB DATABASE + OFFICIAL DETACHED PKCS7 SIGNATURE STAGED; IN-KERNEL VALIDATION REQUIRED'
