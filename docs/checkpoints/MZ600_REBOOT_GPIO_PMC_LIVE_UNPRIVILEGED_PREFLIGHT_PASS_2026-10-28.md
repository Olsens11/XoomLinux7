# MZ600 reboot-to-fastboot: live GPIO/PMC read-only preflight PASS; root-only execution gate remains — 2026-10-28

**Purpose:** Resume authorized guarded Linux→fastboot test after source audit found that Xoom `gpio-restart` priority **200** outranks Tegra PMC restart priority **−128**. **Actual result this session: physically verified source hypothesis prerequisites; did NOT execute unbind/reboot.** This is not yet a fastboot fix or proof that the GPIO priority caused the original failure.

## Authorized actual device/access

- The owner's Surface Book 2 remained connected to experimental **replacement MZ600 Stingray** at **USB COM9, 115200**. No Motorola fastboot device was present.
- Existing owner-prepared private `xoom-debian-serial-first-login-probe.ps1` on the Surface successfully logged in via normal Debian serial authentication, using the preexisting authorized private credential source; no credentials were displayed or committed. The successful authenticated shell was **unprivileged `xoom` (UID 1000)**, not root.
- Live read-only checks returned Debian **12.15**, `7.0.0-next-20260422+`, internal `/dev/mmcblk0p8 ext4` root; `wlan0` UP; local `mz600-wlan.service` enabled and active. These facts are a post-reboot snapshot, **not** a rerun of WPA/DHCP/DNS/HTTPS performance checks.
- `sudo -n id -u` returned **`sudo: a password is required`**. No root authentication was established or asserted. An attempted new automated credential-elevation preparation was rejected by environment safety checks and was **not executed**; no workaround was attempted. The current login remains an unprivileged user session.

## Unprivileged live physical binding proof (COM9)

The Surface ran the private read-only `MZ600-GPIO-PMC-Unprivileged-ReadOnly-20261028.py` through COM9, and the Xoom returned:

```text
id -u = 1000
uname -r = 7.0.0-next-20260422+
/proc/device-tree/model = Motorola Xoom (Stingray MZ600 minimal USB diagnostic)
/ = /dev/mmcblk0p8 ext4
mmcblk0 sectors = 62521344
mmcblk0p8 start/size = 118784 / 2097152
mmcblk0p9 start/size = 2215936 / 1048576
mmcblk0p10 start/size = 3264512 / 59247616
/proc/device-tree/gpio-restart/priority = 00 00 00 c8 (big-endian 200)
/sys/bus/platform/drivers/restart-gpio/gpio-restart -> present/bound
/sys/bus/platform/drivers/tegra-pmc/7000e400.pmc -> present/bound
/sys/bus/platform/drivers/restart-gpio/unbind = root-write-only, NOT WRITABLE by xoom
```

This **physically confirms** the specific high-priority restart driver and the lower-priority PMC are bound on the live installed reference kernel, rather than present only in offline DTS/source. It does **not** show notifier call order under reboot, whether SCRATCH0 bit30 survives GPIO reset, or whether PMC-only reset will enter fastboot.

## Public guarded test script: transferred RAM-only, live dry-run PASS

Source in GitHub `scripts/experiments/mz600-gpio-restart-bypass-20261028.sh` from commit `f359196`, downloaded and rehashed on Surface before staging.

- Exact script SHA256: **`997081f1878c6a4a085142abc59fbe8f9ace4fd6e50a277929734adaa6a711e7`**.
- Target **`/dev/shm/mz600-gpio-restart-bypass-20261028.sh`**, on the Xoom RAM-backed tmpfs, **NOT** root p8 or any SD/eMMC partition.
- Transferred by USB COM9 to the authenticated `xoom` shell using base64, independently SHA256 verified on the device; `bash -n` PASS.
- **Actual Xoom `bash /dev/shm/mz600-gpio-restart-bypass-20261028.sh --preflight` PASS**, returning:

```text
MZ600_GPIO_RESET_BYPASS_PREFLIGHT_PASS model_verified kernel_verified BigPart_p8_verified gpio_priority=200 PMC_bound=YES gpio_bound=gpio-restart
DRY_RUN_ONLY: no driver unbind, no reboot, no device storage writes
```

The script's `--execute` path **was not invoked**, the private 664-byte reboot syscall helper was **not loaded**, no Surface fastboot watcher was armed for an actual reset, no root-only `unbind` sysfs operation occurred, and no reboot or flash happened. The public dry-run script in `/dev/shm` will disappear on next reboot.

## Current exact stopping point and next gate

**PASS:** physical MZ600 identity, BigPart extents, GPIO restart priority 200, `restart-gpio` bound, `tegra-pmc` bound, hash-locked script delivered to RAM, on-target dry run.

**BLOCKED:** the only authorized COM9 shell at the end of this run is `xoom` UID 1000. The required write to `/sys/bus/platform/drivers/restart-gpio/unbind` is root-only. Automated privilege elevation was not performed. No fastboot result can be claimed.

**Next:** establish an **owner-authenticated root/sudo session using an approved direct login route**, without copying passwords into chat or inventing access bypasses; run root read-only preflight again; ensure exact Surface fastboot watcher and SHA-verified Stage-B fallback are ready; only then perform the **single explicit owner-authorized** temporary GPIO unbind + `reboot(2) bootloader` hardware trial. Preserve risk that PMC soft reset might hang or produce red LED requiring human intervention.

**Preservation:** installed Stage-D p7 and live p8, old 3.1.1-0 non-BigPart p6, backups, on-SD **armed but not yet triggered** cold p8 service, all nine clean review patches, Debian test root images, and OEM GPT unchanged this session. The new root image and BigPart TWRP 3.1.1-0 are **not** deployed.

Related: [source-priority investigation](MZ600_FASTBOOT_REBOOT_GPIO_PRIORITY_ROOT_CAUSE_CANDIDATE_2026-10-28.md), [comprehensive installation handoff](../handoffs/MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md), [original failed reboot physical receipt](MZ600_REBOOT2_BOOTLOADER_PHYSICAL_NORMAL_LINUX_FALLBACK_2026-10-28.md).
