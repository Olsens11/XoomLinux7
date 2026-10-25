# MZ600 v06.3 first physical RAM-boot attempt — no PONG, red light recurred

**Date:** Sunday 2026-10-25, ~18:50–18:54 EDT. **Status:** ONE unsuccessful physical v06.3 boot attempt, cause **undetermined**. Do **not** classify the image itself intrinsically unbootable, nor the private BCM4329B1 HCD as rejected.

## Device and immutable image identity

- Replacement Motorola Xoom **MZ600 Stingray**, protected original Xoom not used. The 32GB removable microSD was removed for clean tests. Internal Android/TWRP/eMMC partitions were not flashed, partitioned, formatted, or overwritten.
- v06.2 baseline image SHA256 `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8` was **physically running** USB PID1, with Wi-Fi and Bluetooth drivers unloaded and BCM4329 still detected on onboard SDIO. Read-only COM9 PING, WIFI_STATUS, BT_STATUS, MMC2_STATUS **all passed** just before test.
- New **v06.3 private HCD RAM-only candidate** image `MZ600-CLEAN-WIFI-BT-USB-v063-HCD-RAM-ONLY-UNTESTED.img`, **6,561,792 bytes**, SHA256 `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e` verified on Surface and Desktop. It differs from v06.2 in one additional **built-in initramfs file**: `/lib/firmware/brcm/BCM4329B1.hcd`. It uses the same driver modules, diagnostic program and board DT. Vendor binary stays PRIVATE (17,332B, SHA256 `7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`), never published in repo.
- Source/manifest from `artifacts-embedded-v063/MANIFEST.json`; exact Surface guarded launcher `captures/Xoom-V063-HCD-USB-Once.ps1`; PRIVATE log `captures/MZ600-V063-hcd-firstboot-PRIVATE.log`.

## Exact observed chronology

1. At **18:50:04 EDT** Surface confirmed PONG from live v06.2. The gated USB `REBOOT` command returned `REBOOT ARMED`, and `CONFIRM REBOOT` was sent. USB dropped as expected.
2. At **18:50:45 EDT** Surface independently verified **stock Android Stingray fully booted**; the ADB hardware/device properties matched and `sys.boot_completed=1`. The prior v06.2 shutdown-to-stock-Android path succeeded.
3. At **18:51:14 EDT** guarded v06.3 launcher SHA/size preflight passed and verified stock Android identity. At **18:51:25 EDT**, target bootloader product **xoom-cdma** and unlocked state were verified, then the script invoked **`fastboot boot <verified v063 image>` ONLY**.
4. At **18:51:28 EDT**, fastboot reported `Sending boot.img ... OKAY`, `Booting ... OKAY` and completed. **This only means the bootloader accepted a RAM boot image; it does not prove kernel/PID1 execution.**
5. At **18:51:34.439 EDT** COM9 **briefly appeared in Windows enumeration** (~6s later). First serial Write failed at 18:51:34.624 with *"A device attached to the system is not functioning"*; then opening COM9 repeatedly failed with *"The port 'COM9' does not exist."*
6. Bounded ~75s test ended **18:52:43 EDT** reporting `FINAL_COM9_PRESENT=True_USB_PONG=False_COM9_ARRIVED=True_COM9_DROPPED=False_ERRORS=261`. The last `COM9_PRESENT=True` reflects enumeration; **it contradicts usable COM-port opening**. Independent Surface Windows PnP query showed `USB Serial Device (COM9)` as **Unknown**, while ADB and fastboot devices were empty. There was no functional serial session.
7. At **~18:53 EDT** user directly reported: **"ok- we have the red light again."** This is the camera-side red-light symptom seen previously after the unsuccessful first v06.2 boot. User has **not yet reported** whether normal Power works after removing cables, whether the display shows any kernel text, whether external power cable was attached, or exact LED cadence in this particular incident.

**No `BT_START`, `BT_ON`, `WIFI_START`, RF discovery, scan, HCD patch delivery to chip, module loading on demand, USB software reset, reboot after failed image, or eMMC write was executed.** The diagnostic code would load the HCD only during **explicit Bluetooth startup**, which was NOT reached. Thus the current evidence **does NOT indicate that the BCM4329B1 HCD was applied or incompatible**. An image-dependent early-boot memory/layout regression remains a competing possibility because adding the HCD changes built-in compressed kernel payload size even if firmware is never requested.

## Hypotheses explicitly still open

- **Starting hardware/USB/charger/PMIC state:** Previous black/red-light phenomenon cleared after user **unplugged BOTH USB and external power BEFORE ordinary Power-only startup**, but neither separate cable nor a specific regulator was proven causal. This recurrence followed a USB-connected flashless RAM boot. External-power connection during attempt not separately documented.
- **Early kernel/power/USB-gadget failure vs PID1 hang:** COM9 briefly enumerating without PONG does not identify where boot stopped. Kernel LCD text/photo, crash state, real UART/earlycon, or persistent records would differentiate.
- **New image-content/layout effect:** v06.3 adds exactly one embedded HCD archive file, but the changed CPIO recompresses the kernel, so v06.3 image-specific early behavior is not excluded by offline checksum/header pass. Compare after matching power states, not immediately after a different preceding boot.
- **BCM4329 shared-chip reset ownership:** May be incomplete, but **the firmware module loading was not requested** in this attempt; do not assert Bluetooth UART/HCD causes crash.
- **Windows serial PnP enumeration/USB VBUS:** COM9 appeared as an Unknown stale/unusable PnP device; Windows enumerated device may linger after device crashed/disconnected, which explains `FINAL_COM9_PRESENT=True` despite unusable COM9. Investigate actual device USB connect/disconnect events separately.

## Safe next action and A/B protocol

1. **Stop all remote DUT commands now.** Do not automatically fastboot boot again, enable Bluetooth, or flash/erase anything. Preserve PRIVATE Surface logs and physical red-light state.
2. Ask user to photograph any visible **kernel/LCD panic** before pressing reset if one appears. Then repeat previously successful non-invasive recovery: **unplug USB AND external charger/power cable, try ordinary Power alone**, record result and connector state. If it does not start, prefer the OEM documented **Power + Volume Up forced reset** (do not equate to full electrical power removal). Avoid invasive battery disconnection.
3. When safely back into Android/TWRP, collect read-only available crash evidence where possible; earlier recovery had no accessible pstore or `/proc/last_kmsg`. Avoid interpreting that as proof no panic.
4. To attribute root cause, control identical starting power states and compare exact v06.2 vs v06.3 images using independent fastboot RAM boots, ideally with earliest framebuffer/USB logs and a carefully gated one-variable test. v06.2 has physically booted after an earlier failed attempt; do not condemn v06.3 from one occurrence.
5. Do not attempt Bluetooth patched-firmware/keyboard pairing until PID1/USB is again stable. The project's larger next goal remains standard `iw` Wi-Fi scanning and a real on-screen terminal with a Bluetooth keyboard, while preserving upstream source patch provenance.

**Acceptance:** v06.3 offline image verification PASS; **first v06.3 physical boot attempt NO PONG and red LED observed**; intrinsic image bootability **UNDETERMINED**; HCD firmware patch loading **NOT TESTED**. Prior physically validated v06.2 remains the known-good baseline under its previously tested hardware conditions.
