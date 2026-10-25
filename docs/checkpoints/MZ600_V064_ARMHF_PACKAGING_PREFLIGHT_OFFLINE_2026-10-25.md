# MZ600 v06.4 — ARMHF dependency and packaging preflight (OFFLINE)

**Date:** 2026-10-25, evening EDT. **Evidence class:** OFFLINE HOST PREFLIGHT ONLY.

## Scope and machine

Read the [v06.4 acceptance/build contract](../plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md) and [current handoff](../handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md). Via authorized Desktop Commander, inspected the existing Desktop WSL Ubuntu-22.04, as user `xoomdev`, using the **replacement MZ600's existing kernel build and a Debian 12 Bookworm ARMHF sysroot**. No USB commands to the tablet, downloads, reboots, firmware activation, eMMC modification, flash, build image or kernel recompilation were performed in this preflight.

Repository project checkout `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project` was initially clean at `248803b7ef6c31a5175c93585e9f6b90bdcdbed9` on `wip/clean-wifi-bt-usb-20261025`; GitHub branch head matched. Kernel tree `clean-wifi-bt-usb-20261025/linux` is pinned at upstream `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` and contains the previously documented **uncommitted** clean USB/DTS edits. None were overwritten, reset or cleaned.

## Reproducible host measurements

Public reusable preflight: [`scripts/experiments/preflight-v064-armhf-dependency-closure-20261025.py`](../../scripts/experiments/preflight-v064-armhf-dependency-closure-20261025.py). The script checks the immutable v06.3 image SHA, recursively walks ARMHF ELF dynamic `DT_NEEDED` dependencies and `PT_INTERP`, inspects host availability, and saves a local private report. It does not contact hardware.

**Preflight executed and completed** on the Desktop. Local output: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v064-preflight/PREFLIGHT.json`. The file has not been published.

- v06.3 immutable input: **6,561,792 bytes**, SHA256 `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e` (preflight SHA guard passed).
- Conservative Android RAM-boot image ceiling: **8,388,608 bytes**, remaining **1,826,816 bytes** (before adding any v06.4 components).
- Config explicitly has `CONFIG_VT=y`, `CONFIG_VT_CONSOLE=y`, `CONFIG_FRAMEBUFFER_CONSOLE=y`, `CONFIG_BT_HIDP=m`, and `CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y`. Compiled `net/bluetooth/hidp/hidp.ko` exists locally but **is not yet included in v06.3 initramfs**.
- v06.3 embedded CPIO contains `/init` **as an ARM ELF executable**, the radio modules/firmware and small directory/device-node set; it contains no standard shell, `iw`, `ip`, BlueZ daemon or pairing client.
- Available in the Debian ARMHF sysroot, with no unresolved ELF closure dependencies found by `readelf`: `dash` **1,362,012 raw bytes / 794,613 gzip proxy bytes**, `iproute2 ip` **2,325,572 / 1,320,857**, `iw` **1,637,340 / 901,218**, `getty` **1,272,344 / 769,738**. These figures each include transitive libraries and are **not additive** (libraries overlap); gzip of concatenated ELF contents is an **estimate only**, not the kernel's actual compressed zImage delta.
- `readelf -A` did not report NEON on the inspected executable candidate objects. This is not proof that every future binary is safe for Tegra 2.
- `busybox`, `bluetoothd`, `bluetoothctl`, and `dbus-daemon` **MISSING** from the inspected sysroot; signed `regulatory.db` and detached `.p7s` files also **MISSING from checked sysroot paths**. This is a packaging gap, not proof of a missing kernel trust key or an on-device regulatory failure.
- Original ARMHF `iw` 5.19 had separately passed the prior QEMU smoke test; **this new preflight did not run QEMU or any physical RF test**.

## Engineering consequence and next work

One self-contained <=8 MiB image for the *complete* interactive terminal + standard `iw` scan + BlueZ keyboard has **not been proven to fit**. Do not assert failure purely from summing individual compressed closure numbers. Resolve and hash-pin the Debian ARMHF BlueZ/D-Bus packages, acquire/validate a kernel-trusted signed regulatory database, consider a lean BusyBox for `ip`, calculate *combined* closure and actual incremental kernel compression, and select an honest architecture. If it cannot fit, use a reviewed RAM-only USB userspace transport or separately user-authorized removable SD; no eMMC writes.

Before device use: build an isolated v06.4-stage candidate, preserve the original v06.3 image, prove USB recovery shell and display, then deliberately qualify scan and keyboard under the existing RF/shared-chip safety gates. **All physical v06.4 gates remain NOT TESTED.**

## Current acceptance snapshot

| Gate | Current state |
| --- | --- |
| v06.3 replacement MZ600 rollback | PHYSICAL PASS (earlier documented, unchanged here) |
| v06.4 offline ARMHF inventory | PASS |
| v06.4 boot image built | NOT TESTED / NOT BUILT |
| Visible shell and USB-shell fallback | NOT TESTED |
| Real `iw` scan | NOT TESTED |
| HCD + BlueZ keyboard pairing and typing | NOT TESTED |
| Ordered Wi-Fi/BT teardown regression on v06.4 | NOT TESTED |
| Wi-Fi + Bluetooth simultaneous operation | NOT TESTED |

No private firmware bytes, MAC, local SSIDs, credentials or device capture are published.
