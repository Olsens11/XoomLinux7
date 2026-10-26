# Documentation router

> **2026-10-26 latest Stage-E preparation:** [On currently working Stage-D internal-root Debian, original `/etc/fstab` backed up and corrected to live GPT p8 PARTUUID with complete one-line-only readback proof](checkpoints/MZ600_V064_STAGE_E_FSTAB_LIVE_P8_GUID_CORRECTED_2026-10-26.md). Stage-E internal p8 PARTUUID candidate remains TEMP-boot-only, not tested or flashed. Persistent p7 microSD Debian rescue intact.


> **2026-10-26 native internal Debian breakthrough:** [Stage-D temporary `fastboot boot` produces actual Debian 12.15 running from `/dev/mmcblk0p8 ext4 /`, verified by USB login and `findmnt`](checkpoints/MZ600_V064_STAGE_D_INTERNAL_P8_DEVNODE_BOOT_PHYSICAL_PASS_2026-10-26.md). Current root on internal eMMC p8 while p7 persistent Debian SD fallback remains intact. Old saved PARTUUID mismatched current kernel GPT; Stage-E with verified live PARTUUID prepared offline, NOT booted/flash. Next fix internal `/etc/fstab` after owner sudo, then test Stage-E TEMP only.


> **CURRENT SAFETY HOLD 2026-10-26:** [Stage-C internal BigPart p8 root temporary boot accepted by fastboot but did not reach usable Debian login; COM9 became unresponsive](checkpoints/MZ600_V064_STAGE_C_INTERNAL_P8_TEMPBOOT_NO_LOGIN_2026-10-26.md). Persistent p7 Debian microSD rescue remains flashed and verified; owner can recover by physical reset and normal boot with card inserted. Do not permanently flash Stage-C until root mount verified.


> **2026-10-26 NEW INTERNAL DEBIAN MILESTONE:** [BigPart internal p8 1GiB Debian root installed from microSD with correct internal fstab, ext4 offline fsck exit0; **internal root has NOT yet booted**](checkpoints/MZ600_V064_BIGPART_INTERNAL_DEBIAN_P8_FILESYSTEM_INSTALLED_FSCK_PASS_2026-10-26.md). Owner-repaired physical volume button permits fastboot/recovery. Next test Stage-C by temporary `fastboot boot`, and separately repair kernel/modules release/vermagic mismatch. Keep verified p7 microSD recovery boot.


> **2026-10-26 HARDWARE UPDATE:** [Experimental replacement MZ600 charging jack and volume button have been repaired; physical fastboot and recovery access confirmed by owner](checkpoints/MZ600_REPLACEMENT_HARDWARE_REPAIR_VERIFIED_BY_OWNER_2026-10-26.md). Historical notes saying the buttons are broken are obsolete. Independent software `reboot bootloader` still needs separate work; persistent Debian-on-SD boot and p7 readback pass remain valid.


> **2026-10-26 confirmed milestone:** [Persistent Linux7 Debian SD-root boot accepted, ordinary boot tested, then on-device p7 readback SHA verified exact Stage-B image match](checkpoints/MZ600_V064_PERSISTENT_P7_PHYSICAL_READBACK_SHA_PASS_2026-10-26.md). Current replacement tablet running persistent Debian from SD; p8 BigPart 1GiB still unformatted. Next: verify Android-independent recovery before destructive internal install.


> **2026-10-26 milestone:** [Persistent p7 Stage-B Linux7 Debian microSD boot successfully flashes and boots with normal fastboot reboot, normal Debian USB console](checkpoints/MZ600_V064_PERSISTENT_SD_DEBIAN_BOOT_PHYSICAL_PASS_2026-10-26.md). Current Debian on inserted SD. Independent read-after-write hash of p7 needs owner's local `sudo -s`; do not erase p8 before confirming and testing recovery.


