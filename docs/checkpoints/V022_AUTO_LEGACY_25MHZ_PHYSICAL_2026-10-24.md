# v022 physical control: AUTO + SDIO legacy at 25 MHz — 2026-10-24

**Classification:** physical test performed on the replacement Motorola MZ600, temporary RAM boot only. **SDIO clock timing condition PASS; Wi-Fi Function 2 FAIL (-62) on three trials.** No firmware association, RF scan, Android or recovery partition changes.

## Why this test matters

Broadcom/Cypress BCM4329 Preliminary Datasheet (4329-DS105-R, Section 11, p51 Table 3) permits a maximum **25 MHz** SDIO data clock in **default/legacy mode**. Earlier Xoom AUTO tests measured `46,153,846 Hz / timing=0`, violating that limit. The separately documented v019 test lowered the clock to 25 MHz but ran Motorola high-speed capability override with `timing=2`, **not** legacy timing. v022 specifically isolates the missing 25-MHz legacy control. Source discussion: `docs/research/BCM4329_DATASHEET_SECTION11_REVIEW_2026-10-24.md`.

## Artifact identity and reproducibility

- Image: `MZ600-stingray-diagnostic-v22-AUTO-LEGACY25-TEMPBOOT-ONLY.img`, **6,662,144 bytes**.
- SHA256: **`2be2f5094149f242a5a9e5d290f7505d9b312ae4bfba8dbc74e1f7362995c6b3`**.
- Parent: physically verified v020 image SHA256 `96f01d72782cd3ab6574b806a0d84b1874ec0f98bbe865c74365623ba7148067`, same size.
- Code: `scripts/experiments/v022-build-legacy25.py`. It verifies exact baseline hash, image header, kernel+ramfs bytes, and old/new compiled DTBs; changes only `/mmc@c8000200/max-frequency` `46153846→25000000`. The compiled DTBs have an exact 4-byte difference at offset 46948. The Android boot header digest is recalculated.
- **Exactly 24 image bytes differ:** four bytes of the SDMMC2 limit in the appended DTB and 20 bytes of boot header SHA1. Kernel+v020 USB controls, diagnostic modules, firmware image, NVRAM, all other device-tree data remain byte-identical. No kernel recompile, no source/config mutation.
- Kernel zImage SHA256 `71184366d1988e220e147969ddfae97a7bc4c0902f17822d8dcc88194e31bf1b`.
- Initramfs SHA256 `060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67`.
- Build manifest and boot image are private on Desktop and Surface, not committed to public Git. Surface SHA verified independently before boot.
- Replacement MZ600 identified via private authorized Android ADB and fastboot: product `xoom-cdma`, unlocked; **`fastboot boot` ONLY**. No `flash` command.

## Actual physical measurements (three trials, no repeated OS reboot)

Boot: v020 USB COM9 responded `PONG XOOM-LINUX V20`, `MMC2_STATUS` identified `c8000200.mmc`, BCM4329 SDIO, profile `0` AUTO, modules unloaded. Instrumented v017 Broadcom module was present in unmodified initramfs.

The first trial followed a fresh `MMC2_REINIT`; next two trials each called `WIFI_STOP`, `MMC2_REINIT`, `WIFI_START` and captured `LOGS`, then `WIFI_STOP`. Each controller rebind returned `MMC2 REINIT PASS BCM4329 REENUMERATED`.

| Variable | Trial 1 | Trial 2 | Trial 3 |
| --- | --- | --- | --- |
| Effective SDIO card version | 1 | 1 | 1 |
| High-speed capability / host timing | 0 / **0 legacy** | 0 / **0 legacy** | 0 / **0 legacy** |
| **Actual host clock** | **25,000,000 Hz** | **25,000,000 Hz** | **25,000,000 Hz** |
| SDIO bus width enum | 2 (4-bit) | 2 | 2 |
| Firmware bytes | 253,748 | 253,748 | 253,748 |
| NVRAM bytes | 672 | 672 | 672 |
| RAM download/readback | PASS | PASS | PASS |
| Chip clock CSR before/after | d2 / d2 | d2 / d2 | d2 / d2 |
| IOEx before→after | 02→06 | 02→06 | 02→06 |
| IORx before→after | 02→02 | 02→02 | 02→02 |
| Function 2 return | **-62** | **-62** | **-62** |
| wlan0 | absent | absent | absent |

Excerpt from third trial:
```text
XOOM_F2V017 CARD sdio_vsn=1 multi=1 low=0 wide=0 highpower=1 highspeed=0
XOOM_F2V017 HOST clock=25000000 timing=0 buswidth=2 signalvoltage=0 vdd=21
XOOM_F2V017 before ioex=02/0 iorx=02/0 clkcsr=d2/0 clkstate=3
XOOM_F2V017 after ioex=06/0 iorx=02/0 clkcsr=d2/0 result=-62
```

## Interpretation and remaining uncertainty

- **This specific datasheet requirement is now met and confirmed on real hardware, but F2 never becomes ready.** It rules out default-mode SDIO overspeed as a *sufficient* explanation in this experiment; does NOT demonstrate the prior overspeed was harmless or rule out electrical integrity interaction.
- Firmware memory transfer/readback does **not** demonstrate successful Cortex-M3 execution, reset release, boot mailbox readiness or adequate 32.768 kHz LPO clock.
- Primary next step: authorized read-only v021 LPO/PMC provider telemetry, then scoped Tegra U4 Wi-Fi power / U2 reset and actual VDDC supply-settling measurements per manufacturer minimum 110ms. The Linux 300ms pwrseq delay has not been correlated with physical VDDC ramp.
- Do not transfer Section 11 SPI-only F0 wake-up register sequence into SDIO.
- Existing v020 USB and `MMC2_REINIT` continue working. Final verified live status: target valid, `MMC2` bound, BCM4329 present, AUTO profile 0, Broadcom modules unloaded, `wlan0` absent, USB responsive.
- **No native Wi-Fi fix or long-term stability claim.** True cold-boot validation remains separate from warm card re-enumeration.
