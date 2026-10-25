# MZ600 Linux 7 v06.2 — native BCM4329 Wi-Fi start and WCC ordered shutdown — PHYSICAL PASS

**Test date:** 2026-10-25, 17:40–17:41 EDT. **Branch:** `wip/clean-wifi-bt-usb-20261025`. **Test type:** live, reversible radio-driver lifecycle over an established USB gadget, no external microSD, no radio scans or associations. **No flash, no reboot, no eMMC/Android/recovery partition changes.**

## What was being validated

Original v06.1 Linux physically booted and initialized BCM4329 Wi-Fi, but `WIFI_STOP` tried to remove `brcmfmac`/`brcmutil` without first releasing their `brcmfmac_wcc` dependency, producing `rc -11` while modules remained loaded. v06.2 introduced precisely one laboratory userspace `wifi_stop()` change: **unload `brcmfmac_wcc` → `brcmfmac` → `brcmutil`**, aborting/reporting unexpected errors.

This is an experiment with an **embedded diagnostic `/init` userspace program**, **not an upstream kernel C-code patch**. Exact reproducible laboratory patch: [`patches/lab/0001-v062-broadcom-wcc-unload-order.patch`](../../patches/lab/0001-v062-broadcom-wcc-unload-order.patch), build [`scripts/experiments/build-clean-wifi-bt-v062-wcc-unload-20261025.py`](../../scripts/experiments/build-clean-wifi-bt-v062-wcc-unload-20261025.py). Other 25 files in embedded initramfs, including BCM4329 firmware and modules, were independently verified byte-identical to working v06.1.

## Exact candidate identity and earlier boot status

- **Image:** `MZ600-CLEAN-WIFI-BT-USB-v062-WCC-UNLOAD-RAM-ONLY-UNTESTED.img`
- **SHA256:** `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`
- **Bytes:** 6,549,504
- **Upstream pinned Linux commit:** `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, release `7.0.0-next-20260422+`.
- This identical image previously completed a **controlled no-SD, no-radio physical `fastboot boot` and 75-second USB/PID1 PASS** at 17:28 EDT, following recovery of the abnormal normal-Power condition by unplugging **both USB and external power** before Power-only startup. This precedent is documented in [v06.2 physical boot checkpoint](MZ600_V062_CONTROLLED_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md). It did not yet verify the teardown routine.

## Preflight verified live before radio changes

Surface USB `COM9` was present and answering `PING` with `PONG XOOM-LINUX V20`. `MMC2_STATUS` showed **TARGET VALID**, **BOUND YES**, **CARD BCM4329 VERIFIED**, **DRIVER MODULES UNLOADED**. `WIFI_STATUS` showed empty `/proc/modules` and **WLAN0 ABSENT**. `BT_STATUS` showed **HCI0 ABSENT**, **BT_STARTED_FLAG 0**, HCI_UART not loaded. Surface rechecked local v06.2 SHA256. Test runner PowerShell parser PASS.

Test host script: `C:\Users\olsen\xoom-linux-rom\captures\Xoom-V062-WIFI-Start-Stop-Once.ps1` (PRIVATE original run transcript at `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V062-WIFI-START-STOP-20261025-PRIVATE.txt`). Test ran bounded single-shot USB `WIFI_START`, read-only status, one `WIFI_STOP`, status, PING, LOGS. No `WIFI_RETRY`, BT_START, scan, DHCP, network association, regulatory override, MMC2 rebind, platform restart or partition access.

## Physical results — exact observations

| Time EDT | Step | Evidence |
| --- | --- | --- |
| 17:40:24 | Guarded test began | v06.2 local SHA256 matched |
| 17:40:27–36 | Baseline preflight | `PING`, MMC2, unloaded Wi-Fi/Bluetooth PASS |
| 17:40:45 | One `WIFI_START` | `BRCMUTIL rc 0`; `BRCMFMAC rc 0 debug 6`; `WIFI PROBE STARTED (NO ASSOCIATION)` |
| 17:40:49 | `WIFI_STATUS` | `WLAN0 PRESENT`, `brcmfmac_wcc`, `brcmfmac` and `brcmutil` loaded |
| 17:40:54 | One `WIFI_STOP` | `WCC_STOP rc 0`; `WIFI_STOP brcmfmac_rc 0`; `WIFI_STOP brcmutil_rc 0`; `WIFI_STOP ORDERED UNLOAD COMPLETE` |
| 17:40:58 | `WIFI_STATUS` poststop | **ALL THREE MODULES ABSENT, WLAN0 ABSENT** |
| 17:41:01 | Poststop `PING` | PONG true |
| 17:41:04–05 | Read-only `LOGS` and wrap-up | COM9 present, no reboot, test PASS |

Log evidence from kernel:
- `brcmf_fw_alloc_request: using brcm/brcmfmac4329-sdio for chip BCM4329/3`
- `brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: Sep 2 2011 14:48:19 version 4.220.48`
- `usbcore: registered new interface driver brcmfmac`
- After explicit stop: `usbcore: deregistering interface driver brcmfmac`.
- The missing optional `clm_blob` and `txcap_blob` generated `err=-2` warnings. These did not prevent this initialization, but **are not evidence that Wi-Fi RF regulatory capabilities are qualified**.

Note: `BRCMFMAC rc 0 debug 6` prints the retained display/debug-value field in the diagnostic code. The v06 packager intentionally did **not** pass a nonexistent `debug=` module parameter to this kernel, which has `CONFIG_BRCMDBG` disabled. Do not construe the `debug 6` text as proof the module accepted that argument.

A **second independent USB connection after the test** again returned `PONG=True`, `WLAN0_ABSENT=True`, `MODULE_LIST_EMPTY=True`, `BLUETOOTH_UNLOADED=True`, `BCM4329_STILL_DETECTED=True`, `FINAL_COM9=True`. Xoom was deliberately **left running v06.2 with radios unloaded**.

## Acceptance and remaining unanswered questions

**PHYSICAL PASS:** BCM4329 standard upstream driver and Motorola firmware initialize in the clean kernel; `wlan0` is created; the separate WCC driver is loaded and then correctly unloaded **before** `brcmfmac` and `brcmutil`, with every `delete_module` return code 0; `wlan0` disappears; USB PID1 continues running.

**NOT YET ESTABLISHED:** that unloading the kernel modules powers off BCM4329's shared rail, asserts correct WLAN/BT reset pins, releases all PMIC votes and clocks, restores safe boot state after software power-off, supports RF scanning/association, verifies regulatory operation, or gives Bluetooth HCI functionality. No full shutdown/reboot test was performed immediately after this module cycle, intentionally avoiding recurrence of the earlier red-light/power-on anomaly.

**Patch tracking:** Mark `patches/lab/0001-v062-broadcom-wcc-unload-order.patch` as **physically tested PASS**, while maintaining the upstream `patches/upstream/rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch` as a separate signed-off-by-pending RFC. No actual kernel upstream patch introduced for this userspace change. Consider later board-power/USB VBUS/pwrseq patches only after isolated hardware experiments.

**Preservation:** Full raw output stays privately on Surface; public checkpoint contains no device-specific factory MAC, credentials, firmware bytes, or private authentication data.
