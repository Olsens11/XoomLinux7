> **Newest observational diagnostic prepared, NOT physical:** [v12b 13-stage event RX exact-ABI build and Surface staging](../checkpoints/MZ600_V12B_EVENT26_RX_GATE_OFFLINE_BUILD_PASS_SURFACE_ONESHOT_STAGED_2026-10-26.md) follows [v12a on-hardware event_msgs bit26 ON, callback absent](../checkpoints/MZ600_V12A_EVENT26_FIRMWARE_EVENTMSGS_BIT26_READBACK_PHYSICAL_PASS_2026-10-26.md). Fresh v12b-r1 349520B SHA `48bf1d3f5cc163f33419e3ebddaa4b50067096e6c1954ced578568c86c75f5b6` and owner-only three-pinned-input Surface launcher staged with no COM9 session. Trace numerical `skb,link,length,subtype,oui,user,raw26,proc26,registered26,size26,queued26,worker26,handler26` start-vs-timeout deltas; **do not infer firmware never emitted event26 from zero after ingress when SDIO RX/hdrpull remain outside these counters**. No cfg80211 completion modification or new event mask SET. v12b physical ingress observations remain PENDING and generic regression/upstream release gates OPEN. Do not repeat v12a.

> **Latest v12a build update:** [exact-ABI offline build PASS](../checkpoints/MZ600_V12A_EVENT26_MASK_READBACK_EXACT_ABI_OFFLINE_BUILD_PASS_2026-10-26.md), module 347912B SHA `75b6e80436b371accd01faa943a0ea45d100ab0a3faa0349db1bc3cef826c77f`; original driver restored, no physical device touched. Firmware mask bit26 GET is still unmeasured on actual Motorola hardware. This is observation preparation, NOT scan-completion implementation.

> **2026-10-26 post-v11 source-audit update:** The original v11 physical 4-BSS Linux cfg80211/iW scan **PASSED** after this document's older "v11 not tested" section was written. Separate [v12a source-only checkpoint](../checkpoints/MZ600_V12A_EVENT26_MASK_READBACK_SOURCE_ONLY_OFFLINE_QA_PASS_2026-10-26.md) now adds a bounded read-only event_msgs bit26 readback immediately before the already proven legacy ioctl50, without changing completion, RF restrictions or firmware masks. Desktop static gates PASS; **module not built, no new physical event readback, no v12 lifecycle implemented**. Source review: fweh activation SETs a handler-built event mask; the observer registered in init_escan should request native event26, but firmware GET remains unverified. cfg80211 completion helper clears scan_request before timer deletion; absent additional serialization, late worker/event/abort races require explicit design and testing. Keep v11 last physical reference.

# Original Motorola BCM4329 legacy scan completion — evidence and future isolated patch design

**2026-10-26. RESEARCH / DESIGN ONLY. No new event-based or polling kernel implementation, no physical tests beyond v10.**

## Proven hardware boundary

v7R and v10 physical scans under original HRI39 firmware 4.218.248.20 accepted **WLC_SCAN ioctl50=0** and read **WLC_SCAN_RESULTS ioctl51=0**, v108 header 1632B/3 records; v10 validated all three records' ctl_ch36, SSID length, IE offset and TLV bounds. Both used the existing Linux7 brcmfmac **escan 10-second timeout worker** to obtain results; v9/v10 observation-only `BRCMF_E_SCAN_COMPLETE = 26` handler received no callback during an owned scan. This does not prove the firmware never emits 26 or that the host event mask is correctly interpreted.

## Original Broadcom 2010 driver evidence

