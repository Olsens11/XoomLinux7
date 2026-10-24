#!/usr/bin/env bash
set -euo pipefail
B=/home/xoomdev/xoom-linux-rom
SRC=$B/linux-src
OUT=$B/build-wingray-gcc14-initramfs
ROOT=$B/firmware-reference-v07
INIT=$B/phase1-v09/phase1-initramfs.cpio.gz
for name in brcm/brcmfmac4329-sdio.bin brcm/brcmfmac4329-sdio.txt regulatory.db regulatory.db.p7s;do test -s "$ROOT/$name";done
test "$(wc -c < "$ROOT/regulatory.db")" -eq 6348
test "$(wc -c < "$ROOT/regulatory.db.p7s")" -eq 1085
! grep -iq -e '^macaddr=' -e '^ccode=' -e '^regrev=' "$ROOT/brcm/brcmfmac4329-sdio.txt"
gzip -t "$INIT"
export ARCH=arm CROSS_COMPILE=$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
cd "$SRC"
./scripts/config --file "$OUT/.config" \
 --set-str INITRAMFS_SOURCE "$INIT" \
 --enable CFG80211 --enable BRCMUTIL --enable BRCMFMAC \
 --enable CFG80211_REQUIRE_SIGNED_REGDB --enable CFG80211_USE_KERNEL_REGDB_KEYS \
 --set-str EXTRA_FIRMWARE "brcm/brcmfmac4329-sdio.bin brcm/brcmfmac4329-sdio.txt regulatory.db regulatory.db.p7s" \
 --set-str EXTRA_FIRMWARE_DIR "$ROOT"
make O="$OUT" olddefconfig
for k in CONFIG_CFG80211=y CONFIG_BRCMUTIL=y CONFIG_BRCMFMAC=y CONFIG_BRCMFMAC_SDIO=y CONFIG_USB_G_SERIAL=y CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y CONFIG_CFG80211_USE_KERNEL_REGDB_KEYS=y;do grep -Fx "$k" "$OUT/.config";done
grep -Fx '# CONFIG_NEON is not set' "$OUT/.config"
grep -F 'CONFIG_EXTRA_FIRMWARE=' "$OUT/.config"
echo 'BUILDING V09 OFFICIAL SIGNED REGDB + BROADCOM NATIVE KERNEL'
make -j2 O="$OUT" nvidia/tegra20-motorola-stingray-usbdiag.dtb zImage > "$B/build-stingray-v09.log" 2>&1 || { tail -n 90 "$B/build-stingray-v09.log";exit 1; }
cmp "$INIT" "$OUT/usr/initramfs_inc_data"
sha256sum "$ROOT/regulatory.db" "$ROOT/regulatory.db.p7s" "$ROOT/brcm/brcmfmac4329-sdio.txt" "$INIT" "$OUT/arch/arm/boot/zImage"
echo 'V09 SIGNED REGDB BUILD AND INITRAMFS VALIDATED; NO TABLET WRITES'
