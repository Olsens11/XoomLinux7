# Experimental MZ600 software reboot-to-fastboot — first physical test, 2026-10-28

**RESULT: LINUX REBOOTED, REQUESTED FASTBOOT NOT ENTERED.**
**Tablet returned to regular Linux; no partition flashes, recovery boots,
root filesystem replacement or cold p8 backup occurred.**
User authorized a remotely controlled test while away; owner cannot
press the tablet's buttons during this test.

## Identity and prerequisite checks

Surface Book 2 hosted the entire local guarded workflow, capturing its
private command log at
`C:\Users\olsen\xoom-linux-rom\inspection\MZ600-COLD-P8-REMOTE-CYCLE-20261028.log`.
The owner-controlled USB serial COM9 was an authenticated root shell
on the **experimental replacement MZ600** before the test.
Physical Linux7 `uname -r` was `7.0.0-next-20260422+`,
root `/dev/mmcblk0p8 ext4 rw`, p8 BigPart
`start=118784, size=2097152` sectors.

Surface rehashed the two **proven** 6,645,760-byte private boot images:
- SD-root Stage-B temporary image SHA256
  `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`.
- Internal-p8 Stage-D temporary image SHA256
  `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`.
Both passed exact byte count and hash. Removable rescue microSD
`/dev/mmcblk1p1` was verified present, not mounted and able to
mount `ro,noload` read-only; ~27GiB free, Debian Bookworm root.
The fallback boot images were not used during this test.

## Pre-armed cold-backup agent on removable SD (NOT triggered)

The private rescue SD root was mounted once read-write from the
already running installed Linux *only* for explicit staging.
The staging utility verified original SD contents and installed a
single armed one-shot systemd unit plus shell helper into that SD
root filesystem, then synced and unmounted the card. Neither
internal eMMC p8 nor p6/p7/p9/p10 nor GPT received a direct write.

If a future `fastboot boot` of the physically proven Stage-B image
actually boots from **microSD**, the one-shot service will:
- Immediately disarm to avoid repeat execution.
- Verify expected internal disk, BigPart p8/p9/p10 geometry,
  mount source `/dev/mmcblk1p1`, absence of any internal mounts,
  and microSD available space.
- Copy raw unmounted `/dev/mmcblk0p8` to
  `/var/backups/MZ600-V31-P8-COLD-20261028/p8-cold.img` on SD,
  compare the file SHA256 against the original raw device SHA256,
  run offline read-only `e2fsck -fn`, and emit `RESULT.txt`
  + `SHA256SUMS` only after success.
- Request bootloader reboot with the verified static ARM helper
  **only after backup succeeds**. If the reboot mode is ignored as
  in the current test, it may boot normal installed p7 instead;
  neither possibility has been tested under Stage-B.
- On validation failure, halt without a cold-backup success marker
  or flash, leaving diagnostic logs on SD.

This service is **armed and will activate the next time Stage-B
microSD-root systemd reaches multi-user.target**. It did not run
during the 2026-10-28 attempted transition.

## Exact attempted bootloader transition

The project's existing small freestanding ARM32 helper source,
`scripts/experiments/mz600-arm32-reboot-to-bootloader-20261026.c`,
was compiled with ARM GNU 14.3 as a **664-byte** static ARM EABI
executable (private host SHA256
`451847d8acda2526c93a7b02d4694f3e80fefacce6281417ce75ee4ee6a0bf14`).
It was base64-transferred into Linux `/run` **RAM only**, where
`sha256sum` matched source bytes, and marked executable.

The helper invokes Linux `reboot(2)` ARM syscall with
`LINUX_REBOOT_CMD_RESTART2` and literal `bootloader`. The matching
kernel `drivers/soc/tegra/pmc.c` recognizes the bootloader reason and
attempts to set `PMC_SCRATCH0_MODE_BOOTLOADER` before restart.
**Kernel source support is not proof that Motorola bootloader honored
the reset reason.**

On Surface, the host script
`MZ600-Linux-Fastboot-SDCold-Return-20261028.py` performed its
device/mount/geometry/hash guards and then issued the helper at
**08:19:54 local EDT**. USB serial COM9 was disconnected by
**08:19:56**, consistent with an actual Linux reboot.

During the following **120 seconds**, Windows `fastboot devices`
never reported the expected MZ600 bootloader. The watcher
terminated without issuing **any** `fastboot boot`, `fastboot flash`,
or `fastboot reboot`.

After the timeout:
- Surface `Get-PnpDevice -PresentOnly` found the **Linux USB
  gadget serial interface COM9** with status OK, not the Motorola
  fastboot USB interface.
- Network ping to the Xoom's previously verified private WLAN
  address succeeded.
- Reopening COM9 and sending a non-destructive Ctrl-C returned
  the normal **`xoom-mz600 login:`** prompt.
- No login/password was attempted, no recovery was booted.
- It is therefore **not** an all-device red-LED hang: the
  device did return to a Linux userspace login. The exact reason
  the requested fastboot mode was skipped remains unproven.

## Conclusion and next test gates

**PHYSICAL PASS:** the Linux reboot syscall caused transition out
of the running root shell, and ordinary Linux boot recovery is
reachable again via USB and network.

**PHYSICAL FAIL:** requested reboot-to-bootloader was not honored
in this run; no fastboot device appeared within two minutes.

**NOT ATTEMPTED:** temporary Stage-B boot, cold/unmounted p8 backup,
BigPart TWRP 3.1.1-0 build/boot/flash, any p6/p7/p8 modification.
The previous verified 8-image live snapshot on Surface and the
original/new private rootfs images are preserved separately.

Do not repeat identical remote reboot commands just to hope for a
different outcome. Next investigate the actual persistent
Stage-D Tegra PMC notifier registration/bootloader scratch semantics,
compare Motorola OEM reboot mode conventions and test a safer
reversible approach when operator is physically able to recover
a reset failure. Consider guarded RAM-only kexec as a separate
source/hardware research path; `CONFIG_KEXEC=y` is enabled but
device functional validation is OPEN. Never claim kexec proven.

See [button-free transition plan](../plans/MZ600_REMOTE_NO_BUTTON_FASTBOOT_COLD_BACKUP_RECOVERY_2026-10-28.md),
[preflash preservation](MZ600_V31_PREFLASH_PRESERVATION_AND_TEST_ROOT_2026-10-28.md),
[TWRP 3.1.1-0 recovery audit](MZ600_TWRP_3110_BIGPART_BASELINE_AUDIT_2026-10-28.md).
