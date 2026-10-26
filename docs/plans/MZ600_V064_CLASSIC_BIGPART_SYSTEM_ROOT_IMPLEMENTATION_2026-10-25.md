# Motorola Xoom MZ600 / Linux 7 v06.4 — original classic BigPart, Debian root on /system

**2026-10-25 evening EDT. NEW CURRENT STORAGE PLAN.** This supersedes [earlier p10-root proposal](MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md). This is a host-validated design, not yet an on-device repartition or filesystem installation.

## User's final choice

The user explicitly selects **classic original Xoom BigPart** instead of a Linux root on p10, accepts losing existing **Android /system** and **all /userdata**, and states there is **nothing in userdata worth keeping**. Do not spend work backing up p10 user contents. Preserve private existing p7 boot, p8 Android system, p6 TWRP and reserved 25MiB backups and do not touch the protected original MZ600. The objective is the *conventional Xoom BigPart kernel-visible /system partition* as a Debian 12 Bookworm ARMHF ext4 root mounted at Linux `/`, not a 30GB `/userdata` root, loop filesystem, custom modern GPT, or independently invented BigPart layout.

## Proven upstream reference: ORIGINAL Xoom BigPart (not generic SGDisk/REPIT)

Schischu's [original kernel commit `6b3d70fff905b7395fd15992c3779b27d1b6c101`](https://github.com/Schischu/android_kernel_moto_wingray/commit/6b3d70fff905b7395fd15992c3779b27d1b6c101) explicitly recognizes **Wingray** `system=0x1d000, cache=0x9d000, userdata=0xf1800` *and Everest* offset variants, using 512-byte sectors. It changes the **kernel's in-memory GPT partition view**; it does **NOT rewrite the physical disk GPT partition entries**. On changing kernel/recovery, the view can change back. Recovery + Linux kernel MUST agree when formatting/mounting or filesystem data may overlap.

Critically, read-only same-unit MZ600 TWRP readings on Oct25 show **all three Wingray variant offsets match exactly**, even though the *hardware is Verizon MZ600 Stingray CDMA* and not MZ604 Wingray. Historical ROM guidance also lists a Stingray/Stingray_CDMA BigPart install and KitKat builds. The offset match permits using the **classic layout**, not assuming that a Wingray-only TWRP boot/kernel contains the right MZ600 device drivers. Avoid generic unverified Wingray zip.

