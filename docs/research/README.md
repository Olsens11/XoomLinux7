# Research index — evidence before implementation

- [Motorola / Broadcom BCM4329 source audit](MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md): six-field OEM embedded SDIO workaround, vendor boot flow and why previous tests do not prove equivalence.
- [F2 controlled experiment matrix](BCM4329_F2_TEST_MATRIX.md): observations, one-variable testing, identity, calibration and hardware success gates.
- [v016 physical F2 registers](../checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md): IOEx 02→06, IORx stays 02, clockcsr d2.
- [v017 physical CCCR inventory](../checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md): parsed flags and host timing, comparison to OEM.

Do not call an experimental patch a fix until the claimed function works repeatedly on actual hardware. Diagnostic success is not Wi-Fi success.

- [v018 full Motorola counterfactual](../checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md): all six fields effective; F2 still timed out twice.

- [v019 measured 25 MHz control](../checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md): lower clock effective but F2 still fails.

- [On-demand MMC2 re-enumeration design](../architecture/MMC2_ON_DEMAND_DESIGN.md): safe profile controls, controller-specific unbind/rebind and test acceptance — proposal only.

- [v020 physical on-demand MMC2 card re-enumeration](../checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md).

- [v021 calibration/firmware A-B result and clock/reset research](../checkpoints/V021_OEM_FW_AND_LPO_HYPOTHESIS_2026-10-24.md).

- [BCM4329 full datasheet, Section 11 timing and reset requirements](BCM4329_DATASHEET_SECTION11_REVIEW_2026-10-24.md): first untested control is <=25MHz **legacy** mode.

- [Physical outcome of the Section 11 legacy 25 MHz control](../checkpoints/V022_AUTO_LEGACY_25MHZ_PHYSICAL_2026-10-24.md): three attempts, still -62.

- [Audit of inherited pwrseq property placement and v025 hardware results](../checkpoints/V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md): 100ms effective before reset, still -62.

- [Virtual forensic lab v1 test record](VIRTUAL_FORENSIC_LAB_V1_2026-10-24.md): host artifact checks, independent ARM/QEMU device-tree and NVRAM decoding, seven intentional faults detected.

- [BCM4329 datasheet, full 149-page reference index](BCM4329_DATASHEET_PAGE_INDEX.md) — every page, relevance and topic.
- [BCM4329 requirement audit](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md) — 36 direct and cross-system constraints, evidence levels and gaps.
- [BCM4329 cross-subsystem fault tree](BCM4329_CROSS_SUBSYSTEM_FAULT_TREE.md) — shared WLAN/BT regulators, clocks, reset, straps, PMU and CPU handoff.

- [BCM4329 whole-chip resource ownership and OEM reconstruction](BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md): Motorola shared U4 count, deliberately low BT I7 on rfkill, differences from Linux 7, staged safe power sequencer design and offline verification.

- [BCM4329 shared-chip resource owner architecture](BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md) — now supported by v028 GPIO register tests and v029 isolated kernel object compilation.

- [Whole BCM4329 ownership design](BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md) updated by [v030 BT U4 regulator opt-in](../checkpoints/V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md).
