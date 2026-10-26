# MZ600 v06.4 — Motorola HRI39 legacy single-channel passive scan returns 3 BSS records (PHYSICAL PASS)

**Date:** 2026-10-26 around 14:45 America/New_York. **Owner-operated Surface PowerShell manual v7R one-shot**, exact Linux `7.0.0-next-20260422+` running native Debian 12.15 armhf on Xoom MZ600. **Physical firmware scan command50 and scan-results command51 success.** This is a real on-device firmware result, not synthetic or source conjecture. **Still lab only; cfg80211 populated BSS reporting and normal scan completion event NOT qualified.**

## What changed since unsuccessful v7 scan

Previous v7 physically loaded firmware/created wlan0 with 5GHz NO_IR channels, but `iw dev wlan0 scan passive freq 5180` exited 1 before any driver scan markers. Investigated `iw --version=5.19`, `iw help scan`, and `iw` command parser: `passive` must be the terminal option. **Only change to experiment:** `iw dev wlan0 scan freq 5180 passive` (frequency before passive), with distinct v7R attempted marker/calibration path and sanitized error categorization. **No new kernel module build, firmware/calibration setting, device-tree, regulatory override or low-level chip power change.**

Reused existing SHA pinned **345380-byte** v7 lab `brcmfmac.ko` from Xoom RAM (SHA256 `ca2dbbf1131a44515b724b38f3ce3a7e7a6b8a7712ecceea404c833aa0f3ffec`), original private Motorola HRI39 2011 firmware `4.218.248.20` SHA `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`, matching OEM `US/69` NVRAM without stock bootstrap MAC, factory per-device FDT MAC injection, dual-band passive-only 5GHz wiphy fallback based on **actual firmware channels** (legacy ioctl217 validated 2G=11/5G=9). Restricted to non-DFS 5180MHz channel36 with NO_IR, no SSID directed search, passive firmware mode, `nprobes=0`, `active_time=0`, intended 80ms dwell. **No claim of measured zero RF emissions without spectrum evidence.**

### Original direct lab diagnostic — success

Extracted from Surface **`C:\Users\olsen\xoom-linux-rom\captures\MZ600-V7R-USER-ONESHOT-PRIVATE-COM9-20261026.txt`**:

```text
MZ600_PASSIVE_V7R_PREFLIGHT_BEGIN
MZ600_PASSIVE_V7R_BASELINE_SHA_PASS
MZ600_PASSIVE_V7R_CALIBRATION_RECONSTRUCTION_SHA_PASS
MZ600_PASSIVE_V7R_OEM_FIRMWARE_AND_COUNTRY_REV_IN_RAM_AT_BOOT
MZ600_PASSIVE_V7R_BRCMUTIL_RC0
MZ600_PASSIVE_V7R_DIAGNOSTIC_RC0
MZ600_PASSIVE_V7R_WCC_LOAD_RC=0
MZ600_PASSIVE_V7R_WLAN0_PRESENT
MZ600_PASSIVE_V7R_DYNAMIC_PHY=14
CHANNEL36_NOIR_NONDISABLED_VERIFIED
ONE_CHANNEL_PASSIVE_IW_SCAN_BEGIN_5180
ONE_CHANNEL_PASSIVE_IW_SCAN_RC=0
IW_STDERR_BYTES=0
IW_ERROR_CATEGORY=EMPTY_STDERR
MZ600_PASSIVE_V7R_COUNTRY_LOGS_BEFORE=0 AFTER=1
[34324.806557] brcmfmac: brcmf_run_legacy_passive_probe: MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0
[34324.810402] brcmfmac: brcmf_run_legacy_passive_probe: MZ600_LEGACY_SCAN_LAB_COMMAND50_RC=0
[34335.249868] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_SCAN_LAB_RESULT51 rc=0 bytes=1632 version=108 bss_count=3 envelope_ok=1
MZ600_PASSIVE_V7R_CLEANUP_BEGIN prior_rc=0 state=OBSERVATION_COMPLETE
MZ600_PASSIVE_V7R_LINK_DOWN_RC=0
MZ600_PASSIVE_V7R_UNLOAD_brcmfmac-wcc_RC=0
MZ600_PASSIVE_V7R_UNLOAD_brcmfmac_RC=0
MZ600_PASSIVE_V7R_UNLOAD_brcmutil_RC=0
MZ600_PASSIVE_V7R_UNMOUNT_RC=0
MZ600_PASSIVE_V7R_FIRMWARE_UNMOUNT_RC=0
MZ600_PASSIVE_V7R_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_PASSIVE_V7R_READBACK_A_B_PHYSICAL_PASS_CLEAN
__MZ600_V7R_USER_ONESHOT_20261026_EXIT_CODE_0__
```

**Interpretation:** Real old firmware accepted ioctl `WLC_SCAN=50` (rc0), and a later bounded `WLC_SCAN_RESULTS=51` GET returned **1632 bytes**, correctly framed envelope **version108**, **count3**, checked record version/length boundaries and total buffer consumption (`envelope_ok=1`). `iw` completed with rc0 and no stderr, so it is valid to declare **firmware scan and result-envelope PHYSICAL PASS**. The lab kernel intentionally did **not** parse individual BSS records or report BSS identities to cfg80211. We have **NOT verified** whether all three BSS records are truly on channel36 or a different channel; must validate each record's v108 field offsets, chanspec, ctl_ch, IE ranges against firmware-supported and regulatory-approved channels before claiming 5GHz discoveries or displaying SSIDs/BSSIDs. No raw nearby wireless identities are stored in public GitHub.

