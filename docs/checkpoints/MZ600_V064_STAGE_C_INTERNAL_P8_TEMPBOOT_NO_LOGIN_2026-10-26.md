# Stage-C internal-p8-root first temporary boot: fastboot accepted, Debian login NOT observed

**Date:** 2026-10-26 approximately 03:39–03:42 EDT. Experimental replacement Motorola Xoom MZ600, protected original never touched. Current physical state **UNRESOLVED/UNRESPONSIVE Stage-C temporary boot**; not proven persistent SD rescue rebooted again. Important next operator action: use repaired physical Power/Volume controls to reset and **boot normal** into the persistent known-good p7 Stage-B Debian SD-root, keeping microSD inserted; verify /dev/mmcblk1p1 root before further software changes.

## Correct stage C test evidence

Owner successfully put Xoom in **FASTBOOT** manually using newly repaired working volume/power buttons. Surface verified exact Xoom fastboot serial `170061c243805617`, device type `xoom-cdma`, `unlocked=yes`, and Stage-C image `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-V064-BIGPART-INTERNAL-SYSTEM-ROOT-TEMPBOOT-PREINSTALL-UNTESTED.img` size **6,645,760 bytes**, SHA-256 **`15feced18d384ec532b7e3d9fb04463eac14c445909fadb5798920ee661571c8`**. Private p8 GUID saved on Surface exactly matched `root=PARTUUID=...` inside image (private GUID not committed or exposed in repo). Exactly one `fastboot boot <Stage-C image>` TEMPORARY BOOT was issued (NOT `fastboot flash`, and NO p7 write). Fastboot reports:
```
Sending 'boot.img' (6490 KB) OKAY [0.622s]
Booting OKAY [1.382s]
Finished. Total time: 2.010s
STAGE_C_FASTBOOT_BOOT_EXIT=0
```
Private log Surface `captures/MZ600-V064-StageC-InternalP8-TEMPBOOT-20261026-PRIVATE.log`.

**Crucial result: Stage-C internal-p8-root boot NOT VERIFIED.** USB `COM9` enumerated as USB Serial Device `VID_0525&PID_A4A7`, indicating early Linux USB gadget stack or equivalent hardware, but **NO Debian GNU/Linux login banner or shell output** appeared during 105 second USB-probe window. Host saw neither ADB nor fastboot after boot. Serial probe on COM9 opened port but returned Windows `The semaphore timeout period has expired` on sending a CR; physical Xoom might be stalled prior to a healthy ttyGS0 consumer or powered hung. Do not claim p8 root mounted, systemd started, or Debian boot succeeded; none was observed.

Host-side comparison of Stage-C vs proven persistent p7 Stage-B kernel+ramdisk image: both **6,645,760 bytes**, only **74 differing bytes** all within Android boot image header command-line region (0xAE–0xFD). Both cmdlines are identically structured `androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=8 ignore_loglevel printk.time=1 root=PARTUUID=[private GUID] rootfstype=ext4 rootwait rw init=/sbin/init`; only selector GUID differs (SD partition vs p8). Thus no kernel/ramdisk payload change. This focuses next debugging on root PARTUUID lookup, p8 early mount, userspace/mount setup, and the cloned image's pre-existing kernel/modules mismatch; cause of no tty login **not yet established**. No reason to format p8 again without further diagnostics.

## Proven pretest baseline (unchanged by temporary boot)

- Normal persistent p7 Stage-B Debian SD-root boot PHYSICAL PASS, p7 first 6,645,760 bytes SHA256 **`b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`**, verified p7 readback, and full p7 saved original Android boot image available privately.
- Internal p8 1GiB BigPart ext4 Debian 12.15 copied successfully, tmp/dev/sys/proc/run dirs created, copied fstab root selector changed to actual p8 GUID, root filesystem unmounted and **`e2fsck -fn` exit code 0**, 12,371 files, 129442/262144 blocks. See [p8 installation checkpoint](MZ600_V064_BIGPART_INTERNAL_DEBIAN_P8_FILESYSTEM_INSTALLED_FSCK_PASS_2026-10-26.md). Original p8 Android system 256MiB privately backed up, p6 TWRP unchanged, actual GPT not overwritten.
- **Known kernel modules mismatch:** Linux kernel `uname -r 7.0.0-next-20260422+`, SD module directory and module vermagic `7.0.0-next-20260422` without plus, so current modules not assumed loadable. Needs rebuilt matching modules.
- Owner reports repaired both Volume button and DC charging jack; physical fastboot/recovery entry works. Software `reboot bootloader` from Linux7 previously returned Android (historical), NOT a trusted recovery mechanism.

## Safe next actions

1. **Owner physical reset / power into normal p7 Debian SD-root**. Since `fastboot boot` made no persistent change, normal power-on with the prepared 32GB microSD inserted should boot known-good Stage-B SD-root if power/recovery state permits. If stuck, use repaired physical fastboot controls and issue `fastboot reboot` after verifying device identity. Do NOT flash Stage C.
2. Once SD-root Debian is back, read boot-time evidence (`dmesg`, pstore if supported, p8 superblock via offline read, `/etc/fstab` and cloned `/sbin/init` symlink); confirm p8 partition by the GUID and kernel BigPart map. Consider next Stage-C diagnostic kernel/ramdisk with framebuffer error reporting or an initramfs emergency shell that mounts p8 and prints reason for failure—no permanent flash.
3. Keep p7 SD rescue and p6 TWRP, and never claim p8 boot pass until actual `findmnt -n -o SOURCE,FSTYPE /` shows **`/dev/mmcblk0p8 ext4`** on working internal-root Debian login.
4. Continue updating main handoff and runtime state with every test; do not assume unresponsive COM9 is successful login.


