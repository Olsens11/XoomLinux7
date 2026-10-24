# v027 physical WLAN + Bluetooth GPIO state observation — 2026-10-24

**Context:** Read-only BCM4329 cross-subsystem survey motivated by the 149-page Broadcom datasheet, especially pp.29, 48, 64–70, 81–89, 132–134 and shared regulator OR semantics. The test was run on the **replacement MZ600**, using existing v025 RAM-booted Linux 7, through the established USB diagnostic transport. **No reboot, flash, observer-issued GPIO writes or external power/reset GPIO changes.** The normal brcmfmac startup path still performs firmware download and Cortex-M3 core reset/release; the observer itself only samples state. The BCM4329's F2 ready failure persists.

## Exact observer

- Source: `scripts/experiments/v027-build-dual-reg-state.py`, derived from pretested v024 GPIO observer; read-only extra lines for I7, U0, U1, U6, plus U4/U2/U5 and LPO.
- Compiled ARM kernel module: `brcmfmac-v027-forensic-readonly.ko`; **464,584 bytes**, SHA256 **`12e355a0e2db6ffe6481612825b5292bbbf6010653155e11525adc31d8756d3e`**.
- Surface-side SHA256/size independently matched builder; USB uploader verified **464584 bytes, CRC32 `5D38663F`**.
- Source `sdio.c` restored byte-for-byte after compile, SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab`.
- The observed GPIO function gets direction via `gpiod_get_direction`, raw latch via `gpiod_get_raw_value_cansleep`, logical via `gpiod_get_value_cansleep` and polarity via `gpiod_is_active_low`. **It neither requests nor configures the GPIOs**. Do not infer alternate-function pin voltages from `gpiod_get_raw_value_cansleep` when direction call fails.

## Physical startup trace

The recorded snapshot began at monotonic `8258341750000 ns` and ended at `8258341970000 ns` (approximately 220 μs software sampling span). This **is not** a power-on event timeline, because it occurs after SDIO enumeration and firmware download.

| Tegra GPIO | Observed direction | raw | logical | active_low | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| U2 WLAN reset (162) | 0 (output) | 1 | 0 | 1 | Output high = WLAN reset deasserted |
| U4 WLAN power (164) | 0 (output) | 1 | 1 | 0 | Host GPIO output high |
| U5 WLAN host wake (165) | -22 | 0 | 0 | 0 | Direction query unavailable; no trustworthy pin-level conclusion |
| I7 BT_REG_ON (71) | **-22** | 0 | 0 | 0 | **Do not conclude BT regulator low**; read method invalid for current pin state |
| U0 BT_RST_N (160) | **-22** | 0 | 0 | 0 | **Do not conclude BT reset asserted** |
| U1 BT_WAKE (161) | **-22** | 0 | 0 | 0 | Host-facing BT GPIO state not yet established |
| U6 BT UART_WAKE (166) | **-22** | 0 | 0 | 0 | Interrupt/pinmux ownership unverified |

Also observed pwrseq clock software rate **32768 Hz**, enabled=1; MMC2 host `power_delay_ms=100`, `ios.clock=25000000`, `ios.timing=0`. F2 final `IOEx=06`, `IORx=02`, `result=-62`. Nothing new was demonstrated about chip-side power-on timing.

**Instrumentation artifact:** the optional `SNAPSHOT_BEGIN` and `SNAPSHOT_END` lines contained a literal escaped newline in the emitted log; timestamps were nevertheless parsed, and the individual GPIO result lines were not affected. Do not infer a GPIO error from the formatting issue.

## Cross-subsystem interpretation

Broadcom explicitly ORs `WL_REG_ON` with `BT_REG_ON` for its internal regulator control (p.132). We confirmed from DTS/compiled DTB that Motorola-mapped WLAN U4 and Bluetooth I7 are separate external controls, but **the v027 physical snapshot did not prove I7 electrical or logical state**, because Linux's generic GPIO direction query returned `-EINVAL/-22` for that pad. This is consistent with an unconfigured/alternate-function/otherwise unavailable descriptor but does not distinguish those possibilities.

Additionally, the actual compiled v025 DTB assigns exactly the same **clock phandle and index `<0x26 0x03>`** to WLAN pwrseq `ext_clock` and Bluetooth child `txco`. Linux's `hci_bcm` driver treats `txco_clk` as a normal reference resource, distinct from optional `lpo_clk`. This is a **source-level clock role suspicion**, not yet demonstrated runtime misconduct. Query BT serial device binding and PMC clock parent/rate before changing.

## Next non-destructive discrimination

1. Verify Bluetooth serdev child is actually bound and `CONFIG_BT_HCIUART` module loaded; config alone does not prove driver active.
2. Query Tegra GPIO ownership/pinmux registers and actual I7/U0/U1/U6 pad configuration **without requesting/changing pins**. If alternate function, use appropriate Tegra read-only pad register inspection, not GPIO read.
3. Inspect regulator consumer-vote state and timestamp power/reset callbacks across a future controlled *real* MMC power transition, accounting for `regulator-boot-on`.
4. Compare OEM wired BT power control and oscillator source with the compiled DTS to avoid conflating 32.768kHz LPO with the normal 38.4MHz reference.
5. If all controller/software evidence is exhausted, only then consider supervised electrical measurement. Do not casually drive BT or WL regulator-enable lines.

## Final condition

Executed `WIFI_STOP` successfully (`brcmfmac_rc=0`, `brcmutil_rc=0`). Final `MMC2_STATUS`: target valid, bound yes, card BCM4329 verified, `AUTO` profile 0, Broadcom modules unloaded, USB alive. **Wi-Fi remains F2 -62 / no wlan0.**

All source data is non-sensitive; avoid committing raw MAC, OEM firmware binaries or chip calibration material.
