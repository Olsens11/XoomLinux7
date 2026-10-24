#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
SRC=$B/linux-src
OUT=$B/build-wingray-gcc14-initramfs
ROOT=$B/firmware-reference-v07
FW1="$ROOT/brcm/brcmfmac4329-sdio.bin"
FW2="$ROOT/brcm/brcmfmac4329-sdio.txt"
INIT="$B/phase1-v07/phase1-initramfs.cpio.gz"
test -s "$FW1";test -s "$FW2";gzip -t "$INIT"
! grep -iq -e '^macaddr=' -e '^ccode=' -e '^regrev=' "$FW2"
export ARCH=arm
export CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
cd "$SRC"
./scripts/config --file "$OUT/.config" \
 --set-str INITRAMFS_SOURCE "$INIT" \
 --enable CFG80211 --enable BRCMUTIL --enable BRCMFMAC \
 --enable FW_LOADER \
 --set-str EXTRA_FIRMWARE "brcm/brcmfmac4329-sdio.bin brcm/brcmfmac4329-sdio.txt" \
 --set-str EXTRA_FIRMWARE_DIR "$ROOT"
make O="$OUT" olddefconfig
grep -Fx 'CONFIG_CFG80211=y' "$OUT/.config"
grep -Fx 'CONFIG_BRCMUTIL=y' "$OUT/.config"
grep -Fx 'CONFIG_BRCMFMAC=y' "$OUT/.config"
grep -Fx 'CONFIG_BRCMFMAC_SDIO=y' "$OUT/.config"
grep -Fx 'CONFIG_USB_G_SERIAL=y' "$OUT/.config"
grep -Fx '# CONFIG_NEON is not set' "$OUT/.config"
grep -F 'CONFIG_EXTRA_FIRMWARE=' "$OUT/.config"
grep -Fx "CONFIG_EXTRA_FIRMWARE_DIR=\"$ROOT\"" "$OUT/.config"
echo "V07 KERNEL BUILD: MAINLINE BRCMFMAC/CFG80211 BUILT-IN, TWO BUILT-IN FIRMWARE REFERENCES"
make -j2 O="$OUT" nvidia/tegra20-motorola-stingray-usbdiag.dtb zImage > "$B/build-stingray-v07.log" 2>&1 || { tail -n 100 "$B/build-stingray-v07.log";exit 1; }
cmp "$INIT" "$OUT/usr/initramfs_inc_data"
sha256sum "$FW1" "$FW2" "$INIT" "$OUT/usr/initramfs_inc_data" "$OUT/arch/arm/boot/zImage" "$OUT/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
stat -c '%n %s bytes' "$OUT/arch/arm/boot/zImage"
echo 'V07 BUILD VERIFIED; NO XOOM WRITES'
