# Installation preflight — replacement MZ600, recovery storage and restorable Android baseline

**Date:** October 25, 2026. **Status:** actual read-only eMMC layout examined, 3 Android/recovery partitions and 25 MiB prepartition reserved-area evidence copied off-device and hashed; no Linux install/format/repartition/flash performed.

## Device and recovery identity

Surface USB ADB contacted one physically connected Xoom, device shown under the same previous private USB serial. It initially reported existing Android `ro.product.device=stingray`, build `trygon-userdebug 3.1 HMJ37 124251 test-keys` and `sys.boot_completed=1`, with qtouch functioning after prior cold power cycle.

For user-authorized Linux installation preflight, issued `adb reboot recovery`. Device subsequently enumerated in **TWRP 3.1.1-0**; recovery `id` = uid 0 root, device configuration `wingray`. This recovery hardware description is longstanding; the replacement tablet is the only machine being operated, NOT the protected other Xoom.

## Actual internal eMMC observations

- `/sys/block/mmcblk0/size = 62521344` sectors of 512 bytes, **32,011,960,320 bytes** total (~29.81 GiB).
- `/proc/partitions` and `/sys/block/mmcblk0/mmcblk0p*/start|size` both expose **10** partitions; actual recovery by-name mapping explicitly confirms boot p7, recovery p6, system p8, cache p9, userdata p10:

| Partition | Label | First LBA | Sectors | Nominal size |
| --- | --- | ---: | ---: | ---: |
| p1 | ebb | 51200 | 6144 | 3 MiB |
| p2 | pdsb | 57344 | 4096 | 2 MiB |
| p3 | misc | 61440 | 4096 | 2 MiB |
| p4 | logo.bin | 65536 | 8192 | 4 MiB |
| p5 | kpanic | 73728 | 4096 | 2 MiB |
| p6 | recovery | 77824 | 24576 | 12 MiB |
| p7 | boot | 102400 | 16384 | 8 MiB |
| p8 | system | 118784 | 524288 | 256 MiB |
| p9 | cache | 643072 | 346112 | 169 MiB |
| p10 | userdata | 989184 | 61522944 | 30,040.5 MiB |

p10 physical nominal size = 30,761,472 KiB = 30,040.5 MiB ≈ 29.34 GiB. `df -k /data`: 30,278,164 KiB filesystem size, **298,184 KiB used (~291.2 MiB)**, 29,979,980 KiB available (~28.59 GiB); ext4 mounted at `/data` and `/emmc` by TWRP read-write **automatically**, no install script changed it. `/system` was **not mounted**. `/external_sd` was **not mounted**; no detected microSD block device (`/sys/block` displayed only mmcblk0 in Android; no reader/card connected to Surface or desktop).

- No unallocated eMMC partition or free ~768 MiB disk extent was demonstrated. The 25 MiB region before p1 is **vendor-reserved metadata/boot material**, not a normal available space for Linux and must not be repurposed.
- TWRP fstab: `/external_sd vfat /dev/block/platform/sdhci-tegra.2/mmcblk0p1` historical device naming, USB/gadget and kernel enumeration may differ on Linux 7.
- Initial historical `EFI PART` expectation at LBA1 failed. The actual vendor-era Tegra devices can use NVIDIA **TegraPT** and/or offset GPT, not ordinary primary GPT. No full on-device table parser validation yet; **do not invent a GPT with parted/gdisk** or try to repartition this eMMC based on the Linux 7 `root=PARTLABEL=xoom-linux` sample.
- Current clean Linux 7 OS config has `CONFIG_MSDOS_PARTITION=y`, `CONFIG_EFI_PARTITION=y`, ext4 and loop enabled, but **no compiled CONFIG_TEGRA_PARTITION parser identified in pinned source**. Thus a normal internal root cannot be deemed compatible simply because it is ext4. Relevant upstream NVIDIA Tegra PT research: https://lists.openwall.net/linux-kernel/2020/05/17/27 and https://lkml.iu.edu/2005.2/00406.html .
- Private read-only copy of sectors 0–51199 (25 MiB) from `/dev/block/mmcblk0` used `dd if=/dev/block/mmcblk0 of=/tmp/... bs=512 count=51200` into **TWRP RAM tmpfs**; copied to Surface, and RAM temporary removed. It is **for forensic reference only, NOT a restorable whole-disk image or permission to flash BCT/EBT/GPT**. Search did not find a standard sector-aligned `EFI PART` at expected LBA1; some unaligned string hits can occur inside binaries and are not GPT headers.

