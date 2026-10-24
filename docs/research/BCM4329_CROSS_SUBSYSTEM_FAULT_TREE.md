# BCM4329 cross-subsystem fault tree — OEM vs Linux 7

**Scope:** source-level review against the full Broadcom BCM4329 149-page datasheet and the actual replacement Xoom v025/v026 tests (2026-10-24). Accompanying [149-page index](BCM4329_DATASHEET_PAGE_INDEX.md) and [36-contract audit](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md).

## Interference paths that ordinary WLAN-only debugging misses

| Path | Datasheet proof | Linux / hardware evidence | What to test next |
|---|---|---|---|
| Bluetooth keeps shared PMU regulators on while WLAN toggles | pp.64, 132: `BT_REG_ON` OR `WL_REG_ON`; Fig.32 p.134 WLAN ON/BT OFF still permits regulator-high | `BT_REG_ON` driver GPIO Tegra I7; U4 fixed WLAN regulator; BT binding and I7 runtime state unmeasured | Observe I7 and U4 before/during MMC2 power-down, plus U0/U2 resets, without altering state |
| WLAN reset is not a full chip power-off | pp.66, 85–87, 132–134: core reset, doze and regulator-shutdown distinct | `mmc-pwrseq-simple` can assert U2 without asserting I7/U4 low; `regulator-boot-on` may hold U4 | Confirm regulator vote history and GPIO latch around rebind; compare to OEM true cold reset |
| LPO clock requested at the wrong point relative to internally powered logic | pp.48, 65, 67–70: LPO drives PMU timers; POR/auto frequency detection | pwrseq enables Tegra `CLK_BLINK` in `pre_power_on`, but U4 `regulator-boot-on` may be high earlier | Monotonic timestamps: first U4 assertion vs blink enable and U2 reset release |
| `txco` clock name aliases low-frequency blink instead of normal reference | pp.29, 67–70, 88: normal reference and 32.768kHz LPO distinct, CLK_REQ signal output | BT child `clock-names="txco"` points to Tegra `TEGRA_PMC_CLK_BLINK`; hci_bcm uses separate `txco_clk` and optional `lpo_clk` | Check BT serdev probe/bind and clock provider rate; check OEM intent before edits |
| Generic NVRAM board identity/clock assumption | pp.67–70: WLAN does not auto-detect normal ref frequency | runtime `.txt` has `xtalfreq=38400`; platform MAC callback unavailable and generic NVRAM lacks `macaddr` | Verify same-device OEM oscillator, firmware/configuration source and alternate MAC location, no hardcoded identities |
| SDIO mode selected by strap latched at WLAN reset | p.84: WL_GPIO_8 low -> SDIO, high/floating -> SPI | Live CMD52 F0/F1/BCM4329 enumeration succeeds: current boot functional SDIO mode | Preserve strap/pinmux mapping in OEM comparison; avoid irrelevant SPI boot writes |
| SDIO CMD/DAT pulls change during chip power down | p.49 and Table 13 pp.85–87 | DTS 4-bit bus & Linux enumeration success do not prove pullups in all operating states | Inspect Tegra pinctrl configuration and OEM pads before assuming board pullups |
| Historical SDIO capability misreport silently reduces host features | pp.49–52: supports SDIO v1.2/high speed | raw CCCR `0x11`, Linux CARD sdio_vsn=1 highspeed=0, historical Motorola six-field override | Test complete OEM quirk in a *controlled, scoped* modern MMC interpretation only when separate from clock/power tests |
| Firmware downloaded but WLAN CPU never runs | pp.47 and 62: on-chip Cortex-M3/HNDRTE target executes WLAN firmware | v026 matching CRC buffers and download readback, `brcmf_chip_cm3_set_active` simply releases core reset, F2 still -62 | Read chip CPU/reset and PMU statuses + SDPCM mailbox after release, not more file copies |
| Active internal PMU resource dependencies stall PLL/core readiness | p.65 PMU ResourceMin, dependencies, transition timers; p.48 power states | chip clock CSR `0xD2` ALP/HT request/status, not direct CPU or complete PMU proof | Read-only PMU ResourcePending/ResourceState around F2; avoid speculative writes |
| Bluetooth serial driver changes shared regulator after MMC starts | pp.29, 64, 132 | `CONFIG_BT_HCIUART=m`, Broadcom subdriver configured `y` within UART module, but loaded/bound state unknown | Verify whether BT serial driver is loaded/bound; do not infer module config implies active runtime behavior |
| Misplaced DTS property compiles but is read by different owner | Linux API/property placement, not a chip datasheet rule | Earlier host 10ms versus pwrseq 300ms confusion, v025 correction; earlier sysfs driver spelling bug | Use executable provenance checker and source-to-DTB comparison; keep source and temporary artifact separately |

