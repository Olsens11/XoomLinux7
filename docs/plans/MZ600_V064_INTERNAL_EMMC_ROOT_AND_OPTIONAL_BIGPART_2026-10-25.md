# v06.4 — Internal eMMC Debian root migration, with BigPart only if necessary

> **SUPERSEDED 2026-10-25 late evening:** User *rejected* p10 as Linux root; selected original Xoom BigPart **enlarged p8 `system` 1GiB**, p10 data disposable. Active instructions: [CLASSIC BIGPART p8 system root](MZ600_V064_CLASSIC_BIGPART_SYSTEM_ROOT_IMPLEMENTATION_2026-10-25.md). The rest of this file is historical context only. No change has yet been made on eMMC.


**2026-10-25 evening EDT — design/preflight, NOT installed.** Read the [comprehensive handoff](../handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md), [v06.4 functional acceptance plan](MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md), [same-unit recovery partition measurements](../checkpoints/NATIVE_OS_INSTALL_RECOVERY_PREFLIGHT_2026-10-25.md) and [successful prior conventional Debian microSD boot](../checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md).

## Updated user decision / scope

The user now explicitly accepts **replacing the Android installation** on the **replacement experimental MZ600** if necessary to deliver functional native Debian Linux, and accepts a **BigPart-style expansion/repartition if actually required**. This changes the previous preserve-all-Android design preference; it is **not** a license to flash an unknown partition, randomly apply a Wingray BigPart ZIP, or destroy the protected original MZ600. Actual target and byte ranges, rollback and live detection must be verified before a destructive operation.

**Recommended first architecture:** use existing factory **p10 `userdata` as Debian ext4 root**, keep eMMC partition map unchanged, preserve TWRP p6, old system p8 and old cache p9 initially. A small, verified Linux kernel/early-boot image fits p7's 8MiB limit; the Debian root does not have that limit. Back up p10 contents FIRST; reformatting/replacing p10 will **remove Android applications/settings/internal /data/media** and Android will likely not boot normally afterward, even though p8 remains. For genuine reversibility, restoring boot/system alone is insufficient; userdata backup or recreation is also necessary. **No p10 backup, format or write has occurred in this decision turn.**

## Same-replacement-device measured internal geometry (recovery, 2026-10-25)

`mmcblk0` in TWRP (do **not** hardcode this Linux7 block index); 512-byte sectors, whole eMMC 62,521,344 sectors = 32,011,960,320 bytes. By-name mapping on actual replacement MZ600 was independently checked:

| p# | Name | Start LBA | Sectors | Capacity | Policy |
| -- | -- | --: | --: | --: | -- |
| p1..p5 | vendor/metadata/misc/logo/kpanic | 51200..73728 | various | 13MiB aggregate | NEVER WRITE |
| p6 | recovery | 77824 | 24576 | 12MiB | PRESERVE; TWRP 3.1.1-0 |
| p7 | boot | 102400 | 16384 | 8MiB | potential later Linux boot **only after proven rescue** |
| p8 | system | 118784 | 524288 | 256MiB | too small for standard Debian root; leave intact |
| p9 | cache | 643072 | 346112 | 169MiB | leave intact |
| p10 | userdata | 989184 | 61522944 | 30,040.5MiB (~29.34GiB) | proposed replacement root, AFTER backup/verification |

The existing Debian ARMHF root image is 768MiB, and Desktop sysroot uses ~437MiB (partial permission errors), thus either fits within p10 capacity with ample package/log/write headroom. This **does not yet demonstrate** Linux7 kernel recognition of the factory Tegra partition scheme or validate an internally installed boot.

