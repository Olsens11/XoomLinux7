# MZ600 Linux7 — v12a firmware event26 readback PHYSICAL PASS, no completion callback

**Date:** October 26, 2026. **Owner-operated physical readback PASS, scan PASS, full rollback and independent host read-only audit PASS.** On the actual experimental replacement Motorola Xoom MZ600, the original Motorola HRI39 BCM4329 firmware returned its `event_msgs` mask with event 26 explicitly enabled. The previously missing legacy scan-completion callback remained unobserved. This establishes one specific fact about mask configuration; **it does NOT establish actual firmware event emission, reception, or timely completion**. Current cfg80211 scan lifecycle still uses the modern escan ~10-second timeout.

## Private evidence identity (no nearby network identifiers exposed)

Surface Book 2 `C:\Users\olsen\xoom-linux-rom\captures\`:
- Owner one-shot JSON: `MZ600-V12A-USER-ONESHOT-RECEIPT-20261026.json`, 559 bytes, SHA256 **`2bdf0d556e278efb965f6f09b5686a5862a4607696ea68e4e56e17ba9e059a72`**; states `scan_bash_exit_rc=0`, `event26_mask_diagnostic_observed=true`, `old_firmware_results_command_observed=true`, `original_state_script_and_independently_verified=true`, `independent_audit_ok=true`, `run_completed=true`, `no_persistent_module_or_firmware_install=true`.
- Private COM9 transcript: `MZ600-V12A-USER-ONESHOT-PRIVATE-COM9-20261026.txt`, 453 text lines / 4867 bytes, SHA256 **`fd009ecc38b9e2ff1b945475fd0f897e39be4cf1e73e48514630c54f0559155d`**. Independent Surface `Get-FileHash` result matches both transcript and receipt's `transcript_sha256`.
- RAM transfer receipt: `MZ600-V064-V12A-EVENT26-RAM-TRANSFER-RECEIPT-20261026.json`, 410 bytes SHA256 **`b6b28ef3944e4b5b253140fa1bb50367fe823c8948eecb07ae325909338b6105`**. `source_module_sha256=75b6e80436b371accd01faa943a0ea45d100ab0a3faa0349db1bc3cef826c77f`, 347912 bytes, target **RAM-only** `/run/mz600-v064-legacy-v12a-event26-mask-20261026.ko`, positive serial ACK and on-device SHA; no permanent install or p7 writes.
- All evidence preserved privately, **no SSIDs, BSSIDs, raw beacon information elements, proprietary firmware or owner serial IDs committed**.

## Exact new evidence: firmware event bit 26 is actually enabled

Log, after firmware started and just BEFORE `WLC_SCAN` ioctl50:
```text
[44325.791303] brcmfmac: brcmf_run_legacy_passive_probe:
MZ600_LEGACY_EVENT26_MASK_READBACK rc=0 len=27 registered=1 driver_bit=1 fw_bit=1 map=0
[44325.794287] brcmfmac: brcmf_run_legacy_passive_probe:
MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0
[44325.798329] brcmfmac: brcmf_run_legacy_passive_probe:
MZ600_LEGACY_SCAN_LAB_COMMAND50_RC=0
```

Interpretation:
- `rc=0`: HRI39 firmware accepts `event_msgs` GET and returns success.
- `len=27`: driver's current firmware event-mask readback length; native event index 26 fits in byte 3, 0x04.
- `registered=1`: `BRCMF_E_SCAN_COMPLETE` handler installed in `fweh`.
- `driver_bit=1`: Linux driver-side configured mask requests event 26.
- `fw_bit=1`: actual firmware readback contains bit26.
- `map=0`: no vendor event map in this brcmfmac fweh instance.
- `MZ600_V12A_LEGACY_EVENT26_LOG_LINES=0`: the observation-only scan-complete handler had NO logged callback on this owner scan. **Bit enabled is not proof of transmission or receipt**. Empty callbacks could reflect firmware not emitting event on this scan mode, wrong event packet format, network/bus drop/receive filtering, or earlier/later lifecycle; distinguish by later ingress instrumentation.

This **rules out a simple missing handler registration or missing requested/firmware-reported event26 mask bit** in the tested state. It does **not** yet rule out a malfunction in firmware event delivery, mismapped event semantics or timing.

## Scan and rollback remained operational

Hardware firmware: original HRI39 **4.218.248.20**, matched USA 69 calibration without OEM fixed MAC, live FDT per-device factory MAC preserved; running Linux `7.0.0-next-20260422+`, Debian 12.15 armhf on existing internal p8 `/dev/mmcblk0p8` ext4. Original firmware/NVRAM were mounted as temporary RAM overlays and later unmounted. One channel36/5180MHz **passive** scan on NO_IR, enabled and nonradar; no probes, active association, country override or hardware reset.

New physical transcript:
```text
MZ600_PASSIVE_V12A_PREFLIGHT_BEGIN
MZ600_PASSIVE_V12A_BASELINE_SHA_PASS
MZ600_PASSIVE_V12A_CALIBRATION_RECONSTRUCTION_SHA_PASS
MZ600_PASSIVE_V12A_WCC_LOAD_RC=0
MZ600_PASSIVE_V12A_WLAN0_PRESENT
MZ600_PASSIVE_V12A_DYNAMIC_PHY=18
CHANNEL36_NOIR_NONDISABLED_VERIFIED
ONE_CHANNEL_PASSIVE_IW_SCAN_RC=0
MZ600_V12A_USERSPACE_IW_BSS_LINES=3
MZ600_V12A_LEGACY_EVENT26_LOG_LINES=0
[44335.837122] ieee80211 phy18: brcmf_escan_timeout: timer expired
[44335.851563] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_CFG80211_BSS_INFORM count=3 requested=3
[44335.863509] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_BSS108_VALIDATION records=3 ctl36=3 other=0 invalid_ie=0 safe=1
[44335.875521] brcmfmac: brcmf_cfg80211_escan_timeout_worker: MZ600_LEGACY_SCAN_LAB_RESULT51 rc=0 bytes=1632 version=108 bss_count=3 envelope_ok=1
MZ600_V12A_MASK_LOGS_BEFORE=0 AFTER=1
MZ600_V12A_MASK_OBSERVATION_RECORDED
MZ600_PASSIVE_V12A_CLEANUP_BEGIN prior_rc=0 state=MASK_OBSERVATION_COMPLETE
MZ600_PASSIVE_V12A_LINK_DOWN_RC=0
MZ600_PASSIVE_V12A_UNLOAD_brcmfmac-wcc_RC=0
MZ600_PASSIVE_V12A_UNLOAD_brcmfmac_RC=0
MZ600_PASSIVE_V12A_UNLOAD_brcmutil_RC=0
MZ600_PASSIVE_V12A_UNMOUNT_RC=0
MZ600_PASSIVE_V12A_FIRMWARE_UNMOUNT_RC=0
MZ600_PASSIVE_V12A_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_PASSIVE_V12A_READBACK_A_B_PHYSICAL_PASS_CLEAN
__MZ600_V12A_USER_ONESHOT_20261026_EXIT_CODE_0__
```

All three version108 records validated (`ctl36=3`, `invalid_ie=0`, `safe=1`), were published to cfg80211 and appeared as 3 local `iw` BSS records. v11 previously reported FOUR on a different physical scan; fluctuations of observed AP count do not constitute a regression. Result reading and scan_done **still follow the ~10s timeout**, not an actual completion event. No faster scan completion is claimed.

Cleanup: WCC→brcmfmac→brcmutil removals returned 0; both temporary OEM firmware+calibration bind mounts removed; original generic FW, NVRAM and module SHA restored, no radio module/wlan0; owner launcher then independently audited original root and firmware/module/no-radio over COM9 and recorded `independent_audit_ok=true`. No flash, kernel rebuild on tablet or persistent experimental module.

## Root cause narrowing and next isolated change

**Event-mask setup is working for the tested HRI39 firmware.** Next measure delivery rather than repeat the same scan: inspect *existing* Linux7 `brcmfmac/fweh.c` `brcmf_fweh_process_skb` (EtherType/subtype/OUI event screening), `brcmf_fweh_process_event` (code, `num_event_codes`, handler-index and size checking), firmware event queue/dispatch and SDIO RX routing. Also inspect the OEM 2010 `wl_iw.c` normal scan completion event behavior and whether original Motorola `WLC_SCAN` passive single-channel request is expected to emit 26. Candidate next **v12b observation-only** change: track numeric event code 26 at well-defined RX/dispatch stages, with no SSID/BSSID content and no scan ownership/timer modifications. Correlate timestamps with scan start and timeout. Design with no unnecessary host paths or broad printk noise.

If an authentic terminal event26 can be shown, complete legacy scan on a serialized worker that safely reads/validates `WLC_SCAN_RESULTS=51`, informs cfg80211, then calls `cfg80211_scan_done` exactly once (success vs aborted) and suppresses late timeout/abort. If event26 is not delivered, first identify an actual firmware scan-end predicate (or explicitly bounded conservative timeout path); **GET51 count0 cannot distinguish empty completion from in-progress, and count>0 may be incomplete**. Account for request start failure, cancellation, firmware error, interface-down, suspend, removal/unbind and concurrent requests with protected ownership and work cancellation. Keep modern escan/generic FW and whole-chip BT power path separate.

**Do not rerun v12a or its one-shot marker.** Existing audit restored safe original Debian state. Follow one logical change per patch, no permanent lab install/flash and no upstream submission without owner approval. Generic FW2GHz and MZ602/MZ604 regression gates, KUnit and whole-chip power tests remain open.
