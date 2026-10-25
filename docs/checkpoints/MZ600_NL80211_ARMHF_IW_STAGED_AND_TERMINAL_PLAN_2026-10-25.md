# MZ600 Linux 7: Standard nl80211 Wi-Fi scanning utility staged — 2026-10-25

**Scope:** Whole BCM4329 combo-chip development. **This checkpoint is a userspace preparation milestone, NOT a Wi-Fi RF scan or Bluetooth pairing pass.** microSD remains out of Xoom during experimental boots. No flashed partitions, no new v06.2 USB command or live network changes.

## Why use standard Linux tools?

- Upstream `brcmfmac` with BCM4329 firmware registers `wlan0`. The built-in Linux `cfg80211` and `nl80211` are standard netlink APIs for Wi-Fi control.
- `iw` is the lightweight nl80211 userspace command for **AP discovery** and low-level capability queries. Example: `iw dev wlan0 scan`. A scan **may transmit probe requests**, even without authentication/association; honor signed kernel regulatory channel constraints.
- `ip link set wlan0 up` (from `iproute2`, or a correctly tested equivalent) is normally required before a scan. The bare diagnostic has no `ip` or `iw` yet, so do not assume `wlan0 PRESENT` alone means it can scan.
- `iwd` or `wpa_supplicant` handles authentication/association/roaming. `NetworkManager` can orchestrate those plus IP config; DHCP/IPv6 addressing and DNS are further steps. Our first minimal scanner should **not** connect or request credentials.
- Linux Wireless official docs: https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html and https://wireless.docs.kernel.org/en/latest/en/developers/documentation/nl80211.html

## Verified Debian 12 ARMHF binary acquisition

Official Debian Bookworm package page:
https://packages.debian.org/bookworm/armhf/iw
Official package download:
https://packages.debian.org/bookworm/armhf/iw/download

- `iw` version `5.19-1` (CLI displays `iw version 5.19`)
- Package: `iw_5.19-1_armhf.deb`, **93,300 bytes**
- Official Debian package SHA256: `fd1f6c926853505b0eb03a3afb4c6b68e4350f42b140fe6c5295012eeca872ee`
- Download URL: https://deb.debian.org/debian/pool/main/i/iw/iw_5.19-1_armhf.deb
- Exact public reproducible staging script: [`scripts/experiments/stage-debian12-armhf-iw-20261025.py`](../../scripts/experiments/stage-debian12-armhf-iw-20261025.py)
- Private Desktop WSL staging directory: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/userspace-network/bookworm-armhf-iw/`. Original .deb, extracted package and package+ELF hash provenance in `MANIFEST.json`, **not committed**.
- Actual `sbin/iw` ARMHF ELF32 little-endian, size **207,052 bytes**, instruction attributes do **not** mandate ARM NEON, consistent with Cortex-A9 Tegra 2.
- Direct dependencies from `readelf -d`: `libnl-genl-3.so.200`, `libnl-3.so.200`, `libc.so.6`, ARMHF `ld-linux-armhf.so.3`. All were **already present** in our separate Debian 12 armhf rootfs; dynamically linked `iw` alone is **not sufficient** for the freestanding RAM initramfs.
- Actual qemu-arm user test using Debian rootfs as `-L` loader/sysroot **PASSED**, emitted `iw version 5.19`. This is a CPU/loader/userspace smoke test, **not physical nl80211 scan compatibility**.

## Current kernel/hardware state and barriers

- Physically booted v06.2 clean Linux 7 remains running with USB COM9 responsive. BCM4329 Wi-Fi start created `wlan0`, loaded WCC/brcmfmac/brcmutil with firmware 4.220.48; shutdown successfully unloaded all and removed `wlan0`. Physically tested BT UART serdev/HCI0/ON/OFF/unload on same running kernel, followed by **Wi-Fi start/stop again** with all modules returning `rc 0`, USB PONG preserved. Sequential shared-chip validation **PASS**, simultaneous radios and actual RF scan **NOT TESTED**.
- Current diagnostic USB command list includes `WIFI_START`, `WIFI_STATUS`, `WIFI_STOP`, etc. **No nl80211 scan, generic shell or upload arbitrary binary execution**. Existing `UPLOAD` has narrow allowlist and must not be bypassed by writing a different binary into a Wi-Fi firmware path.
- Current kernel `CONFIG_CFG80211=y`, `CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y`, `CONFIG_CFG80211_USE_KERNEL_REGDB_KEYS=y`, `CONFIG_CFG80211_WEXT` disabled. Correct modern userspace interface is **nl80211**, not deprecated iwconfig/WEXT.
- Config also includes `CONFIG_VT=y`, `CONFIG_FRAMEBUFFER_CONSOLE=y`, `CONFIG_UNIX98_PTYS=y`, `CONFIG_INPUT_EVDEV=y`, so a genuine console is architecturally viable, but **our current test display is a custom framebuffer diagnostic, not an interactive shell.**
- v06.3 is an **offline-built**, **not booted** HCD-enabled image, SHA256 `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`. It adds private hash-pinned Broadcom `BCM4329B1.hcd` to the original v06.2 initramfs. Do not blindly append more untested changes until preserving the v06.3 candidate and test gates.

## Integration plan: standard scan, terminal and Bluetooth keyboard

1. Keep v06.2 hardware lifecycle and v06.3 offline HCD artifacts **immutable**, one source change/test per candidate; no kernel submission patches for stock Debian tools.
2. Introduce ARMHF `iw` and **only its required ARMHF runtime dependencies**, explicitly verify dynamic linker paths and boot-image 8MiB limit. Stage an `ip` implementation so `wlan0` can be set `UP`; later evaluate `iproute2` / BusyBox for full shell.
3. Expose a **bounded, explicit** `WIFI_SCAN` diagnostic command or real interactive terminal with controlled process execution and captured stdout/stderr. Preserve the independent COM9 PING/rollback path; record whether the scan request succeeded, BSS entries and signal strengths, and any regulatory/firmware errors. Do **not** collect or publish local SSIDs/MAC/BSSIDs unredacted in public repo logs.
4. Validate `iw phy` capability listing and a **single scan** on the correct `wlan0` with signed regulatory data. Scan is RF-active even if it does not connect; no association/DHCP/password until authorized.
5. For user's desired *on-screen terminal if Bluetooth keyboard works*: bring up standard VT/framebuffer terminal, armhf shell, input/evdev/HIDP and keyboard mapping, USB serial shell fallback. Avoid replacing USB diagnostics with an unproven shell and avoid binding the terminal to inaccessible hardware keys.
6. HCD patch should first be independently validated on a RAM-only firmware candidate with `BT_START` and read-only logs; Bluetooth pairing needs an agent (`BlueZ bluetoothd` + D-Bus and relevant HID input handling) and proper persistent bonds only when storage is available. Do not infer keyboard compatibility from `HCI_DEV_UP rc 0` alone.
7. Later whole-chip testing: **simultaneous Wi-Fi + Bluetooth**, proper shared regulator/reset clock handling, transitions between roles, and USB/power-off state. Keep firmware binaries private and actual source patches separately tracked.

**Status:** `iw` 5.19 Debian armhf is downloaded, hash-verified and tested under ARM emulation. Not yet in a Xoom boot image, and no network scan has occurred.