> **SAFETY HOLD (2026-10-26):** [Independent Linux-to-fastboot reboot did not work; first persistent p7 boot flash status is unknown after native stderr/PowerShell interruption](checkpoints/MZ600_LINUX7_RESCUE_BOOTLOADER_AND_P7_FLASH_AMBIGUITY_2026-10-26.md). Xoom safely temporarily rebooted into Debian from SD. First verify raw p7 read-only SHA before any retry or p8 formatting.


> **LATEST 2026-10-26:** [Real Debian 12.15 microSD-root successfully boots with Linux 7 Classic BigPart 1GiB p8 and guarded installer passes complete read-only preflight](checkpoints/MZ600_V064_BIGPART_DEBIAN_SDRoot_PHYSICAL_PASS_INSTALL_PREFLIGHT_2026-10-26.md). Current live device stage-B Debian on SD, no partition/boot flash yet. Stage C p8-root boot prepared offline but NOT booted. Next: secure owner sudo in USB console and validate recovery independent of Android before erasing p8.


**LATEST offline candidate:** [BigPart-aware Debian microSD-root stage-B boot image hash-verified across Desktop and Surface](checkpoints/MZ600_V064_BIGPART_DEBIAN_MICROSD_INSTALLER_STAGE_B_OFFLINE_2026-10-25.md). Needs reinserted same 32GB installed Debian microSD for physical normal shell test; no format or flash.


**LATEST:** [Physical v064 original Xoom BigPart geometry PASS](checkpoints/MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md), replacement MZ600 now runs temporary BigPart-aware Linux7; stock TWRP remains 256MiB system view. No persistent writes yet.


> **NEW CURRENT LIVE PHYSICAL STATE (Oct25 20:47 EDT):** [Relocated OEM GPT physically verified from TWRP via 64-bit ARM read-only probe](checkpoints/MZ600_BIGPART_TWRP_PHYSICAL_GPT_LLSEEK_PROOF_2026-10-25.md). Current device is TWRP 3.1.1-0/root ADB, not v06.3 Linux. [Stage-A isolated BigPart kernel builder](../scripts/experiments/stage-v064-bigpart-gpt-readonly-20261025.py) running on Desktop. No BigPart partition writes.


> **Current approved storage target — CLASSIC XOOM BIGPART p8 `system` Linux root:** [implementation + hardware safety gates](plans/MZ600_V064_CLASSIC_BIGPART_SYSTEM_ROOT_IMPLEMENTATION_2026-10-25.md). The earlier p10-root proposal is superseded; no userdata backup is required by user's explicit decision. Host layout proof PASS only; no eMMC changes or boot image yet.


> **NEW storage design decision:** [2026-10-25 internal eMMC p10 Debian root / optional BigPart plan](plans/MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md). User accepts replacing Android on experimental replacement MZ600 if needed, but no partition has been modified. p10 is large enough without BigPart, pending backup and Linux7 native TegraPT visibility.


> **New v06.4 engineering checkpoint:** [offline ARMHF dependency-closure and packing preflight](checkpoints/MZ600_V064_ARMHF_PACKAGING_PREFLIGHT_OFFLINE_2026-10-25.md). The preflight script ran on Desktop WSL; no new image or physical feature pass yet.


> **CURRENT project authority — Oct 25, 2026:** [Comprehensive v06.3 physical-results handoff](handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md), [dated v06.3 hardware PASS](checkpoints/MZ600_V063_PHYSICAL_PASS_HCD_HCI_AND_BLUETOOTH_TO_WIFI_2026-10-25.md), [canonical current machine state](../runtime/CURRENT_LINUX7_STATE.env) and [v06.4 mandatory functional build instructions](plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md). **v06.3 is PHYSICALLY booted and HCD/HCI and sequential Wi-Fi validated; iw is only OFFLINE-STAGED; no actual scan, keyboard pairing, or usable terminal.** Older v015/v020/F2 evidence is historical.



