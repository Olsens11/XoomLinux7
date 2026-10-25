# MZ600 normal Linux microSD boot test: fastboot screen persists; isolated test image prepared

**Date:** October 25, 2026. **Status:** user physically reports the Xoom is **still displaying the fastboot screen** after a successful `fastboot boot` command. USB host sees **no live fastboot, ADB or CDC ACM device** after handoff. No kernel boot confirmation, no Linux login. **Do not infer that the bootloader is still executing only from an unchanged screen**—framebuffer can retain old pixels if not cleared; no direct kernel console observations are available yet.

## Physical evidence
- MicroSD Debian Bookworm armhf ext4 installation was previously verified (full hash readback, resize2fs to 7,633,152 4KiB blocks, e2fsck success). Internal eMMC Android boot, system, userdata, TWRP recovery remain unchanged.
- Bootloader had reported `SEND OKAY` / `BOOT OKAY` for prior *nonpersistent* normal Linux boot image; `fastboot` and ADB subsequently vanished from USB and Surface has no live serial/COM. User now confirms the old fastboot display remains. This neither proves that the CPU stayed in fastboot nor identifies the failing kernel stage.
- Existing normal Linux boot image SHA256 `8bb0a98bab1a5043ab335a21a92fb43cf505a060d3c976e283ebdb60e1b9230d`, **5,890,048 bytes**, contains 5,887,396-byte kernel+appended DTB, **zero-byte ramdisk**, cmdline `root=PARTUUID=[private]-01 rootfstype=ext4 rootwait rw init=/sbin/init`. There is no early initramfs logging or root-mount instrumentation.
- Pinned clean kernel build `CONFIG_ARM_APPENDED_DTB=y`, `CONFIG_ARM_ATAG_DTB_COMPAT=y`, `CONFIG_MMC_BLOCK=y`, `CONFIG_MMC_SDHCI_TEGRA=y`, `CONFIG_MSDOS_PARTITION=y`, `CONFIG_EXT4_FS=y`, `CONFIG_USB_CHIPIDEA_TEGRA=y`, `CONFIG_USB_G_SERIAL=y`, `CONFIG_FRAMEBUFFER_CONSOLE=y`. Board DTB has SDMMC1 `disabled`, SDMMC2 `okay` (BCM4329 SDIO), SDMMC3 `okay` (removable microSD), SDMMC4 `okay` (eMMC). Compile-time presence does not prove runtime initialization.
- **Physical known-working** v034 temporary diagnostic boot image on Surface: `MZ600-v034-HCI-IOCTL-TEMPBOOT-ONLY.img`, SHA256 `9850361687f6d121119a0c3399cdc0abaa68d8e9714238aba5bb9b7207a0af39`; **6,979,584 bytes**. Its Android boot header matches the new candidate's **kernel addr `0x10008000`**, ramdisk addr `0x11000000`, tags `0x10000100`, page size 2048 and no separate DT section. Unlike the normal image, it includes a **702,207-byte gzip initramfs**, SHA256 `7e4eeca0119914693ac243c1cf50d6ef9b36a40d78cf016c32e4b8b136af967b`, and uses `rdinit=/init`. Original v034 kernel payload was 6,274,199 bytes vs clean kernel's 5,887,396 bytes. This is a controlled variable for next test, *not* proof that an empty ramdisk caused the new failure.

## New local controlled test, NOT YET BOOTED

Recovered known-working v034 gzip ramdisk bytes from the previously physically validated v034 boot image, re-verified SHA256. Created a **temporary/nonpersistent hybrid** using only:
- same **clean Linux 7 kernel and appended USB0-peripheral Stingray DTB** used by the normal Debian boot candidate,
- byte-identical v034 diagnostic initramfs,
- compatible bootloader header, `console=tty0 loglevel=7 printk.time=1 rdinit=/init` (diagnostic, not Debian root).
- NEW temporary hybrid filename **`xoom-new-kernel-proven-v034-initramfs-TEMPBOOT.img`**, **6,592,512 bytes**, SHA256 **`67b1fc6b6dc3e673a5eb610cdc5dd96347e60a89c8f715b215344bf8e1bb2743`**. Built Desktop WSL under `/home/xoomdev/xoom-linux-rom/os-build/earlyboot-diagnostic-20261025/`; transferred by existing authorized SSH/SCP LAN to Surface `C:\Users\olsen\xoom-linux-rom\downloads\` and verified exact SHA256 and size on Surface. **No new GitHub binary published. No Xoom partition writes.**

**Interpretation of future outcomes:**
- Hybrid physically draws v034 diagnostic screen and/or enumerates familiar USB: clean kernel/DTB/bootloader can start; investigate `root=PARTUUID` storage discovery, early root handoff, systemd/getty/USB rather than assuming bootloader failure.
- Hybrid fails identically (stale bootloader display, no USB): compare clean kernel and DT startup and gadget/memory setup versus the proven working v034 kernel; move to instrumented early init, UART/kmsg framebuffer as possible.
- Successful hybrid runtime may have mismatched old v034 loadable Wi-Fi/BT modules (kernel release/ABI); only use its core display/USB and static diagnostics for early boot, not WLAN F2 acceptance. It is **not** an installed Debian OS.

## Necessary physical action before next command

After the user confirms screen state, a **manual power-button long press / full power cycle** is needed because the Surface currently sees no USB connection of any kind and thus cannot send ADB/fastboot commands. Power back on into normal existing Android (p7 unchanged) and use ADB to re-enter bootloader; then run hash-guarded `fastboot boot` on the temporary hybrid only. No permanent flash, no changes to SD filesystem beyond already-installed Debian. Preserve recovery and Android. When hybrid tested, document screen AND host USB behavior.

This checkpoint supersedes only the unresolved first-boot portion of [physical microSD Debian installation](MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md). All BCM4329 v045 physical success and verified SD-root contents remain intact.
