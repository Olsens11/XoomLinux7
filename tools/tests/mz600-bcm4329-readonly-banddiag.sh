#!/bin/sh
# Read-only on-device verification AFTER a separately authorized temporary boot.
# Do not source into the normal boot path, do not change firmware or regulatory settings.
set -eu
printf '%s\n' '=== Kernel ABI ==='
uname -r
printf '%s\n' '=== Root mount source ==='
findmnt -n -o SOURCE,FSTYPE /
printf '%s\n' '=== Firmware IOCTL diagnostic (only emitted by lab image) ==='
dmesg | grep -F 'MZ600_IOREAD_' || :
printf '%s\n' '=== PHY bands ==='
iw phy phy0 info | grep -E 'Band [0-9]+:' || :
printf '%s\n' '=== Network state (no SSID or MAC output) ==='
nmcli -g GENERAL.STATE device show wlan0 || :
printf '%s\n' '=== Wi-Fi driver module identity ==='
modinfo -F vermagic brcmfmac || :
printf '%s\n' '=== End read-only capture ==='
