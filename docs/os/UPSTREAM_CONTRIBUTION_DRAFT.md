# Draft for xoom-linux/linux maintainer — DO NOT SEND UNTIL PHYSICALLY QUALIFIED

## Subject
Motorola Xoom MZ600 / BCM4329: firmware MAC bootstrap prerequisite and native Linux 7 bring-up

## Technical finding (source and physical results)

The original xoom-linux Tegra20 DTS and mainline brcmfmac enumerate BCM4329 SDIO Function 1. On our replacement MZ600, firmware `4.220.48` reached SDPCM shared-memory version 3, but repeatedly timed out waiting for F2, `IOEx=0x06 / IORx=0x02 / -62`. Reading the private firmware console showed `Failed to init wireless side, err: 21`. Motorola's original `dhd_common.c` explains that a default MAC must be present in chip OTP or NVRAM *before* firmware bring-up; unique per-unit MAC was historically provided via `ATAG_STINGRAY_MAC` and the board's `get_mac_addr` callback.

A one-field, reversible comparison adding Motorola's original common bootstrap `macaddr` line to a MAC-free but otherwise byte-matched 1550-byte calibration caused **F2 to become ready (0)**. That then exposed an independent missing `brcmfmac-wcc` userspace module-loading dependency (`-ENOENT`). Temporarily linking upstream WCC vendor ops into the diagnostic module caused **native `wlan0` to appear**. We did not scan, associate, or assert per-device identity/regulatory correctness.

## Intended small upstream fix (not ready for PR yet)

1. Preserve Motorola's device-unique factory WLAN MAC during normal boot: vendor `ATAG_STINGRAY_MAC` → Wi-Fi SDIO FDT `local-mac-address` before brcmfmac initializes. Linux already supports `eth_platform_get_mac_address` and NVRAM injection; leave the MAC field **out** of generic board files. Do not hardcode Motorola's shared bootstrap value.
2. Package/load upstream **separate** `brcmfmac-wcc.ko` through the normal rootfs/kmod path; do not upstream the temporary inline WCC experiment.
3. Retain Tegra20 USB0 UDC/peripheral-mode DT settings for normal ttyGS0 access if using a USB gadget serial build.

The branch [os/mz600-native-rootfs-wifi-20261024](https://github.com/Olsens11/XoomLinux7/tree/os/mz600-native-rootfs-wifi-20261024) now has a compiled clean normal OS kernel, minimal Motorola ATAG converter patch, 768MiB Debian armhf ext4 system image, non-diagnostic Android-format boot image and all offline tests passing.

**Do not yet contact upstream as though this is a finished fix:** normal installed-OS boot and actual factory ATAG availability have not been tested. The current image is uninstalled. Need verified same-unit MAC, USB login, F2, `wlan0`, network stability, repeated boot, and a minimal patch diff appropriate to upstream tree. Never share MACs, proprietary firmware, full console dumps, password hashes, or device identifiers.

**Status:** Prepared for a future respectful issue/PR once the remaining acceptance gates are complete. No message/issue/PR posted.
