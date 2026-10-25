# v05 clean upstream kernel early-startup SD breadcrumb physical attempt

**Date:** 2026-10-25 (EDT). **Source branch:** `wip/clean-upstream-usb-rebaseline-20261025`.

## Goal and precise changes

User directed continuation of clean Xoom-Linux kernel rather than further factory-boot restoration. Original TWRP and Android boot and system partition hashes were already physically confirmed factory-identical; ordinary Android reboot into factory `/system` passed. No eMMC installation or repartitioning here.

Exact original xoom-linux/linux kernel SHA `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` with the minimal Stingray USB peripheral DT derivative is reused **byte-for-byte** from prior clean v04 test. `zImage-with-stingray-usb.dtb` exactly unchanged. No BCM4329, MAC, SDIO, BT, FM, radio calibration or regulator patches.

`scripts/experiments/build-clean-upstream-v05-sdtrace-20261025.py` compiled v05 freestanding no-NEON PID1 by injecting a small diagnostic overlay into source-verified v04 USB diagnostic. It retains the existing USB PING/STATUS/LOGS protocol and framebuffer. Diagnostic changes: identify removable SD only by `/sys/block/mmcblkX/device/type == SD` and exact known 61067264 sectors; mount only matching partition 1 as ext4; write bounded kernel ring snapshots via syscall `syslog(3)` and `fsync` alternately to `XOOM-USB-BOOT-DIAG-A.log` and `B.log` at filesystem root, every ~5 sec after init. No internal MMC type device may be selected or mounted; no internal eMMC modifications. SD filesystem metadata changes **are expected**; the snapshots may fail if kernel/userspace crashes before reaching that point. Do not mistake absence of logs for definitive proof PID1 did not start.

Artifact: `MZ600-CLEAN-UPSTREAM-V05-SD-BREADCRUMB-RAM-ONLY.img` size **7,870,464 bytes**; SHA256 **`623d58bafd0ee1049e14baf0b9372dfa27b725d4d2d3d26644ad072e18ee5d81`**. Checksum independently matched on Desktop WSL, Windows Desktop, and Surface. Android boot image integrity check independently passed exact kernel length **7,860,816 bytes**, external diagnostic ramdisk **5,682 bytes**, correct Android header SHA1; source ARM EABI built `-mcpu=cortex-a9 -mfpu=vfpv3-d16` without NEON and QEMU no-NEON nonPID1 selftest passed. Original clean v04 image remains intact and separate.

## Physical one-shot test

Surface guard matched Android `stingray`, boot-completed, correct exact replacement MZ600 USB serial, removable SD `SD` and size 61067264 sectors; fastboot `product=xoom-cdma` unlocked; target image SHA rechecked before `fastboot boot`. USB host recorder saved a private timestamped log to `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V05-USB-Diagnostic-private-20261025.log`.

- **12:28:22 EDT** guard PASS and entered bootloader.
- **12:28:33 EDT** verified RAM-only boot initiated.
- **12:28:35.871 EDT** fastboot acknowledged `Booting OKAY`. **No flash, no internal writes, no auto reboot**.
- **12:28:44.291 EDT** host COM9 arrived.
- **12:28:44.337 EDT** first SerialPort **Open succeeded**.
- **12:28:44.441 EDT** subsequent first `PING` Write failed: Windows `MethodInvocationException` wrapping **“A device attached to the system is not functioning.”**
- Subsequent retries: `Open` errors **“The port 'COM9' does not exist.”**
- **12:28:45.320 EDT** COM9 removed.
- Final: PONG false, COM9 absent; 4 attempts/4 errors. Host ADB and fastboot absent following trial. No device reset automatically.

Compared with previous clean v04 COM9 ~13.38 seconds, this test COM9 ~1 second. Host now physically opened the serial port and immediately encountered a device I/O failure, making pure COM exclusive-open contention less likely, but it **still does not discriminate** kernel panic, power loss, PMIC, USB controller or device restart. Firmware and system mount location not changed; early boot root cause remains unresolved. Different timing is not a regression diagnosis without kernel logs.

## Preserving logs / immediate next task

Xoom currently not visible over ADB/fastboot; user physical Power+Volume Up intervention is required to return to TWRP. For next TWRP boot prepared private Surface script `C:\Users\olsen\xoom-linux-rom\captures\Xoom-Capture-V05-SD-Logs-ReadOnly.ps1`. It confirms hardware+removable/eMMC type+capacity, mounts **only** external ext4 p1 `ro,noload`, ADB-pulls A/B snapshot files into PRIVATE Surface capture directory and unmounts, without touching eMMC or replaying the ext4 journal. PowerShell syntax checked; **NOT EXECUTED** because no ADB currently. If logs present, inspect timestamps, kernel panic/pstore and last messages for USB/PMIC/SD/CPU before another Linux test. Keep unique serial, raw kernel logs, WLAN identities and passwords PRIVATE; commit findings and sanitized excerpts only.

Ramoops backend on **successful earlier Debian boot** had been confirmed in recovered journal: `OF reserved mem: 0x1ff00000..0x1fffffff ... ramoops`, `printk legacy console [ramoops-1] enabled`, `pstore Registered ramoops`; this is a second possible crash source if recoverable across boot into TWRP, but TWRP pstore support and preservation are unverified. Do not claim recoverability yet.

## Roadmap

- Recover SD evidence from TWRP.
- Diagnose whether PID1 mounts SD / reaches framebuffer / USB opens on device, and whether logs show a kernel crash or orderly power event.
- If no SD logs, use OEM UART / bootloader ramoops reserved-area / early kernel tracing and a separate minimal init image to narrow execution stage. Do not blindly repeat the same test.
- Once kernel stable, integrate Wi-Fi/Bluetooth/FM combo chip using current upstream Linux frameworks and isolate verified MZ600 vs family changes; design Linux eMMC installation separately after risk mitigation and tested boot recovery (Volume Down known defective).
