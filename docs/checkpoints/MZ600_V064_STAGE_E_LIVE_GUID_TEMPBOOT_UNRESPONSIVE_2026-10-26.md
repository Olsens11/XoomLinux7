# MZ600 Stage-E live-GPT-PARTUUID temporary boot — no Debian login, root selection still unresolved

**2026-10-26 approximately 04:18–04:22 EDT.** Experimental replacement Motorola Xoom MZ600, protected original not touched. **This supersedes the prior assertion that merely correcting the old saved UUID would restore PARTUUID-based early root boot.** That hypothesis did not work in this test.

## What was performed, physically

- Owner manually entered fastboot with repaired Power/Volume controls, with prepared microSD inserted.
- Surface fastboot identified **exact expected experimental MZ600 serial `170061c243805617`**, product `xoom-cdma`, `unlocked=yes`. USB COM port absent initially. Verified target Stage-E image `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-V064-BIGPART-INTERNAL-P8-TRUEGPT-PARTUUID-TEMPBOOT-OFFLINE-UNTESTED.img` is **6,645,760 bytes** with SHA256 **`c91d7f40d90df5bcb058fee6f843c64b46d02190b74eee36186ba3d9b4c3c63d`**.
- Executed **`fastboot boot` once, TEMPORARY ONLY**. Surface output:
```
Sending 'boot.img' (6490 KB)  OKAY [0.613s]
Booting                       OKAY [1.381s]
Finished. Total time: 2.001s
STAGE_E_FASTBOOT_BOOT_EXIT=0
```
- Host log `captures/MZ600-V064-StageE-InternalP8-TRUEGPT-PARTUUID-TEMPBOOT-20261026-PRIVATE.log`. **NO boot partition flash; NO filesystem format or eMMC write.**
- USB `COM9` enumerated, but **NO Debian login banner**. An attempted serial write returned Windows `The semaphore timeout period has expired`, as with earlier failed Stage-C. A later retry still showed COM9 with 0 readable bytes and same serial-write semaphore timeout. Host currently sees no ADB or fastboot connection after the temporary boot. **Stage-E root mount, systemd init and Debian login NOT verified.** Owner should photograph current physical screen to confirm exact kernel wait text.
- Independently examined source and three boot images on Surface: Stage-B SD-root has `root=PARTUUID=013b61e4-01` (MBR-style PARTUUID), Stage-D proven internal-root has `root=/dev/mmcblk0p8`, Stage-E currently failing has `root=PARTUUID=<private live p8 GPT GUID>`; other cmdline tokens the same (`androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=8 ignore_loglevel printk.time=1 rootfstype=ext4 rootwait rw init=/sbin/init`). Stage-D and Stage-E differ from Stage-B only in Android boot header commandline, kernel/ramdisk otherwise byte-identical. New Stage-E GPT GUID equals the **current private p8 GUID captured by running Stage-D** during the previous boot, not the stale original GUID used in Stage-C. We have **not verified that GUID remained stable across the new boot**, a key unresolved ambiguity.

## Why this matters

**Proven Stage-D success is still authoritative:** exact same Linux7 kernel boots native Debian 12.15 with `/dev/mmcblk0p8 ext4 /` internally, and USB login + `findmnt` physically passed. Thus the p8 ext4 filesystem and Debian userspace were bootable. After Stage-D success, owner supplied sudo and we guardedly corrected ONLY the internal p8 `/etc/fstab` root PARTUUID to the then-current p8 `/sys/class/block/mmcblk0p8/uevent` GPT GUID, preserving a bytewise original backup at `/etc/fstab.before-stage-e-live-guid-20261026`; audit showed only root field differed.

**Stage-C and Stage-E with `root=PARTUUID=<full GPT GUID>` both failed to reach Debian**, while Stage-B microSD SD partition `root=PARTUUID=013b61e4-01` and Stage-D internal p8 `root=/dev/mmcblk0p8` boot. On desktop kernel source `block/early-lookup.c`, `early_lookup_bdev(PARTUUID=)` delegates to `devt_from_partuuid()` matching registered block devices' `bd_meta_info->uuid`, while direct `/dev/mmcblk0p8` resolves via `devt_from_devname()`. Kernel `block/partitions/efi.c` uses actual GPT `unique_partition_guid` for partition metadata and remaps extents separately. **This suggests a GPT-PARTUUID registration, lookup or per-boot identity issue for the virtual BigPart p8.** Exact cause NOT proven; do not assert it is just udev symlink (kernel root lookup precedes udev) or merely a stale saved GUID. The prior missing `/dev/disk/by-partuuid` symlink is a *separate userspace symptom* until proven related.

## Current device state and next safe actions

- **CURRENT physical device may be stalled in temporary Stage-E**: COM9 present, unresponsive; screen not yet rephotographed this turn. No permanent storage changes during Stage-E test, so **p7 persists Stage-B Debian SD-root** (verified image SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`). **p8 ext4 Debian 12.15 was boot-proven under Stage-D**, no reformat required. p6 TWRP/partition table not changed.
- **First: ask owner to inspect/photograph framebuffer** for possible repeated `Waiting for root device PARTUUID=` or a new kernel error. Then power-cycle normally with prepared SD inserted; normal p7 Stage-B SD-root should recover. The owner can also manually enter fastboot and use TEMP `fastboot boot` of proven Stage-D for internal-root again. **Do not flash Stage-E**.
- Next engineering investigation: inspect per-boot p8 PARTUUID under known-good Stage-D and p8 GPT metadata, check whether GUID actually changes after cold/warm boots; or use small kernel instrumentation around early `devt_from_partuuid` / BigPart metadata to print lookup result and registered p8 UUID (without leaking exact private GUID publicly). Compare `root=PARTLABEL=system` diagnostic if useful. Avoid asserting cause without data.
- Safe practical fallback for eventual internal-root default: proven **`root=/dev/mmcblk0p8`** Stage-D could be a stable boot candidate with p7 backup, but it is currently only TEMP-boot validated (no ordinary cold persistent p7 boot yet). Need explicit user approval and rollback plan before overwriting p7. Must continue addressing module uname+ vs vermagic mismatch, Wi-Fi, systemd bus as separate tasks.

