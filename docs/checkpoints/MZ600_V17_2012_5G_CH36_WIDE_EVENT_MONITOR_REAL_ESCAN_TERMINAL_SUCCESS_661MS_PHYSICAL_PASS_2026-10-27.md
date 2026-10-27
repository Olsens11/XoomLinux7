# MZ600 V17 — first real 5GHz ESCAN V1 terminal SUCCESS in 661ms with broad event monitoring (physical PASS)

**Date:** October 27, 2026. **Actual owner-authorized remote Surface COM9 one-shot on MZ600 Debian Linux7, independently verified.** Major milestone: this is the **first physically demonstrated normal native Linux7 5GHz passive scan completion** with the May25 2012 BCM4329 firmware. **Do NOT rerun the consumed V17 one-shot.** All private Wi-Fi SSIDs, BSSIDs, device MAC, USB serial and full serial transcript stay PRIVATE on the Surface.

## Compared with earlier proven physical tests

| Test | Scan | Firmware Event69 | Outcome | Elapsed |
|---|---|---|---|---:|
| V14 | One 5GHz 5180MHz channel36 passive, firmware default dwell | 1 PARTIAL, **no terminal SUCCESS** | watchdog aborted=true, 0 user BSS | 10482ms |
| V15 | One 2.4GHz 2412MHz channel1 passive, firmware default dwell | 2 PARTIAL, **terminal SUCCESS** | aborted=false, 2 user BSS | 179ms |
| V16 | One 5GHz 5180MHz channel36 passive, **500ms dwell** | 7 PARTIAL, **no terminal SUCCESS** | watchdog aborted=true, 0 user BSS, 3 cached BSS | 10374ms |
| **V17** | Same V16 channel36 passive 500ms dwell but *broadened firmware event observation and quiescent Bluetooth stack preserved* | **6 handler PARTIAL, Event69 terminal status0 SUCCESS** | **aborted=false, 2 user BSS** | **661ms** |

All four physical scans used the **same** private May25 2012 Broadcom BCM4329/3 firmware `4.218.248.44` SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, original per-device MAC/NVRAM, Linux7 kernel `7.0.0-next-20260422+`, a **one-channel passive NO_IR** non-DFS scan, and unchanged regulatory configuration. V17 does NOT demonstrate which changed condition produced success; only the outcome is proven.

## What the broader V17 code deliberately monitored

The source audit found historical Broadcom `WLC_E_SCAN_COMPLETE` **Event26** and `SCAN_CONFIRM_IND` **Event45** recognized in Linux7's `brcmfmac/fweh.h`, but **not subscribed by its standard ESCAN implementation**. `brcmf_fweh_activate_events` builds the on-firmware `event_msgs` bitmask from registered event handlers, then `brcmf_fweh_process_event` filters/drops events lacking a handler. **Consequently the earlier Event69-only logs could not rule out firmware reporting completion by Event26/45.** Historical Android Broadcom driver `wl_iw.c` routes Event26 to normal scan result notification; see https://android.googlesource.com/platform/hardware/broadcom/wlan/+/b4ace791eb574f589c53be582ea0d14e1a85ff09/bcm4329/src/wl/sys/wl_iw.c .

