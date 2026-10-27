# MZ600 V15: May 2012 BCM4329 ESCAN V1 2.4GHz receives terminal Event69 SUCCESS, 179ms — physical PASS

**Date 2026-10-26. Evidence: actual owner-executed Surface COM9 private transcript and JSON receipt.** This checkpoint supersedes [V15 offline/staged checkpoint](MZ600_V15_2012_2G_2412_PASSIVE_ESCAN_SURFACE_ONESHOT_STAGED_2026-10-26.md) and is the current XoomLinux7 2012 firmware scan-completion milestone. **DO NOT rerun the consumed V15 one-shot.**

## What this proves

With the **same** later OEM BCM4329 firmware `4.218.248.44` (May25 2012, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`), same factory-per-device MAC and original-installed NVRAM, and same Debian Linux7 kernel `7.0.0-next-20260422+`:
- A one-channel **2412MHz (2.4GHz channel1), passive-only, no SSID, NO_IR, no association** `iw dev wlan0 scan freq 2412 passive` was accepted by the **normal Linux7 ESCAN V1 firmware request**: `MZ600_V15_ESCAN_SET_RC=0 v2=0`.
- The firmware delivered **TWO real `BRCMF_E_ESCAN_RESULT` Event69 status8 PARTIAL** records. First packet datalen380, BSS109 record length368; second datalen420, BSS109 record length408. Both traversed SDIO and reached `brcmf_cfg80211_escan_handler`.
- It then delivered an actual **terminal Event69 status0 SUCCESS** (datalen12). This was NOT a timeout, synthetic completion, or inference from BSS record count.
- Native modern `brcmfmac` parsed/published **two 109-format BSS**, `cfg80211_scan_done` reported **`aborted=0 fw_abort=0 owned=1`**, and `iw` returned `RC=0` with **two displayed network records**. **179 milliseconds** elapsed in the owner script.
- Separate event status summary: `success=1 partial=2 other=0`. **No ESCAN watchdog fired**. Normal Linux7 / firmware terminal completion path physically demonstrated.
- The same firmware on V14 **5GHz ch36 5180MHz passive** previously accepted ESCAN V1 and delivered one Event69 status8 PARTIAL with BSS109, but *no Event69 terminal success* by 10s watchdog. Thus V15 **rules out a global failure of 2012 firmware Event69 terminal emission or Linux7 terminal event recognition.** The gap is specific to 5GHz and/or its scan request/environment/firmware parameters under the tested scenarios, not generally broken completion.

## Actual sanitized fresh owner transcript (no MAC or SSID)

```text
MZ600_V15_PREFLIGHT_START
MZ600_V15_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED
MZ600_V15_TEMP_2012_FIRMWARE_OVERLAY_PASS
MZ600_V15_WCC_LOAD_RC=0
MZ600_V15_WLAN0_PRESENT
MZ600_V15_PHY_2G=14 PHY_5G_TOTAL=29 PHY_5G_NO_IR=24 PHY_5G_DISABLED=5
[60547.939068] brcmfmac: brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: May 25 2012 17:56:21 version 4.218.248.44
MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=35 2g=11 5g=24 other=0 max=383
MZ600_V15_CHANNEL1_NO_IR_NONDFS_PASS
MZ600_V15_LINK_UP_RC=0
MZ600_V15_IW_PASSIVE_CH1_RC=0 ELAPSED_MS=179
MZ600_V15_USERSPACE_BSS_COUNT=2
[60548.659547] MZ600_V15_SCAN_GATE_PASS channel=1 freq=2412 no_ir=1 nssid=0
[60548.663377] MZ600_V15_ESCAN_SET_RC=0 v2=0
[60548.676515] MZ600_V15_EVENT69 status=8 datalen=380
[60548.680630] MZ600_V15_EVENT69_PARTIAL bss_ver=109 bss_len=368 count=1
[60548.706452] MZ600_V15_EVENT69 status=8 datalen=420
[60548.709168] MZ600_V15_EVENT69_PARTIAL bss_ver=109 bss_len=408 count=1
[60548.791030] MZ600_V15_EVENT69 status=0 datalen=12
[60548.798393] MZ600_V15_FINAL_BSS count=2 version=109
[60548.805629] MZ600_V15_SCAN_COMPLETION aborted=0 fw_abort=0 owned=1
MZ600_V15_EVENT69_STATUS_COUNTS success=1 partial=2 other=0
MZ600_V15_NO_ASSOCIATION_OR_DIRECTED_SSID
MZ600_V15_LINK_DOWN_RC=0
MZ600_V15_UNLOAD_brcmfmac-wcc=0
MZ600_V15_UNLOAD_brcmfmac=0
MZ600_V15_UNLOAD_brcmutil=0
MZ600_V15_UMOUNT_FIRMWARE_RC=0
MZ600_V15_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_V15_SINGLE_PASSIVE_SCAN_ATTEMPT_AND_CLEANUP
__MZ600_V15_OWNER___TEST_RC_0__
```

Owner JSON receipt confirms:
```json
{
  "firmware_candidate": "4.218.248.44",
  "root_bash_rc": 0,
  "independent_poststate_ok": true,
  "script_cleanup_ok": true,
  "permanent_install": false,
  "scan_requested": true
}
```
Exact physical V15 scan module SHA `8ab54acbb204aeab49bdbf2ef4265fc40c8454e8a5c07ba57d11028105c719f4`, 344536 bytes. Original installed firmware/NVRAM/module SHA guard passed before scan and independent post-scan; no persistent driver/firmware/calibration writes, original firmware bind overlay unmounted and all Broadcom modules unloaded.

Private complete transcript and machine receipt are on Surface only: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V15-2012-2412-ESCAN-20261026\mz600-v15-owner-COM9-private.txt`, `mz600-v15-owner-receipt.json`, `mz600-v15-owner-attempted.marker`. **Do not publish full serial dump or nearby SSID/BSSID/MAC.**

## A/B comparison — prioritize 5GHz-specific root cause

| Measured property | V14 ch36 5180MHz 5GHz passive | V15 ch1 2412MHz 2.4GHz passive |
|---|---|---|
| Firmware | same 2012 `4.218.248.44` | same |
| Channel enumeration | 11 2G + 24 5G real | same |
| ESCAN V1 SET | RC0 | RC0 |
| Event69 PARTIAL/BSS | one / BSS109 | two / BSS109 |
| Event69 terminal SUCCESS | **not observed** | **status0 physically received** |
| Driver scan done | aborted=true, timeout | aborted=false, immediate |
| User scan duration | 10482ms | 179ms |
| User-visible BSS | 0 | 2 |
| Original state rollback | verified | verified |

**Important limitations**: V14 and V15 differ in both frequency band and local RF conditions, and scan-parameter/channel encoding could also differ. This A/B result establishes **conditional difference under those two tests**, not yet the exact cause. A newer firmware that works on 2.4GHz still requires properly resolved 5GHz scan completion, association, Bluetooth coexistence, longevity, and device variant compatibility before replacing installed firmware.

**Next source-first work:** Examine `brcmf_escan_prep`, old Broadcom 2012 ESCAN V1 channel-list encoding, 5GHz legacy chanspec `0x1b24`, passive scan dwell/timing defaults, firmware regulatory sideband/band behavior, and whether 5GHz scan enters an unfinished state. Compare original OEM stock Android 5GHz scan diagnostics if available. Consider tightly scoped new v16 unique owner test with alternative **source-grounded** passive dwell, or bounded per-channel firmware state (read-only only), after offline code review; do not blindly force terminal-success on receiving a partial result or reuse consumed v14/v15 scripts.

Earlier checkpoints: [V14](MZ600_V14_2012_ESCAN_EVENT69_PARTIAL_BSS109_PASS_TERMINAL_MISSING_2026-10-26.md), [V13](MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md).
