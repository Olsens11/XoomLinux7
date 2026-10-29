> **LATER FORMAL WI-FI/PATCH AUDIT, 2026-10-28:** [Exact nine-patch checksum/style/physical Wi-Fi evidence](docs/checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md) and [internal bug ledger](docs/bugs/README.md). Prior SSID-inferred “5 GHz connection” is corrected: actual `iw` frequency **2462 MHz (2.4 GHz)** and 5 GHz Band 2 is absent. Working Wi-Fi/downloads are PASS, but Wi-Fi patches' full scan/regulatory/API behavior is not certified. See the time-scoped latest audit before further edits.

> **PHYSICAL STATE SNAPSHOT AS OF 2026-10-28 (READ BEFORE OLDER SNAPSHOTS):** [Live nine-review p10 Linux/COM9/Wi-Fi/LCD, touch capabilities, Bluetooth A/B, verified rollback and precise next gates](docs/ACTIVE_TEST_STATE.md). The [new dated OEM Recovery cross-reference + A/B firmware checkpoint](docs/checkpoints/MZ600_REVIEW9_P10_RECOVERY_SURFACE_OEM_BLUETOOTH_FIRMWARE_AB_2026-10-28.md) supersedes the older first BlueZ attempt's end-state. **Now**: Debian p10 online, Wi-Fi associated, native VT2 LCD PASS; Bluetooth HCI loaded using generic firmware but RF powered OFF and BlueZ service inactive, no Surface bond. No reboot/flash; p7/p8 fallbacks preserved. Treat older 'current' paragraphs below as historical test snapshots.

