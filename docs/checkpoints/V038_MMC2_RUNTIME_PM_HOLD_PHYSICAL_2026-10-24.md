# v038 physical — keep Tegra SDMMC2 runtime active across BCM4329 firmware/F2 handshake (2026-10-24)

**Result: TEST PASS, WI-FI STILL FAIL (-62).** The suggested runtime-suspend hypothesis was given a reversible, measurable trial on the replacement Xoom. A balanced Linux runtime-PM reference successfully held the real SDMMC2 host's platform device active across firmware download, CM3 release, SDPCM mailbox write and the entire ~3-second Function 2 enable wait. **F2 readiness did not change.** This narrows but does not universally exclude controller signal integrity, physical clock waveform issues, POR/power or chip firmware execution.

## Correct host and source

- The MZ600 BCM4329 is on **Tegra20 SDMMC2**, Linux platform **`c8000200.mmc`**, Linux host **`mmc2`** in the current runtime. The pasted suggestion's `sdhci-tegra.3` and `sdhci@78000600` / SDMMC4 do not identify the Xoom's WLAN controller.
- Actual [board diagnostic DTS](../src/board/tegra20-motorola-stingray-usbdiag.dts) declares `sdmmc2: mmc@c8000200` with `mmc-pwrseq = <&brcm_wifi_pwrseq>`, `vmmc-supply=<&reg_wifi_vdd>`, `vqmmc-supply=<&vwlan1>`, `keep-power-in-suspend`, `bus-width=4`, and `non-removable`. SDMMC4 `mmc@c8000600` is **eMMC**, not Wi-Fi. Do not wire arbitrary TPS6586x LDOs or WLAN enable GPIO to SDMMC4.
- Pinned Linux 7 `drivers/mmc/host/sdhci-tegra.c` does enable the host device's runtime PM; the question was therefore testable, not imaginary.
- In `sdio_enable_func()` the MMC core writes CCCR IOEx and **polls CCCR IORx**, with a 3-second timeout observed on this build. `cap-sdio-irq` does not substitute for ready-bit assertion; it governs later IRQ behavior.

## Source-only build and safe changes

- [`scripts/experiments/v038-build-mmc2-runtime-awake.py`](../../scripts/experiments/v038-build-mmc2-runtime-awake.py) extends verified v037 instrumentation.
- Original pinned upstream `sdio.c` and `chip.c` guarded by exact SHA256, changed **only temporarily** for module compilation, then restored byte-for-byte under `finally`.
- Actual driver callback computes the MMC host platform parent from `sdiod->func1->card->host->parent`; `pm_runtime_resume_and_get()` before firmware download; holds the balanced reference through the existing F2 handshake; `pm_runtime_put_sync()` on **both** success and failure, before releasing the SDIO drivers. This is **not** a permanent `echo on`, and does not modify clocks/rails/regulators/power GPIOs or reset sequencing.
- Compiled ARMv7 `brcmfmac-v038-pmu-cm3-readonly.ko` (named according to inherited builder convention though it also temporarily changes host runtime-PM policy), **463432 bytes**, SHA256 **`e6047f7cf01bfc50e7893b1a7a40185f0beca14db44ec0db779136e82ac3d9f9`**; correct `7.0.0-next-20260422` module ABI. Independently SHA256-verified on Surface.
- USB COM9 accepted RAM-only upload **`UPLOAD DONE SIZE 463432 CRC32 0x01F129FE`**; `WIFI_START BRCMUTIL rc=0, BRCMFMAC rc=0`. No image flashing/reboot, firmare/NVRAM changes, Bluetooth activation, WLAN RF scan, association, or identity substitution.

## Actual v038 runtime events

The sanitized Surface file `C:\Users\olsen\xoom-linux-rom\downloads\v038-hostawake-sanitized.log` captured:

