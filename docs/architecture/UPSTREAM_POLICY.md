# Upstream-first architecture / ownership

**Provenance:** [xoom-linux/linux](https://github.com/xoom-linux/linux), revision `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. The June 2026 upstream Wingray DTS is the point of departure. Original GPL/SPDX notices must remain attached to copies or patches. Do not rewrite contributor history.

1. **Kernel authority:** upstream Git checkout at pinned commit; maintained externally in `upstream/linux` (ignored), not copied into this small integration repository.
2. **Platform:** Tegra20 and existing Linux `sdhci-tegra`, MMC core, Broadcom `brcmfmac`/cfg80211, Atmel maXTouch input/evdev, DRM/KMS/fb, ALSA/ASoC, regulator/clock/GPIO/pwrseq, `power_supply` and USB gadget.
3. **Board description:** derived Stingray DTS preserves the Wingray Wi-Fi/panel base and changes board identity only; USB diagnostic derivative selects USB0 peripheral. Future true hardware differences must be proven, documented and minimized.
4. **Vendor references:** Motorola board source and tested TWRP recovery Wi-Fi provide *observational* reference, not an excuse for indiscriminate downstream driver copy-paste. Respect redistribution restrictions.
5. **Interventions:** separate generic mainline bugs, Tegra controller quirks, chip/firmware quirks, exact board wiring and user-space policy. Prefer upstreamable scoped patches, with test evidence and negative-test notes.
6. **Identity:** MAC comes from target hardware (e.g. Motorola bootloader ATAG `ATAG_STINGRAY_MAC=0x57464d41`) or verified same-device records, not a copied calibration value. Regulatory domain must be correct for actual hardware/location.
7. **Experiments:** v010–v013 MMC/SDIO changes were probes, not accepted permanent architecture. v014 module lab is diagnostic tooling, not a production runtime.

See original decision text under [historical architecture](../history/README.md) and [hardware Wi-Fi](../hardware/WIFI_BCM4329.md).
