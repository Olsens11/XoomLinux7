# MZ600 V26b — NO_IR laboratory gate removed; second generation reaches firmware (PHYSICAL PARTIAL PASS)

**Date:** 2026-10-27. **Status:** precise negative/positive evidence from the real MZ600 Linux 7 BCM4329, no permanent system change. Source-only V26b candidate, **not** a production/upstream patch, and no normal network association has been attempted yet.

## Why the V25 second scan was rejected

V25 [preceding detailed V24 checkpoint](MZ600_V24_PER_SCAN_GENERATION_PAIRED_MODULE_LAB_FINDINGS_2026-10-27.md) and private V25 read-only dmesg measured two requests for **one 5180 MHz channel 36, n_ssids=0, IE=0, not busy**. First channel had `IEEE80211_CHAN_NO_IR`; after the successful scan the second request's channel flags were `0x801b0`, **NO_IR absent**, neither DISABLED nor RADAR. Old **lab-only** `brcmf_cfg80211_scan` guard returned `-EPERM` before scan generation. This is not proof a regulatory requirement was violated: Linux `net/wireless/scan.c` reports found BSS via `regulatory_hint_found_beacon` and `net/wireless/reg.c` `handle_reg_beacon` can legitimately clear `IEEE80211_CHAN_NO_IR` under world-roaming beacon-hint policy when allowed. No manual channel flag changes are required.

**Owner design decision:** do not keep unnecessary restrictions just because they once simplified a diagnostic. The final, normally usable driver should use cfg80211/regulatory policy, **not a permanent no-IR-only, fixed-channel36 or forced-passive lab gate**. Do not force-clear regulatory flags; preserve channel restrictions and proper permitted operating modes. Do not touch chip firmware to accomplish this.

## V26b code and artifacts

The single authoritative source-restoring lab builder is [`tools/forensics/build_mz600_v26_transitional_passive_scan.py`](../../tools/forensics/build_mz600_v26_transitional_passive_scan.py), added in `45b2708`, refined in `33267bd`. It derives the exact V25 source and removes **only** `!(ch->flags & IEEE80211_CHAN_NO_IR)` from the transient lab request guard; no channel flags or chip settings changed. The ordinary disabled/radar rejection, channel36 single-channel n_ssids0/IE0 constraint and passive 500ms dwell were retained **only to isolate this one A/B test** and must be removed from production. The log string `MZ600_V26_SCAN_GATE_PASS ... no_ir=1` was inherited unchanged and **is not a measurement of NO_IR**; do not treat it as evidence of flag state.

