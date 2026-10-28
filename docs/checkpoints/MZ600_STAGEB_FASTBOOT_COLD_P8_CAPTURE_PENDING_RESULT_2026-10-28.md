# MZ600 physical fastboot restored; Stage-B cold p8 backup executed — 2026-10-28

**READ THIS STATUS EXACTLY: Physical fastboot and temporary Stage-B SD-root Linux boot PASS. Cold-p8 backup script started and progressed into verification; its final RESULT.txt, file SHA and e2fsck output have NOT YET BEEN independently read. The tablet returned safely to its persistent internal Debian Linux. NO FLASH and NO internal partition writes during this action.**

## Physical recovery of fastboot through hardware buttons

Owner's prior physical **boot-menu Fastboot selection** briefly disappeared and fell through to normal Linux, without displaying the fastboot protocol screen. This is distinct from the separately tested Linux software reboot-to-fastboot failure. The owner then used the **direct hardware key method** and reported `Starting Fastboot protocol support`.

Surface Book 2 positively enumerated **exactly one** authorized replacement MZ600 (the same previously verified private USB serial), `fastboot devices -l` reported `fastboot`; `fastboot getvar product` was **`xoom-cdma`**, `unlocked: yes`, `secure: no`. Thus the bootloader's fastboot protocol still works and no bootloader repair is justified.

Surface independently rehashed the prior physically proven classic BigPart-aware **Stage-B SD-root Debian** image:
`C:\Users\olsen\xoom-linux-rom\downloads\MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img`,
size **6,645,760B**, SHA-256
`b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`.
Host guarded script is
`C:\Users\olsen\xoom-linux-rom\inspection\MZ600-StageB-Fastboot-Boot-ColdP8-20261028.ps1`.
Guards PASS, executed **`fastboot -s <exact verified MZ600> boot <image>` only**:
`Sending boot.img OKAY [0.922s]; Booting OKAY [1.089s]; exit 0`.
**NO fastboot flash, no recoveries, no format.**

## Real Stage-B boot and cold backup process

Linux USB serial COM9 reappeared. Authenticated normal (unprivileged) ttyGS0 serial login physically showed `Debian 12.15`, kernel `7.0.0-next-20260422+`, and root **`/dev/mmcblk1p1 ext4 /`** (correct removable SD, NOT internal p8).

Prior setup had armed a one-shot SD-root service with a conservative private backup script. Exact scripts on Surface:
- `inspection/mz600-cold-p8-backup-with-return-20261028.sh`
- `inspection/mz600-cold-p8-backup-20261028.service`

From live unprivileged COM9 read-only probe:
- Script removed the SD one-shot marker = **DISARMED**.
- `findmnt -S /dev/mmcblk0p8` returned no mounts.
- The logged guard string was **`MZ600_COLD_BACKUP_GUARDS_PASS root=removableSD internal_p8=UNMOUNTED bytes=1073741824`**.
- Private output directory `/var/backups/MZ600-V31-P8-COLD-20261028` existed, owned root:root and mode **0700**.
- Root-readable log `/var/log/mz600-cold-p8-20261028.log` began **2026-10-28T19:30:12Z**, and `dd` progressed through more than 500MiB of the 1GiB transfer.
- Later live `ps` showed running backup shell and `sha256sum /dev/mmcblk0p8`, indicating the copy progressed to comparison with the **original raw device**. Captured output did not include completed digest or e2fsck result.
- `systemctl show` on Stage-B returned `Failed to connect to bus: No such file or directory`; this known Stage-B limitation does **not** negate the independently observed backup process, but its service-status utility cannot be used as the acceptance authority.

The staged script validates the readback byte count, computes **file vs raw-device SHA-256**, runs `e2fsck -fn` on the **unmounted captured image** and emits `RESULT.txt`, `SHA256SUMS` only on success. It is coded to run its verified ARM reboot helper **after** all of these stages succeed; the Surface serial connection subsequently dropped. However, the dropped connection and return to normal Linux are **not** a substitute for reading those files and verifying the file directly.

## Return to original internal Debian

After a temporary period with no COM9/fastboot/network visibility, Surface later confirmed **COM9 and prior Wi-Fi IP ping returned**. Fresh authenticated ttyGS0 read-only login physically confirmed:
- `/dev/mmcblk0p8 ext4 /` internal root, kernel 7.0.0-next-20260422+, Debian 12.15;
- `wlan0` UP, LINK UP;
- BigPart p8 size **2097152 512B sectors**, 1GiB;
- rescue microSD `/dev/mmcblk1p1` ext4 present and **unmounted**;
- owner still has working direct hardware fastboot entry.

**No device kernel/DTB/root/recovery image has been replaced and no p6/p7/p8/p9/p10 or on-disk GPT was intentionally written.** The one-shot service wrote only to the removable SD. This was a successful non-flash test of the previously proven Stage-B transition and return to persistent Linux.

## Immediate next safe gate (NOT DONE)

Current authenticated COM9 session is normal user `xoom` UID 1000; the rescue SD image is unmounted, the private backup directory is owned root:root with mode 0700. Therefore checking file integrity requires **owner-entered sudo/root authentication in the Surface interactive USB COM9 terminal**, not extracting a password or guessing credentials.

Then mount the **existing rescue SD** `/dev/mmcblk1p1` **read-only with ext4 `noload`**, inspect:
`/var/backups/MZ600-V31-P8-COLD-20261028/RESULT.txt`,
`SHA256SUMS`, `e2fsck-readonly.txt`, and full `p8-cold.img` exact size 1,073,741,824B; independently recompute SHA and check result against manifest, and preserve an off-device Surface copy. If the file is absent/partial or any check fails, keep hard stop. No root flashing, no new TWRP p6 flash and no new OS install until verified cold backup + rollback.

**Status: FASTBOOT PASS, TEMP_STAGE_B_SD_ROOT PASS, COLD_BACKUP_SCRIPT_STARTED PASS, COLD_BACKUP_COMPLETE NOT YET INDEPENDENTLY VERIFIED, INTERNAL_DEBIAN_RETURN PASS.**