**Canonical CURRENT authority:** [complete handoff](handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md) + [unique-key live state](../runtime/CURRENT_LINUX7_STATE.env) + [human-readable status](status.md); [legacy historical ledger](../runtime/PROJECT_STATE.env) retains older trial values and is not an unqualified current-state reference.

## Project and decisions
- [Project purpose and goals](PROJECT_INTENT.md)
- [Roadmap](roadmap.md)
- [Architecture and upstream provenance](architecture/UPSTREAM_POLICY.md)
- [Board platform and separation of concerns](architecture/PLATFORM.md)
- [Decision log](adr/README.md)

## Engineering / hardware
- [BCM4329 Wi-Fi, SDIO F2 fault and v014 plan](hardware/WIFI_BCM4329.md)
- [Target devices and preservation](hardware/DEVICES.md)
- [Native diagnostics and USB command interface](hardware/USB_DIAGNOSTICS.md)
- [Build, stage and temporary boot](process/DEVELOPMENT_WORKFLOW.md)
- [Source/artifact location map](reference/SOURCE_MAP.md)
- [Git worktrees and machine write keys](process/WORKTREES_AND_KEYS.md)

## Evidence and continuity
- [Chronological v01–v14 checkpoint index](checkpoints/README.md)
- [Verified device GitHub write access (2026-10-24)](checkpoints/GIT_ACCESS_2026-10-24.md)
- [Documentation authority and supersession rules](process/DOCUMENTATION_AUTHORITY.md)
- [Evidence and publishing rules](process/EVIDENCE_AND_PRIVACY.md)
- [Current state](status.md)
- [Machine-readable current state](../runtime/PROJECT_STATE.env)

When a new record is added, link it here and from its local index; update status ONLY when verified evidence changes.

- [v014 USB module hardware test and binary transfer fault](checkpoints/V014_USB_LAB_2026-10-24.md)

- [v015 physical raw USB and module hot-reload qualification](checkpoints/V015_RAW_USB_LAB_2026-10-24.md)

## BCM4329 current research
- [Motorola and Broadcom source comparison](research/MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md)
- [Controlled F2 experimental test matrix](research/BCM4329_F2_TEST_MATRIX.md)
- [v016 physical IOEx/IORx/clock snapshot](checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md)

- [v017 measured raw CCCR and parsed capabilities](checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md)

- [v018 complete Motorola six-field override: effective, but F2 still fails](checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md)

- [v019 25 MHz SDMMC2 control: actual host rate confirmed; F2 still fails](checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md)

- [On-demand SDMMC2 capability profiles and safe re-enumeration design](architecture/MMC2_ON_DEMAND_DESIGN.md) — proposed, not yet implemented.
- [Supplementary v018 recheck and actual host-clock discrepancy](checkpoints/V018_RECHECK_2026-10-24.md).

- [v020 physical no-reboot MMC2 capability profile acceptance](checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md).

- [v020 additional 6,662,144-byte hardware image and repeat MMC2 on-demand test](checkpoints/V020_ADDITIONAL_BUILD_AND_REINIT_2026-10-24.md).

- [v021 OEM firmware A/B and LPO/clock hypothesis](checkpoints/V021_OEM_FW_AND_LPO_HYPOTHESIS_2026-10-24.md): three physical F2 trials all -62; read-only clock observer built but not loaded.

- [BCM4329 full datasheet and Section 11 review](research/BCM4329_DATASHEET_SECTION11_REVIEW_2026-10-24.md): legacy SDIO clock <=25MHz, VDDC settled+110ms, pull-ups, SPI-vs-SDIO distinction.

- [v022 actual 25 MHz legacy SDIO three-trial physical result](checkpoints/V022_AUTO_LEGACY_25MHZ_PHYSICAL_2026-10-24.md): specification met, F2 still -62.

- [v021 actual LPO clock-provider measurement](checkpoints/V021_LPO_CLOCK_PHYSICAL_2026-10-24.md): software enabled 32768Hz; F2 -62 persists.

