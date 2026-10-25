#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
# Reproducible native OS kernel build. NO DEVICE ACCESS / NO FLASHING.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
B="${XOOM_BUILD_ROOT:-/home/xoomdev/xoom-linux-rom}"
K="${XOOM_LINUX_SOURCE:-$B/linux-src}"
BASE="${XOOM_BASE_KERNEL_OUT:-$B/build-wingray-gcc14-initramfs}"
OUT="${XOOM_OS_KERNEL_OUT:-$B/os-build/kernel}"
PATCH_FILE="$REPO/patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch"
TARGET="$K/arch/arm/boot/compressed/atags_to_fdt.c"
CROSS="${XOOM_CROSS_COMPILE:-$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-}"
PIN_SHA=3052214e2f76ee1e3bc5226b73a2515185f20ef7e0ea279a004d8931d764a193

[[ -f "$PATCH_FILE" && -f "$TARGET" && -f "$BASE/.config" ]] || { echo "Missing pinned source, config or reviewed patch" >&2; exit 1; }
[[ "$(sha256sum "$TARGET" | cut -d' ' -f1)" == "$PIN_SHA" ]] || { echo "Source does not match pinned Linux 7 converter" >&2; exit 1; }
[[ "$(id -u)" != 0 ]] || { echo "Run kernel build as non-root" >&2; exit 1; }
mkdir -p "$OUT"
[[ "$OUT" != "$BASE" ]] || { echo "Refusing to reuse diagnostic build output" >&2; exit 1; }
cp "$BASE/.config" "$OUT/.config"

# The canonical upstream source is a source checkout without .git metadata.
# Temporarily apply only the reviewed single-file patch and ALWAYS restore it.
backup="$(mktemp)"
cp -p "$TARGET" "$backup"
restore_source() {
    cp -p "$backup" "$TARGET"
    rm -f "$backup"
    [[ "$(sha256sum "$TARGET" | cut -d' ' -f1)" == "$PIN_SHA" ]] ||
        echo "CRITICAL: converter source restoration differs" >&2
}
trap restore_source EXIT
(cd "$K" && patch -p1 --batch --forward < "$PATCH_FILE")

"$K/scripts/config" --file "$OUT/.config" --set-str INITRAMFS_SOURCE ""
export ARCH=arm CROSS_COMPILE="$CROSS"
make -C "$K" O="$OUT" olddefconfig
for requirement in \
    'CONFIG_ARM_APPENDED_DTB=y' \
    'CONFIG_ARM_ATAG_DTB_COMPAT=y' \
    'CONFIG_MMC_BLOCK=y' \
    'CONFIG_MMC_SDHCI_TEGRA=y' \
    'CONFIG_EXT4_FS=y' \
    'CONFIG_DEVTMPFS=y' \
    'CONFIG_USB_G_SERIAL=y' \
    'CONFIG_BRCMFMAC=m' \
    'CONFIG_INITRAMFS_SOURCE=""'; do
    grep -Fx "$requirement" "$OUT/.config" || { echo "Kernel missing: $requirement" >&2; exit 1; }
done

# Keep all existing board drivers (display, touchscreen, battery, USB, etc.).
# CONFIG_INITRAMFS_SOURCE is the ONLY config change from the qualified v034 base.
make -C "$K" O="$OUT" -j"${XOOM_JOBS:-2}" \
    zImage nvidia/tegra20-motorola-stingray.dtb modules

KREL="$(make -s -C "$K" O="$OUT" kernelrelease)"
[[ -s "$OUT/arch/arm/boot/zImage" ]]
[[ -s "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dtb" ]]
[[ -s "$OUT/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko" ]]
[[ -s "$OUT/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko" ]] || {
    echo "Missing upstream WCC plugin: STOP, do not use inline test workaround" >&2; exit 1;
}
sha256sum "$OUT/arch/arm/boot/zImage" \
    "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dtb" \
    "$OUT/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko" \
    "$OUT/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko"
echo "CLEAN_NATIVE_KERNEL_BUILD_PASS RELEASE=$KREL OUTPUT=$OUT"
echo "NO DEVICE WRITES. Android boot partition remains unchanged."
