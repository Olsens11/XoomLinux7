> **2026-10-27 LAB DIAGNOSTIC BUILD UPDATE:** [V30 offline/blocked-hardware checkpoint](MZ600_V30_FIRMWARE_UP_MPC_DIAGNOSTIC_OFFLINE_CHECKPOINT_2026-10-27.md). The source-restoring exact-ABI, V29 regulatory-preserving read-only WLC_GET_UP/MPC probe compiled and restored original sources; core SHA `c064cd5c23c50d423e1c09be106e61633bdf35ef57046d00f211e10659223738`. The remote Surface script-writing operation was **blocked by a safety check**; no physical V30 measurement or hardware state change occurred. Continue under an authorized deployment path; do not claim confirmed firmware UP/DOWN state or send resets.

# BCM4329 second ESCAN `BCME_NOTUP` — upstream and Broadcom source comparison

**Date:** 2026-10-27. **Research-only; no device, firmware, or kernel module changed.** This memo follows the comprehensive MZ600 handoff and V27/V28 physical checkpoints. It is designed to select a **single high-information** hardware observation, not guess another workaround.

## Actual physical stopping point

- V28 OEM2012 firmware: first **normal multichannel** `iw dev wlan0 scan` succeeded with **12 BSS / 2834ms**; second request in same loaded driver failed Linux `-52` in ~50ms. This is not caused by our removed channel36/forced-passive/NO_IR test restrictions.
- In a comparable isolated V27 sequence, `fwil.c` instrumented original firmware error `-4` on the second `escan` iovar; Broadcom maps `-4` to **`BCME_NOTUP`**. The later V28 test did not repeat that vendor-specific readout independently. Preserve this distinction.
- V26b generated host scan ID 4662 on the second request, so host-side generation increment is not the reason for early rejection. No second true Event69 completion was possible when firmware refused the iovar.
- Nothing yet proves a power-rail failure, interface state change, scan-ID incompatibility or successful firmware workaround.

## External source research: existing common mechanisms

