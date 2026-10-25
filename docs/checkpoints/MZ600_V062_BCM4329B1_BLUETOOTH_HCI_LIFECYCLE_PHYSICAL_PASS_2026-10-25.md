# Motorola Xoom MZ600 clean Linux 7 v06.2 — BCM4329B1 Bluetooth HCI physical bring-up PASS

**Test date:** 2026-10-25, 17:47–17:52 EDT, no microSD. **Upstream base:** xoom-linux/linux `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, WIP Stingray board DTS and WLAN MAC ATAG→FDT patch. **Image:** exact physically booted RAM-only v06.2 SHA256 `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`, 6,549,504B. **No reboot, flash, partitions, Bluetooth discovery/pairing, RF scan, network association, or firmware patchram upload.**

## Starting state and controls

Surface USB COM9 was responsive to `PING`; Linux 7 v06.2 running with previously **physically verified Wi-Fi** `WIFI_START → wlan0 → WIFI_STOP`, all `brcmfmac_wcc`/`brcmfmac`/`brcmutil` modules unloaded. `WIFI_STATUS` confirmed `WLAN0 ABSENT` and modules not present. `BT_STATUS` initially showed HCI_UART not loaded and `HCI0 ABSENT`; `MMC2_STATUS` confirmed onboard SDIO **BCM4329 verified**. The USB dashboard diagnostic does not automatically load Bluetooth.

## Stage 1: actual HCI controller registration

Guarded Surface private script `C:\Users\olsen\xoom-linux-rom\captures\Xoom-V062-BT-Start-Stage1-Once.ps1`, privately logged to `MZ600-V062-BT-START-FIRST-20261025-PRIVATE.txt`. Executed **one** `BT_START` over USB, then BT_STATUS, LOGS, PING.

All six same-kernel ABI modules loaded in correct dependency order with **`rc 0`**: `ecc`, `ecdh_generic`, `cmac`, `bluetooth`, `btbcm`, `hci_uart`. `BT_STATUS` showed **`BLUETOOTH HCI_UART MODULE LOADED`**, **`HCI0 PRESENT`**, `BT_STARTED_FLAG 1`. Linux log:

```
Bluetooth: HCI UART protocol Broadcom registered
Bluetooth: hci0: BCM: chip id 41
Bluetooth: hci0: BCM: features 0x04
Bluetooth: hci0: BCM4329B1
Bluetooth: hci0: BCM4329B1 (002.002.023) build 0000
```

Driver searched for firmware patch at, in order, `brcm/BCM4329B1.motorola,stingray.hcd`, `brcm/BCM4329B1.hcd`, `brcm/BCM.motorola,stingray.hcd`, `brcm/BCM.hcd`, and logged **`firmware Patch file not found`**. This is a **firmware gap**, not failure to enumerate HCI0. No claim full patched radio/keyboard functionality.

Stage 1 retained live COM9 PING/PONG PASS.

## Stage 2: basic HCI up/down and clean module unload

Guarded Surface script `C:\Users\olsen\xoom-linux-rom\captures\Xoom-V062-BT-ON-OFF-Once.ps1`, raw private log `MZ600-V062-BT-ON-OFF-20261025-PRIVATE.txt`, read-only preflights confirmed HCI0 present, BT HCI_UART loaded, Wi-Fi not loaded. **One** `BT_ON` gave **`BT ON HCI_DEV_UP rc 0`**, `BT ON REQUEST COMPLETE`, `BT_USB_ON_REQUESTED_FLAG 1`, and `HCI0 PRESENT`. No Bluetooth discovery/pairing commands or external wireless link tested.

A single `BT_OFF` subsequently gave **`BT OFF HCI_DEV_DOWN rc 0`**. One `BT_STOP` removed all six modules with **`rc 0`** in this order: `hci_uart`, `btbcm`, `bluetooth`, `cmac`, `ecdh_generic`, `ecc`. It reported `BT STOP END MODULE UNLOADED`. Final `BT_STATUS`: `HCI0 ABSENT`, HCI_UART not loaded. COM9 PONG after cleanup true and USB remained connected. **Radio and USB program stay running, Bluetooth software left unloaded**.

**PHYSICAL PASS:** native Linux Broadcom HCI UART/serdev registration, BCM4329B1 controller identified over UART, HCI_DEV_UP and DOWN commands accepted, all dependent modules unload and USB remains alive. Not a full chip reset/PMIC vote validation.

## Candidate Bluetooth firmware now privately available (NOT COMMITTED)

User previously uploaded `BCM4329B1.hcd` to ChatGPT Library on 2026-10-24; identical candidate file also exists on Surface Downloads. Bytes **17,332**, SHA256 **`7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`** across Library and Surface. Local offline parse of vendor HCI patch-command stream PASS: **98 well-formed HCI commands**, 97 opcode `0xFC4C` and one `0xFC4E`; **no device compatibility or licensing approval inferred solely from file syntax**.

File copied privately from Surface to Desktop Windows home and then to Desktop WSL path `/home/xoomdev/xoom-linux-rom/private-firmware/BCM4329B1.hcd`; SHA independently matched again. **Do not commit raw proprietary/vendor firmware, link it publicly, or include its bytes in checkpoint.** This is a candidate matching the Linux driver's requested `brcm/BCM4329B1.hcd` basename, but physical patched-firmware initialization is untested.

Current v06.2 USB `UPLOAD` allowlist only accepts `BRCMFMAC`, `BRCMUTIL`, `WCC`, `FIRMWARE` (Wi-Fi `.bin`) and `NVRAM`. There is **no `UPLOAD BTHCD`** destination and the current BT modules have already been unloaded; the correct route is a reproducible **private v06.3 initramfs candidate** with the HCD in `/lib/firmware/brcm/BCM4329B1.hcd`, then controlled `BT_START` on that candidate (with no SD and known good reset baseline). Prefer one small lab userspace change per image. Never replace the preserved v06.2 image.

## Keyboard pairing: work still needed

For an OEM Motorola classic Bluetooth keyboard, require more than `hci0`:

1. Verify candidate HCD is accepted at HCI controller creation and observe patchlevel/baud/kernel log; test `HCIDEVUP` with firmware applied.
2. Add standard Bluetooth pairing userspace (e.g. Debian BlueZ `bluetoothd`/`bluetoothctl` plus D-Bus and appropriate input stack), or a narrowly scoped bounded HCI/L2CAP/HIDP test tool. The bare-metal freestanding diagnostic `/init` currently **does not contain a pairing agent or general BlueZ toolchain**.
3. Ensure HIDP (for classic HID keyboards) or UHID/evdev path and keyboard keymap; discover/inquire, verify unique device address, accept PIN/passkey, bond and connect, observe `/dev/input/event*` only after a secure pairing path is implemented.
4. Preserve Bluetooth keys/bonding state to the SD card when the Debian/rootfs environment is available (currently **no SD inserted**, so RAM bonding state would be volatile). Do not enable general discoverability or auto-pairing while the security/agent interface is missing.
5. Test clean `BT_OFF`/module unload after firmware, along with CPCAP/USB power lifecycle. WCC Wi-Fi unload was separately physically proven in v06.2; **simultaneous Wi-Fi and BT remain untested**, and separate driver tests must not be treated as a complete combo-chip power reset.

**Patch tracking:** These physical observations validate original upstream-compatible Bluetooth modules + lab diagnostic controls on our WIP board DTS; **no new upstream Linux source patch** has yet been required. Future true DTS/regulator/clock fixes should be separately staged with binary/test evidence and honest DCO status. Bluetooth private firmware and BlueZ userspace are not themselves patches to the upstream Linux kernel.

**Current device status:** Xoom runs v06.2 with successful USB COM9. Both Wi-Fi and Bluetooth module stacks are stopped/unloaded as of the last physical test. No reboot after Bluetooth experiment.
