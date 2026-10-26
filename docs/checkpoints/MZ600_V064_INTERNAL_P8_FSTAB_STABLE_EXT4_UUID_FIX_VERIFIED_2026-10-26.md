# MZ600 internal p8 Debian root fstab migrated to stable ext4 UUID — physical PASS

**Date:** Monday, October 26, 2026. **Device:** experimental replacement Motorola Xoom MZ600, not the protected original Xoom. **Tablet status:** still running Debian 12.15 on **temporary Stage-D internal p8-root boot**, authenticated root USB console available, rescue microSD card remains inserted, p7 permanent boot image unchanged.

## Why this was needed

The actual kernel-generated GPT partition PARTUUID for internal p8 changes between Stage-D physical boots, verified by private comparison of current `/sys/class/block/mmcblk0p8/uevent` with Stage-E's saved GPT GUID and the prior Stage-D capture. Thus two attempts `root=PARTUUID=<captured p8 GPT GUID>` stalled at `Waiting for root device PARTUUID...`, while `root=/dev/mmcblk0p8` Stage-D reliably booted native Debian `/dev/mmcblk0p8 ext4 /`. Internal `/etc/fstab` root PARTUUID had become stale again. The ext4 **filesystem** UUID, recorded during p8 `mkfs.ext4` and checked across boots with `findmnt` and `blkid`, stays **`c2fb0167-7143-4186-b284-c86d6c09ea64`**. GPT PARTUUID and ext4 filesystem UUID are separate identifiers. This does NOT yet establish whether raw on-disk GPT bytes change or their kernel interpretation differs; leave GPT unchanged.

## Physical safety gates before change

Owner opened Surface USB console COM9, `sudo -s`, entered password privately, and obtained `root@xoom-mz600:/home/xoom#` prompt. Surface COM9 remote read-only audit confirmed:

```text
id -u                                 0
findmnt -n -o SOURCE,FSTYPE,OPTIONS /  /dev/mmcblk0p8 ext4 rw,relatime
/sys/class/block/mmcblk0p8/start      118784
/sys/class/block/mmcblk0p8/size       2097152
blkid -s UUID -o value /dev/mmcblk0p8 c2fb0167-7143-4186-b284-c86d6c09ea64
/etc/fstab root entry count            1
/etc/fstab root fstype                 ext4
/etc/fstab root options                errors=remount-ro
backup path                            did not already exist
```

One host PowerShell check initially reported a missing root mount string because its regex expected *one* space in `findmnt` output, which actually had multiple spaces. All physically read fields themselves were correct; no writes had occurred at that check. The later guarded on-device update explicitly used exact `findmnt -n -o SOURCE /` equality, not whitespace parsing.

## Exactly one file changed, with backup and rollback

A guarded, fail-closed `bash` heredoc on **live internal p8 root** reverified UID0, actual `/dev/mmcblk0p8` root ext4, BigPart p8 geometry 118784/2097152 sectors, sysfs `PARTNAME=system`, exact ext4 UUID from `blkid`, one root fstab entry using the old `PARTUUID=...` selector, and no preexisting backup. It then:

1. Prepared a `mktemp` file in `/etc` where **only the single root entry's first field** was replaced: `PARTUUID=<stale per-boot GPT UUID>` → **`UUID=c2fb0167-7143-4186-b284-c86d6c09ea64`**. Other fstab fields, root mount options and all nonroot lines were retained.
2. Verified the replacement by applying the inverse root selector change to the temp file and comparing it **byte-for-byte** with the original `/etc/fstab` via `awk ... | cmp -s`.
3. Made an exact mode/ownership-preserving backup **`/etc/fstab.before-stable-ext4-uuid-20261026`** with `cp -p`, then checked `cmp -s` against the untouched original.
4. Applied the prepared temp file to `/etc/fstab` atomically after `chown --reference`, `chmod --reference`; `sync` completed.
5. Verified postwrite that the single fstab root field was `UUID=<verified p8 filesystem UUID>`, inverse transformation exactly reproduced the backup, owner/group/mode matched the backup, and the running `/` was still mounted from `/dev/mmcblk0p8`.
6. Actual on-device output **`P8_STABLE_EXT4_UUID_FSTAB_UPDATED_AND_FULLY_VERIFIED`**, wrapper's `FSTAB_CHANGE_SCRIPT_EXIT=0`.

An additional read-only independent audit visibly confirmed `ROOT_ACCESS_PASS`, `LIVE_INTERNAL_ROOT_PASS`, `LIVE_EXT4_PASS`, `EXT4_UUID_PHYSICAL_MATCH`, `FSTAB_ROOT_UUID_PHYSICAL_MATCH`, `FSTAB_SINGLE_ROOT_PASS`, `BACKUP_ORIGINAL_ROOT_DIFFERS`, `ALL_OTHER_FSTAB_BYTES_IDENTICAL`, `OWNER_GROUP_MODE_PRESERVED`. Its host parser initially rejected `ROOT_ACCESS_PASS` because terminal ANSI/prompt formatting confused an anchored regex, **not because the command or check failed**. A separate independent end-to-end combined physical check disabled tty command echo, re-read filesystem UUID, actual internal root, single fstab root entry, and preserved backup/mode; terminal printed **`EXT4_FSTAB_POSTCHECK_FINAL_PASS_20261026`**. Thus actual physical readback unambiguously **PASS**.

## Current state and next step

- **Current live root:** Stage-D `fastboot boot` (temporary) with Linux 7 kernel `7.0.0-next-20260422+`, `root=/dev/mmcblk0p8`, Debian 12.15 running from internal `/dev/mmcblk0p8 ext4 /`; authenticated `root` console was confirmed in this turn. This is not yet a persistent internal-root boot.
- **Installed internal p8 /etc/fstab:** **stable ext4 UUID** root selector now installed and physically verified. Backed-up prior GPT selector retained. No p8 reformat, GPT write, p7 flash or power-cycle occurred. p7 remains known verified Stage-B persistent Debian **microSD-root** rescue boot (boot-image first 6645760B SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`), and p6 TWRP is untouched.
- **Working Stage-D temporary kernel boot image:** Surface `downloads/MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img`, SHA256 **`fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`**, 6,645,760B. Proven twice with USB COM9 Debian login and `findmnt /` = actual internal p8.
- **Do not flash Stage-C or Stage-E** GUID-root boot images; both hung during early `root=PARTUUID` resolution. If deciding to persist Stage-D in p7, establish explicit owner authorization, verify p7/Stage-B/stock backups, rescue plan, and then full normal **cold** boot and physical root-readback. Do not assume that boot-tested TEMP Stage-D was already made persistent.
- **Future separate investigation:** why p8 kernel-reported GPT unique PARTUUID changes across boots while ext4 UUID stable. Obtain physically read-only alternate GPT header and entry-array hash across boots, ensure it remains fixed; inspect `efi.c` partition GUID handling/metadata lifecycle. Do not claim specific bug until proven. Separate outstanding kernel/modules release `+` mismatch, Wi-Fi and systemd D-Bus issues.

