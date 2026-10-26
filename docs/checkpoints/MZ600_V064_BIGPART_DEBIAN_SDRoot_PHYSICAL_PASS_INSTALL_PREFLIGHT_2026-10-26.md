# MZ600 v06.4: BigPart Debian microSD PHYSICAL BOOT and internal system installer PREFLIGHT PASS

**Local time: Monday 2026-10-26 around 01:45–02:00 EDT.** **Verified tablet:** experimental replacement Motorola Xoom MZ600 Stingray CDMA, not protected original. **No internal eMMC block writes or flashes occurred in this entire turn.** No formatting was attempted; user explicitly permitted future destruction of Android and userdata.

## Reinserted microSD physically recognized in stage-A Linux7

After user physically inserted the previously prepared 32GB Debian microSD, live v064 stage-A COM9 `PING` returned `PONG XOOM-LINUX V20`. Read-only `STORAGE` showed internal `mmcblk0` p8 BigPart 1,048,576 KiB, p9 524,288 KiB, p10 29,623,808 KiB, plus **new removable `mmcblk1` 30,533,632 KiB and `mmcblk1p1` 30,532,608 KiB**. Read-only SDIO enumeration still returned Broadcom vendor 0x02d0, device 0x4329 with three MMC SDIO functions. No radio activation.

## Guarded fallback and Debian stage-B boot

1. Stage-A Linux USB COM9 two-phase `REBOOT` then `CONFIRM REBOOT` returned acknowledged and USB disappeared. Original Android physically booted, identity `stingray`, `sys.boot_completed=1` at approx **01:47:30 EDT**. Exact USB record on Surface: `captures/MZ600-V064-BigPart-to-Android-before-StageB-20261026-PRIVATE.log`.
2. SHA-pinned Stage-B boot image was already verified on both Desktop and Surface: **6,645,760 bytes** SHA256 **`b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`**, matches [previous offline stage-B checkpoint](MZ600_V064_BIGPART_DEBIAN_MICROSD_INSTALLER_STAGE_B_OFFLINE_2026-10-25.md). Verified Android identity then ADB rebooted to fastboot, verified product `xoom-cdma` and `unlocked=yes`, then executed only **`fastboot boot`** (RAM temporary, **NOT flash**). Transfer 1.119 seconds, boot command 1.393 seconds, accepted at **01:48:37 EDT**.
3. Debian GNU/Linux 12 xoom-mz600 ttyGS0 USB login physically appeared by **01:48:51 EDT**. Known existing Surface local `xoom-debian-serial-first-login-probe.ps1` authenticated normal `xoom` user from previously established private credential workflow without printing its password. Real shell reported `uname -r: 7.0.0-next-20260422+`, Debian 12.15, `findmnt /: /dev/mmcblk1p1 ext4`; `/dev/ttyGS0` present, sysfs Wi-Fi DT MAC node exists. **systemd PID 1 confirmed**.
4. Caveat: `systemctl` responded `Failed to connect to bus: No such file or directory`; `ip -br link` currently showed only loopback/tunnel interfaces, **no wlan0**. So core Debian shell and BigPart are physically confirmed, but Wi-Fi and D-Bus services remain pending. Do not misreport active Wi-Fi or completed `iw scan`.

## Measured separate BigPart partition map under real Debian

Live normal Debian root was on **removable SD `/dev/mmcblk1p1`**, while `/dev/mmcblk0p8` internal system was **UNMOUNTED**. Actual `/proc/partitions` and read-only `/sys/block` start/size:

| p | Start LBA (512B) | Sectors (512B) | Current purpose |
|---|---:|---:|---|
| 6 | 77824 | 24576 | preserved TWRP |
| 7 | 102400 | 16384 | preserved Android boot |
| 8 | **118784** | **2097152** | enlarged BigPart **1GiB system** target |
| 9 | **2215936** | **1048576** | enlarged BigPart 512MiB cache |
| 10 | **3264512** | **59247616** | shifted BigPart data |

Internal `mmcblk0` 62,521,344 sectors, device name `MMC32G`, `removable=0`. Source `mmcblk1` 61,067,264 sectors, device name `SD`, current root ext4; kernel device-mapper minor p8 `179:24`, SD p1 `179:1`. Kernel DT `/mmc@c8000600/motorola,xoom-bigpart` opt-in exists. Standard Debian `/sbin/mkfs.ext4`, `e2fsck`, `tune2fs`, `blkid`, GNU tar ACL+xattr+single-filesystem modes available. `rsync` not installed, so original standard GNU tar copy chosen. Existing SD /etc/fstab points to its old removable SD PARTUUID; installer must change ONLY cloned internal /etc/fstab root to p8 GPT PARTUUID. **Do not modify live SD fstab.** Source SD root filesystem allocated **457,700 KiB (~447MiB)**, comfortably fits new p8 1GiB.

**Important udev difference:** in this minimal Debian system, `/dev/disk/by-partuuid` had only one link (SD) and **no p8 user-space symlink**, even though `/sys/class/block/mmcblk0p8/uevent` has full 36-char GPT `PARTUUID` and kernel `PARTNAME=system`. Do not mistake missing userspace symlink for missing kernel GPT; Linux kernel `root=PARTUUID` uses its own table. A 36-char p8 GUID was verified **privately** and stored only on Surface: `private-backups/replacement-mz600-2026-10-25/P8-BigPart-Partition-UUID-PRIVATE.txt`. Never publish the GUID.

