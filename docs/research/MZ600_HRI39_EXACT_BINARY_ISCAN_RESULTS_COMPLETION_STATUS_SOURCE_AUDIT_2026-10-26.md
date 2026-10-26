# Xoom MZ600: Exact HRI39 binary iovar audit + explicit iscan completion status (2026-10-26)

**RESEARCH ONLY; NO new device scan, driver build, firmware modification, COM9 run or persistent installation.** Owner-supplied external Google analysis prompted verification of its exact firmware claims. This note identifies a better historical protocol to investigate, without committing to changing a working scan.

## Definitive binary identity and comparisons

Private Raspberry Pi OEM reference path (not to be published or copied into Git):
`/home/ps2/xoom-phase1/private/oem-reference-20261021/analysis/oem-driver-study/MZ600_HRI39-fw_bcm4329.bin`

Read-only on Pi:
- 261317 bytes; SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`, matching earlier HRI39/HRI66 artifact checkpoint.
- Embedded exact firmware banner **`Version: 4.218.248.20 CRC: 9cb6f3f Date: Wed 2011-01-12 13:49:01 PST`**.
- At offset 185710: literal `event_msgs`; 185831/185837: `iscan` (overlap with `iscanresults`); **no case-insensitive ASCII occurrence of `escan`** in a byte search of this exact binary.
- Static view of iovar-name table from `od` confirms adjacent names `event_msgs`, `scanresults_minrssi`, `iscan`, `iscanresults`. This proves names are present, **not** that all invocation parameter variants are understood/validated.
- Comparison only, **not HRI39**: Desktop private `firmware-reference-v08-OEM-MZ600-private/brcm/brcmfmac4329-sdio.bin` is 264140 bytes SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`; its *embedded* banner is `4.218.248.44` dated `2012-05-25` and its iovar table contains both `iscan` and `escan`. Do **not** label this image as original 2011 Motorola HRI39.

## An escan compatibility failure was already physically tested

Read [earlier exact HRI39 enhanced scan test](../checkpoints/MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md) before suggesting another `escan` experiment:
- guarded radio boot under HRI39 4.218.248.20 original matched US/69 NVRAM; `wlan0` and NO_IR 5GHz channels PASS;
- `iw dev wlan0 scan freq 5180 5200 5220 5240 passive` attempted modern `brcmf_run_escan`, firmware `escan` iovar returned `-EBADE/-52`, propagated by `brcmf_cfg80211_scan`; no successful scan on this path;
- later HRI39 legacy firmware `WLC_SCAN=50` + `WLC_SCAN_RESULTS=51` single-channel 5180MHz PASS physically; read v7R/v10/v11/v12a/v12b checkpoints.
Thus modern `escan` request is already known not to work **in tested form**. Lack of ASCII `escan` and newer firmware's presence strengthen inference about unsupported old command, but no absolute universal 'never supported' theorem.

## Alternative original protocol with *explicit terminal state*: iscan

The historical Broadcom Android `wl_iw.c`, e.g.
[Google Android Froyo BCM4329 driver source](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/wl/sys/wl_iw.c)
under `WL_IW_USE_ISCAN`, uses:
- `iscan` iovar for incremental scan requests and `WL_SCAN_ACTION_CONTINUE` when partial;
- `iscanresults` iovar GET yielding `wl_iscan_results_t` comprising a **u32 `status` followed by a `wl_scan_results_t` BSS list**, not the same response structure as the known legacy ioctl51 alone;
- Broadcom header `wlioctl.h` defines explicit status `WL_SCAN_RESULTS_SUCCESS=0`, `PARTIAL=1`, `PENDING=2`, `ABORTED=3`. (There can be other error codes such as NO_MEM in variants.)
- `_iscan_sysioc_thread` watches status: PARTIAL -> `WL_SCAN_ACTION_CONTINUE` and next timer, PENDING -> next timer, SUCCESS -> stop and send host scan-completion notification, ABORTED -> teardown/notify.
This is **source evidence of a genuine completion predicate**, unlike `WLC_SCAN_RESULTS=51 rc0 count3`. However it is **specific to an iscan-started operation**; cannot silently query `iscanresults` after a WLC_SCAN scan and treat the status as authoritative without determining the firmware's cross-protocol behavior. No iscan result has been physically tested on the MZ600.