## Prepared additional OFFLINE diagnostic Stage-D (not booted or flashed)

To isolate GUID-specific root-lookup behavior from device-node-based root selection, created a **new host-only diagnostic image** from the proven known-good Stage-B boot image using `scripts/experiments/stage-v064-bigpart-p8-devnode-diagnostic-boot-20261026.py` in the same GitHub branch. The builder checks Stage-B input bytes/size/hash and edits ONLY the legacy Android boot image command line: `root=PARTUUID=<known SD id>` → `root=/dev/mmcblk0p8`, preserving `rootwait rootfstype=ext4 rw init=/sbin/init`. The kernel and ramdisk remain identical. This is **a diagnostic alternative**, not a preferred final root naming convention; p8 PARTUUID remains the desired stable design once the problem is understood.

**Private Surface path:** `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img`. **Bytes 6,645,760**, **SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`**, with adjacent host-only manifest. Built and independently SHA-verified on Surface. **NO Stage-D fastboot boot or flash has occurred**. Do not try it until known-good SD-root rescue is restored and owner again enters fastboot with repaired buttons.

**Additional hypothesis, unproven:** The p8 GPT PARTUUID exists in kernel `/sys/class/block/mmcblk0p8/uevent`, but earlier minimal SD Debian's userspace `/dev/disk/by-partuuid` link for p8 was absent. This might make an internal PARTUUID-based systemd fstab dependency stall even when kernel can find p8. Direct block-device naming Stage-D may help distinguish the issue. Do not claim cause proven and do not rewrite permanent p7 without Stage-D temporary boot validation.


## New owner-supplied PHOTOGRAPH: Stage-C failure localized to ROOT PARTUUID resolution

**2026-10-26:** Owner sent a clear photograph `PXL_20261026_075012822.jpg` of the experimental MZ600 framebuffer from the stalled Stage-C temporary boot. This is stronger evidence than the previous host-side absence of a login. The device itself explicitly prints (GUID omitted from committed documentation for privacy):

```text
[~0.945] mmcblk0: MMC32G 29.8 GiB
[~0.957] MZ600 BigPart: probing relocated OEM GPT at sector 62513151
[~0.958] Primary GPT is invalid, using alternate GPT.
[~0.958] MZ600 BigPart: validated exact factory 10-partition GPT; virtual
         system 1GiB, cache 512MiB, userdata 28929.5MiB
[~0.958] mmcblk0: p1 p2 p3 p4 p5 p6 p7 p8 p9 p10
[~1.875] Waiting for root device PARTUUID=<actual private p8 GPT GUID>...
[~11.35] platform sound-hdmi: deferred probe pending: asoc-simple-card: parse error
[~31.19] vdd_led / ucsi / vrf2 / vrfref / uusb: disabling
[~73.49] random: crng init done
```

The screenshot confirms **kernel, eMMC, relocated GPT, BigPart remap and partition enumeration ALL WORK**, and independently localizes the unbootable Stage-C to the kernel's inability to resolve its `root=PARTUUID=...` selector in early mount. It is NOT a normal Debian/systemd boot, and the failure precedes loading root filesystem; the module ABI mismatch cannot itself explain this specific pre-mount `Waiting for root device` screen. The `asoc-simple-card` sound-hdmi message is a separate pre-existing deferred-probe issue and is not shown to be causal. Do not treat mere COM9 USB enumeration as successful root mount. Kernel continues logging to screen at least through t+73.5 sec rather than producing a Debian login.

**Targeted source-level rationale:** In current Linux7 `block/early-lookup.c`, `early_lookup_bdev(`PARTUUID=...`)` dispatches to `devt_from_partuuid()` and uses `struct block_device->bd_meta_info->uuid` partition metadata. The kernel exposes the verified BigPart p8 block device `mmcblk0p8`, but this message implies early root-PARTUUID lookup failed despite enumerated p8. We must inspect real `/sys/class/block/mmcblk0p8/uevent` metadata on restored Stage-B SD-root and compare the actual PARTUUID **privately** to cmdline recorded in framebuffer; determine whether enumeration-time metadata is mismatched, missing, or the root selector is malformed. Do not infer one precise underlying cause from this screenshot alone.

**Plan now sharpened:** Existing **offline-only Stage-D** SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8` uses `root=/dev/mmcblk0p8` instead of PARTUUID and keeps same exact kernel+ramdisk. This will be a discriminating *temporary fastboot boot* diagnostic with no write/flash. The tablet is still in Stage-C stall with Surface COM9 present, no fastboot/ADB. Owner's repaired physical volume/power controls can reset and manually enter fastboot. **Next operator input:** have owner enter fastboot with microSD kept inserted; run exact SHA-verified Stage-D using host `fastboot boot` TEMP ONLY, photograph result if failure. On any failure, normal hardware boot uses unchanged persistent p7 Stage-B SD-root. Do not format p8 again or flash permanent boot.

