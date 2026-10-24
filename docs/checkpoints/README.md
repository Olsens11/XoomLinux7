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
| v014 | Physical USB boot and Broadcom load/unload PASS; F2 -62; canonical TTY binary upload FAIL | PHYSICAL PARTIAL PASS |
| v015 | Raw tty + CRC binary upload verified (4 KiB, 264 KiB firmware, 17 KiB and 460 KiB .ko), uploaded module lifecycle and retry PASS; wlan0 absent | PHYSICAL USB/DIAGNOSTIC PASS; WIFI NOT WORKING |

v014 image SHA256: `65846a0928feed535e81a0898bc186d48d12a96c40f36719d6b56a8a3589f670`. Its image and raw private test captures stay on controlled machines. Public repository records source, manifest and scrubbed summaries.

Versions are not automatically an acceptance order: last proven-on-device v013 remains the physical baseline. For individual variants such as multiple v08 firmware/reset/log tests, see [historical scripts](../../scripts/README.md) and [source map](../reference/SOURCE_MAP.md).

## Git infrastructure acceptance
- [2026-10-24 — three-device write-key and Git worktree qualification](GIT_ACCESS_2026-10-24.md). This is **repository infrastructure** acceptance, not native Linux hardware qualification.

See [v014 USB and module evidence](V014_USB_LAB_2026-10-24.md).

See [v015 raw USB transport qualification](V015_RAW_USB_LAB_2026-10-24.md).

## v016 diagnostic
- [v016 physical F2 IOEx/IORx and clock readback](V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md): diagnostic PASS, native Wi-Fi FAIL.

- [v017 read-only CCCR inventory](V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md): original reported version/high-speed mismatch reproduced; F2 timeout unchanged.

- [v018 physical Motorola six-field override](V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md): effective SDIO capability and timing correction PASS; F2 remained -62 twice.

- [v019 25 MHz physical A/B](V019_SDMMC2_25MHZ_AB_2026-10-24.md): only compiled DTB max-frequency differs; actual host clock 25 MHz; F2 -62 twice.

- [v018 supplementary live recheck](V018_RECHECK_2026-10-24.md): full Motorola capabilities remained effective, F2 timeout repeated, actual 25 MHz host clock; investigate discrepancy with earlier 46.15 MHz v018 measurement.

- [v020 physical MMC2 on-demand re-enumeration](V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md): AUTO/MOTOROLA/AUTO PASS, host completion PASS, module-loaded safety refusal PASS, Wi-Fi F2 still FAIL.

- [Second v020 image SHA and physical on-demand test](V020_SECOND_IMAGE_VERIFICATION_2026-10-24.md). This does not supersede the earlier v020 image record.

- [v020 additional distinct build and two on-demand AUTO/MOTOROLA/AUTO cycles](V020_ADDITIONAL_BUILD_AND_REINIT_2026-10-24.md).

- [v021 OEM-era firmware, calibration match, and pending LPO observer](V021_OEM_FW_AND_LPO_HYPOTHESIS_2026-10-24.md): F2 remains -62; no native Wi-Fi.

- [v022 AUTO/legacy 25 MHz, three real MMC2 trials](V022_AUTO_LEGACY_25MHZ_PHYSICAL_2026-10-24.md): timing specification pass; F2 failure persists.

- [v021 32768Hz LPO software-clock observation](V021_LPO_CLOCK_PHYSICAL_2026-10-24.md): physically run, electrical waveform not measured.

- [v025 power-on pre-reset timing control on physical Xoom](V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md): Linux effective 100ms, F2 -62 in three trials.

- [v026 physical runtime firmware/NVRAM provenance](V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md): exact file names, 3 matching CRCs, persistent F2 failure.

- [v027 physical read-only WLAN/BT GPIO survey](V027_BT_WLAN_GPIO_READONLY_PHYSICAL_2026-10-24.md): U4/U2 outputs valid; BT I7/U0/U1/U6 GPIO direction -22 and cannot safely establish their levels.

- [v028 GPIO CNF/OE/OUT/IN physical controller test](V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md): BT-side pins are not GPIO-enabled, WLAN U2/U4 high outputs, F2 still -62.

- [v030 Bluetooth U4 shared-power and passive I7/U0 compile-only checkpoint](V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md) — 21 static checks; runtime hardware still untouched.

- [v031 physical read-only BT serdev binding and shared clock probe](V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) — registered Bluetooth child, DRIVER=NONE, live shared 32768Hz provider, F2 -62.
- [v032 clock-role-correct Bluetooth LPO disabled DTB](V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md) — 12 static checks, no boot change.
