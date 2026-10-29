- **[2026-10-29 WIFI-01 r5 source-backed regulatory lifecycle and full nine-member ARM/ABI QA](../checkpoints/MZ600_WIFI01_R5_REGULATORY_LIFECYCLE_NINE_BUILD_QA_2026-10-29.md)** — Exact pinned core.c/reg.c registration-before-query, accepted-country recomputation-before-notifier, custom-99 CORE exception, no immutable country channel freeze; r5 preserves orig_flags and aborts nonunsupported metadata errors. Full ARM zImage/DTBs/modules PASS, original 259/259 CRC and WCC identity; passive unknown 5GHz still required and notifier skip behavior remains open. No physical release.

- **[2026-10-29 native firmware-error r4 source / complete nine-member ARM QA](../checkpoints/MZ600_WIFI01_R4_NATIVE_FWERR_FULL_NINE_BUILD_QA_2026-10-29.md)** — r3's `-EBADE` inference replaced in existing WIFI-01 with per-call true BCME status; full ARM zImage+DTBs+modules PASS, original module 259/259 imported CRC same, 7/7 offline error fixtures. Review-only, no hardware changes. Provisional 5GHz NO_IR and dynamic firmware-country channel refresh still require regulator parity review before any release.

- **[2026-10-29 OEM May2012 country-iovar one-variable comparison and independent rollback](../checkpoints/MZ600_OEM2012_FIRMWARE_COUNTRY_US_REV0_DUAL_BAND_RAM_TEST_ROLLBACK_PASS_2026-10-29.md)** — OEM binary 4.218.248.44 with **unchanged installed NVRAM** also returns **US/US/rev0**, yet exposes 2.4+5GHz. Generic binary on same NVRAM returns US/0 but only 2.4GHz. Supports firmware compatibility—not a forced US69 setting—as priority for WIFI-01; no RF scan/regulatory writes, original Wi-Fi restored, standalone postflight PASS.

- **[2026-10-29 first physically verified generic BCM4329 firmware-country readback and rollback](../checkpoints/MZ600_COUNTRY_IOVAR_US_REV0_PHYSICAL_ROLLBACK_PASS_2026-10-29.md)** — current generic firmware reports **US/US/rev0**, compared with original MZ600 factory calibration US/69; no country SET, source-only diagnostic temporarily loaded only in RAM, original Wi-Fi/module hashes and independent postflight PASS. The earlier generic+OEM-US69 NVRAM test still stayed 2.4GHz, whereas May2012 OEM firmware-only A/B exposed dual band with unchanged NVRAM. Do not claim this rev mismatch causes missing 5GHz.

- **[2026-10-29 selected design: OEM firmware/calibration + native brcmfmac country mapping + bounded BCM4329 channel fallback](../plans/MZ600_BCM4329_OEM_COMPATIBILITY_BOUNDARY_SELECTED_DESIGN_2026-10-29.md)** — accepted design direction, not a signed patch or hardware acceptance. Source-audited the early same-country/revision mismatch and dynamic current-country channel list; read-only country firmware query remains pending after a pre-stage COM9 timeout. New 14-assertion source checker PASS; canonical WIFI-01 r3 unchanged pending minimal revision.

- **[2026-10-29 PHY section re-review and country-source separation](MZ600_BCM4329_PHY_FIRMWARE_REGULATORY_BOUNDARY_2026-10-29.md)** — original 149-page BCM4329 datasheet index pages 42–46 (PHY calibration and internal TX power feedback), 106–115 (RF characterizations), 47/62–63 (embedded firmware interface). Confirmed internal silicon calibration does not supply missing Broadcom firmware channel metadata or legal transmit permission. Live Xoom has global US, custom phy6 99, no NVRAM ccode/regrev or DT country map; exact-nine *source-only* country-readback overlay cross-build/CRC PASS but **not installed**. WIFI-01 still open.

