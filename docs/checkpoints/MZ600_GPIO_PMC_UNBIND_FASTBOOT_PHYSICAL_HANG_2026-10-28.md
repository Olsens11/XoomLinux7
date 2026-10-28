# MZ600 GPIO-restart bypass: one-shot physical reboot-to-fastboot A/B test — 2026-10-28

**RESULT: FAIL TO ENTER FASTBOOT, NO AUTOMATIC LINUX RETURN OBSERVED.**  
**Current physical accessibility (10:44 EDT): NO FASTBOOT USB, NO LINUX COM9, NO PING; owner physical intervention may be required.**  
**No storage flash, eMMC partition write, cold p8 backup, recovery boot, or temporary Stage-D boot occurred.**

This is a new immutable outcome following [the source-level GPIO priority investigation](MZ600_FASTBOOT_REBOOT_GPIO_PRIORITY_ROOT_CAUSE_CANDIDATE_2026-10-28.md) and [live authenticated read-only dry-run](MZ600_REBOOT_GPIO_PMC_LIVE_UNPRIVILEGED_PREFLIGHT_PASS_2026-10-28.md). Do not assert that the GPIO priority change solved fastboot.

## Owner authorization and authenticated root preflight

The owner stated they had entered the password on the Surface's terminal. At 10:37–10:41 EDT, the Surface observed an actual **root@xoom-mz600** prompt on USB COM9. We re-ran a direct **root** read-only preflight through COM9, and checked:

