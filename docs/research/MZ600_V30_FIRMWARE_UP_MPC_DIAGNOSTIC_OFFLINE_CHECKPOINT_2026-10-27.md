# V30: read-only firmware-UP / MPC observation — offline source and ABI verified

**Date:** 2026-10-27. **State: OFFLINE BUILD PASS, HARDWARE TEST NOT RUN.** This is a lab diagnostic only, not a kernel submission patch or a demonstrated firmware repair. The previously verified first V28 normal scan discovered 12 BSS, second scan returned Linux -52; a targeted older V27 result decoded firmware BCME_NOTUP (-4), but the cause is still **unknown**.

## Exact build and provenance

- Source: [`tools/forensics/build_mz600_v30_firmware_up_mpc_observation.py`](../../tools/forensics/build_mz600_v30_firmware_up_mpc_observation.py) in `Olsens11/XoomLinux7`, branch `wip/clean-wifi-bt-usb-20261025`, source correction commit `16966048b9fefa2ee7f4a3a6d28ba4151b943927`.
- Derived solely for measurement from **V29 regulatory-preserving native cfg80211** experimental code, including the earlier tested original Event69 owner route and generation identity. **Does not restore forced channel36, NO_IR, global passive scanning or fixed dwell.** This distinction matters: an earlier V28 scanning policy was physically tested, but V29 regulatory-preserving fallback had not yet had its own physical scan verified.
- Exact Linux 7 ARM ABI module `brcmfmac-2012-escan-state-v30.ko`: **353372 bytes**, SHA256 `c064cd5c23c50d423e1c09be106e61633bdf35ef57046d00f211e10659223738`, `vermagic=7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`.
- Matched `brcmfmac-wcc-matched-v30.ko`: **5892 bytes**, SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`. Never load the old installed WCC binary against a structurally changed brcmfmac core; **do not disable modversions**.
- Development host output under `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-2012-oem-escan-v30-state-observe-20261027/`, including immutable `offline-build-result.json` and `build.log`. Compilation returned success. Existing source at rest independently verified `cfg80211.c` SHA `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`, `cfg80211.h` SHA `89031854e21941889ca07315f693c53ef0b61b94c022bce5743cc204e003735e`, `fweh.c` SHA `4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c`. **No kernel or eMMC/firmware/NVRAM installed on the tablet**.
- Earlier build failures were **local builder errors**, not hardware results: initial generated source anchor no longer matched the V24 generation-aware code; second generated C used an improperly escaped format-string newline. Both issues were corrected. The second failure's build.log was preserved in `v064-2012-oem-escan-v30-failed-compile1-20261027/`; the original sources still passed SHA restoration.
- A Surface test harness preparation via connected remote file writing was **blocked by a safety check**. Do not invoke a different action to bypass that block. **No V30 Surface stage, one-shot COM9 test, firmware-UP measurement or second-scan result exists.**

## What V30 records

For BCM4329 only, `mz600_v30_read_fw_state()` calls read-only firmware command **`WLC_GET_UP=162`** via `brcmf_fil_cmd_int_get` and reads `mpc` via `brcmf_fil_iovar_int_get`. Both errors are recorded explicitly; unsupported firmware requests are **not** assumed to return false. Host measurements include `check_vif_up`, `netif_running` and `BRCMF_SCAN_STATUS_BUSY`. This is **numeric only**, never SSID/BSSID/password/calibration.

Probes occur at scan setup; after the driver's **existing** MPC=0 command; after existing ESCAN request; before existing MPC=1 at true scan completion; after it; and after error cleanup. The current `brcmf_set_mpc` actual firmware SET result is also logged, without changing its control flow or sending an additional MPC SET. The extra read commands may affect scheduling slightly; only a controlled experiment and A/B can assess timing impact. **No additional WLC_UP, WLC_DOWN, reset, radio enable, scan completion, state forcing, regulatory change or firmware file change** was added.

## Firmware-event protocol source audit

Current Linux 7 `cfg80211.c` explicitly registers `BRCMF_E_ESCAN_RESULT`, `BRCMF_E_LINK`, `BRCMF_E_IF` and connection/roam/deauth-related events. `core.c` registers `BRCMF_E_PSM_WATCHDOG`. However, a dedicated controller-UP/firmware-down event handler was **not found** in the inspected `brcmf_fweh_register` call sites. This **does not** prove the 2012 firmware lacks such an event or that a notification was lost; those questions require authoritative firmware event semantics and physical observation. The already-proven Event69 lost-route demonstrates why absence from a final callback is weak evidence of absence on the wire.

## Decision matrix once an authorized physical test can run

| Observation | Consequence |
| --- | --- |
| Read-only WLC_GET_UP unsupported on OEM2012 firmware | Mark unsupported; don't call a random numeric 162 write or infer UP from nonzero error; use supported firmware state proxies and code-path evidence |
| UP reads 1 before scan and 0 after real completion | Investigate exact transition, MPC and BSS/power lifecycle; don't add unconditional reset |
| UP remains 1 throughout but second ESCAN reports BCME_NOTUP | Investigate a firmware **BSS/interface**-specific UP prerequisite or ESCAN protocol state, not a generic dongle power failure |
| MPC SET returns nonzero or readback mismatches expected value | Review current BCM4329 NEED_MPC quirk and command sequencing/READY guard; don't merely duplicate current toggles |
| UP/MPC unchanged and successful | Investigate ESCAN action/status, request bytes/firmware state, event timing and synchronization |
| Both scans actually complete | Verify real terminal Event69 and **distinct** 16-bit sync IDs, normal cfg80211 callbacks, no watchdog, original runtime rollback; repeat before claiming reliability |

## Required test protections

Follow [the established Desktop→Surface→COM9 procedure](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md) and [G01–G12 upstream acceptance rules](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md). Before physical work, ensure no competing session, a fresh one-shot ID, matched WCC SHA, RAM-only original 2012 firmware overlay, original file hashes/rollback and a test script that captures **kernel numeric state even if second scan fails**. A clean offline module is **not** a real-world test result. Never publish private scan outputs or credentials, never load in permanent partitions, and never resume remote writes after a safety block without explicit authorized workflow.

**Current exact next technical step:** run the read-only V30 normal multi-channel test in an authorized controlled environment, compare UP/MPC/readiness and firmware ESCAN errors across both scans, then design the smallest causal correction and **update the appropriate canonical logical patch in place**. No new upstream patch/fix has been promoted.
