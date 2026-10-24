#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
K="$B/linux-src"
OUT="$B/build-wingray-gcc14-initramfs"
export ARCH=arm CROSS_COMPILE="$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
cd "$K"
./scripts/config --file "$OUT/.config" --enable CFG80211 --module BRCMUTIL --module BRCMFMAC --enable BRCMFMAC_SDIO
make O="$OUT" olddefconfig
grep -Fx 'CONFIG_BRCMFMAC=m' "$OUT/.config"
grep -Fx 'CONFIG_BRCMUTIL=m' "$OUT/.config"
grep -Fx 'CONFIG_CFG80211=y' "$OUT/.config"
grep -Fx 'CONFIG_MODULES=y' "$OUT/.config"
grep -Fx '# CONFIG_NEON is not set' "$OUT/.config"
grep -Fx 'CONFIG_USB_G_SERIAL=y' "$OUT/.config"
echo "BUILDING DEFERRED BRCMFMAC KERNEL MODULE ONLY"
make -j2 O="$OUT" drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko > "$B/build-stingray-v08-module.log" 2>&1 || { tail -n 110 "$B/build-stingray-v08-module.log";exit 1; }
KO="$OUT/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
test -s "$KO"
file "$KO"
sha256sum "$KO"
stat -c "BRCMFMAC_MODULE=%s bytes" "$KO"
"$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-readelf" -h "$KO" | grep -e 'Class:' -e 'Machine:'
UT="$OUT/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko"
test -s "$UT"
sha256sum "$UT"
stat -c "BRCMUTIL_MODULE=%s bytes" "$UT"
echo "V08 DEFERRED MODULE VERIFIED; STILL NO XOOM CHANGES"
