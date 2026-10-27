# MZ600 V17: spare stock Xoom OEM Android live Wi-Fi scan observation

**Date:** 2026-10-27. **Status: owner has spare stock Xoom ready, host ADB discovery attempted, capture NOT yet performed.**

## Owner observation

Stock Xoom Wi-Fi network list populates network security details progressively while user scrolls. Hypothesis: 10s modern Linux brcmfmac ESCAN watchdog may interrupt a scan before firmware considers it complete; or hidden SSIDs / per-network information could prevent terminal emission.

Do not conflate UI detail rendering, repeated Android framework requests, passive beacon reception, firmware hardware scan completion, or the Linux ESCAN 10s fallback. On stock Android, security detail often depends on information elements in beacons/probe responses or framework processing, but a delayed list entry alone does not establish one continuous RF scan. Android may perform repeated scans or update caches/UI.

**Important physical counterpoint:** V16 one passive **single 5180MHz ch36** scan produced 7 Event69 PARTIALs in first ~414ms, then no firmware status0 or further PARTIALs for ~9.8 seconds, until 10.37s watchdog aborted. One requested channel at configured passive 500ms dwell ordinarily should not require 10s merely to discover every SSID. This observed silence favors a stalled state or missing completion, although isn't proof of root cause. Generic Android Settings scans may cover many channels and even transmit active probes; not apples-to-apples with strictly NO_IR channel36 test. If OEM truly takes over 10s for equivalent one-channel passive scan, that would challenge the current watchdog; don't extend blindly without evidence.

## Host connectivity checked

- Remote authorized Surface-Book-2 and Desktop are online.
- Stock Android reference Xoom **NOT enumerated by ADB on either host** at the time of check: both `adb devices -l` outputs were empty. Surface had Android Platform Tools available; Desktop exact same ADB executable also available.
- Surface still has unrelated `xoom-v068-bluez4-sdp-reconnect-check.py` PID 13444 for experimental COM9 — DO NOT interrupt it. Stock Android uses its own ADB USB device rather than experimental Linux COM9; keep device identities separate.
- No physical stock scan, root shell, network toggle, firmware modification or system change was performed.

## Read-only Surface capture tool staged

- [Surface owner-invoked PowerShell script](../../scripts/host/surface/observe-stock-xoom-oem-wifi-scan-readonly-20261027.ps1), checked for PowerShell parse errors (0). Private host copy at `C:\Users\olsen\xoom-linux-rom\captures\observe-stock-xoom-oem-wifi-scan-readonly-20261027.ps1`; SHA256 `b2b575d51e533621d15e89abb3c0a157a71ce14a0a5d50c8ed2ed9db682d6675`.
- Requires exactly one ADB device in `device` state, positively identifies Xoom/Motorola model vs experimental Debian kernel, prevents starting if none/other/ambiguous. Reads Android model/device/release/fingerprint/kernel.
- Saves before/after `dumpsys wifi`, live `adb logcat -v time`, post `dmesg` best effort in timestamped folder `C:\Users\olsen\xoom-linux-rom\captures\OEM-XOOM-WIFI-SCAN-READONLY-20261027`; raw network identifiers/logs remain private Surface ONLY.
- Owner manually opens Wi-Fi Settings and refreshes/scrolls; presses Enter in PowerShell to end capture; host stops only its own `adb logcat` process. It does **not** run `adb shell am` actions, toggle Wi-Fi, use root, or change device settings.
- Usage after USB connect and enabled USB debugging on *stock reference only*: `& 'C:\Users\olsen\xoom-linux-rom\captures\observe-stock-xoom-oem-wifi-scan-readonly-20261027.ps1'`. On old Android 3.x USB debugging typically lives in `Settings > Applications > Development`. If model cannot be positively identified, stop.

## What to interpret from OEM evidence

Look for actual timestamps of `SCAN_RESULTS_AVAILABLE_ACTION`, `SCAN_COMPLETE`, `WLC_E_SCAN_COMPLETE` Event26 or firmware ESCAN Event69 if exposed, and whether new scans re-start automatically between security-label refreshes. `dmesg` may be inaccessible without root; **do not claim firmware completion just because Android UI changes**. Identify exact model/build/driver/firmware (MZ600 vs MZ604/MZ602 differ) before direct comparisons. Build raw log privately and summarize with redactions. Only firmware terminal event or explicit iscanresults status would prove the underlying firmware scan completed; framework scan-results broadcasts are a weaker but still useful signal.

## Next test design if warranted

Use OEM timing and existing driver source to design a new, uniquely hashed RAM-only diagnostic. A promising noninvasive approach is to instrument per-BSS SSID_len=0, raw/decoded chanspec and control channel, IE boundary boolean, and event header ingress counters without logging actual SSID/BSSID. Do not rerun spent V14/V15/V16 and never fake cfg80211 successful completion from PARTIAL count.
