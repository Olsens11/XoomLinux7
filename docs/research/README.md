# Research index — evidence before implementation

- [Motorola / Broadcom BCM4329 source audit](MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md): six-field OEM embedded SDIO workaround, vendor boot flow and why previous tests do not prove equivalence.
- [F2 controlled experiment matrix](BCM4329_F2_TEST_MATRIX.md): observations, one-variable testing, identity, calibration and hardware success gates.
- [v016 physical F2 registers](../checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md): IOEx 02→06, IORx stays 02, clockcsr d2.
- [v017 physical CCCR inventory](../checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md): parsed flags and host timing, comparison to OEM.

Do not call an experimental patch a fix until the claimed function works repeatedly on actual hardware. Diagnostic success is not Wi-Fi success.
