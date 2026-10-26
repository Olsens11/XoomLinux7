# Original Motorola MZ600 2a65edc Bluetooth/WLAN shared-power implementation: 51/51 static gates PASS

**October 26, 2026. Offline OEM source and binary forensics only; Xoom tablet unchanged.** Recovered *exact same-generation* Motorola **board-stingray-bluetooth.c** at Tegra commit **2a65edc**, closing the last known source-version gap in shared-U4 Bluetooth callback analysis. The recovered original source is 7,967 bytes, SHA256 **e2cf7582371d5a9a59ac6c237a8d7a6436410025009f57cce15dfecdc93f9fef**. Original authority: https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray-bluetooth.c . Copy is in user's private Pi OEM analysis/source-2a65edc tree; no proprietary Wi-Fi firmware or per-device identity published.

## Source versions and qualified ownership

The **early** matching-generation arch/arm/mach-tegra/Makefile lists board-stingray-bluetooth.o under CONFIG_MACH_STINGRAY (line 70), as well as board-stingray-wifi.o (line 65). board-stingray.c includes a bcm4329_bluetooth platform device in platform_add_devices(stingray_devices,...) called BEFORE stingray_sdhci_init() and stingray_wlan_init(). This establishes source **platform registration order**, not Bluetooth driver probe/bind time.

The private HRI39 bcm4329.ko 264038-byte ELF SHA 4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f independently verifies the *Wi-Fi* platform-control symbols. It is NOT a shipping Bluetooth ELF verification. Matching 2a65edc BT code is source-confirmed; exact boot-zImage inclusion, BT driver bind timing, actual U4 pin transitions, and internal regulator POR still need independent evidence. Previous July 2011 Motorola code was a **related later revision**; stop using it as the sole early source for these functions.

## Exact original Motorola Bluetooth actions

Source file board-stingray-bluetooth.c:
- BT_SHUTDOWN_GPIO = Tegra I7; BT_RESET_GPIO = U0; BT_WAKE_GPIO = U1; BT_HOST_WAKE_GPIO = U6.
- On rfkill UNBLOCK, bcm4329_bt_rfkill_set_power calls change_power_brcm_4329(true) (shared U4 vote), then drives U0 reset HIGH and I7 shutdown LOW.
- On rfkill BLOCK, that callback calls change_power_brcm_4329(false) (shared U4 vote release), then I7 shutdown LOW and U0 reset LOW.
- On first Bluetooth probe it requests U0 and I7 and **calls bcm4329_bt_rfkill_set_power(NULL,true) BEFORE rfkill_alloc and rfkill_register**. This initial blocked call decrements the shared untyped U4 vote counter if its value is positive.
- BT low-power code requests U1 output LOW and U6 input, registers host-wake IRQ and a low-power wake timer, and manages wake locks. This is a distinct sleep/wake pathway beyond Wi-Fi SDIO initialization.
- Bluetooth remove calls rfkill_unregister and frees U0/I7/U1/U6, but there is **no explicit direct change_power_brcm_4329(false)** inside the remove function. This is only a source-level observation; it is unknown whether rfkill unregister invokes the state callback indirectly.

**Source-grounded potential interleaving defect:** The original board-stingray.c shared-U4 counter has no separate Wi-Fi and Bluetooth owners. If Wi-Fi already holds the only U4 vote (count 1) and the BT driver probes later, BT initial blocked callback can decrement that count to zero and lower U4 while WLAN still needs power. This is a **possible ordering hazard, not a demonstrated actual OEM malfunction**. Registering the BT platform device before WLAN device does NOT prove the BT driver was bound or probed first. Our Linux 7 combined-chip design must use typed resource votes: releasing an unacquired Bluetooth vote must never consume Wi-Fi's vote.

## Reproducible evidence upgrade

The [OEM version-locked static source+ELF audit](../../tools/forensics/audit_mz600_oem_system_lifecycle.py) now SHA-checks **eight exact source files**, including the recovered Bluetooth source, plus the authentic original Wi-Fi ELF. New checks verify four BT GPIO assignments, blocking/unblocking U4 and reset order, initial blocked probe, wake IRQ/low-power timer, source BT-remove no-direct-vote observation and board platform registration order.

**Physical command execution on Pi: 51/51 PASS; 0 FAIL**. Sanitized private-local JSON /tmp/mz600-oem-crosslayer-bt-original-checks-20261026.json SHA256 **2fb0d84f9d0bfc52baa9bec9d06cd9c37768a83f4f17d011bb26facea7a6c23f**. Neither the script nor its summary reads firmware/calibration, starts a radio or modifies a tablet.

The earlier [42/42 checkpoint](MZ600_OEM_2A65EDC_CROSSLAYER_SOURCE_BINARY_CONDITIONAL_AUDIT_42_PASS_2026-10-26.md) is a valid intermediate step, superseded in coverage by the new **51/51** audit.

## BCM4329 Linux 7 patch-series impact

- Treat exact early OEM Bluetooth rfkill and wake code as **matching-generation source-verified**; do not claim real hardware probe/voltage/boot success from a static check.
- Keep per-consumer power votes typed and explicitly verified. Only the shared-chip owner should manage U4 and LPO; migrate U2/U0/I7 GPIO ownership without collisions.
- Prioritize regression tests for both initialization orders (WLAN first / Bluetooth first), blocked/unblocked, failure/unwind, suspend/wake, module removal and warm/cold chip state.
- Keep separate ongoing firmware/5GHz diagnosis: current running Linux 7 generic firmware returned one 2.4GHz band and eleven 2.4GHz chanspecs, zero 5GHz. Historic Android same-hardware 5GHz association is evidence of hardware capability, but shared U4 issue is **not proven to explain absent 5GHz band**.
- Multi-device MZ600/MZ602/MZ604 testing, exact per-device firmware/calibration and owner approval are required before community upstream review.

**No firmware swap, kernel patch deployment, reboot, RF scan, regulator write or p7 change performed.**