```text
XOOM_V038_HOSTPM phase=ACQUIRE rpm_rc=0 enabled=1 active=1 held=1
XOOM_V038_RES phase=T2_BEFORE_CM3_RELEASE ccrev=29 pmurev=6 stat=000000ae/0 res=003fe63e/0 pend=00000000/0
XOOM_V038_RES phase=T3_AFTER_CM3_RELEASE ccrev=29 pmurev=6 stat=000000ae/0 res=003fe63e/0 pend=00000000/0
XOOM_V038_MAILBOX write_rc=0 sdpcm_protocol=4
XOOM_V038_RES phase=T4_PRE_F2_REQUEST ccrev=29 pmurev=6 stat=000000be/0 res=003fe63e/0 pend=00000000/0
XOOM_V038_RES phase=T5_POST_F2_RESULT ccrev=29 pmurev=6 stat=000000be/0 res=003fe63e/0 pend=00000000/0
brcmf_sdio_firmware_callback enable F2: err=-62
XOOM_V038_HOSTPM phase=FAIL_RELEASE error=-62 active=1 held=1
```

Here `held=1` in the *post-release logging* is the local condition used to balance the reference; it is **not** a reading that proves the reference remains held after `pm_runtime_put_sync()`. `active=1` does not establish a permanent always-on policy. `pm_runtime_resume_and_get` returned 0 with PM enabled and active throughout the callback, ref held over the F2 interval.

**Conclusion:** preventing ordinary runtime PM suspension of SDMMC2 *during this firmware/F2 window* is **not sufficient**. We have already physically tested lower host frequency, longer power-on delays, and Motorola MMC capability overrides without success. Real oscilloscope-level signal integrity and true cold POR remain untested.

## Other pasted fixes assessed, not applied

1. **Device tree:** Actual SDMMC2 already has proper board-specific supply phandles and `keep-power-in-suspend`. The sample SDMMC4 node with guessed TPS6586x LDO rails would affect the wrong controller/eMMC. No DTS rewiring performed.
2. **`cap-sdio-irq`:** not an IORx-ready polling cure. The driver never reaches the post-F2 IRQ setup stage.
3. **NVRAM `keep_img=1`, `sd_drivestrength=1`, `clkreq=0`:** searched original Motorola 2.6.36 BCM4329 and pinned modern `brcmfmac` host driver for the terms; no parsing or confirmed support for these as firmware NVRAM parameters found. A local C variable named `clkreq` exists, **not** proof the suggested NVRAM `clkreq` field has matching effect. The opaque firmware could have unverified config handling; do not conflate absence from host C with definite absence inside firmware. Not injected.
4. **MAC substitution:** the v026 generic NVRAM omits explicit MAC; Motorola's original calibration has a different per-device reference. Never inject a fabricated or another device's MAC address to bypass F2. Correct identity provenance required for later radio activity.
5. **Logs:** existing v034 BOOTLOG is a bounded, recent 110-match subset affected by earlier periodic MMC status output; live LOGS captures recent ring bytes. Neither is a complete early-boot historical dmesg. The v038 sanitized trace showed no `Internal clock never stabilized` or `Controller timeout` line, but those phrases cannot be ruled out across all historical boot activity from this bounded log alone.

## Final physical safety state

After test, `WIFI_STOP brcmfmac_rc=0 brcmutil_rc=0`. Follow-up `MMC2_STATUS` returned USB verified COM9, target valid, MMC2 bound, BCM4329 card present, driver modules **UNLOADED**, and profile AUTO 0. The temporary-boot v034 kernel remains running unchanged. No changes to the protected original Xoom.

## Next useful discriminating test

Do not blindly copy the LibreELEC CuBox/Wandboard NVRAM: it differs from Motorola in reference crystal, antenna, board ID, regulatory and radio power calibration. Prefer a **RAM-only, one-variable trial** of the authentic early MZ600 firmware (`fw_bcm4329.bin` 261317 bytes, 4.218.248.20, Jan 2011), with the **same existing Xoom-matched generic-minus-identity NVRAM** and one fixed v037 diagnostic driver. Keep the existing generic firmware bytes and hashes for immediate rollback and do not associate/scan. This tests a historically grounded firmware difference, not guessed NVRAM fields.