- **[2026-10-29 WIFI-01 OEM/upstream external precedents and smallest intent-preserving solution](MZ600_WIFI01_EXTERNAL_UPSTREAM_OEM_PRECEDENTS_2026-10-29.md)** — same-vendor Broadcom `bcmdhd` suppresses only native BCME_UNSUPPORTED for unsupported `chanspecs` and optional `per_chan_info`, while preserving band setup; Linux cfg80211 snapshots `orig_flags` at registration; mwifiex/ath9k demonstrate pre-registration hardware policy + later regulatory updates. `GET_VALID_CHANNELS` is a *current regulatory context* query, not a proven immutable hardware superset. Cross-vendor policy compatibility gate, source research ONLY, issue #4 remains OPEN.

- **[2026-10-29 actual firmware ABI discriminator (MZ600)](../checkpoints/MZ600_WIFI01_BCME_SIXFORMAT_NATIVE_UNSUPPORTED_PHYSICAL_PASS_2026-10-29.md)** — clean full nine+r3+lab ARM build, 259/259 CRC; six documented `per_chan_info` formats across ch11 and ch36 **all native BCME_UNSUPPORTED=-23**, not BADARG, transport0, no valid flags. Physically tested RAM-only with OEM2012 firmware; original connected Wi-Fi restored and independently postflight PASS. WIFI-01 regulatory fallback unresolved; r3 unsigned.

- **[2026-10-29 ABI follow-through and live baseline preflight](../checkpoints/MZ600_WIFI01_BCME_ABI_DIAGNOSTIC_SOURCE_AND_PREFLIGHT_2026-10-29.md)** — read-only p10/WLAN/COM9 SHA verification PASS, [bounded six-query raw-BCME source-only probe](../../tools/diagnostics/README-MZ600-WIFI01-BCME-ABI-20261029.md) cleanly applies to pinned r3 scratch source. ARM compile/physical A/B not performed.

- **[2026-10-29 WIFI-01 r3 firmware-error/IOCTL ABI source audit](MZ600_WIFI01_R3_FWERR_COLLAPSE_AND_IOCTL_ABI_SOURCE_AUDIT_2026-10-29.md)** — pinned `fwil.c` collapses distinct native BCME errors to `-EBADE`; r3 mislabels that as `per_chan_info` unsupported. Existing `fwil_fwerr` source precedent and legacy WLC_GET_VERSION conversion suggest a small, read-only, error-preserving diagnostic. Source-only; no kernel/hardware tests or new patch.

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

- [v031 runtime BT serdev/clock evidence](../checkpoints/V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) and [v032 clock-role correction](../checkpoints/V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md), supplementing the BCM4329 datasheet and OEM audit.

- [Original MZ600 HRI39/HRI66 driver recovery](MZ600_HRI39_HRI66_OEM_DRIVER_RECOVERY_2026-10-24.md) — verified 2.6.36.3 BCM4329 loadable module and matching-generation historical source, kept separate from later 2.6.39 BCMDHD.
- [MZ600 OEM versus Linux 7 Cortex-M3/PMU/SDIO F2 startup audit v4](MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md) — detailed source-equivalence matrix, two nonproven chip-setup differences, untested 261,317-byte early OEM firmware, and 27/27 independent read-only assertions. [Verifier](../../tools/forensics/audit_mz600_oem_f2_startup.py).

- [v5 original MZ600 firmware / PMU / Cortex-M3 evidence gates](MZ600_BCM4329_V5_FIRMWARE_PMU_CM3_EVIDENCE_PLAN.md) — January 2011 vs May 2012 firmware versions, private NVRAM structural comparison, live passive USB status and six-event read-only register capture design. [Privacy-preserving offline comparison utility](../../tools/forensics/compare_mz600_oem_firmware_private.py).

- [v035 physical PMU/CM3/F2 state-retention result](../checkpoints/V035_BCM4329_PMU_CM3_F2_PHYSICAL_2026-10-24.md) — measured 3-trial register/timing trace from the [v035 reversible observer builder](../../scripts/experiments/v035-build-readonly-pmu-cm3.py). This is new evidence after the v5 pre-test plan, not a Wi-Fi fix.