The V17 RAM-only diagnostic:
- Registered a **no-side-effect observer** for Event26 SCAN_COMPLETE, Event45 SCAN_CONFIRM_IND, and other low-payload state indications **13,14,35,40,63**; kept the normal Event69 `brcmf_cfg80211_escan_handler` untouched for actual completion. No artificial scan-done signals.
- Instrumented **firmware event ingress in `fweh.c` before dispatch filtering**, logging **numeric** event code/status/reason/datalen/subscription state only; no raw packet data or address identifiers.
- Instrumented each Event69 partial BSS109 `SSID_len`, zero/nonzero hidden-SSID flag, `chanspec`, control channel and safe IE bounds; no SSID/BSSID/IE data printed.
- Preserved the same V16 `passive_time=500`, D11N `0x1b24` ch36 V1 format and one 5180MHz PASSIVE `NO_IR` no-SSID no-IE no-association driver gate; original legacy `WLC_GET_VALID_CHANNELS` 2G/5G HT20 NO_IR wiphy fallback retained.
- Offline ARM module 346508 bytes, SHA256 **`d8ccb6f7077d54db0fa95e90debcd0e06494c9acd8e539eabebb7abde68233c7`**; source-restoring build at [`tools/forensics/build_mz600_v17_2012_5g_all_scan_completion_paths.py`](../../tools/forensics/build_mz600_v17_2012_5g_all_scan_completion_paths.py), original `cfg80211.c` SHA `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`, `fweh.c` SHA `4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c`, original kernel `.ko` SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb` verified restored.
- [Xoom guarded one-shot Bash](../../scripts/host/xoom/test-mz600-v17-2012-5180-passive-wide-event-owner-20261027.sh), latest SHA256 **`f9381b12e090884482b7186b4466f7f8516ff64259a1a43b56ab1b83c02f66e2`**, 7895 bytes. [Surface owner Python](../../scripts/host/surface/mz600-v17-2012-5180-passive-wide-event-owner-once-20261027.py) SHA256 `ba5485cc8d69af75c3dc46961c9e686a7849ef4abd5a1359bec1c86f36f3e21f`.

## Preflight and runtime restoration nuance — DON'T LOSE THIS

At user reconnect, exact Linux kernel, original installed firmware/NVRAM/module SHA matched, but **wlan0 existed in DOWN state** and **wpa_supplicant.service was ACTIVE**, with installed original `brcmfmac_wcc`, `brcmfmac`, `brcmutil` modules loaded. The first V17 original one-shot preflight correctly stopped **before creating an attempt marker, transferring binaries or touching radio** with missing NO_WLAN0. A read-only serial check diagnosed that state.

A cautious host-only Python runtime wrapper, private Surface local file `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V17-2012-WIDE-EVENTS-20261027\v17-restore-runtime-wrapper.py`, was authored and syntax checked. It precisely verified baseline, temporarily stopped **only** wpa_supplicant and unloaded original Broadcom Wi-Fi modules, then calls SHA-pinned owner V17 one-shot, and **always attempts to restore original modules, wlan0 DOWN, and wpa_supplicant ACTIVE** in a finally block. Its first invocation detected an additional obstacle: Linux kernel **bluetooth, btbcm, hci_uart** modules loaded; original owner scripts forbade ANY BT module. Again this aborted preflight **before any firmware swap/scan, no V17 marker**, and wrapper successfully restored original Wi-Fi runtime.

A read-only BT state audit showed `bluetooth.service INACTIVE`, `hci0 PRESENT but DOWN`, `hci_uart` refcount0, so **there was no operating Bluetooth link**. Because unloading `hci_uart` could destroy a UART-attached hci0 and disrupt recovery of its runtime, the V17 owner Bash/Python preflight was **surgically modified**: BT core modules may remain loaded **ONLY** if bluetooth.service is inactive and HCI0 is not UP/RUNNING. Explicit `MZ600_V17_QUIESCENT_BT_STACK_PRESERVED` logged. Active BT or Wi-Fi still fails closed; no BT module was unloaded or reconfigured during successful run. This **BT-loaded-but-idle state is a meaningful V17-vs-V16 variable** (V16's preflight rejected loaded BT modules, hence its BT state differed). Do not claim event-mask change alone caused success.

After this adjustment: original runtime checked, Wi-Fi temporarily quiesced, firmware/ARM .ko uploaded to **/run RAM only** over COM9 with SHA checks, one radio scan, independently audited original installed firmware/NVRAM/.ko and unloaded all temporary Wi-Fi modules, then wrapper **reloaded installed original Wi-Fi modules, put wlan0 DOWN, and restarted the originally active wpa_supplicant service**. Wrapper exited **0** with:
```text
MZ600_V17_RUNTIME_ORIGINAL_BASELINE_VERIFIED
MZ600_V17_RUNTIME_RADIO_IDLE_FOR_ONESHOT
V17_XOOM_ORIGINAL_FW_NV_MODULE_BASELINE_PASS
V17_ON_DEVICE_GUARDED_SCRIPT_SYNTAX_PASS
MZ600_V17_ORIGINAL_FILES_AND_RADIO_RESTORED
V17_2012_WIDE_EVENTS_SCAN_AND_ROLLBACK_PASS
MZ600_V17_OWNER_ONESHOT_PROCESS_RC=0
MZ600_V17_ORIGINAL_RUNTIME_RESTORED
MZ600_V17_BROAD_DIAG_AND_ORIGINAL_RUNTIME_RESTORED_PASS
```

**Do not rerun** V17: its distinct owner attempt marker and receipt exist. No permanent firmware/module/calibration change. Original BT remained loaded and quiescent.

## V17 physical scan observations

```text
MZ600_V17_PREFLIGHT_START
MZ600_V17_QUIESCENT_BT_STACK_PRESERVED
MZ600_V17_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED
MZ600_V17_TEMP_2012_FIRMWARE_OVERLAY_PASS
MZ600_V17_WCC_LOAD_RC=0
MZ600_V17_WLAN0_PRESENT
MZ600_V17_PHY_2G=14 PHY_5G_TOTAL=29 PHY_5G_NO_IR=24 PHY_5G_DISABLED=5
MZ600_V17_ALT_MASK_REQUEST codes=13,14,26,35,40,45,63,69
MZ600_V17_CHANNEL36_NO_IR_NONDFS_PASS
MZ600_V17_V2_PASSIVE_DWELL_MS=500 encoded_chanspec=0x1b24 d11io=1
MZ600_V17_V1_CH36_WIRE chanspec=0x1b24 passive_ms=500 scan_type=1 nprobes=-1 nchans=1
MZ600_V17_ESCAN_SET_RC=0 v2=0
MZ600_V17_IW_PASSIVE_CH36_RC=0 ELAPSED_MS=661
MZ600_V17_USERSPACE_BSS_COUNT=2
MZ600_V17_FWEH_INGRESS code=69 status=8
MZ600_V17_EVENT69 status=8 datalen=512
MZ600_V17_EVENT69_PARTIAL bss_ver=109 bss_len=500 count=1
MZ600_V17_BSS_META ssid_len=0 hidden=1 chanspec=0x1b24 ctl_ch=36 ie_bounds_ok=1 ie_len=369
MZ600_V17_BSS_META ssid_len=13 hidden=0 chanspec=0x1b24 ctl_ch=36 ie_bounds_ok=1 ie_len=460
MZ600_V17_FWEH_INGRESS code=69 status=0 reason=0 datalen=12 subscribed=1
MZ600_V17_EVENT69 status=0 datalen=12
MZ600_V17_FINAL_BSS count=2 version=109
MZ600_V17_SCAN_COMPLETION aborted=0 fw_abort=0 owned=1
MZ600_V17_RX_EVENT_COUNT code=69 count=16
MZ600_V17_ALTERNATIVE_EVENT_COUNTS total=0 success_status=0
MZ600_V17_METADATA_COUNTS total=6 hidden=4 malformed=0 ctl_ch36=6
MZ600_V17_EVENT69_STATUS_COUNTS success=1 partial=6 other=0
MZ600_V17_NO_ASSOCIATION_OR_DIRECTED_SSID
MZ600_V17_ORIGINAL_FILES_AND_RADIO_RESTORED
```

- **Actual terminal event was Event69 status0 SUCCESS, NOT Event26/45**; alternative events were subscribed but **none were observed**. This proves firmware sometimes DOES complete 5GHz correctly with native ESCAN, and the Linux7 handler is capable of processing the terminal. It **does not prove** the cause of prior missing terminal, nor that Event26/45 never occur in other firmware conditions.
- **Ingress vs handler difference**: raw FWEH numeric trace recorded **16 Event69 packets** at firmware event ingress, whereas cfg80211 handler trace logged **6 PARTIAL + 1 terminal**. This is an important new observation, but without precise queue/drop reason instrumentation it **cannot be labeled packet loss**. It may involve stale/batched events, queue ordering, state transitions or processing of late events. Future source review should compare all timestamps, queue state, handler dispatch and filter outcomes before concluding.
- **Hidden SSIDs do not always block completion**: six handler BSS metadata records included **four zero-length SSID observations**, two nonzero length 13, all on **exact requested channel36** (`chanspec=0x1b24`, `ctl_ch=36`), all IE length bounds valid. Duplicate partial reports are present, so 4 hidden observations do not imply 4 unique hidden APs. Final cached/user result count **2**. No names or addresses logged.
- The radio scan completed **normally in 661ms**, not a ten-second watchdog. It is thus neither necessary nor supported to universally increase the timeout based on old failures.

## Receipt and integrity independently verified

Private Surface folder `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V17-2012-WIDE-EVENTS-20261027` contains `mz600-v17-owner-attempted.marker`, `mz600-v17-owner-COM9-private.txt`, `mz600-v17-owner-receipt.json` (all unique to this one-shot). Receipt asserts:
```json
{
  "root_bash_rc": 0,
  "independent_poststate_ok": true,
  "script_cleanup_ok": true,
  "permanent_install": false,
  "scan_requested": true
}
```
The saved private transcript SHA256 `85c6c460d7f453cb104ae69f6acbfa888d5642cda39abf45e8958d82f9cb0700` **matched** the owner's receipt after normalizing Windows CRLF to LF; independent helper returned `TRANSCRIPT_HASH_MATCH=True`. No raw transcript or nearby network identifiers published.

## The right next experiment: isolate event-mask vs idle Bluetooth

The V17 test **changed two potentially relevant conditions** relative to V16: (1) subscribing to extra firmware event codes 13/14/26/35/40/45/63, and (2) allowing loaded but inactive BT modules + HCI0 down, instead of demanding none loaded. It also added ingress/metadata printk and host runtime prep/restore, all potential timing perturbations. **Do not claim the extended event mask is the fix yet.** In fact the actual successful terminal notification was still Event69.

The next new SHA-pinned reversible owner test should **change one variable at a time**:
- **Option A (most direct, source-led):** Keep quiescent BT loaded and compare V17 broad event mask with a diagnostic that only subscribes Event69, retaining **identical ingress/metadata logging, dwell, channel and runtime prep**. If Event69 terminal still succeeds with same BT loaded, mask expansion may be unnecessary; if not, it becomes a strong lead.
- **Option B:** Keep V17 broad mask and temporarily quiesce/unload/reload BT **only if exact HCI restoration is proven safe**. Current UART HCI0 could disappear on unload; do not perform this blindly.
- In parallel audit ingress-vs-handler packet-count discrepancy and whether legacy 2012 firmware treats `event_msgs` bitmask as controlling internal scan-completion paths. Make sure no firmware event mask change silently enables radio transmission or illegal channels (still NO_IR PASSIVE).

**No further physical scan until a new unique one-shot design is grounded and safeguards approved.** Preserve one-shot history and source checks.
