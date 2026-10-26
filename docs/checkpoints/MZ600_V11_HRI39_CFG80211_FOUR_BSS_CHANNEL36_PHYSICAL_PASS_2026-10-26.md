# Motorola Xoom MZ600 Linux7 — v11 populated legacy BCM4329 scan successfully published to cfg80211

**Date:** October 26, 2026. **PHYSICAL PASS:** one owner-executed Surface COM9 guarded RAM-only test ran the exact Linux 7 ABI brcmfmac v11 and showed four populated version-108 BSS records on 5180MHz/channel36 safely converted into Linux cfg80211 scan results, with **four BSS entries visible to local `iw`**. Original environment restored and independently audited by the owner-operated launcher. This is not an upstream-ready patch or a proven normal scan-completion mechanism.

## Evidence sources and identity/privacy handling

Read live-created files **on authorized Surface Book 2**:

- `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V11-USER-ONESHOT-RECEIPT-20261026.json`: `scan_bash_exit_rc=0`, `old_firmware_results_command_observed=true`, `original_state_script_and_independently_verified=true`, `independent_audit_ok=true`, `run_completed=true`, `user_operated=true`, `no_persistent_module_or_firmware_install=true`. Transcript SHA256 **`fdfe7b7bc77fb81c3732a67f3fdc98e8efdadf3a4731dc5a004617a8dba101b5`**. Binary SHA `2c7b3bd5799b08e5c10b828cf498f4957e5c1174a2e96d1962654566ceb47334`.
- `MZ600-V064-V11-CFG80211-RAM-TRANSFER-RECEIPT-20261026.json`: `outcome=XOOM_RAM_DIAGNOSTIC_MODULE_SHA256_PHYSICALLY_VERIFIED`, exactly **347368 B**, checksum above, RAM destination `/run/mz600-v064-legacy-v11-cfg80211-20261026.ko`, `serial_ack_complete=true`, `permanent_install=false`, `radio_modules_loaded=false`, `boot_partition_modified=false` (fields characterize transfer step; module was intentionally loaded later by test).
- Private COM9 log `MZ600-V11-USER-ONESHOT-PRIVATE-COM9-20261026.txt`, **473 lines**; exact new run markers below. No SSIDs, BSSIDs, original proprietary binary, nearby network identifiers or raw IE contents published to GitHub. User's local `iw` scan output was counted privately; this is ordinary local Linux wireless discovery, NOT exposure in diagnostics.

## Physical experiment setup

Reused prior proven HRI39 **4.218.248.20** original firmware, OEM matched US/69 NVRAM without stock bootstrap MAC (live device-specific FDT factory MAC injection), original Linux7 Debian 12.15 armhf p8, kernel `7.0.0-next-20260422+`, same single firmware-supported **5180MHz/channel36 NON_DISABLED/NO_IR/non-radar** passive-only scan and **300 ms** dwell. No active probes, directed SSIDs, association, regulatory override, reboot, p7 write, or permanent driver replacement initiated by test.

Exact-ABI owner-built v11 experimental `brcmfmac.ko` SHA256 **`2c7b3bd5799b08e5c10b828cf498f4957e5c1174a2e96d1962654566ceb47334`**, 347368 B, verified Desktop and Surface before owner-run UART transfer. [v11 builder](../../scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py) adds only guarded v108 BSS->cfg80211 reporting on [v10 fully validated HRI39 3 BSS results baseline](MZ600_V10_HRI39_300MS_PASSIVE_THREE_VALIDATED_CH36_BSS_PHYSICAL_PASS_2026-10-26.md). [v11 owner guarded Bash script](../../scripts/host/xoom/test-v064-hri39-v11-cfg80211-bss-inform-one-shot-20261026.sh), **208 lines, 9394 B SHA256 `190e90ff9b05a217a04d0f315d0e55dae323c4bf02de93ebb71434cc3c61aa90`**, used unique v11 once marker, temporary OEM FW/cal overlays, read-only SHA preflight, proper unloading/restoration. Surface launcher `MZ600-V11-USER-ONE-SHOT-20261026.py` SHA256 `c72739ee8170564db4be76923a86d70453a4748376a18b107064b8f413325246` included **pre-RF exact Bash syntax validation on Xoom** following module upload; host receipts prove it proceeded successfully.

## Exact new on-device evidence (from owner COM9 transcript)

