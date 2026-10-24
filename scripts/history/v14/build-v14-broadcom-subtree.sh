#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
export ARCH=arm
export CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
cd "$B/linux-src"
make -j2 O="$B/build-wingray-gcc14-initramfs" M=drivers/net/wireless/broadcom/brcm80211 modules >"$B/build-stingray-v14-modules.log" 2>&1 || { tail -n 70 "$B/build-stingray-v14-modules.log";exit 1; }
sha256sum "$B/build-wingray-gcc14-initramfs/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko" "$B/build-wingray-gcc14-initramfs/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
echo V14_BRCM_MODULES_VERIFIED
