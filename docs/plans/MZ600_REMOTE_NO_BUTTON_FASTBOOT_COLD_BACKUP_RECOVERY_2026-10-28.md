# MZ600: no-physical-buttons fastboot / cold p8 backup / TWRP 3.1.1-0 — 2026-10-28

**Purpose:** Owner is away from the tablet and wants remote software-controlled transitions rather than pressing volume/power buttons. **Non-disruptive audit only. NO reboot/flash/partition write executed in this checkpoint.**

## Direct kernel code evidence

The pinned Linux7 Tegra20 PMC implementation at `drivers/soc/tegra/pmc.c` implements `tegra_pmc_program_reboot_reason()`. The kernel reboot notifier accepts literal `"bootloader"` and `"recovery"` strings and sets the corresponding `PMC_SCRATCH0_MODE_BOOTLOADER` or `PMC_SCRATCH0_MODE_RECOVERY` bits before Tegra hardware reset. The compiled reference builds include the Tegra PMC driver; Stage-D Linux7 is currently running. A pre-existing owner-project source-only helper `scripts/experiments/mz600-arm32-reboot-to-bootloader-20261026.c` calls ARMv7 `reboot(2)` with `LINUX_REBOOT_CMD_RESTART2` and `"bootloader"`.

**This supports a software route, but it does not physically prove that a real MZ600 bootloader will honor the request on every reset.** The exact current installed Debian-to-fastboot transition remains a hardware gate; prior red-LED reset trouble makes this an important distinction.

## Current device and host evidence (read-only)

2026-10-28 root COM9 preflight from Surface confirmed:
- `id -u=0`, kernel `7.0.0-next-20260422+`, root `/dev/mmcblk0p8 ext4 rw`.
- Internal 1GiB BigPart p8, 512MiB p9 and expanded p10.
- Rescue microSD is inserted and enumerated as `/dev/mmcblk1p1` ext4, **not mounted**.
- The Surface Windows COM9 USB gadget port is present.
- Known-good classic BigPart **Stage-B Debian microSD-root temporary boot** is available on Surface:
  `downloads/MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img`;
  6,645,760B SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`.
- Recovery fallback / installed Stage-D `root=/dev/mmcblk0p8` boot image is also available with verified SHA256
  `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`.
- This same **Stage-B** binary was physically `fastboot boot`-tested on this MZ600 and mounted Debian root from microSD with internal p8 unmounted. USB COM9 login worked.
- The persistent p7 kernel image is already backed up and remains installed; original TWRP 3.1.1-0 p6 is backed up.

## Intended controlled transition chain (NOT executed)

1. From currently running Linux, remotely request **`reboot(2)` `LINUX_REBOOT_CMD_RESTART2` with `"bootloader"`**, not normal `systemctl reboot` and not direct `reboot recovery`. Stage command and prove exact identity before invoking. Current MZ600 might still stall at red LED; operator cannot resolve this remotely if it happens.
2. Surface must explicitly prove exactly one expected `fastboot devices` result, `fastboot getvar product` is correct `xoom-cdma`, and appropriate unlocked identity; **do not send a flash command**. Handle fastboot USB interface switch from Linux USB gadget automatically; timeout and stop on mismatch.
3. Surface executes **`fastboot boot <SHA-pinned Stage-B image>`**, *never* `fastboot flash`. Device should boot Debian from the physically present SD while exposing USB ttyGS0. Verify root `/dev/mmcblk1p1`, and internal `/dev/mmcblk0p8` **unmounted** with correct 1GiB sector size before taking a new p8 cold raw backup. Must be an intentionally authorized root backup agent; Stage-B normal user might require credentials and privileges, so do **not** claim it can operate unattended until the authenticated root path is established.
4. Read-only bit-copy all 1,073,741,824B of p8 to an owner-controlled private receiver and SHA-verify length, with filesystem quiescent; independently offline-check ext4. Preserve previously verified live snapshot and any new cold image separately. No GPT / internal p8 writes.
5. With the original p6 preserved, build a candidate TWRP **3.1.1-0** retaining its userspace but kernel and mounts honoring the classic BigPart view. Ideally use `fastboot boot` for a guarded one-shot read-only test of the candidate, checking 10 partition extents and **no** automatic /data, /cache, /system mounts or recovery writes.
6. Once approved candidate is physically proven and p8 cold backup verified, a **separately approved** p6-only write could occur from Linux's root shell (after hashing the full recovery image and exact p6 restore copy); read-back SHA and verify recovery. Only thereafter use the same `reboot(2)` mode `"recovery"` from Linux. Never reboot into existing factory-partition TWRP, which maps p10 into the current expanded p8.
7. Exiting a stable fastboot session can be by `fastboot boot` of a **known-good** Stage-D image, or `fastboot reboot` to installed p7. Note the latter boots p7 and is NOT an absolute guarantee of Linux if the bootloader state, reset issue or p7 installation changes.

## Operational safety gates

**NO REMOTE REBOOT WHILE OWNER AWAY UNTIL:**
- A plan exists for an unsuccessful software reset / intermittent red LED that can require manual buttons. No software can guarantee a bootloader transition if the system has already hung in hardware reset.
- Host-side exact-device identification, image hash, fastboot wait/timeout and recovery fallback are scripted and dry-run tested with no device reboot.
- Remote root privilege in Stage-B is solved without extracting or exposing private passwords.
- Cold p8 transfer destination and integrity checker ready; must not overwrite the live snapshot.
- TWRP kernel/device identity, automatic mount suppression and BigPart boundaries validated before ever booting any TWRP candidate.
- No acceptance of 2.x TWRP downgrade or invented SuperBigPart; current 1GiB root variant already offline fsck PASS.

**Status:** software reboot mechanism SOURCE-VERIFIED and current recovery images HOST SHA-VERIFIED; actual cross-mode reset NOT RUN; remote no-buttons path REQUIRES a real hardware qualification and safety/recovery gate.

See: [current installed p6 TWRP audit](../checkpoints/MZ600_TWRP_3110_BIGPART_BASELINE_AUDIT_2026-10-28.md), [preflash backup](../checkpoints/MZ600_V31_PREFLASH_PRESERVATION_AND_TEST_ROOT_2026-10-28.md), [existing BigPart recovery plan](../checkpoints/MZ600_ONE_GIB_ROOT_AND_BIGPART_RECOVERY_PLAN_2026-10-28.md).
