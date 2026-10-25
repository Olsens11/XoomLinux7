# Motorola Xoom MZ600 — v06.3 exact-image RAM boot, Bluetooth HCD path, HCI on/off and subsequent Wi-Fi — PHYSICAL PASS

**2026-10-25 19:04–19:13 EDT.** **This later SUCCESS follows an unsuccessful first v06.3 attempt earlier the same evening.** Preserve both outcomes and their different preceding board/reset conditions. **No flashing, SD use, eMMC modification, network scan, Wi-Fi association, Bluetooth discovery or pairing.**

## Original red-light / power-button observation preceding successful retest

After the first v06.3 fastboot RAM boot at ~18:51 briefly enumerated COM9 but never answered PONG, user observed the camera-side red LED. Disconnecting USB and external power **did not** cure the condition on this recurrence. User performed the following direct physical sequence:

1. **Power + Volume Up** forced start into original Android; shut down from Android.
2. A **brief Power press** still showed the red light, not normal boot.
3. **Power + Volume Up** forced start into TWRP; shut down from TWRP.
4. A brief Power press again showed red light, but **holding Power about three seconds then booted normally into Android**.
5. User used **Power + Volume Up to enter fastboot** and expressly requested another v06.3 test.

**Critical distinction:** The earlier recovery coincided with unplugging *both* cables, but this time removing both alone did **not** fix it, whereas a longer ordinary Power hold appeared effective. This weakens a simplistic USB-cable-only explanation and highlights power-button hold duration, system power-on sequencing, retained peripheral state, and/or delayed reset as variables. No mechanism proven.

## Exact immutable candidate and guarded RAM boot

Image `MZ600-CLEAN-WIFI-BT-USB-v063-HCD-RAM-ONLY-UNTESTED.img`, **6,561,792 bytes**, SHA256 **`07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`**, independently verified on Surface before boot. This is the *identical* v06.3 image used in the first unsuccessful attempt. It contains the same kernel, DTS, USB diagnostic `/init` and radio modules as physically verified v06.2 plus a **single extra private embedded firmware file** `/lib/firmware/brcm/BCM4329B1.hcd` (17,332 bytes, SHA256 `7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`). Proprietary firmware bytes must never be committed to public GitHub.

- **19:02:39 EDT:** independent Surface preflight found authorized unlocked **xoom-cdma** in fastboot; preserved v06.2/v06.3 image SHA checks both PASS, no ADB/COM9 preboot.
- **19:04:20 EDT:** guarded one-shot `Xoom-V063-HCD-USB-Once.ps1` confirmed correct bootloader/product and image SHA.
- **19:04:22.717:** `fastboot boot` accepted, **RAM ONLY** (no flashing or partition operations).
- **19:04:28.431:** COM9 enumerated. First `Write` returned a single semaphore timeout, **not persistent**; **19:04:31.547** Linux responded **PONG**, and **19:04:32.381** read-only `BT_STATUS` returned 223 bytes.
- **19:05:37.919:** full observation completed `FINAL_COM9_PRESENT=True_USB_PONG=True_COM9_ARRIVED=True_COM9_DROPPED=False_ERRORS=1`, no Wi-Fi/BT activation on boot. User independently reported **"it booted."**

**Interpretation:** v06.3 is **physically boot-capable**. Its earlier no-PONG attempt remains real, likely contingent on some unresolved hardware/boot/USB/starting-state variable, not evidence of a consistently defective image.

## First native BCM4329B1 HCD firmware initialization

Surface safe test `captures/Xoom-V063-BT-HCD-Start-Stage1-Once.ps1`, raw PRIVATE log `captures/MZ600-V063-HCD-BT-START-FIRST-20261025-PRIVATE.txt`:

- Preflight `PING`, `WIFI_STATUS` (WLAN unloaded), `BT_STATUS` (BT off), onboard `MMC2_STATUS` BCM4329 verified — all PASS.
- **19:08:04:** explicit `BT_START` loaded **ecc, ecdh_generic, cmac, bluetooth, btbcm, hci_uart**, **each rc 0**. Bluetooth HCI_UART module loaded, **HCI0 PRESENT**.
- Kernel at uptime 208.515s: `Bluetooth: hci0: BCM4329B1 'brcm/BCM4329B1.hcd' Patch`. Subsequent chip queries returned `BCM4329B1 Generic FMRX 37.4 MHz`; initial prepatch identification `BCM4329B1 (002.002.023) build 0000`. No missing-patch error.
- **19:08:14:** USB PONG PASS and COM9 present.
- **Correct acceptance wording:** firmware file was **located and processed by the standard Bluetooth driver**, with functioning HCI0 afterward. This does **not** yet prove over-the-air RF reception, pairing, HID compatibility, all vendor HCD instructions were accepted at the radio hardware level, or FM radio operation.

## HCI on/off and all-six-module cleanup

