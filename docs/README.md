# Documentation router

**Canonical current authority:** [status.md](status.md) + [../runtime/PROJECT_STATE.env](../runtime/PROJECT_STATE.env). Historical records remain immutable and may describe older states.

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
