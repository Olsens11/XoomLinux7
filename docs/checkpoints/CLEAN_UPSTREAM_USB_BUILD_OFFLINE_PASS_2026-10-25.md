# Clean upstream Linux 7 + minimal USB tool: offline build PASS

**Date:** 2026-10-25
**Branch:** `wip/clean-upstream-usb-rebaseline-20261025`
**Machine:** Desktop WSL Ubuntu-22.04 xoomdev ARM GCC 14.3 toolchain
**Device:** Replacement Motorola Xoom MZ600 currently black/red LED, **NOT accessed in this build**.

## Result (verified build artifact, not physical test)

- Exact clean upstream kernel source: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Original checkout clean, copied into detached worktree.
- Baseline config from upstream `tegra_next_defconfig`, with required standard ARM appended DTB/ATAG and `USB_G_SERIAL`, Tegra ChipIdea UDC, devtmpfs and pstore enabled; NEON disabled and `INITRAMFS_SOURCE=""`. No Wi-Fi or BT source patches.
- Generated isolated Stingray USB0 peripheral DTS from upstream Wingray base: model, compatible, USB controller and PHY mode only; exact four anchor replacements validated. One new Makefile build target; no upstream source file permanently changed.
- Existing freestanding minimal **v04 read-only USB diagnostic** CPIO from `phase1-v04/phase1-initramfs.cpio.gz` (4855B, SHA256 `e06a62070ef255fed1db39c7d22e6b1d2a6ab6955258eacd3c8dffa50f69d8ba`) embedded as an external Android boot ramdisk. v04 `init.c` from WSL and GitHub match byte-for-byte (SHA256 `aaed4a0ec02ceefcc8ff89e5da89029c4ca84193bebffc28909032cb698782e2`).
- First all-stock kernel compile failed due to an **unrelated stale upstream STMicro IIO sensor-hub driver**: `drivers/iio/imu/st_lsm6db0/st_sensor_hub.c:18` includes missing `linux/of_gpio.h`. Resolved for this USB control by disabling only `CONFIG_IIO_ST_HUB_DRIVERS` in its isolated **build configuration**, not by copying/changing the driver code. This is a separate possible upstream issue; not a BCM4329 fix.
- Second incremental build succeeded: kernel `Image`, compressed `zImage`, target DTB and Android boot image, integrity tests performed by script.
- Kernel `zImage` **7,799,712 bytes**, SHA256 `1fb979c23a4fd2e2f90d0e4e92ceffe71c3b69abe24786e383c3b122df6d53c9`.
- Stingray minimal USB DTB **61,104 bytes**, SHA256 `a352337e2a8554322a83ca430cb0632b7a1fb390cd15137a0c5f895169ee7c37`.
- Android **RAM-only, untested** boot image `MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img`, **7,870,464 bytes**, SHA256 **`da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b`**. Size is under 8 MiB but leaves only ~506 KiB margin, so monitor downstream patch growth.
- Verified `ANDROID!` header, board boot addresses/page alignment, concatenated kernel/DTB byte match, CPIO/gzip integrity and image size. **Note:** build script currently checks CPIO and contents, but does not independently recompute the Android header SHA-1; before physical use we should check independently rather than infer.
- Copied exact compiled image to Desktop Windows `C:\Users\Olsen\MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img`, then securely copied to Surface `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img`. Source and both copies SHA256 agree.
- All Android internal eMMC and 32GB removable microSD partitions **UNCHANGED** by build. No `fastboot boot`, `fastboot flash`, adb reboot or GPIO/radio actions were issued.

## Next controlled device step

User must first restore accessible Android using Power+Volume Up (once ready). Require exact `stingray` ADB identity, normal Android boot, original hardware power state and image SHA guard; then perform one **temporary** `fastboot boot` of this image with host timestamped VID_0525/PID_A4A7 enumeration and v04 PING response. Do not automatically repeat if COM9 drops or perform any flashing. The image is a **new unproven** build despite successful offline integrity.

**Do not install Debian into factory `system` p8:** backup shows 268,435,456B partition; Debian used ~449MiB before resize. Internal factory eMMC partitioning was never changed. Replacement OS partitioning requires a separate, rollback-verified design after RAM-only platform stability, Android OEM reference harvest and explicit named-partition authorization.

**Goal:** establish kernel and USB startup stability before adding verified MAC/SDIO/Bluetooth/whole-chip patches one at a time and packaging upstream-suitable changes.
