# MZ600 Stage-E live-GPT-PARTUUID temporary boot — no Debian login, root selection still unresolved

**2026-10-26 approximately 04:18–04:22 EDT.** Experimental replacement Motorola Xoom MZ600, protected original not touched. **This supersedes the prior assertion that merely correcting the old saved UUID would restore PARTUUID-based early root boot.** That hypothesis did not work in this test.

## What was performed, physically

- Owner manually entered fastboot with repaired Power/Volume controls, with prepared microSD inserted.
- Surface fastboot identified **exact expected experimental MZ600 serial `170061c243805617`**, product `xoom-cdma`, `unlocked=yes`. USB COM port absent initially. Verified target Stage-E image `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-V064-BIGPART-INTERNAL-P8-TRUEGPT-PARTUUID-TEMPBOOT-OFFLINE-UNTESTED.img` is **6,645,760 bytes** with SHA256 **`c91d7f40d90df5bcb058fee6f843c64b46d02190b74eee36186ba3d9b4c3c63d`**.
- Executed **`fastboot boot` once, TEMPORARY ONLY**. Surface output:
```
Sending 'boot.img' (6490 KB)  OKAY [0.613s]
Booting                       OKAY [1.381s]
Finished. Total time: 2.001s
STAGE_E_FASTBOOT_BOOT_EXIT=0
```
- Host log `captures/MZ600-V064-StageE-InternalP8-TRUEGPT-PARTUUID-TEMPBOOT-20261026-PRIVATE.log`. **NO boot partition flash; NO filesystem format or eMMC write.**
- USB `COM9` enumerated, but **NO Debian login banner**. An attempted serial write returned Windows `The semaphore timeout period has expired`, as with earlier failed Stage-C. A later retry still showed COM9 with 0 readable bytes and same serial-write semaphore timeout. Host currently sees no ADB or fastboot connection after the temporary boot. **Stage-E root mount, systemd init and Debian login NOT verified.** Owner should photograph current physical screen to confirm exact kernel wait text.
- Independently examined source and three boot images on Surface: Stage-B SD-root has `root=PARTUUID=013b61e4-01` (MBR-style PARTUUID), Stage-D proven internal-root has `root=/dev/mmcblk0p8`, Stage-E currently failing has `root=PARTUUID=<private live p8 GPT GUID>`; other cmdline tokens the same (`androidboot.modelno=MZ600 product_type=cw console=tty0 loglevel=8 ignore_loglevel printk.time=1 rootfstype=ext4 rootwait rw init=/sbin/init`). Stage-D and Stage-E differ from Stage-B only in Android boot header commandline, kernel/ramdisk otherwise byte-identical. New Stage-E GPT GUID equals the **current private p8 GUID captured by running Stage-D** during the previous boot, not the stale original GUID used in Stage-C. We have **not verified that GUID remained stable across the new boot**, a key unresolved ambiguity.

## Why this matters

**Proven Stage-D success is still authoritative:** exact same Linux7 kernel boots native Debian 12.15 with `/dev/mmcblk0p8 ext4 /` internally, and USB login + `findmnt` physically passed. Thus the p8 ext4 filesystem and Debian userspace were bootable. After Stage-D success, owner supplied sudo and we guardedly corrected ONLY the internal p8 `/etc/fstab` root PARTUUID to the then-current p8 `/sys/class/block/mmcblk0p8/uevent` GPT GUID, preserving a bytewise original backup at `/etc/fstab.before-stage-e-live-guid-20261026`; audit showed only root field differed.

**Stage-C and Stage-E with `root=PARTUUID=<full GPT GUID>` both failed to reach Debian**, while Stage-B microSD SD partition `root=PARTUUID=013b61e4-01` and Stage-D internal p8 `root=/dev/mmcblk0p8` boot. On desktop kernel source `block/early-lookup.c`, `early_lookup_bdev(PARTUUID=)` delegates to `devt_from_partuuid()` matching registered block devices' `bd_meta_info->uuid`, while direct `/dev/mmcblk0p8` resolves via `devt_from_devname()`. Kernel `block/partitions/efi.c` uses actual GPT `unique_partition_guid` for partition metadata and remaps extents separately. **This suggests a GPT-PARTUUID registration, lookup or per-boot identity issue for the virtual BigPart p8.** Exact cause NOT proven; do not assert it is just udev symlink (kernel root lookup precedes udev) or merely a stale saved GUID. The prior missing `/dev/disk/by-partuuid` symlink is a *separate userspace symptom* until proven related.