- [v025 verified 100 ms host pre-reset delay — 3 physical F2 trials](checkpoints/V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md).

- [Virtual Linux 7 forensic lab v1](research/VIRTUAL_FORENSIC_LAB_V1_2026-10-24.md): actual v025 image, two ARM/QEMU consumers, firmware/NVRAM audit, seven negative tests.

- [v026 actual runtime firmware and NVRAM provenance hardware test](checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md): generic source selection, CRC32 match, unavailable platform MAC, F2 still -62.

- [Broadcom BCM4329 complete 149-page datasheet index](research/BCM4329_DATASHEET_PAGE_INDEX.md), [36-requirement source and physical audit](research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md), and [cross-subsystem fault tree](research/BCM4329_CROSS_SUBSYSTEM_FAULT_TREE.md).

- [BCM4329 whole-chip power coordinator design](research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md): OEM shared power reference counts, two Linux consumers, resource ownership and rollback.

- [v028 read-only Bluetooth/WLAN controller register test](checkpoints/V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md) and [v029 disabled whole-chip coordinator compiled prototype](checkpoints/V029_BCM4329_SHARED_OWNER_COMPILE_ONLY_2026-10-24.md).

- [v030 Motorola Bluetooth shared-regulator and passive-reset compile-only work](checkpoints/V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md), with source patch and private DT test.

- [v031 live UART/BT binding and clock provenance](checkpoints/V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) and [v032 corrected Bluetooth LPO description](checkpoints/V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md).

- v033 Bluetooth USB-controlled temporary boot candidate: see checkpoints/V033_BLUETOOTH_USB_LAB_2026-10-24.md.

- v034 physical HCI device-down correction: checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md; v033 kernel, DTB, BT/Wi-Fi modules frozen.

- [Original MZ600 HRI39/HRI66 Wi-Fi driver and OEM-to-Linux 7 F2 audit](research/MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md) — matching-generation 2.6.36 OEM source compared against pinned Linux 7 CM3/PMU/clock/F2 startup; 27/27 offline source and ELF checks, no hardware modification.

- [BCM4329 OEM v5 firmware/PMU evidence](research/MZ600_BCM4329_V5_FIRMWARE_PMU_CM3_EVIDENCE_PLAN.md): tested read-only firmware version metadata, protected calibration differences, current USB state and next Cortex-M3/PMU observation gates.

- [v035 BCM4329 PMU/CM3/F2 read-only physical test](checkpoints/V035_BCM4329_PMU_CM3_F2_PHYSICAL_2026-10-24.md): 3 RAM-module trials established a chip PMUControl transition after CM3 release on first load and stable retained PMUControl on warm driver reloads; F2 remains -62.

- [v036 BCM4329B1 PMU resource physical checkpoint](checkpoints/V036_BCM4329_PMU_RESOURCE_CLOCK_PHYSICAL_2026-10-24.md) — OEM-specific resource-state decoding confirms ALP/HT and regulator/PLL resource votes, no pending, yet F2 remains -62 in two trials.

- [v037 SDPCM mailbox verified before persistent F2 timeout](checkpoints/V037_SDPCM_MAILBOX_WRITE_PHYSICAL_2026-10-24.md) — v4 firmware mailbox SDIO write rc=0, now focus on internal WLAN CPU firmware readiness and RAM handoff.

- [v038 on-chip ARM release and NVRAM token physically proven](checkpoints/V038_BCM4329_CM3_NVRAM_HANDOFF_PHYSICAL_2026-10-24.md); [v039 2011 Motorola firmware single-variable physical test](checkpoints/V039_ORIGINAL_MZ600_FIRMWARE_PHYSICAL_2026-10-24.md) also fails F2 and verified generic firmware rollback. Research branch only.

