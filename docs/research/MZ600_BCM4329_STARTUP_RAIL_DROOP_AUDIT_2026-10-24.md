# MZ600 BCM4329 startup supply transient and regulator-buffering audit

**Date:** 2026-10-24. **Status:** research and read-only source checks only, NOT a physical voltage measurement and NOT an electrical modification. See the physical v035–v039 checkpoint chain, especially v038 MMC2 host PM and v039 original Motorola firmware trials.

## Plausible transient

A short current spike on external VBAT/VDDIO or internally derived 1.25 V VDDC could cause an on-chip reset/firmware-startup disruption. Successful host backplane communication, the BCM4329 PMU resource-state mask 003FE63E with zero pending resources, and ALP-to-HT progression are **discrete software snapshots**, not microsecond-resolution proof of stable power. Their success does not exclude supply sag. The observed SDIO F2 error -62 is a ready-bit timeout, not a voltage reading.

BCM4329 data sheet, original 4329-DS105-R: https://media.digikey.com/pdf/Data%20Sheets/Cypress%20PDFs/BCM4329_RevF_Sep19%2C2016.pdf
- Section 14 figure 22, printed p65 / PDF index 64: integrated core buck, low-noise/core LDOs, PA LDO; different WLAN/BT/FM loads share internal domains. Internal regulator ratings in figure are not measured peak board-current numbers.
- Section 11 printed p49 / PDF index 48: SDIO host MUST wait at least 110 ms **after internal 1.25 V VDDC has ramped and settled**, with greater safety margin dependent on core buck/CLDO output and bypass capacitors. Software U4/U2 delay does not prove VDDC physically met this settling condition.
- Pin table printed p77 / PDF index 76: SR_VDDNLDO and SR_VSSPLDO have specified 220 nF capacitor networks; do not casually alter their manufacturer-defined networks or treat the buck switching output as a DC supply.

## Board-specific supply map, from source

Actual MZ600 diagnostic DTS: src/board/tegra20-motorola-stingray-usbdiag.dts
- Wi-Fi = Tegra SDMMC2, c8000200.mmc / mmc2; **SDMMC4 is eMMC**, not Wi-Fi.
- External switched Wi-Fi supply ownership: 3.3 V **reg_wifi_vdd**, active-high U4 enable, regulator-boot-on, upstream vdd_3v3_sys. **U4 is a control GPIO, not proof of the switched voltage**.
- SDIO interface supply: Motorola **CPCAP VWLAN1**, declared 1.8–1.9 V and always-on, also referenced by Bluetooth.
- WLAN reset U2 and PMC LPO via mmc-pwrseq-simple with 300ms post-power-on delay; 100ms additional host power delay was already tested in v025, F2 still -62. Whether any delay starts after *measured VDDC settling* is not established.
- The sample proposal to swap TPS6586x supplies onto SDMMC4 is wrong for this board. Nominal DTS voltages are not measured physical rail voltages.

## Measurement gate before adding a capacitor

On the **replacement Xoom only**, with the already-qualified temporary kernel, generic 253748-byte Wi-Fi firmware, MAC-free NVRAM and Bluetooth stopped:

1. Use a memory oscilloscope with safe 10x short-ground probing or suitable differential probes; ordinary DMM/min-max is usually too slow for brief startup sag. Verify PCB GND and identify capacitor test nodes with a schematic/continuity trace before probing; avoid shorting dense BGA components or creating earth/USB ground loops.
2. Capture **chip-side 3.3 V switched Wi-Fi input**, **CPCAP VWLAN1 1.8–1.9 V**, and only if safely identified **internal 1.25 V VDDC bypass/output DC node**, plus U2 reset or U4 enable as event markers. Do not confuse regulator output with switching pin SR_VLX1.
3. Trigger on a negative voltage excursion or power/reset transition, save min voltage, droop duration, ripple and timing relative to boot and Cortex-M3 firmware handoff. First test RAM-only WIFI_START with power already present; **do not equate WIFI_STOP/WIFI_START with a new whole-chip POR**. True POR is a separate experiment only after WL_REG_ON/BT_REG_ON/U4 ownership and rollback are qualified.
4. If 3.3 V sags, investigate source and switch; if only 1.8 V sags, investigate CPCAP VWLAN1 and its manufacturer-stability requirements; if only 1.25 V sags, investigate the BCM4329 internal buck/CLDO/inductor/bypass network. If all rails remain stable, prioritize Cortex-M3 NVRAM token/firmware handshake.
5. A bypass or reservoir cap can help *short* current spikes, but not sustained current limiting. Actual needed storage depends on current step, duration and allowable sag, plus ESR/ESL/PCB inductance and ceramic DC-bias derating. Extra capacitance can **increase inrush or destabilize a regulator**. Select both capacitance and placement only after actual rail measurements and control-loop/stability limits are known, never by guessing/soldering to GPIO U4, SDIO pins or switching outputs. TI regulator-stability reference: https://www.ti.com/document-viewer/lit/html/SSZTBJ1/ .

## Assessment of accompanying suggestions

- Early original Motorola HRI39 calibration and the existing Linux 7 prepared 1550-byte NVRAM both contain **boardflags=0x200** and **xtalfreq=38400**. Neither has CR bytes; current reference has 97 Unix LF. There is no demonstrated missing boardflags/CRLF fault.
- The proposed **sdhci.debug_quirks=0x40** is NOT a low-speed control. Pinned Linux 7 sdhci.h defines this as BROKEN_ADMA (bit6); setting the global debug_quirks can replace the per-host quirk mask. Do not apply.
- The suggested **keep_img, sd_drivestrength, clkreq, sd_rxreg, sd_txreg** were not present in the recovered HRI39 or prepared Linux 7 NVRAM references; host C variable named clkreq does not imply a supported NVRAM knob. No firmware parser semantics were proved for these suggestions.
- COM9 is USB gadget diagnostics, not a physical supply or SDIO waveform monitor. Bounded logs showed no recent host clock-stabilization fault but cannot exclude short droop.
- Last verified generic firmware **253748 bytes**, SHA256 d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93, CRC32 B4092AA6 (restored after v039).

**Decision:** Power-rail transient remains unproven and deserves event-aligned analog measurement. No capacitor value or hardware node can be approved from current information. Do not change regulator voltage, current limits, GPIO wiring, sample NVRAM or persistent partitions as a speculative fix.