## Current device state and next safe actions

- **CURRENT physical device may be stalled in temporary Stage-E**: COM9 present, unresponsive; screen not yet rephotographed this turn. No permanent storage changes during Stage-E test, so **p7 persists Stage-B Debian SD-root** (verified image SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`). **p8 ext4 Debian 12.15 was boot-proven under Stage-D**, no reformat required. p6 TWRP/partition table not changed.
- **First: ask owner to inspect/photograph framebuffer** for possible repeated `Waiting for root device PARTUUID=` or a new kernel error. Then power-cycle normally with prepared SD inserted; normal p7 Stage-B SD-root should recover. The owner can also manually enter fastboot and use TEMP `fastboot boot` of proven Stage-D for internal-root again. **Do not flash Stage-E**.
- Next engineering investigation: inspect per-boot p8 PARTUUID under known-good Stage-D and p8 GPT metadata, check whether GUID actually changes after cold/warm boots; or use small kernel instrumentation around early `devt_from_partuuid` / BigPart metadata to print lookup result and registered p8 UUID (without leaking exact private GUID publicly). Compare `root=PARTLABEL=system` diagnostic if useful. Avoid asserting cause without data.
- Safe practical fallback for eventual internal-root default: proven **`root=/dev/mmcblk0p8`** Stage-D could be a stable boot candidate with p7 backup, but it is currently only TEMP-boot validated (no ordinary cold persistent p7 boot yet). Need explicit user approval and rollback plan before overwriting p7. Must continue addressing module uname+ vs vermagic mismatch, Wi-Fi, systemd bus as separate tasks.


## Follow-up photograph physically confirms early kernel PARTUUID wait (2026-10-26)

The owner supplied a photograph directly in this conversation: `PXL_20261026_082627686.jpg`. This replaces the prior open question about what the Stage-E framebuffer showed. The screen **conclusively shows** the Stage-E Linux7 kernel does not resolve the requested `root=PARTUUID=<Stage-E true-prior-live p8 GPT GUID>`. Relevant visible lines (do not publish raw p8 GUID):

```text
[0.897294] mmcblk0: mmc0:0001 MMC32G 29.8 GiB
[0.904453] MZ600 BigPart: probing relocated OEM GPT at sector 62513151
[0.908727] Primary GPT is invalid, using alternate GPT.
[0.908886] MZ600 BigPart: validated exact factory 10-partition GPT; virtual
           system 1GiB, cache 512MiB, userdata 28929.5MiB
[0.909115] mmcblk0: p1 p2 p3 p4 p5 p6 p7 p8 p9 p10
[1.008262] Waiting for root device PARTUUID=<Stage-E GPT GUID>...
[10.725787] platform sound-hdmi: deferred probe pending: asoc-simple-card: parse error
[31.213907] vdd_led: disabling
[62.367013] random: crng init done
```

**Interpretation:** the MMC controller, eMMC enumeration, relocated OEM GPT probing, validated BigPart layout and all ten block partition nodes are reported before the kernel begins waiting for the root PARTUUID. No Debian userspace startup, mount, or login appears. The later HDMI/clock and random logs do not explain this failure. Stage-C with an older (stale/wrong) full GPT p8 PARTUUID showed the identical failure, whereas Stage-D, unchanged kernel+ramdisk but `root=/dev/mmcblk0p8`, physically booted Debian 12.15 and confirmed internal `/dev/mmcblk0p8 ext4 /`. The newer corrected Stage-E GUID came directly from the preceding working Stage-D boot, so its failure **cannot be ascribed solely to the old capture mistake**. It remains possible that the UUID itself varies across boots or that `block/early-lookup.c`'s UUID search cannot match BigPart p8 metadata.

**Next test when the user uses repaired keys to enter fastboot:** temporarily `fastboot boot` the already proven Stage-D devnode-root image SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`, leaving p7 unchanged; in a running internal-root Debian shell compare p8 `/sys/class/block/mmcblk0p8/uevent` PARTUUID against the saved Stage-E GPT GUID **without printing it to chat or public docs**. Also verify `findmnt /`, exact BigPart p8 LBA/size, and whether UUID changed between physical boots. If UUID is unchanged yet Stage-E hangs, prioritize scoped kernel instrumentation of `devt_from_partuuid` / partition metadata registration to establish the exact mechanism. No more p8 formatting or permanent p7 flash is indicated.

