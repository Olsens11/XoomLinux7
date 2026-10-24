# Motorola / Broadcom BCM4329 F2 investigation — source audit (2026-10-24)

**Working state:** v015 ARM Linux diagnostic transport and module hotload physically verified. Native Wi-Fi does NOT work. v016 trace observed `IOEx 0x02→0x06`, `IORx 0x02→0x02`, chip-clock CSR `0xD2`, final `-62`; no `wlan0`.

**Question:** Why does the BCM4329 decline to assert SDIO Function 2 ready after otherwise successful firmware/NVRAM download? No root cause has been demonstrated.

## Sources: original evidence first

1. User-supplied Motorola Tegra historical diff, archived in Android Git:
   https://android.googlesource.com/kernel/tegra/+/13b7fba9ceae2289d828208d6fbb19d7caddefdd%5E%5E%5E2..13b7fba9ceae2289d828208d6fbb19d7caddefdd%5E%5E/
   The enormous diff contains early Stingray Wi-Fi code, kernel config and Broadcom integration.
2. More targeted Motorola Stingray merge diff (July 2011), `board-stingray-wifi.c`:
   https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842%5E2..eb4e253d7d76f6093ef50597e909157c21803842/
3. Historical Broadcom vendor implementation `dhd_sdio.c`:
   https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/dhd/sys/dhd_sdio.c
4. Linux Wireless documentation on `brcmfmac` firmware and board NVRAM:
   https://wireless.docs.kernel.org/en/latest/en/users/drivers/brcm80211.html
5. Original Linux 7 project and Wingray DTS:
   https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dts
6. Local Linux 7 source: `drivers/mmc/core/sdio.c`, `drivers/mmc/core/sdio_io.c`, `drivers/net/wireless/broadcom/brcm80211/brcmfmac/{sdio.c,bcmsdh.c,chip.c}`. Specific code is a local build-source extract; re-verify it against pinned commit and compiled image before calling any behavior accepted.
7. Xoom recovery project OEM Wi-Fi runtime and actual same-device references: **read-only private reference**. Do not publish extracted firmware, calibration or per-unit identity.

## Motorola's actual workaround: six capabilities, not one

Stingray `embedded_sdio_data` supplies:
```
.sdio_vsn = 2,
.multi_block = 1,
.low_speed = 0,
.wide_bus = 0,
.high_power = 1,
.high_speed = 1,
```
Motorola explains that the BCM4329 reports incorrect SDIO version `1`. This structure substitutes *all six* fields during historical card setup; it is not just a post-read revision patch. The card/host wiring also marks WLAN SDIO built-in, supplies 1.65–1.95V OCR, and uses a software card-presence/registration interface. The historical platform controls reset and shared power with staged 100/100/200 ms delays. Modern Linux has different MMC interfaces, so blindly copying old structures is neither possible nor proven safe.

**Critical review of our tests:**
- v010 altered `card->cccr.sdio_vsn` in the modern MMC implementation. It did **not** reproduce the full embedded CCCR override or verify each final field.
- v011 altered `card->cccr.high_speed` separately. It did **not** reproduce Motorola's full structure.
- v013 used host `.init_card` to set high-speed earlier. **Linux 7 `mmc_sdio_init_card()` calls `.init_card` BEFORE `sdio_read_cccr()`, which subsequently reads and can overwrite `high_speed`** unless a complete, correct quirk path is implemented. v013 did not demonstrate that its intended field survived. This is a source-order deduction and must be measured.
- None of v010/v011/v013 conclusively tests Motorola's six-field workaround; none proves the OEM approach would fix F2.
- `sdio_read_cccr` uses the *raw* lower-nibble CCCR structure version to decide which capability addresses to read, and assigns the *upper-nibble* SDIO revision into `card->cccr.sdio_vsn`. An after-the-fact change to `sdio_vsn` does not replay earlier parsing decisions.

## Broadcom's F2 behavior

Vendor `dhd_bus_init` enables F1+F2 by writing SDIO CCCR IOEx and polls IORx until F2 ready, after setting clocks and protocol mailbox. Mainline `brcmfmac` likewise forces the chip backplane clock, sets SDPCM protocol mailbox and calls `sdio_enable_func(func2)`, which writes IOEx and polls IORx for up to its function timeout. They are not fundamentally different checks. The mainline return `-62` is the observed timeout, not a card-presence error.

v016 on real MZ600:
- before F2: IOEx `02` / IORx `02`, valid CMD52 reads; after: IOEx `06` / IORx `02`; no CMD52 errors.
- chip clock status `D2` both times: includes ALP+HT available bits, FORCE_HT and HT request. This suggests clocks are being requested/available at the instant of measurement, but does **not** prove firmware CPU boot or all reference oscillators/sequencing are correct.
- Standard and old vendor firmware have been tried in separate earlier tests. That does not establish a matched working firmware + matching *same-device* NVRAM configuration. CRC download/readback demonstrates memory transfer, **not** that the firmware executed successfully.

## Alternative fault families to discriminate, not guess

1. Card capability discovery differs from Motorola's complete override (raw CCCR, final six fields, host bus configuration, voltage).
2. Firmware + board-specific NVRAM/calibration mismatch or wrong firmware rev/build for BCM4329 rev 3.
3. Chip CPU release/reset-vector/boot handshake failure after firmware RAM download (check CPU core and shared RAM/log).
4. Reset/power/32k low-power reference timing or shared Bluetooth/Wi-Fi regulator sequencing divergence.
5. SDIO controller clock and signal integrity (actual host frequency, timing, tap/trim, voltage; original Wingray DTS chose ~46.15MHz vs downstream 48MHz).
6. Error in SDPCM mailbox write / register readback before enabling F2.
7. A physical device/firmware defect (only after proving same inputs work on reference hardware).

## Strict acceptance criteria

Qualify each stage independently: card enumeration; CCCR/host timing capture; firmware identity, payload and same-device calibration; firmware CPU execution; IORx bit for F2 asserted; `sdio_enable_func` returns 0; `wlan0` persists; valid per-unit MAC and regulatory settings; legally compliant RF scan; stable authenticated link; successful repeat tests across cold and warm boots. None of the latter stages has been claimed.

**No magic delays, unconditional F2-ready faking, hard-coded MAC, speculative clock patches or permanent flash.** Capture accepted negative tests as part of the record.