## Exact same-unit, off-device backups

Surface private directory:
`C:\Users\olsen\xoom-linux-rom\private-backups\replacement-mz600-2026-10-25\`

| Backup file | Recovery origin | Bytes | SHA256 |
| --- | --- | ---: | --- |
| `android-HMJ37-boot-p7.img` | `/dev/block/mmcblk0p7` via root ADB pull | **8,388,608** | `4DA4C9F1486374BB66F31C96389CD1EE3067A447E8A72AEA33B2FC24AC3985E3` |
| `android-HMJ37-system-p8.img` | `/dev/block/mmcblk0p8` via root ADB pull | **268,435,456** | `F17E1D2E4183C2D1283AD7282B8981764C0A64653EB3D11ACC07A9AEE89C5AB1` |
| `twrp-recovery-p6.img` | `/dev/block/mmcblk0p6` via root ADB pull | **12,582,912** | `EBE3F1C16CE9D79962433A60B0E63EC6E9F1D6392813601C264204D58B8BBEEC` |
| `emmc-prepartition-reserved-first25MiB.img` | `/dev/block/mmcblk0` first 51,200 sectors, READ ONLY | **26,214,400** | `19CEEF587C701FB6C53AACCB5BDE2A47CE2521ED3A44053055EC4B45701D82BE` |

These backed-up images are **owned private artifacts, not public Github uploads**. Their exact sizes match the current recovery /proc partitions. Android **userdata is NOT backed up as a full restorable block image**; TWRP reports ~291 MiB used. On recovery, a file-level backup could be obtained with proper ownership/xattr metadata if the user elects to change userdata, but no such backup has yet been performed. TWRP backups should include `userdata` before any destructive action.

## OS artifact status and blocking decision

The currently prepared clean native OS (Debian Bookworm ARMhf, Linux 7 kernel, per-unit MAC bootloader-to-FDT patch, separate upstream WCC, standard g_serial/getty) already passed offline QA. The **uninstalled** boot candidate targets `root=PARTLABEL=xoom-linux` and the uninstalled root is **768 MiB ext4**.

**Do not flash current boot image until the root selector and storage medium are validated!** No GPT-labeled `xoom-linux` partition has been proven or created, no microSD inserted, and internal TegraPT compatibility is unresolved. Neither image has been written to the tablet. User's prior requirement to preserve Android and allow switching back still stands unless explicitly revised for a named persistent write.

Recommended practical non-destructive installation approach: **direct ext4 partition on microSD with standard MSDOS/GPT partition structure and a verified `PARTUUID`/device selector**, with a transient normal-Linux-root boot first and subsequent separately authorized internal boot selection. This keeps Android `system`, `userdata`, recovery and proprietary TegraPT untouched. No external microSD is currently visible in either connected PC or the tablet.

Alternative, only with explicit intent and backup: repurpose the **actual p10 userdata**, maintaining Android system/boot separately; this destroys Android app/userdata until restored. Other options involve risky vendor partition table repartition and require a bespoke verified TegraPT plan and backup. No such destructive action is authorized by the generic instruction to proceed.

## Decision gate

The next necessary user choice is **which actual storage medium** to use: insert an appropriate microSD card (preferred Android-preserving) or explicitly elect p10 destruction with a proper full userdata backup and verified kernel TegraPT/direct-device root path. Once a medium is confirmed, rebuild the root selector in boot image /etc/fstab accordingly, write/verify only the specifically approved target, test USB ttyGS0 login and dynamic Motorola factory MAC before any RF association.

**Physical last known state:** replacement Xoom running TWRP 3.1.1-0, ADB uid0. No flash/format/partition change; original Android HMJ37 still recoverable with reboot system and separate backups. Protected Xoom untouched.