### Remaining driver scan lifecycle deficiency

The diagnostic was logged at `[34335.249868]` after `[34335.233618] ieee80211 phy14: brcmf_escan_timeout: timer expired`, roughly **10.44s after** command50 rc0. The old firmware **did not provide the modern escan completion event used by current cfg80211**. The v7 lab reuses that timeout worker to GET the old scan-results list and complete `cfg80211_scan_done` exactly once. This proves fallback collection works but **normal timely completion was not implemented/tested**. Next study legacy `BRCMF_E_SCAN_COMPLETE` events / firmware event mapping or implement bounded safe polling/notification with proper cfg80211 lifecycle, cancel and suspend/unload races; do not change normal modern escan path.

### On-device and Surface cleanup evidence

- Surface JSON receipt `MZ600-V7R-USER-ONESHOT-RECEIPT-20261026.json` actually created `2026-10-26 14:45:20-04:00`, fields: `scan_bash_exit_rc=0`, `old_firmware_results_command_observed=true`, `original_state_script_and_independently_verified=true`, `independent_audit_ok=true`, `run_completed=true`, `user_operated=true`. Private transcript SHA256 **`5d21f6d59236576f5ee2fb8b0c487140d0a2bfdab3bdad42dc2ac43a0fa0db88`**, lab SHA above.
- Exactly ordered WCC→brcmfmac→brcmutil unload rc0, original Motorola FW+cal RAM bind overlays both unmounted rc0, original generic Linux firmware/calibration/installed module hashes checked in guarded Bash and independent Surface wrapper COM9 postcheck, `wlan0` absent after cleanup; no reboot, kernel/boot partition/module installs. A **further separate assistant-launched COM9 state read** was rejected at the remote process safety layer in the same chat, so don't falsely claim this third manual audit occurred. However owner-executed wrapper's independent audit is already recorded PASS and trustworthy for stated checks.

### Files and source

- [v7 lab builder](../../scripts/experiments/build-v064-bcm4329-legacy-singlepassive-5ghz-scan-probe-20261026.py): 345380B exact-ABI kernel module, compiled previously and physically reused without changes.
- [v7R guarded owner test](../../scripts/host/xoom/test-v064-hri39-singlepassive-5ghz-legacy-scan-proof-v7r-20261026.sh), SHA256 **`d3c5e261479cf71ef3adf6cacca3452e52c9344fb77a14538afbc699951d1d13`**, 177 lines; uses corrected iw positional argument order and sanitized stderr category, fail-closed hash/status preflights and verified cleanup.
- Owner-run Surface launcher (private host only) `MZ600-V7R-USER-ONE-SHOT-20261026.py`, SHA256 **`832bcfbcb56f128e1e8c0dd08dc312450b4dbb05dcc737a8f16b128391f457f8`**, reused exact v7 module on Xoom RAM, no upload, owner manually executed.
- [40 synthetic host safety checks](../../tools/forensics/test_bcm4329_legacy_scan_contract.py) and [version108 full BSS model](../../tools/forensics/test_bcm4329_legacy_bss108_contract.py) remain earlier offline evidence (22+18 cases). **NOT in-kernel KUnit, NOT physical full v108 record decoding**.

### Next upstream-shaped milestones

1. **First** add a safe **version108 BSS header/field parser** into the existing brcmfmac cfg80211 inform pipeline or narrow conversion helper, validate 124-byte struct + actual firmware record lengths, byte alignment/endianness, IE offset+length, SSID length, firmware-validated control channel and regulatory status. Consider one guarded count-only physical test to confirm field-layout without public network identities. Do not globally change version109+ behavior (late 2026 109–112 upstream patch proposal merge status unconfirmed).
2. Replace timer-as-success mechanism with firmware-completion notification or bounded polling integrated with the existing `cfg->scan_request`, timeout/cancel and interface teardown semantics. Test exactly-once cfg80211 completion and fault-injected malformed replies, concurrency, battery and shared BT-power paths. Keep `brcmfmac` feature/quirk selection localized to affected BCM4329 firmware, not all devices.
3. Create bisectable series with **one logical change per patch**, checkpatch, sparse, KUnit, current wireless MAINTAINERS routing; separate whole-chip U4/I7/BT/LPO and OEM MMC SDIO six-field quirk patches. Modern generic 4.220.48 2GHz behavior and independent MZ600/MZ602/MZ604 remain mandatory before upstream consideration.
4. No further physical scan is necessary to re-prove ioctl50/51; target a **new question** next. V7R once-only attempt marker now consumed; do not rerun same script.

**Milestone:** old firmware 5GHz passive **scan request + response framing PHYSICAL PASS**, three BSS envelopes, original baseline clean; *record channel identity and proper lifecycle still unqualified*.
