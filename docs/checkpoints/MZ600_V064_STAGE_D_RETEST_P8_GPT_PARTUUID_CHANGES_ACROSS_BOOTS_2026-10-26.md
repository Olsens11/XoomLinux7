# MZ600 Linux7 v064 — Stage-D repeated internal Debian boot PASS; p8 kernel GPT PARTUUID changes across boots

**Date:** Monday 2026-10-26. **Device:** experimental replacement Motorola Xoom MZ600 only, serial `170061c243805617`. The protected original Xoom was not touched.

## Summary and verified physical results

This is the follow-up test after Stage-E `root=PARTUUID=<prior-live-GPT-p8-guid>` got stuck at the framebuffer text `Waiting for root device PARTUUID=...` despite kernel BigPart enumeration. Owner used their repaired volume/power buttons to enter fastboot and reported it ready. Surface independently verified serial `170061c243805617`, product `xoom-cdma`, unlocked yes, and Stage-D image `downloads/MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img` size **6,645,760 bytes**, SHA256 **`fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`**.

Executed **ONLY `fastboot boot`**, **NOT `fastboot flash`**:
```text
Sending 'boot.img' (6490 KB) OKAY [0.924s]
Booting OKAY [1.080s]
Finished. Total time: 2.010s
FASTBOOT_BOOT_EXIT=0
```
COM9 enumerated and clearly displayed `Debian GNU/Linux 12 xoom-mz600 ttyGS0` and `xoom-mz600 login:`. Reused existing local private Surface USB-console login workflow (credential never exposed or logged). Physically verified **Linux `7.0.0-next-20260422+`, Debian `12.15`, mounted real root `/dev/mmcblk0p8 ext4 /`**. Device is **CURRENTLY LIVE and AUTHENTICATED as normal unprivileged `xoom`** on this **TEMPORARY** Stage-D internal-root boot, with 32GB rescue microSD still inserted. Kernel/p7 boot image not flashed or changed; p7 remains verified persistent Stage-B Debian SD-root rescue. No partition or GPT writes/format in this test.

## Crucial cross-boot GPT-partition identifier result

With live internal root actually `/dev/mmcblk0p8`, confirmed `/sys/class/block/mmcblk0p8/start=118784`, `size=2097152` (1GiB), `PARTNAME=system` and exactly one valid full 36-character GPT `PARTUUID` in its sysfs `uevent`. Read that UUID via Surface COM9 and privately compared it against (1) saved original p8 GUID from the earlier initial install period, (2) p8 GUID read from the **previous successful Stage-D internal-root boot**, and (3) **the full GPT PARTUUID embedded in the Stage-E image**. Result, with raw values kept PRIVATE:

```text
CURRENT_LIVE_ROOT_INTERNAL_P8=TRUE
CURRENT_LIVE_P8_SIZE_1G=TRUE
CURRENT_LIVE_GPT_PARTNAME_SYSTEM=TRUE
CURRENT_LIVE_P8_UUID_EQUALS_STAGE_E_IMAGE=False
CURRENT_LIVE_P8_UUID_EQUALS_PREVIOUS_STAGE_D=False
CURRENT_LIVE_P8_UUID_EQUALS_ORIGINAL_SAVED=False
STAGE_E_IMAGE_UUID_EQUALS_PREVIOUS_STAGE_D=True
```

The previous Stage-D boot's captured p8 PARTUUID was identical to the GUID placed in Stage-E's boot command line; the newly booted Stage-D kernel returns a **different p8 GUID** despite **identical kernel, same internal p8 device, same virtual BigPart start/size**. This is physical evidence that **kernel-reported p8 PARTUUID is not stable across boots**, and is consistent with why Stage-C and Stage-E (both using a captured GPT UUID as root selector) stalled. It does **not alone prove the raw on-disk backup GPT changed**. Disk GPT contents, bootloader write behavior, partition metadata formatting, and GPT scanner's internal fields have not been independently compared across boots. **Do not claim the bootloader is rewriting the GPT or that the kernel is randomizing GUIDs without further evidence.** On this boot the 10 sysfs partition GUIDs were unique, and a **private 10-partition snapshot** was saved on Surface.

