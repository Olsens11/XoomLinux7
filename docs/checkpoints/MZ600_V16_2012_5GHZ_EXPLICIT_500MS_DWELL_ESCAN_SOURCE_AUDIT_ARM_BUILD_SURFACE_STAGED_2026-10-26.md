# MZ600 V16 — source-verified 5GHz ESCAN V1 encoding and finite passive dwell; ARM built, Surface owner one-shot STAGED

**Date:** 2026-10-26. **State: SOURCE/OFFLINE BUILD + SURFACE STAGING PASS; NO V16 PHYSICAL TEST EXECUTED.** Do not overwrite or rerun V14/V15 consumed one-shots.

## Why this is the next experiment

- [V14 physically proved](MZ600_V14_2012_ESCAN_EVENT69_PARTIAL_BSS109_PASS_TERMINAL_MISSING_2026-10-26.md) the **May 2012 original Motorola-related BCM4329 4.218.248.44** firmware (RAM overlay, original NVRAM unchanged) supports real 5GHz channel36 5180MHz passive ESCAN V1, sends Event69 PARTIAL with BSS109, but **no observed terminal Event69 SUCCESS** before ~10s watchdog aborted scan.
- [V15 physically proved](MZ600_V15_2012_OEM_2G_ESCAN_EVENT69_TERMINAL_SUCCESS_179MS_PHYSICAL_PASS_2026-10-26.md) **same firmware** on 2412MHz channel1 passive ESCAN V1 sends 2 partial Event69s then terminal Event69 SUCCESS status0, two BSS109 published by standard Linux7, scan completed in **179ms** without watchdog; rollback independently verified. Thus no universal Event69 terminal generation / SDIO receive / cfg80211 completion failure.
- Original Linux7 `brcmf_escan_prep` initializes `active_time=-1, passive_time=-1, home_time=-1, nprobes=-1` (firmware defaults), then sets scan type PASSIVE when `n_ssids=0`. The on-chip firmware's particular passive 5GHz dwell/termination behavior under default `passive_time=-1` is not established. To separate a dwell-default problem from an underlying 5G state-machine problem, one narrow **500ms finite passive dwell** experiment is justified. This is a hypothesis, not a known fix.

## Checked actual Linux7 channel encoding

Actual local kernel source `cfg80211.c`:
- `brcmf_cfg80211_attach` reads Broadcom `BRCMF_C_GET_VERSION` into `cfg->d11inf.io_type` and dispatches to `brcmu_d11_attach`.
- `channel_to_chanspec` derives channel number from frequency, chooses `BRCMU_CHAN_BW_20`, then calls `cfg->d11inf.encchspec`. With D11N mode, `brcmu_d11n_encchspec` encodes channel36 with `5G 0x1000 | 20MHz 0x0800 | no sideband 0x0300 | 0x24` = **0x1B24**. Actual current run's `io_type` and outgoing request bytes had not been logged in V14, so V16 explicitly logs them; do not mistake formula for a physical capture.
- `brcmf_escan_prep` puts encoded chanspec into `channel_list[0]`, scan count1 and PASSIVE because n_ssids0; `brcmf_run_escan` converts V2 prep struct into ESCAN V1 when `BRCMF_FEAT_SCAN_V2` absent. V14/V15 physically logged `v2=0`. V16 logs **both** pre-conversion chanspec/d11 io type and post-conversion V1 bytes (chanspec, passive_time, scan_type, nprobes, nchans) before firmware request.
- No kernel change to radio regulatory domain, channel set, power, BT, AP selection or MAC/NVRAM. Must retain V05 NO_IR-only legacy ioctl217 channel list fallback because May2012 `chanspecs` iovar fails -52.
- Modern standard `brcmf_cfg80211_escan_handler` treats Event69 status8 as partial and status0 terminal SUCCESS. Firmware/event transport already physically work on 2G; no fabricated completion permitted on 5G.

## V16 build

New [source-restoring builder](../../tools/forensics/build_mz600_v16_2012_5g_explicit_dwell_escan_lab_module.py), new output `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-2012-oem-escan-v16-20261026/brcmfmac-2012-escan-event69-v16.ko`.