Surface test `captures/Xoom-V063-HCD-BT-ON-OFF-Once.ps1`, raw PRIVATE `captures/MZ600-V063-HCD-BT-ON-OFF-20261025-PRIVATE.txt`:

- **19:10:31:** explicit `BT_ON HCI_DEV_UP rc 0`; `HCI0 PRESENT`, controller requested-up flag 1.
- **19:10:42:** `BT_OFF HCI_DEV_DOWN rc 0`.
- **19:10:51:** `BT_STOP` removed **hci_uart → btbcm → bluetooth → cmac → ecdh_generic → ecc**, all **rc 0** and reported `BT STOP END MODULE UNLOADED`.
- Final `BT_STATUS`: **HCI0 ABSENT**, HCI_UART module not loaded. Poststop USB PONG PASS and COM9 present. The host script's `ALL_GONE=False` field is a **string-pattern bug**: it searched for `BT STOP END MODULE UNLOADED` in the later `BT_STATUS` response instead of the actual `BT_STOP` response. Six kernel return codes, explicit stop acknowledgement, and later status support real successful unload; do not call this a driver cleanup failure.

## Whole-chip sequential transition: patched Bluetooth → native WLAN

Surface guarded `captures/Xoom-V063-WiFi-after-HCD-BT-Once.ps1`, PRIVATE log `captures/MZ600-V063-WIFI-AFTER-HCD-BT-SEQUENCE-PRIVATE-20261025.txt`:

- **19:12:35:** preflight after HCD-patched HCI lifecycle: Bluetooth unloaded, Wi-Fi unloaded, onboard BCM4329 verified, COM9 PONG.
- **19:12:42:** `WIFI_START` → `brcmutil rc 0`, `brcmfmac rc 0`; auto WCC dependency loaded, firmware initialized.
- **19:12:46:** `WLAN0 PRESENT`, all **brcmfmac_wcc, brcmfmac, brcmutil** loaded.
- Kernel reported `brcmfmac4329-sdio` for BCM4329/3, Wi-Fi firmware **4.220.48**. Optional **clm_blob and txcap_blob absent (err -2)**, which did not block interface probe but leave regulatory/channel coverage unqualified.
- **19:12:57:** `WIFI_STOP` → **WCC rc 0, brcmfmac rc 0, brcmutil rc 0**, ordered unload complete.
- **19:13:01:** final WIFI_STATUS confirmed **all modules unloaded, wlan0 absent**.
- **19:13:04:** post-test USB PONG PASS and COM9 present.

**PHYSICAL PASS:** v06.3 boots, onboard BCM4329B1 HCD patch path is found and processed, HCI controller UP/DOWN works, all Bluetooth modules unload cleanly, and subsequently Wi-Fi firmware and wlan0 initialize and cleanly unload on the SAME kernel session. This validates sequential **BT-with-HCD → Wi-Fi**, **not simultaneous coexistence**.

## Remaining work / unchanged constraints

1. **Actual Wi-Fi RF discovery**: current v06.3 mini initramfs has NO `iw`, `ip`, scan command, or shell. Official Debian 12 ARMHF `iw 5.19` is downloaded/hash verified and QEMU tested OFFLINE, but **not yet integrated**. Need a versioned new RAM image and nl80211 interface setup; scan may transmit probe requests, honor regulatory constraints.
2. **Actual Bluetooth RF/keyboard pairing**: firmware patch processing and HCI_UP do NOT prove discovery, user keyboard authentication, keys, HIDP, evdev or terminal input. Add supported BlueZ, D-Bus/pairing UI, keyboard event path and real on-screen terminal as requested.
3. **Entire combo-chip**: shared U4 rail power/refcount, WLAN U2, BT U0/I7/reset, 32kHz LPO, wake pins, software module unloading vs measured hardware POR and **simultaneous Wi-Fi/Bluetooth** still unverified. FM “FMRX” string identifies firmware description, not proven FM reception/wiring.
4. **Power/red LED**: exact same v06.3 image was once no-PONG/red-light then booted; USB/external power removal alone did NOT help recurrence, but ~3-second Power hold after TWRP shutdown did. Need separate power-button timing/bootloader/PMIC/USB VBUS tests; avoid treating a transient host serial timeout as a bricked chip.
5. Experimental fastboot images always RAM-only, removable SD absent, original Android/TWRP and protected original Xoom untouched. Never flash as a convenience.
6. **Patches**: keep real Linux source RFCs separate from lab userspace and private firmware; no upstream submission or fabricated DCO.

**CURRENT DUT at end of checkpoint:** replacement MZ600 **running v06.3**, USB COM9 responsive, both Bluetooth and Wi-Fi driver stacks **unloaded**, no scan/connection/pairing. Last observation 19:13 EDT.

**Continuity:** [comprehensive next-session handoff](../handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md) must be appended with this newer physical PASS and corrected power recovery finding.
