# MZ600 V16 — OEM 2012 BCM4329 5 GHz ESCAN 500ms passive dwell: seven PARTIAL, three BSS109, no terminal success

**Physical owner-run result read 2026-10-27.** Evidence: actual Surface-Book-2 COM9 private transcript and independent receipt from the new V16 one-shot. Supersedes [V16 staged-only checkpoint](MZ600_V16_2012_5GHZ_EXPLICIT_500MS_DWELL_ESCAN_SOURCE_AUDIT_ARM_BUILD_SURFACE_STAGED_2026-10-26.md). **V16 was executed and its unique one-shot was consumed; never rerun V16 automatically.**

## Firmware/module tested

- Installed Debian Linux7 kernel `7.0.0-next-20260422+`, original MZ600, factory per-device MAC retained, original installed NVRAM/calibration SHA unchanged.
- Only during the test: RAM-only bind overlay **BCM4329/3 May25 2012 firmware 4.218.248.44**, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`.
- V16 ARMv7 `brcmfmac` diagnostic module, 345004 bytes SHA256 `b0825974bf2bf69663c809239b8f9b7470d90929a7109bea8bab33575c56ebe9`. Builds on proven legacy WLC_GET_VALID_CHANNELS (since `chanspecs` still -52), masks all 5GHz supported channels NO_IR HT20-only, and enforces single-channel 5180MHz channel36 passive-only, no SSID/IE and global WLC_SET_PASSIVE_SCAN=1.
- Unique controlled change relative to V14: a finite **500ms scan-request passive_time** field rather than -1 firmware default. Plus passive scan v1 packet field instrumentation and Event69 status counter. Does not change NVRAM, firmware, frequencies, or timeout length.

## Exact sanitized physical results

```text
MZ600_V16_PREFLIGHT_START
MZ600_V16_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED
MZ600_V16_TEMP_2012_FIRMWARE_OVERLAY_PASS
MZ600_V16_WCC_LOAD_RC=0
MZ600_V16_WLAN0_PRESENT
MZ600_V16_PHY_2G=14 PHY_5G_TOTAL=29 PHY_5G_NO_IR=24 PHY_5G_DISABLED=5
brcmfmac: Firmware: BCM4329/3 wl0: May 25 2012 17:56:21 version 4.218.248.44
MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=35 2g=11 5g=24 other=0 max=383
MZ600_V16_CHANNEL36_NO_IR_NONDFS_PASS
MZ600_V16_LINK_UP_RC=0
MZ600_V16_IW_PASSIVE_CH36_RC=0 ELAPSED_MS=10374
MZ600_V16_USERSPACE_BSS_COUNT=0
MZ600_V16_V2_PASSIVE_DWELL_MS=500 encoded_chanspec=0x1b24 d11io=1
MZ600_V16_V1_CH36_WIRE chanspec=0x1b24 passive_ms=500 scan_type=1 nprobes=-1 nchans=1
MZ600_V16_ESCAN_SET_RC=0 v2=0
MZ600_V16_EVENT69 status=8 datalen=512
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=500 count=1
MZ600_V16_EVENT69 status=8 datalen=600
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=588 count=1
MZ600_V16_EVENT69 status=8 datalen=600
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=588 count=1
MZ600_V16_EVENT69 status=8 datalen=512
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=500 count=1
MZ600_V16_EVENT69 status=8 datalen=556
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=544 count=1
MZ600_V16_EVENT69 status=8 datalen=512
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=500 count=1
MZ600_V16_EVENT69 status=8 datalen=600
MZ600_V16_EVENT69_PARTIAL bss_ver=109 bss_len=588 count=1
MZ600_V16_ESCAN_WATCHDOG_FIRED
MZ600_V16_FINAL_BSS count=3 version=109
MZ600_V16_SCAN_COMPLETION aborted=1 fw_abort=1 owned=1
MZ600_V16_EVENT69_STATUS_COUNTS success=0 partial=7 other=0
MZ600_V16_NO_ASSOCIATION_OR_DIRECTED_SSID
MZ600_V16_UNLOAD_brcmfmac-wcc=0
MZ600_V16_UNLOAD_brcmfmac=0
MZ600_V16_UNLOAD_brcmutil=0
MZ600_V16_UMOUNT_FIRMWARE_RC=0
MZ600_V16_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_V16_SINGLE_PASSIVE_SCAN_ATTEMPT_AND_CLEANUP
__MZ600_V16_OWNER___TEST_RC_0__
```

Surface receipt:
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

The private COM9 transcript SHA256 in receipt `22eb2eadf5972fd111236e165d9a8f73218a0109ebfa1c1b88d024bc4cc4c163` **was independently matched byte-for-byte after normalizing Windows CRLF to LF**. All private scan outputs remain on Surface. No SSID, BSSID, MAC, remote credentials, or proprietary binary placed in Git.

## Comparison to V14/V15

| Evidence | V14 5G ch36 default passive dwell | V15 2G ch1 default passive dwell | V16 5G ch36 explicit 500ms |
|---|---|---|---|
| Same OEM 4.218.248.44 FW | yes | yes | yes |
| ESCAN V1 acceptance | RC0 | RC0 | RC0 |
| Firmware Event69 partial packets | 1 | 2 | **7** |
| BSS format | 109 | 109 | 109 |
| Unique cached BSS records | 1 | 2 | **3** |
| Terminal Event69 status0 SUCCESS | no | **yes** | **no** |
| Native cfg80211 done | aborted=true | aborted=false | aborted=true |
| User `iw` output BSS | 0 | 2 | 0 |
| Elapsed user scan (ms) | 10482 | 179 | 10374 |
| Original system restored | yes | yes | yes |

The V16 seven partial events arrived between `[66246.280]` and `[66246.694]`, about 414 ms; this is temporally consistent with a longer 500ms observation window but does **not** prove firmware actually dwelled precisely 500ms or that longer dwell alone caused the higher BSS count; RF AP traffic differs between tests. Crucially, **finite passive_time by itself did NOT yield a terminal Event69 SUCCESS**, and hardware/host Event69 ingress for partial packets worked.

The V1 parameter trace rules out a **simple 5GHz wrong-chanspec hypothesis** in V16: actual transmitted fields in host packet matched original BCM4329 D11N `0x1B24`, `scan_type=1`, `n_channels=1`, `passive_time=500`, `io_type=1`. It does **not** prove on-chip firmware interprets every field as intended. `nprobes=-1` remains from standard Linux `brcmf_escan_prep`; despite passive scan type and global passive setting, this is a concrete field for further old-fw ABI scrutiny. Do not indiscriminately change every parameter at once.

## Next source-led focus, no physical test committed yet

1. Audit original firmware-era `escan` request handling and status/terminal emission for 5GHz passive single channel versus 2GHz; especially whether `nprobes=-1`, `home_time=-1`, `active_time=-1`, and per-BSS Event69 only affect termination on specific hardware/firmware.
2. Check channel36/passive non-DFS per-channel info and regulatory sideband readback without modifying country or enabling transmission. Existing channel proof remains.
3. Consider a spare stock Android OEM Xoom as a comparison: collect host-side scan-completion signals and timing with no firmware changes. Native GUI alone cannot prove firmware terminal.
4. If another owner-approved unique Xoom test is justified, change one variable at a time, bound duration, preserve guards/NO_IR/no probe/no association, verify Event69 terminal independently; avoid synthesizing `cfg80211_scan_done(...aborted=false)` from partial count.

**Do not install the newer firmware as default until both bands complete correctly, and do not rerun V16.**
