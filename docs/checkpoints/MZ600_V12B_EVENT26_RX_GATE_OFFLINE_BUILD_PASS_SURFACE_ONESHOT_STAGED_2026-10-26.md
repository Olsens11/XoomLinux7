# MZ600 v12b BCM4329 event-26 RX path stage counters — exact-ABI build PASS, Surface one-shot STAGED, physical experiment NOT RUN

**October 26, 2026 — latest verified state.** v12a established original HRI39 firmware `event_msgs GET rc0 len27 registered1 driver_bit1 fw_bit1 map0`, but scan-completion event26 callback was not seen, and scan still completed via modern ~10s timer. [Read actual v12a hardware checkpoint](MZ600_V12A_EVENT26_FIRMWARE_EVENTMSGS_BIT26_READBACK_PHYSICAL_PASS_2026-10-26.md) and [canonical handoff](../handoffs/MZ600_XOOMLINUX7_V11_CURRENT_STOPPING_POINT_2026-10-26.md) first. **Do not repeat v12a**.

## What v12b actually changes (observation only)

Experimental standalone builder `scripts/experiments/build-v064-bcm4329-legacy-event26-rx-gates-v12b-20261026.py` layers on v12a's verified v11/v10/v9 etc source from the exact Linux7 tree. It appends a **sanitized 13-stage set of atomic counters**, recording only integer totals, never MAC, SSID, BSSID, security IE, radio packet content, or proprietary OEM bytes. `brcmf_v12b_event_note()` has a BCM4329 chip gate, and two `brcmf_v12b_event_report()` snapshots are triggered **before the proven legacy passive `WLC_SCAN=50` call** (`stage=start`) and at the existing **~10s escan timeout** (`stage=timeout`, before results diagnostics). The new counter hooks are in `fweh.h`, `fweh.c`; cfg80211.c adds only two logging invocations beyond v12a.

Per-module counter definitions (all numeric, not packet contents):
| Counter | Exact increment stage / meaning |
|---|---|
| `skb` | `brcmf_fweh_process_skb()` called for an RX skb handed to event classifier after protocol/header extraction |
| `link` | skb EtherType `ETH_P_LINK_CTL` matched |
| `length` | event packet meets `sizeof(struct brcmf_event)` minimum |
| `subtype` | optional expected vendor-long subtype check passed |
| `oui` | Broadcom 3-byte vendor OUI matched |
| `user` | Broadcom event user subtype matched |
| `raw26` | after all skb header gates, event type BE32 exactly `BRCMF_E_SCAN_COMPLETE=26` |
| `proc26` | entered `brcmf_fweh_process_event()` with raw event code 26 |
| `registered26` | code range valid and 26 handler registered in fweh |
| `size26` | bounded payload-length validation passed |
| `queued26` | successful event allocation copied and about to queue |
| `worker26` | dequeued on firmware-event worker |
| `handler26` | about to invoke event26 handler through existing dispatch |

The staged scan prints **start and timeout snapshots**, firmware mask readback and unchanged legacy 51 result counts. This differentiates no link-control RX, header filtering, event dispatch dropping, and handler-layer arrival. `skb=0` does **not** prove firmware never emitted an event; an earlier SDIO transport/hdrpull failure could prevent packets reaching this observation point. Events detected in unrelated phases must be correlated using start-vs-timeout deltas. **No firmware event mask SET, ioctl change, country write, scan-completion speedup, cfg80211_scan_done ownership, timeout/cancel/race change or root filesystem install.** It does not collect or commit identities.

## Exact reproducible offline build evidence

Host: authorized Windows DESKTOP-R16QJD4 → Ubuntu-22.04 WSL user `xoomdev`. Existing kernel source `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux` and exact-ABI compiled `v064-bigpart-debian-sdroot-build`. Target `7.0.0-next-20260422+`, `modversions`, ARMv7 p2v8.

- Candidate first try compile failed before module output because `fweh.c` had not included `brcm_hw_ids.h` for BCM4329 chip-ID macro; source/module/object rollback checks passed. Original failed one-shot output directory left as diagnostics.
- Corrected revision `v064-legacy-event26-rx-gates-v12b-r1-20261026` imports chip-ID definitions, compiled **exit0** with output:
  `OFFLINE_INPUT_ABI_SHA_AND_PATCH_PREFLIGHT_PASS`,
  `OFFLINE_SOURCE_AND_ORIGINAL_MODULE_RESTORED_VERIFIED`,
  `BUILD_STATUS=0`,
  `V12B_EVENT_RX_STAGE_OBSERVATION_ONLY_BUILD_PASS`,
  `V12B_ALL_AUX_SOURCE_AND_MODULE_OBJECTS_RESTORED_VERIFIED SUCCESS`.