Direct supporting protocol references: [Broadcom `wl_iw.c` Android Froyo](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/wl/sys/wl_iw.c), [wlioctl.h status values and struct](https://github.com/Jackysi/advancedtomato/blob/67273b06fc58fd744c472ff6f6c0d90e7d15001d/release/src/include/wlioctl.h).

## Corrections to unsolicited precise claims in Google text

- The supplied `wlc_scan_legacy_cb`, `wlc_scan_switch_error`, `wlc_send_setup_string_event`, `wlc_send_qevent`, and `DONGLEBUILD_SEND_SCAN_COMPLETE_EVENT` were **not confirmed** in reviewed historical source; Google's claims that *the exact 4.218.248.20 binary* registers/excludes them are unsupported, not reverse-engineered evidence.
- The publicly mirrored *related* 2010 Broadcom `wlc_scan.c` defines `wlc_scan(...,scancb_fn_t fn, ...)`, a state machine `wlc_scantimer`, and `wlc_scan_callback` that calls a supplied callback. It does **not** expose the Google-proposed `wlc_scan_start(...,wlc_scan_legacy_cb,...)` call or top-level `case WLC_SCAN` ioctl50 demux within that `wlc_scan_ioctl` (which handles scan module controls). A direct successful event26 call is guarded by `MACOSX`, but other callback targets can generate events. Do not assert exact HRI39 event26 impossibility.
- `WLC_SCAN_RESULTS=51` success and valid 3 BSS **do not logically prove** firmware's last channel dwell/scan-terminal state was reached; interim cached results may exist.
- The BCDC/SDPCM RX header format is not dictated by whether the request was legacy scan or ESCAN; a packet that fails `brcmf_rx_hdrpull` requires actual transport/header evidence, not an inference from scan mode.
- Do **not** call `cfg80211_scan_done` merely because `brcmf_fil_cmd_data_set(WLC_SCAN)` or `WLC_SCAN_RESULTS` returns success. Finish only upon a verified terminal predicate with race-safe ownership, abort/error transitions, worker execution, timeout fallback and exactly-once completion. Never use count>0 as a terminal predicate.
- Event26 firmware mask was physically ON in v12a and v12b; v12b event ingress counters all zero. Missing subscription is already excluded; a later raw event dump by itself is not likely to explain RX path before `brcmf_rx_hdrpull`.

## Recommended low-risk next research and experiment sequencing

1. Offline: compare exact HRI39 original host-side `WL_IW_USE_ISCAN` definitions and parameter structs. Audit `wl_iscan_params_t` version, passive scan bit, channel list, dwell controls and pause/continue semantics in contemporary headers, and ensure no mismatch with firmware HRI39. Verify on-chip `iscan` request expectations as far as reverse engineering allows.
2. Only then consider **a new dedicated single-channel NO_IR 5180MHz passive-only**, no-probe, bounded `iscan` GET/SET diagnostic module, with user authorization and per-device factory MAC, original FW/cal only in RAM, independent restore. Do not reuse previous one-shots.
3. If terminal status is verified on physical hardware, design separate **iscan-based** old-firmware lifecycle under existing cfg80211 ownership with bounded delayed work and conservative fallback; maintain current WLC_SCAN path as known-good until validated. Keep generic firmware/BT and other variants untouched.
4. Until that proof, the validated fallback remains original HRI39 ioctl50/51 plus conservative ~10s watchdog and v108 cfg80211 3-BSS validation; no fast scan completion claim.

This source-driven hypothesis is **a higher-value next target** than instrumenting another downstream event26 function, but is not yet proof of live HRI39 iscan status behavior. All related private images and network identities stay off GitHub.