- Target Linux `7.0.0-next-20260422+`, exact ARMv7 module ABI `SMP mod_unload modversions ARMv7 p2v8`.
- Firmware SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` (264140 bytes, private only), V16 module SHA256 **`b0825974bf2bf69663c809239b8f9b7470d90929a7109bea8bab33575c56ebe9`**, **345004 bytes**.
- Reuses V14's strict BCM4329-only **single ch36 5180MHz NO_IR nonDFS noSSID noIE** driver-side scan guard, `WLC_SET_PASSIVE_SCAN=1`, standard ESCAN V1, Event69/BSS109/aborted/watchdog diagnostics. Changes **only one radio-scan parameter** relative to V14: `passive_time=500` milliseconds specifically for the one allowed 5180MHz scan (instead of firmware default `-1`). No directed probes or association; existing passive-scantype logic unchanged.
- Two read-only numeric markers `MZ600_V16_V2_PASSIVE_DWELL_MS=500 encoded_chanspec=0x... d11io=...` and `MZ600_V16_V1_CH36_WIRE chanspec=0x... passive_ms=... scan_type=... nprobes=... nchans=...` confirm actual outgoing V1 bytes. Expected D11N channel is 0x1B24, but **physical result pending**.
- First offline compiler pass caught escaping in added `brcmf_info` format strings. The compiler rejected that candidate, restored unmodified baseline cfg80211.c and .ko safely. Corrected in committed builder, reran, **ARM compile PASS** with new unique final module. Source and original installed-module SHAs verified restored after build: `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8` and `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`.

## Xoom guarded V16 test

New [Linux owner script](../../scripts/host/xoom/test-mz600-v16-2012-5180-500ms-passive-escan-owner-20261026.sh), **6773 bytes**, SHA `1dee9b41dec5d559f7dd5308f091645f8c1b70d6ed5ce2235d88d55067643491`, Bash syntax PASS.

- Same V14 working one-shot: validate root, exact Debian p8/kernel, original fw/NVRAM/module hashes, per-device FDT MAC, no conflicting WiFi/BT services/modules/overlay, new one-shot marker, private 2012 FW and V16 module /run SHA, single allowed 5180MHz `NO_IR` and not disabled/radar before scan, then just `iw dev wlan0 scan freq 5180 passive` with bounded outer timeout24s.
- Print only numeric firmware band/WIPHY counts, `escan` accept RC, Event69 status/counts (0 SUCCESS, 8 PARTIAL), packet BSS v109 lengths/count, scan result exit/duration and kernel watchdog, not user MAC, SSID or BSSID. `MZ600_V16_EVENT69_STATUS_COUNTS success=N partial=N other=N` is derived from fresh post-start dmesg, not old logs.
- Always down WLAN, unload Broadcom modules, unmount matching firmware-only RAM overlay, verify original installed FW, NVRAM and baseline .ko hashes, absence of radio modules; independent Surface serial poststate check. Never install/flash firmware or change calibration/regulatory, never reboot as part of test.
- The test may **execute cleanly but still fail to complete the scan**. Do not conclude success from `iw` exit0 alone. Only Event69 status0 and `scan_done aborted=0` count as terminal success. Keep V14 and V15 as separately measured controls.
- Only one execution; if preflight or rollback fails STOP and inspect, not rerun.

## Surface staged and verified

Surface directory `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V16-2012-500MS-5G-ESCAN-20261026`:

| Item | SHA256 |
|---|---|
| Private May2012 `mz600-v16-oem2012.bin` | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` |
| ARM `mz600-v16-escan-event69.ko` | `b0825974bf2bf69663c809239b8f9b7470d90929a7109bea8bab33575c56ebe9` |
| Bash `mz600-v16-passive-scan.sh` | `1dee9b41dec5d559f7dd5308f091645f8c1b70d6ed5ce2235d88d55067643491` |
| Surface [owner launcher source](../../scripts/host/surface/mz600-v16-2012-5180-500ms-passive-escan-owner-once-20261026.py), `mz600-v16-owner-once.py` | `238f202e5c72556a73a841ac2a2f73bdf73a467709c3a6c0f1a64b7fef2ffa5f` |

Surface PowerShell `python -m py_compile` PASS, no V16 attempt marker or receipt at staging. Desktop transfer via existing TCP43157 temporary Python file server (Surface-restricted), Surface binary hashes verified; temporary server explicitly terminated, port closed and temp working directory removed. Another user Python PID13444 `xoom-v068-bluez4-sdp-reconnect-check.py` **still running** on Surface; do not interrupt it, must close its COM9 session normally before the owner launches V16.

**Owner-run once, only when COM9 is free:**

```powershell
python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V16-2012-500MS-5G-ESCAN-20261026\mz600-v16-owner-once.py"
```

The owner launcher serial-transfers SHA-pinned two files into RAM, validates Xoom preflight, `bash -n` check, one run, independent post-audit and saves receipt/transcript locally; no physical V16 action yet.

## What result decides

- If `chanspec=0x1b24`, passive_ms500, Event69 **terminal status0**, scan done aborted=false, no watchdog: firmware default passive dwell likely relevant, follow up with careful repeats/conditions on different fresh one-shots before production change.
- If 5G still returns PARTIAL but no SUCCESS at ~10s: default dwell setting alone is not sufficient; investigate firmware 5GHz channel-state/clock/BT coexistence/events, and consider OEM Android stock reference before speculative retries.
- If emitted V1 chanspec isn't `0x1b24` or scan_type isn't PASSIVE, treat as request ABI/driver implementation discrepancy, fix source before further radio testing.
- Regardless, 2012 candidate's 2.4GHz genuine Event69 SUCCESS 179ms remains separately proven. No automatic installation.

