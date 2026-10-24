# MZ600 HRI39/HRI66 BCM4329 — OEM Cortex-M3 / PMU / SDIO F2 startup audit (v4)

**Date:** 2026-10-24  
**Status:** Source, ELF and archived-image comparison; **no physical device changes**. Supersedes speculative statements in earlier v3 where source-to-build attribution was unclear.  
**Goal:** Linux 7 native BCM4329 Wi-Fi on the replacement Motorola MZ600. Bluetooth/FM are coordinated chip-resource consumers, not separate release blockers.

## Source and artifact authority

**Original early MZ600 build:** both HRI39 and HRI66 Android boot images contain kernel `2.6.36.3-g2a65edc`; both read-only ext4 system images have **identical** ARM EABI5 `/system/lib/modules/bcm4329.ko`, 264,038 bytes, SHA256 `4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f`, `vermagic 2.6.36.3-g2a65edc SMP preempt mod_unload ARMv7`. The module is **not stripped**; its symbol table confirms `wifi_probe`, `dhd_bus_start`, `dhd_bus_init`, `dhdsdio_download_state`, `dhdsdio_htclk`, `si_doattach`, and `dhd_module_init`.

**Matching-generation source:** [Motorola Tegra `2a65edc`](https://android.googlesource.com/kernel/tegra/+/2a65edc/). The original module's compiler debug path references `android-tegra-moto-2.6.36/tegra-moto/drivers/net/wireless/bcm4329/`; this is a strong source-lineage match **not a bit-for-bit reproduced build**. No claim that historical build flags are identical without compiled conditional verification.

**Modern source authority:** [`xoom-linux/linux` pinned commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`](https://github.com/xoom-linux/linux/tree/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3). The retrieved modern `sdio.c` SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab` matches the previously documented v026 original source hash. Modern `chip.c` SHA256 `932e25c75f9ea5247194dfdb78c6b41a457af68d7a558935a7b5489bf548aa9d`. The prior tested diagnostic image is **v034**; matching upstream text with a previously pinned source does not by itself independently reproduce the v034 binary.

**Private OEM files:** `/home/ps2/xoom-phase1/private/oem-reference-20261021/analysis/oem-driver-study/` on Raspberry Pi. Recovered `fw_bcm4329.bin` is **261,317 bytes**, different from the Linux 7 generic **253,748 bytes** and the later OEM `fw_bcmdhd.bin` **264,140 bytes** previously tried. Original `bcm4329.cal` and three firmware variants remain **PRIVATE**; do not publish their bytes, MAC, board calibration or proprietary patches. The 261,317-byte original early-MZ600 image has **not been qualified in a Linux 7 physical F2 test**.

## 1. Board-to-driver startup path, oldest pinned generation

| Phase | OEM `2a65edc` source | Evidence | Kernel 7 mapping |
| --- | --- | --- | --- |
| Module registration | [`dhd_linux.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_linux.c), approx. 2531–2595 | Customer power hook; with relevant conditionals registers `wifi_add_dev`, waits semaphore; then SDIO driver registration | Linux SDIO registration, platform regulators and MMC pwrseq; same *function* is spread across components |
| Platform probe | `dhd_linux.c` 126–143 | `wifi_set_power(1,0)` **before** `wifi_set_carddetect(1)` | Linux boots MMC controller, regulator and pwrseq based on DT/host discovery; runtime electrical equivalence unproven |
| Board power and reset | [`board-stingray-wifi.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray-wifi.c) 155–166 | `mdelay(100)`, shared `change_power_brcm_4329(on)`, `mdelay(100)`, U2 reset to `on`, `mdelay(200)` | U4 fixed regulator, U2 `mmc-pwrseq-simple`, host 100ms and pwrseq 300ms. **Software delays are not proof of equivalent chip power history** |
| OEM MMC discovery | `board-stingray-wifi.c` 106–152 | Logical card-detect and embedded six-value SDIO capability override | v018 physically reproduced override; still no F2 |
| Bus bring-up | [`dhd_sdio.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_sdio.c) ~4850–4910 | `dhdsdio_probe_attach`, `dhdsdio_probe_init`, `dhd_bus_start` | [Linux 7 `sdio.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c) ~3949–4055 and ~4448 |
| Firmware + bus | OEM `dhd_linux.c` 2176–2230, `dhd_sdio.c` 5615–5688 | `dhd_bus_download_firmware` followed by `dhd_bus_init` | `brcmf_sdio_firmware_callback` ~4208, `brcmf_sdio_download_firmware` ~3385 |
| F2 barrier | OEM `dhd_sdio.c` 2723–2820 | Force HT, send SDPCM mailbox data, IOEx F1/F2 and wait IORx; only then bus DATA | Linux 7 `sdio.c` ~4245–4275 invokes `sdio_enable_func(F2)`; physically returns -62 with IORx 0x02 |

## 2. Matching early clock and SDIO preparatory actions — **confirmed source equivalence, not a missing Linux feature**

A critical earlier suspicion was that modern brcmfmac did not perform Motorola's pre-attach ALP/PLL clock preparation. **The pinned code disproves that simple hypothesis.**

| OEM 2.6.36 | Modern Linux 7 | Comparison |
| --- | --- | --- |
| `dhdsdio_probe_attach` ~4946–4958 writes `DHD_INIT_CLKCTL1 = FORCE_HW_CLKREQ_OFF | ALP_AVAIL_REQ`; verifies register | `brcmf_sdio_probe_attach` ~3968–3983 writes `BRCMF_INIT_CLKCTL1` with the same intended flags; verifies readback | **Source equivalent** |
| `si_buscore_prep` in [`siutils.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/siutils.c) ~147–176: request ALP, wait available, force ALP, 65µs, clear SDIO extra pullups | `brcmf_sdio_buscoreprep` ~3845–3886: ALP request, wait, force, 65µs, clear SDIO pullups | **Source equivalent** (OEM applies an optional supported-register check) |
| OEM `dhdsdio_probe_attach` ~5054–5055 sets `CC_BPRESEN`: SDIO reset also resets backplane | Modern `brcmf_sdio_probe_attach` ~4048–4057 sets `SDIO_CCCR_BRCM_CARDCTRL_WLANRESET` | Same **design intent**; physical register equivalence/bit behavior on this revision should be checked rather than assumed |
| OEM `dhdsdio_download_state(FALSE)` ~2508–2524 clears SDIOD `intstatus` *before* ARM reset release | Modern `brcmf_sdio_buscore_activate` ~3890–3905 clears same interrupt status before modern `brcmf_chip_cm3_set_active` ~1304–1319 releases CM3 | **Source order and intent equivalent** |
| OEM `dhd_bus_init` forces `SBSDIO_FORCE_HT`, writes SDPCM mailbox and enables F2 | Linux 7 firmware callback ~4250–4268 does the same BCM4329-specific clock/mailbox/F2 operations | **Source equivalent up to readiness handshake** |

**Interpretation:** These matches are positive findings and should prevent redundant 'fixes'. Our F2 problem is not explained by the *absence* of these lines. It may still reflect different startup history, previous state, board inputs, firmware content or chip effect.

## 3. WLAN Cortex-M3 download/release equivalence and critical unknown

OEM `dhd_sdio.c` `dhdsdio_download_state(TRUE)` ~2452–2489: restrict to ALP; disable ARM7/CM3 core; reset SOCRAM; clear RAM tail 4 bytes. `_dhdsdio_download_firmware` ~5615–5688: download firmware, attempt NVRAM, then `dhdsdio_download_state(FALSE)`. Exit ~2491–2535: verify SOCRAM core up, write variables, clear SDIO interrupts, reset/release ARM, clear ALP-only flag. **The original source logs NVRAM load failure without immediate abort**; do not infer this made invalid NVRAM acceptable to the silicon.

Linux 7 `chip.c` `brcmf_chip_cm3_set_passive` ~1281–1302 disables CM3, resets 802.11 and internal memory; `sdio.c` `brcmf_sdio_download_firmware` ~3385–3424 writes firmware and packed NVRAM, calls `brcmf_chip_set_active`; `brcmf_chip_cm3_set_active` ~1304–1319 verifies SOCRAM up, clears interrupts via bus `activate`, resets/releases CM3 and returns `true`.

**Neither implementation here has a positive assertion proving on-chip firmware instructions ran**. Linux 7 v026 verifies request paths, firmware CRC and NVRAM pack; F2 IORx remains 0x02. The earliest observable lost transition is *after ARM reset release and before F2-ready*, not necessarily the precise first failed instruction.

**Unresolved differentiators:** reset history before `set_passive`, exact core reset-controller semantics, chip-specific RAM tail and NVRAM placement, boot vector semantics (CM3 uses resetcore without the CR4 resetvec), matched original firmware/calibration versions, and PMU/clock dependencies during firmware execution.

## 4. Two **real source differences** worth auditing, NOT yet diagnosed causes

### A. PMU control/register behavior

OEM [`siutils.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/siutils.c) ~395–405 explicitly **skips PMU initialization from the host** and says firmware handles it. At that point it reads chipcommon and PMU capabilities, then prepares the cores. Linux 7 [`sdio.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c) ~4059–4069 additionally sets `BCMA_CC_PMU_CTL_RES_RELOAD` in `pmucontrol`, intending a backplane reset to reload PMU state. This is **not the same as full host PMU programming**, and the presence of the write **does not prove that a reset occurs or that the bit changes F2 startup**. Compare exact initial/after values with a read-only probe before contemplating any write change.

### B. ChipCommon GPIO pull configuration

OEM `siutils.c` ~395–400 clears both ChipCommon `gpiopullup` and `gpiopulldown` when `ccrev>=20`. No corresponding broad register clear was found in the retrieved mainline `chip.c` or SDIO bring-up path. **Open:** which chipcommon pin group these registers govern on BCM4329 rev3, its actual `ccrev`, whether a reset/default already makes the effect equivalent, and whether clearing would inadvertently affect WLAN/BT/FM control. Do not insert an unconditional clear.

Both discrepancies concern *shared-chip setup*, exactly the class of cross-subsystem interactions being investigated. Prioritize reading their values, not experimenting with writes.

## 5. OEM-vs-Linux-F2 test interpretation

Live Linux 7 experiments through v033: F1 and firmware transfer work; `IOEx 0x02→0x06`, `IORx` remains `0x02`; `sdio_enable_func(F2)` returns `-62` after ~3 seconds; no `wlan0`. The OEM code requires the same F2-ready bits to progress. This **does not establish that the OEM firmware was actively executing in Linux 7**. v034 separately qualified corrected Bluetooth HCI shutdown and kept WLAN unchanged.

The **original HRI39/HRI66 261,317-byte WLAN firmware** is different from both the mainline 253,748-byte firmware and the later `fw_bcmdhd.bin` 264,140-byte trial firmware. This constitutes an **untested historical payload pairing**, not proof of a missing firmware fix. Any eventual test must preserve matched private calibration provenance, prohibit publishing per-unit MAC, and hold RF transmission until per-device identity and regulatory state are established.

## 6. Direct next verification gates

1. **Reproducible source/ELF provenance:** map symbol names and sections in the 264,038-byte OEM `bcm4329.ko` against pinned `2a65edc` source; retrieve exact early MZ600 kernel configuration, `Makefile` preprocessor flags and Android module load arguments. Binary-to-source equality is not yet claimed.
2. **Compile-config / conditionals:** prove which `CUSTOMER_HW2`, `CONFIG_WIFI_CONTROL_FUNC`, `DHD_DEBUG`, firmware path and interrupt options were active, using binary symbols and disassembly where possible; avoid treating conditional debug-only CIS reads as unconditional startup.
3. **Read-only chip event timeline:** start from actual U4/VDD, LPO, U2, CCCR, ChipClkCSR, PMUControl initial and post values, ChipCommon GPIO pulls, SOCRAM state, CM3 reset/clock state, SDPCM mailbox and F2 IORx. Use source-defined addresses and capture read errors as first-class results.
4. **One-variable firmware pairing plan:** compare early MZ600 actual `fw_bcm4329.bin` and same-device calibration semantics against current generic/later OEM choices in offline model first, without disclosing identities or booting modified firmware yet.
5. **Suspend/resume and Bluetooth vote ordering:** trace all users of OEM shared U4 counter, Wi-Fi platform remove/re-probe and radio suspend; actual chip POR must not be inferred from software vote release alone.
6. **Documented stop gate:** do not modify kernel power GPIO, PMU, clocks, firmware or image until the latest evidence table isolates a falsifiable change with reversible experiment/rollback. Protected recovery Xoom remains untouched.

## References

- [Original driver recovery and binary provenance](MZ600_HRI39_HRI66_OEM_DRIVER_RECOVERY_2026-10-24.md)
- [Prior whole-chip call graph](MOTOROLA_BCM4329_OEM_CALLGRAPH_TRACE_V3.md)
- [Current physical v034 result](../checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md)
- [Datasheet requirement matrix](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md)
- [F2 experiment protocol](BCM4329_F2_TEST_MATRIX.md)

**Truth labels:** source-equivalent = compared matching source intentions and order only; artifact-verified = extracted hash/ELF/source matching; chip effect remains unobserved. No permanent or RAM-only hardware experiment in this phase.
