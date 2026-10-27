# MZ600 V19 — root-cause milestone: Event69 terminal reaches worker but interface lookup fails

**Physical date 2026-10-27. Two mask0 passive ch36 5180MHz owner-authorized scans. Both watchdog-aborted, cleanup/restoration verified.** This is strong evidence that old BCM4329 2012 scan events are misrouted by current Linux7 event-header/interface-index handling.

## Physical root cause observed

V18 established EVERY scan produced one Event69 status0 SUCCESS at firmware-event ingress, but most never reached cfg80211 handler. V19 instrumented read-only validation/drop, allocation, admission, worker dequeue and handler dispatch, retaining user-selectable extra event mask (here always mask0). **Both V19 trials reproduced the failure at a specific branch:**

    MZ600_V19_FWEH_ADMIT code=69 status=0 datalen=12 pktlen=86
    MZ600_V19_FWEH_WORKER code=69 status=0 bsscfg=1
    MZ600_V19_FWEH_DISPATCH code=69 status=0 ifp=0 handler_rc=-22

Thus valid-length terminal event WAS allocated, enqueued, dequeued, and passed to generic handler dispatch, but the interface pointer could not be resolved for reported bsscfg=1. Core fweh.c brcmf_fweh_call_event_handler returns -EINVAL when ifp=NULL, so cfg80211 Event69 handler is not invoked. **Do not synthesize completion or lengthen watchdog.**

Both also had multiple raw Event69 PARTIAL packets dropped in worker before callback because bsscfg index was invalid **140** (>=BRCMF_MAX_IFS=16).

| Trial | Mask | Scan terminal at ingress | Worker bsscfg on terminal | ifp lookup | Event69 handler status0 | iw ms | rollback |
|---|---:|---|---:|---|---|---:|---|
| drop1-01-mask000 | 0 | YES | 1 | NULL, rc=-22 | NO; watchdog | 10454 | PASS |
| drop1-02-mask000 | 0 | YES | 1 | NULL, rc=-22 | NO; watchdog | 10149 | PASS |

Stage counts first: drop=5 invalid bsscfg, admitted=16, worker=11, dispatch=11. Second: drop=3 invalid bsscfg, admitted=13, worker=10, dispatch=10. Both handler saw 7 valid Event69 PARTIAL records but no terminal. The missing partials and terminal are not bad lengths or allocation failures in these trials; failures occurred in interface index lookup.

## Firmware event-header version lead (IMPORTANT)

- Local Linux7 brcmfmac/fweh.h defines a packed brcmf_event_msg_be with version, flags, event_type/status/reason/auth_type/datalen, address, ifname, **ifidx, bsscfgidx**. Worker validates raw bsscfgidx <16 and then resolves drvr->iflist[emsg.bsscfgidx]. For this MZ600, only primary WLAN0 is present.
- Historical Broadcom bcmevent.h explicitly defines **wl_event_msg_v1_t** ending immediately after ifname, WITHOUT ifidx/bsscfgidx; later **wl_event_msg_t VERSION 2 adds both**. Primary source https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/proto/bcmevent.h . This is a highly plausible source of garbage numeric bsscfg indices in old BCM4329 firmware event packets, but V19 did **not** print the actual emitted event version, so version1 on this physical MZ600 is a hypothesis, not yet established.
- Do NOT globally route all events to iflist0. A minimally scoped fix should apply to EVENT69 ESCAN_RESULT only, BCM4329 only, single primary interface and no secondary P2P/other iflist; only when raw bsscfg index invalid or does not resolve. Better version-specific behavior if observed header version supports it. Keep original firmware behavior for valid bsscfg indices and other chips.
- Next V20 should add event header version/ifidx/bsscfgidx NUMERIC logging and parameterized targeted interface fallback 0/1, maintaining identical module for comparison. Candidate guard must not affect any non-ESCAN event or multi-interface devices. A/B scan tests compare fallback disabled/enabled under mask0, same Bluetooth quiescent state and firmware/dwell/channel, with independent cleanup. If consistently successful only with fallback, extract a tiny production patch and remove all temporary logging/bitmask machinery.

## Offline and runtime reproducibility

New [V19 source-restoring builder](../../tools/forensics/build_mz600_v19_2012_5g_event_delivery_drop_audit.py) compiled temporary ARM module brcmfmac-2012-escan-event69-v19.ko 348836B SHA256 c6580ff0f2e354e2f8a885bdc76168417e16779b9f93d41db0614375ae67efbd; preserved V18 mask-param capability, 500ms passive single ch36 NO_IR without association, and printed numeric-only drop/queue/dispatch events (no SSID/BSSID/MAC). Source-restoring build verified original cfg80211.c SHA1cb2c6..., fweh.c SHA4a4c09..., original module SHA9fec47.... The first offline attempt failed on a nonmatching builder anchor and restored source; corrected and built PASS.

[Xoom test script](../../scripts/host/xoom/test-mz600-v19-event-drop-audit-mask-owner-20261027.sh) SHA 9c581f5cdb2da79338eaf26483f124777ac317abc9a09e5c4a20311d6f401beb. [Surface suite](../../scripts/host/surface/mz600-v19-event-drop-audit-suite-20261027.py) SHA 06faaabeea0792e65a39456c4cc534377f801c1ab4c7f94bfd32eacccf8557e0. Two unique consumed trial markers and private COM9 logs/JSON receipts at Surface C:\Users\olsen\xoom-linux-rom\captures\MZ600-V19-2012-EVENT-DROP-AUDIT-20261027\runs. Both independent poststate PASS; original brcmfmac modules and wpa service restored, wlan0 DOWN, hci0 DOWN service BT inactive; no persistent binary or NVRAM changes. Desktop temporary transfer server stopped and staging directory removed.

**No more event subscription scans justified until conditional interface-index handling is investigated.**
