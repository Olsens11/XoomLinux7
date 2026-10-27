# MZ600 V15 — controlled 2.4GHz channel1 ESCAN completion comparison — ARM built and Surface staged

**Date:** 2026-10-26. **Status: OFFLINE BUILD + SURFACE STAGING PASS; OWNER PHYSICAL TEST PENDING.** This is an entirely NEW unique v15 experiment, not a repeat of V14. No v15 firmware overlay, RF scan, module load or Xoom command has been executed in this research turn.

## Why V15 now

[V14 physical record](MZ600_V14_2012_ESCAN_EVENT69_PARTIAL_BSS109_PASS_TERMINAL_MISSING_2026-10-26.md) established with **May 25 2012 OEM BCM4329 4.218.248.44**:
- Actual dual band 11 valid 2G and 24 valid 5G channels, original stock Linux7 NVRAM unchanged, safe old ioctl217 NO_IR fallback.
- One passive non-DFS 5GHz **5180MHz ch36** `escan` V1 request accepted RC0, actual **Event69 status8 PARTIAL**, one BSS v109 record delivered (matches Linux7).
- **No terminal Event69 SUCCESS**, 10s watchdog, aborted=true, `iw` exit0 but zero public BSS records; independent rollback PASS. Consumed v14 cannot be rerun.
- V15 tests **same firmware and normal Linux7 ESCAN code**, *only* one **2.4GHz 2412MHz channel1 passive** instead of 5GHz ch36, to see whether missing terminal is band-dependent versus a common old protocol behavior. A PASSIVE-only scan may collect BSS records; count is NOT proof of completion. No SSID/probes/association.

## New ARMv7 temporary driver build

[`tools/forensics/build_mz600_v15_2012_2g_escan_lab_module.py`](../../tools/forensics/build_mz600_v15_2012_2g_escan_lab_module.py) is V14's proven source-restore builder transformed to **V15 ch1=2412** scan gate; it retains the original Broadcom BCM4329 legacy ioctl217 passive-only wiphy fallback, double passive constraints (no SSID/IE, `NO_IR`, `!DISABLED`, `!RADAR`, firmware global passive scan=1), and Event69 status/BSS109/ESCAN error/watchdog/completion diagnostics. V15 has separate distinct `MZ600_V15_*` log markers, no user MAC or nearby SSID logging.

- ARM module `brcmfmac-2012-escan-event69-v15.ko` **344536 bytes**, SHA256 `8ab54acbb204aeab49bdbf2ef4265fc40c8454e8a5c07ba57d11028105c719f4`. Built against matching `7.0.0-next-20260422+` ARMv7 EABI, original baseline source and installed module restored after host build (source SHA `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`, baseline .ko SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`).
- Firmware exactly same previously validated private `4.218.248.44`, **264140 bytes**, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`. It is NOT stored in Git.
- Distinct script [`scripts/host/xoom/test-mz600-v15-2012-2412-passive-escan-owner-20261026.sh`](../../scripts/host/xoom/test-mz600-v15-2012-2412-passive-escan-owner-20261026.sh), **6754 bytes**, SHA `63a80df74ad805db3ace9bde19fc7a67b34925087d65118a10c8706021683cee`, Bash syntax PASS.
- Script preflight verifies original Debian p8/Linux7 kernel, no WLAN/BT/modules/net manager, FDT MAC present, no mounted overlays, original FW/NVRAM/module pinned SHA, RAM candidate hashes, ch1 wiphy `2412 MHz [1]` present with NO_IR and not disabled or radar. If not, **no scan**. One `iw dev wlan0 scan freq 2412 passive`, 24s bounded external command timeout, records only elapsed, rc and counts; separate safe numerical `MZ600_V15_EVENT69_STATUS_COUNTS success=X partial=Y other=Z` after filtering fresh dmesg. Discerns kernel terminal SUCCESS from watchdog and sanitized BSS version/count; preserves private scan contents only temporarily in RAM then deletes.
- Rollback unloads Broadcom modules, downs interface, unmounts only matching SHA firmware bind overlay, verifies installed old FW/NVRAM/kernel module SHA, no wlan0 and no loaded radio modules. Independent Surface poststate audit confirms. No permanent firmware/calibration/regulatory changes.

## Surface one-shot package and integrity

Staged to `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V15-2012-2412-ESCAN-20261026`, verified matching SHA on Surface:

| File | Bytes | SHA256 |
|---|---:|---|
| `mz600-v15-oem2012.bin` | 264140 | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` |
| `mz600-v15-escan-event69.ko` | 344536 | `8ab54acbb204aeab49bdbf2ef4265fc40c8454e8a5c07ba57d11028105c719f4` |
| `mz600-v15-passive-scan.sh` | 6754 | `63a80df74ad805db3ace9bde19fc7a67b34925087d65118a10c8706021683cee` |
| `mz600-v15-owner-once.py` | 10417 | `f5f55c0f22e69d1bb535c5b5bde273f14a8658f3374bd35efaeba73078590dfc` |

Surface Python py_compile PASS, v15 owner marker and receipt ABSENT. Launcher [source](../../scripts/host/surface/mz600-v15-2012-2412-passive-escan-owner-once-20261026.py) reuses physically successful V14 gzip/base64 ACK serial upload and hashes firmware+module into /run, one checked script `bash -n`, execution then independent restoration check, preserves private transcript+receipt locally. It explicitly does not equate a clean test/rollback with successfully terminal-completed scan.

**Surface PowerShell owner action, only after safely closing separate COM9 Bluetooth process:**

```powershell
python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V15-2012-2412-ESCAN-20261026\mz600-v15-owner-once.py"
```

At stage time existing unrelated user Python PID13444 `xoom-v068-bluez4-sdp-reconnect-check.py` was still active: do NOT terminate this process without owner permission or race it for COM9. Launcher fails closed if COM9 unavailable. Run only **ONCE**, preserve partial receipts and stop on error.

Firmware binary transfer used approved Desktop->Surface TCP43157 existing Surface-restricted firewall rule; matching SHA Surface checked. Temporary Python http server verified and stopped, port closed, temp staging removed.

## Expected interpretation

- Terminal Event69 `status=0` + completion aborted=false with no watchdog on 2.4GHz -> **missing terminal is specific to 5GHz or per-channel/dwell conditions**, requiring focused audit.
- Partial Event69 on 2.4GHz but watchdog and no status0 -> **common 2012 ESCAN terminal signaling gap** possible; do NOT assume Event69 raw receive is broken because PARTIAL already arrived.
- No partial result does not prove scan engine failure (environment may have no AP beacons), but accepted RC and terminal status still informative.
- `iw` exit0, nonzero internal BSS count, or scan results in stale buffer alone are NOT terminal evidence. The single attempt's logs must be evaluated together with firmware status and cleanup state.

**Do not modify original permanently or rerun used one-shot.**
