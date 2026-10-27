# MZ600 V31 — conditional Broadcom firmware-UP diagnostic

**Prepared 2026-10-27. OFFLINE BUILD PASS. NOT YET PHYSICALLY TESTED.** User explicitly authorized the experiment. The earlier connected Surface file-write step was blocked; do not defeat that platform restriction. This package is a user-operated one-shot, with independent rollback and evidence. It neither flashes p7/p8 nor overwrites original NVRAM, factory firmware or installed kernel modules.

## Purpose

V30 [proved physically](../../../docs/checkpoints/MZ600_V30_FIRMWARE_UP_LOST_BETWEEN_ESCANS_PHYSICAL_PASS_2026-10-27.md) that Broadcom firmware **WLC_GET_UP** changed from **1** immediately after its first legitimate scan to **0** before the second scan, while Linux still had VIF READY and netdev running. Vendor BCMDHD [has a matching documented mechanism](../../../docs/research/MZ600_BCM4329_MAINLINE_PEERS_AND_MPC_AUTO_DOWN_WLC_UP_2026-10-27.md): disable MPC to avoid automatic interface-down, then explicitly bring the controller UP. The experiment **does not assume** this is the production fix.

V31 reuses the fully normal cfg80211/regulatory-preserving V29→V30 lab implementation and adds **exactly one narrowly guarded write**: on a BCM4329 primary station interface, after the existing MPC=0 scan-entry action, read WLC_GET_UP=162; **only if successful and exactly 0**, send `BRCMF_C_UP=1` once and read WLC_GET_UP again. Other chips / interfaces use the unchanged driver path. If the firmware GET is unsupported, returns an unexpected value, or UP fails/does not read back 1, do not send ESCAN; restore original MPC. Normal scan generation, real Event 69 completion, regulatory policy and original cleanup remain in effect. This is not yet a submission patch.

## Pinned artifacts

| Item | SHA256 | Bytes |
| --- | --- | ---: |
| V31 ARM brcmfmac lab core, 7.0.0-next-20260422+ | `c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8` | 354392 |
| Matched WCC module, source ABI pair | `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d` | 5892 |
| Original Motorola 2012 candidate firmware (private Surface original) | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` | 264140 |
| [V31 Bash scan/cleanup script](mz600-v31-normal-scan.sh) | `5b168d624d23e68c828b6d169c4425de54b4f10e97c618d7a449cbe5f31033ea` | 11426 |
| [V31 Python COM9 owner harness](mz600-v31-owner-once.py) | `9b54594f65c9b1ceb2e03f4ef793c201d0eaf16fd6a24217cdc37426ac3e9b29` | 19753 |

The [source-restoring V31 builder](../build_mz600_v31_conditional_fw_up.py) produced the exact ARM module pair, compiled successfully, and restored original source SHA. This **does not** imply a physical result. The Desktop temporary module-only transfer folder already contains the 354392-byte file under `C:\Users\olsen\AppData\Local\Temp\mz600-v31-conditional-share-20261027\mz600-v31-escan-event69.ko`; its SHA and destination size were verified. The Surface prior V30 firmware/WCC capture hashes were verified, COM9 exists and the new V31 folder was unused when checked.

## One owner-operated run

**On Desktop** `DESKTOP-R16QJD4`, open PowerShell:

```powershell
py -3 -m http.server 43157 --bind 192.168.0.125 --directory 'C:\Users\olsen\AppData\Local\Temp\mz600-v31-conditional-share-20261027'
```

Leave that **one temporary module-only server** open during transfer. Do not change port, expose the whole filesystem, or overwrite staged artifacts.

**On Surface Book 2**, disconnect competing serial terminals, open PowerShell, then:

```powershell
$u = 'https://raw.githubusercontent.com/Olsens11/XoomLinux7/2c9d02a7d57a5508495b8bb10603295fd5425678/tools/forensics/v31/run-v31-on-surface.ps1'
$p = Join-Path $env:TEMP 'run-v31-on-surface.ps1'
Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile $p
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $p
```

Review the [PowerShell launcher](run-v31-on-surface.ps1) first if desired. Its execution-policy argument is **process-local**, not persistent. It validates SHA/size of all required files, pulls the public Bash and Python runners at a pinned GitHub commit, copies the previously verified **private** V30 firmware/WCC from the Surface, and stages into a **new** `MZ600-V31-CONDITIONAL-UP-20261027` directory. **Only after staging** will it prompt for `RUN`. Anything else exits without a COM9 device test.

The user-operated test calls `mz600-v31-owner-once.py --masks 0 --series up31a`, with one-shot identity `up31a-01-mask000`. This ID must never be reused; failure and success produce a consumed `.attempted` file. The system requires root COM9, the exact Linux kernel/runtime, Wi-Fi/BT quiet, original SHA, preflight no overlays, matching WCC, and the original temporary RAM firmware overlay. It runs **two regular multichannel `iw dev wlan0 scan`** requests in one loaded module. Log `MZ600_V31_UP_BEFORE_SCAN`, `MZ600_V31_WLC_UP`, `MZ600_V31_UP_AFTER_RECOVERY`, per-scan generation, genuine Event69 and MPC state. A nonzero result may be a valuable negative finding; an absent postflight or unexpected hash is a real safety stop.

When done, close the Desktop HTTP server with **Ctrl+C**. Results stay privately on Surface:
`C:\Users\olsen\xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027\runs\` as `up31a-01-mask000.json`, `up31a-01-mask000.private.txt`, and `up31a-01-mask000.attempted`. Avoid publishing SSIDs/BSSIDs or private calibration/firmware. The assistant can inspect private files through authorized tools after the user reports the run.

**Success standard:** two accepted ESCAN requests, two real Event69 terminal SUCCESS events with distinct IDs 4661/4662 (or independently verified expected generation), `cfg80211_scan_done(aborted=0)` twice, ordinary iw scan success, no watchdog, original runtime SHA and independent preflight PASS. The command need only be issued on the firmware DOWN branch. No ordinary association/authentication/IP was tested.

**Important:** This is a reversible diagnostic, not automatic approval for upstream patches or firmware replacement. Any permanent solution must satisfy [G01–G12](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md) and independently preserve proper power management, multidevice behavior and Bluetooth coexistence.
