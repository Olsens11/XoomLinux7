# MZ600 v14: May 2012 BCM4329 passive 5180MHz ESCAN and Event69 diagnostic STAGED, no physical run

**Date:** 2026-10-26. **Evidence:** host-only ARMv7 kernel module build, source audit, Surface transfer and syntax verification. **The Xoom has NOT run V14**; neither event69 nor 5GHz scan acceptance has yet been observed. Original V13 physical no-scan dualband PASS remains authoritative.

## Rationale

After v13 proved both 2G+5G channels under OEM 2012 `4.218.248.44`, test the **normal** Linux7 ESCAN/Event69 mechanism before implementing older HRI39 ISCAN. Firmware-only RAM overlay, original NVRAM and device-specific FDT MAC retained. The proven BCM4329 `WLC_GET_VALID_CHANNELS` fallback remains because 2012 `chanspecs` still returns -52.

## New source-restored V14 driver build

Host builder: [`tools/forensics/build_mz600_v14_escan_lab_module.py`](../../tools/forensics/build_mz600_v14_escan_lab_module.py).

- Base source `cfg80211.c` SHA `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`, original baseline brcmfmac.ko `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`, proven passive NO_IR fallback source patch SHA `9ef957fc8c8a8d4843e35666db8d71092d06c92a456d5d17d1521d2125b7575a`.
- In temporary protected build, applies old v05 patch then adds **BCM4329-only scan entry restriction** to one channel exactly CH36 5180, `NO_IR`, non-disabled, non-RADAR, no SSIDs or request IE; issues `BRCMF_C_SET_PASSIVE_SCAN=1` before accepting request. Driver's `brcmf_escan_prep` already specifies passive for n_ssids 0. All other BCM4329 scans refused. **No regulatory override or channel-force**.
- Instrumented `MZ600_V14_ESCAN_SET_RC`, `MZ600_V14_EVENT69 status`, `MZ600_V14_EVENT69_PARTIAL bss_ver/count`, `MZ600_V14_FINAL_BSS count/version`, `MZ600_V14_SCAN_COMPLETION aborted/fw_abort`, and `MZ600_V14_ESCAN_WATCHDOG_FIRED`; no SSIDs/BSSID/private RF identities in logs.
- ARM EABI5 compile PASS, kernel vermagic **`7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`**, artifact **344536 bytes SHA256 `40a8779fe83b03201b3df79fabce55ea1f47fcd4095150889d7f9b1bc88b0df8`**, Desktop private `v064-2012-oem-escan-v14-20261026/brcmfmac-2012-escan-event69-v14.ko`.
- Builder SHA-preserved and restored source and original baseline module after building. No installed kernel changes.

## Test script

[`scripts/host/xoom/test-mz600-v14-2012-5180-passive-escan-owner-20261026.sh`](../../scripts/host/xoom/test-mz600-v14-2012-5180-passive-escan-owner-20261026.sh), **6481 bytes SHA256 `5e90a8bd7867073eb9682363eeeb68733d8cca98f1e18c696d85db035d8182d3`**, Bash syntax PASS on Desktop. Derived from physically successful V13 rollback lifecycle and checked as new one-shot. Unique marker `/run/mz600-v14-2012-bandlist-20261026.attempted` (the actual script's concrete `ONCE` constant is authoritative; do not rerun).

- Preflight exact kernel, Debian p8, no prior overlay/WLAN/BT modules/services, FDT MAC and SDIO physical presence, old installed .bin/.txt/.ko SHA, candidate new .bin and module SHA+size.
- Bind-mount only later OEM firmware RAM file over base .bin, original NVRAM unchanged; load ARM diagnostic module and firmware; firmware band/channel readouts.
- Requires actual `iw phy` CH36 5180MHz `no IR` and not `disabled` or `radar`; otherwise REFUSE scan. Driver independently limits to one passive channel. Does one `iw dev wlan0 scan freq 5180 passive` under `timeout -k 3s 24s`, with stdout/stderr held privately in `/run` and erased, reporting count, rc, elapsed milliseconds only. Fresh dmesg markers record ESCAN/Event69, BSS versions, aborted/watchdog.
- Always cleanly down interface, remove modules, unmount firmware overlay, compare original SHA and absence of wlan0/Broadcom modules; no permanent .bin/.ko/NVRAM write, boot change, association or driver install.
- **A successfully executed one-shot is NOT the same as successful ESCAN**. Inspect set RC, Event69 terminal status, command exit and BSS version; never declare Event69 complete based solely on cleaned status.

## Surface package: integrity verified

At `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V14-2012-ESCAN-20261026`:

| File | Size | SHA256 |
|---|---:|---|
| mz600-v14-oem2012.bin | 264140 | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` |
| mz600-v14-escan-event69.ko | 344536 | `40a8779fe83b03201b3df79fabce55ea1f47fcd4095150889d7f9b1bc88b0df8` |
| mz600-v14-passive-scan.sh | 6481 | `5e90a8bd7867073eb9682363eeeb68733d8cca98f1e18c696d85db035d8182d3` |
| mz600-v14-owner-once.py | 10426 | `7ff5d22ee4e5f562c68acc0b553fdd059473c26fb4412b3c1f871d0f416b7ad5` |

Python launcher code: [`scripts/host/surface/mz600-v14-2012-5180-passive-escan-owner-once-20261026.py`](../../scripts/host/surface/mz600-v14-2012-5180-passive-escan-owner-once-20261026.py). Python `py_compile` PASS on Surface. Surface receipt/attempt marker **absent** at staging time. Uses existing verified serial ACK gzip+base64 streaming for FW + module to /run, independent pre/post SHA audit and `bash -n`, one guarded execution. On user execution it writes private full COM9 log and machine-readable receipt in same Surface folder.

**Command when authorized COM9 user session is free:**
```powershell
python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V14-2012-ESCAN-20261026\mz600-v14-owner-once.py"
```
A separate user Python PID 13444 was still running `xoom-v068-bluez4-sdp-reconnect-check.py` at staging; **do not stop/hijack it**. The new launcher's serial open should fail safely when COM9 is held, but close the prior session normally first.

## Transfer procedure

Desktop host temporary HTTP server was restricted by existing inbound firewall port43157 remote `192.168.0.40` Surface; downloaded two source-pinned binaries and verified Surface SHA. The exact temporary HTTP server PID was verified, stopped, and TCP43157 closed; temporary private staging directory was removed. Source files never published to GitHub. Existing firewall rule left in place.

## Decision after owner run

- If `MZ600_V14_ESCAN_SET_RC=0` and Event69 **terminal SUCCESS** with valid BSS and no watchdog, prioritize modern `escan` with 2012 OEM image and next check 2.4 GHz scan/association + BT coexistence before any installation.
- If `-52`, keep 2012 dualband but revisit legacy ISCAN or direct event26/old ioctl scan paths. If Event69 SUCCESS but `FINAL_BSS version=108` vs Linux7 expected109, treat as parser-compatibility follow-up, **not** firmware scan failure.
- If no success/abort event, retain known-good V13/HRI39 and investigate event transport without claiming result count = terminal.
- Any rollback incomplete -> stop, inspect, don't repeat consumed one-shot.

Build code and public docs only; private OEM firmware, calibration values, MAC and BSSID stay off GitHub.
