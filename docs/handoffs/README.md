# XoomLinux7 conversation and engineering handoffs

## Current handoff: October 25, 2026

- [Comprehensive MZ600 / Linux 7 / BCM4329 engineering handoff](MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md) — full current state, kernel/DT architecture, exact hashes, physical Wi-Fi and Bluetooth tests, 2011 Motorola OEM evidence, intermittent USB/charger Power-button symptom, repo/worktree/tooling, preliminary patch queue, Debian ARMHF iw stage, HCD v06.3 offline-only, next user-requested terminal/keyboard and network scan steps.

### Interpretation and safety

Read the latest handoff and its dated checkpoints before using historical state files. The original Xoom with custom TWRP/XoomToolkit is protected. The replacement MZ600 is the Linux DUT. Experimental Linux images are **temporary, hash-verified fastboot boot only**, with no partitions flashed without explicit separate authorization. Public docs may include sanitized test hashes/results but never credentials, factory MACs, Wi-Fi addresses, pairing keys or proprietary firmware files.

Source and physical statuses are separate: **v06.2 is physically verified** for RAM-booted Linux/PID1, WLAN driver/wlan0 and Bluetooth HCI up/down plus sequential use; **v06.3 and Debian armhf iw are offline-only** and have not yet demonstrated HCD application or Wi-Fi scanning on hardware. The user wants a real on-device terminal with OEM Bluetooth keyboard and standard Linux Wi-Fi network scanning as immediate priorities, while tracking whole-chip power/coexistence and upstream-ready kernel patch candidates.
