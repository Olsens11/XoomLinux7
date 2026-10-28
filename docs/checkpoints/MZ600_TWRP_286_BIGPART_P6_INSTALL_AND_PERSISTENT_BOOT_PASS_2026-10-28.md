# MZ600 TWRP 2.8.6.0 BigPart — p6-only install, readback and persistent boot PASS (2026-10-28)

**DUT:** experimental replacement Motorola Xoom MZ600 CDMA; original Xoom protected and untouched. Owner explicitly authorized replacing **p6 recovery only**. Executed from root ADB in a *temporary RAM-booted recovery*. No other internal partition written.

## Sources and rollback

- Original Schischu/matt4321 TWRP 2.8.6.0 Wingray BigPart ZIP, original `recovery.img` **9,129,984 bytes**, SHA-256 `81d7d118cb156b0a2fe7f4f6b46c870ef1d00b9047cb1e0cb11a1ebf259cfbc8` (not the restricted experimental variant). Android boot image; 2.6.39.4-ElementalX-Xoom-2.0+ kernel.
- Original full 12,582,912-byte p6 private Surface backup `private-backups/replacement-mz600-2026-10-25/twrp-recovery-p6.img`: SHA-256 `ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`. Independently matched actual live p6 **before** write; keep rollback image immutable.
- Official project transfer SOP: Desktop WSL to isolated Windows staging, port 43157 HTTP on desktop LAN interface, Surface Invoke-WebRequest and SHA verification. Server stopped, port closed, temporary stage deleted. Private Surface image `captures/MZ600-TWRP286-BigPart-original-20261028-A/recovery.img` remains.

## Physical verification and p6 installation

- Original image successfully temporarily started with `fastboot boot`, not flash. ADB root established and model `MZ600` proved from bootloader kernel command line. Recovery self-reports Wingray, but physical tested device is CDMA MZ600.
- Exact internal eMMC (called `mmcblk1` by TWRP, versus `mmcblk0` in Linux 7): 62,521,344 sectors. p6 start=77,824 size=24,576 sectors (12MiB); p8 start=118,784 size=2,097,152; p9 start=2,215,936 size=1,048,576; p10 start=3,264,512 size=59,247,616. All physically matched required classic BigPart mapping.
- Initial temporary boot verified root ADB, no internal auto-mount, and `/dev/block/mmcblk1p8` successfully mounted as Debian ext4 via `mount -t ext4 -o ro,noload ... /system` (reported `ro,norecovery`). Read `/etc/os-release` Debian Bookworm and unmounted.
- Live p6 full hash before write matched historical rollback. Staged exact new image into RAM as `/tmp/mz600-twrp286-p6-authorized.img`, on-tablet SHA matched.
- **Only authorized persistent write:** `dd if=/tmp/mz600-twrp286-p6-authorized.img of=/dev/block/mmcblk1p6 bs=4096 count=2229`. Kernel reported 2229+0 records in/out, 9,129,984 bytes. `sync` complete.
- Independent postwrite **image-prefix** readback `dd if=/dev/block/mmcblk1p6 bs=4096 count=2229 2>/dev/null | sha256sum` exactly matched `81d7d118cb156b0a2fe7f4f6b46c870ef1d00b9047cb1e0cb11a1ebf259cfbc8`. This verifies the first 9,129,984 bytes, not padded trailing bytes of full p6.
- `adb reboot recovery` succeeded. ADB disconnected then reconnected with new transport; `/proc/cmdline` had bootloader `rec` flag: **installed p6 recovery independently boots**. Postrestart p6 prefix SHA and all p8/p9/p10 sector boundaries again matched.
- On both recovery starts `/sdcard` rescue microSD was auto-mounted **read-write**; remounted **read-only** after each, and `/proc/mounts` independently verified it was `ro`. No internal p8, p9 or p10 filesystem auto-mounted.

## Scope and remaining gates

**PASS:** installed TWRP 2.8.6.0 BigPart on MZ600, root ADB, p6 readback, reboot-to-installed recovery, correct BigPart mapping, Debian ext4 read-only no-journal mounting and unmounting. Old p6 rollback and separate cold p8 backups retained.

**OPEN:** TWRP GUI touch, internal RW mount, repair, backup/restore features, and safe handling of p9/p10. Do not use wipe/format or infer full recovery qualification. TWRP automatically mounts external rescue microSD RW on boot; avoid unnecessary writes.

**Preservation:** cold p8 original 1GiB SHA `a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346` exists separately on SD and Surface. Prior read-only `e2fsck` found one free-block bitmap/count mismatch, with no repair or restore rehearsal yet. Do not write p8 until a **disposable duplicate** restore/fsck procedure passes. p10 has no complete backup.

**Upstream integration:** Recovery is an INTERNAL INTEGRATION milestone, not a tenth kernel patch. The clean XoomLinux7 nine-patch Linux kernel (source tip `507eb069df819cb5cc801ad8be096f70d9ca7609`) and new 1GiB Bookworm root remain offline-built only, not physically booted/installed. Next: disposable cold p8 clone/restore proof; separately temporary-boot exact nine-patch kernel with matching modules, correct Stingray DTB and `gpt xoom_bigpart=1`. Persistent p7/p8 writes require separate explicit owner authorization.