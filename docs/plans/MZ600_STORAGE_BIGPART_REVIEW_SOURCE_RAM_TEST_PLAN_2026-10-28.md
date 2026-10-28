# STORAGE-01 — read-only test plan for exact upstream-form source

**PLAN ONLY; NOT AUTHORIZATION TO FLASH, REBOOT, WRITE, INSTALL OR MOUNT p8 RW.**
Test implementation: [STORAGE-01 unsigned RFC](../../patches/upstream/review-storage-bigpart-20261028/README.md);
milestone: [2026-10-28 BigPart checkpoint](../checkpoints/MZ600_STORAGE_BIGPART_SUBMISSION_FORM_RFC_2026-10-28.md);
current nine-source `507eb069df819cb5cc801ad8be096f70d9ca7609` (or its later
documented, exact-source revision). This plan must be re-evaluated if the
kernel source changes.

## Preparation and hard stop gates

1. Source must replay from the pinned upstream base using the separate
   3-DT + 1-ARM + 4-Wi-Fi + 1-STORAGE RFC members. Verify all review patch
   hashes and record toolchain, `.config`, final kernel source SHA, zImage,
   Stingray DTB, any matched modules and complete boot-image hashes.
2. Require `CONFIG_MOTOROLA_XOOM_BIGPART=y` **and**
   boot command-line `gpt xoom_bigpart=1`. The old installed kernel used a
   different BigPart activation scheme: **do not reuse its boot arguments
   without adding the new explicit opt-in**.
3. Preserve existing verified p7, p8, GPT and recovery information on the
   authorized MZ600. Never use an ordinary TWRP kernel to format, fsck-write,
   or mount BigPart p8 RW. Have independently proven RAM boot/rollback and
   USB serial/host procedures available and identify the exact device first.
4. Build a **private, temporary, RAM-boot-only** image using the reviewed
   zImage and correct Stingray DTB. Do not flash p7, update eMMC/GPT, install
   an OS, or include firmware in the public patch repository. Target a
   trusted initramfs or removable-SD root where internal p8 need not mount
   to obtain a shell.
5. Run only after separately authorized hardware access and review of the
   complete boot image. Do not carry out this plan automatically in a
   documentation or source-QA milestone.

## Read-only physical acceptance

On the exact authorized MZ600 temporary boot:

- Confirm the boot banner/kernel release and exact image/hash provenance.
- Read `/proc/cmdline`; verify **both** `gpt` and `xoom_bigpart=1` are
  present and no conflicting legacy override is required.
- Inspect `dmesg` for native Tegra MMC alternative GPT detection and any
  BigPart refusal message. Do **not** assume that a correct-sized p8 means
  the native GPT retrieval path was verified; record the actual evidence.
- Inspect `/proc/partitions`, `/sys/class/block/mmcblk0p*/start` and
  `/sys/class/block/mmcblk0p*/size` **without any device writes**.
  Expected 512-byte sector map:
  p8 start **118784**, size **2097152** (1GiB);
  p9 start **2215936**, size **1048576** (512MiB);
  p10 start **3264512**, size **59247616** (28,929.5MiB).
  Verify p1..p7 preserve their factory starts/lengths; the final p10 end
  remains **62512127**, before OEM relocated GPT at **62513151**.
- Verify runtime does **not** mount p8 read-write or run filesystem journal
  replay. The first experiment should be partition *enumeration only*.
- Capture sanitized logs with exact kernel/DTB/module hashes and recorded
  stop/rollback status. Any mismatch, wrong capacity, parser refusal,
  wrong device or missing expected p8 size is a **STOP**, not a reason to
  format or rewrite storage.

## Separate negative cases (never mutate the live eMMC)

Use synthetic disposable GPT-sector images and/or isolated kernel test
harnesses to exercise corrupted CRC/header, absent header, shifted extents,
new active p11, wrong disk capacity, mismatched controller and both opt-in
states. Test disabled CONFIG separately on a clean build. Host arithmetic
tests alone do **not** prove the C parser's failure path.

## Milestone closure

On completion or a blocked trial: record new dated immutable checkpoint,
exact source commit, all artifact hashes and raw-log location, PASS/FAIL/OPEN
per test, changed G01–G12 gates, maintainer route and next code decision.
Update the original STORAGE-01 focused patch in place if findings require
a code correction; do not append a chronological upstream fixup. Actual
upstream posting remains prohibited until full Xoom BCM4329 integration is
ready and specifically authorized.
