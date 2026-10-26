# MZ600 BCM4329 ISCAN action-specific payload sizing and Linux 7 cancellation audit

**Date:** 2026-10-26. **Read-only historical source comparison and offline code tests.** No firmware commands, Xoom scan, device reboot, module build, or flashing. Do not confuse host-generated packet lengths with verified HRI39 firmware acceptance.

## Source-verified correction to proposed "all three actions always send 76 bytes"

The exact 2.6.39 Broadcom cfg80211-era implementation [`wl_cfg80211.c`](https://android.googlesource.com/kernel/common/+/refs/heads/deprecated/linux-bcm43xx-2.6.39/drivers/net/wireless/bcmdhd/wl_cfg80211.c), also available as [source mirror](https://github.com/lvchaqiu/meizu-mx-kernel/blob/7098c1021763c824d7198b156966d3fa040ec162/drivers/net/wireless/bcmdhd/wl_cfg80211.c), implements `wl_run_iscan(struct wl_iscan_ctrl *iscan, struct cfg80211_scan_request *request, u16 action)`:

- Initial `params_size = WL_SCAN_PARAMS_FIXED_SIZE + offsetof(wl_iscan_params_t, params) = 64 + 8 = 72 bytes`.
- **Only when `request != NULL`**, add `2 * (n_channels + (n_channels % 2)) + 36 * n_ssids` bytes for the aligned channel list and SSID list.
- Single-channel, zero-SSID **START with request**: 72+4=**76 bytes**.
- On **PARTIAL**, `wl_iscan_inprogress` calls `wl_run_iscan(iscan, NULL, WL_SCAN_ACTION_CONTINUE)`: no request -> **72 bytes**, and the host routine builds a fresh, zero-initialized allocation and executes `wl_scan_prep(&params->params, NULL)`. Thus it does *not* resend the original channel list or preserve the original per-request dwell/probe settings. Do not repeat the external claim that 76B and identical params on CONTINUE are source-mandated.
- Older [Froyo BCM4329 `wl_iw.c`](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/wl/sys/wl_iw.c) likewise starts with 72-byte base length when no extra SSID is supplied and calls `wl_iw_iscan(iscan, NULL, WL_SCAN_ACTION_CONTINUE)`; its exact normal START parameters differ from the one-channel cfg80211 generation.
- **ABORT=3 is declared in `wlioctl.h`, but the reviewed Broadcom 2.6.39 `wl_cfg80211.c` contains no invocation of `wl_run_iscan(..., WL_SCAN_ACTION_ABORT)`.** Neither a 72B nor a 76B ABORT packet nor precise firmware behavior on abort has been established for Motorola HRI39 4.218.248.20. The claim that the vendor implementation "verifies uniform 76B START/CONTINUE/ABORT" is false. Do not assume an ABORT ioctl automatically releases hardware, channel dwell, or scan cache.
- Neither natural `sizeof(wl_iscan_params_t)=76` (includes one u16 channel plus alignment) nor fixed 72B header+base is a universal firmware requirement for all actions. The `brcmf_fil_iovar_data_set()` helper automatically constructs `"iscan\\0"` plus passed bytes, so total control command data before SDIO/CDC framing is **82B for 76B parameters** or **78B for 72B parameters**.

For production passive 5GHz NO_IR scanning, historical defaults `scan_type=0`, `nprobes=-1`, `active_time=-1` in `wl_scan_prep(NULL)` should not be copied blindly for a new design. Distinguish fields ignored by firmware on CONTINUE (possible) from fields that could affect scan legality (untested). Preserve stricter global passive `WLC_SET_PASSIVE_SCAN=1`, no active probe path, and fail closed on HRI39-specific uncertainty.

## Cleanup and cfg80211 race corrections

The proposed external snippet was incorrect:
```c
struct cfg80211_inform_bss_info info = {};
cfg80211_scan_done(req, &info);
```
- The pinned modern Linux7 `brcmfmac/cfg80211.c` uses **`struct cfg80211_scan_info info = {.aborted = aborted}; cfg80211_scan_done(req, &info)`**. `cfg80211_inform_bss_info` is for informing BSS records, not `cfg80211_scan_done`.
- For cancel/timeout/firmware-ABORT, **`info.aborted = true`**, not an all-zero struct that claims successful scan.
- The actual request owner is **`cfg->scan_request`**; no source-verified `cfg_lock` or `ifp->vif->scan_request` scan-state lock exists in the pinned original baseline. Adding a lock requires defining ownership, lock order and existing event/timeout/work interaction explicitly.
- Simply detach request pointer under an invented spinlock, unlock, send iscan ABORT, then signal cfg80211 is NOT enough: worker may be running, stale IOVAR could outlive interface, the normal timer can still fire, next scan may start before old abort, and the default `brcmf_notify_escan_complete(...fw_abort=true)` sends `BRCMF_C_SCAN` rather than iscan action.
- The historical 2.6.39 `wl_cfg80211.c` uses `wl_term_iscan`, a worker/thread, timers and `dhd_os_spin_lock`; it does **not** contain `cancel_delayed_work_sync` nor a demonstrated standardized 76-byte iscan ABORT send. Its successful path calls `wl_notify_iscan_complete(iscan,false)`, aborted path `wl_notify_iscan_complete(iscan,true)`. Those are historical concurrency patterns, not Linux7-ready drop-in code.

Required for any later patch: operation-type and generation ownership under a real lock; stop new work and detach request once; synchronously quiesce worker outside locks that it needs; serialize bus IOVARs against scan START and module teardown; perform only safe best-effort firmware abort while interface/bus remains valid; deactivate the legacy-mode timeout/event processing; call `cfg80211_scan_done(req,&(struct cfg80211_scan_info){.aborted = true/false})` **exactly once**, without later freed-pointer access. Keep existing generic escan path unchanged.

## Offline regression proof

`tools/forensics/test_bcm4329_iscan_abi_and_transitions.py` updated with source-based host-encoded lengths and guard tests:
- Original 7 test groups still check legacy `0x1B24` 5GHz/20MHz channel36, natural 76-byte struct, field offsets, passive flags, 16B results header, terminal status state mapping.
- Added tests that historical `wl_run_iscan(request=NULL)` builds **72B**, a one-channel zero-SSID request builds **76B**, 2-channel=76B, 3-channel=80B, one-channel+SSID=112B; CONTINUE base bytes are a 72B zero-channel header; ABORT length explicitly marked unproven by that source.
- Desktop WSL after bugfix: **Ran 10 tests ... OK**, repository checker 603 entries, errors=0 (before this doc added). Tests inspect an ABI/source-level model; no physical firmware acceptance claim.

## Next action

Offline target ARMv7 C `BUILD_BUG_ON` for struct offset/length/chanspec and simulated status/error/abort races; separately trace if HRI39 original firmware expects a particular iscan ABORT representation from a broader historical host/firmware build. Only then discuss staging a unique guarded owner-operated passive-only 5180MHz test. The existing old `WLC_SCAN=50` / `WLC_SCAN_RESULTS=51` physical PASS and ~10s fallback remains untouched.
