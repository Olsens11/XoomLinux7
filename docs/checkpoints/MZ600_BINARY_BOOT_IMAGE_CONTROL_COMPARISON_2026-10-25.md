# Binary boot-image comparison — original microSD first boot, proven Debian boot, US/69 and clean rebaseline

**Date:** 2026-10-25. **Method:** Read-only offline parsing of original archived Android-format boot images on authorized Surface, including `ANDROID!` header, kernel payload, appended FDT magic/total-size, raw 512-byte legacy cmdline, compressed ramdisk and SHA256 identities. No passwords, private full root PARTUUID, MACs or firmware were printed; no tablet or storage modified.

## Previously missing chronological evidence

The **first temporary boot from the freshly installed and verified Debian microSD root was not confirmed**, before any US/69 regulatory experiment. Its initial 5,890,048-byte image `xoom-linux-boot-sd-20261025.img`, SHA256 `8bb0a98bab1a5043ab335a21a92fb43cf505a060d3c976e283ebdb60e1b9230d`, contained a **zero-byte ramdisk**. Fastboot reported boot OKAY but no Linux USB COM port/PID1 was observed; this alone did NOT document the later red-LED symptom.

The subsequent `xoom-linux7-SDROOT-nonempty-ramdisk-TEMPBOOT.img`, 6,645,760 bytes, SHA256 `c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c`, physically booted Debian 12.15 with a photo-confirmed tty1 login, authenticated COM9 USB login, microSD ext4 root, systemd PID1, Linux 7, `wlan0`, separate upstream WCC and dynamic identity. Its gzip CPIO contains v034 diagnostic components with the diagnostic `/init` renamed/disabled, allowing `init=/sbin/init` on the real root.

## Exact SHA256/byte-level structural findings

Extracted kernel binary = Android boot header kernel payload, consisting of compressed zImage and appended DTB. FDT start identified at compressed-kernel offset `5,826,304` (successful image), and DTB length from big-endian FDT header.

| Saved boot image | Total bytes | Kernel+DTB bytes | DTB bytes | Compressed ramdisk bytes |
| --- | ---: | ---: | ---: | ---: |
| `xoom-linux-boot-sd-20261025.img` (initial) | 5,890,048 | 5,887,396 | 61,092 | **0** |
| `xoom-linux7-sdroot-verbose-TEMPBOOT.img` (initial diagnostic variant) | 5,890,048 | 5,887,396 | 61,092 | **0** |
| `xoom-linux7-SDROOT-nonempty-ramdisk-TEMPBOOT.img` (successful Debian) | 6,645,760 | 5,887,396 | 61,092 | **754,277** |
| `xoom-linux7-mz600-us69-TEMPBOOT.img` (regulatory experiment) | 6,645,760 | 5,887,435 | 61,131 | **754,277** |
| `MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img` (new clean v04) | 7,870,464 | 7,860,816 | 61,104 | 4,855 |
| `MZ600-CLEAN-UPSTREAM-V05-SD-BREADCRUMB-RAM-ONLY.img` (new clean v05) | 7,870,464 | 7,860,816 | 61,104 | 5,682 |

### Controlled pairs

1. **First verbose failure vs successful Debian:** zImage **byte-identical**, full kernel+DTB **byte-identical**, appended DTB **byte-identical**, raw boot command line **byte-identical** including unchanged private PARTUUID (SHA256 raw cmdline same). **Only external ramdisk differs:** 0 → 754,277 bytes, with corresponding Android boot header/padding changes. This is unusually strong forensic evidence that the ramdisk composition/boot protocol matters; nevertheless the initial log records no confirmed USB and does not prove exactly where execution stopped.
2. **Successful Debian vs US/69 test:** zImage **byte-identical**, external ramdisk **byte-identical**, complete raw boot cmdline **byte-identical**, and the DTB is **39 bytes larger** with a different SHA. Thus the appended **device-tree change is the only payload difference** besides derived boot header alignment/ID. Chronologically the US/69 test was the first *post-success red-LED* failure, not the first failed boot; later retry of the exact successful image also failed, so US/69 cannot by itself explain all subsequent failures.
3. **Clean rebaseline v04 vs clean v05:** kernel+DTB, zImage, DTB and cmdline **identical**; external diagnostic ramdisk differs. Their v04/v05 COM9 lifetimes differed substantially (~13.38 seconds vs ~1 second) and no PONG was confirmed. Do not attribute differences automatically to the kernel.
4. **Original proven Debian vs new clean diagnostic v04/v05:** the **zImage is different** (original zImage ~5,826,304 bytes vs new ~7,799,712 bytes), appended DTB differs (61,092 vs 61,104 bytes), boot cmdline differs and ramdisk differs. All share original upstream ancestry, but the newly built configuration/image is **not** a byte-identical control for the proven Linux boot. It is incorrect to use "clean upstream" as synonymous with the tested exact working kernel binary.

These are **read-only offline binary facts**, not new physical kernel passes. The user-specific PARTUUID and factory MAC stay private.

## Implications for next kernel test

- **Preserve the exact successful 6,645,760-byte boot image as golden artifact**; do not overwrite it and do not reformat microSD or eMMC.
- Before another risky physical boot, examine private logs captured on removable SD by v05 if present; inspect pstore/ramoops without assuming persistence. A mere host USB disconnect is not a confirmed PMIC shutdown.
- Instead of rebuilding the whole generic kernel configuration, begin from the original proven kernel+DTB **byte-for-byte**. Change only its external RAM initramfs, ideally retaining full proven boot cmdline and nonempty CPIO layout. Demonstrate how diagnostic init hands off to external root and optionally logs earliest stages. Keep one-variable changes separately named and hashed.
- Compare exact known working to US/69 board DTS at node/property level for board-scoped regulatory mapping, but do not add US/69 again until stable boot repeatability exists and firmware calibration/legal channels are qualified.
- If the exact working image now fails after a true power-off/Android interlude, investigate system state/CPU power/USB behavior and restore logs; the image bytes themselves are unchanged and eMMC Android p7/p8 are factory-verbatim.
- When publishing upstream patches, split kernel/DT/firmware changes into focused increments and distinguish source build pass, bootloader acceptance, USB enumeration, real Debian login and RF verification.

## Primary project sources

- `docs/checkpoints/MICROSD_ROOT_OFFLINE_PREFLIGHT_2026-10-25.md`, OS working branch.
- `docs/checkpoints/MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md`, OS working branch.
- `docs/checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md`, OS working branch.
- The user-pasted original installation conversation confirms the SD card FAT32->ext4 procedure, exact physical SHA readback, clean ext4 expansion and the **first unconfirmed Linux boot**.
- Private Surface read-only comparison script: `C:\Users\olsen\xoom-linux-rom\captures\Xoom-Compare-20261025-Boot-Images-PRIVATE.py`.
