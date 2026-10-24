#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
OUT="$B/firmware-reference-v07"
mkdir -p "$OUT"
URL='https://kernel.googlesource.com/pub/scm/linux/kernel/git/firmware/linux-firmware/+/refs/heads/main/brcm/brcmfmac4329-sdio.bin?format=TEXT'
curl -fsSL --retry 2 --max-time 35 "$URL" | base64 -d > "$OUT/brcmfmac4329-sdio.bin.tmp"
test "$(wc -c < "$OUT/brcmfmac4329-sdio.bin.tmp")" -gt 100000
mv "$OUT/brcmfmac4329-sdio.bin.tmp" "$OUT/brcmfmac4329-sdio.bin"
file "$OUT/brcmfmac4329-sdio.bin"
sha256sum "$OUT/brcmfmac4329-sdio.bin"
stat -c '%s BYTES' "$OUT/brcmfmac4329-sdio.bin"
echo 'UPSTREAM BCM4329 FIRMWARE DOWNLOADED; NO DEVICE WRITES'
