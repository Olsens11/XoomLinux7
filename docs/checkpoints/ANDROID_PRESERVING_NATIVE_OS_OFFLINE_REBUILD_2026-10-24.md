# Android-preserving native Linux OS — verified offline rebuild

**Date:** 2026-10-24, after user clarified requirement for a conventional, reversible Linux/Android installation. **Result:** Source/package update + rebuilt normal boot and Debian ext4 image **PASS OFFLINE**; **no target partition created, mounted, resized, formatted or flashed**.

## Explicit new requirement

Keep the replacement Xoom's **existing Android system and user data unchanged**. The prior proposal to install Linux by replacing the Android `system` partition is **withdrawn**. Do not drop a second root directory tree directly into the Android `/system` filesystem: overlapping library/config paths would compromise Android. Also avoid an elaborate loopback/subdirectory boot if a dedicated ext4 filesystem can be used.

The preferred arrangement is a *separate, GPT-labeled partition* `xoom-linux`, preferably on internal eMMC **only if** actual free/available partition space can be verified and allocated without destroying Android; otherwise a dedicated ext4 microSD partition is a more nonintrusive standard Linux root. An installed OS can use the kernel's normal direct `root=PARTLABEL=xoom-linux rootfstype=ext4 rootwait` and `/etc/fstab` on the same label.

**Important:** There is **no known existing** `xoom-linux` partition yet. This boot image is **not bootable on the current unmodified device** until a separate, correctly identified Linux-only partition exists with its root image. Creation/resizing is not authorized. A legacy Xoom bootloader selecting normal `boot` versus a Linux image is a **different** problem from the root filesystem. Restoring a verified Android boot image is a possible recovery procedure but **no on-device boot chooser is confirmed**.

## Corrected builder and OS configuration

- `configs/os/fstab`: root `PARTLABEL=xoom-linux / ext4` instead of Android `system`.
- `scripts/os/package-native-os.sh`: default target `XOOM_LINUX_ROOT_PARTLABEL=xoom-linux`; validates label and **rejects** the names `system`, `userdata`, `data`, `cache`, `boot`, `recovery`, `misc`. Writes a normal Android-format *boot container* with native Linux kernel and ext4 root selector; **never** writes an actual device.
- `scripts/os/verify-offline-native-os.py`: checks `root=PARTLABEL=xoom-linux`, rejects `root=PARTLABEL=system` / `userdata`, checks rootfs `fstab` and every previous module/firmware/USB/kernel invariant.
- The original older candidate artifacts with `root=PARTLABEL=system` were hash-confirmed and moved under `/home/xoomdev/xoom-linux-rom/os-build/archive-rejected-android-system-root-target/` with `REJECTED-ANDROID-SYSTEM-TARGET.txt` do-not-install marker, **rather than being destroyed**. Older hashes remain in [prior offline build checkpoint](NATIVE_OS_OFFLINE_BUILD_PASS_2026-10-24.md) as historic evidence, **not current deployable artifacts**.

## New verified artifacts — on developer desktop WSL

Path `/home/xoomdev/xoom-linux-rom/os-build/artifacts/`:

| File | Size | SHA256 |
| --- | ---: | --- |
| `xoom-linux-boot.img` | 5,890,048 bytes | `40e32a9806183482b3e440ce493e505d9fa32b6f4c9dde9364f528b1b55c6756` |
| `xoom-linux-system.ext4` (legacy output **filename**, now a Linux-only root image) | 805,306,368 bytes = 768 MiB | `0aafdddccf58c5259007f272fb7878c417006629f5cb678c6d5e0f361ef8376e` |

**Filename clarification:** `xoom-linux-system.ext4` is now intended to be written **only into a new, verified Linux-only ext4 partition**. Its basename does *not* authorize writing to Android's `system` GPT partition. Future rename to `xoom-linux-root.ext4` is desirable to remove operator confusion; do not treat names as device locators.

Physical device state unchanged: v034 temporary diagnostic kernel running, USB COM9, MMC2 bound, both Wi-Fi modules unloaded, original 1,550-byte MAC-free NVRAM staged. No RF, no network association.

## Actual acceptance command

As root on Desktop WSL, `python3 .../scripts/os/verify-offline-native-os.py` returned:

```text
PASS: native root fstab targets dedicated Linux-only partition
PASS: offline ext4 integrity check clean (no write)
PASS: separate upstream module installed: brcmfmac.ko
PASS: separate upstream module installed: brcmfmac-wcc.ko
PASS: separate upstream module installed: brcmutil.ko
PASS: normal USB gadget serial login is enabled
PASS: no static or copied MAC in public DTB
PASS: ARM decompressor includes Motorola MAC→FDT startup translator
NATIVE_OS_OFFLINE_ACCEPTANCE_PASS kernel=7.0.0-next-20260422 boot_bytes=5890048
DEVICE_FLASHED=NO BOOT_TESTED=NO FACTORY_MAC_RUNTIME_UNVERIFIED
```

Other previously validated criteria also rechecked: full zImage+USB0 UDC DTB byte comparison against boot container, ARMv7 source/output, firmware and NVRAM SHA256, packaged inodes for USB login, separate WCC, non-default local owner credential hash (not printed), normal `systemd`, zero diagnostic initramfs, no §XOOM_V0xx§ brcmfmac instrumentation, and offline no-write `e2fsck -fn`.

## Necessary future verification before any deployment

1. Identify the **replacement** MZ600, not the protected recovery Xoom. Read **that actual unit's** GPT block start/end, sizes, GUIDs, any unused partition space, and filesystem/encryption status. The separate older Xoom's BigPart/noBigPart partition diagnostics **must not be assumed to describe this target**.
2. Choose an **existing independently available** or explicitly approved *new* Linux-only partition; if unsafe internally, a dedicated microSD ext4 partition offers conventional direct root mounting while keeping Android partitions untouched.
3. Check root image fits *within* its actual partition (including any reserved filesystem space) and verify partition labeling. Back up Android **boot** and any partition that will be modified, with byte-readback and off-device hashes. No change to Android `system` or `userdata`.
4. Verify host bootloader can boot Linux and *select or restore* Android's boot image. A boot-mode menu or dual boot manager is **not yet demonstrated**. Define a non-destructive fallback and get explicit user permission before writing specifically named partition(s).
5. First normal-boot test: native Linux root and USB `ttyGS0` login; inspect validity of Motorola's per-device `ATAG_STINGRAY_MAC` (without logging the MAC value); then modprobe separate WCC and brcmfmac; verify F2, native `wlan0` and per-device identity. Do **not** automatically scan/associate or configure regulatory transmitter.
6. Continue graphics/touch/Bluetooth coexistence, cold/warm boot and stability tests after normal OS root access is proven.

This update complements [comprehensive BCM4329 breakthrough milestone](BCM4329_BREAKTHROUGH_AND_NATIVE_OS_MILESTONE_2026-10-24.md). No maintainer contact has yet occurred.