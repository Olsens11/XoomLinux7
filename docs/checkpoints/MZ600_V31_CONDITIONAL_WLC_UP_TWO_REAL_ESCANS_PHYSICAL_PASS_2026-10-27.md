# MZ600 V31 — conditional Broadcom WLC_UP allows TWO normal ESCAN completions

**2026-10-27 PHYSICAL MILESTONE.** Status: **ONE successful two-scan, same-loaded-module hardware trial**, with an independent post-test rollback verification; **NOT YET a production-ready/upstream patch**. This directly follows [V30's measured firmware idle UP→DOWN](MZ600_V30_FIRMWARE_UP_LOST_BETWEEN_ESCANS_PHYSICAL_PASS_2026-10-27.md) and is grounded in [Broadcom-era driver precedents](../research/MZ600_BCM4329_MAINLINE_PEERS_AND_MPC_AUTO_DOWN_WLC_UP_2026-10-27.md).

## Private evidence and immutable test identity

- Replacement Motorola Xoom MZ600, Tegra 2/BCM4329, Debian internal p8 with Linux `7.0.0-next-20260422+`, original 2012 Motorola candidate BCM4329 firmware `4.218.248.44` via temporary RAM overlay.
- Surface trial **`up31a-01-mask000`**, receipt `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027\runs\up31a-01-mask000.json`, private trace `up31a-01-mask000.private.txt`, consumed `up31a-01-mask000.attempted`. **NEVER reuse this trial ID or overwrite its private evidence.**
- Receipt: `root_bash_rc=0`, `independent_poststate_ok=true`, `script_cleanup_ok=true`, `permanent_install=false`, `event69_terminal_success=true`, `scan_done_success=true`, `watchdog_fired=false`, `header_versions=[2]`, `header_event_samples=23`, `alt_events_total=0`, `iw_elapsed_ms=3210`, `userspace_bss=23`. The last two receipt fields are **last scan**, not a two-scan aggregate; full numeric trace proves both.
- SHA256 of private transcript: `70a5f08e613af475a5d794bc242044ac0c972212a6983248046db55ef36f52d2`. No private SSIDs/BSSIDs or MACs published.
- Trial-specific ARM `brcmfmac-2012-escan-conditional-up-v31.ko` **354,392B**, SHA256 `c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8`; matched WCC `brcmfmac-wcc-matched-v31.ko` **5892B**, SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`; private firmware 264140B SHA `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`.
- Lab source: [V31 source-restoring builder](../../tools/forensics/build_mz600_v31_conditional_fw_up.py), [scan and rollback](../../tools/forensics/v31/mz600-v31-normal-scan.sh), [COM9 owner one-shot](../../tools/forensics/v31/mz600-v31-owner-once.py), [owner-run launcher](../../tools/forensics/v31/resume-v31-on-surface.ps1). The first Surface fresh-staging launcher initially stopped before COM9 on a duplicate size check error; the user then ran **only the fresh/unused trial** with the verified safe resume launcher. This is not a repeated physical trial.

## The exact mechanism confirmed by REAL firmware reads and commands

V31 retains the normal V29 regulatory-preserving scanning path and all existing MPC behavior. Its only new firmware SET is conditional, **BCM4329 primary STA ifidx0/bsscfgidx0 only**: after the normal `mpc=0` operation, `WLC_GET_UP=162` checks actual controller UP. Only when GET succeeds and UP is precisely **0**, `BRCMF_C_UP=1` is sent once and another GET verifies UP=1. Otherwise the scan follows unchanged regular code (or fails closed if the read/UP is invalid). No always-on MPC0, reset, arbitrary delays, channel36/NO_IR/passive restrictions, hardware power sequencing or new firmware bytes.

### First normal multichannel scan (firmware already UP)

| dmesg time | Event | Exact numerical result |
| --- | --- | --- |
| 50244.852988 | Scan generation allocated | sync ID **4661** |
| 50244.857553 | before scan read | `WLC_GET_UP rc=0 up=1`, MPC1, host_ready1 / netdev_running1 |
| 50244.865365–50244.869950 | Existing MPC0 SET and readback | SET rc0; firmware UP1, MPC0 |
| 50244.877479 | New V31 UP precheck | rc0, UP1 |
| 50244.881059 | **No recovery command sent** | `WLC_UP sent=0 rc=0` |
| 50244.892947 | First firmware ESCAN | `ESCAN_SET_RC=0` sync4661 |
| 50247.703103 | Genuine Event69 terminal | `status=SUCCESS` (receipt/events), sync4661, 12B/version109 |
| 50247.735148 | Generation match | `TERMINAL_GENERATION_ACCEPT id=4661` |
| 50247.767218 | Normal cfg80211 callback | `aborted=0 fw_abort=0 owned=1` |
| 50247.805981–50247.819498 | Existing MPC1 restore | SET rc0, firmware UP1, MPC1 |
| User command | `iw dev wlan0 scan` | **rc0; 2999ms; 17 BSS** |

### Second normal multichannel scan — decisive controller recovery

| dmesg time | Event | Exact numerical result |
| --- | --- | --- |
| 50251.952616 | New generation | sync ID **4662**, same loaded module |
| 50251.962143 | Pre-scan firmware read | `WLC_GET_UP rc=0 up=0`; MPC1; host_ready1 / netdev_running1 |
| 50251.969330–50251.973622 | **Existing** MPC0 SET/readback | SET rc0; firmware **still UP0**, MPC0 |
| 50251.981271 | V31 conditional check | `UP_BEFORE_SCAN rc=0 up=0` |
| 50252.045482 | **Actual official Broadcom bring-up command** | `WLC_UP sent=1 rc=0` |
| 50252.054779 | Firmware immediate readback | `UP_AFTER_RECOVERY rc=0 up=1` |
| 50252.071519–50252.076901 | Second ESCAN actually accepted | sync4662; `ESCAN_SET_RC=0` |
| 50255.030116 | Genuine Event69 terminal | `status=SUCCESS` (receipt/events), sync4662, 12B/version109 |
| 50255.066332 | Normal generation match | `TERMINAL_GENERATION_ACCEPT id=4662` |
| 50255.102498 | Normal cfg80211 callback | `aborted=0 fw_abort=0 owned=1` |
| 50255.124206–50255.127584 | Existing MPC1 restoration | SET rc0; firmware UP1, MPC1 |
| User command | `iw dev wlan0 scan` | **rc0; 3210ms; 23 BSS** |

Suite explicitly reported **`MZ600_V31_SCAN_SUITE_RESULT completed=2 failure=0`**. Kernel evidence `MZ600_V31_EVENT69_STATUS_COUNTS success=2 partial=51 other=0`; real firmware terminal events (IDs4661 & 4662), two normal cfg80211 successful completion callbacks, no watchdog. This is much stronger than merely offering an ESCAN to firmware or completing via an artificial timeout. The conditional branch was **NOT** taken on scan1, **WAS** taken on scan2 precisely when firmware read DOWN. These results show a causal intervention in the tested sequence: restoration to UP1 immediately preceded the normally failing firmware ESCAN and enabled two real successes. **Still only one trial**, not proven universal/bisectable/race-safe.

## Cleanup and independent verification

- Script logged `MZ600_V31_CLEANUP_START rc=0 state=OBSERVATION_COMPLETE`, `UMOUNT_MATCHED_WCC_RC=0`, `UMOUNT_FIRMWARE_RC=0`, `ORIGINAL_FILES_AND_RADIO_RESTORED`.
- Both receipt flags `script_cleanup_ok=true`, `independent_poststate_ok=true`, and `permanent_install=false`.
- An **additional independently executed** existing Surface COM9 read-only safety preflight, `MZ600-V26B-REGSTATE-20261027\preflight-v26b.py`, returned **`V26B_INDEPENDENT_COM9_PREFLIGHT_PASS`** exit0 **after V31**. It verified original installed firmware, NVRAM, core, matched WCC hashes, no temporary bind overlays, wlan0 down, WPA active, BT quiet, COM9 available. No reboot, flash, permanent firmware or module replacement. The original source tree was hash restored after offline build.

## What this DOES and DOES NOT demonstrate

**YES:** exact-era vendor Broadcom `WLC_UP` precondition recovers controller UP0 after idle and makes a previously failed second normal multi-channel ESCAN succeed on the physical Xoom. Normal Linux cfg80211 remains the scan owner, true firmware status-SUCCESS event is routed, generation identity matches. This is the **first observed two-scan successful continuous module session** with OEM2012 firmware in this project.

**NOT YET:** why the firmware's MPC1 idle period makes it DOWN (MPC causality not isolated), whether firmware emits a usable UP/DOWN notification, repeated third/fourth/fifth scans, different idle durations or power modes, Wi-Fi authentication/association/DHCP, Bluetooth coexistence and shared power, sleep/resume, many Xoom units and firmware versions, multivif roles, query error/race/teardown behavior, dynamic PM impact or production upstream kernel patch acceptance. Avoid labeling all follow-up gates PASS. Do not add temporary MZ600_V31 debug instrumentation to a submission patch.

## Precise next engineering actions

1. Retain/commit this milestone and update G01–G12 ledger; do not overwrite trial, lose original hash receipts, or change boot/root.
2. Analyze **what exactly goes DOWN and when** with MPC1 idle, and whether an event is defined/delivered. Source comparison with A500/TF101 and original Broadcom remains relevant. The WLC_UP recovery works without answering that independent causality question.
3. Controlled hardware reliability series using **unique trial IDs, source-fixed exact module, same policy and proper rollback**, preferably 3–5 normal scans separated by realistic idle delays, including repeated conditional recoveries. Test error paths and no WLC_UP on already UP.
4. With consent and private credentials, standard association, auth, DHCP and sustained data after one or more idle periods. Do not copy regulatory/NVRAM across devices.
5. Extract only the **minimum generic-correct controller-ready logical issue** into WIFI-4 canonical review patch as appropriate, with comprehensive locking/lifetime/PM/regulatory and Kconfig compile validation. Prove each prefix, run checkpatch and other [G01–G12](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md). No autonomous human DCO/submit.

**Trust boundary:** User’s supplied code and raw private results stay on Surface. This report retains only numeric/non-identifying observations and SHA digests. V31 code remains LAB until those gates are met.