```text
MZ600_PASSIVE_V11_PREFLIGHT_BEGIN
MZ600_PASSIVE_V11_BASELINE_SHA_PASS
MZ600_PASSIVE_V11_CALIBRATION_RECONSTRUCTION_SHA_PASS
MZ600_PASSIVE_V11_OEM_FIRMWARE_AND_COUNTRY_REV_IN_RAM_AT_BOOT
MZ600_PASSIVE_V11_BRCMUTIL_RC0
MZ600_PASSIVE_V11_DIAGNOSTIC_RC0
MZ600_PASSIVE_V11_WCC_LOAD_RC=0
MZ600_PASSIVE_V11_WLAN0_PRESENT
MZ600_PASSIVE_V11_DYNAMIC_PHY=17
CHANNEL36_NOIR_NONDISABLED_VERIFIED
ONE_CHANNEL_PASSIVE_IW_SCAN_BEGIN_5180
ONE_CHANNEL_PASSIVE_IW_SCAN_RC=0
MZ600_V11_USERSPACE_IW_BSS_LINES=4
IW_STDERR_BYTES=0
IW_ERROR_CATEGORY=EMPTY_STDERR
[40223.167560] brcmfmac: brcmf_run_legacy_passive_probe: MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0
[40223.171762] brcmfmac: brcmf_run_legacy_passive_probe: MZ600_LEGACY_SCAN_LAB_COMMAND50_RC=0
[40233.483300] ieee80211 phy17: brcmf_escan_timeout: timer expired
[40233.500607] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_CFG80211_BSS_INFORM count=4 requested=4
[40233.509036] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_BSS108_VALIDATION records=4 ctl36=4 other=0 invalid_ie=0 safe=1
[40233.517407] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_SCAN_LAB_RESULT51 rc=0 bytes=2176 version=108 bss_count=4 envelope_ok=1
MZ600_V11_KERNEL_INFORMED_BSS=4 REQUESTED=4
MZ600_PASSIVE_V11_CLEANUP_BEGIN prior_rc=0 state=OBSERVATION_COMPLETE
MZ600_PASSIVE_V11_LINK_DOWN_RC=0
MZ600_PASSIVE_V11_UNLOAD_brcmfmac-wcc_RC=0
MZ600_PASSIVE_V11_UNLOAD_brcmfmac_RC=0
MZ600_PASSIVE_V11_UNLOAD_brcmutil_RC=0
MZ600_PASSIVE_V11_UNMOUNT_RC=0
MZ600_PASSIVE_V11_FIRMWARE_UNMOUNT_RC=0
MZ600_PASSIVE_V11_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_PASSIVE_V11_READBACK_A_B_PHYSICAL_PASS_CLEAN
__MZ600_V11_USER_ONESHOT_20261026_EXIT_CODE_0__
```

The three independent count sources **all agree: 4 validated v108 records, 4 cfg80211-informed, 4 returned as user-local `iw scan` BSS lines**; original firmware GET WLC_SCAN_RESULTS=51 returned **2176 bytes** / version108 / four bounded records. All four control channels 36, no malformed IEs, safe=1. The full scan was single channel 36 with NO_IR/non-DFS. User-local scan contains usual network-identifying contents, but test only printed a COUNT and deleted volatile raw output; no public identifiers. Distinguish historical `MZ600_V11_BSS108_VALIDATION_LOG_LINES=3` from current timestamped **four** records; this marker counts cumulative dmesg diagnostics across runs, not BSS count.

## Restoration and limits

The test's cleanup unloaded WCC -> brcmfmac -> brcmutil with rc0, unmounted both OEM HRI39 FW and US/69 cal RAM overlays rc0, and verified original installed generic firmware/NVRAM/base module hashes and no wlan0. Owner launcher performed an independent **post-cleanup read-only COM9 audit** with `independent_audit_ok=true`. No permanent device changes, no reboot or p7 modifications. No extra independently initiated assistant COM9 audit is claimed.

**Open and mandatory before production/upstream:**
1. **LEGACY SCAN COMPLETION:** Firmware event26 still not observed (`MZ600_V11_LEGACY_EVENT26_LOG_LINES=0`, includes historic dmesg too). GET51, cfg80211 inform, and `cfg80211_scan_done` still happen on the existing modern escan **~10-second timeout**, not normal prompt firmware event notification. Separate patch needed: validate legacy `event_msgs` bit26 and raw events or develop bounded asynchronous results polling with deterministic empty-scan semantics, scan request ownership/abort/firmware failure/removal/suspend and exactly-once completion. See [legacy lifecycle research](../research/MZ600_BCM4329_LEGACY_SCAN_EVENT26_OR_BOUNDED_POLLING_UPSTREAM_DESIGN_2026-10-26.md).
2. **VERSION AND REGRESSION:** Keep modern v109+ firmware scan untouched, preserve regulatory NO_IR behavior, validate v108 parser on deliberately malformed and varying IE formats with in-tree KUnit, handle partial cfg80211 inform allocation errors/teardown and data deduplication.
3. **MULTIDEVICE + MAINLINE:** Additional MZ600s/MZ602/MZ604, normal generic 4.220.48 2GHz scan regression, BT/U4 coexistence, runtime power and OEM SDIO hardware quirks, real checkpatch/sparse/coding conventions; split by one logical bisectable change per patch and obtain owner's explicit permission before DCO or upstream submission.

**Latest physical result:** HRI39 firmware 5GHz passive scan on native Linux7 produces **four properly validated, cfg80211-published, user-visible local `iw` BSS entries**, safe SHA-restored baseline. Main unqualified scanner task is correct completion lifecycle, not BSS discovery.
