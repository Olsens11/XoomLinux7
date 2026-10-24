# BCM4329 datasheet — complete implementation contract and discrepancy audit

**Reference:** Broadcom BCM4329 Preliminary Data Sheet 4329-DS105-R, 2010 text / Cypress wrapper Rev *F, 2016, 149 pages. See [page-by-page index](BCM4329_DATASHEET_PAGE_INDEX.md). Current Linux 7 checkpoint: real v025 temporary boot plus v026 module logs. This is not a Wi-Fi repair claim.

Classification is strict: **FAIL** only when actual source/artifact contradicts a requirement, **PASS** only for the measured level (source/artifact/controller), and **OPEN** wherever chip-level delivery has not been verified. A datasheet requirement does not determine Tegra GPIO numbers without Motorola board-specific wiring.

| ID | PDF pages | Broadcom requirement / cross-dependency | Current implementation/evidence | Classification |
|---|---|---|---|---|
| R01 | 49,51–52 | Default SDIO transfer <=25 MHz unless high-speed mode actually enabled | Base repository DTS still requests max 46,153,846; v025 compiled image and physical host clock 25MHz legacy | **SOURCE FAIL / V025 PASS** |
| R02 | 49,51–52 | SDIO identification <=400 kHz, high-speed <=50 MHz; legal timings depend on selected mode | Physical logs prove post-enumeration 25MHz, not frequency of initial CMD5 or EHS negotiation | **OPEN for identification** |
| R03 | 49 | DAT0–DAT3 and CMD pull-ups 10–100kΩ maintained in all operating states | Neither Tegra pad pulls nor external board pullups fully inventoried across power modes | **OPEN** |
| R04 | 49,132 | Host access >=110ms after VDDC/VDDIO settled (internal POR can persist) | v025 software 100ms host +300ms pwrseq +100ms host, but no physical VDDC settling clock | **TIMING SOURCE EXISTS; CHIP EVENT OPEN** |
| R05 | 49 | F0/F1/F2 distinct, F2 max 512-byte block and must become ready | F0/F1 CMD52 and backplane RAM readback pass, F2 IORx 02 and -62 timeout | **F2 FAILURE CONFIRMED** |
| R06 | 49–52 | Correct SDIO 4-bit pins, CMD, CLK, pad timing and data voltage | DTS bus-width=4, physical reported MMC enum buswidth=2 (4-bit); pad electrical characteristics unmeasured | **SOFTWARE MATCH / PHYSICAL OPEN** |
| R07 | 47,62 | Downloaded firmware must execute on embedded Cortex-M3 | Actual binary 253,748 bytes loaded and read back, ARM reset released; no CPU execution/handshake proved | **OPEN, HIGH PRIORITY** |
| R08 | 48,65–66 | WLAN PMU controls internal supplies and clock resources via 32.768-kHz timers and dependencies | PMU resource votes and ResourcePending not sampled; `clkcsr=d2` alone not full PMU proof | **OPEN, HIGH PRIORITY** |
| R09 | 64,132 | WL_REG_ON and BT_REG_ON are ORed for shared internal regulator enable | DTS WLAN U4, Bluetooth I7; no paired runtime measurements | **OPEN, CROSS-SUBSYSTEM** |
| R10 | 64,132–134 | External resets and internal POR are distinct; both WL and BT regulator-control contexts matter | U2 WLAN reset, U0 BT reset, U4 WLAN power, I7 BT power; reset sequence only partly traced | **OPEN, CROSS-SUBSYSTEM** |
| R11 | 66 | Full low-power shutdown differs from WLAN-only reset or doze; VDDIO can remain powered | MMC re-enumeration does not prove shared BCM4329 regulators cycled; boot-on property on WLAN regulator | **OPEN** |
| R12 | 65,116–119 | VDDC 1.25V internal CLDO/CBUCK rails are not MMC `vmmc`/`vqmmc` | Linux reports 3.3V vmmc and 1.8V vqmmc; actual 1.25V core topology unverified | **OPEN** |
| R13 | 132–134 | WLAN reset active-low and must be driven, never floating | DTS U2 active-low; v024 steady read raw HIGH => reset deasserted; no pin-level waveform | **CONTROLLER PASS ONLY** |
| R14 | 132–134 | BT reset active-low and must be driven, never floating | DTS U0 active-low; actual runtime pin owner/state not audited | **OPEN** |
| R15 | 132–134 | Figure 32 WLAN-on/BT-off must be possible; BT need not run for WLAN | Shared OR regulator logic allows distinct subcore reset control | **DESIGN FACT, NOT FIX** |
| R16 | 69–70 | Stable ~32.768kHz LPO when required by PMU/POR | v021 Linux clock provider enabled=1 at 32768Hz; physical delivery, phase, duty unknown | **SOFTWARE PASS ONLY** |
| R17 | 67–70 | Normal TCXO/crystal distinct from LPO; WLAN does not auto-detect normal frequency | NVRAM xtalfreq=38400, hardware oscillator source and real PLL configuration unverified | **OPEN** |
| R18 | 29,67–70,88–89 | Bluetooth `CLK_REQ` is an output; `txco` normal reference and LPO must not be conflated | Bluetooth DTS labels Tegra `CLK_BLINK` as `txco` while `hci_bcm` names separate txco/lpo handles | **POSSIBLE SOURCE SEMANTIC ERROR** |
| R19 | 64,67,132 | External LPO must be ready before the chip requires it | pwrseq enables `ext_clock` before U2 release, but U4 `regulator-boot-on` may assert power earlier | **ORDER INDETERMINATE** |
| R20 | 84 | WL_GPIO_8 low at WL_RST_N release chooses SDIO, high/floating chooses SPI | Live SDIO F0/F1 respond, so current strap mode is SDIO | **FUNCTIONAL PASS, SAME BOOT** |
| R21 | 85–87 | Reset-state GPIO and SDIO pad pulls vary by operating mode | DTS strap/pad default source not proven for cold power-up and idle transitions | **OPEN** |
| R22 | 49,84–89 | Out-of-band WLAN IRQ GPIO optional but level/pinmux must match board | U5 configured level-high, GPIO read direction -22; IRQ mux/registration unproven | **OPEN, LOWER PRIORITY TO F2** |
| R23 | 49,51 | CCCR/CIS SDIO capability parsing must respect silicon errata | CCCR 0x11 parsed SDIO version 1 & highspeed false despite Broadcom SDIO v1.2 support; OEM six-field override exists | **OEM TRANSLATION DISCREPANCY** |
| R24 | 62–63 | Host downloader and on-device BDC/SDPCM software are separate | v026 runtime CRC matches known .bin and NVRAM; target execution not proven | **FILE PROVENANCE PASS / RUNTIME OPEN** |
| R25 | 81–83,90–92 | GPIO inputs have pad pulls, thresholds, and voltage domains | Tegra U4 controller high != confirmed BCM4329 WL_REG_ON pin above VIH | **ELECTRICAL OPEN** |
| R26 | 64,132–134 | BT GPIO I7 may keep regulator on during WLAN reset/rebind | BT child shutdown=I7, hci_bcm shutdown handler drives it when BT driver is active; BT binding unmeasured | **CROSS-SUBSYSTEM OPEN** |
| R27 | 29,88–89 | BT_WAKE/UART_WAKE mux and polarity are software configurable | BT U1 and U6 configured separately from Wi-Fi U5; pad function and BT startup unknown | **OPEN; DO NOT CONFUSE WITH WLAN F2** |
| R28 | 116–119 | Internal regulator ramp/settling characteristic depends on topology | No board-level measurements of CBUCK/CLDO; Fig.22 only a topology example | **OPEN** |
| R29 | 121 | Bluetooth can be operating with WLAN held in reset | Page 121 Bluetooth power measurements use WLAN reset asserted, reinforcing independence | **HARDWARE INTERACTION FACT** |
| R30 | 132–134 | Power/reset diagrams show distinct combinations of WLAN/BT on/off | Fig.32 has BT reset LOW while shared REG_ON can be HIGH; I7 state alone not proof Bluetooth active | **IMPORTANT INTERPRETATION** |
| R31 | 53–61 | SPI host wake-up registers/boot sequence apply to SPI mode | Physical Xoom uses SDIO; cannot directly apply SPI F0 0x14 procedure to it | **NOT APPLICABLE TO SDIO** |
| R32 | 62,81–82 | Board-specific NVRAM and MAC data are integration concerns, not an explicit F2 enable timing requirement | v026 platform MAC unavailable, generic NVRAM lacks macaddr; OTP path unknown | **INTEGRATION OPEN, CAUSALITY UNPROVEN** |
| R33 | 29,88 | BT GPIO mux register controls whether CLK_REQ mode is actually active | DTS cannot establish BCM4329 internal pad mux or BT_TM0 strapping | **OPEN** |
| R34 | 49,132 | Host clock and first access cannot precede POR and valid SDIO pad state | MMC pwrseq ordering source correct in principle; first actual SDIO CMD time not traced | **EVENT TIMELINE OPEN** |
| R35 | 67–70 | Valid external normal crystal/TCXO signal must match configured xtalfreq | Host power pwrseq CLK_BLINK only 32k software proof; 38.4MHz physical signal not established | **CLOCK INPUT OPEN** |
| R36 | 64–66 | Retained shared supply means warm reset and true power-cycle may produce different firmware state | No actual complete regulator-off cycle demonstrated, and F2 persists through MMC2 rebinds | **MAJOR TEST-COVERAGE GAP** |

