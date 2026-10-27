# V17 — Stock Xoom MZ604 Wi-Fi observation: results update, repeated scan requests, no captured firmware completion

**Date:** 2026-10-27. **Actual physical OEM Android observation and host-side analysis.** Captured read-only ADB logcat while owner operated Wi-Fi Settings on stock Motorola Xoom. Capture stopped cleanly with exit code 0 after owner said done. No Android root, firmware/USB/scan modification. Distinguish reference MZ604 Wi-Fi variant from experimental Debian MZ600 CDMA.

## Device and evidence

- OEM tablet: Motorola Xoom wingray (MZ604 family), Android 4.1.2 JZO54K, kernel 2.6.39.4-g4e32b94.
- ADB fixed on Surface by selecting signed Microsoft WinUSB for Motorola ADB MI_01 only; original Motorola driver exported for rollback, described in previous checkpoint.
- On Surface, read-only capture stored in private folder C:\Users\olsen\xoom-linux-rom\captures\OEM-XOOM-WIFI-SCAN-READONLY-20261027\20261027-033524. Files: private-device-identity.txt, private-wifi-before.txt, private-wifi-after.txt, private-live-logcat.txt, private-live-logcat-errors.txt, private-dmesg-after.txt. Private helper analyze-scan-private.py also in parent folder.
- Owner pressed done, Remote Desktop Commander interact_with_process sent newline to capture session PID 9088. Capture exited 0, saved after snapshot, no ongoing OEM logcat capture.
- Actual logcat lines: 2,936. Raw log and SSIDs/BSSIDs remain on Surface and were NOT uploaded to GitHub.

## Aggregate results from private before/after dumpsys wifi

| Measurement | Before | After |
|---|---:|---:|
| System UID1000 scan request/counter | 3 | 14 |
| Other UID10019 scan count | 2 | 2 |
| Total cached BSS rows | 31 | 34 |
| 2.4 GHz cached BSS rows | 16 | 16 |
| 5 GHz cached BSS rows | 15 | 18 |
| Cached BSS entries at 5180 MHz channel 36 | 1 | 1 |
| Wi-Fi enabled | Yes | Yes |
| Connected to AP | No | No |

These are BSS cache records, not necessarily unique SSIDs. The system scan counter +11 indicates scan requests/counter increments, NOT independently verified 11 successful RF scan completions. The cached results did change. A long Android settings list does NOT mean 31–34 networks share experimental Linux's single 5180 MHz channel.

## Log messages relevant to firmware scan completion

- At tablet time 10-27 07:32:00.600, wpa_supplicant logged: wlan0: Failed to initiate AP scan.
- At 07:32:34.730, wpa_supplicant logged CTRL-EVENT-TERMINATING; another supplicant PID started at about 07:32:38. This complicates using the spare as a healthy steady-state reference.
- Neither raw logcat nor the last-100-entry Wi-Fi state-machine ring snapshots showed a SCAN_RESULTS_EVENT or CTRL-EVENT-SCAN-RESULTS terminal record. This does NOT prove no scan succeeded; logging and ring retention may be incomplete.
- WifiStateMachine ring contained many what=147462 (0x24006). Historical AOSP WifiMonitor defines this as SUPPLICANT_STATE_CHANGE_EVENT, NOT scan result completion. what=147461 (0x24005) is SCAN_RESULTS_EVENT; none observed in two tail ring snapshots. The approximately 15-second spacing of what=147462 MUST NOT be interpreted as scan duration or recurrence.
- Historical AOSP reference: https://android.googlesource.com/platform/frameworks/base/+/fea9df6386d66089b004719f194625e159bb344a/wifi/java/android/net/wifi/WifiStateMachine.java and https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/tags/android-mainline-12.0.0_r122/service/java/com/android/server/wifi/WifiMonitor.java .
- Stock Android shell dmesg returned klogctl: Operation not permitted. There is NO direct captured firmware Event26, ESCAN Event69 terminal, or ISCAN terminal status.

## How to interpret user's original hypothesis

Owner noticed security descriptions fill in gradually while scrolling original Android Wi-Fi list and suggested Linux's 10s watchdog might be too short. The Android framework counted +11 system scan requests and its cache changed, which is consistent with repeated requests/cached-result rendering rather than one continuous prolonged RF scan. It does not prove timing of even one scan. Security annotations can appear after result discovery; a hidden SSID normally does not prevent a passive scanner from ending after its scheduled channel dwell.

On experimental MZ600 V16 using same May2012 4.218.248.44 firmware, all seven received 5GHz channel36 Event69 partial packets occurred within approximately 414ms under explicit passive_time=500ms, then there was a ~10s absence of further partial or terminal, followed by driver watchdog. V15 2GHz on same firmware completed genuinely with Event69 SUCCESS in 179ms. So no demonstrated evidence that Linux needs >10s to gather Wi-Fi security metadata; waiting longer might only delay recovery of stuck firmware state.

Spare wingray is a different variant, runs different host framework and possibly different firmware and board data. Its single ch36 cached BSS entry validates a local 5180MHz beacon is possible, but does not establish Linux test's same BSS channel metadata or hardware scan-complete status.

## Next work

1. Do not increase production ESCAN watchdog simply because Android UI is slow; no firmware scan-duration evidence supporting longer timeout.
2. Prioritize a new source-led, owner-controlled RAM-only Linux MZ600 diagnostic collecting privacy-safe Event69 PARTIAL metadata: BSS109 SSID_len zero/nonzero, raw and decoded BSS chanspec and ctl_ch, IE bounds valid boolean, Event69 ingress status counts, and timing. No SSID/BSSID/MAC/IE raw bytes in public results.
3. Compare low-level event ingress with cfg80211 terminal/aborted paths. Do not synthesize SUCCESS from PARTIAL counts. Continue reviewing Broadcom 2012-era ESCAN/ISCAN termination and nprobes/home_time fields.
4. Avoid reusing consumed V14, V15, or V16 scripts. Preserve all original firmware/NVRAM/module SHA, NO_IR-only scan restrictions and independent rollback.

## Status

OEM capture complete; read-only, no firmware modification, no direct firmware completion proof. This closes the current stock Xoom observation and preserves evidence for a later V17 experimental diagnostic.
