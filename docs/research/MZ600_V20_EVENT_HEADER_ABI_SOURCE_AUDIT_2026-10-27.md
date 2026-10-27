# MZ600 V20 — event-header ABI source audit and guarded experiment design (2026-10-27)

Status: SOURCE AUDIT ONLY. No V20 module built, no Xoom radio test, no production compatibility change.

## Verified prior physical evidence

V18: all ten passive ch36 scans delivered terminal Event69 status=0 at firmware-event ingress; most did not reach cfg80211 handler. V19: two trials delivered Event69 status=0 through packet validation, allocation, queue and worker, but worker/dispatch showed bsscfgidx=1, ifp=NULL, -EINVAL; some partial results carried bsscfgidx=140 and failed the BRCMF_MAX_IFS=16 guard. Restoration passed. These are the physical findings; header version was NOT captured.

## Source audit completed

1. Broadcom historical `bcmevent.h` (https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/proto/bcmevent.h) defines **wl_event_msg_v1_t** through the 16-byte `ifname` with NO `ifidx` or `bsscfgidx`; the later `wl_event_msg_t` adds both one-byte fields. Version 2 is explicitly defined as `BCM_EVENT_MSG_VERSION`. In the packed protocol, v1 event message is 46 bytes and v2 48 bytes (inferred from defined field widths; confirm actual compiler packing).
2. Current *actual Desktop Linux7 source* `drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c`: `brcmf_fweh_process_event()` treats `data = &event_packet[1]` and validates `datalen + sizeof(*event_packet) <= packet_len`; it then stores the full modern event-message struct into the queue. `brcmf_fweh_event_worker()` checks `event->emsg.bsscfgidx >= BRCMF_MAX_IFS` **before converting emsg.version**, uses raw index to select `drvr->iflist[emsg.bsscfgidx]` (except TDLS), then calls `brcmf_fweh_call_event_handler()`. There is no header-version-specific index handling in this path.
3. Consequently a real v1 event would make the two optional interface-index bytes unavailable / potentially interpreted as adjacent data. However **this is NOT proven to be the physical cause**: V19 did not record version; a v1 frame may also fail modern length validation or cause a 2-byte payload offset, depending on actual framing. V19 admitted the terminal; thus validate frame length/offset and prefix before making any inference from index 1 or 140.
4. Desktop repository was observed clean on branch `wip/clean-wifi-bt-usb-20261025` during this read. No kernel-source files were changed.

## Required V20 diagnostic gates

- Print numeric `be16_to_cpu(event_packet->msg.version)`, raw index bytes only if within validated received frame, event code/status, `packet_len`, `datalen`, expected v1/v2 minimum lengths and exactly which interface objects exist. Do not print SSIDs/MAC addresses or raw IEs.
- For **version=1**, first prove the physical packet's actual field/payload boundary before using it; the current `&event_packet[1]` offset assumes v2. Never fix only bsscfg lookup if the payload starts two bytes earlier.
- Keep V18 `mz600_extra_events` 0..127 param; for comparisons select 0. Retain V19 validation/queue/worker logging and original NO_IR 5180 ch36 passive 500ms script.
- Build a **separate default-off** `mz600_legacy_escan_if_fallback=0/1` test switch, but enable remapping only when version, packet layout, BCM4329 chip, Event69, valid primary wlan interface, sole-if topology and missing index prove eligibility. Version1 handling must be length-safe, must preserve correctly aligned payload, and must not rewrite valid mappings. If the emitted version is 2, investigate why indices are inconsistent rather than claiming v1.
- A/B with the SAME exact ARM module and new unique attempts; verify each cleanup independently. Compare actual cfg80211 `scan_done aborted=0`, firmware terminal, partial BSS counts and userspace iw results—not iw exit status alone.
- Do NOT touch boot partitions, original generic FW/NVRAM/module, shared BT, regulatory flags, watchdog duration or persistent files. No V20 radio experiment has run yet.

## Important unresolved question

V19 Event69 terminal showed `pktlen=86` and `datalen=12`. Compute the exact full Ethernet + Broadcom vendor header + versioned event-message offsets from actual local types before interpreting this difference. `pktlen - datalen` alone is insufficient to identify protocol version because of framing/padding and may not match unadjusted wire payload boundaries.

Primary continuity references: `docs/handoffs/MZ600_XOOMLINUX7_V19_TO_V20_FULL_ENGINEERING_HANDOFF_2026-10-27.md`; `docs/checkpoints/MZ600_V19_EVENT69_WORKER_PRIMARY_IF_LOOKUP_FAIL_PHYSICAL_2026-10-27.md`. This is a SOURCE-ONLY V20 checkpoint, not a completed fix.

## Mandatory configuration-versus-patch necessity gate (owner decision, 2026-10-27)

Before promoting the V20 brcmfmac code to any integration patch, establish which layer is actually misconfigured or incompatible. A successful lab fallback is **not** proof a production code change is necessary.

1. **Enumerate existing controls** from this exact kernel source and 2012 firmware-era OEM driver documentation: event mask/subscriptions and mappings, event-header version negotiation (if any), firmware feature/capability selection, scan protocol version, interface creation and bsscfg index mapping, firmware/NVRAM alternatives, device-tree/board wiring, and any supported module parameters. State explicitly whether each is runtime configurable, probe-time setup or hardcoded code. Never invent an iovar or assume the event mask sets header version.
2. **Measure read-only reality first:** raw event.version, length/offset and raw ifidx/bsscfgidx; actual interfaces installed in drvr->iflist and their bsscfg mappings; event-map selection; firmware revision and scan protocol. Keep numeric privacy-safe logs and guard older header bounds. Differentiate a valid version2 index with interface lifecycle timing from a true version1 layout mismatch.
3. **Test the simplest supported configuration-only correction**, if a real documented control is found. Preserve the usual NO_IR, firmware hashes, rollback and single-variable A/B; configuration changes must not override regulatory rules, factory MAC/NVRAM or shared-chip GPIO ownership.
4. **Only if supported configuration cannot correct a confirmed incompatibility**, develop a minimal version-aware general driver patch. If the correct change belongs in DT/MMC/pwrseq/firmware selection instead, place it in the appropriate logical patch track; don't incorrectly force everything into brcmfmac.
5. **Evidence for conclusion:** source reference and exact existing control(s) checked, physical firmware observation, isolated comparison, cross-firmware regression, retained earlier trial evidence, negative findings and which assumptions remain unproven. Classify final decision as CONFIGURATION SUFFICIENT / DRIVER PATCH REQUIRED / OTHER-SUBSYSTEM PATCH REQUIRED / UNRESOLVED. Until then: **UNRESOLVED**.

Current source-level evidence: event-mask changes only choose subscribed event codes, not demonstrated header versions; V18 mask0 sometimes succeeded and sometimes failed, so masks alone are not a proven solution. Existing fweh.c uses event-header indices directly, and V19 proved a NULL lookup; the actual firmware event-header version remains unknown. The configuration necessity gate is independent from whether a laboratory fallback can turn a scan green.