## What is proven wrong versus merely unresolved

**Direct checked-in source discrepancy:** main `src/board/tegra20-motorola-stingray-usbdiag.dts` still requests `max-frequency = <46153846>` for SDMMC2, while the measured effective card mode is legacy (`timing=0`) and Broadcom page 51 limits default data-transfer mode to **25 MHz**. The tested v025 **appended DTB** was patched to 25 MHz, and repeated physical tests still failed F2. Therefore the canonical source is non-compliant for that mode, but fixing clock speed is *not sufficient* to explain F2.

**Potential semantic clock mixup:** Bluetooth DTS `clock-names="txco"` points to Tegra PMC `TEGRA_PMC_CLK_BLINK`, which is also the WLAN low-power pwrseq clock provider. Linux `drivers/bluetooth/hci_bcm.c` treats `txco_clk` as the external reference resource and separately looks for optional `lpo_clk`. Confirm whether this 32.768-kHz source is intentionally mislabeled or actually consumed by the BT driver before modifying it. A wrong BT clock name may have no impact if the BT UART controller was never bound.

**Shared-power hazard:** Bluetooth `BT_REG_ON` (DTS I7) and WLAN `WL_REG_ON` (DTS U4) are ORed on silicon. Fig. 32 (p.134) depicts WLAN ON with BT reset held low even if both REG lines are high. Do not infer BT is active from a REG line high; do not infer complete shared regulator-off from WLAN U2 reset or MMC2 re-enumeration.

