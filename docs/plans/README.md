# Native Linux 7 implementation plans

## Current next-build instructions

- **[v06.4 functional Linux build — real Wi-Fi `iw` scan, framebuffer terminal, Motorola Bluetooth keyboard](MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md)**. This is an **approved engineering plan, not a completed image**. Contains precise ARMHF binary/library dependency checks, 8MiB size gate, RAM-only/possible removable storage options, build provenance, USB fallback, physical acceptance matrix, cleanup, whole-BCM4329 concerns and handoff update requirements. Read it after [the comprehensive project handoff](../handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md).

Latest source-of-truth device state: [runtime/CURRENT_LINUX7_STATE.env](../../runtime/CURRENT_LINUX7_STATE.env); latest physically completed milestone: [v06.3 HCD / HCI / Wi-Fi](../checkpoints/MZ600_V063_PHYSICAL_PASS_HCD_HCI_AND_BLUETOOTH_TO_WIFI_2026-10-25.md).

Safety: Keep protected original MZ600 untouched; experimental replacement MZ600 uses **hash-verified `fastboot boot` RAM-only** and no internal partition writes; private firmware, factory MAC, link keys and SSIDs must stay outside the public repository. v06.4 is not finished until actual radio scan, interactive terminal and keyboard pairing are physically demonstrated or individually marked PARTIAL/FAIL with evidence.
