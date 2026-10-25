# 32 GB microSD discovered; normal Linux 7 root images prepared OFFLINE

**Date:** 2026-10-25. **Status:** SD card detected and checked read-only; per-card native kernel/ext4 boot pair built and verified **OFFLINE**, **NO MICROSD OR INTERNAL PARTITION WRITE**. *Explicit per-media destructive-format permission still required.*

## User-provided removable medium / device identity

User inserted a 32GB microSD in the **replacement** MZ600 while TWRP 3.1.1-0 was running. One ADB recovery device root uid0. Recovery added **`/dev/block/mmcblk1`** (removable card) and **`/dev/block/mmcblk1p1`**. **`/dev/block/mmcblk0` remains the internal eMMC: do not write it.** Physical card size per sysfs 61,067,264 × 512-byte sectors = 31,266,439,168 bytes (~29.12 GiB). Removable p1 currently starts LBA64 and occupies 61,067,200 sectors. `ro=0` capability only, not user permission to write.

The current card has a valid DOS/MBR boot sector, one **type 0x0B FAT32** partition, filesystem label **`DISK_IMG`**, standard FAT UUID and no other partitions. It was mounted explicitly **read-only** from `/dev/block/mmcblk1p1` at a TWRP RAM `/tmp/sd_ro` path:
- vfat `ro,nosuid,nodev` confirmed in mount table.
- `df -k` reported 30,518,672 KiB total, **16 KiB used**, 30,518,656 KiB free; directory listing contained **no files**.
- Read-only block tests of the card at beginning, offset 100 MiB and offset 10,000 MiB each read 16 MiB successfully (~17–18 MB/s).
- Initial card insertion logs did show two temporary `mmc1` re-detect timeouts `-110` followed by a successful third SDHC enumeration; monitor connection reliability during larger reads/writes.
- The exact original MBR first sector (512 bytes) has been backed up privately to `C:\Users\olsen\xoom-linux-rom\private-backups\replacement-mz600-2026-10-25\inserted-32gb-microsd-original-mbr-512.bin`, SHA256 `29e1bb4263738efbcaf87a02b6a908c0db6f2f8ab53f9d7972e31fa55cf23acf`. A private host Python script verified `0x55AA`, nonzero 32-bit MBR signature, the exact single partition table entry, and the corresponding MBR `PARTUUID`. **Do not publish device-specific disk signature/card ID in the public repository.**

## Correct installation design

This card uses **DOS MBR**, not GPT, so **`root=PARTLABEL=xoom-linux` is the wrong kernel selector**. For a conventional ext4 root partition on this card, use stable **`root=PARTUUID=<private-card-disk-signature>-01`**, with the matching entry in Debian `/etc/fstab`. DOS-MBR PARTUUID is derived from the 4-byte MBR disk signature plus the 1-based partition number; it is **not** FAT32 UUID or ext4 filesystem UUID. The source builder accepts an explicit `XOOM_LINUX_ROOT_PARTUUID` environment variable and validates `8 hex digits + -01..-04`. Never embed that media-specific identifier in the generic public source.

The current card partition starts at LBA64, a legacy 32 KiB alignment. A more conventional reformat will change only **the microSD's partition table** to one Linux type-0x83 MBR partition with 1 MiB alignment and use its remaining space, *after permission*. Preserve the MBR disk signature to keep the planned PARTUUID stable. The card has no content to preserve, but changing its MBR / FAT32 and formatting ext4 is still a destructive, user-specific write. It has **NOT** happened yet; no eMMC/Android alteration authorized.

Keep existing Android `boot`, `system`, `userdata`, TWRP `recovery`, and old original protected Xoom all untouched. First bring up normal Debian from the **microSD filesystem** using a temporary boot of the validated normal Linux kernel image; this does not make the temporary diagnostics environment the OS. A persistent Linux boot selector can be considered separately, with existing Android HMJ37 boot backup (SHA256 `4DA4...`) and explicit per-partition authorization.

## Prepared OFFLINE files (user's desktop)

On Desktop WSL: `/home/xoomdev/xoom-linux-rom/os-build/artifacts-microsd-20261025/`:

- `xoom-linux-boot.img` **5,890,048 bytes**, SHA256 **`8bb0a98bab1a5043ab335a21a92fb43cf505a060d3c976e283ebdb60e1b9230d`**. Its Android-format kernel container has empty diagnostic ramdisk and normal root command line `root=PARTUUID=<private>-01 rootfstype=ext4 rootwait rw init=/sbin/init`.
- `xoom-linux-root.ext4` **805,306,368 bytes (768MiB)**, SHA256 **`7ab44285a110626f8533ba46fb43837827c5fa565ef48a254dd92dd432e1c746`**.
- `SHA256SUMS`, `NOT_INSTALLED.txt` and the validated zImage+USB0 UDC DTB.
- Both images passed `scripts/os/verify-offline-native-os.py` with correct MBR PARTUUID and matching `/etc/fstab`, exact verified broadcom firmware/NVRAM, separate upstream WCC, no tracing code, standard USB serial getty, current first-login owner account, ext4 integrity, and no static MAC.
- **Important ext4 compatibility change:** desktop `mkfs.ext4` by default enabled `64bit` and `metadata_csum`, while TWRP's `resize2fs` is 1.41.14. The packager now explicitly creates ext4 with `-O ^64bit,^metadata_csum`. Verified resulting feature list: `has_journal ext_attr resize_inode dir_index filetype extent flex_bg sparse_super large_file huge_file dir_nlink extra_isize`. This reduces the old recovery resize compatibility risk, but **physical grow/resize is not yet tested**.
- The packager updates fstab **before** generating the filesystem image. Earlier script revision had a faulty escaped regex/newline and then an unsupported `orphan_file` option, both corrected and source-build re-run to PASS; do not reuse their aborted outputs.

## What is still required

1. Receive **explicit consent to erase the inserted empty 32GB card** to install Linux at **`/dev/block/mmcblk1` / p1**. The current statement that a card was inserted is not itself an unambiguous instruction to format it.
2. On TWRP verify unchanged exact card size, DOS MBR signature/hash and by-device path, unmount the read-only inspection mount, and ensure only the removable card will be written.
3. Create 1MiB-aligned single type-0x83 Linux MBR partition on the **removable** card, preserving original disk signature for PARTUUID; reboot or reread partition table. **NEVER** alter eMMC `mmcblk0`.
4. Write full 768MiB ext4 root image to new microSD p1, verify readback SHA256, and extend ext4 to card's partition end using supported `resize2fs` after `e2fsck` (or use another previously tested robust method); verify full Linux OS contents and `PARTUUID` resolution.
5. Temporarily boot *normal* Linux kernel with actual microSD root without changing Android boot p7, verify Debian userland + USB ttyGS0, SD mount and correct Motorola bootloader MAC property. Do not scan/associate until unique MAC and regulatory provenance are qualified.
6. Separately decide persistent boot selection only after the normal microSD-root boot passes. Restore verified Android boot p7 to return; leave recovery p6 and existing Android system/data intact.

**Current physical state:** replacement MZ600 TWRP 3.1.1-0, root ADB; removable SD inserted, mounted read-only at RAM `/tmp/sd_ro`; Android eMMC unchanged. This is not yet an installed Linux OS. 
