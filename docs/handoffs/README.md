# XoomLinux7 conversation and engineering handoffs

> **CONTINUATION AFTER HANDOFF — OCTOBER 28:** [Fastboot source-level GPIO restart priority conflict](../checkpoints/MZ600_FASTBOOT_REBOOT_GPIO_PRIORITY_ROOT_CAUSE_CANDIDATE_2026-10-28.md): GPIO reset priority 200 outranks PMC -128, potentially losing bootloader scratch mode. A test-only reversible unbind script is prepared; **no physical confirmation or new reboot yet**. Read alongside the comprehensive handoff below.

> **CURRENT COMPLETE HANDOFF — OCTOBER 28, 2026, START OF NEW LINUX INSTALLATION CHAPTER:** [MZ600 preinstallation, preserved Stage-D/V31 baseline, nine-patch review build, Debian images, backups, TWRP 3.1.1-0 and first remote fastboot test](MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md). This is the entry point for the next conversation. **Observed outcome:** reboot(2) requested bootloader but returned to ordinary Linux; no fastboot, no cold p8 capture, no replacement boot or flash. A rescue-SD one-shot cold-backup service remains **armed**. The older October 25 handoff and next-step notes below are historical; safety rules remain binding.

> **Verified current Oct 25 19:25 EDT:** v06.3 running USB/PONG, Bluetooth firmware/HCI and sequential Wi-Fi physically passed. **Next:** [v06.4 functional Linux implementation and acceptance plan](../plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md). v06.4 is not built, network scan/keyboard pairing and terminal not yet proven. Use the continuously updated complete handoff below.


## Current handoff: October 25, 2026

- [Comprehensive MZ600 / Linux 7 / BCM4329 engineering handoff](MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md) — full current state, kernel/DT architecture, exact hashes, physical Wi-Fi and Bluetooth tests, 2011 Motorola OEM evidence, intermittent USB/charger Power-button symptom, repo/worktree/tooling, preliminary patch queue, Debian ARMHF iw stage, HCD v06.3 **physically verified**, next user-requested terminal/keyboard and network scan steps.

### Interpretation and safety

Read the latest handoff and its dated checkpoints before using historical state files. The original Xoom with custom TWRP/XoomToolkit is protected. The replacement MZ600 is the Linux DUT. Experimental Linux images are **temporary, hash-verified fastboot boot only**, with no partitions flashed without explicit separate authorization. Public docs may include sanitized test hashes/results but never credentials, factory MACs, Wi-Fi addresses, pairing keys or proprietary firmware files.

Source and physical statuses are separate: **v06.2 is physically verified** for RAM-booted Linux/PID1, WLAN driver/wlan0 and Bluetooth HCI up/down plus sequential use; **v06.3 is now physically booted with its Bluetooth HCD patch path processed and HCI/WLAN sequential tests passed**; Debian armhf iw remains **offline-staged** and no Wi-Fi network scan, keyboard pairing or on-device terminal has been tested. The user wants a real on-device terminal with OEM Bluetooth keyboard and standard Linux Wi-Fi network scanning as immediate priorities, while tracking whole-chip power/coexistence and upstream-ready kernel patch candidates.
