# MZ600 V14 — 2012 OEM BCM4329 5GHz ESCAN accepted, Event69 PARTIAL/BSS109 received, terminal absent (physical test)

**Date: 2026-10-26. Actual owner-run V14 Surface/COM9 receipt and private transcript read back.** This checkpoint supersedes the preceding [V14 staged-only record](MZ600_V14_2012_OEM_PASSIVE_5180_ESCAN_MODULE_AND_SURFACE_ONESHOT_STAGED_2026-10-26.md) and carries the result into the handoff. Do **NOT** repeat the consumed v14 one-shot.

## Verified successful capabilities on the original MZ600

The known original MZ600 Linux7/Debian12.15 kernel `7.0.0-next-20260422+`, previously verified passive-wiphy fallback, unchanged board NVRAM and RAM bind-overlay firmware **4.218.248.44** (May25 2012; firmware sha256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`) initialized correctly with driver v14 SHA `40a8779fe83b03201b3df79fabce55ea1f47fcd4095150889d7f9b1bc88b0df8`, `wlan0` up and registered 2G/5G. Firmware `chanspecs` still returns -52, but legacy ioctl217 fallback yields 35 real supported channels, 11x2G and 24x5G, with 5GHz wiphy 24 NO_IR and 5 disabled.

**New v14 breakthroughs:** Linux7's **legacy version-1 ESCAN** iovar now **physically accepts the channel36 passive scan with return code0**; Event69 `BRCMF_E_ESCAN_RESULT` **physically arrives across SDIO into brcmf_cfg80211_escan_handler**, with event status **8 = PARTIAL**, data length600, one BSS record length588, **BSS version109** matching Linux7 `BRCMF_BSS_INFO_VERSION=109`. Consequently, these questions are settled: 2012 ESCAN command is supported at least to request acceptance; firmware sends Event69 partial results; driver receives them; BSS record version matches Linux7, no global 108-to-109 conversion needed for this result.

## Fresh exact sanitized diagnostic lines

```text
MZ600_V14_PREFLIGHT_START
MZ600_V14_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED
MZ600_V14_TEMP_2012_FIRMWARE_OVERLAY_PASS
MZ600_V14_WCC_LOAD_RC=0
MZ600_V14_WLAN0_PRESENT
MZ600_V14_PHY_2G=14 PHY_5G_TOTAL=29 PHY_5G_NO_IR=24 PHY_5G_DISABLED=5
MZ600_V14_DMESG_LINES_BEFORE=647
brcmfmac: Firmware: BCM4329/3 wl0: May 25 2012 17:56:21 version 4.218.248.44
MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=35 2g=11 5g=24 other=0 max=383
MZ600_V14_CHANNEL36_NO_IR_NONDFS_PASS
MZ600_V14_LINK_UP_RC=0
MZ600_V14_IW_PASSIVE_CH36_RC=0 ELAPSED_MS=10482
MZ600_V14_USERSPACE_BSS_COUNT=0
[58710.756011] MZ600_V14_SCAN_GATE_PASS channel=36 freq=5180 no_ir=1 nssid=0
[58710.761488] MZ600_V14_ESCAN_SET_RC=0 v2=0
[58710.885761] MZ600_V14_EVENT69 status=8 datalen=600
[58710.889628] MZ600_V14_EVENT69_PARTIAL bss_ver=109 bss_len=588 count=1
[58721.163288] MZ600_V14_ESCAN_WATCHDOG_FIRED
[58721.188204] MZ600_V14_FINAL_BSS count=1 version=109
[58721.200248] MZ600_V14_SCAN_COMPLETION aborted=1 fw_abort=1 owned=1
MZ600_V14_NO_ASSOCIATION_OR_DIRECTED_SSID
MZ600_V14_CLEANUP_START rc=0 state=OBSERVATION_COMPLETE
MZ600_V14_LINK_DOWN_RC=0
MZ600_V14_UNLOAD_brcmfmac-wcc=0
MZ600_V14_UNLOAD_brcmfmac=0
MZ600_V14_UNLOAD_brcmutil=0
MZ600_V14_UMOUNT_FIRMWARE_RC=0
MZ600_V14_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_V14_SINGLE_PASSIVE_SCAN_ATTEMPT_AND_CLEANUP
__MZ600_V14_OWNER___TEST_RC_0__
```

The original driver recorded one internally collected BSS, but user `iw` exposed zero `^BSS ` lines. `iw` process exit0 **does not indicate a successful network scan**: scan **timed out at roughly 10.5 seconds** and driver reported `cfg80211_scan_done` as **aborted=true**, `fw_abort=true`. **There is no Event69 SUCCESS terminal event in captured incoming handler events** (only one Event69 PARTIAL); this remains the outstanding blocker. No proof yet whether firmware omitted terminal, terminal was lost before host classifier, command format/status demanded follow-on, or scan engine stalled.

## Receipt and verified baseline restoration

Surface owner's JSON receipt recorded `root_bash_rc:0`, `independent_poststate_ok:true`, `script_cleanup_ok:true`, `permanent_install:false`, `scan_requested:true`. The pre-run original installed generic firmware, unchanged calibration and original brcmfmac module all had exact matching SHA; independent postrun verification repeated them, confirmed no bind overlay and no wlan0/brcm modules. No Xoom reboot, permanent files, system partition, NVRAM, MAC identity, regulatory override, or network association changed. **No repeat of this one-shot.**

Private evidence stays in Surface directory `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V14-2012-ESCAN-20261026`:
- `mz600-v14-owner-COM9-private.txt` (full transcript)
- `mz600-v14-owner-receipt.json` (receipt SHA and boolean restoration)
- `mz600-v14-owner-attempted.marker`

Do not upload private full serial transcript or any SSID/BSSID/MAC/credentials to public repository.

## Interpretation and next research gate

Before V14, HRI39 4.218.248.20 had physical 5G but **no modern escan** (iovar -52), while generic 4.220.48 had escan and normal 2.4G scans but no 5G. **Now the later compatible 2012 4.218.248.44 provides both 5GHz and real Event69 partial BSS109.** This substantially elevates it to the leading firmware candidate even though the event69 terminal completion remains unsolved; do not install permanently yet.

Suggested source-first next iteration: investigate what ends or stalls 2012 ESCAN V1 for one passive channel, whether source's v1 request layout and passive dwell fields meet this firmware's expected semantics, and event69 terminal emission/ingress at pre-headerpull. Compare with contemporaneous OEM Android behavior to distinguish timeout/event protocol. Need a new unique guarded laboratory build, not another V14 run, if owner wants a future physical test. Avoid treating any nonzero BSS count or PARTIAL result as evidence of terminal success; never convert PARTIAL into fake success. Maintain NO_IR safety and original BSS109 parser.

Links: [Source audit](../research/MZ600_V14_DECISION_2012_OEM_FIRMWARE_LEADING_CANDIDATE_ESCAN_SOURCE_AUDIT_2026-10-26.md); [v14 module/launcher](MZ600_V14_2012_OEM_PASSIVE_5180_ESCAN_MODULE_AND_SURFACE_ONESHOT_STAGED_2026-10-26.md); [V13 physical dualband](MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md).