## Exact source ownership and semantic chain

1. **Host-controller/power plumbing:** `drivers/mmc/core/core.c` executes `mmc_pwrseq_pre_power_on`, `mmc_delay(host->ios.power_delay_ms)`, `mmc_pwrseq_post_power_on`, sets initial MMC clock, then another host delay. `drivers/mmc/core/pwrseq_simple.c` enables `ext_clock`, asserts U2 reset, releases reset and waits its *separate* `post-power-on-delay-ms`. GPIO commands in this code do not by themselves prove the physical BCM4329 pin voltages.
2. **Regulator:** `regulator-wifi` represents U4 at nominal 3.3V; it is a host-side enable switch, not a 1.25V internal CLDO readback. Boot-on affects the regulator framework's initial enable request. `vmmc` and `vqmmc` are logically separate from internal VDDC.
3. **Bluetooth side:** `drivers/bluetooth/hci_bcm.c` calls `bcm_gpio_set_shutdown`, which changes BT shutdown/REG_ON and resets BT according to the `powered` state. The DT child names I7 for shutdown, U0 for reset, U1 device wake, U6 host wake, PMC blink `txco`. We have not physically read BT I7 or bound-state evidence yet.
4. **SDIO identity:** Linux `sdio_read_cccr` reads raw card capabilities. Motorola's legacy `.embedded_sdio_data` six values cannot be modeled by setting `highspeed` before `sdio_read_cccr` if that routine overwrites the field. Our prior partial v010/v011/v013 changes are not conclusive OEM-quirk tests.
5. **Firmware core:** `brcmfmac/firmware.c` runtime selects files; v026 confirms generic fallback (bin 253748 bytes, source NVRAM 1550, packed 672, CRC matching virtual). `brcmf_chip_cm3_set_active` resets/releases ARM Cortex-M3 but returns true without proving firmware instructions actually ran.
6. **F2 barrier:** `brcmfmac/sdio.c` requests backplane clock, writes mailbox, calls `sdio_enable_func(func2)`; `sdio_io.c` writes IOEx F2 then waits IORx F2. Physical state IOEx `0x06`, IORx `0x02`, -ETIME/-62. This is the earliest hard failure. Later scan/association/RF tuning is out of scope until F2 succeeds.

## Four levels of proof (for every hypothesis)

| Level | Evidence | What it cannot prove |
|---|---|---|
| 0. Stated in datasheet/OEM | Required relationship, pins, time, or programmed sequence | This exact board used that topology or firmware version |
| 1. Present in source/DTB | Correct property exists on correct node and is included in exact image | Runtime callback actually executed |
| 2. Controller execution | Timestamped GPIO/regulator/clock operations and digital readback | Physical chip pin waveform and internal supply settlement |
| 3. Chip effect | SDIO CMD52 chip register changes, PMU status, CPU-generated response | All analog signal-integrity parameters without measurement |

## Ordered non-destructive follow-ups

**First:** run read-only I7/U4/U0/U2 state/owner capture on same v025 kernel through a RAM diagnostic module. Before calling an MMC2 reinit a cold start, determine actual BT driver status and whether U4/I7 reached low together. Do not indiscriminately toggle I7; Bluetooth and WLAN share power.

**Second:** reconstruct Motorola board supply topology (actual VDDC generator and normal 38.4MHz oscillator). Check whether Bluetooth `txco` is a wrong software name, a harmless alias, or an active clock consumer. Correlate PMU clock/votes and the embedded Cortex-M3 reset with the failed F2 enable.

**Third:** add a code-based regression contract that compares checked-in DTS, compiled DTB and live effective MMC clock; ensure the canonical legacy source no longer exposes 46.15MHz as the default without high-speed negotiation.

**Excluded claims:** There has been no measurement of I7, no physical rail capture, no confirmed failed oscillator, no verified internal PMU deadlock, no proof that a missing MAC causes F2, and no evidence Bluetooth must be operational for WLAN. The current objective is to *falsify hypotheses*, not build up a story around one.

## Reference sources

- Datasheet *BCM4329 Preliminary Data Sheet*, supplied PDF (149 pages); sections 3, 9–16, 21, 23.
- Motorola OEM audit: `docs/research/MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md` includes documented full six-field capability override and historical OEM reset sequence.
- Actual test checkpoint files: `V021_LPO_CLOCK_PHYSICAL_2026-10-24.md`, `V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md`, and `V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md`.
- Runtime audit script: `tools/forensics/bcm4329_contract_audit.py` outputs JSON under private build workspace.