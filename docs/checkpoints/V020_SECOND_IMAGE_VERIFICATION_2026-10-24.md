# v020: second image identity and live MMC2 testing, 2026-10-24

**Physical tests passed for runtime MMC2 re-enumeration; Wi-Fi remains FAILED at F2 -62.**

## Exact image distinction

Two different compiled v020 boot images are present in the records, each 6,660,096 bytes. They are NOT the same binary:

- Earlier published v020 image SHA256: b08863d6be4ae15f757eb9bfa8089d3a2d23859fc3ea63c4f119f4be9430ebf3.
- Image separately staged and SHA256 verified on Desktop and Surface for this test: e23e3dea2a0996bb7d63c8e7158715ad6799b57f45e4dcc3fcab454b528bc6bb.

The source of the differing binary hashes is not established. The second image uses RAM rootfs SHA256 060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67. ARMv7 Cortex-A9/no-NEON and QEMU smoke passed, the Android boot header/kernel/DTB/initramfs tests passed, and the original kernel MMC source was restored at SHA256 cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6.

The replacement MZ600 was identified by the existing private serial and fastboot product xoom-cdma, then temporary-booted using fastboot boot. **No partitions flashed.**

## Hardware sequence with no intervening reboot

1. USB COM9 identified V20. MMC2_STATUS reported target valid, driver bound, BCM4329 card verified, modules unloaded, AUTO profile 0.
2. MMC2_REINIT (AUTO) passed and re-enumerated the card. Read-only v017 probe confirmed version 1, highspeed 0, timing 0, clock 46,153,846 Hz, F2 -62 and no wlan0.
3. An MMC2_REINIT attempt while Broadcom modules were loaded was DENIED PREFLIGHT; host treated this as an error. Modules were then unloaded cleanly.
4. MMC2_PROFILE MOTOROLA selected and read back mode 1, pending reinitialization. MMC2_REINIT passed. Read-only v017 probe confirmed version 2, highspeed 1, timing 2, raw SDIO SPEED 0x03, actual clock 46,153,846 Hz; IOEx 0x06, IORx 0x02, F2 -62.
5. Both modules unloaded; MMC2_PROFILE AUTO selected mode 0 and MMC2_REINIT passed. Read-only v017 probe verified version 1, highspeed 0, timing 0 and raw SDIO SPEED 0x01 again. F2 remained -62. Both modules unloaded.
6. Final status check: Wi-Fi controller bound, card verified, AUTO profile 0, Broadcom modules unloaded, USB live.

These tests prove a working on-demand card re-enumeration path without rebooting or rebuilding Linux **for capability-profile changes**, not a full chip power cycle and not working Wi-Fi. No RF scan or association was attempted.

## Stability limitation

Another project checkpoint observed an intervening Linux session restart of unknown cause after the original live testing sequence. Long-running v020 stability is **not qualified**, and no specific MMC2 reinit action has been proven to cause the restart. Later USB checks found COM9 responding with profile AUTO. Do not conflate separate boot instances.
