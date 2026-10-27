# MZ600 V22b — real firmware Event69 SUCCESS echo of ESCAN sync_id PHYSICAL PASS (2026-10-27)

**Status:** one controlled physical measurement **PASS**, packet-field readout verified. This proves **echo of fixed requested 0x1234 only**; different scan IDs, late/stale detection, multiple devices, races and upstream patch correctness are **NOT YET TESTED**.

## Test definition and provenance

Owner's MZ600 running Debian armhf Linux `7.0.0-next-20260422+`; unchanged private 2012 BCM4329 OEM firmware `4.218.248.44`, firmware file SHA `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`; no firmware or chip register edits. One NO_IR non-DFS passive 5180MHz channel36 scan, existing 500ms dwell; no SSID-directed probing/association. The driver already sent `params->sync_id=cpu_to_le16(0x1234)` in `brcmf_run_escan`.

V22b source [`tools/forensics/build_mz600_v22_terminal_sync_id_readback.py`](../../tools/forensics/build_mz600_v22_terminal_sync_id_readback.py) latest commit `a793b003c94860d7e09031a32371c1b47967c41b`; source-restoring exact ARM ABI module `brcmfmac-2012-escan-terminal-sync-v22.ko`, **350900B, SHA256 `80f51a4641de80be9953de5ebc132111c99f8b5aa5dc341066280cb51db20c74`**. Compiled without errors, baseline driver/source restored; no installed module/firmware change. Lab `mz600_terminal_owner` switch enabled to allow unresolved terminal event dispatch, but this scan's index was 0 and it completed by normal path. `mz600_extra_events=0` unchanged.

Exact established Desktop WSL→Windows stage→Python temporary LAN HTTP **port43157**→Surface native PowerShell `Invoke-WebRequest`→SHA-verify transfer, server closed, isolated temp removed. On Surface fresh directory `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V22-2012-HEADER-20261027\` contains module, guarded owner runner, private firmware, private logs and receipts. Runner SHA `89adba9523cc90b51ba89902f8c705cd1a75a920197a593cb406d69aee55450c`; Bash SHA `7a4ffe627c13b5a2a7d19d9ad0404afd32fed21ca21088da8563fa0ab7d2c270`. Superseded *earlier* V22 module SHA `2eb55150...` retained in a different folder and **not used**. See [transfer SOP](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md).

## Physical measured values — `sync22b-01-mask001` (CONSUMED, DO NOT RERUN)

- Event `code=69`, true `status=SUCCESS (0)`, **event header version 2**, wire `ifidx=0 bsscfgidx=0`.
- Terminal `datalen=12`, `pktlen=86` (different surrounding wire lengths than prior V21's pktlen94; never infer ABI corruption from this alone).
- Numeric terminal payload, decoded with bounds and unaligned LE reads: **`bytes=12 buflen=12 escan_version=109 sync_id=4660 bss_count=0`**. This is unambiguously **0x1234**, precisely the firmware-request `params->sync_id=0x1234`.
- Existing cfg80211 completion received Event69 status0 and executed `MZ600_V22_SCAN_COMPLETION aborted=0 fw_abort=0 owned=1`; `iw` rc0 **750ms** and **3 BSS** observed; no watchdog.
- Native interface index0 and ordinary handler dispatch, no V21 owner fallback markers on this trial. Do not attribute outcome to owner remap.
- Trial `root_bash_rc=0`, script automatic rollback PASS, independent runtime state/BT quiet PASS; separate read-only COM9 preflight after trial PASS: original installed firmware, NVRAM, baseline brcmfmac module, wlan down, WPA active, Bluetooth quiet, no overlays.

## Interpretation and next decisive gate

**Proven:** fixed ESCAN result header contains returned sync_id matching exactly the requested fixed ID. This strengthens a design that attributes terminal events to a Linux-owned scan transaction rather than relying exclusively on potentially unresolved firmware interface indices.

**NOT proven:** old firmware honors a *different* host-chosen sync_id, or that it maintains distinct IDs across consecutive scans. Because current Linux7 code **always uses 0x1234**, checking for equality with this constant alone cannot reject a delayed completion for an earlier scan. A new, independent, reversible host-request-A/B variant should test alternate benign IDs (e.g. 0x1235 then 0x1236), with exact run receipts and no persistent changes. This would exercise **the existing firmware ESCAN request field**, not edit firmware. If firmware echoes them and returns normal scan results, evaluate how best to track the active generation with proper concurrency and lifetime before extracting a production patch. V21 prototype remains reference, not production patch.

Private original console and BSS identity data stay on Surface and must not be committed.
