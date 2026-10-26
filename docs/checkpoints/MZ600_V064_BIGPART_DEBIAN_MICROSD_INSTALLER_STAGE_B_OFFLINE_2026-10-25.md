# MZ600 v064 — BigPart-compatible Debian microSD-root installer boot preflight

**Date:** 2026-10-25 ~21:00 EDT. **Evidence level:** successful OFFLINE build + independent SHA verification on Desktop and Surface, **NOT booted on tablet**. No partition writes/flash.

## Starting physically validated milestones

- [Classic BigPart physical PASS](MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md): kernel 7 recognizes virtual p8 system 1GiB, p9 cache 512MiB, p10 28,929.5MiB on the real replacement Stingray CDMA, USB PONG, no flash. Current Xoom in stage-A RAM-only Linux, microSD absent.
- [Earlier Debian microSD normal Linux boot PASS](NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md): Debian 12.15 normal systemd, on-device tty1 login, USB COM9 ttyGS0 shell, wlan0 created, microSD root ext4. Old physically successful exact boot image SHA256 c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c.
- Original immutable 768MiB Debian ext4 filesystem image SHA256 0aafdddccf58c5259007f272fb7878c417006629f5cb678c6d5e0f361ef8376e fits expanded 1GiB internal p8, **but has not been written to device**.

## New independent stage B builder and artifact

Builder: [build-v064-bigpart-debian-sdroot-stageB-20261025.py](../../scripts/experiments/build-v064-bigpart-debian-sdroot-stageB-20261025.py). Copies separately staged source/build from stage A into new v064-bigpart-debian-sdroot-build with recorded provenance, preserving immutable stage-A outputs, clears CONFIG_INITRAMFS_SOURCE so embedded diagnostic /init does not override normal Debian root, uses same BigPart source and unchanged same compiled Stingray device tree. Repackages the new zImage+DTB with the exact **private** proven microSD PARTUUID boot cmdline and old successful nonempty external gzip CPIO ramdisk (no /init) into an Android legacy boot image. Full recreated boot ID, size and source SHA guard. External PARTUUID value is not printed or published.

- New stage-B boot image on Desktop private path artifacts-embedded-v064-bigpart-debian-sdroot-stageB/MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img; also checksum-verified in Surface private downloads.
- Bytes: **6,645,760**. SHA256: **b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba**. New kernel+DTB 5,887,602 bytes, proven external ramdisk 754,277B. Legacy Android image below 8MiB.
- New build CONFIG_MOTOROLA_XOOM_BIGPART=y, CONFIG_INITRAMFS_SOURCE empty, output v064 BigPart DTB byte-identical to stage A. Empty generated kernel initramfs CPIO is 512 bytes (no executable /init). Physical test not yet performed; do not assume it boots.
- Byte SHA256 independently checked on Desktop WSL source and Desktop NTFS transfer, then Surface Win32 copied via existing private authenticated host SSH/SCP and hashed matching. Source rootfs remains private.

## Exact next physical milestone (no storage writes)

User must physically reinsert the **same previously installed and verified 32GB Debian ext4 microSD** into **the replacement MZ600**. Do not format or substitute unknown card. Reconfirm removable card geometry and private partition selector using read-only diagnostics and one-shot guarded boot. After physical insertion, perform only a temporary fastboot boot of the new stage-B hash, confirm native Debian systemd, on-screen tty1 and authenticated USB serial shell. Verify Debian / is ext4 on removable SD, internal eMMC p8 BigPart system exactly 1GiB, p9 512MiB, and no internal mounts or extraneous SDIO MMC ambiguity. Do not run mkfs, wipe, partition commands or package installs before this gate.

Once stable, separately prepare a guarded, verified standard ext4 image installer on the **physically mapped** p8 with checksum of source Debian root, exact verified target identity/start/size, exclusive unmounted target, progress/result capture, and readback validation. Android original p7 and TWRP p6 are maintained unchanged until native p8 boot proves repeatable. Stock TWRP 3.1.1-0 sees p8 256MiB, so it is **not** an appropriate BigPart formatter.

**Current acceptance:** stage A BigPart geometry = PHYSICAL PASS; stage B Debian microSD boot image = OFFLINE BUILT/HASH VERIFIED, PHYSICAL NOT TESTED; internal p8 format/install = NOT PERFORMED; Wi-Fi scan, BT keyboard typing and persistent Linux install = NOT TESTED.
