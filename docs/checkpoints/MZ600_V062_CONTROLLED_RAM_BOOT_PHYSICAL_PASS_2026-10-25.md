# MZ600 v06.2 controlled repeat boot — physical USB/PID1 PASS, October 25 2026

**Hardware:** replacement Motorola Xoom MZ600, Tegra 2 Stingray, removable microSD absent, original Android boot/system/TWRP preserved. **Classification:** v06.2 is **physically boot-capable and diagnostic-USB stable**. Its corrected Wi-Fi module unload routine and hardware radio lifecycle are **not yet physically tested**.

## Critical physical starting-state evidence

Earlier on 2026-10-25, an identical v06.2 image was accepted by `fastboot boot`, but the host observed **no COM9 for 75 seconds**, followed by black screen and red camera-side LED on normal Power press. The user subsequently reproduced an inability to start normally even after shutting down from both TWRP and stock Android. The user then **unplugged BOTH USB and the external power cable and successfully started the tablet using Power ALONE without Volume Up**. This was explicitly confirmed. Whether unplugging USB, unplugging charger, their combination, passage of time, or a separate power-state change caused restoration is **unknown**. The USB cable was necessarily reconnected for the host-controlled v06.2 retest; exact charger connection state during the new retest was not independently measured.

This means the unsuccessful earlier attempt cannot be attributed to an intrinsically bad v06.2 image. It also does not prove a BCM4329/PMIC latch or the source of the red LED.

## Exact controlled v06.2 physical boot

- Identical immutable image `MZ600-CLEAN-WIFI-BT-USB-v062-WCC-UNLOAD-RAM-ONLY-UNTESTED.img`.
- **SHA256 `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`**, **6,549,504 bytes**, checksum/size verified independently on Surface before launch.
- Target Surface ADB serial was the expected authorized MZ600; `ro.hardware=stingray`, `ro.product.device=stingray`, `sys.boot_completed=1`, TWRP absent: fully booted **original stock Android**. `/proc/partitions` listed only internal `mmcblk0` eMMC and its p1–p10, no removable microSD block device.
- Guarded Surface script `C:\Users\olsen\xoom-linux-rom\captures\Xoom-V062-WCC-USB-Once.ps1` first checked image identity, then Android → fastboot, confirmed unlocked `xoom-cdma`, and invoked **`fastboot boot` ONLY**, never flash/write partitions.
- **17:28:27.985 EDT:** `fastboot boot` accepted, boot transfer/launch OKAY.
- **17:28:33.693:** Linux gadget CDC ACM **COM9 enumerated**.
- **17:28:35.776:** Linux diagnostic PID1 replied to **USB `PING` with `PONG XOOM-LINUX`**.
- **17:28:36.660:** `BT_STATUS` query (read-only, no radio activation) returned 223 chars.
- **17:29:43.234:** bounded 75-second observation completed `FINAL_COM9_PRESENT=True_USB_PONG=True_COM9_ARRIVED=True_COM9_DROPPED=False_ERRORS=0`. No automatic restarts, no firmware loading, no RF scans or pairing.
- **After the observation** a second independent host COM9 session passed `PING` again and queried read-only `STATUS`, `WIFI_STATUS`, `BT_STATUS`, and `MMC2_STATUS`. Results: Linux `7.0.0-next-20260422+`, `MMC PRESENT`; **`CARD BCM4329 VERIFIED`, `DRIVER MODULES UNLOADED`, `WLAN0 ABSENT`, `BLUETOOTH HCI_UART MODULE NOT LOADED`, `HCI0 ABSENT`, `BT_STARTED_FLAG 0`**. COM9 remained present.

## Precise interpretation and patch acceptance status

1. **v06.2 now has a physical boot/PID1/USB PASS.** The exact same SHA-pinned image produced no COM9 in one earlier attempt and stable COM9/PID1 in this controlled retest. Therefore the claim `v06.2 intrinsically cannot boot` is **refuted**. An intermittent failure or one depending on prior hardware conditions remains unexplained.
2. **v06.2's Wi-Fi teardown fix is still UNTESTED ON HARDWARE.** `wifi_stop()` was modified to unload `brcmfmac_wcc` → `brcmfmac` → `brcmutil` on explicit `WIFI_STOP`, but neither `WIFI_START` nor `WIFI_STOP` was sent in this clean reboot. Do not claim that the new ordered removal resolves the prior `-11` module-unload failure without a dedicated test.
3. **v06.1 remains the tested BCM4329 Wi-Fi firmware/`wlan0` baseline.** v06.2 contains byte-identical DTB, firmware and modules; only embedded `/init` differs. No Bluetooth HCI0 functionality is claimed yet.
4. **Neither USB nor external charger individually proved causal**: both were unplugged before the normal Power-only recovery. Restored startup may reflect USB VBUS/OTG, charger input, combined electrical state, elapsed time, reset sequence or another factor. The BCM4329 shared-power idea remains a hypothesis.
5. **No new upstream Linux source patch from this observation.** The WCC unload correction is a separately tracked **laboratory userspace patch** (`patches/lab/0001-v062-broadcom-wcc-unload-order.patch`); RFC WLAN MAC ATAG patch remains unsigned and unsubmitted.

Private, full per-session host log: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V062-wcc-firstboot-PRIVATE.log` (contains BOTH failed 14:25 and successful 17:28 attempts); read-only post-observation capture: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V062-CLEANBOOT-POSTOBS-PRIVATE-20261025.log`. Do **not** publish raw logs or per-device MAC identifiers.

## Next discriminating steps (separate experiment, do not conflate)

- Keep the current v06.2 no-radio stable baseline documented.
- In a **separately authorized/tested phase**, verify `WIFI_START` still boots firmware and creates `wlan0`, then send **one** `WIFI_STOP` and check whether `brcmfmac_wcc`, `brcmfmac`, and `brcmutil` all unload in reverse dependency order without `-11`; capture kernel messages, USB health, and any PMIC/SDIO behavioral changes. No network scan/association required.
- Later, in a controlled connector-state matrix, test normal Android Power-only startup with **no cables, USB only, power only**, then both attached if the device remains healthy, changing only one factor per trial. Do not blind boot-loop or assume software shutdown proves all battery/PMIC rails are unpowered.
- Only after hardware power-state evidence supports it should a *new independent* kernel pwrseq/CPCAP/OTG patch candidate be developed, tracked separately from the upstream WLAN MAC bridge.
