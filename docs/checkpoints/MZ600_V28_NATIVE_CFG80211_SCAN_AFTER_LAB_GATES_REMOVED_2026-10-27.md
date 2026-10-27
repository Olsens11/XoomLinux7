# MZ600 V28 — normal cfg80211 scan, all temporary passive/ch36 restrictions removed (physical test 2026-10-27)

**Outcome: FIRST NORMAL MULTICHANNEL SCAN PASS, SECOND REQUEST FAIL `-52`.** This confirms that the second-scan failure seen in V26b/V27 persists after removing the earlier diagnostic scan-policy scaffolding. The source is still a reversible lab candidate; **no permanent Linux install, firmware binary or chip-side modifications**.

## Why this is the right comparison

Owner direction: stop retaining experimental requirements solely because they once simplified Event69 tests. The ultimate kernel driver must use ordinary cfg80211 scan requests, capabilities and regulatory rules rather than hardcode one 5GHz channel, permanent NO_IR, global passive scanning, no SSIDs, or a synthetic dwell. V25 demonstrated that the old NO_IR guard interfered with legal beacon-hint transitions; V26 removed the gate and showed a second firmware request fails with `-52`; V27 [firmware-error checkpoint](MZ600_V25_TO_V27_SECOND_SCAN_REGSTATE_AND_FIRMWARE_NOTUP_2026-10-27.md) decoded this error as `BCME_NOTUP` (-4) on its controlled second request.

## Exact native-scan candidate and evidence

Source-restoring [V28 native cfg80211 builder](../../tools/forensics/build_mz600_v28_native_cfg80211_scanning.py), commit `7241583`, based on earlier V21–V26 Event69 completion and generation research. V28:
- Removes the **entire** diagnostic admission gate checking one channel36 / 5180 MHz, zero SSIDs, zero IEs, `NO_IR` and hardcoded passive global `BRCMF_C_SET_PASSIVE_SCAN=1`.
- Removes imposed 500ms passive dwell override. Normal driver `brcmf_escan_prep()` derives active/passive scan from cfg80211 request; a broadcast request with `n_ssids=0` may naturally remain passive under original driver behavior, **not because of an inserted test restriction**.
- On BCM4329 with missing `chanspecs` iovar, preserves firmware-reported `WLC_GET_VALID_CHANNELS` capability list and HT20-only conservative hardware bandwidth; removes artificial blanket NO_IR on all allowed channels. No runtime regulatory flag clearing, firmware image change, private NVRAM change or country spoofing. Separate verification of the **effective** per-channel regulatory restrictions remains needed before active probing or association. The standard brcmfmac source applies a custom wiphy regulatory domain and has a regulatory notifier; normal regulatory compliance must be verified, not inferred solely from the absence of NO_IR.
- Retains evidence-grounded real Event69 terminal-to-current-scan owner and ID tracking. These remain *experimental/race-hardening open*, not yet upstream-ready.

Physical MZ600, Debian armhf Linux `7.0.0-next-20260422+`, same original Motorola 2012 candidate firmware, no persistent firmware or module install. Matched ARM core `mz600-v28-escan-event69.ko`: **352004 bytes**, SHA256 `f58391f2eb7753ea7effe4fa83fcf9364523cf90e4aaeaadf663a5d91cfd0d8b`; paired WCC **5892 bytes**, SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`. Original private firmware SHA `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`; the installed baseline was preserved. Private receipt and transcript at `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V28-NATIVE-SCAN-20261027\runs\native28a-01-mask000.*`. **Trial ID is consumed, never reuse.** Owner Bash SHA `a36f47555228ec77e8d7f9774e9468392d003ad5ce4b494e6da2924c7f604baa`.

**Measured:**
| Stage | Actual result |
| --- | --- |
| Original guarded test module stack | Core + matched WCC loaded, wlan0 present, temporary firmware and companion mounts hash-checked |
| Firmware available bands | 14 defined 2GHz, 29 defined 5GHz; 5GHz disabled 5; firmware valid-channel fallback reported total35 (11 2GHz,24 5GHz) |
| 5GHz displayed NO_IR after normal fallback | **0 channels** (formerly 24 with passive-only fallback); this is a measurement, **not proof that any transmission on those channels complies with the full effective regulatory domain** |
| First ordinary `iw dev wlan0 scan` | **rc=0, 2834ms, 12 BSS** (no `freq 5180 passive` hardcode) |
| Second ordinary scan, same loaded driver | `iw rc=204`, **50ms**, error `Invalid exchange (-52)`, 0 BSS |
| Automatic cleanup | Core/WCC/util unload rc0, WCC transient bind unmount rc0, FW transient bind unmount rc0; original files and radio restored |
| Separate poststate | Host receipt `independent_poststate_ok=true`, `permanent_install=false`. Suite `root_bash_rc=38` and `script_cleanup_ok=false` because a required successful two-scan result was absent; do **not** label complete test PASS |

No SSID/password or BSSID data should leave private local files. No association/authentication has yet been attempted with this candidate.

## Implications and next concrete engineering question

**Settled now:** The diagnostic channel36 / passive / NO_IR / 500ms restrictions are not needed to perform the first scan and do not explain why the second request fails. Native multichannel scanning works and finds more BSS. V27's controlled second scan firmware code `BCME_NOTUP` strongly motivates a narrowly instrumented source audit of BCM4329 `BRCMF_FEAT_QUIRK_NEED_MPC`, firmware MPC/UP/DOWN state and scan completion lifecycle, not more arbitrary scan-policy gates.

**Not settled:** whether the second V28 firmware error corresponds to the exact same vendor `BCME_NOTUP` reason without numerical readback on that module; why firmware state changes after completion; repeated native scan reliability; credentialed network association; full effective regulatory-domain verification across all bands; cancellation, stale-generation and multi-interface races.

**Next:** concentrate on firmware readiness after first scan and apply only an evidence-grounded compatibility correction; validate effective regulatory channel permissions before introducing directed active scanning or association. Prefer reusing the standard cfg80211, wpa_supplicant and normal radio paths. Do not add permanent diagnostic scan restrictions or bypass kernel regulatory enforcement.
