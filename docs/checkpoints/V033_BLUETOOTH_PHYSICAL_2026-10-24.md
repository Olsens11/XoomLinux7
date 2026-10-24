# v033 physical Bluetooth/U4 integration test — replacement MZ600

**Date:** 2026-10-24. **Verdict:** Successful nonpersistent v033 boot, successful real Bluetooth-core identification and shared-U4 vote ON/OFF, but Bluetooth firmware patch missing and **Wi-Fi F2 still -62**. No system, recovery or userdata flashing.

## Device, image, and route

- Original verified v025 Linux USB handler acknowledged guarded REBOOT; replacement device subsequently appeared as Android ADB. Strictly verified the replacement-device identity before adb reboot bootloader; fastboot identified `product=xoom-cdma`, `unlocked=yes`. Executed **fastboot boot only**, never flash.
- v033 candidate: 6,979,584-byte `MZ600-v033-BLUETOOTH-USB-TEMPBOOT-ONLY.img`, SHA256 `6806f2aa87abbfecf0b2f8a3625292de5366a4a52370d10e61cd53204069fb45`; both candidate and v025 fallback SHA256 pre-verified on Surface. Fastboot reported upload OK and Booting OK; COM9 returned.
- First v033 USB `BT_STATUS`: HCI UART module **NOT LOADED**, `hci0` ABSENT, both USB BT flags zero. MMC2 bound, BCM4329 enumerated, no Wi-Fi driver loaded. Therefore v033's v025-derived kernel, corrected BT DTB and new external initramfs actually executed.

## Actual live commands and kernel results

1. `BT_START` loaded `ecc`, `ecdh_generic`, `cmac`, `bluetooth`, `btbcm`, and `hci_uart` in dependency order; all returned module insertion rc=0. `BT_STATUS` verified HCI0 PRESENT and all six module dependencies loaded.
2. Despite the host's 'HCI POWER NOT REQUESTED' message, Linux `hci_uart_register_device()` performed **automatic chip power initialization at module insertion time**. This invalidates the prototype assumption that module binding was electrically passive.
3. Linux logs showed `XOOM_V030 event=BT_RESET_REQUEST release=0` at kernel t≈64.510s; `BT_U4_VOTE_ON` at 64.6813s; `BT_RESET_REQUEST release=1` at 64.6817s; then real UART Bluetooth response. HCI recognized **BCM4329B1**, chip id 41, features 0x04, firmware identification `(002.002.023) build 0000`.
4. Broadcom HCI driver tried but could not find BT patch firmware `brcm/BCM4329B1.motorola,stingray.hcd`, `brcm/BCM4329B1.hcd` or generic `BCM...hcd`. The chip-identification response **does not prove patched, fully functional Bluetooth**.
5. `BT_OFF` returned `HCIDEVDOWN rc=-19`, incorrectly labeled 'COMPLETE OR ALREADY DOWN'. Source inspection later proved PID1 passed **pointer to int** where Linux `hci_sock_ioctl()` expects **HCI device number as the ioctl argument itself**. `hci_dev_close(arg)` therefore tried the wrong device and returned ENODEV. This is a **userspace ABI bug**, not evidence that the chip does not support BT shutdown.
6. `BT_STOP` subsequently unloaded **all six modules (rc=0)**. Logs positively recorded `BT_RESET_REQUEST release=0` and `BT_U4_VOTE_OFF` at t≈144.620s. `BT_STATUS` then showed HCI0 ABSENT and no modules, MMC2 still bound, AUTO=0, USB responsive. The proper module-remove path cleaned up the shared regulator vote even though the earlier ioctl did not.
7. With BT completely unloaded, loaded the original v025 Wi-Fi binaries through existing `WIFI_START`. Firmware RAM download/readback passed, 25MHz legacy SDIO remained in effect. Function 2 again failed: `IOEx 02→06`, `IORx 02→02`, result `-62`; `wlan0` absent. Ran `WIFI_STOP` rc=0 for both modules; final MMC2 status valid, bound, BCM4329 card verified, driver modules unloaded.

## What the test actually proves

- Motorola-gated Linux `hci_bcm` reached a working Bluetooth command interface and drove its **requested** U4 regulator vote on/off and U0 reset in kernel order. The Bluetooth CPU/firmware responded to chip-identification traffic. We have **not** measured analog pin voltages, internal VDDC dropout, complete chip POR, correct timing at pads or final Bluetooth radio functions.
- BT shared supply voting while MMC2 also holds U4 is not a full chip off/on cycle. The unchanged F2 failure is therefore useful negative evidence about this **specific** coordination experiment, not a disproof of all BCM4329 power/PMU theories.
- The on-demand protocol has two newly proven concerns: auto hardware power-up on HCI UART module bind; HCI ioctl expects integer device ID by value. Both require a v034 correction and independent test before relying on USB `BT_OFF` as a safety control.

## Final condition

**Running v033 temporary Linux, COM9 reachable, MMC2 bound with BCM4329 detected, AUTO profile 0, Bluetooth and Wi-Fi modules both unloaded, no wlan0.** Original Android/recovery partitions unchanged. v025 rollback image remains hash-verified on Surface.
