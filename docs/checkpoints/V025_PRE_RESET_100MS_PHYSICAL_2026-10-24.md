# v025 physical test — MMC2 pre-reset power delay 100 ms (2026-10-24)

**Result:** The replacement Motorola Xoom MZ600 successfully executed the intended new Linux 7 MMC host delay, but **BCM4329 SDIO Function 2 still timed out (-62) on all three trials**. Linux Wi-Fi remains nonfunctional. This is a controlled negative result, not proof that board sequencing is fully correct.

## Why this experiment

An audit of the actual Linux 7 code showed that the earlier 300 ms `post-power-on-delay-ms` lived in the `wifi-pwrseq` node and executes **after reset release**. The MMC core independently reads that same property name from the **`/mmc@c8000200` host node** to delay between `MMC_POWER_UP` and the power sequencer's `post_power_on` reset release. That host property was absent; the physically measured default `host->ios.power_delay_ms=10`. Motorola's downstream initialization explicitly uses about 100 ms between enabling its Wi-Fi power line and releasing its reset line, followed by another 200 ms. The 300 ms post-reset delay is therefore not equivalent to the OEM powered-while-reset-held interval.

**Important caveat:** The current device tree declares `regulator-boot-on` for the U4 Wi-Fi power regulator. Consequently, changing the host delay does not by itself prove any particular *actual GPIO-to-GPIO timing* or an actual power cycle. We must not infer electrical rail timing from the Linux delay field.

## Exact v025 candidate

- Temporarily booted file: `MZ600-stingray-diagnostic-v025-HOST-PRE-RESET-100MS-TEMPBOOT-ONLY.img`.
- Bytes: **6,662,144**.
- SHA256: **`142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb`**. Host transfer independently SHA256-verified on Surface.
- Parent: verified v022 AUTO/default-mode 25 MHz image SHA256 `2be2f5094149f242a5a9e5d290f7505d9b312ae4bfba8dbc74e1f7362995c6b3`.
- Image builder: `scripts/experiments/v025-build-pre-reset100.py`. It verifies parent SHA/header/kernel/ramdisk, applies the single device-tree property by `fdtput`, semantically compares the decomposed DTBs, recalculates Android boot header kernel size and SHA-1, and checks that kernel bytes outside DTB and the ramdisk are untouched.
- Decoded device-tree **only semantic change**: add `/mmc@c8000200/post-power-on-delay-ms = <100>`. DTB 61,092 → 61,108 bytes.
- Unchanged: `/wifi-pwrseq/post-power-on-delay-ms=300`; MMC2 `max-frequency=25,000,000`; firmware 253,748 bytes; normalized OEM-matched NVRAM 672 bytes; v020 RAM diagnostic userspace and installed Linux kernel code. The image remains RAM-only; no partition flashing.
- RAM filesystem SHA256: `060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67`.
- Replacement MZ600 was positively identified in Android ADB and fastboot (`product=xoom-cdma`, unlocked); used **`fastboot boot`**, no `fastboot flash`.

## Actual hardware procedure and measurements

Booted v025 once, reloaded known read-only v024 diagnostic `brcmfmac.ko` in RAM (464,904 bytes, SHA256 `9fe98a71af06f8864c9ba5420f1251e04107725c450583e8a9206893530dfc87`; host and USB CRC32 `3F68C4FC` verified), performed first test after boot, then **two additional tests each after MMC2-only unbind/rebind**. Each rebind returned `MMC2 REINIT PASS BCM4329 REENUMERATED`.

| Measurement | Trial 1 (boot enumeration) | Trial 2 (rebind) | Trial 3 (rebind) |
| --- | --- | --- | --- |
| Effective MMC host pre-reset delay | **100 ms** | **100 ms** | **100 ms** |
| SDIO profile | AUTO | AUTO | AUTO |
| Host clock / timing | 25,000,000 Hz / legacy 0 | 25,000,000 Hz / legacy 0 | 25,000,000 Hz / legacy 0 |
| Firmware RAM image | 253,748 bytes | 253,748 bytes | 253,748 bytes |
| NVRAM converted data | 672 bytes | 672 bytes | 672 bytes |
| Firmware transfer/readback | PASS | PASS | PASS |
| IOEx before → after | `02→06` | `02→06` | `02→06` |
| IORx before → after | `02→02` | `02→02` | `02→02` |
| F2 enable result | **-62** | **-62** | **-62** |
| `wlan0` | ABSENT | ABSENT | ABSENT |

