# MZ600 v12a — event26 firmware-mask readback source-only checkpoint

**2026-10-26. SOURCE / DESKTOP STATIC QA PASS ONLY. NOT BUILT, NOT FLASHED, NO NEW MZ600 RF TEST.** Latest physical outcome remains [v11 four-BSS cfg80211/iW PASS](MZ600_V11_HRI39_CFG80211_FOUR_BSS_CHANNEL36_PHYSICAL_PASS_2026-10-26.md), original firmware/module/cal restored and separately audited.

## Why the next experiment is a readback rather than a new completion handler

v11 reached firmware ioctl50 success, GET51 version108 four valid BSS records, cfg80211 publication of four and four entries in local iw. It still relies on the approximately ten-second modern escan timeout; observation-only event26 has not been seen, not proof it cannot occur. The exact Linux7 source review confirms:

- `fweh.h`: `BRCMF_E_SCAN_COMPLETE=26`, byte `26/8=3`, bit `26%8=2` (0x04). Native Broadcom handler registration is indexed by event code; an alternate vendor event map would require separate verification.
- `cfg80211.c`: the earlier v9 observer is registered in `brcmf_init_escan()`, which is called by `wl_init_priv()`; the real `fweh.c` event activation constructs a mask from registered handlers, then calls `brcmf_fil_iovar_data_set(ifp,"event_msgs",mask,len)`.
- A firmware `event_msgs` GET was **never physically read back** under HRI39. Absence of observer callbacks could mean no notification, an unset event bit, mapping/receive path failure, or timing/ownership errors.
- `brcmf_notify_escan_complete()` clears `cfg->scan_request` before `timer_delete_sync()`; that alone does not prove mutually exclusive event/timeout/abort processing or make an already queued timeout worker harmless. Additional lifecycle serialization is essential for a later completion patch.

## New exactly isolated source change

- [v12a builder](../../scripts/experiments/build-v064-bcm4329-legacy-event26-mask-readback-v12a-20261026.py), committed at `2093658a3f59bef5c3e77f3218563a121f5389ca`. Layers on [physically verified v11 builder](../../scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py) **without changing any existing scan/cfg80211/timeout implementation**.
- In the already narrow passive channel36 legacy code path, immediately before WLC_SCAN ioctl50, inspect registered handler and driver's requested event bit, GET the firmware `event_msgs` mask with bounded allocated length, and log only integers: `rc,len,registered,driver_bit,fw_bit,map`. Failure to read is diagnostic only; it does not block the previously verified scan. No event mask SET, no radio operation beyond the existing owner-selected scan, no network identifiers in new logs.
- [v12a source-only test](../../tools/forensics/test_bcm4329_v12a_mask_probe_source.py), committed at `d8b9c9436e0b995ce679187778877cbf2c291604`. Independently compares original Linux7 source -> v11 -> v12a and proves new delta consists solely of inserted read-only diagnostic lines. PASS, 42 lines added, no existing lines deleted/replaced, no completion, timer, firmware SET or scan command introduced.

## Actual offline checks on authorized DESKTOP-R16QJD4 / WSL

No kernel/module build requested or performed. Results read from completed processes (not just start acknowledgements):

| Check | Result |
| --- | --- |
| v12a source-only insertion and no-lifecycle-change test | **PASS** exit 0, 42 lines added |
| `tools/forensics/test_bcm4329_legacy_scan_contract.py` | **22/22 PASS**, exit 0 |
| `tools/forensics/test_bcm4329_legacy_bss108_contract.py` | **18/18 PASS**, exit 0 |
| `tools/check_repository.py` | **588 entries, zero errors**, exit 0 |
| `tools/forensics/check_bcm4329_patch_series_gates.py` | **PASS execution** exit 0, release `review_ready=false`, physical matrix incomplete |

The branch was fast-forward synced to Desktop with `git pull --ff-only`. This is *not* exact-ABI compilation, on-device readback, an event26 sighting, improved latency, or completed scan ownership.

## Interpretation of a future bounded owner-operated test

1. `registered=0` or `driver_bit=0`: audit the handler activation path and native/vendored event mapping before changing firmware or completing a scan.
2. `rc=0 driver_bit=1 fw_bit=1 map=0`: firmware mask accepts bit26; next observe raw numeric event ingress, dispatch, and timing. Bit set is **not proof of actual delivery**.
3. `rc=0 driver_bit=1 fw_bit=0`: firmware did not report the requested bit; separately investigate event_msgs GET/SET semantics/length and firmware masking before assuming unsupported event.
4. `rc != 0` or `map=1`: **inconclusive**, investigate iovar readback support or vendor event mapping; do not infer event26 unavailable.
5. If an authentic scan-complete event is later observed, implement completion with a single serialized scan owner, a work item to GET51/validate/inform, and exactly-once scan_done; keep terminal failure and abort distinct. If not, identify a *real* scan-finished firmware predicate before using bounded asynchronous polling. **GET51 count=0 is ambiguous; count>0 can also be partial.**

Every new physical test must use a **new unique one-shot marker**, exact-ABI checksum and source restoration, private COM9 logs with no public identities, legal single-channel passive NO_IR scan, owner-controlled execution and independent original-system rollback verification. Never rerun v11 marker. Do not flash p7/p8 or install a lab module persistently. Current p8 still contains original normal generic firmware/NVRAM/modules; that state is not modified by this milestone.

## v12 status and next action

**v12a source/probe STATIC PASS; exact-ABI build and real `event_msgs` measurement NOT DONE.** Next mechanical step, only if a new controlled experiment is warranted: review probe source and build under the known exact ARMv7 Linux7 ABI on Desktop; independently verify original source/module restored and checksum of RAM artifact; prepare separately guarded user-operated one-shot with rollback and postcheck, *not* repeat v11. Lifecycle integration is another logical patch after the evidence. No DCO, PR or upstream submission authorized.
