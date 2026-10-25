#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
# Install stock modular Linux 7 wireless drivers in the OFFLINE OS rootfs.
set -euo pipefail
[[ $# -eq 1 ]] || { echo "usage: $0 /path/to/staged-debian-armhf-rootfs" >&2; exit 2; }
[[ "$(id -u)" == 0 ]] || { echo "root needed for modules_install ownership" >&2; exit 1; }
ROOT="$(readlink -f "$1")"
[[ "$ROOT" == */bookworm-armhf-root && -f "$ROOT/etc/debian_version" ]] || exit 1
B="${XOOM_BUILD_ROOT:-/home/xoomdev/xoom-linux-rom}"
K="${XOOM_LINUX_SOURCE:-$B/linux-src}"
O="${XOOM_OS_KERNEL_OUT:-$B/os-build/kernel}"
CROSS="${XOOM_CROSS_COMPILE:-$B/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-}"
[[ -s "$O/arch/arm/boot/zImage" ]] || { echo "Build clean native kernel first" >&2; exit 1; }
export ARCH=arm CROSS_COMPILE="$CROSS"
REL="$(make -s -C "$K" O="$O" kernelrelease)"
[[ -s "$O/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko" ]] || {
    echo "Upstream WCC plugin not built" >&2; exit 1;
}
make -C "$K" O="$O" INSTALL_MOD_PATH="$ROOT" INSTALL_MOD_STRIP=1 modules_install
# Linux on an ARM root needs a matching module dependency database in /lib/modules.
depmod -b "$ROOT" "$REL"
for mod in brcmfmac brcmfmac-wcc brcmutil; do
    find "$ROOT/lib/modules/$REL" -name "$mod.ko*" -type f | grep -q . || {
        echo "Missing OS driver package: $mod" >&2; exit 1;
    }
done
echo "NATIVE_OS_MODULES_INSTALLED release=$REL"
echo "Separate brcmfmac-wcc plugin preserved. No inline vendor workaround."
echo "No partition/image flashing."