- Exact ABI V26b ARM core module: `brcmfmac-2012-escan-regstate-v26.ko`, **353304 bytes**, SHA256 `296a2408863bcefb8d0216d23f76aa1e63308755b8ebf8df617bb359ebb8536a`.
- Matched `brcmfmac-wcc-matched-v26.ko`, **5892 bytes**, SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`. Guarded temporary RAM bind onto the installed WCC autoload path avoids the proven module-symbol CRC race; original installed WCC SHA `31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80` restored.
- 2012 original candidate BCM4329 FW SHA `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` staged in RAM only. Installed FW SHA `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, calibration NVRAM SHA `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb` unchanged.
- Staged using [canonical Desktop→Surface transfer SOP](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md): Desktop WSL→Windows temporary directory, Python HTTP LAN **43157**, Surface `Invoke-WebRequest`, byte count/digest verified. HTTP server shut down and exact temporary staging removed.
- Surface private test and receipts: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V26B-REGSTATE-20261027\`; host script SHA `82cd74483a66a5928cbb9192a6c25a42aa59050ea739e137c5793a7fd3be96fd`, Bash SHA `9b2b7ec0e4bab84be812ba7432186de5e85a01eb20c18e1b3f1bea6bff5b799a`. One-time **CONSUMED** trial `reg26b-01-mask000`; never rerun or overwrite its logs.

## Hardware result: V26b two scans in ONE continuously loaded driver

On-device shell `root_bash_rc=38` because the runner deliberately stops if either scan fails. However both firmware and core/WCC loaded correctly, `wlan0` appeared, and both requests reached `brcmf_cfg80211_scan`. No watchdog occurred on first scan.

| Stage | Measured result |
| --- | --- |
| First userspace scan | `iw rc=0`, 1218ms, 3 BSS |
| First driver submission | `NEW_SCAN_GENERATION id=4661`, `SCAN_REQUEST_SYNC id=4661`, `ESCAN_SET_RC=0 v2=0` |
| First genuine terminal | Event69 status0, `TERMINAL_SYNC bytes=12 buflen=12 escan_version=109 sync_id=4661 bss_count=0`; `TERMINAL_GENERATION_ACCEPT id=4661`, ordinary `SCAN_COMPLETION aborted=0 fw_abort=0 owned=1` |
| Second userspace scan, 4 seconds later | `iw rc=204`, 66ms, stderr `command failed: Invalid exchange (-52)` |
| Second scan guard | `SCAN_REQUEST n_channels=1 n_ssids=0 ie_len=0 busy=0`, `SCAN_GATE_PASS`; **no EPERM** |
| Second driver submission | `NEW_SCAN_GENERATION id=4662`, actual effective `SCAN_REQUEST_SYNC id=4662`, `ESCAN_SET_RC=-52 v2=0` |
| Second terminal | **None**: firmware did not accept ESCAN command. This is not an Event69-completion or scan-generation mismatch. |

Read-only kernel trace after completed trial confirmed both first and second request fields and return codes; no new physical scan was initiated merely to gather those logs. The prior `V25` `-EPERM` condition was removed; a **different firmware ESCAN command return `-52`** is now the next actual technical blocker. Do not claim the exact firmware-side reason for the `-52` return has been determined (e.g. busy, unsupported repeated request, stale state) without targeted evidence.

A second invocation of the V26b owner suite noticed that `reg26b-01-mask000` was consumed and refused it; **no additional on-device scan** from that invocation. Do not confuse this attempt-marker refusal with the actual measured completed trial.

**Rollback:** Shell logged successful unload of WCC/core/util, WCC temporary bind unmount rc0, FW temporary bind unmount rc0, original file hashes and runtime restored. Host receipt `independent_poststate_ok=true`, `permanent_install=false`. A separate **independent read-only COM9 preflight PASS after this investigation** reconfirmed original FW/NVRAM/core/WCC, wlan down, WPA active, Bluetooth quiet and no overlays. As `root_bash_rc=38`, the suite correctly reports overall test failure, not a pass.

## Next design direction

1. **Retire lab gating from eventual normal-operation patch.** Retain cfg80211 channel/regulatory enforcement and supported firmware operation; no added `NO_IR` perpetuity requirement, no permanent passive-only/channel36 hardcode. The ultimate goal is ordinary scanning, association, authentication and data transfer on Xoom Linux 7.
2. **Investigate `-52` at second `brcmf_fil_iovar_data_set(..., "escan", ...)`** with minimal firmware-protocol/scan-state evidence: query current firmware scanning state (where supported), use existing normal abort/completion management, evaluate enhanced vs legacy protocol semantics. Do not manufacture terminal status or add arbitrary delays/restrictions unless causally justified.
3. **Maintain scan-generation/owner mapping quality:** V21 physically proved genuine completion routing; V22/V23 verified sync-ID echo; V24–V26 first live scan accepted generated ID4661. V26 now proves generation4662 is correctly generated and transmitted; its command is rejected at firmware interface, so stale/late-event behavior is still not validated.
4. After evidence-supported fix and multi-scan reliability, move promptly to normal cfg80211/wpa_supplicant network join tests in permitted regulatory state, using established private SSID/PSK handling. Keep logs private and never commit credentials, MACs or SSIDs. Multi-interface, cancel/reset/race, Wi-Fi+Bluetooth and Xoom model regression gates remain open before upstream submission.

**Conclusion:** unnecessary host-side `NO_IR` requirement eliminated; scan generation advances as designed; next real blocker is firmware second ESCAN request error `-52`, not Linux regulatory enforcement. No firmware file or chip modification, no upstream patch promoted.
