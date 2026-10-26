# 2026-10-26 — Internal p8 Debian `/etc/fstab` corrected to physical live GPT p8 PARTUUID

**Experimental replacement Motorola Xoom MZ600 only.** User locally logged into Debian from internal p8 (Stage-D temporary `fastboot boot`) and entered `sudo -s` on Surface USB ttyGS0; password not disclosed/logged; user released COM9. All work used verified root shell on the running tablet. No new reboot, temporary boot, persistent flash, or partition format performed in this checkpoint.

## Live physical guard and detected inconsistency

Initial checks verified `id -u=0`, `findmnt -n -o SOURCE,FSTYPE,OPTIONS /` shows **`/dev/mmcblk0p8 ext4 rw,relatime`**, `/sys/class/block/mmcblk0p8/start=118784`, `size=2097152` (1GiB classic BigPart), `PARTNAME=system`, and kernel sysfs uevent has exactly one full 36-character live GPT `PARTUUID`. Existing internal `/etc/fstab` contained exactly **one** root entry whose old `PARTUUID=...` differed from that current kernel p8 ID. A unique backup filename `/etc/fstab.before-stage-e-live-guid-20261026` was checked not to exist before modifying any file.

Private raw p8 GPT GUID is in Surface `private-backups/replacement-mz600-2026-10-25/P8-BigPart-Partition-UUID-LIVE-VERIFIED-20261026-PRIVATE.txt`, SHA256 `000ea863f8ae2651543cf30b0fc9f6fe6b4f453ada8ea01fdbdea65f3aa27ae3`. Do not add raw GUID to public docs or disclose a password.

## Exactly scoped write and physical verification

An on-device guarded shell script:

1. Independently revalidated UID0, root mounted **only from p8**, BigPart geometry and `PARTNAME=system`; verified both old and new root identifiers have full GPT-style 36-character format, differ, and exactly one `/` fstab entry exists.
2. Created a unique private on-device backup **`/etc/fstab.before-stage-e-live-guid-20261026`** using `cp -p`, checked `cmp -s` exact against original.
3. Used `awk` to replace **only the first field of the single root entry** with `PARTUUID=<live actual mmcblk0p8 GPT GUID>`, writing a unique `mktemp` file. Checked generated root selector and entry count, restored owner/group/mode from backup with `chmod/chown --reference`, atomically moved temporary file onto `/etc/fstab`, and synced.
4. Post-edit on same live root independently verified:
    - `id -u=0` and `findmnt /` still `/dev/mmcblk0p8`.
    - Installed root fstab entry **exactly matches** `PARTUUID` from live `/sys/class/block/mmcblk0p8/uevent`.
    - Old root identifier in backup differs from new one.
    - Undoing only the root selector in the edited `/etc/fstab` produces **byte-identical** file compared to the backup via `awk ... | cmp -s - <backup>`, proving **no other line changed**.
    - Owner/group/mode preserved exactly via `stat -c '%u:%g:%a'`.
5. On-device script printed **`STAGE_E_P8_FSTAB_LIVE_GUID_UPDATED_AND_BACKUP_VERIFIED`**, and independent audit printed `P8_FSTAB_NEW_GUID_MATCHED`, `P8_FSTAB_BACKUP_EXISTS`, `USER_IS_ROOT`, `P8_LIVE_ROOT`, `P8_BOUNDARIES_OK`, `INTERNAL_ROOT_GUID_MATCHED`, `OLD_ROOT_IDENTIFIER_WAS_DIFFERENT`, `FSTAB_ONLY_ROOT_SELECTOR_CHANGED`, and `FSTAB_OWNER_MODE_PRESERVED`. Note the host PowerShell immediate-output parser prematurely printed a false negative because of tty ANSI/bracketed paste prefix and serial-buffer timing; subsequent physical device output and a separate independent audit **confirmed all checks passed**. Never misclassify that host parser error as a failed on-device edit.

## What has NOT been tested

The **Stage-E true-live-GPT-PARTUUID temporary boot image** is prepared **offline** on the Surface at `downloads/MZ600-V064-BIGPART-INTERNAL-P8-TRUEGPT-PARTUUID-TEMPBOOT-OFFLINE-UNTESTED.img`, **6,645,760 bytes**, SHA256 **`c91d7f40d90df5bcb058fee6f843c64b46d02190b74eee36186ba3d9b4c3c63d`**, source from proven Stage-B kernel+ramdisk. It is **NOT yet booted, NOT flashed**. Current tablet STILL RUNS TEMPORARY STAGE-D Debian internal root `/dev/mmcblk0p8`. Permanent p7 retains proven Debian-on-SD Stage-B rescue, original p7 OEM boot backup on Surface and TWRP p6 preserved.

**Next:** owner uses repaired physical power/volume buttons to manually enter fastboot, leaving SD card inserted. Surface verifies known unlocked replacement MZ600 identity and checksum, issues `fastboot boot <Stage-E image>` **TEMPORARY ONLY** (do NOT flash). Watch Xoom framebuffer and COM9, log into Debian privately, and verify `findmnt /` is **`/dev/mmcblk0p8 ext4`**. If PARTUUID early root works, diagnose whether UUID was merely stale/incorrect earlier; don't assume stable across reboots without verifying kernel uevent again. If Stage-E fails, reset normally to preserved p7 SD-root rescue, and do not format or modify p8.

Potential persistent follow-up: only after TEMP Stage-E boot passes, explicitly evaluate user choice of permanent p7 Stage-E internal root vs maintaining removable rescue option; ensure cold boot and rollback plan. Separate kernel modules `uname -r +` mismatch, Wi-Fi and systemd bus issues remain.

