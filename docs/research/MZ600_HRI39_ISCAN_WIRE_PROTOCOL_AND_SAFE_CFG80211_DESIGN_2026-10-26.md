# MZ600 BCM4329 HRI39: historical ISCAN wire protocol and safe Linux 7 cfg80211 design (source-verified, untested on tablet)

**Date:** 2026-10-26. **Status: source audit only.** NO radio activity, firmware modification, module build or physical ISCAN test. This is NOT a production patch and does NOT supersede known-good WLC_SCAN(50)+WLC_SCAN_RESULTS(51) passive scan.

## Source audit and corrections to Google-generated diagram

Original Broadcom BCM4329 host `wl_iw.c` [2011-era source mirror](https://github.com/lvchaqiu/meizu-mx-kernel/blob/7098c1021763c824d7198b156966d3fa040ec162/drivers/net/wireless/bcm4329/wl_iw.c) and [protocol structs](https://github.com/lvchaqiu/meizu-mx-kernel/blob/7098c1021763c824d7198b156966d3fa040ec162/drivers/net/wireless/bcm4329/include/wlioctl.h) show:

1. **Start is `WLC_SET_VAR("iscan", struct wl_iscan_params {version=1, action=START(1), scan_duration=0, params=wl_scan_params_t...})`.** `wl_iw_iscan()` calls only the `iscan` iovar; `wl_iw_iscan_set_scan` calls START once. There is **NO second `WLC_SCAN=50`** after START for the incremental scan. Explicit `WLC_SCAN` in this source is a *separate* directed-scan fallback, not the incremental scan launch. Combining them could create overlapping incompatible state.
2. Poll `WLC_GET_VAR("iscanresults")`, supplying a `wl_iscan_results_t` request with `list.results.buflen` set to maximum response space in firmware endian. Response layout is **u32 status + u32 results.buflen + u32 results.version + u32 results.count + BSS record(s)**. The status has defined `SUCCESS=0`, `PARTIAL=1`, `PENDING=2`, `ABORTED=3`, `NO_MEM=4`. Reject undersized, overflowing, unsupported version, impossible count, wrong control channel, bad BSS lengths/IEs.
3. **`PARTIAL` requires `WL_SCAN_ACTION_CONTINUE=2` via SET `iscan`** after safely processing that batch, then a subsequent timer/poll. **`PENDING` requires poll again WITHOUT CONTINUE.** `SUCCESS` is an actual terminal predicate; on valid last batch deliver BSS and once-only `cfg80211_scan_done(aborted=false)`; ABORTED, malformed status or exceeded deadline mark aborted.
4. `ABORT=3` is a SET `iscan` control action for a formerly STARTed iscan session; cancellation/teardown must make best effort without leaking req/worker/timer or issuing asynchronous firmware commands after interface removal.
5. A historical *cfg80211* Broadcom implementation [`wl_cfg80211.c`](https://github.com/lvchaqiu/meizu-mx-kernel/blob/7098c1021763c824d7198b156966d3fa040ec162/drivers/net/wireless/bcmdhd/wl_cfg80211.c) reinforces exact behavior: `wl_do_iscan` sets `WLC_SET_PASSIVE_SCAN`, `wl_run_iscan(... START)`, timer; `wl_iscan_pending` reschedules only; `wl_iscan_inprogress` informs BSS then CONTINUE; `wl_iscan_done` publishes and notifies completion; `wl_iscan_aborted` marks aborted. **Do not copy older kernel concurrency patterns verbatim.**

## Wire details that must be respected before even a diagnostic SET

- From BCM4329 `wlioctl.h`: `wl_iscan_params_t { u32 version; u16 action; u16 scan_duration; wl_scan_params_t params; }`, `ISCAN_REQ_VERSION=1`, actions 1,2,3. `wl_scan_params_t` has `ssid[36], bssid[6], bss_type(u8), scan_type(u8), nprobes(s32), active_time(s32), passive_time(s32), home_time(s32), channel_num(s32), channel_list(u16[1])`; fixed scan-params size `64` bytes. Incremental fields add 8 bytes. One selected channel requires correct 4-byte alignment/padded channel-list allocation and exact firmware/chanspec encoding; use firmware channel-number + band 5G/BW20/CTL_SB_NONE conventions verified against earlier *working legacy* test, not a raw 5180 integer.
- **Passive-only enforced twice:** `WLC_SET_PASSIVE_SCAN=1` (matching original OEM host use) and per-request `scan_type=WL_SCANFLAGS_PASSIVE (0x01)`, `nprobes=0`, `active_time=0`, bounded `passive_time`. Historical default prep uses `scan_type=0` (active) and `nprobes=-1`: cannot copy it unchanged for an NO_IR channel! Restrict to firmware-supported 5180MHz channel36, regulator-enabled NO_IR, non-DFS, no directed SSID, no active/probe/association. Restore saved firmware global passive state on cleanup, with module/no-radio restored in owner script; adhere to BT/U4 shared power.
- For `PARTIAL`, continuation should include correct header/version/action and parameter length. Check contemporaneous host code's allocation/padding; zero-initialize all bytes and fail closed when a firmware version/length contract is unknown. For read status, bound advertised length and reject BSS v108 envelope errors; do not publish nearby BSSID or SSID in public logs.
- Unlike legacy ioctl51, `iscanresults`' u32 status **could** give an unambiguous firmware terminal predicate for an **iscan-STARTed scan only**. Presence of ASCII `iscan` and `iscanresults` in the exact verified 2011 HRI39 binary is necessary but not proof this new request works physically. The same HRI39 `escan` request already failed with `-EBADE/-52`. Do not rerun.

## Proposed separate, nonintrusive development stages

**Stage A (next)**: Source-only wire-ABI/guard study of one-channel `iscan` request and response; create small synthetic unit tests for endian/offset/padding/length/buffer/counter and state transitions `PENDING→PENDING→SUCCESS`, `PARTIAL→CONTINUE→SUCCESS`, `ABORTED`, malformed status, read errors, timeout, cancel, disconnect, suspend and device remove. Fail if passive/no-IR constraints cannot be represented safely.

**Stage B (owner-approved physical lab, only after A)**: New unique SHA-pinned original firmware/NVRAM RAM-only module, no flashing; strictly one passive 5180MHz channel36 START, response-only numeric status and result envelope, bounded polls/CONTINUE and original full cleanup with independent audit. Do **not** route results to cfg80211 early or change existing ~10s watchdog until successful controlled proof; no repeated v12b or ESCAN experiments.

**Stage C (conditionally, after proven terminal status)**: Narrow BCM4329/HRI39 quirk with:
- `cfg->scan_request` ownership protected by existing scan mutex and private generation ID,
- `delayed_work` polling within explicit deadline, serialized against stop/suspend/netdev teardown, no IOCTL in timer/atomic/IRQ context;
- strict firmware response parser, dedupe/publish via existing validated v108 BSS parser;
- partial/pending/success/aborted states, bounded retries and backoff, exactly-once scan completion, finish callback detached under ownership lock and dispatched outside lock; do not hold mutex across `cancel_delayed_work_sync()`;
- best-effort firmware ABORT on user teardown, no further SET/GET or accesses after interface invalid; avoid double completion with existing escan watchdog or event callbacks;
- no change to default modern generic firmware path, other Xoom variants or Bluetooth power behavior until regression qualified.

**CRITICAL**: Do not design a `brcmf_fil_cmd_data_set(WLC_SCAN)` wrapper that immediately completes cfg80211 on success or nonzero BSS. That signals request acceptance/available cached data, NOT terminal firmware state.

## Known evidence kept intact
- [HRI39 exact binary audit](MZ600_HRI39_EXACT_BINARY_ISCAN_RESULTS_COMPLETION_STATUS_SOURCE_AUDIT_2026-10-26.md), SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`.
- [Original firmware modern escan physically returns -52](../checkpoints/MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md).
- [v12a event26 firmware mask ON](../checkpoints/MZ600_V12A_EVENT26_FIRMWARE_EVENTMSGS_BIT26_READBACK_PHYSICAL_PASS_2026-10-26.md); [v12b event RX classifier source/staged](../checkpoints/MZ600_V12B_EVENT26_RX_GATE_OFFLINE_BUILD_PASS_SURFACE_ONESHOT_STAGED_2026-10-26.md).
