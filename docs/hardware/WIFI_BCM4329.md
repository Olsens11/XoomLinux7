# BCM4329 Wi-Fi bring-up and Function 2 blocker

**Status (2026-10-24): no working native wlan0 yet; v014 is an untested-on-device diagnostic tool.**

## Shared upstream baseline
The original Wingray DTS in [xoom-linux/linux](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dts) already defines BCM4329, `mmc@c8000200`, SDIO clocks, Wi-Fi supplies/reset/interrupt. Our Stingray derivative preserves it. Whether the upstream author achieved network association is **not documented/proven**.

## Actual hardware findings
- `mmc2:0001` SDIO device, three functions; `BCM4329 rev3`, F1 signature `0x9934329`.
- Mainline `brcmfmac`, `brcmutil`, `cfg80211` and firmware request/download path run.
- `brcmf_sdio_firmware_callback enable F2: err=-62` after ~3 seconds. Kernel never creates `wlan0`.
- Both standard `brcmfmac4329-sdio.bin` (253,748 bytes; SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`) and historical OEM `fw_bcmdhd.bin` (264,140 bytes; SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`) were tested and hit the same F2 issue. Binaries are **not** committed here.
- v09 signed `regulatory.db` path succeeded at integration; F2 problem remained.
- v010 forced SDIO CCCR revision for exact board/chip; observed OEM-style revision 1→2 log, F2 timeout remained.
- v011 high-speed host change observed; F2 timeout remained.
- v012 F2 IOEx/IORx instrumentation built; no separate conclusive physical log on record.
- v013 narrowly scoped Tegra host `.init_card` callback ran and high-speed enumeration passed, but F2 timeout remained. Last on-device serial observation `PONG XOOM-LINUX V13`.
- v014 built a RAM-only hot-reload lab for USB commands `WIFI_START`, `WIFI_STOP`, `WIFI_RETRY`, `WIFI_STATUS`, `WIFI_DEBUG`, `UPLOAD`. **Not yet hardware verified**.

## OEM reference and unresolved questions
Motorola Tegra OEM source points to WLAN reset PU2, host IRQ PU5, power PU4, staged 100/100/200ms sequencing and SDMMC2 tap delay 6. OEM driver forces CCCR SDIO revision due to older chip reporting. Mainline `brcmfmac` F2 `sdio_enable_func` ready timeout may involve power, firmware CPU boot, SDIO clock, IRQ or bus timing; **do not claim root cause yet**.

Investigate chip IOEx/IORx progression and clocks across before/after firmware transfer, compare with reference TWRP/OEM trace, and apply smallest upstream-compatible correction.

## Per-device safety
No embedded real MAC addresses, Wi-Fi SSIDs/passwords or unique calibration. Candidate bootloader identity: `ATAG_STINGRAY_MAC (0x57464d41)`; inspect actual same-device provenance. Do not attempt RF scan/association until this and regulatory source are qualified.
