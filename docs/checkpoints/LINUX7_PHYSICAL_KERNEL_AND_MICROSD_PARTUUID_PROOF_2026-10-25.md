# 2026-10-25 screen photograph: clean Linux 7 boots, microSD partition recognized, rootless hybrid panic

**Physical observation:** User supplied a photograph of the replacement Motorola Xoom screen following manual `fastboot boot` of the **new Linux 7 kernel + physically proven v034 diagnostic initramfs** hybrid SHA256 `67b1fc6b6dc3e673a5eb610cdc5dd96347e60a89c8f715b215344bf8e1bb2743`. This supersedes earlier uncertainty that the kernel might not start. **No eMMC flash or install occurred.**

## Photograph: kernel display and device recognition — physical PASS

Linux 7 has started executing and initializes framebuffer console, system memory and MMC subsystems. Its screen prints a partition inventory with both the internal eMMC (multiple Android partitions) and the removable microSD card. Critically the removable partition appears as:

```text
mmcblk1p1   <correct per-card DOS MBR PARTUUID>-01
```

This identifier **matches the private card-specific `PARTUUID`** in our Debian image and originally built Linux boot image. It is *not* the Android internal partition. The kernel has demonstrably enumerated the card's host, identified its partition, and can see the root candidate. Device numbering changed again (`mmcblk1` SD in this boot), which is exactly why stable PARTUUID selection is necessary. The printed list of supported filesystems includes `ext4`. Do not call filesystem mounting PASS yet; enumeration and ext4 driver availability are not a successful root mount.

## Kernel panic: expected missing root spec, not yet Debian evidence

The photo shows:

```text
VFS: Cannot open root device ... or unknown-block(0,0): error -6
Please append a correct "root=" boot option; here are the available partitions:
...
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

The hybrid's temporary boot cmdline was **`androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=7 printk.time=1 rdinit=/init`**: it deliberately **did not specify `root=`** because the intended test was to run the v034 diagnostic initramfs. The original v034 archive `/init` exists as a small statically linked ARM32 ELF, and its gzip archive passed integrity checking. Why the hybrid did not actually hand off to that `/init` is **not yet established** (possible bootloader ramdisk handoff, initramfs interpretation, or init path issue). Once it fell through to root mounting, the absent `root=` parameter naturally yielded unknown-block(0,0). The resulting panic does *not* demonstrate corrupted microSD ext4, an unsuitable partition UUID, or unbootable Debian, because this particular trial never specified Debian as root.

**Main conclusion:** The new kernel/DTB is physically executing, display console works and the removable root partition is visible. This removes most of the prior bootloader/DDI uncertainty and focuses next tests on root selection, actual filesystem mount and PID1.

## Next test — prepared offline, no installation changes

Built a clean, normal **temporary Debian-root boot image** with the same kernel/DTB, no extra diagnostic ramdisk and **the correct private microSD PARTUUID**, but with verbose framebuffer console so root-mount progress or a failure appears visibly. Command line includes `console=tty0 loglevel=8 ignore_loglevel printk.time=1 root=PARTUUID=<private>-01 rootfstype=ext4 rootwait rw init=/sbin/init`.

New image: `xoom-linux7-sdroot-verbose-TEMPBOOT.img`, 5,890,048 bytes; SHA256 **`ea4204a30f2fd73c17c2156b5877e91a2714419b0f911c19277ba03e325fd975`**. Built under WSL `/home/xoomdev/xoom-linux-rom/os-build/earlyboot-diagnostic-20261025/`, copied via authorized local SCP to Surface `C:\Users\olsen\xoom-linux-rom\downloads\`, and byte-hash-verified there. **It has not been booted yet**. This image is for `fastboot boot` only, not `fastboot flash`; it does not alter the internal boot p7, recovery p6, Android system p8 or userdata p10, nor the installed SD ext4 layout.

**Next physical step:** tablet is at a kernel panic with USB enumeration absent, so user must power-cycle back to Android/fastboot as before. Then we can transiently launch the verbose Debian-root image to see whether root mounts and whether systemd/g_serial starts. If it still fails, preserve the screen and debug exact root mount, kernel's `CONFIG_BLK_DEV_INITRD`, bootloader commandline, and root device runtime; do not reformat the fully hash-verified SD card or flash boot to diagnose.

**Historical SD milestone:** [physically installed Debian root and first boot uncertainty](MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md). All original Android/TWRP remain intact.