1. [Broadcom BCM4329-era `wlioctl.h`](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/include/wlioctl.h) explicitly defines **`WLC_GET_UP=162`**; older and newer Broadcom headers consistently retain command 162, and `WLC_UP=2`, `WLC_DOWN=3`. This provides a **read-only firmware interface-up query**, separate from Linux `IFF_UP` or brcmfmac's host `BRCMF_VIF_STATUS_READY`. Whether the exact OEM2012 firmware supports this query must be tested (a failed/unsupported query is not evidence of UP or DOWN).
2. [Broadcom driver `wlc_mac80211.c`](https://android.googlesource.com/kernel/common.git/+/ff29ee8f9301c38f28d4d22fe49373d3b996956e/drivers/staging/brcm80211/sys/wlc_mac80211.c) shows that several firmware iovars return `BCME_NOTUP` when `wlc->pub->up` is false, because of `IOVF_*_UP` guards. This is a **source-example mechanism**, not proof that the OEM2012 `escan` iovar uses that exact conditional. It motivates measuring actual controller UP state before altering firmware.
3. [Current upstream Linux `brcmfmac/feature.h`](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.h) defines `BRCMF_FEAT_QUIRK_NEED_MPC` as **driver must disable MPC during scanning**. The pinned xoom-linux kernel has this quirk **specifically enabled for BCM4329** (`feature.c` around line361). In `cfg80211.c`, `brcmf_do_escan` calls `brcmf_scan_config_mpc(ifp,0)` before the firmware `escan`, and `brcmf_notify_escan_complete` calls `brcmf_scan_config_mpc(ifp,1)` upon completion. Upstream Linux uses the **same pattern** (see [current implementation](https://kernel.googlesource.com/pub/scm/linux/kernel/git/netdev/net-next/+/2929c2568c9be9deda15aa8dbf93a8c67508e4fc/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c)). **Do not add duplicate MPC toggles or assume toggling itself fixes the problem.**
4. The pinned Linux source `brcmf_set_mpc` only invokes `brcmf_fil_iovar_int_set(ifp,"mpc",value)` if **host vif READY**; failures log `fail to set mpc`, while original scan code does not propagate such an error into scan acceptance. A host `vif READY` check and command success are distinct from the firmware's UP state. Missing/failed `mpc` calls may leave the firmware in a different state; measure return codes instead of silently treating success as established.
5. In `cfg80211.c:brcmf_config_dongle`, first netdev-UP config invokes `brcmf_fil_cmd_int_set(ifp,BRCMF_C_UP,0)` and later sets `cfg->dongle_up=true` to prevent reinitialization on subsequent normal vif-up calls. Thus a firmware internal state change after a scan could go unnoticed by host-ready bookkeeping. **This is a hypothesis, not an observation** and not a reason to automatically issue an UP/reset at every scan.
6. Broadcom's older code and headers distinguish `BCME_NOTUP=-4`, `BCME_BUSY`, `BCME_NOTREADY`, `BCME_DONGLE_DOWN`, and other errors. The observed `-4` is specific; avoid conflating it with "scan still busy" or assuming a fixed sleep is the solution.
7. A downstream Broadcom utility path reads firmware `WLC_GET_UP` and, in a particular **WPS** context, issues `WLC_UP` when firmware is down ([reference](https://github.com/RMerl/asuswrt-merlin.ng/blob/main/release/src/router/rc/sysdeps/wps-broadcom.c)). This shows a **common diagnostic/recovery pattern exists**, but its WPS/router context cannot justify directly copying a reset into BCM4329's normal scan callback or calling it an upstream solution.

## Most decisive next measurement (before a new workaround)

Make one reversible, source-restoring **V30? numeric-only lab diagnostic** (name chosen only after checking current repo and Surface for an existing same name; do not overwrite) on the latest *normal-scan*, regulatory-preserving module source. Use exact ABI matched WCC and established Desktop→Surface→COM9 guarded SHA/rollback SOP. Do **not** alter scan flags, country, RF channels, firmware file, sleep delay, MPC state transitions, UP/DOWN, sync-ID, or Event69 callback behavior.

At safe, bounded points log **only numbers and return codes**, not network identities:

| Moment | Read-only firmware and host observations |
| --- | --- |
| After driver attach and before first scan | `WLC_GET_UP` (BCM4329 command 162) return code + 0/1 value if successful; `brcmf_fil_iovar_int_get(ifp,"mpc",&value)` return + value; host `vif READY`, `netif_running`, `scan_status`/owner and SDIO runtime-PM status |
| Immediately before brcmf's normal `mpc=0` set | Same UP+MPC values (only when measurable); capture *actual* `mpc=0` set result |
| After true Event69 SUCCESS but **before** normal restore `mpc=1` | UP/MPC and normal scan lifecycle numeric markers |
| Immediately **after** normal restore `mpc=1` | UP/MPC and set result; no sleeps/extra writes |
| At second legitimate scan, before and after original `mpc=0` | UP/MPC, host scan generation, actual set result; normal second `escan` iovar firmware numeric error |
| Cleanup | Same original-file hashes and normal-state markers as preceding experiments; independently verify no temp mounts |

Use `brcmf_fil_cmd_int_get(ifp, 162, &fw_up)` **only after verifying its exact signature/firmware ABI** and checking that it is safe read-only on this BCM4329 firmware; treat unsupported result explicitly. These reads may alter timing slightly, so make instrumentation minimal and distinguish observational side effects from a causal fix. Keep all original read/write semantics and regulatory permissions.

**Interpretation matrix:**

- **Firmware UP changes 1→0 on completion or `mpc=1`:** find where firmware transitions down and whether it is tied to MPC/roam/BSS mode; determine safe normal lifecycle before even considering an UP command. Don't mask the cause with unconditional reset.
- **Firmware UP remains 1, but ESCAN still returns `BCME_NOTUP`:** may indicate **BSS/interface-scoped** precondition, not global `pub->up`. Inspect `ifidx`/`bsscfgidx` and firmware-specific ESCAN gating. Do not assume general controller down.
- **MPC readback not supported or commands fail:** record exact firmware error and review iovar availability/capabilities. Linux's current `brcmf_set_mpc` ignores result for scan flow; this could be a meaningful compatibility gap.
- **UP is 0 even before first scan but first scan succeeds:** cannot use WLC_GET_UP alone to interpret ESCAN status; need distinguish BSS-level state and ioctl semantics for this firmware.
- **UP/MPC unchanged and all writes successful:** study ESCAN firmware state, request action/status, scan-completion cleanup and early/late event ordering—not arbitrary delays or RF restrictions.

**Possible next controlled A/B only after measurement:** Change exactly one causal, previously established state transition using already-existing firmware control paths and with no flash, wait or regulatory override, then run two normal scans within a single loaded module and compare requested/echoed generation IDs. Do not manufacture scan completions. Physical PASS requires two accepted ESCAN iovars and **two true Event69 terminal events**, normal `cfg80211_scan_done(aborted=0)`, no watchdog and original-state restoration. Then proceed toward user-authorized real network joining.

## Upstream-quality standards

Follow `patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md` (G01–G12) and `docs/plans/MZ600_UPSTREAM_CANONICAL_PATCH_DECOMPOSITION_2026-10-27.md`. This memo is research/provenance only. Do not merge diagnostic logs/knobs into submitted `brcmfmac` patches. WIFI-4 "firmware readiness" remains an **open logical patch**, not a completed implementation. One canonical patch per independently justified issue; no chronological Vxx patch stack. No unsolicited `Signed-off-by`, no confidential data in public repository.

**Current evidence basis:** V21–V28 private physical tests plus cited kernel/Broadcom source. **No new physical test or ready-state value obtained in this research memo.**