- [v040 authoritative Motorola MAC bootstrap and protected per-device provenance](research/V040_MOTOROLA_MAC_BOOTSTRAP_ATAG_PROVENANCE.md): candidate missing `macaddr` requirement, OEM bootloader ATAG MAC, current Linux ATAG kernel configuration; lab NVRAM override refused by host guard and not physically tested.

- [v038 MMC2 runtime-PM awake result](checkpoints/V038_MMC2_RUNTIME_PM_HOLD_PHYSICAL_2026-10-24.md) / [v039 original MZ600 firmware result](checkpoints/V039_ORIGINAL_MZ600_FW_PHYSICAL_2026-10-24.md) — two additional controlled, reversible, physically verified negative F2 results and exact generic firmware rollback.

- [BCM4329 supply transient / buffering research](research/MZ600_BCM4329_STARTUP_RAIL_DROOP_AUDIT_2026-10-24.md) — distinguish real 3.3 V, CPCAP VWLAN1 and internal 1.25 V from DTS regulators, plan scoped transient measurement before choosing decoupling additions; no physical experiment yet.

- [v040/v041 CM3 and SDPCM shared-header physical test](checkpoints/V040_V041_CM3_NVRAM_SHARED_STRUCTURE_PHYSICAL_2026-10-24.md) — firmware runs far enough to publish a version-3 shared header and console pointer, while F2 still times out.

- [v042–v045 first native BCM4329 wlan0 physically demonstrated](checkpoints/V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md) — recovered firmware console initialization error 21, proved stock bootstrap MAC unblocks F2, linked upstream WCC for experimental wlan0, safe identity-free rollback verified.

- [Native MZ600 installed-OS workstream](os/NATIVE_OS_INTEGRATION_2026-10-24.md) — staged Debian Bookworm armhf rootfs, clean kernel and factory-MAC ATAG→FDT patch, USB ttyGS0 login, standard upstream brcmfmac/WCC modules; **not flashed or hardware-verified yet**. See dedicated `os/mz600-native-rootfs-wifi-20261024` branch.

- [Native installed-OS offline build PASS checkpoint](checkpoints/NATIVE_OS_OFFLINE_BUILD_PASS_2026-10-24.md) — exact images/hashes/QA and no-flash boundary. [Future xoom-linux upstream handoff draft](os/UPSTREAM_CONTRIBUTION_DRAFT.md) (not sent).

- **[Start here: BCM4329 native WLAN breakthrough and comprehensive milestone](checkpoints/BCM4329_BREAKTHROUGH_AND_NATIVE_OS_MILESTONE_2026-10-24.md)** — definitive history, evidence, physical WLAN0 proof, current safe state, clean OS and Android-preservation decisions.
- [Android-preserving Linux root and boot artifacts — offline PASS](checkpoints/ANDROID_PRESERVING_NATIVE_OS_OFFLINE_REBUILD_2026-10-24.md) — `xoom-linux` dedicated root target, SHA-reverified images, no device writes, reversible Android requirement.

- [Native Linux installation preflight and Android rollback backups (2026-10-25)](checkpoints/NATIVE_OS_INSTALL_RECOVERY_PREFLIGHT_2026-10-25.md) — real 10-partition eMMC map, private off-device images, TegraPT warning; staged Linux remains uninstalled.

- [MicroSD Linux root target — physical media inspection and verified offline build](checkpoints/MICROSD_ROOT_OFFLINE_PREFLIGHT_2026-10-25.md) — microSD detected as independent mmcblk1; no writes or Android modification. Root ext4 installation requires media erase approval.

- **[MicroSD native Debian installation succeeded; first boot not yet qualified](checkpoints/MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md)** — complete physical SD layout and integrity, bootloader temp boot evidence, no Android flash, USB/boot remains unresolved.

- **[New milestone: real Debian 12 boots on MZ600 microSD with USB console and native BCM4329 wlan0](checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md)** — systemd, verified factory-MAC FDT/interface match, separate WCC module; no RF association yet.
