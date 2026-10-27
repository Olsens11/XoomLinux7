# MZ600 V23 — alternate host ESCAN sync IDs echoed by original firmware: PHYSICAL PASS

**Date:** 2026-10-27. **DUT:** replacement Motorola Xoom MZ600, Debian armhf Linux7 kernel `7.0.0-next-20260422+`. **Qualification:** true on-device BCM4329 Event69 terminal payload echo for **three values across V22b/V23: 0x1234, 0x1235, 0x1236**. V23 adds *only* a reversible host-side request-field substitution on BCM4329. The firmware binary, on-chip software, NVRAM, permanent Linux installation, hardware chip registers and device partition contents are unchanged.

## Baseline

Previous physically verified [V22b checkpoint](MZ600_V22B_TERMINAL_SYNC_ID_ECHO_PHYSICAL_PASS_2026-10-27.md) established a real 12-byte event69 status0 terminal: payload `buflen=12 escan_version=109 sync_id=4660 bss_count=0`, matching existing Linux7 firmware request `params->sync_id=cpu_to_le16(0x1234)`. One scan completed in 750ms with three userspace BSS.

[V21 six-trial physical checkpoint](MZ600_V21_TERMINAL_OWNER_LAB_SWITCH_AB_PHYSICAL_PASS_2026-10-27.md) separately established the precise interface routing failure (genuine terminal EVENT69 status0 can be lost in `fweh.c` when `bsscfgidx` cannot resolve) and proved an exceptional active-owner route can deliver the real completion to the original cfg80211 handler, with no fabricated signal. **Neither V21 nor V22b alone proved scan generation identity.**

## V23 source, binary and lab control

