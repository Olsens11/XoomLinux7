# MZ600 v06.4 — Original Xoom BigPart layout match (OFFLINE, no device access)

**Date:** 2026-10-25 late evening EDT. **Evidence:** PUBLIC SOURCE VERIFIED + VERIFIED HISTORICAL REPLACEMENT MZ600 BLOCK GEOMETRY + DESKTOP OFFLINE MATHEMATICAL AUDIT. **Not a physical BigPart boot/format/install.**

**User choice:** Xoom's original BigPart enlarged `system` p8 as conventional Debian Linux root `/`. Previous proposal to root Debian on p10 is **superseded**; p10 user data may be destroyed, no need to back it up. Preserve bootloader/vendor metadata, original TWRP recovery and protected original MZ600.

Original BigPart source: Schischu [2013 kernel patch `6b3d70fff905b7395fd15992c3779b27d1b6c101`](https://github.com/Schischu/android_kernel_moto_wingray/commit/6b3d70fff905b7395fd15992c3779b27d1b6c101), changes **virtual GPT partition view in the running kernel**, not the physical GPT. Original Wingray starts `0x1D000` system, `0x9D000` cache, `0xF1800` userdata match this **same replacement Verizon MZ600** precisely, as previously captured with TWRP.

The standard Xoom BigPart result using 512-byte sector layout (MZ600 total `62521344` sectors):

| Part | START factory / BigPart | SIZE factory / BigPart | BigPart physical ending sector (inclusive) |
|---|---|---|---|
| p8 `system` | 118784 / **118784** | 256MiB / **1024MiB** | 2215935 |
| p9 `cache` | 643072 / **2215936** | 169MiB / **512MiB** | 3264511 |
| p10 `userdata` | 989184 / **3264512** | 30040.5MiB / **28929.5MiB** | 62512127 |

All partitions p1..p7 **unchanged**; p10 ending sector unchanged. No overlaps, gaps introduced among p8-10 or crossed reserved boundaries. The earlier 768MiB Debian ext4 image fits the 1GiB system extent (future BlueZ packages/space still must be measured).

Host-side test: `python3 scripts/experiments/audit-mz600-classic-bigpart-layout-20261025.py --output /home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v064-preflight/MZ600-CLASSIC-BIGPART-OFFLINE.json` ran under `xoomdev` on WSL Ubuntu-22.04. Output `CLASSIC_BIGPART_OFFLINE_AUDIT_PASS`, with 1024MiB p8, 512MiB p9, 28929.5MiB p10 and explicit `NO GPT/DEVICE WRITES`. The report remains in private local artifacts, not in Git.

Important unresolved hardware gate: A **Stingray/MZ600-specific BigPart recovery** and Linux7 matching GPT parser/remap have not been verified or booted. Typical mirror filenames are Wingray/MZ604 and may not be compatible despite same sector offsets. Old TWRP 3.1.1-0 sees factory extents and **must not be used to write a BigPart-format p8**. Kernel7 `block/partitions/efi.c` has regular GPT parser, no original BigPart logic, and a relocated Tegra GPT at non-LBA1 remains to be physically demonstrated. Exact recovery boot/USB, independent rescue (bad Volume Down button), known red-LED event and detailed MZ600-specific device verification must pass before any format.

**Acceptance:** Original BigPart virtual-layout compatibility PASS OFFLINE. Actual BigPart recovery boot/recognition, Linux7 virtual p8, system wipe/install, new kernel, USB/RF/Bluetooth all **NOT TESTED**. No destructive write has happened.

See [active step-by-step BigPart system-root plan](../plans/MZ600_V064_CLASSIC_BIGPART_SYSTEM_ROOT_IMPLEMENTATION_2026-10-25.md).
