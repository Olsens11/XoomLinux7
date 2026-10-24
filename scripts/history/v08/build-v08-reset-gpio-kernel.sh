#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
SRC=$B/linux-src
OUT=$B/build-wingray-gcc14-initramfs
ROOT=$B/firmware-reference-v07
INIT=$B/phase1-v08/phase1-initramfs.cpio.gz
FW1=$ROOT/brcm/brcmfmac4329-sdio.bin
FW2=$ROOT/brcm/brcmfmac4329-sdio.txt
gzip -t "$INIT";test -s "$FW1";test -s "$FW2"
! grep -Eiq '^[[:space:]]*(macaddr|ccode|regrev)=' "$FW2"
export ARCH=arm CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
cd "$SRC"
./scripts/config --file "$OUT/.config" --set-str INITRAMFS_SOURCE "$INIT" --enable RESET_GPIO
make O="$OUT" olddefconfig
for opt in CONFIG_RESET_GPIO=y CONFIG_PWRSEQ_SIMPLE=y CONFIG_BRCMFMAC=y CONFIG_BRCMUTIL=y CONFIG_CFG80211=y CONFIG_BRCMFMAC_SDIO=y CONFIG_USB_G_SERIAL=y;do
 grep -Fx "$opt" "$OUT/.config"
done
grep -Fx '# CONFIG_NEON is not set' "$OUT/.config"
grep -F 'brcm/brcmfmac4329-sdio.bin brcm/brcmfmac4329-sdio.txt' "$OUT/.config"
grep -Fx "CONFIG_EXTRA_FIRMWARE_DIR=\"$ROOT\"" "$OUT/.config"
echo 'V08 ENABLES RESET_GPIO AND READ-ONLY SDIO BOOTLOG; NO NETWORK ASSOCIATION'
make -j2 O="$OUT" nvidia/tegra20-motorola-stingray-usbdiag.dtb zImage > "$B/build-stingray-v08.log" 2>&1 || { tail -n 75 "$B/build-stingray-v08.log";exit 1; }
cmp "$INIT" "$OUT/usr/initramfs_inc_data"
sha256sum "$FW1" "$FW2" "$INIT" "$OUT/usr/initramfs_inc_data" "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
stat -c '%n %s bytes' "$OUT/arch/arm/boot/zImage"
echo 'V08 KERNEL VERIFIED AND READY FOR PACKAGING (NO DEVICE WRITES)'