- Repo `Olsens11/XoomLinux7`, topic branch `wip/clean-wifi-bt-usb-20261025`, source-restore builder [`tools/forensics/build_mz600_v23_variable_scan_sync_id.py`](../../tools/forensics/build_mz600_v23_variable_scan_sync_id.py), initial commit `a71c1655b347eac1c73ab44c2d5d612364b23663`. It derives the exact V22b and V21 source/diagnostics. It adds one read-only-at-load 16-bit `mz600_request_sync_id` parameter with **default 4660** and changes the legacy **host-side `brcmf_run_escan()` request field** only when chip id is BCM4329. All other devices retain the original `0x1234`. Log numeric requested and returned IDs independently; no firmware file editing, no new completion handler, no persistent installation.
- Matched offline ARM `brcmfmac-2012-escan-variable-sync-v23.ko`, **351540 bytes**, SHA256 `dc338742e4e8c36fca4b325ee6a885bb888949281129f6898c420a4e39f45bcf`; `vermagic=7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`. `modinfo` confirmed both `mz600_terminal_owner` (lab only) and `mz600_request_sync_id` ushort. Offline compilation succeeded; builder verified original host `cfg80211.c` SHA `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`, `fweh.c` SHA `4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c`, baseline .ko SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`; no kernel build or flash on Xoom.
- Original private BCM4329 2012 firmware SHA `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, only bind-mounted in RAM for each trial. Original installed firmware SHA `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, NVRAM SHA `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb` remain intact.
- Standard documented [Desktop→Surface→COM9 transfer](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md): exact WSL→Windows staging, desktop Python HTTP LAN port43157, Surface `Invoke-WebRequest` and SHA hash check, confirmed temporary server shutdown and directory removal. Surface private staging: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V23-2012-ALT-SYNC-20261027\`. Surface Bash SHA `c9bf7fd1b7c16bf5c668f5ae024f4f0ac1be62cc7e4b9bf6894cf044fe24d8a5`; owner Python runner SHA `e9f02349cf8a02325d0b22c1c97be19f95466ca2d5813a82c096f3628f879b45`. Their legacy UI still names its selector "mask" but in V23 `mask=0 → request_sync_id=4661`, `mask=1 → 4662`, while `mz600_extra_events=0` remains fixed and V21 `mz600_terminal_owner=1` always enabled. The lab parameter is verified via `/sys/module/brcmfmac/parameters/mz600_request_sync_id` before each scan.
- Two unique, **CONSUMED** trial IDs under local private `runs/`: `sid23a-01-mask000`, `sid23a-02-mask001`; never rerun with those IDs. Each tested one passive NO_IR/non-DFS 5180MHz channel36 scan using the proven 500ms dwell, no directed SSID or association.

## Actual hardware results, corroborated by on-device numeric kernel markers

| Trial | Driver **request** | Firmware terminal **returned** | Terminal Event69 header | Actual owner route | Linux outcome |
| --- | --- | --- | --- | --- | --- |
| `sid23a-01-mask000` | `4661 = 0x1235` | `4661 = 0x1235` | `ver=2 ifidx=1 bsscfgidx=1 datalen=12 pktlen=94` | `TERMINAL_OWNER_CHECK eligible=1` / `TERMINAL_OWNER_DELIVER status0` | **1847ms**, 3 BSS, `scan_done aborted=0`, no watchdog |
| `sid23a-02-mask001` | `4662 = 0x1236` | `4662 = 0x1236` | `ver=2 ifidx=1 bsscfgidx=1 datalen=12 pktlen=94` | `TERMINAL_OWNER_CHECK eligible=1` / `TERMINAL_OWNER_DELIVER status0` | **1742ms**, 3 BSS, `scan_done aborted=0`, no watchdog |

Both terminal payloads independently decoded `bytes=12 buflen=12 escan_version=109 bss_count=0`; `MZ600_V23_SCAN_REQUEST_SYNC id=4661/4662` and `MZ600_V23_TERMINAL_SYNC ... sync_id=4661/4662` matched exactly. The fact that these `ifidx,bsscfgidx` were both `1,1` independently proves the existing V21 routing hypothesis operates even with nonstandard request IDs. These two V23 scans **each used separately loaded/reinitialized module state**; we have **not yet proven per-scan increment within one continuously running module instance**, nor stale-event rejection.

Both receipts show `root_bash_rc=0`, `script_cleanup_ok=true`, `independent_poststate_ok=true`, `permanent_install=false`. Suite result `V23_MULTI_MASK_SUITE_COMPLETE_AND_ORIGINAL_RUNTIME_PASS`; independent **post-test read-only COM9 preflight PASS**: installed firmware/NVRAM/module SHA unchanged, wlan0 down, WPA active, Bluetooth quiet, no temporary overlays. Neither trial changed the device filesystem or flash contents permanently.

### Private evidence digests (no BSSID/SSID/MAC exposed)

| Trial | Private transcript SHA256 | Receipt JSON SHA256 |
| --- | --- | --- |
| `sid23a-01-mask000` | `124365b7fd1d2c2030eaa19d172693231ba4624eadc9fe423c74ae8089295765` | `0d6a21cd73ee9783a01ee6db254da95a600142aa324adb1cfdd24c1b5785c47c` |
| `sid23a-02-mask001` | `08ad10f294abde21935b94693aff854fd88e6424e77b0467a6d1adc684215470` | `b0ea6132b2ade329a6a6cb5800d0cee1902ee606d706c8276c832e14a1cbc947` |

## Engineering interpretation, upstream-quality requirements

**New real protocol evidence:** The actual 2012 BCM4329 firmware accepts non-default ESCAN request sync IDs `0x1235` and `0x1236`, emits Event69 status0 containing the same IDs in the 12-byte fixed result header, and produces successful normal Linux completion when the genuine terminal is dispatched to the active scan owner. Combined with V22b's fixed `0x1234`, this supplies a **strong basis** for a correctly modeled, scan-generation-aware driver compatibility layer.

**Not proven:** That Linux currently protects against stale terminal events (it does not; original request ID constant), that firmware guarantees unique IDs, that a per-scan sequence counter and wrapping work on BCM4329, or that matching only a sync ID is sufficient for cancellation/reset/teardown correctness. We also have not proved whether the firmware-supplied trailing event ifidx/bsscfg bytes are wrong versus parsed from semantically different field offsets. A 12-byte terminal header does **not** itself explain this variance.

**Next patch-model step:** Isolate a coherent `wifi: brcmfmac` logical change: maintain a safely synchronized per-device/scan-generation `u16` sync ID, associate real Event69 SUCCESS with current active `cfg->escan_info.ifp` only after payload length/format and ID match; preserve ordinary routes; do not global-remap indexes, synthesize scan completion, or modify firmware/chip resources. Model stale/duplicate/aborted/completion-race, reset, P2P/multi-interface and scan ownership lifetime; unit-test before multi-device promotion. Use the physically tested V21 owner-fallback and V23 ID echo as reference cases, not production patch by default. Keep distinct MMC/DT/BT/coexistence series and upstream signoff gates intact.