- [v036 Motorola-specific PMU resource decoding](../checkpoints/V036_BCM4329_PMU_RESOURCE_CLOCK_PHYSICAL_2026-10-24.md) — physical ChipCommon 29 / PMU 6 and resource mask 003FE63E decoded via OEM sbchipc.h. [Source-guarded v036 observer](../../scripts/experiments/v036-build-pmu-status-readonly.py); [source writer / clock audit](MZ600_V036_PMU_CLOCK_WRITER_SOURCE_AUDIT.md).

- [v037 firmware mailbox/write acknowledgment checkpoint](../checkpoints/V037_SDPCM_MAILBOX_WRITE_PHYSICAL_2026-10-24.md) — original OEM and Linux 7 both advertise SDPCM v4, live mailbox SDIO write rc=0. [v037 reversible source builder](../../scripts/experiments/v037-build-sdpcm-mailbox-status.py).

- [v038 CM3/NVRAM token physical investigation](../checkpoints/V038_BCM4329_CM3_NVRAM_HANDOFF_PHYSICAL_2026-10-24.md) and [reversible v038 builder](../../scripts/experiments/v038-build-cm3-nvram-handoff.py) — verified 288KiB RAM/CM3 core-up and end-of-RAM token, source-vs-runtime NVRAM provenance.
- [v039 one-variable original OEM 2011 firmware physical comparison](../checkpoints/V039_ORIGINAL_MZ600_FIRMWARE_PHYSICAL_2026-10-24.md) — both firmware images fail F2, baseline restored, remaining device-identity/regulatory provenance audit.

- [v040 Motorola default MAC bootstrap requirement, ATAG/OTP provenance and NVRAM safety gate](V040_MOTOROLA_MAC_BOOTSTRAP_ATAG_PROVENANCE.md) — actual OEM `dhd_common.c` requires a default MAC from OTP/NVRAM for firmware bring-up; later unit-specific ATAG callback confirmed in original binary; temporary test upload **rejected before device write** by existing identity/regulatory guard.

- [v038 host-awake test](../checkpoints/V038_MMC2_RUNTIME_PM_HOLD_PHYSICAL_2026-10-24.md) and [v039 authentic MZ600 firmware one-variable test](../checkpoints/V039_ORIGINAL_MZ600_FW_PHYSICAL_2026-10-24.md) — both safely physically exercised and **do not** resolve F2 -62; generic firmware restored afterward. [v038 source-guarded runtime-awake builder](../../scripts/experiments/v038-build-mmc2-runtime-awake.py).

- [MZ600 BCM4329 startup rail-droop and regulator-buffering audit](MZ600_BCM4329_STARTUP_RAIL_DROOP_AUDIT_2026-10-24.md) — verifies actual CPCAP VWLAN1 and switched 3.3 V paths, manufacturer 110 ms-after-VDDC-settled requirement, explains why software PMU snapshots do not exclude short droop, and provides a no-guesswork oscilloscope/capacitor decision gate. Research only, no electrical modifications.

- [v040/v041 firmware shared-state physical checkpoint](../checkpoints/V040_V041_CM3_NVRAM_SHARED_STRUCTURE_PHYSICAL_2026-10-24.md) — validated end-of-SOCRAM NVRAM token, Cortex-M3 release and version-3 SDPCM shared header with console and msgtrace pointers.

- [v042–v045 firmware console to successful WLAN0 milestone](../checkpoints/V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md) — exact SDPCM shared pointer/header, private firmware console err21, authentic Motorola bootstrap MAC single-variable proof of F2 and self-contained upstream WCC diagnostic; includes complete rollback. Reversible builder scripts [v042](../../scripts/experiments/v042-build-sdpcm-console-metadata.py), [v043](../../scripts/experiments/v043-build-private-console-sample.py), [v045](../../scripts/experiments/v045-build-inline-wcc-vops.py).

- **[Motorola MZ600 BCM4329 regulatory provenance and safe Linux 7 country plan (2026-10-25)](MZ600_BCM4329_REGULATORY_OEM_LINUX7_AUDIT_2026-10-25.md)** — factory HRI39/HRI66 `US/69`, live country 00/custom 99, actual 1–11 channel limits, BCM4329 country mapping source, verified upstream-signed Debian regulatory package staged on device but not installed; no RF activity.
