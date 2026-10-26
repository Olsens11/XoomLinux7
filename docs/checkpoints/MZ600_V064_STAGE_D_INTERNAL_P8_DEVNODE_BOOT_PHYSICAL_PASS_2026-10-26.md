# 2026-10-26 MZ600 v064 — Stage-D **internal BigPart p8 Debian root physically BOOTED**, GPT PARTUUID discrepancy isolated

**Time**: 2026-10-26 roughly 03:58–04:08 EDT. **Device**: authorized experimental replacement Motorola Xoom MZ600, fastboot serial `170061c243805617`, product `xoom-cdma`, unlocked=yes. **Never touch the owner's protected original Xoom.** This checkpoint supersedes the [Stage-C failed internal PARTUUID boot](MZ600_V064_STAGE_C_INTERNAL_P8_TEMPBOOT_NO_LOGIN_2026-10-26.md).

## Physical successful Stage-D boot, using NO persistent flash

1. The owner manually entered fastboot using working **repaired Volume/Power buttons**. Surface verified expected serial `170061c243805617`, product `xoom-cdma` and `unlocked=yes`. A SHA-gated **Stage-D diagnostic image** `MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img`, **6,645,760B**, **SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`**, was selected. This image derives byte-for-byte from proven Stage-B except Android boot v0 cmdline `root=/dev/mmcblk0p8`; same kernel, ramdisk, rootwait, ext4, and systemd init.
2. Surface issued **only `fastboot boot`**, not `fastboot flash`. Actual host response: `Sending 'boot.img' (6490 KB) OKAY [0.914s]`, `Booting OKAY [1.093s]`, total 2.015 s, native fastboot exit0. Private log Surface `captures/MZ600-V064-StageD-InternalP8-DEVNODE-TEMPBOOT-20261026-PRIVATE.log`.
3. USB `COM9` returned the real screen `Debian GNU/Linux 12 xoom-mz600 ttyGS0`, `xoom-mz600 login:`. Existing Surface `downloads/xoom-debian-serial-first-login-probe.ps1` privately authenticated the unprivileged `xoom` account (credential never shown, fetched, committed, or logged), yielding real live shell `xoom@xoom-mz600:~$`.
4. **Critical physical root proof** from the running Debian shell:
   ```text
   Linux kernel: 7.0.0-next-20260422+
   Debian version: 12.15
   findmnt -n -o SOURCE,FSTYPE,TARGET /
   /dev/mmcblk0p8 ext4 /
   findmnt -n -o SOURCE,FSTYPE,OPTIONS /
   /dev/mmcblk0p8 ext4 rw,relatime
   /sys/class/block/mmcblk0p8/start: 118784
   /sys/class/block/mmcblk0p8/size: 2097152
   ```
   The **internal p8 root is REAL, MOUNTED, READ/WRITE AND RUNNING SYSTEMD LOGIN**; root is NOT on removable SD. This fully proves the copied internal Debian userspace and p8 ext4 are bootable. Retain prepared 32GB SD for rescue.
5. Read-only extra tests: p8 `/sys/class/block/mmcblk0p8/uevent` has `PARTNAME=system` and valid 36-character `PARTUUID`. Device-tree Wi-Fi `local-mac-address` property present, but `wlan0` absent (only lo/sit0/ip6tnl0), systemctl bus still reports `Failed to connect to bus: No such file or directory`, and `/lib/modules/$(uname -r)` absent due preexisting **7.0.0-next-20260422+ kernel vs 7.0.0-next-20260422 module folder and vermagic** mismatch. Those issues remain separate and **did not prevent p8 boot**.
6. **NO p7 permanent flash, NO p8 format, NO recovery p6 write or GPT write** in Stage-D test. p7 retains physically verified persistent Stage-B Debian SD-root image SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`, which is the normal restart fallback with microSD installed.

## Why Stage-C failed: GPT partition UUID discrepancy

