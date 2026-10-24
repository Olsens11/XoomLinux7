# On-demand SDMMC2 initialization — design proposal (2026-10-24)

**Status: PROPOSED, NOT IMPLEMENTED OR HARDWARE QUALIFIED.** This document describes a test-harness extension, not an available USB command.

## Why this is necessary
Linux `drivers/mmc/core/sdio.c` and `sdhci-tegra` are built into the experimental kernel. Loading/unloading `brcmfmac.ko` already works dynamically but does **not** rerun `mmc_sdio_init_card()`, nor re-read raw CCCR capabilities, choose host bus timing or rerun the controller power sequence. v018/v019 have required temporary kernel boots because the six-field OEM override and SDMMC2 max-frequency were compiled in.

An on-demand **card re-enumeration** after selecting a **runtime-configurable board-specific profile** can eliminate future boot-image rebuilds for those experiments. Initial enumeration may still happen at boot; what matters is that experiments can subsequently reinitialize the card without rebooting Android/kernel. Profile mutation **without** re-enumeration is insufficient.

## Feasibility — observed on replacement MZ600 during v018 USB session

The existing read-only `SDIO` command returned:
- `/sys/bus/platform/drivers/sdhci-tegra/` contains `c8000200.mmc`, `c8000400.mmc`, `c8000600.mmc`, `bind`, and `unbind`.
- `/sys/bus/platform/devices/c8000200.mmc/uevent` names `DRIVER=sdhci-tegra`, `OF_FULLNAME=/mmc@c8000200`, `OF_ALIAS_0=mmc2`.
- SDIO functions `mmc2:0001:1`, `:2`, `:3` and Broadcom vendor/device `0x02d0/0x4329` present.
- `mmc0` is the internal eMMC with multiple Android partitions; **never** unbind it. `mmc1` is also out of scope.

The existence of `bind`/`unbind` is a practical control point but not proof that software rebind reliably resets all chip clocks/regulators or equals a true cold power cycle. That MUST be tested separately.

## Proposed runtime controls, fail-closed

1. **Kernel-owned per-board profile** (Stingray BCM4329 only): choose `AUTO` (raw Linux CCCR parsing) or `MOTOROLA` (the six proven-to-take-effect OEM fields). Eventually separately expose `MAX_CLOCK` with bounded profiles; do **not** change clock in the same experimental comparison as capability mode. Expose and read back via a root-only runtime sysfs or debugfs parameter, with locking and an exact card/vendor+device check. Other boards/cards must remain unaffected. Specify whether a profile change is merely *pending* until next SDIO enumeration.
2. **USB commands in RAM-only PID1** such as `MMC2_STATUS`, `MMC2_PROFILE AUTO|MOTOROLA`, `MMC2_REINIT`. Implement command parser allowlists, explicit success/failure/status, and no arbitrary shell/path writes.
3. **Preflight**: confirm running board/model and actual matched `c8000200.mmc` platform device/driver, serial-session health, battery and stable USB, no mounted filesystems/swap backed by MMC2, and `brcmfmac` and `brcmutil` completely unloaded. Do not allow control of `mmc0` or `mmc1`. Fail closed on ambiguities.
4. **Reinitialize** exactly `c8000200.mmc` by writing its device ID to `/sys/bus/platform/drivers/sdhci-tegra/unbind`, wait for MMC2 disappearance, set/request runtime profile while host is safely detached if supported, and write the same exact ID to `bind`. Wait for SDIO enumerated functions and vendor/device confirmation. No partition writes, no fastboot and no system-level recovery changes.
5. **Postflight**: capture newly parsed six fields, actual `ios.clock`, timing, width, signaling/voltage *software values*, reset and power state if measurable, and compare read-only raw CCCR. Load selected RAM firmware and `.ko`, capture IOEx/IORx and F2 readiness plus trace. A kernel module load with `rc=0` is not network success.
6. **Rollback**: unbind/rebind with AUTO profile if re-enumeration is healthy; otherwise recover via previously qualified **temporary boot**. Never blindly loop rebind requests or mutate eMMC. Treat missing GPIO/regulator recovery or lost USB as a stop condition.

## Cold-vs-warm experiment labels

- `MODULE_RETRY`: Broadcom driver reload, card kept enumerated.
- `CARD_REINIT`: platform MMC2 driver detached/re-attached with existing board power policy.
- `POWER_CYCLE`: additionally proven actual reset/regulator/32k off/on sequence (not automatically implied by rebind).
- `COLD_BOOT`: physical reboot and kernel initialization (still necessary for final validation).

Each is distinct; do not promote one result as proof of another.

## Proposed acceptance order

- Review on-device MMC2 topology and driver remove/probe effects; verify that rebind will not impact eMMC or recovery partitions.
- Add exact scoped runtime capability profile to MMC initialization and a safe PID1 USB control interface **in one further temporary-boot diagnostic candidate**. Keep default AUTO, and preserve v015 as rollback.
- Qualify on hardware: no-change AUTO→AUTO on-demand reinit first, then AUTO→MOTOROLA→AUTO with matched firmware/NVRAM and USB telemetry. Verify *effective* capabilities and fresh SDIO enumeration each step.
- Verify stop/error paths: loaded module should refuse reinit; bad profile should refuse; missing driver should refuse; loss of SDIO functionality should not trigger unbounded retries.
- Only after the mechanism is stable, test independent clock, reset and firmware sequencing profiles. Do not confuse the loader with a Wi-Fi fix.

**No such dynamic control was executed in v018.** The v018 workaround was compiled into a temporary-boot image and its F2 error remained -62. This design is the next infrastructure workstream.
