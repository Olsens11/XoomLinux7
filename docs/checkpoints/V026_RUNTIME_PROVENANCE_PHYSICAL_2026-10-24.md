# v026 actual firmware/NVRAM runtime provenance — replacement MZ600 — 2026-10-24

**RESULT:** Physical RAM-only tracer **PASS** for runtime firmware path selection, returned firmware/NVRAM content CRC32, Linux NVRAM packed-buffer CRC32 and platform-MAC callback presence. **Wi-Fi remains FAILED** at Function 2 ready (`IORx=0x02`, `-62`); no `wlan0`. **No Xoom reboot or flash for this experiment.** The first builder was a draft that did not compile until corrected using exact Linux 7 source anchors. One tracing bug initially mislabeled an initial asynchronous request as a retry; corrected in the *qualified final* module.

## Exact tested module

- Final ARM Linux 7 RAM module: `brcmfmac-v026-provenance-readonly.ko`
- **467,412 bytes**, SHA256 **`5b4b28b9aa7d8a1708a190dfd85fee5274f7c6eba82c1bc3bb5bbe9d50d7c690`**.
- USB upload: `UPLOAD DONE SIZE 467412 CRC32 0x9AD8EA57`, matching Surface host transfer CRC.
- Source/build: `scripts/experiments/v026-build-runtime-provenance.py` plus `patches/experiments/v024-gpio-regulator-readonly.patch`. Rebuilds only brcmfmac and brcmutil modules, modifying local Linux source temporarily; both original sources were restored and independently hashed after compilation.
- Original `sdio.c` SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab`; original `firmware.c` SHA256 `f2b6fe570981bf69a81fd5965712f18840df9b97dabcdbd4aa4cf260b4e9760b`.
- Physical environment: replacement Motorola MZ600, existing temporary v025 kernel; Linux 7 MMC2 AUTO, 25 MHz legacy mode, MMC host pre-reset delay=100 ms, MMC pwrseq after-reset delay=300 ms.
- Logger emits `XOOM_PROV026` kernel messages with `ktime_get_ns()`. File metadata and CRC32 are visible; **no MAC, calibration bytes, passwords or other private chip data are printed**. CRC32 is a noncryptographic fingerprint.

## Verified actual file-selection sequence

1. Broadcom F1 signature identified BCM4329. First asynchronous request was **`brcm/brcmfmac4329-sdio.motorola,stingray.bin`**; its completion did not provide firmware, so the driver requested **`brcm/brcmfmac4329-sdio.bin`**.
2. Canonical generic binary returned **253,748 bytes**, CRC32 **`B4092AA6`**, matching the exact known file in the virtual lab.
3. The driver attempted the board-specific `brcm/brcmfmac4329-sdio.motorola,stingray.txt`, then successfully returned generic **`brcm/brcmfmac4329-sdio.txt`**, **1,550 bytes**, CRC32 **`FAFCC93A`**.
4. The file was interpreted as NVRAM text. The platform MAC callback was **unavailable** (`platform_mac_available=0`). The kernel's actual NVRAM packer emitted **672 bytes**, CRC32 **`596925B1`**.
5. The optional board-specific `.motorola,stingray.clm_blob` and generic `.clm_blob` were attempted but **not found**; this was optional and does not imply a fatal lookup error.
6. Cortex-M3 release path and memory download/readback completed, but `sdio_enable_func(F2)` still returned **-62** after roughly **3.002 seconds**, with `IOEx:02→06` and `IORx:02→02`.

**Virtual-lab comparison (exact CRC32 from actual offline reference objects):**

| Buffer | Physical CRC32 | Virtual reference CRC32 | Result |
| --- | --- | --- | --- |
| Generic `.bin`, 253748 bytes | `B4092AA6` | `B4092AA6` | MATCH |
| Generic source `.txt`, 1550 bytes | `FAFCC93A` | `FAFCC93A` | MATCH |
| NVRAM packed data, 672 bytes | `596925B1` | `596925B1` | MATCH |

The independent v1 Python and ARM/QEMU packers also generated *byte-identical* NVRAM buffers, SHA256 `401b0b9a7b898519aa3c7403b53eff050ef1e8917fd90483145f59d675ad46ab`. The v026 kernel's CRC32 now confirms the same buffer fingerprint at actual runtime. CRC agreement provides strong evidence under a controlled non-adversarial test, but is not cryptographic byte-for-byte proof.

## Other measured runtime values

- Tegra MMC pwrseq clock rate `32768`, software enabled `1` (not proof of waveform delivered to chip).
- Tegra GPIO U2 reset controller: direction output, raw=1, active-low=1 (logical=0); U4 power output raw=1, active-low=0; U5 host-wake direction query yielded `-22` (pinmux/IRQ use unresolved).
- Reported MMC2 regulator states: `vmmc` enabled, nominal 3.3 V; `vqmmc` enabled, nominal 1.8 V (not physical measurements).
- MMC2 `ios.clock=25000000`, `ios.timing=0` (legacy); `power_delay_ms=100`.
- Shared F2 failure was unchanged. Even though firmware/NVRAM delivery passed memory readback, this **does not establish that embedded Cortex-M3 firmware actually executed**.

## Interpretation

**Ruled down:** wrong generic filename, firmware/NVRAM source bytes being inadvertently swapped, malformed NVRAM text-to-binary conversion, board-specific file accidentally winning over generic files under the current kernel, and the incorrect initial `REQUEST_ASYNC_RETRY` logging assertion (that was a bug in the initial v026 tracer, now corrected).

**Still unverified:** true MAC provenance. The old Motorola OEM calibration reference included `macaddr`, while this generic NVRAM intentionally lacks it and Linux's platform callback is unavailable. An OTP/NVRAM/firmware fallback cannot be ruled out; **do not borrow or hardcode the MAC from another Xoom**. Missing platform MAC is **not** established to cause F2 failure.

**Next higher-value cause audit:** instrument whether MMC2 detach/rebind actually deasserts WLAN power on Tegra U4 and resets U2, and whether Linux 7 leaves `regulator-boot-on` power asserted across all retries. Also inspect core reset, PMU startup resources, SDPCM mailbox and CPU activity before and after Cortex-M3 reset release. A replaceable brcmfmac module loads **after** initial MMC2 controller initialization; it cannot retrospectively observe U4/U2 sequencing. Achieving that timeline likely requires kernel-core tracing or a carefully scoped new temporary-boot image, not a claim of pure module observation.

## Final real-device condition and safety

After verification, executed `WIFI_STOP`: brcmfmac rc=0, brcmutil rc=0. `MMC2_STATUS` verified target VALID, driver BOUND, BCM4329 detected, profile `AUTO=0`, modules UNLOADED, USB responsive. No Android or TWRP partition altered; physical tablet unopened. V025 remains a temporary RAM boot.

## Reproducibility

- Final builder checks exact source hashes and the v024 patch, applies instrumented source into the private Linux 7 tree for the compile, and restores the source bytes in `finally`. Run source review and preflight before reproducing.
- Source and tests live on the `lab/runtime-provenance-v026` branch. Compiled binaries, private OEM material, MAC identifiers and raw calibration sources **must not** be published.
- An initial unsuccessful draft and first physical module (467408 bytes, SHA256 `89143f4a...`) are **not** the qualified reference; use final SHA256 `5b4b28b9...` above.
