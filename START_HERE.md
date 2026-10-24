# START HERE — XoomLinux7

This is the **session handoff**, not a historical narrative. Begin with [AGENTS.md](AGENTS.md).

1. Read [docs/status.md](docs/status.md) and [runtime/PROJECT_STATE.env](runtime/PROJECT_STATE.env).
2. Read [docs/README.md](docs/README.md) for the subsystem map.
3. Review [docs/checkpoints/README.md](docs/checkpoints/README.md) for last actual hardware results.
4. Check [docs/hardware/WIFI_BCM4329.md](docs/hardware/WIFI_BCM4329.md) if working on SDIO/F2.
5. Check [docs/architecture/UPSTREAM_POLICY.md](docs/architecture/UPSTREAM_POLICY.md) for source authority.
6. On each machine, run `scripts/resume-state.sh` then `python3 tools/check_repository.py` and inspect `git status --short`, `git branch -vv`, `git worktree list`.
7. Resolve current DUT identity, USB status, and user approval **before** any hardware command.

**Current next action:** review [v018](docs/checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md) and [v019](docs/checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md) measured failures, then investigate BCM4329 firmware CPU/SDPCM startup and same-device OEM NVRAM provenance. v015 remains diagnostic baseline. No temporary OEM patch is an accepted Wi-Fi fix.

**Do not assume:** a kernel build is a boot test; an SDIO card is a functional wlan0; an embedded firmware file is legally redistributable; a branch has write access because a public clone succeeded.

Historical original source: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Our maintainable integration lives here.

## Current 2026-10-24 diagnostic baseline
v020 supports no-reboot MMC2_STATUS, MMC2_PROFILE AUTO or MOTOROLA, MMC2_REINIT and MMC2_BIND recovery control. Physical AUTO/MOTOROLA/AUTO card re-enumeration and loaded-module safety guard PASS; native Wi-Fi F2 -62 persists. Start with docs/checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md before further experiments. Keep v015 as USB fallback, and never touch mmc0 or mmc1.

- [Offline virtual forensic lab](tools/forensics/README.md): single-command v025 provenance audit without connecting to the physical Xoom.

- [Broadcom BCM4329 full datasheet review](docs/research/BCM4329_DATASHEET_PAGE_INDEX.md): all 149 pages indexed; follow the requirement audit and cross-subsystem fault tree before changing Wi-Fi initialization.

- [Shared BCM4329 physical-chip ownership design](docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md) and offline tests: Motorola already coordinated both radios through shared U4, whereas Linux 7 currently does not.

- v028/v029 milestone: [GPIO controller proof](docs/checkpoints/V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md) and [compile-only shared-chip coordinator](docs/checkpoints/V029_BCM4329_SHARED_OWNER_COMPILE_ONLY_2026-10-24.md). The coordinator is NOT deployed or linked to MMC/BT consumers.

- **v030 Motorola Bluetooth shared-U4 experiment:** compile-only, not deployed. See [checkpoint](docs/checkpoints/V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md); 21 static contracts and isolated ARM compilation pass. No chip regulator or Bluetooth pin changed.

- **v031/v032:** [Physical BT serdev and clock reference test](docs/checkpoints/V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) proved Bluetooth child registered but unbound, and the nominal BT txco is actually the same 32k clock as WLAN LPO. [v032 disabled LPO-correct preview](docs/checkpoints/V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md) passes 12 checks; no new hardware driver loaded.

- v033 RAM-only Bluetooth USB lab: read docs/checkpoints/V033_BLUETOOTH_USB_LAB_2026-10-24.md. Six linked Bluetooth dependencies, USB BT commands only on demand, exact v025 kernel preserved and 25 MHz MMC2.

- v033 physically proven BT shared-U4 ON/OFF vote and BCM4329B1 identification, but F2 still -62 and the USB HCIDEVDOWN path passes the wrong ioctl argument type. Read docs/checkpoints/V033_BLUETOOTH_PHYSICAL_2026-10-24.md before another BT power experiment.
