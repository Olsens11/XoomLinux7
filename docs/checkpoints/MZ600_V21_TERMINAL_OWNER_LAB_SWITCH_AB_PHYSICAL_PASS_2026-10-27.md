# MZ600 V21 — real Event69 terminal routed to active Linux scan owner (PHYSICAL LAB PASS, NOT UPSTREAM PATCH)

**Date:** 2026-10-27. **Device:** experimental MZ600, Linux `7.0.0-next-20260422+`, Debian armhf. **Scope:** native Broadcom BCM4329 2012 firmware ESCAN status0 handoff to Linux; NO_IR 5180MHz channel36, passive 500ms firmware dwell, no directed SSID, no association. **Result:** two physically observed terminal-owner redirections completed the actual scan normally; negative control reproduced the original watchdog. **This proves this narrowly gated lab behavior, not a general ABI/root-cause fix or an upstream-ready patch.**

## Inputs and source provenance

- Git development branch `wip/clean-wifi-bt-usb-20261025`; SHA-pinned V20 builder is the source-restoring baseline. New V21 offline builder: [`tools/forensics/build_mz600_v21_terminal_owner_probe.py`](../../tools/forensics/build_mz600_v21_terminal_owner_probe.py), final build-source commit `f712b58bb4159fa1c60507f5180d449a815c83fb` (prior staged revisions `0312341`, `61e4785`), builder SHA256 `fbe5d26c031fe54ce66dceae09eeccb428f7a7d560c6234786c589f68cb1bfff`.
- Exact-ABI ARM lab module `brcmfmac-2012-escan-terminal-owner-v21.ko`: **350,476 bytes**, SHA256 `aa222e2bebe47b76649dacabeddfd3d6fe823813a74c267b73c82813fcd13741`. `vermagic` `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`. The original host `fweh.c` SHA `4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c` and baseline module SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb` were restored by source-restoring builder; the first V21 compile initially failed on wrong `vif_cnt` API and escaped format string and was corrected before successful build. No change to production module on disk.
- Private OEM 2012 firmware `4.218.248.44`: **264,140 bytes**, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`; temporary RAM bind overlay only. The installed firmware SHA `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`; NVRAM SHA `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb` unchanged.
- **Exactly the normal, documented transfer procedure**: desktop WSL → desktop Windows staging → temporary Python HTTP on LAN **43157** → Surface PowerShell `Invoke-WebRequest` → exact 350476-byte hash check → server closed and staging removed. [Mandatory standard transfer runbook](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md). Do not repeat the earlier nonstandard 43158/nested-PowerShell approaches.
- Surface private staging `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V21-2012-HEADER-20261027\`. Surface guarded Bash runner SHA256 `ce8a784a0c646f1bbe947e44598d2449b6331256b196f9d2c689febc1d1703f1`; Python owner-suite SHA `7a43cfb21df00aa174266a23c800434d12279af3bf64beabf8f6551033085c2d`. **Important:** the Bash/Python local trial metadata calls its switch `mask` for historical compatibility, but this experiment fixed `mz600_extra_events=0` and changes only `mz600_terminal_owner=0` vs `1`; these are NOT subscription-mask sweeps. Retain consumed scripts/hashes unchanged. Kernel logs used a unique `/dev/kmsg` marker rather than unsafe `dmesg | wc -l`, resolving V20 log rollover error.

## Deliberately narrow source change

New read-only-after-load `mz600_terminal_owner` bool parameter defaults OFF. At firmware-event worker, only consider real `BRCMF_E_ESCAN_RESULT` Event69 with header `version=2`, `status=SUCCESS`, on BCM4329, when firmware-index lookup would otherwise fail (missing or >=16 bsscfg). Require existing external `scan_request`, BUSY state, `WL_ESCAN_STATE_SCANNING`, **one** active interface/list member and the recorded `cfg->escan_info.ifp == drvr->iflist[0]` with valid vif/netdev, and no internal scan buckets. Only then pass the original terminal event unchanged to the real scan owner's existing handler. Normal Event69, partial BSS events, other chips/event codes, firmware, timeout behavior and scan parameters are not modified. The event itself is **never fabricated**.

The implementation is **a controlled hypothesis test**, not a generic permanent correction: scan request presence and the fixed `sync_id=0x1234` do not by themselves bind old delayed events to the correct scan generation; race/teardown and P2P/multi-interface cases remain unproven. We do **not** yet know why the version-2 event's `bsscfgidx` sometimes reads as 0, 1 or 16.

## Six independent physical trial results, same module and firmware

Every trial executed one authorized passive ch36 scan with distinct consumed `.attempted` marker, `root_bash_rc=0`, `script_cleanup_ok=true`, `independent_poststate_ok=true`, `permanent_install=false`. All numeric results below from owner-private COM9 log + JSON receipts.

| Trial | Terminal-owner switch | Terminal ver2 `ifidx,bsscfgidx` | V21 fallback actually executed? | Scan time | iw BSS | scan_done | Interpretation |
| --- | ---: | --- | --- | ---: | ---: | --- | --- |
| `term1-01-mask000` | OFF | `2,16` | No | 10,476 ms | 0 | watchdog aborted=1 | **Negative control reproduces lost terminal** |
| `term1-02-mask001` | ON | `42,0` | No, ordinary event route | 1,388 ms | 3 | aborted=0 | Success **cannot** be attributed to fallback |
| `ba21-01-mask001` | ON | `1,1` | **YES**, owner eligible=1 | 1,642 ms | 3 | aborted=0 | **First causal lab delivery proof** |
| `ba21-02-mask000` | OFF | `0,0` | No | 1,613 ms | 3 | aborted=0 | Normal intermittent success with switch OFF |
| `ba21-03-mask001` | ON | `2,16` | **YES**, owner eligible=1 | 1,232 ms | 3 | aborted=0 | **Second delivery proof; same invalid index16 as failing control** |
| `ba21-04-mask000` | OFF | `0,0` | No | 1,654 ms | 3 | aborted=0 | Normal intermittent success with switch OFF |

**Causal observation A:** In off control `term1-01-mask000`, *real* terminal Event69 status0 arrived with `bsscfgidx=16`, was dropped in worker, and scan watchdog eventually aborted. No Event69 terminal was delivered to the cfg80211 handler.

**Causal observation B:** In on trial `ba21-01-mask001`, the genuine terminal had `version=2 status=0 bsscfgidx=1`. Kernel explicitly logged `MZ600_V21_TERMINAL_OWNER_CHECK raw_bsscfg=1 eligible=1 owner_mode=1`, followed by `MZ600_V21_TERMINAL_OWNER_DELIVER status=0 raw_bsscfg=1`, then `MZ600_V21_SCAN_COMPLETION aborted=0 fw_abort=0 owned=1` and `MZ600_V21_FWEH_DISPATCH code=69 status=0 ifp=1 handler_rc=0`; `iw` saw 3 BSS after 1642ms.

**Causal observation C:** On trial `ba21-03-mask001` produced terminal `ifidx=2 bsscfgidx=16`, with the same eligible-owner and delivery markers, then **normal** `cfg80211` scan_done aborted0 with 3 BSS at 1232ms—demonstrating that the same invalid index as the earlier OFF timeout can be interpreted by Linux successfully with the eligible owner route. The fallback itself does not correct partial event losses; that was intentionally out of scope.

**Interpretation:** ON trials 3/3 completed with BSS3, including **2/3 where the fallback actually fired**; OFF trials 2/3 completed through ordinary valid index0 routing and 1/3 timed out on index16. These are strong controlled proof-of-mechanism observations, but not enough to claim universal reliability or patch-quality lifetime safety. Nothing was installed persistently.

## Privacy-safe evidence ownership

Exact original transcripts and receipts remain PRIVATE on the Surface in `runs/term1-*.private.txt`, `runs/ba21-*.private.txt` and matching `.json`/`.attempted`; never push SSIDs, BSSIDs, private MACs or proprietary firmware. Local `analyze-v21-numeric.py` computed the above from saved files. For reproducibility, private log SHA256:

| Trial | Private transcript SHA256 |
| --- | --- |
| `term1-01-mask000` | `33cdb096bfda117e202b8645226997d3f1446f9b621c443fbf3fcd418e3ff496` |
| `term1-02-mask001` | `264fa3165085f100b5f8d266e6184c6adb4de55c8942cc0b87f64e6d8702a47e` |
| `ba21-01-mask001` | `4baf01c09bd689bf474352d1fd01477665906825cbb2e451d1446276496d5124` |
| `ba21-02-mask000` | `02db179d60714c9382b6fd23efdf19bb9f3f49a91eb1486b3bf197c7b354a24c` |
| `ba21-03-mask001` | `5363ae7dacfd433286ecc56bd8006c5d9c4e4360ba6be0b848c2b473cf0d84de` |
| `ba21-04-mask000` | `cc9eb84d9cb45b685a6a99e6908c8e70a7391e1a9111014103c6cbaa80e4a4c6` |

After final test suite, separate **independent read-only COM9 preflight again PASSED**: original firmware/NVRAM/module SHA, Linux 7 kernel, root p8, wlan0 down, WPA service active, Bluetooth service inactive/HCI down, no firmware overlay. Desktop staging/server removed. No flash, no permanent firmware or driver changes.

## Next engineering steps and upstream patch gates

1. **Freeze V21** as evidence-backed, reversible lab prototype. Never mislabel it as upstream-ready; preserve SHA, source builder, local test receipts and negative trial.
2. Precisely define *which* firmware event interface attribution is legacy/nonstandard and whether a generic driver-side scan ownership selection or normalized decoding rule is preferable to a BCM4329-only fallback. Do **not** assume the firmware emitted corrupt bytes; the interface indices may be misinterpreted by host parser. Avoid revisiting broad event-subscription tests.
3. For any candidate production patch, prove scan generation binding, late-event/cancellation/timeout races, interface lifetime/synchronization, P2P/multi-BSS, supported firmware variants, 2.4/5GHz, Bluetooth coexistence and representative device variants. Test fallback off/on with same ABI where meaningful.
4. Maintain the distinct `wifi: brcmfmac` logical patch slot in [whole-chip integration ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md), then extract the minimal source diff, independent regression tests and proper commit description when causality and scope are sufficiently established. Do not add DCO sign-off or submit upstream without explicit owner approval.

**Current gate verdict: V21 terminal-only mechanism PHYSICAL PASS; multi-device/upstream patch readiness OPEN.**
