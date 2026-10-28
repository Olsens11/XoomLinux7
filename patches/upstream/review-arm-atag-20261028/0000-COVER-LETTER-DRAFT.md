# [RFC PATCH 0/1] ARM: tegra: propagate Stingray WLAN factory MAC from bootloader

**Draft for internal review only. Not sent or human-signed.**

This proposes to make the Motorola Stingray bootloader-provided WLAN
identity available to Linux through the SDIO node's local-mac-address.
The change is isolated from Broadcom Wi-Fi protocol compatibility,
board DTS descriptions, Bluetooth and in-memory BigPart GPT handling.

The implementation was reconstructed as one source commit on the pinned
Xoom-Linux 7 base. It passes strict checkpatch, but has not been run on
the tablet in this exact form. ATAG provenance, bounds, FDT update
failures, board targeting and upstream ARM/Tegra ownership require
review before any submission. No proprietary firmware or user-specific
MAC information is included.

The wider XoomLinux7 project withholds ALL submission until complete
whole-chip integration is ready and the human owner separately approves
posting.