No standard primary `EFI PART` header was found at eMMC LBA1 in the earlier recovery audit, and no independently validated full TegraPT parser has mapped the table. **Do NOT run generic `parted`, `sgdisk`, `gdisk` or a Wingray BigPart repartitioner on this eMMC.** Upstream TegraPT parser design: [Linux 2020 v6 Tegra partition table patch](https://lists.openwall.net/linux-kernel/2020/05/17/27); in this pinned Linux7 source, `CONFIG_MSDOS_PARTITION=y` and `CONFIG_EFI_PARTITION=y`, but no `CONFIG_TEGRA_PARTITION` or `block/partitions/tegra.c` exists. Original OEM kernel/recovery partition enumeration does **not** automatically establish what current Linux7 enumerates. Port/bind/validate a proper device-aware TegraPT parser if necessary; avoid blind hardcoded whole-device LBA operations or invented PARTLABEL.

## Off-device recovery inventory RE-VERIFIED, read-only on Surface

Private directory `C:\Users\olsen\xoom-linux-rom\private-backups\replacement-mz600-2026-10-25\` contains these hash-verified backups (SHA256 remeasured on Surface during this design turn):

| Image | Size | SHA256 |
| -- | --: | -- |
| `android-HMJ37-boot-p7.img` | 8,388,608B | `4DA4C9F1486374BB66F31C96389CD1EE3067A447E8A72AEA33B2FC24AC3985E3` |
| `android-HMJ37-system-p8.img` | 268,435,456B | `F17E1D2E4183C2D1283AD7282B8981764C0A64653EB3D11ACC07A9AEE89C5AB1` |
| `twrp-recovery-p6.img` | 12,582,912B | `EBE3F1C16CE9D79962433A60B0E63EC6E9F1D6392813601C264204D58B8BBEEC` |
| `emmc-prepartition-reserved-first25MiB.img` | 26,214,400B | `19CEEF587C701FB6C53AACCB5BDE2A47CE2521ED3A44053055EC4B45701D82BE` |

These are private, not complete eMMC backups and are not themselves a tested restoration pathway. Surface has >800GB free; enough to hold a full 29.34GiB read-only p10 snapshot if desired. Only ~291MiB of `/data` appeared used in the previous recovery filesystem report, but this is **not** a sufficient reason to skip backing up the whole p10 partition and files with metadata. Before any destructive action back up p10 off-device, record exact hash/readback and confirm recoverability; record if data is encrypted and whether ext4 `/data/media` is included.

## Required gated implementation

1. **Continue host-only v06.4 development now.** The prior actual Debian 12.15 *microSD* normal Linux systemd + tty1 framebuffer login + COM9 USB login + `wlan0` passed physically, providing a stronger starting point than the v06.3 bare diagnostic. Reuse validated native Debian tools, board DTB/ATAG identity code and WCC lifecycles in a new separate build candidate, while integrating HCD, kernel HIDP/evdev and correct BlueZ + D-Bus + `iw` + signed regulatory files. Never claim keyboard scan pass without actual device testing.
2. **Kernel partition visibility gate BEFORE writes:** boot a separate RAM-only *read-only diagnostic* with working USB and inspect `/sys/block`, eMMC `type`/capacity, partition enumeration and block geometry. Confirm all ten internal p# sizes/starts **on Linux7**, or integrate and offline test the appropriate TegraPT support with genuine proprietary reserved-header forensic evidence. The verified microSD must be absent if comparing against the clean v06.3 RF baseline. Do not make assumptions from `mmcblk0` vs `mmcblk1` names. A simple `root=PARTLABEL=userdata` is **not** yet valid.
3. **No-write standard Linux eMMC root test:** once p10 actually enumerates correctly, test block read-only mount of the *existing Android userdata ext4* from a temporary Linux ramboot/diagnostic. Check superblock/fs health and mount source; no filesystem changes. Prove reproducible bootloader init/USB and independent recovery first. A normal Linux initramfs can resolve and validate the root block by stable on-device attributes, mount by verified Linux root UUID/partition, and `switch_root` into Debian; no need to force a bogus partition label. Note filesystem UUID changes when p10 is formatted.
4. **Recovery gate:** before destructive p10 conversion, in TWRP read and back up **userdata p10**, verify off-device hashes, securely preserve known-good p7/p8/p6/restoration tooling and test a Power-button-only fastboot/TWRP route independent of broken Volume Down **and independent of a working Linux boot**. Verify battery/external dock charging; red-light/no-PONG issue remains unresolved. Do not overwrite reserved sectors, BCT/bootloader, p1..p5, p6 or p9.
5. **Specific reviewed write:** after these gates and a verified root image layout, p10 could be formatted as Debian ext4 and populated from hash-verified staged userspace via TWRP or minimal installer, with symlinks, users, dynamic libraries, module/firmware trees, permissions and ext4 metadata. Re-check p10 start/size/identity at write-time and reject mismatch. Never blindly `dd` a 768MiB image to an assumed `mmcblk*px`; require an identified `/dev/block/.../by-name` resolution or audited alternate. Validate p10 readback and read-only first boot **via fastboot boot**, leaving p7 OEM untouched.
6. **Persistent boot is a separate operation:** after Linux systemd, screen login, USB fallback, `iw` scan and deliberate Bluetooth keyboard pairing/typing succeed repeatably from internal p10 using temporary boot, consider flashing the **exact** hash-verified kernel/initramfs image to only p7. Preflight image <=8MiB and independent TWRP rescue; factory p7 image retained. Do not mark permanent installation before cold-boot pass.
7. **BigPart contingency only:** if p10 cannot be used safely, evaluate an MZ600-specific migration to reassign space from p10 to p8 or create a separate eMMC Linux partition. This is more dangerous because TegraPT/vendor boot metadata may need coherent updates. Existing old BigPart downloads may target **Wingray/MZ604/MZ606** (not verified appropriate to Verizon MZ600); never run one unchanged. BigPart is a deliberately later, independently reviewed operation with complete table/backups/restore dry run.

## Acceptance and known limitations

**As of this decision:** v06.3 clean RAM-boot remains last documented physically running test (19:25 EDT 2026-10-25), and v06.4 has only an OFFLINE ARMHF package preflight. No eMMC writes or partition changes, no v06.4 boot, no p10 backup, no internal Linux7 p10 visibility test; Wi-Fi RF scan, keyboard pairing and simultaneous operation still **NOT TESTED**. The exact same earlier v06.3 image experienced both no-PONG/red-LED and later successful boot, so irreversible writes during an unqualified power state are contraindicated.

**Definition of a meaningful next milestone:** new clean read-only kernel evidence that Linux7 recognizes internal p10 geometry, and a complete, restorable p10 backup. Then an internal root temporary boot with native shell, `iw`, BlueZ/HID; later persistent boot. This plan is an architecture update, **not permission to bypass gates**.
