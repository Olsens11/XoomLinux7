#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
BASE=/home/xoomdev/xoom-linux-rom
K=$BASE/linux-src
O=$BASE/build-wingray-gcc14-initramfs
V=$BASE/phase1-v033
P=$REPO/patches/experiments/v030-stingray-hci-bcm-u4.patch
T=$K/drivers/bluetooth/hci_bcm.c
CROSS=$BASE/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
mkdir -p "$V"
sha=$(sha256sum "$T"|cut -d' ' -f1)
test "$sha" = 3cdaf7e671babfc131f94909c009de0450e6da628786b2f9d9220c85d862bda2
cp "$T" "$V/original-hci_bcm.c"
cleanup() {
 cp "$V/original-hci_bcm.c" "$T"
 test "$(sha256sum "$T"|cut -d' ' -f1)" = "$sha" || echo "FATAL HCI RESTORE MISMATCH" >&2
}
trap cleanup EXIT
git -C "$K" apply --check --whitespace=nowarn "$P"
git -C "$K" apply --whitespace=nowarn "$P"
echo BUILDING_BT_DEPENDENCY_MODULES
set +e
make -j2 -C "$K" O="$O" ARCH=arm CROSS_COMPILE="$CROSS" \
  crypto/ecc.ko crypto/ecdh_generic.ko crypto/cmac.ko net/bluetooth/bluetooth.ko drivers/bluetooth/btbcm.ko drivers/bluetooth/hci_uart.ko >"$V/modules-build.log" 2>&1
rc=$?
set -e
if [ "$rc" -ne 0 ]; then tail -75 "$V/modules-build.log"; exit "$rc"; fi
for obj in crypto/ecc.ko crypto/ecdh_generic.ko crypto/cmac.ko net/bluetooth/bluetooth.ko drivers/bluetooth/btbcm.ko drivers/bluetooth/hci_uart.ko; do
  test -f "$O/$obj"
  cp "$O/$obj" "$V/$(basename "$obj")"
  file "$V/$(basename "$obj")"
  sha256sum "$V/$(basename "$obj")"
done
echo V033_BT_MODULE_BUILD_PASS
