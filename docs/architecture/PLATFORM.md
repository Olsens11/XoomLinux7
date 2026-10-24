# Board platform

MZ604 Wingray (Wi-Fi-only) and MZ600 Stingray (cellular) share Tegra2, BCM4329 Wi-Fi on SDMMC2 and the same GPIO wiring described by the contributor's Wingray DTS. A direct file diff of our derived Stingray board DTS against upstream Wingray DTS showed only header/model/compatible changes. The USB diagnostic DTS adds only USB0 OTG-to-peripheral override.

Core Wi-Fi wiring: power U4, reset U2, host wake U5, SDMMC2 four-bit bus, 32k reference; original DTS uses default tap=6 and assigned SDIO clock 46,153,846 Hz, with comment that 48MHz from downstream was not working in author's tests. The same wiring is not **proof** the author's wlan0 worked; it is evidence of a common hardware baseline.

Separate modem-specific changes must be confined to Stingray profiles. The user's original recovery Xoom is a separate protected device from the Linux test tablet.

Native Linux installation, Debian userspace and Windows 95 emulator integration are deferred; current PID1 is strictly an initramfs hardware-diagnostic process.
