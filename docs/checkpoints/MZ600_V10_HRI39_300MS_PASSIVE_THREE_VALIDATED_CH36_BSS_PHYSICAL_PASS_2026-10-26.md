# MZ600 Linux7 BCM4329 v10 — three original-HRI39 5GHz BSS records validate on physical hardware

**Date:** October 26, 2026. **Classification: OWNER-RUN PHYSICAL PASS for populated Broadcom firmware version-108 BSS structure and channel-36 IE bounds.** Do not misclassify as cfg80211 reporting, scan-completion event, upstream patch quality, modern-firmware regression, or independent second-device validation.

## Purpose and controlled variable

Prior HRI39 v7R passed old firmware single-channel 5180MHz NO_IR passive scan ioctl **WLC_SCAN=50 rc0**, **WLC_SCAN_RESULTS=51 rc0**, response 1632 bytes / v108 / 3 framed BSS, but did not validate per-record fields and IE TLVs. v9 added full version108 record validator and observation-only event26 handler, scanned with 80ms passive dwell, obtained empty BSS count0 and no event26. Its owner-run restoration passed.

New [v10 source builder](../../scripts/experiments/build-v064-bcm4329-legacy-passive-dwell300-v10-20261026.py) composes v9 **unchanged except one line**: `params->passive_time = cpu_to_le32(80)` -> **`cpu_to_le32(300)`**. A direct GNU diff of generated v9/v10 C patches verified exactly one code-line difference; scan still one firmware-supported **channel36 5180MHz NO_IR/non-DFS**, passive `scan_type`, `nprobes=0`, `active_time=0`, no directed probe, no active RF assumptions, same OEM HRI39 4.218.248.20 and US/69 matching board cal minus OEM MAC, and factory Xoom FDT MAC injection. No boot, on-disk Linux firmware or installed .ko changed. **300ms improves chances of receiving passive beacons, but proof of its causality is NOT established:** the earlier v7R *80ms* test also returned 3 records, while v9 *80ms* returned none.

Lab source/module exact-ABI ARMv7 Linux `7.0.0-next-20260422+` build PASS, original source and module hashes verified restored. Binary **346440 bytes**, SHA256 **`d20da8542676df6aa226efe9868c8019b5ab840be6ef4787a9582a7a2e9cb911`**; combined experimental patch SHA **`a19f4be8c3081e4087f88ea20780139429f41de2ac4ca7fb1ca377ec58144db2`**. Authenticated Desktop-to-Surface SCP preserved bytes and independently verified SHA. User executed guarded one-shot `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V10-USER-ONE-SHOT-20261026.py`; COM9 ACK transfer verified RAM module SHA without permanent install. Dedicated [v10 guarded shell](../../scripts/host/xoom/test-v064-hri39-v10-dwell300-bss108-event26-one-shot-20261026.sh) SHA **`9f426e2b964907e1464d3c6e811796dac6b0c69f651768fc1473f02f1b91deca`**, unique attempt/cal paths and original SHA preflights.

## Exact new on-Xoom scan results

Owner private COM9 log `MZ600-V10-USER-ONESHOT-PRIVATE-COM9-20261026.txt`, SHA256 **`4ce2ac31c4aa25dc4aeec7fc88e0e12cd2773e7c4cfba1e17efbf11a7da90aef`**:

```text
MZ600_PASSIVE_V10_PREFLIGHT_BEGIN
MZ600_PASSIVE_V10_BASELINE_SHA_PASS
MZ600_PASSIVE_V10_CALIBRATION_RECONSTRUCTION_SHA_PASS
MZ600_PASSIVE_V10_OEM_FIRMWARE_AND_COUNTRY_REV_IN_RAM_AT_BOOT
MZ600_PASSIVE_V10_BRCMUTIL_RC0
MZ600_PASSIVE_V10_DIAGNOSTIC_RC0
MZ600_PASSIVE_V10_WCC_LOAD_RC=0
MZ600_PASSIVE_V10_WLAN0_PRESENT
MZ600_PASSIVE_V10_DYNAMIC_PHY=16
CHANNEL36_NOIR_NONDISABLED_VERIFIED
ONE_CHANNEL_PASSIVE_IW_SCAN_BEGIN_5180
ONE_CHANNEL_PASSIVE_IW_SCAN_RC=0
IW_STDERR_BYTES=0
IW_ERROR_CATEGORY=EMPTY_STDERR
MZ600_V10_BSS108_VALIDATION_LOG_LINES=2
MZ600_V10_LEGACY_EVENT26_LOG_LINES=0
[37445.390677] brcmfmac: brcmf_run_legacy_passive_probe: MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0
[37445.394236] brcmfmac: brcmf_run_legacy_passive_probe: MZ600_LEGACY_SCAN_LAB_COMMAND50_RC=0
[37455.900559] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_BSS108_VALIDATION records=3 ctl36=3 other=0 invalid_ie=0 safe=1
[37455.909209] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_SCAN_LAB_RESULT51 rc=0 bytes=1632 version=108 bss_count=3 envelope_ok=1
MZ600_PASSIVE_V10_CLEANUP_BEGIN prior_rc=0 state=OBSERVATION_COMPLETE
MZ600_PASSIVE_V10_LINK_DOWN_RC=0
MZ600_PASSIVE_V10_UNLOAD_brcmfmac-wcc_RC=0
MZ600_PASSIVE_V10_UNLOAD_brcmfmac_RC=0
MZ600_PASSIVE_V10_UNLOAD_brcmutil_RC=0
MZ600_PASSIVE_V10_UNMOUNT_RC=0
MZ600_PASSIVE_V10_FIRMWARE_UNMOUNT_RC=0
MZ600_PASSIVE_V10_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_PASSIVE_V10_READBACK_A_B_PHYSICAL_PASS_CLEAN
__MZ600_V10_USER_ONESHOT_20261026_EXIT_CODE_0__
```

