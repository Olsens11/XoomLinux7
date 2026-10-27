# MZ600 Linux 7: V25–V27 consecutive-scan compatibility checkpoint (2026-10-27)

**Status: blocker localized, not yet fixed.** Real firmware Event69 terminal delivery with scan-generation ID remains proven by V21–V24. This checkpoint documents why the **second scan in one loaded driver** failed, without changing firmware or compromising regulatory state.

## V25: observe why the second scan was rejected

The [V24 checkpoint](MZ600_V24_PER_SCAN_GENERATION_PAIRED_MODULE_LAB_FINDINGS_2026-10-27.md) ended with an immediate userspace `-EPERM` on scan 2. V25 built a source-restoring diagnostic that logs only bounded numeric scan-request counts, channel and flags, and effective ESCAN sync ID; it **does not alter any rejection condition**. ARM core 353308B SHA256 `ea17a5308f71c2feea495a0047c2f3ff8d788917cf6014ac3c6566cdca7051e2`, matched WCC 5892B SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`.

On physical trial `gate25a-01-mask000`: first passive 5180MHz channel36 scan passed, firmware echoed sync ID **4661**, Linux finished with `aborted=0`, three BSS and 2291ms. Four seconds later, second `iw` failed `Operation not permitted (-1)`. Numeric kernel log:
```text
MZ600_V25_SCAN_REQUEST n_channels=1 n_ssids=0 ie_len=0 busy=0
MZ600_V25_GATE_REJECT reason=channel present=1 freq=5180 channel=36 flags=0x801b0 no_ir=0 disabled=0 radar=0
```
Thus the *private lab gate's* insistence that `NO_IR` stay set was the immediate cause. This is **not a regulatory violation or firmware malfunction**: kernel source `net/wireless/reg.c:handle_reg_beacon()` can clear `IEEE80211_CHAN_NO_IR` on a beacon hint in regulatory conditions permitting it. No reason to force the flag back. Linux regulatory remains authoritative.

## V26b: remove the obsolete flag requirement, locate the next blocker

V26b was an offline source-restoring rebuild of the V25 diagnostic. Its **only new behavior** removes the private lab guard's `!(ch->flags & IEEE80211_CHAN_NO_IR)` predicate; it never clears, adds, overwrites or weakens Linux's regulatory flags. The *remaining test-only restrictions* continue to enforce one 5180MHz channel36, no SSIDs or extra IE, no disabled/radar flag and a passive 500ms dwell. The **production driver should later remove this entire hardcoded lab gate and forced passive policy** and follow ordinary `cfg80211` regulatory constraints for scans and associations.

Core module 353304B SHA256 `296a2408863bcefb8d0216d23f76aa1e63308755b8ebf8df617bb359ebb8536a`, same matched WCC. Trial `reg26b-01-mask000`: first scan 1218ms / three BSS; V21 owner fallback delivered a genuine version2 Event69 status0 with `bsscfgidx=16`, firmware terminal sync ID **4661**, and standard scan_done `aborted=0`. The next scan **passed** the lab gate and generated next ID **4662**; firmware request logged `MZ600_V26_SCAN_REQUEST_SYNC id=4662`, but ESCAN command returned Linux `-52`:
```text
MZ600_V26_SCAN_REQUEST n_channels=1 n_ssids=0 ie_len=0 busy=0
MZ600_V26_SCAN_GATE_PASS ...
MZ600_V26_NEW_SCAN_GENERATION id=4662
MZ600_V26_SCAN_REQUEST_SYNC id=4662
MZ600_V26_ESCAN_SET_RC=-52 v2=0
```
This proves consecutive **host-side generation increments in one continuously loaded module**. It does **not** prove that firmware accepted the second request or emitted Event69 ID4662.

V26 initial result packaging failed because V25's WCC output path was captured at import time; build corrected in V26b, preserving failed output. Source commit `33267bd`; offline exact ABI build and source restoration passed.

## V27: decode firmware-specific error rather than generic Linux -EBADE

`brcmfmac/fwil.c` converts any negative firmware-reported error to generic Linux `-EBADE` (errno52, `Invalid exchange`). New source-restoring V27 builder [`tools/forensics/build_mz600_v27_escan_fwerror_probe.py`](../../tools/forensics/build_mz600_v27_escan_fwerror_probe.py), commit `9630635`, added a numeric-only logging line **specific to failed `escan` iovar** at that conversion. No changes to commands, firmware, chip, regulatory state or results. The original `fwil.c` SHA256 `1ba05bb9a089f6da2e7cdc863473c6168e2443e5c97d9e4906a94bde8bb202a9` was restored. Exact-ABI core 353624B SHA256 `25d9d2862c694a24c4feed2398d9df5e45aadfe11f2e6abf92569373ef396c6c`; WCC unchanged/matched SHA `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`.

Physical trial `fwerr27a-01-mask000` first scan completed in 704ms with two userspace BSS; second scan after 4 seconds reached firmware and returned Linux `-52`. New captured firmware diagnostic:
```text
MZ600_V27_ESCAN_FWERR fwerr=-4 generic_errno=-52
```
The `fwil.c` Broadcom error string table maps **firmware error -4 to `BCME_NOTUP`**. This is a *firmware-reported state error*. It does not prove `wlan0` lost Linux IFF_UP, that RF was off, or that changing the scan ID caused it.

## Relevant upstream source behavior and hypotheses to test, not assume

- `cfg80211.c` calls `brcmf_scan_config_mpc(ifp, 0)` before `escan`, and `brcmf_scan_config_mpc(ifp, 1)` after completion. `feature.c` sets `BRCMF_FEAT_QUIRK_NEED_MPC` **specifically for BCM4329**; `brcmf_set_mpc` uses the firmware `mpc` iovar when vif is up.
- The firmware has explicit `BRCMF_C_UP` and `BRCMF_C_DOWN` commands elsewhere in `cfg80211.c`; there is no evidence here that forcing an UP, hard-reset or bypassing MPC is a correct fix. Do not do so without a controlled source audit and targeted state evidence.
- **Leading question:** Does MPC/power state, BSS-level firmware readiness, or a legacy ESCAN state transition after first completion cause `BCME_NOTUP`? A repeat scan with the same fixed request ID is also a useful negative control if needed, but alone does not reveal firmware state.
- Next engineering step: source-only audit of modern brcmfmac `NEED_MPC`, firmware UP/DOWN and scan lifecycle, then reversible numeric readbacks of applicable firmware state before the second request, without altering regulatory flags or changing the firmware. If evidence supports a compatibility change, keep it BCM4329/scoped and test whether two consecutive actual firmware completions with distinct IDs occur under a single loaded module.
- **No more work on Event69 existence or forcing NO_IR**; settled. Final integration goal is *normal* Linux network discovery, authentication and association through `cfg80211` and `brcmfmac`. The private channel36/no-SSID/passive guard is a temporary controlled test and must not become production code.

## Operations and preserved restoration evidence

The standard [Desktop→Surface→COM9 SHA transfer SOP](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md), LAN port 43157, was used for V26b and V27. Server and isolated staging directory removed. Surface trial records are in private folders:
- `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V25D-GATE-20261027\runs\gate25a-01-mask000.*`
- `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V26B-REGSTATE-20261027\runs\reg26b-01-mask000.*`
- `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V27D-FWERR-20261027\runs\fwerr27a-01-mask000.*`

All IDs **consumed; never rerun**. The shell reports rc38 because the second scan failed and intentionally stops. That makes the suite's `script_cleanup_ok` false under its success definition, **even though each detailed shell log confirms both WCC/firmware bind mounts were unmounted and the original runtime restored**. Independent read-only COM9 postflight after V27 PASS: original firmware, NVRAM, core and WCC hashes; wlan0 down; WPA active; Bluetooth quiet; no overlays. No permanent filesystem, firmware, partition or module modifications. Private network identity data are not committed.

**Gate verdict: V25 obsolete NO_IR check diagnosed; V26 lab check eliminated and generated second ID4662; V27 negative firmware code BCME_NOTUP proven; second firmware scan and upstream-quality production patch remain OPEN.**
