# Project intent and scope

Take forward the original [xoom-linux/linux](https://github.com/xoom-linux/linux) Linux 7.0 development for Motorola Xoom Tegra2 hardware, with respect for the author's work and the conventions of the wider Linux kernel project. Start from upstream drivers and the contributed Wingray device tree; add thin Stingray board integration rather than a separate fork of every subsystem.

**Immediate goal:** hardware-qualified native Linux for MZ600/MZ604: display, touch, MMC, USB, Wi-Fi, power/charging, Bluetooth and eventually audio. Bring-up must be observable and reproducible.

**Intended later software:** Debian armhf userspace on a durable Linux install; then experimental Windows 95 x86 emulation/translation. Emulation ideas (including NEON Lite) are longer-term and should not contaminate driver bring-up.

**Safety:** original toolkit Xoom untouched. Replacement diagnostic DUT runs temporary `fastboot boot` images. Device-specific identities/calibration stay outside the public source tree.

**Project ethos:** upstream-first, hardware evidence before conclusions, reversible experiments, immutable test provenance, minimal background tasks, explicit ownership of components and useful documentation for agents resuming without chat context.