**Unresolved but high-priority:** power-on reset timing relative to *physical VDDC* (not an artificial kernel delay), internal PMU resource-request sequencing, 38.4MHz normal crystal presence versus 32k LPO, full six-field OEM SDIO capability override, firmware Cortex-M3 execution, all-state CMD/DAT pull-ups, and correct first-access voltage and clock.

**Negative evidence:** v026 actual firmware (253748 bytes CRC B4092AA6), source NVRAM (1550 bytes CRC FAFCC93A), and packed NVRAM (672 bytes CRC 596925B1) matched the virtual lab, so a missing generic file or wrong NVRAM packing is disfavored. Platform MAC callback unavailable remains unverified for alternate chip sources and is **not** established to cause F2.

## Reproducible source/artifact check

`tools/forensics/bcm4329_contract_audit.py` independently inspects the **source DTS** and **actual v025 compiled DTB** plus selected Linux consumer symbols, writing JSON to the private build workspace. Initial run: **31 static assertions, 1 failure** (`SOURCE_CLOCK_WITHIN_25MHZ`; source=46153846 Hz), while actual compiled v025 DTB=25000000 Hz. Presence of source consumer symbols or device-tree properties is not proof of invocation or electric pin state.

## A/B/C hierarchy for each signal

- **A — Executed:** common-monotonic timestamps at the Linux callback plus return status; compare v025 source and actual built image.
- **B — Delivered:** regulator/GPIO controller latch and clock consumer state; matching MMC host node; SDIO-side readable register response.
- **C — Effective at chip and correctly ordered:** internal PMU status, observed Cortex-M3 progress and chip-generated response; no software-only test can prove physical VDDC waveform or electrical timing.

Prioritize a scoped **read-only four-GPIO trace** (I7/U4/U0/U2), regulator votes, Bluetooth serdev binding and clock handles, then chip PMU ResourcePending/ResourceState and the Cortex-M3 release-to-F2 sequence. Ensure any future active power-cycle experiment does not accidentally interrupt a Bluetooth/shared rail needed elsewhere.

## Verification boundaries and references

- Datasheet pp.29 (Bluetooth UART handshake), 47–52 (CPU/PMU/SDIO), 62–70 (software/power/clock), 81–89 (pinout/strap/pad), 116–119 (internal regulator), 132–134 (shared reset and regulator timing).
- Software: `src/board/tegra20-motorola-stingray-usbdiag.dts`, `drivers/mmc/core/{core.c,pwrseq_simple.c,sdio.c,host.c}`, `drivers/bluetooth/hci_bcm.c`, `brcmfmac/{sdio.c,chip.c,firmware.c}`.
- Physical checkpoints: `docs/checkpoints/V021_LPO_CLOCK_PHYSICAL_2026-10-24.md`, `V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md`, `V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md`.
- Datasheet itself is not copied into the public repo; only index, paraphrased requirements, test sources and evidence are committed.