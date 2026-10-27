# MZ600 V30 — physical proof of firmware controller-UP loss between normal ESCAN requests

**Date:** 2026-10-27 (local afternoon). **Evidence:** ONE real hardware test under normal multichannel cfg80211 policy; one independent post-test COM9 integrity verification. **Overall two-scan suite FAILS** because second ESCAN is rejected. **Specific hypothesis of firmware UP→DOWN transition is PHYSICALLY CONFIRMED.** This is not yet a causal fix, repeat-scan solution, or upstream patch submission.

## Authoritative private evidence and source

- Surface DUT receipts: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V30-UPSTATE-20261027\runs\up30a-01-mask000.json` plus `up30a-01-mask000.private.txt` and consumed `.attempted` marker. **Never reuse trial ID** or overwrite private transcript.
- Receipt: `root_bash_rc=38`, `independent_poststate_ok=true`, `script_cleanup_ok=true`, `permanent_install=false`, `event69_terminal_success=true`, `scan_done_success=true`, `watchdog_fired=false`, `header_versions=[2]`, `header_event_samples=17`, `alt_events_total=0`, `iw_elapsed_ms=3263`, `userspace_bss=19`. Note: these latter two values describe **the first successful** scan; they do **not** mean second scan succeeded. Raw transcript SHA256 `659472b159b844c3f0364c42b96e6bebd32f744650f4517cefe913089123803f`. Private SSIDs/BSSIDs/MACs are not reproduced.
- Source: [`tools/forensics/build_mz600_v30_firmware_up_mpc_observation.py`](../../tools/forensics/build_mz600_v30_firmware_up_mpc_observation.py), from V29 *regulatory-preserving* normal-scan source; the diagnostic adds numeric reads `brcmf_fil_cmd_int_get(ifp,162,&fw_up)` (Broadcom `WLC_GET_UP`) and `brcmf_fil_iovar_int_get(ifp,"mpc",&mpc)`, plus original MPC SET return logging at existing call sites. No new MPC SET, UP/DOWN/reset, event subscription, scan-policy change, country/regulatory flag override, firmware binary edit or persistent install. V30 first normal scan is a *physical test of this V29-derived source with extra state probes*, **not** of an uninstrumented finalized V29 patch.
- Exact module: `brcmfmac-2012-escan-state-v30.ko`, **353,372 bytes**, SHA256 `c064cd5c23c50d423e1c09be106e61633bdf35ef57046d00f211e10659223738`; paired WCC 5892 bytes SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`. Private original 2012 Motorola firmware 264140B SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` mounted in RAM only; no distribution authorized.
- One-shot user-controlled trial launched from [`tools/forensics/v30/run-v30-on-surface.ps1`](../../tools/forensics/v30/run-v30-on-surface.ps1), [host harness](../../tools/forensics/v30/mz600-v30-owner-once.py) and [Bash test](../../tools/forensics/v30/mz600-v30-normal-scan.sh), all SHA verified. Desktop-to-Surface transport used existing 43157 SOP. Temporary LAN server shut down; no listener remained when checked.

## Actual exact firmware readback — new breakthrough

All `WLC_GET_UP` and `mpc` getter calls returned **`rc=0`**; the firmware explicitly reported the listed values. Both existing `mpc` setter calls returned `rc=0`. Host `host_ready=1`, `netdev_running=1`, `scan_busy=1` in **every** measured probe (busy bit set within a running scan; no evidence of an existing earlier request at entry). No unverified readback was interpreted as a value.

| Linux dmesg timestamp (s) | Probe | Firmware `fw_up` | Firmware `mpc` | Evidence |
| ---: | --- | ---: | ---: | --- |
| 44948.417398 | before first scan, following NEW_SCAN_GENERATION id4661 | **1** | 1 | Host READY1, Linux netdev running1 |
| 44948.424692 | original `mpc=0` SET | — | — | `rc=0` |
| 44948.429294 | after original `mpc=0` SET | **1** | 0 | Controller stays UP |
| 44948.439234 | first ESCAN request effective sync ID | — | — | **4661** |
| 44948.443881 | first `escan` iovar | — | — | `ESCAN_SET_RC=0` |
| 44948.560352 | after first accepted ESCAN | **1** | 0 | UP |
| 44951.523648 | genuine Event69 SUCCESS fixed 12B | — | — | result version109, `sync_id=4661` |
| 44951.561291 | kernel validates Event69 generation | — | — | ACCEPT id4661 |
| 44951.599094 | existing scan-completion callback | — | — | `aborted=0 fw_abort=0 owned=1` |
| 44951.615278 | completion before original `mpc=1` | **1** | 0 | UP |
| 44951.643095 | original `mpc=1` SET | — | — | `rc=0` |
| 44951.646617 | immediately after original `mpc=1` | **1** | 1 | UP **at this instant** |
| 44955.729299 | second generation allocated | — | — | **4662** |
| 44955.739464 | before second scan / before original MPC=0 | **0** | 1 | Host still READY1/netdev running1 |
| 44955.747468 | original `mpc=0` SET | — | — | `rc=0` |
| 44955.752176 | after original MPC=0 | **0** | 0 | DOWN; setting MPC=0 alone did **not immediately restore** UP |
| 44955.765073 | second request effective ID | — | — | **4662** |
| 44955.770682 | second `escan` iovar | — | — | `ESCAN_SET_RC=-52`; `iw` `Invalid exchange (-52)` |
| 44955.786673 | after rejected ESCAN | **0** | 0 | DOWN |
| 44955.797055 | original error path `mpc=1` SET | — | — | `rc=0` |
| 44955.803023 | after error MPC restore | **0** | 1 | DOWN |

**Most important fact:** firmware-UP changed from **1 after completion's successful MPC=1 command** to **0 before the next scan**, a gap of about **4.09 seconds** between those snapshots. The exact transition time within that interval was **not measured**. Firmware UP remained0 despite subsequent MPC=0 and the second ESCAN's normal command submission. This explains why `BCME_NOTUP` is highly plausible; V27 separately decoded the underlying `BCME_NOTUP=-4` in an analogous second ESCAN. **V30's numeric module logged only Linux `-52`; do not claim it independently decoded the Broadcom `-4` result.**

First userspace scan: `iw rc=0`, **3,263ms**, **19 BSS**, genuine Event69 normal cfg80211 completion; no watchdog. Second scan: `iw rc=204`, error `Invalid exchange (-52)`, one-scan-success/one-scan-failure shell `rc=38`. This **does not** constitute two successful scan completions. No active association attempted, and private network identities remain local.

## Source-path and notification audit

On the exact pinned Linux source `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`:

- `brcmf_scan_config_mpc` at ~1025 calls `brcmf_set_mpc` under the BCM4329 `NEED_MPC` quirk; its host-ready guard at ~1031 does **not** read `WLC_GET_UP`. A successful `mpc` iovar write and host-vif readiness **do not themselves imply internal firmware UP**.
- `brcmf_notify_escan_complete` at ~1183 uses the existing normal cfg80211 completion and at ~1227 calls `brcmf_scan_config_mpc(ifp,1)`. **There is no explicit `BRCMF_C_DOWN` command in that completion path.**
- `brcmf_config_dongle` at ~7782 calls `BRCMF_C_UP` only during initial host configuration and later uses a cached `cfg->dongle_up` state. A firmware idle DOWN transition could be invisible to that host cache; no evidence yet that `cfg->dongle_up` actually changed.
- Explicit `BRCMF_C_DOWN` calls at lines ~5223/5399/5412 are AP configuration/teardown paths, **not the normal ESCAN completion**. There may be other vendor/module/bus/firmware-internal behavior not visible through these inspected calls; do **not** claim no software path anywhere ever sends DOWN.
- The currently inspected `brcmf_fweh_register` sites subscribe to conventional LINK/IF/ESCAN/connection and PSM watchdog events. No **confirmed** unsolicited controller-UP-state event was proven or traced in this experiment. A lack of a subscription or `alt_events_total=0` does **not** prove firmware never emits a state-change notification. Prior real Event69 was lost in another code path despite arriving physically.
- MPC is a plausible *correlate* because DOWN was first observed after MPC restored to1, but this test does **NOT establish that setting MPC=1 caused UP=0**. The actual transition time, internal state machine and any independent idle timer are unknown.

## Independent restoration / no lasting modifications

The on-device script logged `MZ600_V30_CLEANUP_START rc=38` followed by `MZ600_V30_ORIGINAL_FILES_AND_RADIO_RESTORED`. Host receipt shows `script_cleanup_ok=true`, `independent_poststate_ok=true`, `permanent_install=false`. On 2026-10-27 **after inspecting V30**, an additional **independent read-only COM9 preflight** was executed via the proven `MZ600-V26B-REGSTATE-20261027\preflight-v26b.py` and returned `V26B_INDEPENDENT_COM9_PREFLIGHT_PASS` with exit0: original installed firmware/NVRAM/core/WCC hashes, no bind overlays, `wlan0` down, WPA active, Bluetooth quiet, intact COM9/kernel. The original source code on desktop was restored after the V30 offline ARM build. **No reboot, permanent module update, firmware flash or persistent rootfs modification was performed.**

## Minimal next research, without a false fix

1. **Read-only causal timing/source audit:** check whether any tracked normal-mode firmware event, SDIO idle/runtime PM behavior or Broadcom internal MPC routine transitions controller-UP after `mpc=1`; measure controller UP at several times **within the ~4s postcompletion gap** without changing normal scan policy or emitting extra RF requests, while recording whether `BRCMF_C_DOWN`/BSS-down requests occurred. A read-only snapshot schedule may itself perturb firmware timing; document it.
2. **One-variable causal A/B only if justified:** compare the original production MPC completion behavior with a temporary, strictly defined, RAM-only altered post-scan MPC policy on **new unique trials**. If keeping MPC0 prevents firmware-UP=0 and enables two genuine Event69 completions, that implicates the idle power-management transition but does **not** justify permanently disabling power saving. Alternatively test an evidence-supported official controller bring-up path at next scan, only after evaluating firmware protocol and shared BT/power implications. No blanket reset, speculative wait, permanent MPC-off, or fake scan done.
3. **Actual desired production behavior:** standard cfg80211 scan, legitimate regulatory permissions, successful controller readiness protocol, genuine terminals and distinct sync IDs on multiple scans, no watchdog, then user-authorized network association/authentication/DHCP. Refactor into properly scoped, G01–G12 compliant canonical patches; keep V30 debug logs/knobs outside upstream code.

**Status:** verified firmware controller-UP loss while host remains ready, real firmware reads supported; causality, notification semantics, power state management and generalizable fix still OPEN. Consult [standards](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md) and [handoff](../handoffs/MZ600_XOOMLINUX7_COMPREHENSIVE_CANONICAL_PATCH_AND_WIFI_HANDOFF_2026-10-27.md) before implementing fixes.
