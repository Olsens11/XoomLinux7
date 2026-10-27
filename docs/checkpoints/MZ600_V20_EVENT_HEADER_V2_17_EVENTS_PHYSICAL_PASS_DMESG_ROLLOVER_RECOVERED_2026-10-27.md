# MZ600 V20 actual physical event-header evidence — all Event69 headers VERSION 2; 2026-10-27

**Status: V20 PHYSICAL HEADER ABI OBSERVATION PASSED, V20 compatibility patch NOT IMPLEMENTED, no RF regression certification.** One unique owner-authorized 5180 MHz ch36 500ms passive NO_IR trial `hdr1-01-mask000` on the experimental MZ600 was executed over Surface COM9. Do not rerun this ID.

## Immutable input and provenance
- Branch `wip/clean-wifi-bt-usb-20261025`; owner source-only V20 builder commit `3f825be717e16f6b9aeb677e5b677595a53ebde8`; builder `tools/forensics/build_mz600_v20_2012_5g_event_header_probe.py` SHA256 `7287ed6f619f94fb5da3a795c1c6ccd222d2ac29b8d9ffe1c69b249579701b45`.
- Exact-ABI ARMv7 diagnostic `brcmfmac-2012-escan-event69-v20.ko`, **349176 bytes**, SHA256 `4ddce3565c79d96a6c040b94a1fd76e00d62d6360f15f2fb898dfa7eadf09a8c`; preserved source and installed original brcmfmac module unchanged.
- Original private OEM 2012 Broadcom firmware `4.218.248.44`, 264140 bytes SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, in **RAM bind overlay only**. Existing device-specific NVRAM unchanged. Extra event subscription mask **0**.
- Owner-private Surface staging `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V20-2012-HEADER-20261027\`. The v20 shell SHA256 `83aa91b7611c3046b40e8ba5ee05980cddd6cda46906922feec9500f95686234`, owner Python suite SHA256 `7700d706f28f1d7eb62a88d3ca8e985e05533ebbec47d579d48a264fd61adab7`. These are locally adapted from SHA-pinned V19 scripts; V20 test script/receipt remain private on Surface as of this checkpoint.
- Known-good installed firmware SHA `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`; installed calibration SHA `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`; original installed module SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`.

## Actual physical result — read the recovered dmesg evidence, not the incomplete original transcript receipt
- `iw dev wlan0 scan freq 5180 passive` returned rc0 **1801 ms** and **3 userspace BSS entries**. The terminal-success event reached `brcmf_cfg80211_escan_handler`: `MZ600_V20_EVENT69 status=0 datalen=12`, then `MZ600_V20_SCAN_COMPLETION aborted=0 fw_abort=0 owned=1`, `MZ600_V20_FWEH_DISPATCH code=69 status=0 ifp=1 handler_rc=0`.
- Recovered **17 numeric Event69 HEADER records** in the same scan from read-only live Xoom `dmesg`: **every header reports `ver=2`**, so the prior simple theory that this firmware emits a version-1 header missing the two trailing interface indices is **NOT SUPPORTED** for these observed frames.
- Terminal frame: `MZ600_V20_HEADER code=69 ver=2 ifidx=0 bsscfg=0 has_indices=1 pktlen=94 datalen=12 v1_hdr=70 v2_hdr=72`.
- Some partial events have irregular interface indices **despite version2**: 6 of 17 headers show nonzero `bsscfgidx`; **3 are >=16** and cannot be valid local indices. Other partials with `bsscfgidx=1` or `2` reached worker but ifp NULL, as in V19. Exact cause **unresolved**: possible firmware-specific field semantics, mixed wire subformat, receive offset/length issues, or actual corrupted indices. Do not force `iflist[0]` globally, do not add speculative v1 parsing, do not infer a power/reset fix.
- `has_indices=1` is a **byte-length guard only**; it does not imply the byte values have valid interface semantics. Variations in `pktlen-datalen` (e.g. terminal 94-12, partial 686-600) require independent framing study.
- **V20 source did not remap/repair any event**, so this is a successful *unmodified dispatch* for the terminal packet in this particular scan, not a claimed compatibility fix or sustained improvement.

## Why the original suite falsely flagged missing header logging

Original v20 shell copied V19 strategy:
`LOG_LINE_BEFORE="$(dmesg | wc -l)"` and later `dmesg | awk -v first="$LOG_LINE_BEFORE" 'NR>first'`.
The pre-scan log count was **1378** lines; the recovered ring then held **1357** lines. Under finite ring-buffer turnover, this *line-count threshold is not a stable append cursor*. All filtered kernel logs were omitted, so the suite's first `hdr1-01-mask000.json` receipt misleadingly had `event69_terminal_success=false`, `header_versions=[]` and `script_cleanup_ok=false`, despite physical SUCCESS and clean rollback. This receipt MUST NOT be overwritten or reported as true firmware failure.

Recovery used a **separate read-only COM9 dmesg inspection**, no second scan or installed changes. Owner-private `runs/hdr1-01-mask000.recovered-v20-kernel-numeric.private.txt` capture SHA256 `80b145e2fdb2b65ff24749bf232caa62f805ca39d97a847f4583dc36b2837eb8`; derived `runs/hdr1-01-mask000.recovered-v20-summary.json`. Recovered summary confirmed `header_samples=17, versions=[2], terminal_headers=[[2,0,0,1,94,12]], invalid_bsscfg_count=3, nonzero_bsscfg_count=6, event69_terminal_seen=true, scan_done_success_seen=true`. Do not publish SSID/BSSID/MAC or full raw dmesg.

**Future harness fix:** anchor kernel messages to a unique authorized `/dev/kmsg` marker or monotonic printk timestamp/snapshot and verify capture before declaring pass; never use `dmesg | wc -l` as an append cursor. Test the log extraction in offline synthetic ring-turnover cases before any further physical scan. Preserve this consumed script and signed hashes; stage corrected **new** trial scripts for next test.

## Restoration and gates

The one-shot Bash completed `rc=0`, logged original file and unloaded-radio integrity pass; independent owner root postflight **PASS**, original WPA/WLAN/BT runtime restored. A separate fresh, read-only COM9 preflight again confirmed original installed firmware/NVRAM/module hashes, wlan0 DOWN, WPA ACTIVE, BT SERVICE/HCI quiet, and overlay absent. No firmware, NVRAM, kernel module or boot partition was permanently changed.

**Conclusions:** PHYSICAL Event69 version2 PROVEN for this firmware/scan. V19 terminal-index misrouting remains real but not caused simply by a version1 event header; fault is intermittent and affected some v2 partials. Need isolate genuine v2 index anomalies/frame boundaries with a minimally instrumented source-controlled follow-up (if evidence requires), then decide configuration versus driver patch scope; don't promote an untested conditional index fallback into upstream series. No DCO or external submission authorization.