Additional physical observations:
- ext4 filesystem UUID reported for mounted **internal p8** by `findmnt -n -o UUID /` is **`c2fb0167-7143-4186-b284-c86d6c09ea64`**, unchanged from the previous native p8 `mkfs.ext4` recorded when Debian was installed; this is a filesystem identifier, **NOT GPT PARTUUID**. `lsblk` still reports ext4 on p8.
- The internal p8 `/etc/fstab` had previously been backed up and changed to the GUID captured on the *prior* Stage-D boot. On this newly booted Stage-D instance, a read-only comparison printed `LIVE_FSTAB_STALE` again. **Do NOT keep rewriting fstab to per-boot GPT PARTUUID**. Instead consider a guarded fix to use the stable ext4 `UUID=c2fb0167-7143-4186-b284-c86d6c09ea64` or the device node `/dev/mmcblk0p8` for the root mount entry, after owner personally runs `sudo -s`.
- The on-device user `xoom` is unprivileged after reboot. Do not try to acquire sudo password via remote files or connectors; owner can enter privately on Surface as in previous phases.
- Wi-Fi and module ABI mismatch `7.0.0-next-20260422+` vs modules `7.0.0-next-20260422`, and systemd bus error, remain separate tasks.

**Private evidence on Surface (never publish raw GPT GUIDs):**
- Host output flag file: `captures/MZ600-V064-StageD-FreshBoot-P8-GUID-Comparison-20261026.txt` SHA256 `04945b77accc1aa1b5a624d49c530773866bcaae604767c82a044cbc75313c4a`.
- Complete 10 partition GUIDs from this live boot: `private-backups/replacement-mz600-2026-10-25/MZ600-GPT-PARTUUIDS-LIVE-STAGE-D-RETEST-20261026-PRIVATE.txt` SHA256 `0e19be0c7fc9d6d44022244623fae335a4bdefde4a304b033b638e622af3c0cd`.
- Prior true-live capture (now obsolete across boot): `private-backups/replacement-mz600-2026-10-25/P8-BigPart-Partition-UUID-LIVE-VERIFIED-20261026-PRIVATE.txt` SHA256 `000ea863f8ae2651543cf30b0fc9f6b4f453ada8ea01fdbdea65f3aa27ae3`.
- This current boot has no known GPT or eMMC writes. Only a host-level temporary boot and serial read-only queries.

## Relevant kernel source and next engineering steps

Source `block/partitions/efi.c` for this BigPart Linux7 kernel validates exact factory GPT partition extents and remaps **only p8/p9/p10 starts and sizes** in `state->parts`; it sets metadata `info->uuid` using **`efi_guid_to_str(&ptes[i].unique_partition_guid, info->uuid)`** from GPT's per-entry unique GUID. The parser reads the relocated **alternate OEM GPT at physical sector 62513151** on this exact eMMC configuration. Source `block/early-lookup.c` resolves `root=PARTUUID=...` by comparing partition metadata UUIDs; `root=/dev/mmcblk0p8` uses separate device-name lookup. This strongly focuses diagnostics on **per-boot GPT metadata identity versus readback of raw GPT contents**. Validate against a READ-ONLY raw partition entry-array capture under owner-supplied root. No GPT writes or rewriting physical partition table are justified.

**Immediate recommended direction:** preserve current successful Stage-D boot, avoid Stage-E `PARTUUID` boot for now, fix internal p8 root `/etc/fstab` to **stable ext4 filesystem UUID** (after owner `sudo -s`, with bytewise backup and an exact one-field change), and retain **`root=/dev/mmcblk0p8`** in kernel boot image until an independently verified stable GPT GUID is available. Before making any permanent p7 change, validate device identify, original p7 backup, Stage-B rescue and explicit rollback, and at least one normal cold boot from chosen Stage-D image. User has not yet requested a permanent flash in this turn. An alternate longer-term solution could be initramfs-based filesystem UUID discovery if stable across boots. Separate root-cause research might compare raw OEM GPT sector and partition entry CRCs across boots.

