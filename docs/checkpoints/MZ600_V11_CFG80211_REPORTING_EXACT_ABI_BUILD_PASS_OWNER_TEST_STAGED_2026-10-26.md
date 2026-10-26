# MZ600 original BCM4329 firmware — v11 cfg80211 BSS reporting build PHYSICAL TEST PENDING

**2026-10-26 approximately 16:07 EDT**, owner has run the exact v11 builder on authorized Windows Desktop WSL. This checkpoint supersedes [earlier v11 source-only/build-blocked checkpoint](MZ600_V11_LEGACY_BSS108_CFG80211_REPORTING_SOURCE_READY_BUILD_BLOCKED_2026-10-26.md). **Exact-ABI offline build PASSED; user-controlled RAM-only physical test prepared on Surface; NOT EXECUTED.** No persistent Xoom module/firmware/boot changes or restart by the assistant.

## Verified on Desktop, independent of owner's terminal output

Actual Desktop WSL path:
`/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-legacy-v108-cfg80211-inform-v11-20261026/`.

- Exact artifact `brcmfmac-legacy-v108-cfg80211-inform-v11.ko`: **347368 bytes** (file and standalone sha256sum verified), SHA256 **`2c7b3bd5799b08e5c10b828cf498f4957e5c1174a2e96d1962654566ceb47334`**.
- Module vermagic report: `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`, matching installed kernel.
- Actual `build.log`: `CC [M] cfg80211.o`, `LD [M] brcmfmac.o`, `MODPOST Module.symvers`, `LD [M] brcmfmac.ko`, no error reported.
- Actual `offline-build-result.json` `result=V11_LAB_ONLY_BSS108_VERIFIED_TO_CFG80211_ABI_BUILT`, `physical_scan_performed=false`, `scan_lifecycle_change=false`, `upstream_ready=false`.
- Source diff `0011-bcm4329-lab-v108-cfg80211-bss-inform.patch` SHA256 **`406e140c827facc1cfacdeb50997fc04b01ec5858ea62a94aa702cef601c3826`**.
- The report verified original ABI module SHA **`9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`**; Desktop Git checkout clean. Do not imply original p7 kernel partition was re-hashed by this operation.
- [Source builder](../../scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py) commits originally 84e33c9/d5e1004/7a83c3c. Build extends physically proven v10 single channel36 5180MHz NO_IR 300ms passive HRI39 old FW WLC_SCAN50/SCAN_RESULTS51, version108 fixed/IE TLV validation and event26 observation-only.

### What the new code changes

Adds `brcmf_legacy_inform_bss108()` invoked after **all** old v108 record+IE layout checks succeed; separately preflights all records' wire version/length, channel36, RSSI range, BSSID validity and complete consumption before publishing any record. Requires actual wiphy frequency5180, 5GHz, channel36, explicitly NO_IR, not disabled/radar, matching the only requested scan channel. Copies validated legacy metadata into cfg80211 `cfg80211_inform_bss_data()`, then `cfg80211_put_bss()` for each BSS. Logs only integer `MZ600_LEGACY_CFG80211_BSS_INFORM count=... requested=...`, not any nearby BSSID/SSID/IE. Ordinary owner-local `iw scan` output should now contain BSS entries from the kernel cache IF reporting works; owner one-shot redirects all that output privately into RAM, only reporting the integer number of BSS blocks, then erases private raw output in cleanup. **No firmware event/lifecycle change:** current scan still reads v108 results on the roughly ten-second escan timeout, with event26 observer only.

The initial assistant-initiated automated kernel build was remote-tool safety-blocked, but the owner used the documented Desktop PowerShell command to compile successfully. The module was **not** built on or installed to the Xoom.

## Surface staging and manual guarded test, NOT EXECUTED

