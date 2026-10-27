# MZ600 V18 — 10 parametric event-mask scans: terminal Event69 seen at ingress every time, but eight fail in scan handler

**2026-10-27 ACTUAL PHYSICAL RESULTS. Major milestone.** One ARM module, multiple masks; no rebuild between radio scans. All ten owner-authorized scans used RAM-only private May25 2012 BCM4329 firmware and the same MZ600/Linux7 kernel/installed calibration. All test and independent rollback receipts passed. All ten trial IDs CONSUMED: NEVER re-run one.

## Central observation (replaces prior firmware-terminal-missing theory)

Every one of ten V18 scans generated **exactly fifteen incoming Event69 status8 PARTIAL packets** (five each of datalen 556,512,600), followed by **one incoming Event69 status0 SUCCESS packet with datalen12, subscribed=1** at low-level brcmf_fweh_process_event. In all eight watchdog failures that firmware Event69 SUCCESS arrived ~9.5–9.8 seconds BEFORE the watchdog. On those eight the cfg80211 Event69 handler saw some PARTIAL packets but NEVER saw status0. The other two returned native scan_done aborted=0 within 676/805ms.

**Conclusion:** the firmware DOES send timely 5GHz scan completion. It is not accurate to say that the firmware never reports terminal SUCCESS. The actual terminal packet is disappearing somewhere between early Linux firmware-event ingress and cfg80211 handler dispatch. A likely area is the packet_len/datalen validation, allocation, queuing or event worker (NOT proven yet). The ingress log precedes all these checks, so ingress alone does not prove queue acceptance. Additional low-level instrumentation of exact drop branch and packet lengths is now much more valuable than changing dwell or watchdog.

## Ten tests / trial receipts

| Trial | Mask | Raw Event69 SUCCESS received? | cfg80211 SUCCESS? | iw elapsed ms | BSS | Poststate |
|---|---:|---|---|---:|---:|---|
| ab1-01-mask000 | 0 | yes | yes | 676 | 1 | PASS |
| ab1-02-mask127 | 127 | yes | no, watchdog | 10401 | 0 | PASS |
| ba1-01-mask127 | 127 | yes | no, watchdog | 10500 | 0 | PASS |
| ba1-02-mask000 | 0 | yes | yes | 805 | 2 | PASS |
| split1-01-mask003 | 3 | yes | no, watchdog | 10362 | 0 | PASS |
| split1-02-mask124 | 124 | yes | no, watchdog | 10447 | 0 | PASS |
| bitcheck1-01-mask000 | 0 | yes | no, watchdog | 10515 | 0 | PASS |
| bitcheck1-02-mask001 | 1 | yes | no, watchdog | 10200 | 0 | PASS |
| bitcheck1-03-mask000 | 0 | yes | no, watchdog | 10242 | 0 | PASS |
| bitcheck1-04-mask002 | 2 | yes | no, watchdog | 10492 | 0 | PASS |

**Do not overclaim mask effects:** Initial A/B plus reversal suggested event mask127 interference, with mask0 succeeding 2/2, but two later mask0 controls themselves timed out. Mask selection alone does NOT explain success/failure; hardware/host/runtime timing/state is another factor. No alternate event type handler received an event in any trial. Event69 status0 arrived at early ingress regardless of mask, including mask127.

## Parametric V18 implementation

- ARM .ko **347380 bytes, SHA256 65b805f5fe6ca1d28a14b5af6f1cf7251b490fbed9488a3a69d5f70eed02c229**, ABI 7.0.0-next-20260422+ ARMv7; firmware SHA256 5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834. Original cfg80211.c, fweh.c and brcmfmac.ko restored SHA-verified after offline compilation.
- [ARM source-restoring parameter builder](../../tools/forensics/build_mz600_v18_2012_5g_runtime_event_mask.py) adds validated read-only load-time module_param_cb mz600_extra_events=0..127. Event69 stays subscribed. Mask bit0=1 Event26 SCAN_COMPLETE, bit1=2 Event45 SCAN_CONFIRM_IND, bit2=4 Event35 RESET_COMPLETE, bit3=8 Event13 QUIET_START, bit4=16 Event40 RADIO, bit5=32 Event14 QUIET_END, bit6=64 Event63 CHANNEL_ADOPTED.
- [Guarded Xoom scan script](../../scripts/host/xoom/test-mz600-v18-parametric-event-mask-owner-20261027.sh) takes decimal mask and unique trial ID as bash positional args, verifies sysfs module parameter readback, strictly one 5GHz ch36 5180MHz NO_IR PASSIVE no-SSID/no-IE/no-association 500ms scan, catches rollback, unique /run marker. SHA256 48c917557330ef6fc75cd9040f2786095291786ef3eb670d29a7ef6c730507ca.
- [Reusable Surface serial owner suite](../../scripts/host/surface/mz600-v18-parametric-event-mask-ab-suite-20261027.py) takes --masks 0,127 and --series ab1 (1–8 unique masks per invocation), retains identical .ko across all tests; SHA-pinned firmware/module staged into /run once, independently verifies per-scan cleanup, stores separate JSON receipts and PRIVATE console logs per attempt, restores original loaded Wi-Fi modules/wpa_supplicant runtime afterwards. Surface script SHA256 ad98e6713f65e5cfc596a08fb193f3aeb1c75394e7977a53922b1e7887437d20.
- An abandoned static V18 mask-off builder had an offline anchor failure and never generated a physical diagnostic. Superseded by the parameterized builder.

## Runtime / private evidence

Surface PRIVATE folder: C:\Users\olsen\xoom-linux-rom\captures\MZ600-V18-2012-MASK-SWEEP-20261027\runs. Ten consumed .attempted markers, ten private.txt full console logs, ten JSON receipts. Do NOT publish SSIDs, BSSIDs, MACs or full raw transcript. Local safe-aggregate scripts analyze-v18-safe-private.py, analyze-v18-ingress-status-private.py, analyze-ingress-times-private.py validate the 15 PARTIAL+1 SUCCESS pattern and terminal-arrival-before-watchdog.

After each suite original FW/NVRAM/module SHA and absence of candidate overlay verified, all temporary Wi-Fi modules removed, original brcmfmac_wcc/brcmfmac/brcmutil reloaded, wlan0 DOWN, wpa_supplicant ACTIVE, BT stack loaded but hci0 DOWN and bluetooth.service INACTIVE. Transfer HTTP server closed and transient Desktop staging removed.

## Recommended next step

Audit drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c: brcmf_fweh_process_event ingresses and then checks invalid code, unsubscribed handler, datalen > BRCMF_DCMD_MAXLEN, datalen + sizeof(*event_packet) > packet_len, and kzalloc_flex allocation, before brcmf_fweh_queue_event. Worker dequeues, checks interface/bsscfg and dispatches event. Build a one-off BRANCH-SPECIFIC validation/queue/dequeue diagnostic printing numeric code/status, packet_len and drop reason, no network identifiers. Preserve runtime-load mask feature for all subsequent tests. Keep firmware and radio scan settings unchanged. No further event-mask-only scans are justified until these drops are understood.

**Key finding: 'firmware 5GHz never sends scan terminal' was falsified. In all ten tests, the hardware sent an on-time Event69 status0 into Linux ingress; cfg80211 lost it in eight.**
