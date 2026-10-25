# Factory boot/system physical verification — October 25, 2026

## Result: the original boot-to-system path is already intact

This is the direct answer to the user's concern that our Linux-from-microSD experiments might have permanently redirected the internal Android boot partition. The tested Linux SD-root instruction was carried in the command line of a temporary boot image passed to fastboot boot. It was not flashed to internal boot.

The user physically returned to TWRP 3.1.1-0. Surface ADB verified stingray hardware, MZ600 OEM model boot arguments, and the actual eMMC by-name partition aliases. In this recovery session removable microSD was mmcblk0 and eMMC was mmcblk1. These indices are not universal; identify storage by hardware and by-name aliases.

**LIVE eMMC factory readbacks (read-only):**
- boot, eMMC p7, 8,388,608 bytes: SHA-256 4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3 — exact match to factory Android HMJ37 boot backup and prior boot readback.
- system, eMMC p8, 268,435,456 bytes: SHA-256 f17e1d2e4183c2d1283ad7282b8981764c0a64653eb3d11acc07a9aee89c5ab1 — exact match to original HMJ37 system partition backup.
- Boot image factory header has no SD root=PARTUUID override. Its OEM legacy header hash should not be evaluated using a simplified modern boot-header SHA1 convention (OEM factory and physically working TWRP legacy IDs similarly differ).
- No modifications were made to boot, system, recovery, eMMC GPT or microSD during this verification.

**PHYSICAL NORMAL BOOT PASS:** Authorized reboot command issued from TWRP into the ordinary factory boot flow. Surface then verified the Xoom reports Android 3.1 HMJ37, ro.product.device=stingray, sys.boot_completed=1, and the live filesystem mount reports:

    /dev/block/platform/sdhci-tegra.3/by-name/system /system ext4 ro

This proves actual original Android boot -> Android init -> factory internal system path, not merely on-disk files.

## Distinguish temporary Linux boots

Our external SD root was selected by parameters like root=PARTUUID=... rootfstype=ext4 rootwait rw init=/sbin/init embedded in the temporary alternate Linux boot image. Fastboot boot uploaded its kernel/ramdisk into RAM; no fastboot flash was issued, no persistent p7 rewrite. After reboot original Android's p7 boot image was again loaded. The microSD's altered MBR is irrelevant to factory Android's system mounting. A separate minimal Linux 7 v04 USB diagnostic with NO SD root dependency also reproduced USB loss and dark screen/red camera LED (COM9 duration around 13 seconds); therefore this symptom cannot be confidently blamed on the chosen filesystem location.

## Next engineering action

No evidence supports “repairing” p7 or p8; both are factory-identical and physically booted. Keep stock Android as an OEM hardware reference. Establish Linux kernel/platform boot reliability and early serial/pstore evidence without permanent flashing. USB tool ownership and COM9 open failures need more accurate diagnosis. Reintroduce candidate BCM4329 native patches individually into the pinned xoom-linux kernel and submit only logically isolated, validated changes.

An eventual **installed** Linux OS on internal eMMC remains the goal, but requires a deliberate layout; factory p8 system is only 256 MiB and cannot hold the staged Debian filesystem unchanged. The faulty Volume Down button complicates recovering from an unbootable p7 replacement: validate a button-independent entry to recovery/fastboot and restore procedure before any explicit-approved internal flash.
