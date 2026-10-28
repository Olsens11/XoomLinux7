#!/usr/bin/env bash
# Copies device-private firmware/calibration to an OFFLINE PRIVATE folder only.
set -euo pipefail
[[ $# == 2 ]] || { echo "Usage: $0 MZ600_REFERENCE_ROOTFS NEW_PRIVATE_OUTPUT" >&2; exit 2; }
root="$(realpath "$1")"; target="$2"
[[ ! -e "$target" ]] || { echo "REFUSE existing target"; exit 2; }
src="$root/lib/firmware/brcm"
[[ -s "$src/brcmfmac4329-sdio.bin" && -s "$src/brcmfmac4329-sdio.txt" ]] || {
 echo "Refusing incomplete BCM4329 firmware or board calibration" >&2; exit 2;
}
mkdir -p "$target/brcm"
target="$(realpath "$target")"
cp -p "$src/brcmfmac4329-sdio.bin" "$src/brcmfmac4329-sdio.txt" "$target/brcm/"
(cd "$target/brcm" && sha256sum brcmfmac4329-sdio.bin brcmfmac4329-sdio.txt) > "$target/SHA256SUMS"
cat > "$target/PRIVATE-NOT-FOR-UPSTREAM.txt" <<'EOF'
BCM4329 Motorola firmware and NVRAM/calibration, PRIVATE DEVICE PACKAGE.
Not a public Linux kernel patch, and not universally safe for other Xooms.
Verify exact board/model-specific calibration, regulatory country/revision,
device identity and firmware release before using on a different unit.
Place into /lib/firmware/brcm/ on the disposable image only after review.
EOF
chmod 0700 "$target"
chmod 0600 "$target/brcm/"*
echo "PRIVATE_BCM4329_MZ600_FIRMWARE_STAGED: $target"
