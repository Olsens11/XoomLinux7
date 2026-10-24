# BCM4329 Wi-Fi bring-up and Function 2 blocker

**Status (2026-10-24): no working native wlan0 yet. v015 diagnostic raw-USB/module transport is physically verified; F2 readiness is unresolved.**

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
- v014 physical USB/driver lifecycle PASS, binary upload FAIL. v015 physical raw USB/firmware/.ko uploads and reload PASS; WLAN0 remains ABSENT.

## OEM reference and unresolved questions
Motorola Tegra OEM source points to WLAN reset PU2, host IRQ PU5, power PU4, staged 100/100/200ms sequencing and SDMMC2 tap delay 6. OEM driver forces CCCR SDIO revision due to older chip reporting. Mainline `brcmfmac` F2 `sdio_enable_func` ready timeout may involve power, firmware CPU boot, SDIO clock, IRQ or bus timing; **do not claim root cause yet**.

Investigate chip IOEx/IORx progression and clocks across before/after firmware transfer, compare with reference TWRP/OEM trace, and apply smallest upstream-compatible correction.

## Per-device safety
No embedded real MAC addresses, Wi-Fi SSIDs/passwords or unique calibration. Candidate bootloader identity: `ATAG_STINGRAY_MAC (0x57464d41)`; inspect actual same-device provenance. Do not attempt RF scan/association until this and regulatory source are qualified.

## Current hypothesis review (2026-10-24)
Motorola embedded SDIO supplied SIX capability values. v010 changed only version, v011 high-speed and v013 attempted host \`.init_card\` high-speed; \`sdio_read_cccr\` may overwrite the latter. These do NOT constitute a complete reproduction of Motorola original behavior. v016 measured IOEx \`02→06\`, IORx \`02→02\`, chip-clock CSR \`D2\` and \`-62\`: a chip-side F2-ready failure with successful register transport, not a demonstrated remedy. See [source audit](../research/MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md) and [test matrix](../research/BCM4329_F2_TEST_MATRIX.md).

## v017 measured capability discrepancy (2026-10-24)
Raw CCCR=0x11; CAPS=0x02; POWER=0x01; SPEED=0x01 (all CMD52 reads rc 0). Linux effective \`sdio_vsn=1,multi=1,low=0,wide=0,highpower=1,highspeed=0\` versus Motorola embedded override \`2,1,0,0,1,1\`. Host IOS \`clock=46153846,timing=0 (legacy),bus_width=2 (4-bit),signal_voltage=0,vdd=21\`. F2 IOEx=06 and IORx=02 after timeout; no wlan0. This demonstrates a configuration mismatch, **not** its causal relationship to F2. See [v017 physical checkpoint](../checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md).

## v018 full Motorola override tested, no network
Board/chip-scoped complete six-field OEM override was physically effective: SDIO version 2, high-speed 1, raw SPEED 03, timing=2; unchanged 46.15MHz clock. F2 IORx still 02, err -62 on two trials. The six-field workaround alone is not sufficient. See [v018](../checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md).

## v019 host clock A/B fails to resolve F2
With complete Motorola six-field override active, reducing actual host SDIO clock from 46,153,846 to 25,000,000Hz (single compiled DTB max-frequency property) left IORx at 02 and F2 timeout -62 on two trials. Neither the full capability correction nor lower host clock alone resolves F2 under tested OEM firmware/generic NVRAM. [v019](../checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md).

## v020 dynamic testing environment
MZ600 v020 physically supports MMC2-only card reinit and runtime full OEM six-field capability mode without reboot. Actual Motorola capability fields and host HS mode were verified; the v017 driver still showed IOEx 06 / IORx 02 and -62. Bundled v020 test firmware is 253,748 bytes with generic NVRAM: compare only with matched payloads. This **does not fix native wireless**. [v020 hardware acceptance](../checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md).
