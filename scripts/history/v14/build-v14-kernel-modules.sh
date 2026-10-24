#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
K=$B/linux-src
O=$B/build-wingray-gcc14-initramfs
V=$B/phase1-v14
ROOT=$B/firmware-reference-v07
export ARCH=arm CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
test -s "$V/phase1-initramfs.cpio.gz"
cd "$K"
./scripts/config --file "$O/.config" \
 --enable MODULES --enable MODULE_UNLOAD --enable CFG80211 \
 --module BRCMUTIL --module BRCMFMAC \
 --enable BRCMFMAC_SDIO --enable BRCMDBG \
 --enable FW_LOADER --enable RESET_GPIO \
 --set-str INITRAMFS_SOURCE "$V/phase1-initramfs.cpio.gz" \
 --set-str EXTRA_FIRMWARE "regulatory.db regulatory.db.p7s" \
 --set-str EXTRA_FIRMWARE_DIR "$ROOT"
make O="$O" olddefconfig
for k in 'CONFIG_BRCMUTIL=m' 'CONFIG_BRCMFMAC=m' 'CONFIG_CFG80211=y' 'CONFIG_MODULE_UNLOAD=y' 'CONFIG_USB_G_SERIAL=y' 'CONFIG_BRCMDBG=y' '# CONFIG_NEON is not set';do grep -Fx "$k" "$O/.config";done
grep -Fx 'CONFIG_EXTRA_FIRMWARE="regulatory.db regulatory.db.p7s"' "$O/.config"
echo 'BUILD V14 STABLE KERNEL WITH HOT-RELOADABLE BROADCOM MODULES'
make -j2 O="$O" zImage nvidia/tegra20-motorola-stingray-usbdiag.dtb \
 drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko \
 drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko > "$B/build-stingray-v14-stage1.log" 2>&1 || { tail -n 100 "$B/build-stingray-v14-stage1.log";exit 1; }
for ko in "$O/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko" "$O/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko";do
 test -s "$ko";file "$ko";sha256sum "$ko";
done
echo 'V14 KERNEL AND MODULES STAGE1 PASS'
