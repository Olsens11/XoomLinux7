# Diagnostic checkpoint ledger — v01 through v014

**Evidence labels:** `BUILT` offline successful build; `BOOTED` device reached Linux; `PHYSICAL` observed test behavior; `FAILED` negative feature test; `UNVERIFIED` no independent hardware proof. This table is a timeline, *not* a single escalating success rating.

| Rev | Key result | Evidence classification |
| --- | --- | --- |
| v01 | Tegra20 zImage/DTB compile, earliest Linux init failure due missing /init | BUILT / BOOT INVESTIGATION |
| v02 | Freestanding ARMv7 PID1 and initramfs built | BUILT |
| v03 | Replacement MZ600 Stingray startup and basic diagnostics | BOOTED |
| v04 | CDC ACM USB serial and `PING`, framebuffer, MMC, DRM/thermal | PHYSICAL |
| v05 | Atmel maXTouch event2: 273 frames / 29 reports, coordinate mapping | PHYSICAL |
| v06 | Grid + crosshair physical touch mapping, temporary UI | PHYSICAL |
| v07 | Native `brcmfmac` driver/firmware integrated; no `wlan0` | BOOTED / WIFI FAILED |
| v08 | 3 SDIO funcs, BCM4329 rev3 F1 signature, F2 `-62` timeout; two FW variants | PHYSICAL / WIFI FAILED |
| v09 | Signed regdb staged, F2 unchanged | PHYSICAL / WIFI FAILED |
| v010 | OEM SDIO CCCR v1→v2 forced; F2 unchanged | PHYSICAL / WIFI FAILED |
| v011 | SDIO high-speed mode tested; F2 unchanged | PHYSICAL / WIFI FAILED |
| v012 | SDIO F2 IOEx/IORx instrumentation built | BUILT; independent physical log NOT FOUND |
| v013 | Tegra `.init_card` high-speed hook; last confirmed `PONG ... V13`; F2 unchanged | PHYSICAL / WIFI FAILED |
| v014 | Modular Broadcom, RAM-only USB live diagnostic/firmware upload, 6,656,000-byte image | BUILT + OFFLINE SHA VERIFIED; **NOT PHYSICAL** |

v014 image SHA256: `65846a0928feed535e81a0898bc186d48d12a96c40f36719d6b56a8a3589f670`. Its image and raw private test captures stay on controlled machines. Public repository records source, manifest and scrubbed summaries.

Versions are not automatically an acceptance order: last proven-on-device v013 remains the physical baseline. For individual variants such as multiple v08 firmware/reset/log tests, see [historical scripts](../../scripts/README.md) and [source map](../reference/SOURCE_MAP.md).
