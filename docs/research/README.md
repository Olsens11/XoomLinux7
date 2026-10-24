# Research index — evidence before implementation

- [Motorola / Broadcom BCM4329 source audit](MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md): six-field OEM embedded SDIO workaround, vendor boot flow and why previous tests do not prove equivalence.
- [F2 controlled experiment matrix](BCM4329_F2_TEST_MATRIX.md): observations, one-variable testing, identity, calibration and hardware success gates.
- [v016 physical F2 registers](../checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md): IOEx 02→06, IORx stays 02, clockcsr d2.
- [v017 physical CCCR inventory](../checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md): parsed flags and host timing, comparison to OEM.

Do not call an experimental patch a fix until the claimed function works repeatedly on actual hardware. Diagnostic success is not Wi-Fi success.

- [v018 full Motorola counterfactual](../checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md): all six fields effective; F2 still timed out twice.

- [v019 measured 25 MHz control](../checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md): lower clock effective but F2 still fails.

- [On-demand MMC2 re-enumeration design](../architecture/MMC2_ON_DEMAND_DESIGN.md): safe profile controls, controller-specific unbind/rebind and test acceptance — proposal only.
