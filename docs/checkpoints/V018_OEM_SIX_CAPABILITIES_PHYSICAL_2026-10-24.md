# v018 — complete Motorola BCM4329 six-capability override

**Date:** 2026-10-24. **Classification:** build, physical tempboot, actual effective capability override **PASS**; native Wi-Fi Function 2 readiness **FAIL** twice. No partition writes.

## Exact controlled variant
- Source overlay: \`scripts/experiments/v018-build-oem-caps.py\`, \`patches/experiments/v018-motorola-six-field-sdio-capabilities.patch\`.
- Pinned external Linux source from [xoom-linux/linux](https://github.com/xoom-linux/linux). Source edited only for build then restored SHA256 \`cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6\`. The build config was restored byte-identically.
- Uses the identical v015 RAM initramfs (SHA256 \`c0b437e2296748f823b8db079a98bc2601b906c81b2bad17eb9166954266e23b\`), v015 USB command interface, v017 read-only brcmfmac diagnostic module, same generic NVRAM, and same private OEM firmware (264140 bytes, SHA256 \`5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834\`) as v017 baseline. Private payloads not published.
- Image: \`MZ600-stingray-diagnostic-v18-OEM-SDIO-CAPS-TEMPBOOT-ONLY.img\` (6,658,048 bytes; SHA256 \`ae93785ef6ede0e3463a992c676a40da699205fb0d32af00814e95dcec485173\`). Desktop and Surface SHA matched; kernel/header/DTB/initramfs verified offline.
- Selected *replacement MZ600* by private identity; fastboot product \`xoom-cdma\`, unlocked. Temporary \`fastboot boot\` succeeded. USB COM9 and v015 userland STATUS worked.
- OEM card initialization override is applied **after** standard MMC capability parsing and CIS/fixups, before \`sdio_enable_hs()\`; requires Stingray machine and Broadcom BCM4329 CIS IDs. All six OEM fields assigned exactly as Motorola specified.

## Measured comparison (read-only v017 probe)

| Measurement | v017 unmodified Linux core | v018 six-field OEM patch |
| --- | --- | --- |
| Raw CCCR structure/version | 0x11 | 0x11 |
| Raw SDIO SPEED | 0x01 | **0x03** (EHS bit enabled) |
| Parsed SDIO version | 1 | **2** |
| Parsed multi, low, wide, highpower, highspeed | 1,0,0,1,0 | **1,0,0,1,1** |
| Host clock | 46,153,846 Hz | 46,153,846 Hz |
| Host timing | 0 (legacy) | **2 (SD HS)** |
| Host width | 2 (4-bit enum) | 2 |
| IOEx before/after | 02/06 | 02/06 |
| IORx before/after | 02/02 | 02/02 |
| ClockCSR | d2 | d2 |
| F2 result | -62 | **-62 (both trials)** |

Two physical v018 WIFI_START attempts with a clean STOP between produced the same six-field state and F2 -62 timeout. After testing, both Broadcom modules were unloaded normally. **No wlan0, RF scanning or association.**

## What this does and does not establish
- It **does** show previous v010/v011/v013 partial interventions were not equivalent to the complete OEM workaround; the full modern Linux equivalent now demonstrably takes effect and changes high-speed timing.
- It **does not** make the BCM4329 report F2 ready. The six-field override **alone** is insufficient under the tested firmware, NVRAM, clock and power conditions.
- Does not rule out additional Motorola sequencing, firmware/calibration, low-frequency reference, regulator, clock/tap or firmware CPU boot differences.
- Next controlled variation: retain **exact v018 six-field override and payloads**, change only SDMMC2 max-frequency from 46,153,846 to 25,000,000 and *measure* actual host clock (v019). No speculative permanent quirk acceptance.

This image is an experiment, not a Wi-Fi release or working native network stack.
