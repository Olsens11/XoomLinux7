# v020: MMC2 on-demand physical acceptance, 2026-10-24

**Result: on-demand MMC2 capability selection and re-enumeration PASSED physically. Native BCM4329 Wi-Fi still FAILED at Function 2 timeout -62.** The tablet was temporarily booted; no partition flashes or block writes, original TWRP Xoom untouched.

## Provenance
- Image: MZ600-stingray-diagnostic-v20-MMC2-ON-DEMAND-TEMPBOOT-ONLY.img, 6,660,096 bytes; SHA256 b08863d6be4ae15f757eb9bfa8089d3a2d23859fc3ea63c4f119f4be9430ebf3.
- RAM initramfs SHA256: 060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67.
- Built from verified ARMv7/no-NEON toolchain; non-PID1 QEMU smoke, boot header, DTB and initramfs embedding PASS. Original MMC source SHA256 cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6 and original build config restored after build.
- Source: patches/experiments/v020-on-demand-mmc2-capability-parameter.patch, src/diag-init/phase1-v20/init.c; build scripts under scripts/experiments/v020-*; Surface host client scripts/host/surface/Xoom-v20-Mmc2LiveLab.ps1.
- Verified source/destination SHA256 via authenticated Desktop-to-Surface SSH. Replacement MZ600 identity and product xoom-cdma confirmed before fastboot boot; USB returned PONG XOOM-LINUX V20.
- Bundled test firmware 253,748 bytes, generic NVRAM 672 bytes; these were not the same OEM firmware used in some earlier v018/v019 experiments. Do not compare across these environments as a firmware-controlled A/B.

## Controlled live test sequence

| Step, no reboot | Observed outcome |
| --- | --- |
| Initial MMC2_STATUS | TARGET VALID, BOUND YES, CARD BCM4329 VERIFIED, MODULES UNLOADED, profile 0 AUTO |
| MMC2_REINIT with AUTO unchanged | mmc2 card removed, mmc-pwrseq reallocated, mode=0 final SDIO version 1 high-speed=0, new SDIO card at address 0001 |
| MMC2_PROFILE MOTOROLA | Root-only kernel sysfs parameter read back 1; flagged pending reinit |
| MMC2_REINIT in MOTOROLA | mmc2 card removed, then kernel logged mode=1 final version 2, multi=1 low=0 wide=0 highpower=1 highspeed=1 and new HIGH-SPEED SDIO card |
| WIFI_START in MOTOROLA | brcmutil rc=0, brcmfmac rc=0; v017 read-only driver reported raw SPEED 03, host timing 2, clock 46,153,846Hz |
| F2 result | IOEx before 02/after 06, IORx before/after 02, chipclkcsr D2, result -62; wlan0 absent |
| MMC2_REINIT with drivers loaded | DENIED PREFLIGHT (no detach); USB remained working |
| WIFI_STOP | Both modules unloaded rc=0 |
| MMC2_PROFILE AUTO + MMC2_REINIT | Kernel logged card removal, mode=0 final version 1 high-speed=0, new SDIO card; profile 0 readback |
| Host acknowledgement regression | Updated host waits for MMC2 REINIT PASS, not just BEGIN. Another AUTO reinit explicitly returned BEGIN followed by PASS BCM4329 REENUMERATED |
| Host failure recognition | With Broadcom modules loaded, client reported DENIED and raised an error instead of reporting success |
| Final | AUTO profile, BCM4329 bound and enumerated, both Wi-Fi modules unloaded, wlan0 absent |

## Scope and limits
- Kernel module parameter xoom_mmc2_profile resides under /sys/module/mmc_core/parameters/, root-only, rejects values other than 0 or 1. Motorola six-field assignment is limited to Stingray plus Broadcom 02d0:4329 after normal CCCR/CIS parsing and before high-speed timing. Other MMC devices use upstream rules.
- USB RAM diagnostic commands: MMC2_STATUS, MMC2_PROFILE AUTO/MOTOROLA, MMC2_REINIT, and MMC2_BIND (recovery). Command paths are fixed, not supplied by host. Guards verify c8000200.mmc OF alias mmc2, compatible platform, presence of mmc0, device CIS and fully unloaded brcmfmac/brcmutil. Driver bind/unbind is restricted to c8000200.mmc.
- CARD_REINIT via driver rebind does not prove Wi-Fi chip rail power-off, 32k clock restart, reset GPIO toggling or a true cold boot. Failure/timeout and MMC2_BIND recovery paths have not been deliberately fault-injected on hardware.
- USB control functionality is accepted, **not native Wi-Fi**. Continue firmware CPU boot/SDPCM tracing, private same-device OEM NVRAM provenance and power/clock sequencing. No RF scan or association was attempted.
- v015 remains separately preserved as reliable RAM-only USB diagnostic fallback.

## Later post-qualification observation: unexpected session restart, cause unknown
After the on-demand test sequence, all worktrees were synchronized and a final Surface check found Xoom USB CDC absent. Windows transiently enumerated the expected replacement MZ600 serial as Motorola USB Composite / ADB, and later detected the Linux CDC COM9 interface again. The v020 USB console responded, but read-only STATUS reported Linux uptime **83.96 seconds**, whereas this same test session had previously logged events beyond **250 seconds**. This is direct evidence that a Linux session restarted in the interim. This workflow issued **no further deliberate reboot/fastboot boot commands after its first v020 boot**; the cause and mechanism of the later restart are not established from available logs.

**Qualification impact:** the tested AUTO/MOTOROLA/AUTO card reinitialization and guard paths physically PASSED during the earlier uninterrupted session. However, v020 must NOT yet be claimed to maintain an indefinitely stable Linux session. Long-duration stability, controller-rebind reset side effects, possible host/tool concurrent activity, device power reliability and any persistent crash evidence remain open. v015 is retained as fallback. Do not conflate this later restart with a failure of a particular card-reinit command without causal evidence.
