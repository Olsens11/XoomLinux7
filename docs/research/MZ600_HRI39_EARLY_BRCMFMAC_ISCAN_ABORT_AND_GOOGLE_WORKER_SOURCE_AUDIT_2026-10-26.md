# Historical upstream brcmfmac ISCAN implementation, host ABORT format, and proposed-worker audit

Date: 2026-10-26. **Source/offline only: NO Xoom runtime, RF scan, firmware operation, build, flash or reboot.**

## Major source discovery

Early Linux brcm80211/brcmfmac **already contained an end-to-end ISCAN implementation** in wl_cfg80211.c. This is a stronger architectural reference for our Linux7 port than a newly invented loop:

- [Historical brcmfmac reference, Googlesource](https://cos.googlesource.com/third_party/kernel/+/23e44302b30ea15c538c3fcc4631c56358ae2feb/drivers/net/wireless/brcm80211/brcmfmac/wl_cfg80211.c)
- [Linux 3.4 historical brcmfmac mirror, GitHub](https://github.com/hi35xx/hi35xx-buildroot/blob/0f39440bd33ef4ef02120bd818901b60450c4fe6/linux/linux-3.4.y/drivers/net/wireless/brcm80211/brcmfmac/wl_cfg80211.c)

Relevant functions: brcmf_run_iscan, brcmf_do_iscan, brcmf_get_iscan_results, brcmf_iscan_pending, brcmf_iscan_inprogress, brcmf_iscan_done, brcmf_iscan_aborted, brcmf_abort_scanning / brcmf_term_iscan, and brcmf_cfg80211_iscan_handler. Result handler dispatches SUCCESS, PARTIAL, PENDING, ABORTED, and NO_MEM; PARTIAL explicitly invokes CONTINUE.

### Verified 72-byte host ABORT format

Historical brcmfmac calls **brcmf_run_iscan(iscan, &ssid, WL_SCAN_ACTION_ABORT)** after zeroing ssid. The helper sets params_size = BRCMF_SCAN_PARAMS_FIXED_SIZE + offsetof(brcmf_iscan_params_le, params_le) = 64+8 = **72 bytes**. It adds 36 bytes only for a nonempty SSID. Thus **one real Broadcom host implementation transmits 72 parameter bytes for ABORT**, with the iovar name automatically prefixed (78 bytes in the command buffer prior to CDC/SDIO framing). This corrects the earlier uncertainty caused by looking only at a different 2.6.39 bcmdhd implementation without an ABORT call. **This does not prove the exact Motorola HRI39 4.218.248.20 firmware accepts ABORT or releases all radio state.**

CONTINUE is also 72 bytes in these sources. Important: this early brcmfmac code's START is a **broadcast scan with channel_num=0**, also 72 bytes, and has legacy defaults scan_type=0 and nprobes=-1. It does NOT construct the user-required one-channel 76-byte passive CH36 START. Our original bcmdhd version with explicit request->n_channels shows how to represent one channel; the old brcmfmac source supplies the worker/control/abort architecture. Do not paste the all-channel or active-scan defaults into the new Linux7 integration.

### What source does *not* prove

Absence of an on-chip firmware parser source means that claiming CONTINUE completely ignores parameters, HRI39 stores all START fields in a particular struct, or that an action-3 72B packet resets hardware is **not proven**. Search for proposed function 'wlc_iscan_set' yielded no verified exact firmware implementation. Historic host behavior is evidence for expected ABI, not device acceptance.

## Errors in Google-supplied C worker (do not compile or deploy)

1. **Unverified locking/lifetimes:** cfg->scan_lock is not a defined initialized lock in our pinned Linux7 source. Reading cfg->scan_request under a proposed lock then unlocking and using req/ifp later does not pin their lifetimes across cancel, detach, suspend, and next-scan ownership. The raw cfg->pub->ifp[0] pointer can become stale.
2. **Infinite retry loop:** allocation failures, firmware GET errors and parse failures all fall through to unconditional 250ms reschedule, no bounded retries/deadline, no guaranteed terminal cleanup.
3. **Incorrect firmware GET preparation:** actual brcmf_get_iscan_results zeroes its input and sets nested results.buflen to the maximum receive space *before* GET_VAR("iscanresults"). Google's allocated zero buffer omits that required host preparation; synthetic offset is status:0, results.buflen:4, version:8, count:12. The exact brcmf_fil_iovar_data_get API copies the caller input into GET_VAR request.
4. **Unsafe response processing:** no envelope size, count, version108, per-BSS stride/IE validation or allowed-channel check; no parser error propagation, no dedupe, no robust result ownership across worker exit; CONTINUE firmware failure ignored. Use existing validated HRI39 BSS108 parsing, not struct reinterpretation on untrusted bytes.
5. **Incomplete cancellation:** no synchronized delayed work quiescence, operation-kind/generation gate to prevent stale callbacks, modern escan timeout conflict, serializing firmware ABORT vs next START, or bus/interface disappearance protection. Only pointer-equality when calling cfg80211_scan_done is insufficient for exactly-once ownership.
6. **Incorrect certainty:** 250ms is a proposed polling frequency, not proven HRI39 safe; 72B CONTINUE implies statefulness but NOT proof of complete param ignore. For ABORT, source shows host packet length, NOT actual Motorola firmware response.

## Next source-first work

Create a source-directed Linux7 narrow ISCAN design that reuses upstream historical concepts but owns cfg->scan_request, scan operation kind, unique generation, delayed work, timeout, cancellation and device teardown under a real lock. Validate architecture with offline concurrency/error-state tests and compile-time target-ARM ABI checks first. Enforce passive-only global setting and per-request flags, nprobes=0, active_time=0, original regulatory NO_IR channel36 5180MHz with legacy chanspec 0x1B24. Do not allow all-channel default or any active probe. No generic firmware changes or special treatment of wlan Event26 in this phase.

Only after offline verification may a new owner-approved single-channel passive-only original-HRI39 ISCAN experiment be considered. Current known-good WLC_SCAN 50 / RESULTS 51 and 10s fallback stays intact.

## Offline model

Added 2 source-based tests to tools/forensics/test_bcm4329_iscan_abi_and_transitions.py: historical early-brcmfmac 72-byte ABORT encoding (firmware acceptance unproven), and required synthetic nested GET request result capacity at byte 4. Test results should be checked in current desktop run.
## Additional concrete Linux7 GET_VAR buffer-size conflict

Read-only actual pinned Linux7 `brcmfmac/core.h` defines `BRCMF_DCMD_MAXLEN=8192`, with `drvr->proto_buf[BRCMF_DCMD_MAXLEN]`. In `fwil.c`, `brcmf_fil_iovar_data_get` calls `brcmf_create_iovar(name,data,len,proto_buf,sizeof(proto_buf))`, which copies the **name + NUL + full caller-provided len** and rejects when they do not fit. `"iscanresults"` is 12 characters plus NUL=13 bytes, thus `len=8192` cannot be used with this helper: **8192+13=8205 exceeds the proto_buf, and the helper returns -EPERM**, without sending a firmware GET. Within this helper's framing max is 8179 data bytes, but do not assume firmware accepts that maximal size. The original brcmfmac `brcmf_dev_iovar_getbuf` accepted *short input paramlen* and a *separate larger output buflen*, and initialized `results.buflen` before GET. A real new Linux7 helper must carefully implement equivalent bounded semantics or choose a smaller safe buffer, seed requested capacity, validate response, and prove under target compile/tests before hardware. Added offline regression check of name overhead.
