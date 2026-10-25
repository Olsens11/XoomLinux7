# v037 physical — SDPCM mailbox write error visibility (2026-10-24)

**Result:** Instrumentation and RAM-only live test PASS; **existing SDPCM mailbox write returned rc=0**; original SDPCM protocol is **4** in both Motorola 2.6.36 and Linux 7; **Wi-Fi F2 still times out (-62)**. No evidence the firmware consumed the mailbox message, ran correctly, or asserted F2 readiness.

## Why this check mattered

Motorola's original [`dhd_sdio.c` at kernel `2a65edc`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_sdio.c) line ~2759 uses `W_SDREG` to transmit the SDPCM protocol number through SDIO `tosbmailboxdata`. Its macro at ~398–413 tests for an SDIO register failure and retries up to `retry_limit`.

The pinned [Linux 7 `brcmfmac/sdio.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c) ~4264–4268 performs the same write but previously supplied `NULL` for its optional error pointer. The backend [`bcmsdh.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcmsdh.c) ~265–286 returns the host-controller write outcome through that optional pointer. A silent host-side SDIO write error was therefore a falsifiable possibility, not a proven defect.

The original Motorola [`bcmsdpcm.h`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/include/bcmsdpcm.h) defines `SDPCM_PROT_VERSION=4` and `SMB_DATA_VERSION_SHIFT=16`. The Linux v037 runtime reported `sdpcm_protocol=4`, agreeing with OEM.

## Builder and test provenance

- [`scripts/experiments/v037-build-sdpcm-mailbox-status.py`](../../scripts/experiments/v037-build-sdpcm-mailbox-status.py) builds the existing source-hash-guarded v036 observer with **one extra instrumentation delta**: it leaves the original mailbox register-write data/address/order unchanged, but passes a local error-output pointer rather than `NULL` and records the result and protocol version once.
- Compiled module `brcmfmac-v037-pmu-cm3-readonly.ko`: **462212 bytes**, SHA256 **`2d24bf221f04ada352ccc52efd1041717f25852e730dd54d6285862a02b35bf5`**. Binary ABI `7.0.0-next-20260422 SMP mod_unload modversions ARMv7 p2v8`. The builder restored the original `sdio.c` and `chip.c` pinned SHA256 values byte-for-byte.
- The binary was transferred to Surface Book 2 and independently verified exact size and SHA256. USB RAM upload to the already-running **temporary v034** replacement MZ600 was acknowledged `UPLOAD DONE SIZE 462212 CRC32 0xAE5D0A69`; no firmware/NVRAM change, no persistent write, power-cycle or new kernel boot.
- v037 USB WIFI_START: `BRCMUTIL rc 0`, `BRCMFMAC rc 0`. Its sanitized runtime log recorded:

```text
XOOM_V037_MAILBOX t_ns=7211718704000 write_rc=0 sdpcm_protocol=4
XOOM_V037_RES ... T4_PRE_F2_REQUEST ... ccrev=29 pmurev=6 stat=000000be/0 res=003fe63e/0 pend=00000000/0 pu=00000000/0 pd=00000000/0
brcmf_sdio_firmware_callback enable F2: err=-62
```

The timestamped mailbox write completed before the F2 enable request, without host-side SDIO error. The original v036 PMU resource and ALP/HT behavior repeated. The sanitized local file is `C:\Users\olsen\xoom-linux-rom\downloads\v037-trial1-sanitized.log`, not published with any proprietary firmware.

## What this rules out and what it does not

- **Ruled out in the measured attempt:** a *reported host-side SDIO transaction failure* from the `tosbmailboxdata` write, a mismatch in the declared SDPCM protocol version `4`, and absent HT/regulator resource status at the F2 boundary.
- **Not ruled out:** an incorrect mailbox register window or internal semantics, firmware failure to read the mailbox, faulty firmware/NVRAM content or placement, CPU code not executing, device reset/power history, or a firmware bug. `write_rc=0` proves only successful completion at the Linux SDIO request level, not internal firmware acknowledgment.
- OEM retry macro versus modern driver remains a *difference*, but this particular measured write required no retry. Do not modify production error handling or add duplicate mailbox writes merely to make F2 ready.

## Device end state and safety

After test `WIFI_STOP brcmfmac_rc 0 brcmutil_rc 0`. Final `MMC2_STATUS`: USB COM9 responsive, target verified, MMC2 bound, BCM4329 detected, `AUTO` profile 0, Wi-Fi drivers unloaded. No partition flash or reboot, OEM firmware publishing, Wi-Fi RF scan/association, or GPIO/PMU write beyond the unchanged normal Linux driver sequence.

## Next discriminating steps

1. **Prioritize firmware execution / RAM handshake:** compare actual OEM and Linux firmware RAM layout, NVRAM token placement and SOCRAM tail, CM3 wrapper reset status, mailbox register target core. Find one non-destructive alive/progress indicator not gated behind F2.
2. Consider a controlled **RAM-only, one-variable firmware image** comparison to January 2011 Motorola's `fw_bcm4329.bin`, with per-device identity and calibration protected, and without radio association. Version matched to original OEM module is not the same as proven compatible with mainline `brcmfmac`.
3. A true BCM4329 cold POR experiment requires verified shared U4/WL_REG_ON/BT_REG_ON ownership and fixed recovery; do not infer it from repeated module starts.
4. Preserve diagnostics and log uncertainty; never promote v037 as Wi-Fi working. The last accepted kernel temporary-boot baseline remains v034 and the v025 rollback image is untouched.

**Acceptance labels:** v037 source build PASS; hash/USB CRC PASS; live mailbox status PASS; F2 FAIL (-62); cleanup/MMC2 PASS.
