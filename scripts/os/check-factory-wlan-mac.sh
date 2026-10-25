#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
# Normal installed OS boot only. Do not print or invent hardware MAC values.
set -eu
DT_MAC=/sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address
if [ ! -r "$DT_MAC" ]; then
    echo "WLAN_DISABLED: no verified Motorola bootloader MAC in Device Tree" >&2
    exit 1
fi
bytes="$(wc -c < "$DT_MAC")"
[ "$bytes" -eq 6 ] || { echo "WLAN_DISABLED: invalid MAC length" >&2; exit 1; }
set -- $(od -An -tu1 "$DT_MAC")
[ "$#" -eq 6 ] || exit 1
# Reject all-zero, multicast, and the original unprogrammed 00:90:4c:00:00:00.
[ "$(( $1 & 1 ))" -eq 0 ] || { echo "WLAN_DISABLED: multicast identity" >&2; exit 1; }
[ "$(( $1 | $2 | $3 | $4 | $5 | $6 ))" -ne 0 ] || exit 1
if [ "$1" -eq 0 ] && [ "$2" -eq 144 ] && [ "$3" -eq 76 ] &&
   [ "$4" -eq 0 ] && [ "$5" -eq 0 ] && [ "$6" -eq 0 ]; then
    echo "WLAN_DISABLED: unprogrammed Motorola fallback" >&2
    exit 1
fi
echo "WLAN_FACTORY_MAC_VALID: exact six-byte per-device FDT identity available"
# WCC first. brcmfmac and the NVRAM parser remain upstream and unchanged.
modprobe brcmfmac-wcc
modprobe brcmfmac
