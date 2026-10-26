# Broadcom 2010 internal scan-engine source discovery — event26 generation investigation (2026-10-26)

## Answer to source availability question

**The exact BCM4329 HRI39 `4.218.248.20` on-chip firmware source is NOT verified publicly found** as of this search. Android AOSP distributed compiled `fw_bcm4329.bin` family variants separately from the open host `dhd` / `wl_iw.c` sources. AOSP's accompanying firmware license expressly describes binary distribution without grants for corresponding human-readable source. `linux-firmware` contains BCM4329 binaries, not chip firmware build sources.

**Major new and more promising lead:** contemporaneous Broadcom internal **WLAN MAC scan-engine source `wlc_scan.c`**, dated `2010-12-23`, does exist in public router/vendor SDK mirrors. It is not just the Android/Linux host scan handler. It exposes the **internal scan timer/channel state machine, scan completion callback, and `WLC_E_SCAN_COMPLETE` emission site**:
- [Broadcom `wlc_scan.c`, revision 1.192.2.32, 2010-12-23](https://github.com/luminais/ecos_http/blob/9cb66a1085d8519f536b493aedb4ea8b477972aa/bcm/src/wl/sys/wlc_scan.c), roughly 2897 lines.
- [Similar period BCM4323 `wlc_scan.c`](https://github.com/yangfl/bcm4323/blob/ef9ddb3744087594f39e19001ee4076851dea363/bcm/wl/sys/wlc_scan.c).
- [Later internal scan engine, 2012, `wlc_scan.c`](https://github.com/djdisodo/broadcom-wl-src/blob/efe6c331679577080a3167e8fa93a7fcb3c4b7ec/src/wl/sys/wlc_scan.c), around 3101 lines.
- [Contemporary Android host driver](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/wl/sys/wl_iw.c) and [AOSP BCM4329 firmware archive](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/gingerbread-mr4-release/bcm4329/firmware/).
- Other direct firmware projects researched: `seemoo-lab/nexmon` supports related Broadcom parts such as BCM4330 but does not list BCM4329; `openfwwf` targets old softmac `b43` core revisions, not a BCM4329 fullmac firmware drop; `bcmon` released patched BCM4329 binaries, not buildable full source.

## Newly proven historical implementation structure

In the Dec 23 2010 `wlc_scan.c`, the scan engine:
1. Clears old BSS results, sets channel index, marks `in_progress=TRUE`, and starts a firmware-side scan timer/state-machine `wlc_scantimer()`.
2. Iterates channels and per-channel passive/active passes via `wlc_scan_do_pass()`, reading beacons/scan responses into internal results.
3. On normal scan wrap-up, returns to home channel, marks `in_progress=FALSE`, restores radio wake/power state, then invokes the configured `wlc_scan_callback(..., WLC_E_STATUS_SUCCESS)`. That callback invokes a supplied function pointer `cb` if non-NULL; its downstream implementation needs tracing.
4. Crucial: an additional direct `wlc_bss_mac_event(..., WLC_E_SCAN_COMPLETE, ..., WLC_E_STATUS_SUCCESS,...)` appears **only under `#if defined(MACOSX)`** after the normal-success cleanup. The later 2012 source retained the same conditional placement. For `DEVICEREMOVED` and abort status, `wlc_bss_mac_event(... WLC_E_SCAN_COMPLETE ... ABORT)` appears outside the `MACOSX` guard.
5. The internal callback `wlc_scan_callback` (at approximately 1861–1875 in 2010 source) does **not itself** send a firmware event; it invokes `cb(cb_arg, status, cfg)`. **Do not assume the success event is never sent by non-Mac firmware**: the callback target could emit the same event or a different event, depending on build and caller.

## What this means for our Xoom

The absence of event26 observed in v9–v12b is now consistent with at least one documented contemporaneous Broadcom design in which a successful scan need not result in the **direct** event26 call; `event_msgs` bit26 enabled only requests a notification *if* firmware generates one. The v12b classifier counters all zero cannot prove missing firmware generation, as some SDIO/BDC paths precede it. Firmware scan completion remains real (HRI39 2011 results ioctl51, v108, 3 BSS) but the exact event behavior remains unknown.

**Highly recommended next work:**
- Identify `cb` function passed to the scan engine for old `WLC_SCAN` ioctl50, especially `wlc_custom_scan_complete` or DHD dongle callback, and whether it posts `WLC_E_SCAN_COMPLETE` on BCM4329 firmware builds. Compare DONGLEBUILD/BCMDONGLEHOST/STA/MACOSX flags (not interchangeable).
- Look in contemporaneous Broadcom `wlc.c`, `wlc_event.c`, scan callback dispatch and dongle packaging; don't conflate GPL host driver, router host MAC implementation, and proprietary BCM4329 on-chip firmware.
- Cross-check original Motorola HRI39 custom firmware behavior without violating original RF/regulatory safety constraints. Do not use the presence/absence of BSS records as definitive scan-done indicator.
- Preserve current v12b physical PASS, no kernel/module persistence and no v12b rerun; only proceed to a new physical experiment if a precise unresolved software question remains.

**Source rights:** The mirrored Broadcom file carries proprietary restrictions. Link to source; do not copy the proprietary source into this repo. This note is independently authored high-level engineering analysis, not a redistribution of Broadcom code.