## Prepared full internal-root boot candidate — OFFLINE ONLY

A reproducible public [Stage-C builder](../../scripts/experiments/stage-v064-bigpart-internal-root-boot-from-proven-sd-20261026.py) created a **private, UNTESTED** internal p8-root temporary boot candidate using the physically proven Stage-B kernel/ramdisk, changing **only the legacy Android boot cmdline root selector** to this exact internal p8 GPT PARTUUID, preserving all other header fields, embedded kernel and ramdisk bytes. SHA256 **`15feced18d384ec532b7e3d9fb04463eac14c445909fadb5798920ee661571c8`**, 6,645,760B, independently reviewed on Surface: other image bytes identical; SD PARTUUID selector no longer present, new 36-char p8 root GUID format correct. Filename `downloads/MZ600-V064-BIGPART-INTERNAL-SYSTEM-ROOT-TEMPBOOT-PREINSTALL-UNTESTED.img` on Surface. **DO NOT BOOT stage C until p8 contains a complete verified Debian installation.** This is not yet physical proof it can boot.

## Guarded standard Debian p8 installer: READ-ONLY PREFLIGHT PASS

Public reproducible script [`scripts/experiments/mz600-bigpart-install-debian-from-sd-20261026.sh`](../../scripts/experiments/mz600-bigpart-install-debian-from-sd-20261026.sh), final known SHA256 **`e265a0e8f7baae66311788d37ea504dc4e9785530139423428b15a1f41a28650`**. Source was syntax-checked in Desktop WSL, independently hashed on Surface, transferred over CDC serial **only to removable SD** `/home/xoom/mz600-bigpart-install-debian-from-sd-20261026.sh`, and readback-hash verified. Nonprivileged default `--preflight` checks 10-partition geometry, board identity, mount state, systemd, Debian version/kernel, true GPT p8 PARTUUID, root SD identity, GNU tar capabilities and capacity. First two revisions aborted safely on overly restrictive fstab regex and absent p8 udev symlink; fixed in public source and new SHA verified before retries. Third revision physically returned:

```
INFO_P8_UDEV_SYMLINK_MISSING_KERNEL_GPT_UUID_VERIFIED
MZ600_BIGPART_PREFLIGHT_PASS
ROOT=Debian-12.15-SD-ext4 KERNEL=Linux7
TARGET=P8_BIGPART_1G P9_CACHE_512M P10_DATA_28929_5M
ALL_PROTECTED_P1_TO_P7_UNCHANGED=PASS
SD_ROOT_USED_KIB=457700 TARGET_UNMOUNTED=PASS
IDENTITY_AND_PARTUUID_VERIFIED=PASS
READ_ONLY_NO_FORMAT_NO_MOUNT_NO_TRANSFER
PREFLIGHT_TRUE_RETURN:0
```

The separate explicit `--install` path, **NOT EXECUTED**, requires root and formats only validated virtual p8 using normal Debian `mkfs.ext4`, copies Debian from mounted SD root via GNU tar preserving metadata, changes the cloned target root fstab PARTUUID, unmounts, fsck validates. It never writes BCT/GPT, p1–p7, p9 or p10, and never flashes boot. This script has NOT yet had destructive path acceptance tests on the device. User knowingly authorizes future erase of original Android system and userdata, but no such erase has occurred.

## Blocker and next execution sequence

**Privilege gate:** `sudo -n id` physically returned `sudo: a password is required`; owner must enter their Debian sudo password **directly in the existing Surface USB serial console** (never in ChatGPT). An attempted secure automation of the already-private credential was stopped by a tool safety check; do not attempt to bypass or extract it. Existing authorized `C:\Users\olsen\xoom-linux-rom\downloads\Start-Xoom-USB-Console.ps1` is a fully interactive COM9 console with password characters not echoed. User can open that console and run `sudo -v`, type password locally, then exit with Ctrl+]. DO NOT capture or publish password. sudo timestamp may expire; if so reauthenticate.

**Before destructive p8 format:** with authenticated privileged Debian SD-shell, **prove the bootloader/rescue route that does not depend on Android /system** (especially replacement device broken Volume Down and recurring red-camera-LED no-boot episodes). Preferred preserve a physically proven bootable removable-SD Debian Stage-B fallback in p7 only after explicit recovered fastboot and careful backup checks; test warm/cold reboots and returning to bootloader/recovery. The currently installed p7 boots stock Android, which will no longer boot after p8 is overwritten. **Don't format p8 until rescue is reliable.** After that, run guarded p8 installer using sudo; verify copied root and ext4 fsck; temporary fastboot boot prebuilt Stage C and verify real Debian internal p8 root plus USB login. Finally decide persistent p7 flash only after repeated success. Wi-Fi scan and Bluetooth keyboard testing remain separate v064 goals.

**Current exact hardware state:** Stage-B normal Debian 12.15 running from inserted microSD, BigPart-aware Linux 7, USB COM9 logged in as xoom, kernel p8 1GiB, internal Android p8 unmounted and untouched, p7 Android boot/p6 TWRP untouched. No formatting, no flash, no internal block writes. Whole upstream project and source state kept in GitHub branch wip/clean-wifi-bt-usb-20261025; firmware, credentials and GUIDs stay private.
