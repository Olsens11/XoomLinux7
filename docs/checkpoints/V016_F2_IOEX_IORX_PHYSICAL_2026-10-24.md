# v016: read-only F2 register trace — 2026-10-24

**Result:** Diagnostic-module build and RAM transfer PASS; firmware init still FAIL. This is a negative Wi-Fi result, not a repair.

Source: `scripts/experiments/v016-build-f2probe.py`, `patches/experiments/v016-brcmfmac-f2-cccr-readback.patch`.
- Original kernel `brcmfmac/sdio.c` SHA256 before/after: `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab` (byte-identical restoration).
- Initial standalone module-only build failed modpost due missing brcmutil symbols; corrected build includes *both* modules.
- Read-only instrumented `brcmfmac.ko` 460,696 bytes, SHA256 `ff08f3ac3058d35c18d1b4aacb3f712aead17208fcfd425dab34934772279a87`.
- Transferred Desktop → Surface SSH with SHA verification; uploaded via v015 USB RAM-only loader. Device responded `UPLOAD DONE SIZE 460696 CRC32 0x9BCAB7E6`.
- v015 WIFI_START returned BRCMUTIL rc 0 / BRCMFMAC rc 0, debug 3. Driver log:
```
XOOM_F2V016 before ioex=02/0 iorx=02/0 clkcsr=d2/0 clkstate=3
XOOM_F2V016 after  ioex=06/0 iorx=02/0 clkcsr=d2/0 result=-62
```
- Mainline SDIO `sdio_enable_func` wrote enable bit for F2 (IOEx bit 2), but device did **not** assert ready bit in IORx within the driver timeout. F1 stays ready, CMD52 register reads successful. No `wlan0` demonstrated.
- Clock CSR `0xd2`: status ALP+HT available and force/request bits. This is a register state snapshot only. **Do not claim firmware execution, a root cause or fully qualified clock conditions.**
- At test time the v015 private RAM firmware had earlier been replaced with a CRC-verified old OEM candidate; readback confirms firmware/NVRAM transfer but not chip execution. Verify every future experiment's RAM payload exact provenance.

Next: Motorola full embedded six-field card capability audit, then scoped equivalent A/B test if fields differ. See `docs/research/MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md` and `docs/research/BCM4329_F2_TEST_MATRIX.md`.

Protected original Xoom not modified; temporary boot only; no permanent partition writes.
