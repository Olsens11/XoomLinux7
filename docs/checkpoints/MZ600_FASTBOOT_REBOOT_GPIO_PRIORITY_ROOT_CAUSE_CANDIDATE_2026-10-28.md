# MZ600 reboot-to-fastboot failure: GPIO restart priority vs Tegra PMC — 2026-10-28

**SOURCE-LEVEL ROOT-CAUSE CANDIDATE IDENTIFIED; NO LIVE FIX APPLIED.**

This checkpoint follows the [8:19 EDT failed physical reboot-to-fastboot trial](MZ600_REBOOT2_BOOTLOADER_PHYSICAL_NORMAL_LINUX_FALLBACK_2026-10-28.md). The owner wants a button-free transition from working Debian into fastboot, followed by a temporary BigPart-aware SD-root Linux boot to capture a cold p8 backup. **Do not repeat the original failed `reboot(2)` invocation unchanged.**

## 1. Direct source evidence, not inference

The exact pinned Linux7 source used for the clean nine-review build is:

`qa-nine-review-v2-source-20261028/` (private Desktop WSL), kernel source git tip `507eb069df819cb5cc801ad8be096f70d9ca7609`, based on `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.

The common Motorola Xoom DT definition in `arch/arm/boot/dts/nvidia/tegra20-motorola-xoom.dtsi`, lines 173–179:

```dts
gpio-restart {
    compatible = "gpio-restart";
    gpios = <&gpio TEGRA_GPIO(G, 3) GPIO_ACTIVE_LOW>;
    priority = <200>;
    active-delay = <100>;
    inactive-delay = <100>;
};
```

The same definition is included by both the legacy Stage-B/Stage-D and clean review device trees. The [earlier comparative audit](MZ600_STAGE_D_INSTALLED_VS_NINE_PATCH_REVIEW_2026-10-28.md) established that the *only* decompiled board-DTB differences were model description and the old BigPart boolean; the GPIO reset wiring remains unchanged.

`drivers/power/reset/gpio-restart.c` registers `gpio_restart_notify` with `SYS_OFF_MODE_RESTART` using the **DT-supplied priority 200**. Its callback actively toggles the GPIO to reset the device. Driver build config has **`CONFIG_POWER_RESET_GPIO_RESTART=y`**. The restart callback does **not** inspect `data->cmd`, so it handles ordinary and requested `bootloader`/ `recovery` modes identically.

`drivers/soc/tegra/pmc.c` separately registers the Tegra PMC as `SYS_OFF_MODE_RESTART` with `SYS_OFF_PRIO_LOW`. `include/linux/reboot.h` **defines `SYS_OFF_PRIO_LOW = -128`**, so the GPIO handler has a much **higher restart priority**. The Tegra PMC reboot notifier sets SCRATCH0 `PMC_SCRATCH0_MODE_BOOTLOADER = BIT(30)`, `PMC_SCRATCH0_MODE_RECOVERY = BIT(31)`, and `PMC_SCRATCH0_MODE_RCM = BIT(1)` before reset.

`kernel/reboot.c` confirms `LINUX_REBOOT_CMD_RESTART2` copies the user-supplied mode string into the kernel and invokes `kernel_restart(buffer)`. The reboot notifier receives `SYS_RESTART` and `cmd` before restart handlers run. The notifier may therefore set PMC SCRATCH0 bit30, yet the high-priority GPIO restart can initiate a *different external reset* before the PMC's own warm-reset handler is invoked.

The original historical NVIDIA Tegra restart implementation used **the same bit30** for `bootloader`, not an alternate magic keyword (Android Tegra source `arch/arm/mach-tegra/common.c`, `tegra_assert_system_reset()`, [public reference](https://android.googlesource.com/kernel/tegra.git/+/d28c42ee85e186bf02189e9cdacaff0c3c55f2e9/arch/arm/mach-tegra/common.c)). Thus a wrong mode string/bit-number is an inferior hypothesis.

The Tegra20 PMC source uses a **single MMIO aperture**, has `pmc->scratch = base`, and attempts to register `tegra_pmc_reboot_notify` when its platform probe succeeds. The presence of this code alone **does not prove that the installed board actually bound the PMC or invoked the notifier during the failed reboot**. That needs live inspection.

## 2. What is proven vs inferred

**Proven in source:**
- Two independent restart mechanisms exist.
- Xoom-specific GPIO restart has priority **200**, above PMC **-128**.
- The GPIO callback does not distinguish the requested reboot reason.
- The Tegra PMC notifier supports the correct bootloader scratch bit.
- `kernel_restart` preserves the requested `bootloader` string to notifier handling.
- A clean nine-source build uses a DT with this conflict; Stage-D derived DT has the same node.

**Proven in hardware (previous trial):**
- ARM `reboot(2)` helper issued the `bootloader` request.
- Linux COM9 dropped; a reset occurred; Surface fastboot polling found **no device for 120 seconds**.
- Linux COM9 and network later reappeared, ordinary login prompt observed.
- No flash, new boot, cold p8 capture or recovery test occurred.

**Likely, but not yet proven:** GPIO G3 external reset wins and causes the Motorola bootloader to lose/ignore the PMC reboot reason. We have **NOT measured scratch0 before/after the reset**, handler invocation order on the live installation, or bootloader consumption of the bit. Do not call this a verified complete root cause until an A/B test confirms fastboot using the corrected path.

## 3. Narrow reversible hardware test (prepared, NOT EXECUTED)

New test-only public source: [`scripts/experiments/mz600-gpio-restart-bypass-20261028.sh`](../../scripts/experiments/mz600-gpio-restart-bypass-20261028.sh).

It has two explicit modes:

1. `--preflight` — **read-only**: confirms exact previously observed Stingray diagnostic DT model, currently installed Linux release, internal `/dev/mmcblk0p8` and BigPart geometry, DT GPIO restart priority 200, and one bound instance of `restart-gpio` and `tegra-pmc`. On non-Xoom Desktop WSL, the same dry-run **correctly fails** on missing OF model. No reset/driver changes.
2. `--execute` — **root privilege and explicit host watcher handshake required**: verifies private static 664-byte ARM `reboot(2)` helper (SHA256 `451847d8acda2526c93a7b02d4694f3e80fefacce6281417ce75ee4ee6a0bf14`) in **`/run` tmpfs**; temporarily writes the precise bound device name to `/sys/bus/platform/drivers/restart-gpio/unbind`. That unregisters the high-priority GPIO restart handler, *without touching boot/recovery/root partitions or changing the on-disk DT*. It then invokes the verified `bootloader` syscall helper; a trap rebinds the driver if that invocation returns or any subsequent check fails. **On any ordinary kernel boot, the platform driver will be probed again from unchanged device tree.**

The host-side fastboot watcher must first be independently prepared to verify exactly one **`xoom-cdma`** unlocked expected device, and to restore/start proven Stage-B via **`fastboot boot` only** if fastboot appears. This test cannot guarantee hardware recovery if the PMC warm reset hangs (the existing red-LED issue). Be physically prepared to recover if remote conditions are uncertain.

**No on-device experiment was executed here:** After the previous reboot, Linux returned to a serial *login* prompt; the old authenticated root session ended. Surface network showed port 22 accepting connections, but noninteractive SSH failed with `Permission denied (publickey,password)`. There is **no currently verified authenticated root shell** available to run `--preflight`, unbind the GPIO handler or execute a second reboot. Do not solicit or publish the user's password. No privilege-elevation or credential-guessing attempted.

## 4. Engineering decision and next work

1. Reestablish an owner-authorized root terminal on the **replacement** MZ600. Begin with **read-only `--preflight`**, plus if available `dmesg` showing the `tegra-pmc` probe and `restart-gpio` binding. If the PMC isn't actually bound, stop and diagnose that instead.
2. Verify the exact live boot-image/DT and source hash before concluding the priority logic applies in production.
3. Decide whether the owner has access to physical power/volume rescue if a PMC-only restart hangs. Given prior red-LED behavior, **do not assume** every future software reset succeeds.
4. For a single controlled experiment only, prepare host fastboot observer and SHA-verified Stage-B image and stage the static helper in the Xoom `/run`. Execute the guarded GPIO-unbind script. Record **whether fastboot actually enumerates**.
5. If the hardware A/B test passes, design a **mode-selective, board-scoped** permanent solution that preserves the reliable GPIO hard-reset for ordinary reboots but yields to the Tegra PMC for explicit bootloader/recovery modes. The core Linux `struct sys_off_data` already offers the **`cmd`** field for restart handlers; a generic binding/API design must be reviewed before adding any upstream patch. **Do not** simply lower/disable GPIO reset priority for *all* modes in submitted series or invent a board-specific driver hack without evidence.
6. Protect TWRP 3.1.1-0 / BigPart: even if `recovery` mode becomes software-reachable, the *currently installed* factory-layout TWRP remains unsafe. Only try new BigPart recovery after p8 cold backup and a proven reversible test route.

**Results this turn:** discovered exact priority difference, reviewed OEM/Tegra source convention, authored a fail-closed test-only shell script, `bash -n` PASS, desktop non-Xoom `--preflight` refusal PASS. **Live physical GPIO-unbind and fastboot test NOT RUN; no new eMMC/SD mutations, no flashes, no reboots.**

Related: [chapter-boundary comprehensive handoff](../handoffs/MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md), [fastboot failed physical checkpoint](MZ600_REBOOT2_BOOTLOADER_PHYSICAL_NORMAL_LINUX_FALLBACK_2026-10-28.md), [remote cold backup plan](../plans/MZ600_REMOTE_NO_BUTTON_FASTBOOT_COLD_BACKUP_RECOVERY_2026-10-28.md).