From live read-only observer:

```text
XOOM_V024 MMC_HOST power_delay_ms=100
XOOM_LPOV021 pwrseq rate=32768 enabled=1
XOOM_V024 GPIO U2_WIFI_RESET pin=162 direction=0 raw=1 logical=0 active_low=1
XOOM_V024 GPIO U4_WIFI_POWER pin=164 direction=0 raw=1 logical=1 active_low=0
XOOM_V024 REG vmmc enabled=1 reported_uV=3300000
XOOM_V024 REG vqmmc enabled=1 reported_uV=1800000
XOOM_F2V021 HOST clock=25000000 timing=0 buswidth=2 signalvoltage=0 vdd=21
XOOM_F2V021 before ioex=02/0 iorx=02/0 clkcsr=d2/0 clkstate=3
XOOM_F2V021 after ioex=06/0 iorx=02/0 clkcsr=d2/0 result=-62
```

Software-reported GPIO output levels and nominal regulator voltages are **not physical rail measurements**. The 32.768 kHz rate and enabled flag are Linux's clock framework values; they do not prove the signal reaches the chip.

## Interpretation

- Proven: the v022 host default of 10 ms was a distinct pre-reset delay from the 300 ms on the pwrseq node; setting the host's delay to 100 ms took effect in Linux 7; Function 2 still failed under three trials.
- Not proven: that U4 actually rises for each MMC2 rebind, that U2 reset is held low for precisely 100 ms after physical 3.3 V/1.25 V stabilization, or that the WLAN Cortex-M3 starts its firmware. `regulator-boot-on` and separate GPIO/regulator ownership are priority audit targets.
- Additional inherited mistake: read-only USB `SDIO` command queried `/sys/bus/platform/drivers/mmc-pwrseq-simple` instead of driver name `pwrseq_simple`; the earlier UNAVAILABLE was a diagnostic path error, **not proof of absent pwrseq**. Kernel boot log explicitly shows `allocated mmc-pwrseq`.
- The current `brcmf_chip_cm3_set_active` checks SOCRAM core state then releases Cortex-M3 reset; it does not independently verify firmware execution or SDPCM readiness. This remains an untested handoff.

## Final live state

After third test, `WIFI_STOP` unloaded `brcmfmac` and `brcmutil` successfully. Final `MMC2_STATUS`: target valid; driver bound; BCM4329 verified; runtime profile AUTO=0; USB responsive. `WIFI_STATUS`: WLAN0 absent, no scan/association/DHCP. No tablet partition changed. The v025 image remains temporarily running in RAM.

## Next evidence-driven investigation

Audit the entire Tegra/BCM4329 initialization chain from reset GPIO and regulator boot-on state to MMC host power-up, pwrseq `pre_power_on/post_power_on`, SDIO CCCR/card initialization, brcmfmac firmware/NVRAM loading and Cortex-M3 core release, with a timeline of observed events and source lines. Distinguish the original Motorola code from inherited downstream fixes and new mainline behavior. Use read-only kernel telemetry to verify actual transitions and reference counts, not just final steady state. Before another change, evaluate whether `regulator-boot-on` masks power toggling across MMC2 rebinds, and whether the bootloader owns/initializes the Wi-Fi power/reset lines before Linux takes over. The hardware remains unopened.

## Supplemental confirmation after interrupted continuation

The v025 USB console was verified still responsive, and its full `BOOTLOG` independently confirmed host `power_delay_ms=100` and `F2=-62`. A further `MMC2_REINIT` returned `PASS BCM4329 REENUMERATED`; the subsequent RAM-driver test again measured `power_delay_ms=100`, `ios.clock=25000000`, `ios.timing=0`, `IOEx=02→06`, `IORx=02→02`, `F2=-62`. Finally `WIFI_STOP` returned both module unload codes 0, and `MMC2_STATUS` reported target VALID, BOUND YES, BCM4329 verified, AUTO profile 0, and modules unloaded. This extra observation agrees with the three earlier trials. It does not demonstrate a physical WLAN power cycle or fix.

