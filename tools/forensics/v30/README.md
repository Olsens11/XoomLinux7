# V30 read-only controller-UP / MPC observation — owner-run one-shot

**State:** offline module built and validated; original firmware/installed kernel unchanged. The remote Surface harness-write action was blocked, so this is an intentionally **human-operated** workflow. Do not attempt remote-write workarounds. The user's authorization allows running the test locally; it does not change any remote tool safety gate.

**Module provenance:** exact ABI Linux `7.0.0-next-20260422+` ARMv7 `brcmfmac.ko` 353,372 bytes SHA256 `c064cd5c23c50d423e1c09be106e61633bdf35ef57046d00f211e10659223738`; matched WCC 5,892B SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`. Public lab script/host harness committed at **`9438ba83b58bb7d482a0fe186a214edc4bf8ce20`** and SHA pinned in the Surface bootstrap. Existing private original Motorola 2012 firmware comes from prior V28 captures, *never from GitHub*. See [V30 checkpoint](../../../docs/research/MZ600_V30_FIRMWARE_UP_MPC_DIAGNOSTIC_OFFLINE_CHECKPOINT_2026-10-27.md).

## How to run (two hosts, original SOP)

**1. On the Desktop (DESKTOP-R16QJD4), open PowerShell and run:**
```powershell
py -3 -m http.server 43157 --bind 192.168.0.125 --directory 'C:\Users\olsen\AppData\Local\Temp\mz600-v30-state-share-20261027'
```
The exact SHA-matched single V30 module is already staged there. Leave that PowerShell window open while performing step 2, then stop the temporary server using **Ctrl+C**. Verify no listener remains on 43157. Do not use a different transfer port or serve unrelated private directories.

**2. On SURFACE-BOOK-2, disconnect other COM9 terminals. Open PowerShell and run:**
```powershell
$u = 'https://raw.githubusercontent.com/Olsens11/XoomLinux7/9cc949168dc57b9fe9a6aa6ff1dff0f4b3362bf9/tools/forensics/v30/run-v30-on-surface.ps1'
$p = Join-Path $env:TEMP 'run-v30-on-surface.ps1'
Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile $p
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $p
```
This changes **only the execution policy of the new PowerShell process**, not persistent Windows settings. Read/review the [bootstrap](run-v30-on-surface.ps1) first; the SHA-pinned script checks installed COM9, source firmware, matched WCC, the exact module and both downstream scripts before it offers to run anything. Enter `RUN` at the interactive prompt for one trial, or anything else to cancel after staging.

**Result:** Surface saves private per-trial receipt `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V30-UPSTATE-20261027\runs\up30a-01-mask000.json`, full private transcript and `.attempted` one-time marker. Never reuse this name or overwrite attempt files. A second-scan `-52` still counts as trial **FAIL** even if independent rollback PASS. The Bash test now prints numeric `MZ600_V30_FW_STATE`, `MZ600_V30_MPC_SET`, terminal sync and request-generation lines **even when scan 2 fails**, then performs temporary firmware/WCC unmount and SHA rollback. No permanent firmware, BigPart, kernel module or p7/p8 flash; no SSIDs, MAC addresses or raw scan logs sent to GitHub.

**When discussing results:** Share only sanitized receipt fields and numeric `MZ600_V30_FW_STATE`, `MZ600_V30_MPC_SET`, `MZ600_V30_ESCAN_SET_RC` / kernel generation/terminal markers. Full private logs remain on Surface. After testing, close the Desktop HTTP server and ask the assistant to read the local receipts through the authorized connector. Do not paste private SSIDs/BSSIDs.

## If the bootstrap stops

- SHA/size or existing V30 staging folder mismatch: **STOP**; do not delete evidence and rerun an already consumed trial. Investigate and use a fresh controlled identifier on any future attempt.
- Port 43157 unavailable: verify only our Desktop server command/PID; don't terminate an unknown listener.
- COM9 already open: disconnect the other console; don't race a shared serial device.
- Original firmware, matched WCC, installed module or Bluetooth state differs: host or Bash preflight should refuse and preserve installation. Investigate before continuing.
- V30 script executes but reports nonzero because the second scan fails: check `independent_poststate_ok` in the receipt before further actions. The failure is a valid negative result, not a reason to automatically reboot/flash.
- If a platform safety tool blocks an action, do not bypass the tool. This owner-run bundle is for the user to execute and control personally.

**Research question:** does controller `WLC_GET_UP=162` change around the genuine Event69/normal `mpc=1` completion, or does `BCME_NOTUP` arise with firmware still reporting UP? No unobserved firmware-state claim should enter the canonical upstream patch series.
