# V021 — OEM firmware A/B and clock/reset hypothesis, 2026-10-24

**Result:** Firmware A/B was physically performed via v020 RAM-only USB without reboot. Neither firmware fixed BCM4329 Function 2 `-62`. Calibrations match except for OEM MAC. The subsequent LPO clock observer compiled and was staged on Surface, but **was not physically loaded/tested** because its RAM-upload attempt was blocked by an access/safety check. Native Wi-Fi remains absent.

## Controls and provenance

- Reused current v020 temporary-boot kernel and `MMC2_PROFILE` / `MMC2_REINIT`; only replacement Motorola MZ600. No flash or persistent tablet changes.
- Baseline firmware: 253,748 bytes, SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`.
- OEM-era reference firmware: 264,140 bytes, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`.
- Generic NVRAM: 672 bytes effective binary. A private original `bcm4329.cal` (1594 bytes) was located under the Pi's original-Android archival reference; **all 53 shared key/value settings match** the local no-MAC generic NVRAM. Only original OEM calibration contains `macaddr`. It was not uploaded, disclosed or copied from Pi. `xtalfreq=38400` in both.
- Baseline/Firmware/Profile shared comparison performed with same generic NVRAM, using v017 read-only SDIO instrumentation in the loaded module. Each probe used a fresh `MMC2_REINIT` and both modules unloaded after each test. `brcmfmac` reports load rc=0, but that alone is not Wi-Fi success.

| Trial | Firmware | MMC2 profile | Clock / timing | IOEx before→after | IORx before→after | F2 | Firmware RAM length | Shared addr |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| A | Standard | AUTO | 46153846 Hz / 0 legacy | 02→06 | 02→02 | -62 | 253748 | 0x0002B134 |
| B | Motorola-era | AUTO | 46153846 Hz / 0 legacy | 02→06 | 02→02 | -62 | 264140 | 0x00030860 |
| C | Motorola-era | MOTOROLA | 46153846 Hz / 2 HS | 02→06 | 02→02 | -62 | 264140 | 0x00030860 |

For all: chip clock CSR `d2` before/after, direct SDIO error counts 0, firmware and 672-byte NVRAM transfer/readback completed, no wlan0 demonstrated, no association/scanning. OEM-era firmware RAM upload returned `UPLOAD DONE SIZE 264140 CRC32 0xCFE64001`, matching host CRC. Note this does **not** prove firmware CPU ran successfully.

After C, modules were unloaded, `MMC2_PROFILE AUTO` + `MMC2_REINIT` returned PASS; standard firmware restored in RAM with host/device CRC `0xB4092AA6` for 253748 bytes. A subsequent tool safety block prevented an additional status tool invocation in the same orchestration; do not overclaim an observed final STATUS for that sequence.

## Highest-ranked OEM discrepancy

Motorola downstream `board-stingray-wifi.c`:
- `STINGRAY_WLAN_PWR=TEGRA_GPIO_PU4`, `STINGRAY_WLAN_RST=TEGRA_GPIO_PU2`, host-wake `PU5`.
- `mdelay(100)`, turn power on, `mdelay(100)`, release reset, `mdelay(200)`.
- Historical OEM SDIO card capability override is already thoroughly tested by v018/v020: effective profile takes effect, F2 still fails. Source: https://android.googlesource.com/kernel/tegra/+/13b7fba9ceae2289d828208d6fbb19d7caddefdd%5E%5E%5E2..13b7fba9ceae2289d828208d6fbb19d7caddefdd%5E%5E/

Current Stingray diagnostic DTS:
- Wi-Fi regulator on PU4; `mmc-pwrseq-simple` reset on PU2, `post-power-on-delay-ms=300`, `power-off-delay-us=200`.
- pwrseq `ext_clock` points to `tegra_pmc TEGRA_PMC_CLK_BLINK`, and PMC's 32k input fixed-clock node exists.
- Wi-Fi child `wifi@1` has no directly declared `lpo` clock; Linux reports `brcmf_of_probe no LPO clock`.
- This log is **not proof the physical PMC blink output is off**: a separate MMC power sequencer may have enabled the clock.

Broadcom BCM4329 specification (2010), Frequency References, page 70: 38.4-MHz default crystal reference or auto-frequency detection needing stable 32.768-kHz low-power input during power-on reset. The v020 NVRAM has `xtalfreq=38400`. Full source: https://media.digikey.com/pdf/Data%20Sheets/Cypress%20PDFs/BCM4329_RevF_Sep19,2016.pdf
Current upstream clock binding: https://kernel.googlesource.com/pub/scm/linux/kernel/git/stable/linux-stable/+/master/Documentation/devicetree/bindings/net/wireless/brcm,bcm4329-fmac.yaml

## v021 observer — offline build only

Branch `wifi/oem-clock-audit`, builder `scripts/experiments/v021-build-lpo-observer.py`, patch `patches/experiments/v021-brcmfmac-f2-cccr-readback.patch`. Instrumented module 462,492 bytes, SHA256 `13fb5af5cc637bf77d61fed8c7199dbaef2d979879e49669fe6c72387cb5007d`. Original kernel `sdio.c` restored to SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab`.

The observer obtains the Wi-Fi power sequencer's first clock from its DT node and reports Linux's `clk_get_rate()` and `__clk_is_enabled()`, without enabling or changing hardware. **Do not infer physical waveform quality even if these software fields report enabled.** The module compiled, SHA-verified on Surface, but was **not uploaded or activated** due to remote safety block. No clock result is claimed.

## Next controlled experiment

1. Resolve the approved/authorized RAM module upload path, then collect v021 read-only clock-provider rate/enable fields at the actual F2 window. Do not bypass a host safety block.
2. Compare effective pwrseq and regulator transitions to OEM 100/100/200 ms GPIO sequence. If the clock is disabled or rate wrong, correct only that specific clock path; do not change firmware simultaneously.
3. If clock provider is enabled at 32768, investigate GPIO power/reset timing and actual voltage/oscillator with read-only kernel instrumentation; physical waveform requires measurement to confirm.
4. Only use on-demand MMC2 re-enumeration to compare reset/power profiles after proving it really toggles the appropriate lines. Keep eMMC and original recovery untouched.
5. Promote Wi-Fi only after F2 ready and persistent wlan0, then per-device MAC/regulatory provenance and repeat connection qualification.
