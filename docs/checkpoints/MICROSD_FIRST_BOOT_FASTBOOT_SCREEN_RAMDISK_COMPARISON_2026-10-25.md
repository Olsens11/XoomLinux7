# First normal Debian boot: fastboot screen persists, USB absent — controlled ramdisk comparison ready
**Date:** October 25, 2026. **Target:** replacement Xoom MZ600, clean installed Debian microSD root (SD install and expansion already physically verified). **Current status:** FIRST NORMAL OS BOOT UNCONFIRMED; **NO INTERNAL EMMC WRITES**.

## Direct physical user observation and remote USB
After `fastboot boot` returned `Sending OKAY` and `Booting OKAY` for the clean Debian boot image, the user reported **the tablet remained at the fastboot screen**. Remote Surface found **no present USB serial COM, ADB, fastboot, Motorola VID/PID or Linux gadget VID_0525**, and a historical COM9 PnP entry was disconnected. This is **not proof of a completed Linux boot**, and also not sufficient to distinguish a stopped kernel from a kernel stalled at `rootwait` or a USB gadget initialization problem. We **do not claim a root-mount, PID1, or display success**.

The **32GB microSD installation remains physically verified** by full first-768MiB SHA readback, `resize2fs`, `e2fsck -fn` exit 0 and a read-only successful mount including Debian `/etc/debian_version=12.15`, root fstab MBR PARTUUID, installed WCC and ttyGS0 login service. None of these facts depends on first boot succeeding. EMMC Android boot/system/userdata and TWRP recovery were not flashed, formatted or altered during this trial.

## Source and boot-image comparison

- Pinned Linux kernel `xoom-linux/linux@2404d273...`, device kernel build branch `os/mz600-native-rootfs-wifi-20261024`. Modern system is Linux 7 `7.0.0-next-20260422`.
- Offline Linux kernel config diff against previously working diagnostic image shows only removal of `CONFIG_INITRAMFS_SOURCE=` built-in cpio, initramfs compression/UID/GID no longer selected because no payload, and intentional disabling of Broadcom optional debug/tracing. Essential `CONFIG_MMC_BLOCK=y`, `CONFIG_MMC_SDHCI_TEGRA=y`, `CONFIG_EXT4_FS=y`, `CONFIG_USB_G_SERIAL=y`, `CONFIG_ARM_APPENDED_DTB=y`, `CONFIG_ARM_ATAG_DTB_COMPAT=y`, `CONFIG_ARM_ATAG_DTB_COMPAT_CMDLINE_EXTEND=y` remain. Device Tree `tegra20-motorola-stingray-usbdiag.dtb` is **byte-identical** to previously working build, SHA256 `afae7fb328bc66c0ea186ef6c8e77164c41be8588bb5d14303374a3545499959`.
- Previous working v15 boot-image packager [`scripts/build/v15-package.sh`](../../scripts/build/v15-package.sh) used `--ramdisk <373 KiB cpio.gz>` **as well as** the diagnostic kernel's *embedded* `CONFIG_INITRAMFS_SOURCE` initramfs and specified `rdinit=/init`. Our normal OS image has **zero boot-image ramdisk bytes** and no embedded initramfs, using real SD root `root=PARTUUID=<private card>-01 rootfstype=ext4 rootwait rw init=/sbin/init`.
- **Hypothesis to test, not proven:** legacy Xoom fastboot/ATAG boot path may require a nonempty Android-format boot-image ramdisk. Other valid possibilities include early kernel failure, MMC/MBR root discovery, boot command-line collision from ATAG CMDLINE_EXTEND, and USB0 gadget early bind. Don't claim a conclusive root cause yet.

## Controlled next boot image staged OFFLINE only

Desktop build script **`C:\Users\olsen\Downloads\build-xoom-legacy-ramdisk-compat.py`**:
1. Verifies SHA256 of original root-from-microSD normal boot `xoom-linux-boot.img` exactly **`8bb0a98bab1a5043ab335a21a92fb43cf505a060d3c976e283ebdb60e1b9230d`**.
2. Reads exact boot cmdline and kernel payload and constructs a **71-byte** compressed valid `cpio newc` ramdisk **with directory `dev` only, no `/init`**, so kernel should still mount *actual Debian microSD root* if it progresses. No boot cmdline, kernel, FDT, or installed root change.
3. Invokes the same working `mkbootimg` and memory layout as the prior image (`2048` page, kernel addr `0x10008000`, ramdisk addr `0x11000000`, tags addr `0x10000100`).
4. Independently verifies boot header, payload byte identity, command-line bytes, initramfs decompress/contents, header SHA-1 and image size.

**OFFLINE validation:** `BOOT_COMPARISON_OFFLINE_PASS`, `EXACT_KERNEL_AND_CMDLINE_UNCHANGED=True`, `EXTERNAL_RAMDISK_HAS_NO_INIT=True`; no device writes.
- Controlled next **TEMPBOOT-ONLY** image: `C:\Users\olsen\xoom-linux-rom\downloads\xoom-linux-boot-sd-legacy-ramdisk-only-TEMPBOOT.img`, size **5,892,096 bytes**, SHA256 **`d4a76ef50b52882db5237a4a2975645b8615a20ef2692d61d1ed905457306a45`**.
- Also staged the prior **known-working diagnostic v15 temporary boot** for an independent bootloader/recovery comparison (not production OS): `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-v15-known-working-reference-TEMPBOOT.img`, size **6,656,000 bytes**, SHA256 **`47db713acd8e2df8a0b90e8bec24bcfd241cdbfc6d7d9837440b6d6b0b78ed04`**. Previously validated with USB and screen display, but **not yet re-tested in this session**.

Both images transferred via already-established authorized encrypted SSH/SCP to Surface and their local SHA-256 values verified. The controlled 71-byte ramdisk image is **not a new installed OS**; it is only a temporary boot-image packaging compatibility experiment, still targeting the existing physically installed Debian SD root. The v15 image is explicitly a diagnostic reference, not the installed OS.

## Next user/device action and experiment order

At last check, **no ADB, fastboot, or COM USB device was enumerated** after the unsuccessful boot, so remote tool cannot force a safe restart. User must physically long-press Power to stop the stalled boot and power on normally. Android boot and TWRP recovery **remain unmodified** on eMMC. Once Android ADB reconnects, remotely `adb reboot bootloader` to regain fastboot; confirm exactly one `fastboot` serial, `product=xoom-cdma`, unlocked, then *read-only hash validate* the 71-byte-ramdisk boot candidate and issue **`fastboot boot` ONLY**. Do not `fastboot flash`.

If that produces no screen or USB, power-cycle and perform the known working v15 diagnostic reference `fastboot boot` to distinguish bootloader/USB physical state from new OS boot. If v15 succeeds but same-kernel tiny ramdisk fails, build a temporary *early-boot root probe* or minimal initramfs that shows SD detection, partition UUID, and mount errno, then uses `switch_root` to enter normal Debian. Avoid permanent tracing, unapproved internal storage writes, or changing the already verified SD ext4 root.

**Safety:** The 32GB microSD remains available for testing; neither boot candidate has been flashed to internal `boot` p7. No permanent kernel/ROM change or further destructive device operation was performed during this comparison.
