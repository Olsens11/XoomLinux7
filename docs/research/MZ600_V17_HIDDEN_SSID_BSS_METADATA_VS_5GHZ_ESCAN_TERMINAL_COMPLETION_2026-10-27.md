# MZ600 V17 research: could hidden SSIDs, AP density, or off-channel BSS results prevent OEM 2012 5GHz ESCAN completion?

**Date 2026-10-27. Source review, photograph discussion and research only; NO new RF test, Xoom change, module build, or scan.**

## Owner's observation

An owner-provided Android-style Wi-Fi list showed about twenty nearby SSID entries and a visibly labeled "Hidden Network". This establishes that many access points are visible to that *listing device*, but **does not establish** whether the entries are 2.4GHz vs 5GHz, whether any of those APs operate on our selected **5180MHz channel36**, or whether the hidden SSID was present on channel36 during V14/V16. SSID names ending in "-5" / "5G" are not reliable channel metadata. Do not upload or reproduce the user's SSID list in the public repo.

## Physical Linux7 MZ600 comparison

- V14 5G single 5180MHz passive: firmware accepts ESCAN V1; Event69 PARTIAL **1** / cached BSS109 **1**; no terminal SUCCESS, timeout ~10.48s; independent rollback verified.
- V15 2G single 2412MHz passive: firmware accepts same ESCAN V1; Event69 PARTIAL **2** / cached BSS109 **2**; **real terminal Event69 SUCCESS status0**, normal cfg80211 scan done aborted=false at **179ms**; rollback verified.
- V16 5G single 5180MHz passive, explicit 500ms dwell (vs firmware-default -1): ESCAN V1 accepted, actual outgoing host encoded channel **0x1B24** and `scan_type=1,nprobes=-1,nchans=1`; Event69 PARTIAL **7**, cached unique BSS109 **3**, **no terminal SUCCESS**, watchdog ~10.37s; rollback verified. 7 partials arrived within ~414ms, then no terminal before 10s watchdog. Increased partial count was not independently shown to result solely from dwell; local RF varies.
- So **lack of APs is not demonstrated as the failure**, and receiving multiple BSS is not a terminal-completion criterion. Event69 transport and normal event69 SUCCESS callback already work on the same firmware in 2G.

## What the active Linux7 source actually does

Files inspected locally in Desktop WSL kernel `v064-bigpart-linux`:
- `brcmfmac/cfg80211.c` `brcmf_cfg80211_escan_handler`: branches on the **firmware-supplied Event69 status**. For PARTIAL(status8), validates and caches one BSS record. For non-PARTIAL statuses, independently sets ESCAN_IDLE, calls `brcmf_inform_bss`, interprets `status == BRCMF_E_STATUS_SUCCESS`, and invokes `brcmf_notify_escan_complete`/cfg80211 scan done. There is **no minimum discovered AP count and no SSID-nonempty check controlling this terminal path**. A hidden SSID should NOT block normal scan completion.
- `brcmf_compare_update_same_bss` does read `SSID_len` and SSID bytes, but **only to deduplicate partial network records**; it does not decide whether the firmware emits terminal Event69. An improperly handled empty SSID could hypothetically expose a **firmware-side bug**, but no such bug has been demonstrated.
- `brcmfmac/fwil_types.h` `struct brcmf_bss_info_le` contains **`SSID_len`**, `chanspec`, `ctl_ch`, `ie_offset`, `ie_length`, `version`, `length`, `beacon_period`, and flags. We can check if a partial record represents a blank/hidden SSID without logging the SSID; can also check whether the reported channel matches requested channel36 **0x1B24** and whether the IE region fits within the BSS record. The old V14/16 logs did NOT capture these per-BSS metadata fields.
- IEEE 802.11 passive scanners listen for beacon frames; access points with hidden SSIDs ordinarily still emit beacon frames with an empty/zeroed SSID element. Scans finish after scheduled channel dwell/state processing even with **zero APs**. However it remains reasonable to test whether a firmware defect triggered by specific beacons/IEs could block firmware-specific terminal transition.

## Ranked, discriminating next investigation (source first)

1. **First collect privacy-safe BSS metadata for the next unique owner-approved controlled 5GHz passive scan**. For each Event69 PARTIAL packet, report packet index; result BSS109 version and lengths; `SSID_len` numeric and `is_hidden=(SSID_len==0)`; *decoded and raw BSS chanspec and control channel number*, and `ie_offset+ie_length <= bss_info.length` boolean; packet's firmware Event69 numeric status and terminal/timeout marker. **No SSID names, BSSID/MAC, raw IEs or private AP fingerprint hashes in public logs.**
2. Crucial check: **do all 5G partial BSS records actually report channel36?** If not, the chipset may be scanning different/more channels than the one-channel host request, or delivering cached/off-channel events. Investigate frequency/firmware behavior before changing dwell again.
3. If a BSS has SSID_len=0, correlate *time order* (not identity) with whether a terminal event ever comes. A hidden SSID on channel36 would show it is encountered, **not establish causation**. In next comparison, first inspect OEM Android reference scan or select a controlled RF environment before attributing failure to hidden AP.
4. Instrument **all Event69 terminal statuses and ingress/drop/error counts** at firmware-event layer (not just cfg80211 handler) if metadata shows normal well-formed BSS. Under V16, only seven status8 partial events reached the handler and none status0. Do not synthesize terminal SUCCESS from number of BSS reports.
5. Inspect original Broadcom-era ESCAN scan-state machine, passive-channel exit, and scan_params default `nprobes=-1`, `home_time=-1`, `active_time=-1`; only build new one-shot if a specific hypothesis survives source audit. Preserve NO_IR/HT20 channel gate, original board calibration, single device factory MAC, bounded timeout and independent rollback. **Never reuse spent V14, V15 or V16.**

## Key interpretation

The owner's intuition about *unsatisfied completion conditions* is a useful framing. The condition should be **scan engine finished its requested channel(s)**, not "all nearby SSIDs have been found." A misbehaving old firmware on 5GHz could stall that transition. Hidden SSIDs and malformed management frames are candidate *triggers* for such a bug, not known causes and not ordinarily legitimate conditions that a scan must satisfy to finish.

## Earlier physical evidence

- [V14 5G default dwell](../checkpoints/MZ600_V14_2012_ESCAN_EVENT69_PARTIAL_BSS109_PASS_TERMINAL_MISSING_2026-10-26.md)
- [V15 2G real terminal](../checkpoints/MZ600_V15_2012_OEM_2G_ESCAN_EVENT69_TERMINAL_SUCCESS_179MS_PHYSICAL_PASS_2026-10-26.md)
- [V16 5G 500ms no terminal](../checkpoints/MZ600_V16_2012_5GHZ_ESCAN_PASSIVE_500MS_MORE_PARTIALS_NO_TERMINAL_PHYSICAL_2026-10-27.md)