- Generated module `brcmfmac-legacy-event26-rx-gates-v12b-r1.ko`: **349520 bytes SHA256 `48bf1d3f5cc163f33419e3ebddaa4b50067096e6c1954ced578568c86c75f5b6`**, independent Desktop/Surface SHA verified.
- Exact source patch `0012b-lab-only-bcm4329-event26-rx-stages.patch`: **SHA256 `8074badeb1c42b294cb98d24133d6aa1e97c0ed5c0993a152795bd9fd403e3ca`**; `git -C <original kernel source> apply --check <patch>` exit0 after source restoration.
- Original exact ABI module `brcmfmac.ko` independently verified **`9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`** restored. All fweh.h/fweh.c source bytes and prior generated source/build object artifacts were byte-for-byte restored. The builder itself never accesses Xoom, scans, flashes or installs.

## Surface staging and owner's ONE PHYSICAL next action

**All four staged inputs independently checked ON SURFACE-BOOK-2** under private `C:\Users\olsen\xoom-linux-rom\captures\`:
1. `MZ600-BRCMFMAC-V12B-EVENT26-20261026.ko` **349520B**, SHA `48bf1d3f5cc163f33419e3ebddaa4b50067096e6c1954ced578568c86c75f5b6` (Desktop WSL artifact → Desktop Windows SHA check → authenticated `devdesktop` SCP → Surface Windows SHA check).
2. `MZ600-V12B-USER-ONESHOT-SCAN-20261026.sh` **9373B / 207 lines**, SHA `ed3f95cc9b67ee1bbaf9feb240f2cb03da2f15a0638193b21c0a064435594c23`. GitHub source: `scripts/host/xoom/test-v064-hri39-v12b-event26-rx-gates-one-shot-20261026.sh`; independent Desktop `bash -n` exit0. Proven v12a conservative RF, calibration SHA, module hierarchy and cleanup with **v12b NEW all-unique** once markers and paths. Adds log presence requirement for 2 event counter snapshots.
3. `MZ600-V064-V12B-EVENT26-RAM-SERIAL-UPLOAD-20261026.py` **4764B** SHA `5b2bfa9dbe5c05e545f1b62bb1104eb802edcfc28a80aa07e1478a9248a2cf64`, new unique v12b transfer ACK/receipt and RAM `/run/mz600-v064-legacy-v12b-event26-rx-gates-20261026.ko`. No insmod inside uploader.
4. `MZ600-V12B-USER-ONE-SHOT-20261026.py` **12537B** SHA `10264defa3fb39d76a0ff49a6e8d1ba1c23e48db3545d20a2a2632b2cd66940e`; pinned triple SHA, root ABI/p8 and no-radio checks, unused RAM target, invokes uploader once, on-Xoom `bash -n`, one passive NO_IR ch36 scan, strict timeout and numeric-only markers, independent COM9 original environment audit, unique private receipt. `py_compile` passed for both Python scripts.

A new **host-only** `MZ600-V12B-STATIC-PREFLIGHT-20261026.py` passed `V12B_SURFACE_STATIC_TRIPLE_SHA_GUARD_AND_PATHS_PASS`, explicitly `V12B_OWNER_PHYSICAL_SCAN_NOT_STARTED`. New v12b COM9 private transcript, owner JSON receipt and upload JSON receipt **all ABSENT** before owner physical run. The owner has not executed v12b and no COM9 interaction or Xoom state change was made while creating/staging these files.

**ONLY WHEN AT SURFACE-BOOK-2 WITH THE ORIGINAL XOOM CONNECTED**, stop an existing COM9 terminal using Ctrl+] and use Windows PowerShell:

```powershell
python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V12B-USER-ONE-SHOT-20261026.py"
```

This is a **user-operated**, once-only guarded RF experiment. It will refuse reruns if its private run receipt or transcript exists or if the Xoom baseline has changed. Do **not** run the script from Desktop, do not run v12a again, do not change module paths/hashes, do not omit required physical gates.

After owner run, inspect Surface `MZ600-V12B-USER-ONESHOT-RECEIPT-20261026.json` and matching `MZ600-V12B-USER-ONESHOT-PRIVATE-COM9-20261026.txt`, validate actual shell exit, both `stage=start` and `stage=timeout` numeric counters, raw26→handler26 causal sequence, scan ioctl50/51, version108 BSS validation, no IDENTITIES, rollback ordered modules+overlay teardown and independent audit. Record the ***measured*** ingress outcome and the immutable transcript/receipt hashes, not predictions. **Do not claim event26 delivery or faster scan yet.**

## Subsequent plan

If `skb>0`, inspect progressive stage counters to identify the earliest drop. If `skb=0` or `link=0`, trace SDIO RX transport/hdrpull earlier; if `raw26=0` despite other valid firmware events, original HRI39 may not emit `SCAN_COMPLETE` for this passive ioctl50 mode (further OEM source audit needed). If `raw26>0` but callback remains absent, focus exact gate/queue where count stops. Only **after** an authenticated complete event or trustworthy firmware scan-done predicate exists, design an isolated race-safe exactly-once cfg80211 completion patch. Never use results count0/count>0 as proof of termination. Maintain generic FW2.4G and other Xoom variants regressions, BT shared power ownership, NO_IR, no MAC overrides and no upstream sign-off without owner's explicit approval.