Via existing authenticated devdesktop SSH/SCP, a Desktop staging copy and Surface copy independently verified same 347368B and exact module SHA, with **no new firewall rule**. Private Surface artifacts in `C:\Users\olsen\xoom-linux-rom\captures\`:

- `MZ600-BRCMFMAC-V11-CFG80211-20261026.ko`, 347368 B SHA `2c7b3bd5799b08e5c10b828cf498f4957e5c1174a2e96d1962654566ceb47334`.
- `MZ600-V064-V11-CFG80211-RAM-SERIAL-UPLOAD-20261026.py`, existing successful 109-line gzip/base64/COM9 ACK and SHA protocol with only module size/name/SHA, unique receipt, destination changed. SHA `11ced05b7bcaf6f0aae4776ee7d849abc1cc92966765e592f81b2d4f65c6bda9`, RAM target `/run/mz600-v064-legacy-v11-cfg80211-20261026.ko`; does **not** insmod.
- [Source v11 guarded shell](../../scripts/host/xoom/test-v064-hri39-v11-cfg80211-bss-inform-one-shot-20261026.sh), Surface filename `MZ600-V11-USER-ONESHOT-SCAN-20261026.sh`, **208 lines / 9394B**, SHA `190e90ff9b05a217a04d0f315d0e55dae323c4bf02de93ebb71434cc3c61aa90`. Fork of successful v10 owner scan, new once-only attempt/cal RAM paths, hash-pinned v11 module, same original HRI39 FW and matching US/69 calibration minus bootstrap MAC, factory device-specific FDT MAC. Exact same channel36 NO_IR/non-DFS single passive `iw dev wlan0 scan freq 5180 passive`. Logs bounded v108 validation, `MZ600_LEGACY_CFG80211_BSS_INFORM`, private local iw BSS line COUNT ONLY. Fails closed on mismatched positive counts, empty reply, scan error or unsafe parser; always unloads WCC→brcmfmac→brcmutil, unmounts OEM FW+cal RAM overlays and verifies original installed FW/NVRAM/module hashes/no wlan0. Raw `iw` stdout+stderr are private volatile `/run` files erased during cleanup; no nearby network identifiers committed to GitHub.
- `MZ600-V11-USER-ONE-SHOT-20261026.py`, SHA **`c72739ee8170564db4be76923a86d70453a4748376a18b107064b8f413325246`**, Python `py_compile` PASS and internal file-size/SHA/static string gates checked. **Extra pre-RF protection:** after upload and independent SHA readback, launcher transmits the exact 208-line shell into Xoom root `bash -n` for syntax validation ONLY, no module load, no RF; refuses test if syntax failed. This avoids representing assistant-blocked direct remote `bash -n` validation as performed. The future owner run then submits the exact same source as Bash heredoc; private unique v11 COM9 transcript/JSON receipt and independent post-cleanup root read-only audit, no overwrite v7/v9/v10 evidence.
- At checkpoint creation, new `MZ600-V11-USER-ONESHOT-RECEIPT-20261026.json` **did not exist**, older v10 receipt retained. No v11 owner execution or physical BSS reporting success has happened. The module is staged on Surface only; original working Linux kernel/drivers remain installed on Xoom.

### One exact owner command (Surface PowerShell, after close other COM9 terminal)

```powershell
python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V11-USER-ONE-SHOT-20261026.py"
```

**Result interpretation:** require the new (not historical) `MZ600_LEGACY_BSS108_VALIDATION records>0 safe=1`; driver `MZ600_LEGACY_CFG80211_BSS_INFORM count>0 requested=<same>`; private `iw` BSS line count equal published count; iw scan rc0 and independent owner wrapper restoration audit PASS. Scan outcome can be inconclusive if no beacons or data fails new metadata checks; no success claim until actual receipts. This owner test is not KUnit and still relies on 10s timeout.

## Next separate project patch

[Legacy scan completion design](../research/MZ600_BCM4329_LEGACY_SCAN_EVENT26_OR_BOUNDED_POLLING_UPSTREAM_DESIGN_2026-10-26.md): no firmware event26 observed physically; investigate actual event_msgs mask and period-specific WLC_E_SCAN_COMPLETE, then asynchronous bounded polling if necessary, with correct event/timeout/cancel/suspend ownership and exactly once cfg80211_scan_done. **Do not mix with v11 BSS reporting patch.** Modern generic FW4.220.48, other Xooms, KUnit and owner upstream authorization remain open.

**Classification: V11 EXACT-ABI BUILD SUCCESS + VERIFIED SURFACE OWNER TEST READY; DEVICE REPORTING NOT PHYSICALLY TESTED.**
