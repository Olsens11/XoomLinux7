# BCM4329 full datasheet review — Section 11 and F2 diagnosis (2026-10-24)

**Document:** Broadcom BCM4329 Preliminary Data Sheet 4329-DS105-R (2010), Cypress 002-14927 Rev *F (2016). Reviewed all 149 PDF pages, concentrating on Sections 9–15 and 23. User-provided source: https://www.rxelectronics.jp/datasheet/ff/CYW4329HKUBGT.pdf (private attachment remains authoritative); second hosted copy: https://media.digikey.com/pdf/Data%20Sheets/Cypress%20PDFs/BCM4329_RevF_Sep19,2016.pdf.

**Diagnosis still open.** Physical Xoom reports F1 responsive, firmware/NVRAM readback PASS, F2 IOEx=0x06 but IORx=0x02, timeout -62; no wlan0. Do not call any proposed test a fix.

## Section 11 — specific requirements, pages 49–52

1. **SDIO default timing = maximum 25 MHz** data-transfer clock (Table 3, p51); initial card identification = maximum 400 kHz. High-speed mode allows up to **50 MHz**, with different input setup/hold and rise/fall specifications (Table 4, p52). Correct physical bus timing depends on the operating mode, not just the clock number.
2. Many Xoom experiments measured `ios.clock=46153846` and `ios.timing=0` (Linux legacy/default). This is **outside the BCM4329 default-mode clock specification** by ~85%. CMD52 functioning and RAM readback do not prove the high clock met timing. **Immediate controlled candidate: AUTO capabilities + actual measured <=25MHz + timing=0**, with unchanged firmware/NVRAM, to test F2.
3. Important NOT-YET-TESTED distinction: v019 capped SDMMC2 to 25MHz **but retained Motorola capabilities and `ios.timing=2` (SD high speed)**, so its negative -62 result is **not** the legacy-mode 25MHz control. v020 Motorola/Auto live tests did not provide arbitrary clock selection. Do not claim the exact 25MHz legacy control was previously disproven.
4. Page 49 SDIO core VDDC must rise and **settle at 1.25 V**, and host must wait **at least 110 ms AFTER this event** before initiating SDIO access. p132 separately says internal POR may hold up to 110ms after **VDDC and VDDIO** pass 0.6V; host must wait >=110ms after supplies available. The current DTS `mmc-pwrseq-simple` 300ms post-power-on delay is not a measurement of actual VDDC/CBUCK/CLDO availability. Confirm timing origin/ordering, don't blindly increase delays.
5. Pull-ups **10–100 kOhm on CMD and all four DAT lines** in every operating state (p49). The device has default weak pull-ups on CMD and DAT0-3, which may be disabled by software; values depend on VDDIO_SD (p77: 30–82kOhm at 1.8V; 15–35kOhm at 3.3V). Check pinmux/regulator and software state without assuming all internal pulls stay enabled through reset.
6. Functional roles (p49): SDIO Function 0 = CCCR, max 32-byte size; Function 1 = backplane SOC register access, max 64 bytes; Function 2 = WLAN DMA packet transfer, max 512 bytes. Our `IOEx=06 / IORx=02` means F2 is enabled/requested in IOEx but not marked ready in IORx. Data readback through F1 proves F1 access, **not** the readiness of the embedded WLAN firmware.
7. Section 11 includes SPI-specific boot handshake/register addresses on pp59–61: SPI F0 address 0x14 test word, wake bit at F0 0x00 bit7, XTAL_PU ~8 ms settling, separate SPI register table. **These are expressly SPI protocol directions, not SDIO CCCR registers. Do not write SPI F0 offsets to an SDIO host or treat the 8ms sequence as a documented SDIO startup requirement.**

## Other crucial sections reviewed