- Earlier Stage-C temporary boot using a full GPT PARTUUID selector stopped on physical framebuffer `Waiting for root device PARTUUID=...` although kernel enumerated internal p8 with correct 1GiB BigPart mapping. Stage-D same kernel with `root=/dev/mmcblk0p8` **boots**, so earlier issue is **root selector identity/resolution** rather than inability to mount internal ext4.
- On running Stage-D internal-root Debian, the **kernel's actual current p8 PARTUUID** is a valid 36-character GPT UUID with `PARTNAME=system`. The earlier privately saved p8 GUID (`private-backups/replacement-mz600-2026-10-25/P8-BigPart-Partition-UUID-PRIVATE.txt`) and Stage-C boot image match **each other**, but **do not match p8 or ANY of the ten current kernel-reported p1–p10 partition GUIDs**. The copied internal `/etc/fstab` root PARTUUID also **does not match the current kernel p8 partition GUID**. Thus old stored identifiers were stale/incorrect relative to the live kernel's GPT metadata. Whether the identifiers actually varied across boots or were initially captured from the wrong context is **NOT YET DETERMINED**. Do **not** conclude that kernel PARTUUID lookup is generally broken; test with correct live GUID first.
- A distinct **live, read-only physical kernel p8 PARTUUID** was captured via running internal Debian `/sys/class/block/mmcblk0p8/uevent` after verifying `/dev/mmcblk0p8` was actual mounted `/` and p8 sector count. Kept **only on Surface private backup path** `private-backups/replacement-mz600-2026-10-25/P8-BigPart-Partition-UUID-LIVE-VERIFIED-20261026-PRIVATE.txt`. Clean text file length **38B**, SHA256 **`000ea863f8ae2651543cf30b0fc9f6fe6b4f453ada8ea01fdbdea65f3aa27ae3`**. The old UUID text file remains available for forensics. Do NOT expose raw physical GUID in GitHub or chat when a private local value suffices.
- Source code `block/early-lookup.c`: early `root=PARTUUID=` lookup searches `bd_meta_info->uuid`. Device-specific `block/partitions/efi.c` reads per-entry `unique_partition_guid` from OEM GPT and sets `info->uuid` for each virtual BigPart partition, so dynamic random generation is NOT apparent from this function. Need investigate how earlier saved GUID was captured or whether alternate GPT metadata is inconsistent; **still unconfirmed**.

## New corrected Stage-E candidate prepared — OFFLINE, NEVER BOOTED/FLASHED

- New GitHub builder `scripts/experiments/stage-v064-bigpart-p8-true-gpt-partuuid-boot-20261026.py`, adapted from proven Stage-C builder but uses only a **new live-captured p8 PARTUUID** input file, legacy Android v0 cmdline changed in Stage-B, kernel/ramdisk/boot addresses byte-identical. Private GUID never stored in source or manifest.
- Surface offline-only image `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-V064-BIGPART-INTERNAL-P8-TRUEGPT-PARTUUID-TEMPBOOT-OFFLINE-UNTESTED.img`: **6,645,760B**, SHA256 **`c91d7f40d90df5bcb058fee6f843c64b46d02190b74eee36186ba3d9b4c3c63d`**, generated with strict Stage-B source SHA gate, local captured full p8 GUID input, and verified host SHA after build. **NOT flashed or temporarily booted yet.** Keep working Stage-D running until installed fstab is corrected and backed up.

## Required next actions

1. **While Stage-D still running from internal p8**, owner opens Surface's USB console and enters `sudo -s` with personal Debian password locally (password must never be printed or pulled by connectors). Then Ctrl+] disconnects and frees COM9 for controlled admin commands.
2. With root, verify again that `findmnt -n -o SOURCE /` is `/dev/mmcblk0p8`, kernel's live `/sys/class/block/mmcblk0p8/uevent` p8 GUID is well formed, check identity before *backing up and correcting ONLY internal p8 `/etc/fstab` root line* to `PARTUUID=<actual current kernel p8 GUID> / ext4`. Keep prior fstab as backup and leave microSD's own fstab untouched; validate result read-only. Assess missing `/dev/disk/by-partuuid` userspace symlink separately; may affect systemd mount configuration. Be cautious because this is the live mounted root.
3. Use owner's functioning manual fastboot path, SHA-gated `fastboot boot` of **Stage-E TEMPORARY ONLY** and prove `findmnt /` = p8. If Stage-E works, PARTUUID root lookup with proper identifier is restored. Still do not flash p7 until owner approves persistent switch, and retain Stage-B SD rescue image and original p7 backup.
4. Fix module release/vermagic mismatch with correctly rebuilt, symbol-matched modules; Wi-Fi scan/systemd bus later. No kernel/devnode alias hacks without evidence.

