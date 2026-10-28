# MZ600 installed Stage-D kernel vs clean nine-patch review source — 2026-10-28

**Comparison checkpoint — offline/read-only host artifacts and prior physical receipts; NO live device access, no flash/reboot/install.** This compares the physically SHA-verified persistent Stage-D **boot image** and the Stage-B build it was derived from, against the completely built current nine-patch source. The persistent image itself was not re-read during this comparison.

## Exact source and artifacts

| Evidence | Installed Stage-D / Stage-B provenance | Clean nine-review source |
| --- | --- | --- |
| Kernel base | `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` with v06.4 downstream ATAG, Stingray DTS and GPT overlays | Same pinned base with 3 Tegra DT + 1 ARM ATAG + 4 brcmfmac + 1 block/GPT logical review commits |
| Actual running kernel release | `7.0.0-next-20260422+` physically observed | `7.0.0-next-20260422+` built |
| `.config` | `v064-bigpart-debian-sdroot-build/.config`, SHA256 `e613d891a75e0e2e8f9b87d55fa7023936d48ecec7d3126ea6f4eeaef6dd5cef` | **byte-identical** `qa-nine-review-v2-build-20261028/.config`; same SHA |
| Embedded kernel initramfs | **Stage-B / Stage-D kernel build** has `CONFIG_INITRAMFS_SOURCE=""` | Also `CONFIG_INITRAMFS_SOURCE=""` |
| Compressed ARM zImage | Stage-B build 5,826,464 B; SHA256 `d0ada47734cd7686f780cb37f9abb95e354a80d333840c7979b756053fe6a9d1` | 5,826,528 B; SHA256 `570c98f1ce187f33c46cc671bb54b0e7b4837756bbec97ef721f8b4c998a5cf1` |
| Boot partition | Persistent Stage-D boot image **6,645,760 B**, SHA256 physically matched over same length from eMMC p7: `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`. Full 8MiB p7 SHA256 `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c` | Review build produces kernel/DTB/modules, **no comparable Android-v0 boot image has been installed or validated on device** |
| Board DTB | `tegra20-motorola-stingray-clean-usb.dtb` 61,138 B (Stage-B kernel + DTB = 5,887,602 B as recorded) | `tegra20-motorola-stingray.dtb` 61,076 B |
| Internal root | Physically proven `/dev/mmcblk0p8 ext4` read/write, Debian 12.15 | Desired same internal root, **not hardware-tested** |

**Important provenance correction:** An older `v064-bigpart-build/.config` (Stage-A) embeds a private `v063-private-bcm4329b1-firmware.cpio.gz`. That is **not the actual Stage-B build used to derive the persistent Stage-D image**. The correct Stage-B `.config` and new nine-patch `.config` match byte-for-byte, both with empty kernel embedded initramfs. The Stage-B/Stage-D Android boot image still contains a *separate external ramdisk*, which is not implied by the kernel CONFIG setting. Proprietary runtime resources must remain outside review patches. Do not compare raw Stage-D boot-image SHA to a naked zImage SHA as like-for-like.

## Compiled device-tree semantic difference

Both compiled Stingray DTBs were decompiled read-only with `dtc -I dtb -O dts -s` and diffed. There were **exactly two** changes:
1. Root descriptive `model` from `Motorola Xoom (Stingray MZ600 minimal USB diagnostic)` to `Motorola Xoom (Stingray)`.
2. Removal of `motorola,xoom-bigpart` Boolean from `/mmc@c8000600` (internal eMMC). The new storage RFC uses explicit `gpt xoom_bigpart=1` kernel parameters and `CONFIG_MOTOROLA_XOOM_BIGPART=y` instead of this undocumented DTS policy flag.

No other decompiled DT property differed, including SDIO, clock, GPIO, regulator and USB descriptions. Both decompilations emitted the same seven existing warning categories; DTS schema acceptance remains separately open.

## Module ABI: real distinction even though the kernel release matches

Both built kernels advertise `7.0.0-next-20260422+`. The previous V31 *lab* brcmfmac module and new nine-review `brcmfmac.ko` have identical vermagic `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`, but their binaries are **not identical**: V31 laboratory candidate SHA256 `c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8` vs review module `5e767d47017ff9028e6c364f8325420b0fc79efd1c1e07d36595fb4fd0540d26`. A 2026-10-28 physical postboot checkpoint confirmed V31 scan-generation and terminal-owner parameters active on the tablet; it did not establish byte identity of the installed filesystem .ko with this offline V31 artifact.

Stage-B and new nine-source `Module.symvers` both contain **14,030 named exports** with no added/missing symbols, but differ in **exactly three CRCs**, all Broadcom:
- `brcmf_fweh_register`: installed-build `0x1d31861b` → review `0x9c21b40f`
- `brcmf_fwvid_register_vendor`: `0xbe543d6e` → `0x3b7b85dd`
- `brcmf_set_wsec`: `0x3ffcd99d` → `0x16dd9685`

Therefore `uname -r` and modinfo vermagic alone **do not establish module interchangeability**. Test with a matched, complete review-source module set and matched WCC component; never combine the new core module with arbitrary installed V31/WCC artifacts, nor assume the earlier installed 114 modules all remain proven without a CRC/dependency audit.

## Runtime functionality: existing hardware proof versus untested reviewed code

- **Installed:** BigPart was physically booted with p8 1GiB, p9 512MiB and p10 28,929.5MiB. Permanent p7 Stage-D image and internal p8 Debian were hash/boot verified. The V31 lab module demonstrated two successful successive ESCAN completions; another reboot demonstrated WPA2, DHCP, DNS, NTP and HTTPS success **eventually after ~399 s**, with serious association latency and connection-event index issues still unresolved.
- **New:** Reconstructed equivalent intended channel, ESCAN generation, terminal owner and conditional WLC_UP changes as 4 logical Wi-Fi patches, plus ARM MAC ATAG, board and opt-in BigPart source patches; 9-member clean replay and full ARM `zImage dtbs modules` cross-build PASS. The exact clean kernel was **not loaded on the physical MZ600**. New source has fewer experimental diagnostics; no physical Wi-Fi, boot, suspend/resume, Bluetooth coexistence or p8 mount proof can be borrowed from V31.

**Critical boot-argument difference:** Old installed BigPart uses the device-tree flag `motorola,xoom-bigpart` and downstream `gpt_sector=` fallback. The revised review source removes both and defaults to ordinary GPT behavior until `CONFIG_MOTOROLA_XOOM_BIGPART=y` **and** bootargs `gpt xoom_bigpart=1` are present. Never try to boot the existing BigPart-formatted p8 with missing opt-in, or mount/recover it under ordinary 256MiB p8 geometry. Follow [guarded RAM-only read-only test plan](../plans/MZ600_STORAGE_BIGPART_REVIEW_SOURCE_RAM_TEST_PLAN_2026-10-28.md), first using partition enumeration only and no writes.

## Disposition

**Nearly aligned by configuration and hardware description; not a drop-in boot replacement yet.** Whole-chip integration still needs exact private boot packaging and cmdline, correct matched review modules, synthetic GPT/controller fail-closed tests, guarded physical MZ600 boot, repeated Wi-Fi and auth tests, BT/SDIO/power validation and upstream-maintainer design review. No patch posting/human signoff and no live device changes were made in this comparison.