- **Section 9, p47:** BCM4329 WLAN firmware executes on on-chip **ARM Cortex-M3**. Firmware bytes matching a downloaded image is not proof the WLAN CPU exited reset or started its scheduler.
- **Section 10, p48:** WLAN PMU power/resource sequencing clocks count at 32.768kHz; doze mode relies on LPO for wake-up. This motivates measuring clock providers, but not assuming the log `brcmf_of_probe no LPO clock` implies a physically absent clock.
- **Section 12, pp62–63:** DHD downloads firmware at chip powerup; HNDRTE and on-chip software handle BDC/LMAC communications. Firmware boot/SDPCM mailbox handshake must be observed separately from RAM-copy success.
- **Section 13, pp64–66:** WL_REG_ON/BT_REG_ON jointly control internal power regulators; core VDDC is provided by internal converter/CLDO in common topologies. A software `vmmc` regulator state or GPIO transition is not measurement of actual settled VDDC. True low-power shutdown can retain VDDO while removing VDDC/VDDRF.
- **Section 14, pp67–70:** main crystal default 38.4 MHz, consistent with private OEM/generic NVRAM `xtalfreq=38400`. LPO nominal 32.768 kHz, input amplitude 200–1800 mVp-p, duty cycle 30–70% (Table 9, p69). The text acknowledges internal or external LPO options; p68 footnote explicitly states **WLAN does NOT auto-detect reference clock frequency** (Bluetooth/FM can). Do not misapply the p70 auto-detection assertion to WLAN.
- **Section 15, p79:** LPO input pad is WRF_EXTREFIN; pin `XTAL_PU` is the reference-clock request. p84 selects SDIO versus SPI **at WL_RST_N deassertion**, based on WL_GPIO_8 strap (low=SDIO). We have observed enumeration as SDIO but should not ignore reset/strap timing in later power-cycle experiments.
- **Section 15, pp77, 81, 85–87:** device SDIO pull-ups have rail-dependent values; WL_REG_ON and BT_REG_ON have on-chip 200k pulldowns; WL_RST_N and BT_RST_N must be actively driven high or low, not floating.
- **Section 23, pp132–134:** WL_REG_ON/BT_REG_ON are ORed for internal regulator power; active-low WL_RST_N controls WLAN independently. Internal POR and external reset can each hold the WLAN in reset. 110ms minimum after core/I/O rails become available, with Figure 30–33 showing sleep clock and reset/regulator sequencing; diagrams are not directly GPIO-level waveform proof on Xoom.

## Exact next experiment (no hardware claim)

**Test A — first:** Keep known 253,748-byte baseline firmware and MAC-free OEM-matched NVRAM fixed. Set MMC2 to **AUTO / effective legacy timing=0 with actual measured SDIO clock <=25,000,000 Hz**. Preserve v020 RAM-only transport, MMC2 status logging and capability readback. This may require adding a board-scoped on-demand MMC2 host clock control or one bounded temporary-boot candidate. If a 25MHz legacy setting is only a requested max and actual clock differs, record actual rate. Repeat three attempts including card re-enumeration. Capture pre/post IOEx/IORx, chip clock CSR, F2 return, firmware CPU/shared readback and wlan0.
**Test B:** If F2 still -62, audit actual CLK_BLINK/32.768kHz provider enabled and rate, host regulator/pwrseq state, PU4 power and PU2 reset transitions relative to **settled** VDDC; label software telemetry separately from physical oscilloscope/power-rail measurements.
**Test C:** Verify CMD/DAT pull-up and Tegra pinmux electrical requirements in the correct state. Do not change signal pull-up configuration until baseline is established.
**Test D:** Compare Broadcom WLAN core release, PMU resources and SDPCM mailbox handshake versus preserved Motorola vendor source. Avoid conflating the SPI boot procedure with SDIO.
**Acceptance:** Ready bit F2 IORx asserted and enable rc=0, persistent wlan0, correct unique MAC, regulatory settings, repeat stable operation. Module-load rc=0 alone does not pass.

### Non-causal controls already tried

v018 full Motorola six-capability override did change effective parsed version+HS, yet F2 -62. v019 capped clock to 25MHz **in high-speed mode**, still -62. v021 standard vs OEM firmware under AUTO and MOTOROLA, same MAC-free NVRAM, all -62. None of these is an explicit 25MHz **legacy** test. Prefer that next.