Public matching forum background:
- [Original Xoom BigPart and recovery/ROM resource center](https://xdaforums.com/t/bigpart-repartition-upgrade-and-resource-center.2506997/)
- [2014 unified Wingray/Stingray/Everest BigPart ROM](https://xdaforums.com/t/rom-4-4-4-cyanogenmod-11-0-wingray-stingray-everest-bigpart.2596566/)
- [Schischu original partition remap commit](https://github.com/Schischu/android_kernel_moto_wingray/commit/6b3d70fff905b7395fd15992c3779b27d1b6c101)
- [MZ600-specific community guide for Stingray BigPart](https://4pda.to/forum/index.php?showtopic=221608&st=3440)

## Exact original vs in-memory BigPart map

Factory MZ600 eMMC = **62,521,344 x 512-byte sectors**, with a 25MiB Tegra/vendor reserved start. **p1–p7 remain byte-for-byte same logical sector extents**; p6 TWRP recovery remains 12MiB, p7 boot 8MiB.

| Partition | Factory start LBA | Factory MiB | BigPart start LBA | BigPart sectors | BigPart MiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| p8 `system` | 118,784 | 256 | **118,784** | **2,097,152** | **1024** |
| p9 `cache` | 643,072 | 169 | **2,215,936** | **1,048,576** | **512** |
| p10 `userdata` | 989,184 | 30,040.5 | **3,264,512** | **59,247,616** | **28,929.5** |

BigPart `system` end inclusive: **2,215,935**. BigPart cache end: **3,264,511**. BigPart userdata end **62,512,127** unchanged from factory; no reserved partition overlap.

**New verified reproducible tool:** [`scripts/experiments/audit-mz600-classic-bigpart-layout-20261025.py`](../../scripts/experiments/audit-mz600-classic-bigpart-layout-20261025.py). Run on Desktop WSL `xoomdev`: it requires exact known MZ600 eMMC sector count, p1–p10 historical map, original BigPart offsets, extents, contiguity, invariance of p1–p7 and original p10 end. It calculates/prints the kernel-visible **virtual** layout. Host execution returned `CLASSIC_BIGPART_OFFLINE_AUDIT_PASS`; no device read/write. Private JSON `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v064-preflight/MZ600-CLASSIC-BIGPART-OFFLINE.json` saved.

### 1GiB system sizing contract

Existing Debian root ext4 image **768 MiB (805,306,368B)** fits classic BigPart `/system` **1GiB (1,073,741,824B)**, leaving **256MiB nominal extra image capacity** before additional installed packages, filesystem reserves and logs. Actual sysroot is ~437MiB now but **BlueZ/D-Bus/HID/regdb still need integration**. Do not treat 1GiB as unlimited: establish the assembled footprint and free-space margin, and use remaining large `userdata` for writable `/home`, `/var` and/or `/var/cache/apt` if warranted. Keep Debian Linux root **/** on the partition historically named `system`, not the Android mount name `/system`.

## Implementation sequence — use existing code, fail closed

1. **Identify an original Xoom BigPart recovery/kernel matched to Stingray/MZ600**, extract/check SHA-256, image header, bootloader-facing board/DT machine variant and kernel partition code, then compare its remap constants with the exact script and Oct25 TWRP p1–p10 snapshot. Available web downloads labeled `TWRPv2.8.6.0-Wingray-BigPart.zip` or `R.A.H._TWRPv2.6.3_BigPart_selinux.zip` are often cataloged for **MZ604/MZ606 only** and are not yet independently proven safe for MZ600. Historical Stingray community guides prove there is an established method, not that any single downloaded recovery binary can safely execute here.
2. **Preserve recovery and rollback:** Surface private p6/p7/p8 and first 25MiB backups were re-hashed in the prior step and matched recorded SHA. No userdata backup is required by user choice; explicitly record its destruction. Do not overwrite BCT/vendor metadata, bootloader, PDS, p1–p5. Verify button-independent fastboot/TWRP recovery before a persistent p7 or p6 modification; replacement MZ600 has broken Volume Down and intermittent red-LED no-PONG boots.
3. **Recognize GPT correctly BEFORE applying the view:** the source of pinned Linux 7 `block/partitions/efi.c` has normal `efi_partition` and primary/alternate GPT logic, but no original Schischu BigPart remap and no confirmed MZ600 Tegra relocated GPT handling. Factory LBA1 was not a verified GPT header. Use existing known relocated GPT research and a *minimal strict opt-in* compatibility adaptation using original code and measured physical GPT headers. Do not force `root=PARTLABEL=system` until Linux7 physical visibility confirms an actual corresponding partition identifier. As a separate initial diagnostic, the existing Android/TWRP kernel may parse layout, whereas current Linux7 might not.
4. **Temporary boot/preflight** a proven compatible BigPart recovery or an isolated Linux7 read-only diagnostic with correct view. Before any wipe/format compare **all ten** p# starts/sizes, eMMC capacity, boot/recovery identities and actual mount targets against expected values. Do not format p8 under the **stock 256MiB** view or write past one filesystem extent under the other view. Prefer `fastboot boot` compatible diagnostic/recovery without modifying original p6/p7 if physically proven possible.
5. **User-authorized destructive migration only once exact hardware view and rescue are proven:** perform the traditional BigPart recovery formatting of `system`, `cache` and `userdata` (including Android data loss). Re-check system is exactly **1,073,741,824 bytes**, contiguous p9 starts at **2,215,936** and p10 at **3,264,512**. Never run generic parted/sgdisk; the original method is a consistent **kernel-visible map** and formatting.
6. **Populate full Debian into enlarged `system`:** use reproducibly built/hashed rootfs, normal device nodes, `/bin/sh`, systemd+getty, validated BlueZ/D-Bus/HID, `iw`, regulatory signatures, modules+firmware and `/etc/fstab` referencing stable verified root identity. If deploying the previously prepared 768MiB ext4 block image, grow the ext4 filesystem after installation to fill the new 1GiB virtual `system` extent; do not assume `dd` alone auto-expands. Validate offline and after mount before boot.
7. **Boot Linux7 with `/` on BigPart p8, initially via `fastboot boot`:** preserve boot p7 and TWRP p6 until repeated USB fallback/tty1, `iw` nearby scan and user-driven Motorola Bluetooth keyboard typing tests pass. Keep whole BCM4329 shared U4/clock/lifecycle work as separate gated tests. Only after boot-independent TWRP rescue tested, perform **explicit measured/pinned persistent p7** Linux boot replacement and verify restart without USB host assistance.

## Provenance and current verdict

**PASS OFFLINE:** matching BigPart exact factory offsets for this actual MZ600, non-overlapping original remap, 768MiB image size fits 1GiB system, host auditor, existing private backup hashes.

**NOT TESTED:** verified MZ600-compatible recovery BigPart binary and SHA; Linux7 correct GPT/BigPart virtual enumeration on hardware; formatting of any partition; install into p8; v06.4 Linux BigPart-root boot; RF scans; keyboard; power/reboot consistency.

**No eMMC writes, no repartition, no new BigPart image and no hardware command have occurred in this decision implementation turn.** The last physical target verification remains v06.3 RAM-only PONG from 19:25 EDT.