[Original Broadcom BCM4329 `wl_iw.c` source](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/wl/sys/wl_iw.c) has `wl_iw_set_event_mask` which GETs firmware `event_msgs`, sets `WLC_E_SCAN_COMPLETE` (26), and SETs `event_msgs`. Its event dispatcher handles `WLC_E_SCAN_COMPLETE`: for incremental scans it wakes a scan background thread; for normal scans it sends a WEXT scan-completed indication. A contemporaneous [Linux legacy staging driver](https://android.googlesource.com/kernel/common/+/890879cfa08f5ceaa09810611f46e890f7d57ff6/drivers/staging/brcm80211/brcmfmac/wl_iw.c) contains similar handling. This is a period-correct implementation pattern, **not proof the specific HRI39 firmware generated event26 during v10**.

The exact project Linux7 `brcmfmac/fweh.c` `brcmf_fweh_activate_events()` builds a mask of registered event handlers, then SETs `event_msgs` to firmware; v9/v10 registered event26 observation-only next to modern event69. That covers the general intended driver-side event-bit enable, but has **not independently read back firmware mask bit26** or measured raw firmware notification dispatch.

## Next isolated measurements (no unsolicited transmissions)

1. **Read-only** inspect the actual firmware `event_msgs` bit26 after handler registration while the original OEM firmware is loaded under a guarded RAM module. Treat an unexpectedly unset bit as a firmware/event programming issue, not evidence event26 doesn't exist.
2. If set, observe raw event-code counters only (not BSSID or content), record numeric `status`, `datalen`, local scan ownership and timestamps. Ensure event handler is registered prior to activation, and that eventmask length and 26 map correctly in BCM4329 vendor-specific event mapping.
3. Do not modify `cfg->scan_request`, timer cancellation, or call `cfg80211_scan_done` in observation-only handlers; collect physical evidence first.

## If firmware event26 proves absent: bounded asynchronous polling design

- Keep `cfg80211_ops.scan` as ownership point, accepting only supported channel/SSID/IE/passive constraints and returning error **before** accepting request when old firmware cannot start a scan.
- Start ONE controlled `delayed_work` scan-results getter via `WLC_SCAN_RESULTS=51` on the chip/firmware capability branch. Set an absolute deadline to cap work and preserve the existing outer scan-abort watchdog. Never sleep in the event workqueue or monopolize a shared workqueue waiting for a radio response.
- Beware: a successful GET returning `buflen12 count0 version108` **can mean either an empty completed scan or an unfinished scan**. A "nonempty => done" algorithm is not a reliable complete state machine (legitimate empty air and partial results are possible). Prefer a documented firmware scan-status ioctl, a genuine event, or a verified stabilization/timeout condition. A poll may collect results early for diagnostic purposes, but not assert scan completion absent a completion signal or deterministic bounded rule.
- Validate **all** v108 BSS boundaries/SSID/IE TLVs/fields before cfg80211 inform, confirm requested channel is allowed by current wiphy/regdb, use standard `cfg80211_inform_bss_data` + `cfg80211_put_bss`; no public identifier logs.
- Handle races with exactly-once clear-of-ownership under correct serialization: timeout, event, explicit abort, interface down/removal, USB/SDIO disconnect, suspend and firmware failure. Cancel synchronous delayed work carefully and never `cfg80211_scan_done` on a scan whose start returned an error.
- Keep the modern `escan` path, version109+, generic 4.220.48 fw, P2P and scheduled scans untouched. Consider fw-specific narrow capability rather than global chip ID only, and document firmware 4.218.248.20 proof.
- Add KUnit for v108 malformed packets, BSSID/signal/IE gates, empty/late/duplicate event, timeout and cancellation; exercise actual 2G/5G/BT and MZ602/MZ604 before any upstream proposal.

## Current sequence / bisectability

**v11:** implement cfg80211 reporting for already-validated v108 scan results, **source committed but exact ABI build safety-blocked**, see [v11 checkpoint](../checkpoints/MZ600_V11_LEGACY_BSS108_CFG80211_REPORTING_SOURCE_READY_BUILD_BLOCKED_2026-10-26.md). Do not call it tested. **v12 (future separate logical patch):** event26 readback/observation OR bounded lifecycle work as above, validated against actual Motorola firmware; do NOT merge into v11 until individual ABI build, physical scan, regressions and upstream test gates pass. Non-driver whole-chip regulator U4, BT reset, OEM SDMMC tap and CCCR quirk remain separate patches.

**Bottom line:** the historical standard pattern is *event-driven notification after firmware scan*; our earlier tests have not seen that event, so the design must gather more evidence before asserting a replacement completion mechanism.
