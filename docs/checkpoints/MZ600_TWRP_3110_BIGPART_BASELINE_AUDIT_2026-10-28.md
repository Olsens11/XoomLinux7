# MZ600 TWRP 3.1.1-0 BigPart recovery adaptation audit — 2026-10-28

**Owner's target: preserve TWRP 3.1.1-0. Do not downgrade to TWRP 2.x.**
**Forensic read-only inspection complete, safe replacement NOT YET BUILT.**
No Xoom partition writes, fastboot boots, flash, reboots or mounted-device changes.

## Existing image actually in p6

The owner's private Surface backup
`xoom-linux-rom/private-backups/replacement-mz600-2026-10-25/twrp-recovery-p6.img`
is a whole **12,582,912-byte** p6 block capture with SHA256
`ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`.
Its bytes match exactly the p6 region independently extracted from the
preflash `head64m.img`, the larger 2026-10-28 live raw image.
This is a verified recovery rollback source.

The recovery's Android boot-image header and compressed ramdisk were
**parsed off-device only**:
- Android magic `ANDROID!`, **2,048-byte page size**.
- Kernel **3,435,708 bytes**; gzip ramdisk **3,953,970 bytes**,
  uncompressed CPIO **7,770,880 bytes**, containing **431** entries.
- Ramdisk contains TWRP **`3.1.1-0`** version text.
- `default.prop` identifies
  `omni_wingray-eng 4.4.4 KTU84P eng.dan.20200714.225735 test-keys`.
  This is the **Wingray family recovery build used on the MZ600**;
  it is not a separate proven Stingray release.
- `etc/recovery.fstab` uses factory by-name paths including
  `/system`, `/cache`, `/data`. It has legacy length offsets
  `/system length=-4096` and `/data length=-16384`, which must be
  audited before any ext4/backup/wipe usage. `fstab.stingray` likewise
  references factory by-name devices.
- The ramdisk contains **no BigPart keyword**. This alone is not proof
  of kernel behavior, but past **physical** TWRP 3.1.1 tests explicitly
  saw the factory p8/p9/p10 map rather than the current BigPart layout.
- The kernel and TWRP UI are **separate components**. Rewriting an
  `fstab` does not change Linux block-device extents; BigPart must
  exist at the recovery-kernel partition-parser layer.

## External release search

- Official Xoom TWRP archive lists old **2.x** builds and gives no
  independently verified **3.1.1-0 BigPart for MZ600**:
  <https://dl.twrp.me/wingray/>.
- Linusdan's July 2020 Xoom TWRP **3.1.1** release is explicitly
  named `twrp-3.1.1-wingray-noBigPart-20200714-linusdan.img`:
  <https://androidfilehost.com/?fid=8889791610682892799>.
- Historical **Wingray BigPart** distributions exist at TWRP
  **2.8.6.0/2.8.1.0/2.7.1.0**, but are not accepted as replacement
  for the owner's 3.1.1-0 requirement. They may provide kernel
  implementation references; no unverified binary transplant.
- Historical original BigPart kernel implementation:
  <https://github.com/Schischu/android_kernel_moto_wingray/commit/6b3d70fff905b7395fd15992c3779b27d1b6c101>.
- The 2020 Lineage-MZ6XX project advertises a 3.x Xoom TWRP
  device-tree workstream; a complete version-locked, buildable
  3.1.1-0 + compatible BigPart kernel source chain still must be
  verified. Do not declare a ready-to-flash image based on repository
  names or search result snippets alone.

## Requirements for a candidate 3.1.1-0 BigPart build

1. Preserve TWRP **3.1.1-0** UI/features; derive a compatible kernel
   source and apply the **classic** in-memory BigPart GPT remap, not a
   new on-disk GPT. No need for SuperBigPart: the existing 1GiB
   Debian root image already passed independent 5-pass ext4 checks.
2. **Stingray MZ600 identity, eMMC geometry, and controller fail-closed
   check:** internal disk 62,521,344 sectors; p8 start=118784
   size=2097152, p9 start=2215936 size=1048576,
   p10 start=3264512 size=59247616; p1-p7 unchanged. The
   actual relocated factory GPT remains at LBA=62513151.
   A kernel must enforce this mapping *before* TWRP uses by-name
   paths. Do not rely solely on a ramdisk/fstab change.
3. Safe recovery init must **not automatically mount, repair,
   format, wipe, or write** `/system`, `/cache`, `/data`,
   p8/p9/p10 or GPT before geometry is independently confirmed.
   In particular, OEM p10 starts within currently occupied
   BigPart p8; prior TWRP behavior mounted `/data` RW.
4. Audit device paths, `length=-4096` /`-16384` offsets,
   Android recovery/adb USB availability, MZ600 display/touch,
   external microSD and restore/backup semantics.
5. Android boot-image length **must be <=12,582,912 bytes**,
   below the actual 12MiB p6 partition. Preserve exact source,
   kernel config, private/proprietary file separation, byte hash,
   bootcmdline and reproducible packaging notes.
6. **Do not flash candidate p6 first.** Prefer reversible temporary
   `fastboot boot` with a hash-verified candidate and storage
   auto-mount protections; physically prove correct sectors, device
   identity, zero internal mounts, ADB read access and UI.
7. To obtain the cold 1GiB p8 backup without involving unsafe old
   TWRP, an already **physically proven** fallback is the
   classic BigPart-aware Stage-B Debian microSD-root fastboot image
   (SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`).
   It booted with `/dev/mmcblk1p1` root and internal p8 **unmounted**.
   Use that route for cold backup if it can be reverified in the
   current state; no `fastboot flash`. Preserve both rollback and
   the new p8 image on private hosts.
8. **Only after** cold p8 backup, recovery candidate physical tests,
   verified p6 restoration route and owner-approved exact p6 image:
   consider an in-place p6 write from current Debian or
   `fastboot flash recovery`; read back exact p6 bytes and SHA,
   reboot recovery and revalidate in safe read-only mode.
   No writes to p7/p8/p9/p10 or OEM GPT as part of recovery upgrade.

## State

**Current p6 rollback = verified.**
**3.1.1-0 base = identified and analyzed.**
**Published 3.1.1-0 BigPart MZ600 binary = not verified.**
**Replacement kernel/build, physical tests, cold p8 backup, flash = OPEN.**
This is an OS/recovery engineering track and is **NOT** a modification
of the nine upstream Linux 7 kernel review patches.
