# XoomLinux7 MZ600 v12a — exact-ABI event26 mask readback offline build PASS

**2026-10-26. Verified DESKTOP-R16QJD4 / WSL Ubuntu-22.04 only.** This supersedes the *build-pending* part of [v12a source-only checkpoint](MZ600_V12A_EVENT26_MASK_READBACK_SOURCE_ONLY_OFFLINE_QA_PASS_2026-10-26.md). **No physical MZ600 v12a execution, no scan, no firmware mask result, no module upload, no permanent install, no boot or tablet writes.** Last real hardware state is verified v11 four BSS and independent original-environment restoration audit.

## Exact offline build and independent baseline evidence

- Builder: [v12a read-only mask GET builder](../../scripts/experiments/build-v064-bcm4329-legacy-event26-mask-readback-v12a-20261026.py), based on already physically validated v11 driver and its checked source tree.
- Executed on Desktop under WSL as `xoomdev`:
  `python3 /home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project/scripts/experiments/build-v064-bcm4329-legacy-event26-mask-readback-v12a-20261026.py`
- Output showed `OFFLINE_INPUT_ABI_SHA_AND_PATCH_PREFLIGHT_PASS`, `BUILD_STATUS=0`, `OFFLINE_SOURCE_AND_ORIGINAL_MODULE_RESTORED_VERIFIED`, `V12A_LEGACY_MASK_OBSERVATION_ONLY_BUILD_PASS`. Process completion independently read **exit code 0**.
- Experimental module path, Desktop only: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-legacy-event26-mask-readback-v12a-20261026/brcmfmac-legacy-event26-mask-readback-v12a.ko`
- Experimental module **347,912 bytes**, **SHA256 `75b6e80436b371accd01faa943a0ea45d100ab0a3faa0349db1bc3cef826c77f`**, verified separately with `sha256sum` outside builder output.
- Generated source diff SHA256 `8b53a525eb29dbd26bdd46cbfdbc382a967d25971c47df23124cc5fe5a0bf0e4`. (This is the whole lab source diff accumulated from the original source, not a small upstream-ready isolated v12a patch.)
- `modinfo -F vermagic`: `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`, independently read from built binary.
- Original source+module restore assertions PASS; original source-tree module `brcmfmac.ko` SHA256 **`9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`** independently verified after build, matching v11 baseline.
- Project Git working tree clean and tracking `wip/clean-wifi-bt-usb-20261025`. Before build, source-only insertion invariant PASS (42 added lines, no replacements); scan lifecycle tests 22/22 and v108 tests 18/18; repository checker 588 entries zero errors. Release gates are still NOT READY, no upstream submission.

## Exact narrow v12a question

The module is intentionally **observation-only**: just before the physically established channel36 passive `WLC_SCAN` ioctl50, compare registered native event26 handler, requested driver `event_msgs` bit26, firmware `event_msgs` readback bit26, getter return code, mask length and possible vendor event mapping. The new diagnostic logs numeric fields only. It does not SET the mask, inject an event, bypass NO_IR, alter `cfg->scan_request` or `cfg80211_scan_done`, or replace the old ~10s completion timeout. `GET` failure does not block the old working scan.

Interpretation rules in [v12a static checkpoint](MZ600_V12A_EVENT26_MASK_READBACK_SOURCE_ONLY_OFFLINE_QA_PASS_2026-10-26.md). In particular, **firmware mask bit set does not prove a scan-completion event was emitted**; bitmap unsupported or missing is inconclusive unless the firmware GET contract is established. A legitimate empty GET51 reply may have count zero *after completion*, but count zero is also possible *while scanning*, and count positive can contain partial results.

## Next single new controlled physical experiment — NOT EXECUTED

If owner elects to measure bit26 physically, reuse existing v11 reversible test design but create a **new v12a once marker and receipt**, preflight exact module SHA/ABI and original files, checksum-verify RAM-only upload, run Bash syntax-only gate before RF, allow only user-requested passive `iw dev wlan0 scan freq 5180 passive` under original HRI39 firmware 4.218.248.20 and matched US/69 calibration, collect **numeric event-mask readback and event26 receipt** without public SSIDs/BSSIDs, unload in required WCC→brcmfmac→brcmutil order, unmount OEM FW/cal RAM overlays and independently verify original generic FW/NVRAM/driver/no-radio state over COM9. No v11 script rerun, boot flashes, partition operations, persistent lab installation, or manual firmware override.

Only after physical evidence of the actual firmware completion signal (or a documented, tested alternative) design the separate **v12b completed-scan lifecycle patch**: one serialized cfg80211 owner, generation/late-event exclusion, protected teardown, bounded asynchronous work, real terminal success/abort/error conditions and exactly-once delivery under timeout/suspend/unbind/interface-down.
