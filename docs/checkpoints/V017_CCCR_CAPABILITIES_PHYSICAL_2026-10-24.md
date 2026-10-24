# v017: actual BCM4329 CCCR and MMC host capability inventory — 2026-10-24

**Classification:** physically executed on replacement MZ600; read-only register and parsed-state inspection succeeded, native Wi-Fi still FAIL. v015 temporarily booted diagnostic environment; no partitions flashed.

## Build and provenance
- Source script: `scripts/experiments/v017-build-capability-inventory.py`.
- Kernel patch: `patches/experiments/v017-brcmfmac-f2-cccr-readback.patch`.
- Original Linux `brcmfmac/sdio.c` SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab`, restored byte-identically after build.
- Generated ARM32 `brcmfmac.ko` bytes 461628, SHA256 `ed4f947944045c4c0f6a8f74703e231537107c0c336c8975e94f1319de276003`.
- Surface transfer SHA256 verified; v015 RAM upload response `UPLOAD DONE SIZE 461628 CRC32 0xD91898E2`.
- `WIFI_START` returned `BRCMUTIL rc 0`, `BRCMFMAC rc 0 debug 3`; probe logs below.

## Raw card and parsed capability values

```text
XOOM_F2V017 RAW cccr=11/0 caps=02/0 power=01/0 speed=01/0
XOOM_F2V017 CARD sdio_vsn=1 multi=1 low=0 wide=0 highpower=1 highspeed=0
XOOM_F2V017 HOST clock=46153846 timing=0 buswidth=2 signalvoltage=0 vdd=21
XOOM_F2V017 before ioex=02/0 iorx=02/0 clkcsr=d2/0 clkstate=3
XOOM_F2V017 after  ioex=06/0 iorx=02/0 clkcsr=d2/0 result=-62
```

All direct CCCR reads returned error 0. Raw CCCR `0x11` carries version nibbles 1/1; SDIO SPEED raw `0x01` sets advertised high-speed support bit, but the legacy CCCR version inhibits modern Linux's capability parsing and leaves `highspeed=0`. Compare with Motorola original embedded SDIO override: `sdio_vsn=2,multi=1,low=0,wide=0,highpower=1,highspeed=1`.

Host `timing=0` = legacy timing; `buswidth=2` = 4-bit mode in Linux MMC enum. Host actual clock `46153846 Hz` is configured and observed, despite legacy timing. This discrepancy warrants a proper timing control. `signalvoltage=0` and `vdd=21` represent *software-reported MMC ios values*, NOT externally measured rail voltages; do not infer actual physical regulator voltage without checking power supply and OEM design.

## Interpretation with measured limits
- Modern Linux did not end up with Motorola's desired version/high-speed capabilities; v010-v013 did not demonstrate a complete working equivalent.
- Function 2 IOEx bit was set but never ready; we have NOT established that incorrect timing alone prevents firmware CPU startup.
- Firmware source and device calibration are separate variables. This run was in v015 RAM environment with previously uploaded private OEM firmware and a generic board NVRAM, not proven to match the exact reference device.
- The correct next counterfactual is to set OEM six fields **after** standard capability parsing and matching CIS board/chip ID, before `sdio_enable_hs()`, and verify effective capability values, `SDIO_CCCR_SPEED` high-speed-enable result, host timing, IOEx/IORx and wlan0. A control with no override and otherwise identical inputs is required.
- A second clock-only control at a conservative legacy rate may help isolate overspeed from capability interpretation. Do not combine unrelated changes in one result.

No claims of Wi-Fi connectivity. No hard-coded MAC or regulatory identity. Preserved temporary boot safety.
