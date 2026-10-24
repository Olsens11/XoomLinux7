# MZ600 BCM4329 v5 — firmware provenance, PMU/CM3 observability gates, and live read-only baseline

**Date:** October 24, 2026  
**Goal:** explain and repair Linux 7 SDIO Function 2 never-ready (`IOEx 02→06`, `IORx 02→02`, timeout `-62`) by matching Motorola's actual MZ600 OEM lifecycle and whole-chip dependencies.  
**Status:** OEM artifact inspection **PASS**; privacy-preserving firmware comparator **PASS**; live USB state checks **PASS**; instrumented time-correlated PMU/CM3 register snapshots **NOT YET TAKEN**. No kernel changes, Xoom reboot, power-state toggles, module load or flash during this phase.

## Verified sources and version boundaries

The early **HRI39 and HRI66** production MZ600 Android images contain the identical `bcm4329.ko` (264,038 bytes, SHA256 `4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f`) for `2.6.36.3-g2a65edc`. The matching-generation Motorola kernel sources at [Android Tegra revision 2a65edc](https://android.googlesource.com/kernel/tegra/+/2a65edc/) and modern [pinned Linux 7 commit 2404d273](https://github.com/xoom-linux/linux/tree/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3) were compared in the [v4 source audit](MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md). v4 independently passed 27/27 source/ELF assertions.

The distinct later original-Wingray `2.6.39.4`/BCMDHD environment is **not** used as proof of an early MZ600 startup action.

## 1. Offline original firmware identity and pairing result

| Archived Broadcom binary | Embedded chip/build identity | Bytes | SHA256 |
| --- | --- | ---: | --- |
| Early HRI39/HRI66 normal Wi-Fi | `4329b1`, `4.218.248.20`, Jan 12 2011 | 261317 | `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a` |
| Early HRI39/HRI66 AP+STA | `4329b1`, `4.218.248.20`, Jan 12 2011 | 249307 | `38579087e2b0fbaf61ecae5fcc3363f4331045cd81d29941df0c8ea60b6244ee` |
| Early HRI39/HRI66 manufacturing | `4329b1`, `4.218.248.17`, Dec 9 2010 | 262058 | `e25cad622a165d5faccf6cc2684fc4b3a0d493cee0e35a760df338438232b935` |
| Later OEM `fw_bcmdhd.bin` | `4329b1`, `4.218.248.44`, May 25 2012 | 264140 | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` |
| Linux 7 generic `brcmfmac4329-sdio.bin` | Distinct currently verified runtime blob; embedded build identity not revalidated in this phase | 253748 | CRC32 `B4092AA6` in [v026 physical source provenance](../checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md) |

The January 2011 normal firmware is a **historically matched OEM reference** and has **not** undergone a qualified Linux 7 physical F2 test. The alternate AP/STA and manufacturing variants are *not* drop-in candidates for routine Wi-Fi bring-up.

### OEM calibration provenance: private, NON-interchangeable

- Archived HRI39 and HRI66 `bcm4329.cal` files are byte-identical, 1595 bytes each.
- Separately extracted later OEM reference calibration is 1594 bytes and **not** identical to the early one.
- Sanitized offline parse: 55 entries each, 54 unique parameter names, identical key order and set, **two value fields differ**, including at least one identity/regulatory field. No names of differing keys, private values, MACs, or raw files were emitted or committed.
- Neither file is automatically proven to belong to the currently attached replacement MZ600, even though it came from an original Motorola Android system. **Do not transplant identifiers or board calibration between tablets.** We need authenticated same-unit provenance before any meaningful RF/association test.

Tool: [`tools/forensics/compare_mz600_oem_firmware_private.py`](../../tools/forensics/compare_mz600_oem_firmware_private.py). Ran on Pi: early/later identity and structural calibration comparison PASS. Private input files remain outside public Git.

## 2. Hardware state verified live without touching power

Surface Book's original guarded USB host client `scripts/host/surface/Xoom-v34-BluetoothLiveLab.ps1` found one appropriate CDC serial interface, **COM9**, and accepted a **read-only** `MMC2_STATUS` followed by **read-only** `BT_STATUS` on October 24:

| Value | USB-reported evidence |
| --- | --- |
| CDC diagnostic protocol | `VERIFIED_V20_USB=COM9` |
| MMC2 | `TARGET VALID`; `BOUND YES`; `CARD BCM4329 VERIFIED` |
| MMC2 profile | `0` / AUTO |
| Driver modules | `DRIVER MODULES UNLOADED`, empty `/proc/modules` |
| Bluetooth state | `HCI_UART MODULE NOT LOADED`, `HCI0 ABSENT`, two USB status flags `0` |
| Linux 7 Wi-Fi status | Previous documented v033 `F2=-62`, `wlan0` absent; **not retried during this phase** |

The USB checks validate a current passive diagnostic state, **not** that every on-chip regulator is actually off. No GPIO/clock timing, PMU state or RF measurement can be inferred from status flags.

## 3. Motorola versus Linux 7: what the code already does

| Milestone | Motorola 2.6.36 source | Linux 7 equivalent / difference |
| --- | --- | --- |
| SDIO function 1 ALP request | `dhd_sdio.c:4946-4958` requests `FORCE_HW_CLKREQ_OFF | ALP_AVAIL_REQ` | `brcmfmac/sdio.c:3968-3983` same intent |
| Backplane ALP preparation | `siutils.c:147-176` waits ALP, forces ALP, delays 65 us, disables excess SDIO pull-ups | `brcmfmac/sdio.c:3845-3887` same intent |
| Core preparation | `siutils.c:274-281` disables ARM; `dhd_sdio.c:2452-2489` resets SOCRAM | `chip.c:1281-1302` disables CM3 and resets Wi-Fi D11 and SOCRAM; order/previous state merits closer scrutiny |
| Interrupt clear / CM3 reset release | `dhd_sdio.c:2508-2535` clears SDIO interrupt status before ARM core reset/release | `sdio.c:3890-3905` via `activate`, `chip.c:1304-1319` CM3 reset/release |
| F2 clock/mailbox/enable | `dhd_sdio.c:2723-2820` forces HT, writes SDPCM version, IOEx F1+F2, polls IORx | `sdio.c:4245-4270` forces HT, writes mailbox, `sdio_enable_func(F2)` polls IORx |
| PMU resource reload | `siutils.c:402-405` says **host skips PMU initialization; firmware handles it** | `sdio.c:4059-4069` sets `BCMA_CC_PMU_CTL_RES_RELOAD` (an added PMU reset/reload behavior, not complete PMU initialization) |
| ChipCommon GPIO pulls | `siutils.c:395-400` clears ChipCommon pull-up and pull-down regs when ccrev >= 20 | Equivalent whole-register clear not found in the inspected modern path; effect on rev3 remains unknown |

**Important:** Source-level equivalence of intent does not establish equivalent electrical history or working internal firmware. It is **incorrect to claim** that Linux 7 lacks early ALP preparation or interrupt clearing; both are present. It is likewise incorrect to call the two remaining differences the F2 root cause.

## 4. Required evidence for the next PMU/CM3 diagnostic probe

The present v034 USB runtime provides `MMC2_STATUS`, `BT_STATUS`, and `LOGS`, but no vetted readout for **ChipCommon GPIO pull controls, PMU control/status, SOCRAM state, CM3 wrapper reset state, and mailbox state at release time**. Existing GPIO/regulator observer results are steady-state software observations, not a synchronous snapshot across release.

Build a **reversible instrumented brcmfmac module**, without modifying the committed Linux kernel image, using the proven v026 staging/build style on a separate lab branch or worktree. It should preserve exact module ABI, original firmware and MAC-free NVRAM baseline in first test. Do not load it until offline review passes.

| Time boundary (use `ktime_get_ns`) | What to read / record | Safety / source anchor |
| --- | --- | --- |
| T0: after SDIO chip recognition, before PMU reload operation | chip ID/rev, ChipCommon revision, `pmucontrol`, `pmustatus` if supported, ChipCommon `gpiopullup/gpiopulldown`, `CHIPCLKCSR` | `sdio.c:3985-4069`; use actual `CORE_CC_REG` definitions; only documented non-destructive register reads; do not dump entire GPIO block |
| T1: immediately after existing PMU state-reload **write** | same PMU control/status values; capture errors | Observe current normal driver writes; **do not add new writes** |
| T2: immediately before firmware CPU release | SOCRAM up indicator, CM3 reset/control status where safe, ChipClkCSR, PMU status/control, confirmed firmware CRC and NVRAM metadata **not raw buffers** | `sdio.c:3385-3414` and `chip.c:1304`; verify access paths and read semantics |
| T3: after existing CM3 reset/release call | same status and timestamp, any read error | `chip.c:1314-1319`; no additional reset/power operations |
| T4: before Function 2 enable | existing SDPCM mailbox protocol write outcome, ChipClkCSR, IOEx/IORx | `sdio.c:4245-4268`; do not poll outside regular driver flow |
| T5: on F2 timeout only | existing IOEx/IORx, clock state, limited non-destructive PMU/CM3 status registers, kernel return code | `sdio.c:4268-4270` and failure branch; no fake IORx values |

### Observer safety rules

1. No writes to U4, U2, U0, I7, PMU, clock masks, silicon backplane, CPU reset, or regulator enable other than those performed by the **unchanged normal driver**. No device restart/flash; only vetted USB RAM-module load when permitted.
2. Read **only register addresses/pin semantics validated against the exact BCM4329 rev3 and active silicon-backplane core**; some registers may be clear-on-read or inaccessible while the core sleeps. Errors are data, never spin indefinitely.
3. Preserve firmware/NVRAM as current generic baseline until observer produces a meaningful trace; one independent variable per later test.
4. Emit restricted structured event lines with monotonic timestamps, explicit register name, masked/numeric values and return codes; prohibit MAC, serial, calibration bytes, addresses not needed for trace, or firmware content.
5. Instrumentation must not insert arbitrary sleeps or additional polling around CM3 release because that might itself repair/mask the problem.
6. Initial acceptance is **correct instrumentation and unchanged -62 outcome**, not functioning Wi-Fi. Stop on USB instability, errors, or unexpected device state.

### What can and cannot be decided today

- **Can decide:** original-MZ600 2011 driver/firmware lineage, matched source startup paths, last documented Linux F2 failure boundary, and the exact missing register measurements.
- **Cannot yet decide:** CPU firmware instruction execution, which PMU resources transition, whether `RES_RELOAD` changes resource sequencing on BCM4329 rev3, whether ChipCommon pull settings are causally important, whether U4 is truly power-cycled, or whether the January 2011 firmware would work under current Linux 7.

## Next deliverable

Prepare the v035 source-only observer against pinned Linux 7 with checked source hashes, compile it without replacing `main` or touching Xoom, and audit the emitted event fields. Only after offline qualification, do a bounded RAM-only baseline trace on replacement MZ600 using its already proven USB transport. Do not test original OEM firmware, modify PMU control, or change power sequencing until that measurement gives a falsifiable reason.

References: [v4 OEM-to-Linux 7 source audit](MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md), [v026 runtime provenance](../checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md), [v034 physical status](../checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md), [BCM4329 datasheet requirements](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md).
