# MZ600 Linux7 original BCM4329 legacy BSS108 -> cfg80211 publication — v11 source milestone

**October 26, 2026. Status: CODE AUTHORED AND COMMITTED; EXACT-ABI BUILD NOT VERIFIED, NO V11 MODULE, NO DEVICE TEST.** The assistant's normal authorized remote WSL kernel-build request was **blocked by the platform's safety checks**. No attempted alternate remote build or device action followed. Do not describe this as a compiler/build failure, a broken Xoom, or a successful kernel module.

## Previously proven physical prerequisites

[Owner's v10 HRI39 channel36 scan milestone](MZ600_V10_HRI39_300MS_PASSIVE_THREE_VALIDATED_CH36_BSS_PHYSICAL_PASS_2026-10-26.md): original 4.218.248.20 firmware + device-specific FDT MAC and matching US/69 calibration (no cloned OEM MAC); Linux 7.0.0-next-20260422+; single 5180MHz/channel36 NO_IR passive scan started via `WLC_SCAN(50) rc0`, firmware GET `WLC_SCAN_RESULTS(51) rc0` returned 1632 bytes, version108 and 3 records. Actual v108 safe-structure validator logged `records=3 ctl36=3 other=0 invalid_ie=0 safe=1` (124-byte historical BSS header, bounded SSID/IE/TLV), owner script and independent COM9 post-audit restored original FW/cal/installed module. This is one MZ600, not full cfg80211 reporting nor event-driven completion. Event26 unobserved; 10sec escan fallback remains.

## New code: one logical capability on top of exact proven v10

[GitHub v11 exact-ABI builder](../../scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py), source commit `7a83c3cbeec0b7c889ea9d2e22ae82e7e22b7b12` following initial `84e33c9`, extends the pre-existing v10 RAM-only lab source (no mainline kernel code copied wholesale):

- Defines `brcmf_legacy_inform_bss108()` which is called from the legacy timeout-worker **only after full existing outer buffer, per-record length, SSID length, channel count, IE offset+length and entire IE-TLV sequence validator passes on all records** (`valid && count && v108_checked == count && v108_other == 0`).
- Before publishing **any** record, makes a separate all-record precheck: every record's wire version must be 108, length at least124 and inside total; ctl_ch exactly36, RSSI in expected negative dBm range, non-multicast/nonzero BSSID; checks complete consumption. In its reporting loop it repeats record and IE bounds. This avoids partial publication caused by late invalid metadata (though a cfg80211 allocation failure after earlier inform calls may still leave previously accepted BSS in the kernel cache).
- Resolves **actual wiphy 5180 MHz** via `ieee80211_get_channel()`, requires band5G, channel36, **not DISABLED/RADAR**, explicit NO_IR, and that it equals the single cfg80211 scan-request channel pointer. Does not expose fabricated frequency/channel, unlock regulatory constraints, initiate probes or association.
- Extracts legacy BSSID, BSS capability and beacon interval, signed RSSI converted to mBm, and validated IE slice. Calls kernel `cfg80211_inform_bss_data()` and releases the resulting ref with **`cfg80211_put_bss()`**, as does Linux7's already-existing native `brcmf_inform_single_bss()`. Uses native `ktime_to_ns(ktime_get_boottime())` for reporting time.
- Uses the normal cfg80211 scan BSS cache (so **local** `iw scan` may display SSIDs/BSSIDs to the device user as expected), but **no wireless identities are logged in new kernel printk or published to GitHub**. Diagnostic reports only `MZ600_LEGACY_CFG80211_BSS_INFORM count=<value> requested=<n>` and normal v108 validated-count status. This is ordinary Linux scan reporting, not public logging.
- Preserves modern v109+ firmware escan, precise BCM4329 HRI39 fallback, 300ms passive channel36 scan, 10sec timeout completion, observation-only event26 handler and unchanged v10 host/dev environment. **No legacy scan completion-lifecycle implementation in v11**: that is the next *separate* kernel patch.

## Build blocker / required release gate

The requested WSL operation `git pull --ff-only && python3 -m py_compile ... && python3 ...v11...py` was rejected before execution by the Remote Desktop Commander tool's **OpenAI safety checks**. This was an execution-policy block, not a compiler error. No attempt was made to circumvent it by changing remote tool or command routing. Therefore the script is **uncompiled and unqualified**. Do not create a v11 owner device one-shot or infer its module SHA from v10. The next verification must perform the build on the normal authorized Desktop WSL host with owner control, inspect compiler output, exact ABI, generated patch SHA, module file SHA, original-source/module hash restoration and repository status.

One-shot owner-controlled build command, **Desktop PowerShell** (not the Xoom root shell):

```powershell
wsl.exe -d Ubuntu-22.04 -u xoomdev -- bash -lc 'cd /home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project && git pull --ff-only && python3 -m py_compile scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py && python3 scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py'
```

The builder's planned output lives in `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-legacy-v108-cfg80211-inform-v11-20261026/`: `brcmfmac-legacy-v108-cfg80211-inform-v11.ko`, generated patch, build report and restoration hashes. **These files do not currently have verified existence or digest.** Compile or static errors must be corrected before any RAM transfer.

After a verified build, prepare a **new v11 owner-operated checksum-pinned RAM-only test** using previous proven COM9 transfer and restoration, with `iw dev wlan0 scan freq 5180 passive`; capture only sanitized validation/report counts publicly. Review nearby BSS identities privately on owner host; do not commit identities. Clean rollback and independent COM9 audit as with v10.

## Separate next stage: scan completion

Original HRI39 firmware did not deliver an event26 callback in v9/v10; do not assume it exists or substitute an invented notification. Linux7 `fweh.c` `brcmf_fweh_activate_events()` enables registered event masks via firmware `event_msgs` iovar but events may be absent/unsupported/mapped differently on old FW. Research its exact legacy completion semantics; if no event, build bounded delayed-work polling with deterministic timeout/abort ownership and exactly-once `cfg80211_scan_done`. Do not combine this lifecycle change with the v11 BSS inform change. Upstream: current maintainer baseline, KUnit for v108 parser and cancel paths, checkpatch/sparse, modern generic 4.220.48 no-regression, MZ602/MZ604, unrelated BT/U4/MMC on separate series, and explicit owner approval/DCO before submission.

**At checkpoint, accomplished = source code and documented safe plan, NOT compilation or physical v11 success.**