- Identifying device-tree model: `Motorola Xoom (Stingray MZ600 minimal USB diagnostic)`; actual installed kernel `7.0.0-next-20260422+`, root `/dev/mmcblk0p8 ext4`.
- Internal eMMC 62,521,344 sectors; p8 `118784/2097152`, p9 `2215936/1048576`, p10 `3264512/59247616`; all expected classic BigPart virtual geometry.
- Live bound devices: `/sys/bus/platform/drivers/restart-gpio/gpio-restart`, `/sys/bus/platform/drivers/tegra-pmc/7000e400.pmc`, GPIO restart DT priority 200.
- Previously staged public experiment script `/dev/shm/mz600-gpio-restart-bypass-20261028.sh`, SHA256 `997081f1878c6a4a085142abc59fbe8f9ace4fd6e50a277929734adaa6a711e7`, on-device `--preflight` PASS.
- Previously compiled 664-byte freestanding ARM32 `reboot(2)` helper transferred/verified in the Xoom **RAM filesystem** at `/run/mz600-reboot-bootloader.elf`, SHA256 `451847d8acda2526c93a7b02d4694f3e80fefacce6281417ce75ee4ee6a0bf14`.
- Private Surface file `downloads/MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img`, exactly 6,645,760 bytes, SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`, verified for a **temporary `fastboot boot` fallback only**. No existing fastboot device before test.
- Host observer `inspection/MZ600-GPIO-PMC-ONE-SHOT-FASTBOOT-20261028.py` Python syntax PASS; the observer is an on-demand process, not a persistent service.

No private password or serial number was published or stored in this public checkpoint.

## Exactly what was executed (Surface local clock EDT)

Full host execution log is PRIVATE: `C:\Users\olsen\xoom-linux-rom\inspection\MZ600-GPIO-PMC-ROOT-ONE-SHOT-20261028.log`.

| Time | Verified host/device observation |
| --- | --- |
| **10:41:46** | Host starts one-shot, verifies known Stage-D image SHA256 |
| **10:41:47** | Final root prompt, p8 BigPart sectors, staged script and ARM helper hashes, both driver binding guards PASS |
| **10:41:47** | Host sends **`MZ600_FASTBOOT_WATCHER_READY=YES_XOOM_CDMA_ONLY bash /dev/shm/mz600-gpio-restart-bypass-20261028.sh --execute`** to root COM9 |
| **10:41:47** | COM9 prints `MZ600_GPIO_RESET_BYPASS_PREFLIGHT_PASS` |
| **10:41:47** | COM9 prints `MZ600_GPIO_RESET_EXPERIMENT_UNBINDING_RAM_DRIVER_ONLY` |
| **10:41:47** | COM9 prints **`MZ600_GPIO_RESET_UNBOUND_TEMPORARILY`**, confirming actual root-only GPIO restart unbind succeeded |
| **10:41:47** | Host begins bounded fastboot monitor, about 130 seconds. Script source next performs the Tegra PMC `bootloader` `reboot(2)` request, after a `sync`; detailed serial text after the unbind confirmation was **not captured** before the USB interface disappeared |
| **10:41:48**, **10:42:16**, **10:42:44**, **10:43:13**, **10:43:41** | Polls show **no fastboot device** at elapsed 0, 29, 57, 85, 114 seconds |
| **10:43:58** | Host emits `FASTBOOT_NOT_SEEN_IN_130_SECONDS_CHECK_LINUX_OR_MANUAL_RECOVERY` and `NO_FASTBOOT_ENTRY_CONFIRMED; NO_FURTHER_AUTOMATIC_DEVICE_ACTION`. Normal successful process termination; **this is a negative test** |
| **After 10:43:58** | Separate Windows PnP: **no COM9**; no Android/Motorola fastboot (unrelated Bluetooth keyboard visible). Surface network ping to prior Xoom private LAN IP: **False**; socket to SSH port 22 not connected. A hard hang or lost USB/Wi-Fi is consistent but **not physically established** |

**Do not overclaim the firmware path:** the Surface captured a successful sysfs GPIO unbind and intended request, but not a register-level trace of `PMC_SCRATCH0`, actual notifier invocation, or hardware bootloader consumption. The helper was called next in the known source flow; the exact final post-unbind UART was not retained. The root shell is no longer remotely reachable, so no live follow-up register inspection occurred.

## Result vs previous A/B baseline

**A / original 08:19 reboot request (GPIO bound):** Linux `reboot(2) bootloader` caused an ordinary restart and **COM9 returned**. Fastboot never appeared within 120 seconds.

**B / 10:41 test (GPIO temporarily unbound):** test reported `GPIO_RESET_UNBOUND_TEMPORARILY` and then no fastboot for 130 seconds; **COM9 and WLAN did not return**, at least by 10:44 EDT.

This is **not evidence that bypassing GPIO makes the bootloader request succeed**. The difference suggests the GPIO hardware reset may be important to bring the MZ600 out of Tegra PMC's soft restart. Tegra PMC restart is documented as a last-resort soft CPU reset; the Xoom uses a dedicated active-low G3 hardware reset line at priority 200. It remains unclear whether the bootloader request is lost because of reset-domain semantics, missing scratch writes, a Motorola-specific boot mode convention, or another board-specific interaction.

**Next implementation direction:** preserve the working GPIO restart mechanism for ordinary Linux reboot rather than simply reducing its priority; investigate whether bootloader mode can be encoded in a Motorola OEM-compatible persistent location or a different restart API *before* GPIO hardware reset, or whether a mode-specific Xoom/PMC reset sequence is needed. Do not write speculative PMC/CPCAP registers on the live device without a reasoned and reviewed test. No upstream patch series modifications or submission resulted from this negative test.

## Immediate safety, recovery and next gates

1. **STOP remote reboot attempts** while tablet is not enumerating as Linux COM9 or fastboot and not answering network. There is no command path to the tablet.
2. Owner or someone with physical access should use the previously successful hardware power/volume reset sequence to revive the **experimental replacement MZ600**. Observe red LED and exact boot screen. Do not operate on the protected original Xoom.
3. Once Linux restarts, confirm the normal GPIO driver **rebinds from unchanged on-disk DT**: `/sys/bus/platform/drivers/restart-gpio/gpio-restart`. The script's unbind was RAM-only, not persistent, so a successful cold/normal boot should naturally restore it.
4. Check `/dev/mmcblk0p8`, p7, BigPart geometry and Debian root integrity **read-only** before any more reboot. Exact Stage-D boot image, recovery and test image hashes are still privately preserved; do not assume a reset necessarily damaged storage.
5. Keep known **non-BigPart TWRP 3.1.1-0 p6 OFF** while p8's filesystem is valuable; current rescue microSD holds an **armed but not executed** one-shot cold-p8 backup systemd service. **No new Linux image or recovery has been installed; cold p8 backup is still OPEN.**
6. Continue offline OEM Tegra/CPCAP/bootloader reboot-mode analysis, carefully distinguishing a firmware mode flag from hardware reset implementation. Only consider the next software attempt after designing a checked escape path and ensuring physical recovery access.
7. Preserve this checkpoint and the broader [chapter-boundary handoff](../handoffs/MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md) for seamless continuation.

**Result classification: physical GPIO-unbind PASS; fastboot FAIL; self-recovery-to-Linux not observed; overall no-button restart fix NOT QUALIFIED.**