> **WIFI-01 R2 SOURCE QA (2026-10-28):** [Versioned four-member draft r2](patches/upstream/review-wifi-four-logical-20261028-r2/README.md) amends **existing WIFI-01**, not a fifth patch, to read optional Broadcom `per_chan_info` restrictions as normal path does. [Exact source/compile checkpoint](docs/checkpoints/MZ600_WIFI01_R2_PER_CHAN_RESTRICTION_SOURCE_QA_2026-10-28.md): 4/4 strict checkpatch PASS, modified ARM object and whole brcmfmac prefix PASS, other 3 stable patch-IDs unchanged. **This r2 has NOT been installed or tested on Xoom**; historical nine-review manifest and physical device remain unchanged. [Issue #4](https://github.com/Olsens11/XoomLinux7/issues/4) OPEN for real firmware/NO_IR testing.

> **GITHUB ISSUE TRACKER INITIALIZED — 2026-10-28:** [16 live development issues](https://github.com/Olsens11/XoomLinux7/issues), with a [dated issue-to-evidence index and maintenance rules](docs/ISSUE_TRACKER.md). Each finding is tagged in its title/body as observed, inherited, new source review risk, validation gap, or release gate. No issues filed upstream; development candidates intentionally unsigned.

> **ADDITIONAL DEEP UPSTREAM PROVENANCE REVIEW (2026-10-28):** [Current nine-patch source-vs-original problem classification](docs/checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md) and [internal source regulatory review risk](docs/bugs/WIFI-REVIEW-04-LEGACY-CHANNEL-REGULATORY-PARITY_2026-10-28.md). Upstream issue tracker has no filed items as of check, but original source already contained some compatibility limitations. Do not confuse unreported legacy limitations, newly reproduced symptoms, and regressions caused by our patches. No upstream submission or owner DCO until ready.

# START HERE — XoomLinux7

> **LATEST BLUETOOTH LAB MILESTONE — 2026-10-28:** [XoomLinux7 nine-review p10 BlueZ 5.66, 17,332-byte Motorola BCM4329B1 HCD installed and SHA-verified, simultaneous Wi-Fi+HCI powered PASS, BR/EDR inquiry corrected, exact Surface pairing failed status 0x04](docs/checkpoints/MZ600_REVIEW9_P10_BLUEZ_BCM4329B1_SURFACE_BLUETOOTH_PAIR_ATTEMPT_2026-10-28.md). **No pairing or BT input yet**. Firmware file in p10 but active HCI setup not rerun; BT safely OFF, Wi-Fi connected, COM9 available, Windows discovery restored OFF. No reboot or driver unbind while owner away. This checkpoint supersedes earlier Bluetooth status; private firmware and nearby device IDs are not in Git.

> **LATEST PHYSICAL MILESTONE — 2026-10-28: NINE-PATCH LINUX 7 + FULL BOOKWORM P10 BOOT PASS.** [First live exact-review kernel USB COM9 login proof, all 1GiB p10 Debian filesystem hashes and TWRP fsck, temporary fastboot boot only](docs/checkpoints/MZ600_NINE_REVIEW_LINUX7_P10_BOOKWORM_FIRST_PHYSICAL_BOOT_PASS_2026-10-28.md). The 1GiB new Debian filesystem is installed in **p10** (remaining p10 unexpanded); p7 original V31 and p8 working fallback **untouched**, p6 TWRP BigPart retained. Actual COM9 `xoom-mz600 login:` verified; **logged-in uname, new BigPart runtime geometry, Wi-Fi/BT/modules remain OPEN**. Older notes claiming nine-review Linux not booted or p10 empty are historical. Next use owner credential for serial login and run non-destructive runtime checks.


> **LATEST PHYSICAL MILESTONE — 2026-10-28:** [Original TWRP 2.8.6.0 BigPart successfully written to MZ600 p6 only, exact SHA readback and independent reboot into installed recovery PASS; eMMC p8/p9/p10 BigPart sector mapping and root ADB PASS, Debian p8 read-only ext4 mount PASS](docs/checkpoints/MZ600_TWRP_286_BIGPART_P6_INSTALL_AND_PERSISTENT_BOOT_PASS_2026-10-28.md). Old p6 rollback safely retained; clean nine-patch Linux and new Debian NOT installed. Next: disposable p8 cold-image restore/fsck rehearsal, then temporary nine-patch exact-source boot. Internal RW mounting/repair/backup-restore untested; recovery automatically mounts rescue SD RW, later remounted RO.


> **CURRENT COMPLETE CONTINUATION HANDOFF — 2026-10-28, SOURCE AND SURFACE COLD BACKUP VERIFIED:** [Full XoomLinux7 fastboot/Stage-B/cold p8 chapter, all exact source and Debian image hashes, nine-patch review architecture, BigPart TWRP 3.1.1-0, documented recovery experiments and ordered next steps](docs/handoffs/MZ600_XOOMLINUX7_FASTBOOT_COLD_P8_VERIFIED_HANDOFF_2026-10-28.md). **Real 1GiB cold backup exists on rescue SD AND Surface with SHA match; SD unmounted. Next do offline fsck/restore on disposable copy, then BigPart TWRP temporary test; no flash.** This supersedes older status labels but not project safety policies.

> **LATEST 2026-10-28 COLD P8 1GiB BACKUP VERIFIED ON SD AND SURFACE:** [Independent source hash and off-device Surface 1GiB hash match, all original backup reports preserved, SD safely unmounted](docs/checkpoints/MZ600_COLD_P8_OFFLINE_IMAGE_VERIFICATION_2026-10-28.md). Source p8 UNMOUNTED during capture. SHA256 `a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346`. **One 4KiB ext4 free-block accounting discrepancy in `e2fsck -fn`; original raw file intact; copy-only repair/restore exercise OPEN. NO flash.**

> **PRIOR 2026-10-28 HARDWARE FASTBOOT/SD ROOT AND COLD BACKUP STATUS:** [Direct hardware keys recovered fastboot; verified `fastboot boot` ran BigPart-aware Debian from rescue microSD; cold p8 capture progressed into SHA comparison; internal Debian returned, COM9/WLAN online. Final backup RESULT and hash still require independent read-only verification](docs/checkpoints/MZ600_STAGEB_FASTBOOT_COLD_P8_CAPTURE_PENDING_RESULT_2026-10-28.md). **No flash, no internal writes.**

> **HISTORICAL PHYSICAL RESULT 2026-10-28 10:44 EDT — TABLET UNREACHABLE (NOW RECOVERED):** [Controlled root-authorized temporary GPIO reset unbind physically succeeded; PMC-only reboot did not enter fastboot, did not return to Linux in host observation](docs/checkpoints/MZ600_GPIO_PMC_UNBIND_FASTBOOT_PHYSICAL_HANG_2026-10-28.md). Windows detected no COM9/fastboot, network ping false. **Stop remote reboot/flash; physical power/volume recovery required.** No eMMC write or cold p8 backup. Earlier read-only PASS notes below are historical pre-reboot results.

> **2026-10-28 LATEST LIVE XOOM READ-ONLY RESULT:** [Replacement MZ600 COM9 logged in as xoom, full BigPart geometry and both GPIO/PMC bindings confirmed; public one-shot test on /dev/shm RAM passed --preflight](docs/checkpoints/MZ600_REBOOT_GPIO_PMC_LIVE_UNPRIVILEGED_PREFLIGHT_PASS_2026-10-28.md). Root-only `unbind` remains blocked until authorized sudo; no second reboot or flash.

> **2026-10-28 REBOOT-TO-FASTBOOT INVESTIGATION:** [New source-proven restart priority conflict, guarded no-flash test ready](docs/checkpoints/MZ600_FASTBOOT_REBOOT_GPIO_PRIORITY_ROOT_CAUSE_CANDIDATE_2026-10-28.md). Xoom hardware GPIO reset (priority 200) runs before Tegra PMC reset (priority -128); mode preservation in a hardware-reset transition remains a hypothesis. No second reboot. Current COM9 awaits login, so the reversible test has not been run.

> **CURRENT STARTING POINT — 2026-10-28 INSTALLATION CHAPTER:** [Read the full MZ600 preinstallation engineering handoff first](docs/handoffs/MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md). This supersedes the outdated 2026-10-25 v06.3 and uninstalled BigPart status blocks below. The experimental MZ600 **already runs persistent Stage-D/V31 Debian on internal BigPart p8**, with eight reference captures and a clean, separately built nine-patch candidate plus 1GiB test root. The first no-button `reboot(2) bootloader` attempt **returned to normal Linux instead of fastboot**. Rescue microSD is **armed with a one-shot cold p8 backup service** (not yet run); the cold backup and safe TWRP 3.1.1-0 BigPart recovery are mandatory open gates. Never flash based solely on this notice.

> **Latest user decision — CLASSIC BIGPART on replacement MZ600**: enlarge traditional p8 `system` to **1GiB kernel-visible** as Debian Linux `/`, *not* use p10 as root. Data on p10 is disposable. [Active BigPart implementation plan](docs/plans/MZ600_V064_CLASSIC_BIGPART_SYSTEM_ROOT_IMPLEMENTATION_2026-10-25.md) supersedes previous p10 root proposal. Original BigPart manipulates the **kernel's in-memory GPT view**; do not blindly repartition eMMC with generic tools. Offline layout proof PASS; no actual partition write.


> **2026-10-25 new authorized storage direction:** [v06.4 internal Debian p10 root / optional BigPart plan](docs/plans/MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md). User accepts replacing Android on the **replacement** MZ600 and optional BigPart if necessary. No partition changes have occurred; current v06.3 physical baseline remains. Read handoff and the plan before proposing persistent writes.


> **CURRENT — October 25, 2026:** Replacement MZ600 runs **verified v06.3** (19:25 EDT read-only COM9 PONG). BCM4329B1 HCD firmware path/HCI up/down and subsequent Wi-Fi/wlan0 initialization and cleanup **physically PASS**. **No Wi-Fi RF scan or Bluetooth keyboard pairing yet; no real on-screen terminal.** Mandatory NEXT functional deliverable is [v06.4 build specification](docs/plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md), using the [comprehensive handoff](docs/handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md). Earlier Oct24 F2 -62 and v015/v020 guidance is *historical*, not the current clean v06.3 state.



This is the **session handoff**, not a historical narrative. Begin with [AGENTS.md](AGENTS.md).

1. Read [docs/status.md](docs/status.md) and [runtime/PROJECT_STATE.env](runtime/PROJECT_STATE.env).
2. Read [docs/README.md](docs/README.md) for the subsystem map.
3. Review [docs/checkpoints/README.md](docs/checkpoints/README.md) for last actual hardware results.
4. Check [docs/hardware/WIFI_BCM4329.md](docs/hardware/WIFI_BCM4329.md) if working on SDIO/F2.
5. Check [docs/architecture/UPSTREAM_POLICY.md](docs/architecture/UPSTREAM_POLICY.md) for source authority.
6. On each machine, run `scripts/resume-state.sh` then `python3 tools/check_repository.py` and inspect `git status --short`, `git branch -vv`, `git worktree list`.
7. Resolve current DUT identity, USB status, and user approval **before** any hardware command.

**HISTORICAL 2026-10-24 NEXT ACTION (SUPERSEDED by v06.3):** review [v018](docs/checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md) and [v019](docs/checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md) measured failures, then investigate BCM4329 firmware CPU/SDPCM startup and same-device OEM NVRAM provenance. v015 remains diagnostic baseline. No temporary OEM patch is an accepted Wi-Fi fix.

**Do not assume:** a kernel build is a boot test; an SDIO card is a functional wlan0; an embedded firmware file is legally redistributable; a branch has write access because a public clone succeeded.

Historical original source: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Our maintainable integration lives here.

## Historical 2026-10-24 diagnostic baseline (superseded by clean v06.3)
v020 supports no-reboot MMC2_STATUS, MMC2_PROFILE AUTO or MOTOROLA, MMC2_REINIT and MMC2_BIND recovery control. Physical AUTO/MOTOROLA/AUTO card re-enumeration and loaded-module safety guard PASS; native Wi-Fi F2 -62 persists. Start with docs/checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md before further experiments. Keep v015 as USB fallback, and never touch mmc0 or mmc1.

- [Offline virtual forensic lab](tools/forensics/README.md): single-command v025 provenance audit without connecting to the physical Xoom.

- [Broadcom BCM4329 full datasheet review](docs/research/BCM4329_DATASHEET_PAGE_INDEX.md): all 149 pages indexed; follow the requirement audit and cross-subsystem fault tree before changing Wi-Fi initialization.

- [Shared BCM4329 physical-chip ownership design](docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md) and offline tests: Motorola already coordinated both radios through shared U4, whereas Linux 7 currently does not.

- v028/v029 milestone: [GPIO controller proof](docs/checkpoints/V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md) and [compile-only shared-chip coordinator](docs/checkpoints/V029_BCM4329_SHARED_OWNER_COMPILE_ONLY_2026-10-24.md). The coordinator is NOT deployed or linked to MMC/BT consumers.

- **v030 Motorola Bluetooth shared-U4 experiment:** compile-only, not deployed. See [checkpoint](docs/checkpoints/V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md); 21 static contracts and isolated ARM compilation pass. No chip regulator or Bluetooth pin changed.

- **v031/v032:** [Physical BT serdev and clock reference test](docs/checkpoints/V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) proved Bluetooth child registered but unbound, and the nominal BT txco is actually the same 32k clock as WLAN LPO. [v032 disabled LPO-correct preview](docs/checkpoints/V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md) passes 12 checks; no new hardware driver loaded.

- v033 RAM-only Bluetooth USB lab: read docs/checkpoints/V033_BLUETOOTH_USB_LAB_2026-10-24.md. Six linked Bluetooth dependencies, USB BT commands only on demand, exact v025 kernel preserved and 25 MHz MMC2.

- v033 physically proven BT shared-U4 ON/OFF vote and BCM4329B1 identification, but F2 still -62 and the USB HCIDEVDOWN path passes the wrong ioctl argument type. Read docs/checkpoints/V033_BLUETOOTH_PHYSICAL_2026-10-24.md before another BT power experiment.

- v034 HCI ioctl correction physically tested: see docs/checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md. Previous v033 HCIDEVDOWN -19 was caused by the pointer instead of integer device index; v034 returns 0. Complete BT module unload and U4 vote release verified; WLAN F2 unresolved.
