#!/usr/bin/env bash
# v030 SOURCE-ONLY qualification; no hardware access.
set -euo pipefail
REPO=/home/xoomdev/projects/XoomLinux7-bt-v030
BASE=/home/xoomdev/xoom-linux-rom
K=$BASE/linux-src
WORK=$BASE/phase1-v030-bt-power
BT=$K/drivers/bluetooth/hci_bcm.c
CROSS=$BASE/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
OLD=$(sha256sum "$BT" | awk '{print $1}')
python3 "$REPO/scripts/experiments/v030-prepare-stingray-bt-u4.py"
(cd "$K" && git apply --check "$REPO/patches/experiments/v030-stingray-hci-bcm-u4.patch")
make -s -j2 -C "$K" ARCH=arm CROSS_COMPILE="$CROSS" \
 O="$BASE/build-wingray-gcc14-initramfs" M="$WORK" hci_bcm.o
NEW=$(sha256sum "$BT" | awk '{print $1}')
if [[ "$NEW" != "$OLD" ]]; then
  echo 'FATAL: kernel source changed' >&2; exit 1
fi
file "$WORK/hci_bcm.o"
sha256sum "$WORK/hci_bcm.o"
if ! grep -Fq 'of_device_is_compatible' "$WORK/hci_bcm.c"; then exit 1; fi
if ! grep -Fq 'regulator_enable(dev->stingray_shared)' "$WORK/hci_bcm.c"; then exit 1; fi
if ! grep -Fq 'regulator_disable(dev->stingray_shared)' "$WORK/hci_bcm.c"; then exit 1; fi
OUT=$WORK/board
mkdir -p "$OUT"
cp "$REPO/src/board/tegra20-motorola-stingray-usbdiag.dts" "$OUT/stingray-v030.dts"
printf '\n#include "tegra20-stingray-bcm4329-bt-u4-v030.dtsi"\n' >> "$OUT/stingray-v030.dts"
gcc -E -P -x assembler-with-cpp -nostdinc -undef -D__DTS__ \
 -I "$K/include" -I "$K/arch/arm/boot/dts" -I "$K/arch/arm/boot/dts/nvidia" \
 -I "$REPO/src/chip" "$OUT/stingray-v030.dts" -o "$OUT/stingray-v030.pre.dts"
dtc -q -I dts -O dtb -o "$OUT/stingray-v030.dtb" "$OUT/stingray-v030.pre.dts"
NODE=/serial@70006200/bluetooth
test "$(fdtget -t s "$OUT/stingray-v030.dtb" "$NODE" status)" = disabled
fdtget -t s "$OUT/stingray-v030.dtb" "$NODE" compatible
fdtget -t x "$OUT/stingray-v030.dtb" "$NODE" shared-supply
fdtget -t s "$OUT/stingray-v030.dtb" "$NODE" motorola,shared-u4-power >/dev/null 2>&1 || \
  fdtget -p "$OUT/stingray-v030.dtb" "$NODE" | grep -Fx 'motorola,shared-u4-power'
test "$(fdtget -t x "$OUT/stingray-v030.dtb" /mmc@c8000200 max-frequency)" = 2c04076
python3 "$REPO/scripts/experiments/v030-check-stingray-bt-u4.py" \
 "$WORK/hci_bcm.c" "$OUT/stingray-v030.dtb"
echo V030_PRIVATE_KERNEL_COMPILE_AND_DISABLED_DTB_PASS
echo LIVE_XOOM_UNCHANGED
