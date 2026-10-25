# Clean upstream Linux 7 v04: NO MICROSD physical USB/diagnostic PASS (2026-10-25)

**Branch:** `wip/clean-upstream-usb-rebaseline-20261025`  
**Scope:** user removed 32GB ext4 Debian microSD from the replacement MZ600, then manually entered fastboot. Only a `fastboot boot` RAM image was used; NO flash, eMMC mount/write, Android system alteration or automated restart.

## Input and exact control

- Device at Surface fastboot had the expected private device serial, `product=xoom-cdma`, `unlocked=yes`.
- Clean upstream kernel `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, minimal Stingray identity/USB0 UDC device-tree derivative, minimal v04 USB diagnostic PID1. **No Debian SD root or filesystem mounting.**
- Boot image `MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img`, 7,870,464B, SHA256 **`da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b`**; preflight length/hash checks PASS. This is **the same exact image** tested on Oct 25 with the SD inserted and 13.38s COM9 appearance then dropout/no PONG.
- Separate read-only Surface one-shot host script `captures/Xoom-Run-Clean-V04-No-SD-Once.ps1` was parser-checked and used to capture private USB timing. No automatic recovery or reboot.

## Physical no-SD results

- **12:57:44 EDT** fastboot image verification and RAM-only start.
- **12:57:46.626** fastboot transfer + `Booting OKAY`, no flash.
- **12:57:54.994** USB CDC ACM COM9 enumerated.
- **12:57:55.017** host opened COM9 successfully.
- **12:57:55.497** genuine **`PONG XOOM-LINUX V04`** received from Linux PID1 diagnostic over USB.
- **12:58:32.786** 46-second host observation completed with `ARRIVED=True GONE=False PONG=True PORT_NOW=True`. USB never disappeared during this monitoring interval.
- A second serial session opened independently and again received **PING/PONG**, STATUS, STORAGE, USB, LOGS and CMDLINE replies. COM9 still remained connected at the end.
- Live STATUS identifies `Linux version 7.0.0-next-20260422+`; `MMC PRESENT` and `FB ACTIVE`. Framebuffer activity reported by the diagnostic tool, not photographed. STORAGE `/proc/partitions` shows **only the 31,260,672KiB internal eMMC** as `mmcblk0`, its original p1..p10 plus `mmcblk0boot0/boot1`; no 32GB removable microSD block device, independently confirming absent card in Linux.
- Filtered live `LOGS` includes `xoom-init: USB ttyGS0 ready` at 2.524s, a known nonfatal `sound-hdmi ... parse error` and `vusb: disabling` ~32.5s; the latter is not a physical USB failure because COM9 and protocol continued operating much later.
- A read-only host transcript (possible private kernel/board identifiers) is retained on Surface at `C:\Users\olsen\xoom-linux-rom\captures\MZ600-NO-SD-LIVE-20261025-125917-PRIVATE.txt`. Keep raw logs and serial private; submit only sanitized, causally relevant excerpts to GitHub.

## Diagnostic implications

**Important correlated result:** The **same byte-for-byte clean v04 kernel/DTB/ramdisk Android boot image** previously showed COM9 for ~13.38s then disappeared with the 32GB microSD inserted, but **without the card** it boots to functioning PID1 USB gadget/diagnostic and remains reachable across multiple independent sessions. This is the first recent successful clean-kernel USB `PONG` after black-screen failures. Earlier v05 with the card inserted used the same kernel/DTB but a *different* RAM-based diagnostic program and wrote SD breadcrumbs, so do **not** call v05 a controlled identical-image comparison.

Removal of the card is a strong variable; plausible mechanisms are Tegra MMC controller/card detection and request/power/timing, card-dependent pinmux/PMIC regulator behavior, SD media integrity or intermittent contact. Do **not** declare media defective, kernel root-filesystem corruption, bootloader rejection, USB-only fault, regulatory country mismatch or specific MMC controller bug on this evidence alone. A prior TWRP SD insertion had intermittent `mmc1` timeout -110 before successful enumeration; read-only card/host tests and original verified ext4 root then passed. Preserve the Debian card and all installed data.

The bootloader *definitely* launched Linux far enough for freestanding PID1 to answer PING; screen-off red-LED with SD cannot therefore be categorically called pre-kernel bootloader refusal. Factory boot/system p7/p8 separately hash to original OEM values and Android boot physically passed.

## Next discriminating tests (one variable at a time)

1. Keep this **known live no-SD kernel** running long enough for another bounded USB uptime/PING observation; avoid speculative power/reset changes.
2. Capture complete early kernel ring, CPCAP/regulator, MMC host/controller and warnings from the stable no-SD run; avoid publishing device identifiers.
3. Recover v05 SD breadcrumb logs later by **TWRP mount `ro,noload`** (the microSD is now physically removed), without overwriting or reformatting the card. Those snapshots could reveal where an inserted card causes Linux to stop.
4. After preserving logs, test a controlled A/B with the exact same v04 image and same host protocol, first without card (PASS), then with original card (prior FAIL), and possibly with a different known-good microSD. Always completely power off before inserting/removing media; never hot-swap to provoke a crash unless OEM hardware specifically supports it and user approves.
5. If card presence reliably causes failure, test boot with Tegra external SDMMC host disabled in a **device-tree-only** diagnostic variant (while card inserted), separating physical card effects from controller enumeration; do not disable eMMC/boot or BCM Wi-Fi SDIO by accident. A different Linux root mounting path is not a supported fix yet.
6. Once stable, resume clean upstream BCM4329 integration, split model-specific fixes, and maintain separate production Debian installed OS path.

**Evidence class:** physical PASS for RAM boot → Linux PID1 → USB gadget → stable host commands with no removable card. Not a pass for native Debian root, Wi-Fi RF, suspend/resume, or internal Linux installation.
