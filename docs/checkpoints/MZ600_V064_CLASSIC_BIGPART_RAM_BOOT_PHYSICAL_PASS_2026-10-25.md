# MZ600 v06.4 Classic BigPart — PHYSICAL PASS (RAM-only, no writes)

**2026-10-25 at 20:57 EDT.** Verified replacement Stingray CDMA MZ600 only. Full raw private log on authorized Surface: captures/MZ600-V064-BIGPART-STAGEA-TEMPBOOT-PRIVATE-20261025.log. No persistent device modifications.

## Source and offline boot artifact

- Pinned Linux 7 upstream commit 2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3. The isolated v064-bigpart-linux worktree retains verified v06.3 USB diagnostic and clean-board DTS, and adds exact original Schischu BigPart remap with strict 10-entry factory GPT validation, MZ600 model/internal eMMC bounds check, OEM relocated GPT LBA 62513151 and 64-bit gpt_sector option handling. Kernel has explicit eMMC-DT-only motorola,xoom-bigpart opt-in.
- Reproducible builder: [v064 isolated BigPart Stage A](../../scripts/experiments/stage-v064-bigpart-gpt-readonly-20261025.py). Local private artifact: artifacts-embedded-v064-bigpart-stageA/MZ600-V064-BIGPART-GPT-READONLY-STAGE-A-TEMPBOOT.img, 6,561,792 bytes, SHA256 626e33972bff4bcb6d4bfad895397b7ff28343a781322fad68cb96836ed94cf6. Included private Broadcom HCD firmware must not be published.
- SHA independently verified on Desktop and Surface. Surface independently checked Android! magic, 2048-byte pages, legacy SHA1 boot ID, no external ramdisk, identical bootloader load parameter bytes/boot cmdline as v06.3, appended correct DTB magic. Legacy v06.3 still exists unchanged, SHA256 07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e.

## Real physical boot

1. Starting at TWRP 3.1.1-0 root ADB, same-unit internal eMMC original factory map and relocated GPT were already physically verified read-only. Guarded adb reboot bootloader used; fastboot checked xoom-cdma unlocked and authorized private serial.
2. Exactly ONE verified image fastboot boot (never flash) accepted; fastboot transfer 1.114s, boot 1.390s. One initial serial MethodInvocationException recovered without reboots. Linux USB CDC COM9 PING -> PONG XOOM-LINUX V20 PASS at 20:57:47 EDT.
3. Read-only diagnostic STORAGE delivered Linux /proc/partitions on the actual hardware. Measured KiB block counts: mmcblk0 whole eMMC 31,260,672; p1 3,072; p2 2,048; p3 2,048; p4 4,096; p5 2,048; p6 recovery 12,288; p7 boot 8,192; **p8 system 1,048,576 (1,024 MiB)**; **p9 cache 524,288 (512 MiB)**; **p10 userdata 29,623,808 (28,929.5 MiB)**. Dedicated eMMC boot0 and boot1 each 2,048 KiB. Every required Classic BigPart dimension precisely matches the previously verified host geometry audit.
4. Surface guard verdict: V064_BIGPART_P8_1G=True P9_512M=True P10_REMAP=True. Bluetooth and Wi-Fi modules never started, no filesystem mount, no partition format, no raw sector write, no flash, no reboot. Raw kernel LOGS captured privately, never published.

## Next required gate

**BigPart physical partition enumeration PASS. Debian installation NOT done.** Current replacement device running this RAM-only stage-A v064 Linux7 image until a later documented action. Original Android system/boot and TWRP recovery remain unchanged, which means original TWRP's stock kernel still sees the old 256 MiB p8, and MUST NEVER be used to format/overwrite the new BigPart p8.

To populate p8, first use a BigPart-aware kernel with a verified **real Linux userspace and shell**. Reuse the already physically qualified Debian 12.15 microSD-root / USB-console runtime and this BigPart kernel source rather than inventing unsafe raw-sector writes or blindly flashing stock-geometry system via fastboot. Before any formatting confirm by-name p8 points to exact 1,024 MiB virtual partition, root filesystem of installer is removable SD (not internal p8), preserve independent recovery and p7 boot image. Write/readback-check exact hashed Debian root ext4 image; use appropriate ext4 grow procedure, prove temporary boot with root on p8, then separately qualify USB serial, display, iw scan, keyboard. Only then consider persistent p7 boot flash.