**Important log-count distinction:** `MZ600_V10_BSS108_VALIDATION_LOG_LINES=2` counts **historical + current printk lines** and does not mean two BSS or two completed tests. The **current timestamped** validation reports exactly **3** BSS, **all ctl_ch==36**, **other=0**, **invalid_ie=0**, **safe=1**. It validates version108 124-byte header field positions, SSID length <=32, IE offset/length bounds and iterative TLV boundaries. It is not evidence all 3 uniquely identify distinct access points (no SSID/BSSID emitted), nor does it prove semantic validity of every advertised IE or check all RF/PHY fields. The 29 `iw phy` 5GHz frequency entries include disabled channels; true firmware-supported list remains 9.

## Legacy completion event still missing

No new `MZ600_LEGACY_SCAN_EVENT26` printk observed during owned passive scan. Command50 rc0; results were read about **10.5 seconds later**, after `brcmf_escan_timeout: timer expired`. Current v9/v10 diagnostic registers an **observation-only** `BRCMF_E_SCAN_COMPLETE=26` handler, filtered to pending legacy requests, but real event26 presence remains unproven. **Do not call the timeout the firmware's normal completion event**. Need event-mask/firmware behavior forensics and then either safe event-driven completion or bounded polling plus cfg80211 ownership/abort/suspend/teardown and exactly-once completion.

## Independent cleanup and privacy

User Surface owner-launcher `MZ600-V10-USER-ONESHOT-RECEIPT-20261026.json` recorded `scan_bash_exit_rc=0`, `old_firmware_results_command_observed=true`, `original_state_script_and_independently_verified=true`, `independent_audit_ok=true`, `run_completed=true`, `user_operated=true`, transcript hash above and exact lab module hash. Guarded Bash confirmed original installed firmware, calibration and module SHA after releasing temporary OEM RAM bind mounts, ordered WCC -> brcmfmac -> brcmutil unload rc0 and no wlan0. Owner launcher separately read COM9 baseline and recorded independent restoration audit PASS. No added boot/flash changes or original OEM binary in public repository. Avoid printing local network identities. **An extra assistant-started COM9 audit is not necessary to claim owner's already-completed independent wrapper check; don't claim one happened without tool evidence.**

## Next work, kernel-quality and gates

- **Now established on one MZ600 with OEM HRI39:** 5GHz channel36 passive scan command50, results51 populated response, 3 v108 framed/field/IE-safe BSS on 5180MHz, current firmware regulatory restrictions preserved.
- **Open:** propagate each validated v108 BSS to cfg80211 via a safe version-aware representation (without breaking v109+), ensure SSID/IE semantics, signal quality, freq regulatory/wiphy membership and lifetime, data deduplication, and test what iw displays. Determine if firmware event26 is absent or masked; replace 10sec timeout-as-success with normal bounded scanning completion (poll, event, or proven hybrid), exactly-once callback including abort/removal.
- Build and run real KUnit C tests, checkpatch/sparse, modem/BT coexistence and modern generic FW 4.220.48 unaffected, independent MZ602/MZ604 tests, one logical bisectable patch per upstream commit; owner's explicit permission before DCO/upstream submission. No repeat RF scan needed merely to reconfirm this exact milestone.

**Physical test PASS; restoration independently verified by owner launcher. Upstream cfg80211 reporting and timely completion still OPEN.**
