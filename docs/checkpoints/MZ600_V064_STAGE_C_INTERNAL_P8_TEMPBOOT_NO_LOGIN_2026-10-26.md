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

