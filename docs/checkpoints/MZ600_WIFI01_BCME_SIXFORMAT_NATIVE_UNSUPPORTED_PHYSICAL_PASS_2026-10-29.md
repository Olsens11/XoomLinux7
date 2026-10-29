# MZ600 WIFI-01: six native Broadcom per-channel ABI queries all BCME_UNSUPPORTED — actual physical test, 2026-10-29

**Status: PHYSICAL SIX-QUERY DIAGNOSTIC PASS; all six metadata queries returned native `BCME_UNSUPPORTED (-23)`; complete original p10/NM/WLAN rollback PASS and independent postflight PASS.** No RF scan, forced country, TX-power modification, association in the trial, permanent firmware install, boot flash, partition write or new upstream patch. This is a meaningful **negative firmware capability result**, not regulatory/5GHz production acceptance. Existing WIFI-01 r3 remains unsigned and unaccepted; issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4) remains OPEN.

## Historical lookup, intent and sources

Prior physical [r2](MZ600_WIFI01_R2_OEM_2012_PERCHAN_PHYSICAL_AND_HISTORY_2026-10-28.md) returned OEM May2012 dual band and 35 valid channels but **0/35** modern `per_chan_info` success, without original BCME codes. [Oct28 ABI research](../research/MZ600_BCM4329_LEGACY_CHANNEL_REGULATORY_CONTRACT_2026-10-28.md) found three source-grounded argument formats: original archived Xoom band+channel, intermediate band+BW20, modern D11n full HT20. [Oct29 source audit](../research/MZ600_WIFI01_R3_FWERR_COLLAPSE_AND_IOCTL_ABI_SOURCE_AUDIT_2026-10-29.md) proved pinned `fwil.c` normally maps **any** negative firmware BCME to `-EBADE`; hence r3's unsupported-cache treats multiple different errors alike. This trial captures the native error before that mapping.

Original Oct26 v05/V13 blanket passive-only fallback was a **lab safeguard**; V28 intentionally retired it and restrictive scan gates to return to native cfg80211, with legitimate changing NO_IR state and an independent firmware-UP/MPC issue. Do not reinstate obsolete broad NO_IR workarounds as a proven production policy. User wants **one logical issue per patch**, refining WIFI-01 instead of adding a fifth chronological fixup, and no human DCO until ready.

## Exact source provenance and offline build

- Upstream pinned base `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Project branch `wip/clean-wifi-bt-usb-20261025`.
- Desktop `DESKTOP-R16QJD4` resumed online; fresh independent WSL worktree `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-nine-r3-bcme-abi-source-20261029` created directly from pinned base. Exactly nine review patch files replayed in order: DT-01/02/03, BOOT-01, WIFI-01 r3, WIFI-02/03/04, STORAGE-01. Replay **9/9 PASS**, `git diff --check` PASS, original nine-member source kept unchanged. This is **r3 substitution**, not stacking r1/r2/r3.
- [Reproducible lab-only generator and two-file trace](../../tools/diagnostics/README-MZ600-WIFI01-BCME-ABI-20261029.md) applied separately, not part of nine submit candidates. Lab-overlay SHA256 `c748a30d30d3e0ed25338e7ca9057f2f16a719bb7d3d4e83701f1d9913f38f43`. Two edited files: `brcmfmac/cfg80211.c` bounded six read-only `BRCMF_C_GET_VAR/per_chan_info` calls and duplicate `BRCMF_C_GET_VERSION` read; `brcmfmac/fwil.c` narrowly gated logging of original negative BCME and transport error **before** `-EBADE` conversion. No persistent shared `ifp->fwil_fwerr` toggle, no channel set/scan/power IOCTL. No device identifiers in lab output.
- ARM toolchain `arm-none-linux-gnueabihf-gcc 14.3.1`, same trusted original nine-build `.config`, `CONFIG_MODVERSIONS=y`. Fresh isolated O= `qa-nine-r3-bcme-abi-build-20261029`: **olddefconfig PASS**, **prepare PASS**, **full brcmfmac prefix PASS**, **full zImage PASS**, **DTBs PASS**, **complete modules PASS**.
- Lab `brcmfmac.ko`: **344756 bytes**, SHA256 **`93908d6ff54e49cbee638d4e46f96a01d04198ad2481ef48ea660e9b66ffec20`**. Lab WCC `brcmfmac-wcc.ko`: 5916 bytes, SHA256 `eb9aa7efc8d9e356088aa9693cf1937c8c7e1a65dcd0193618915521b7a048b9`, byte-exact original.
- `modprobe --dump-modversions` comparison against physically validated original nine-build: **core 259/259 imported CRCs equal**, **WCC 7/7 equal**, zero new or mismatched imported symbols. Real ABI coherence **PASS**, not just a successful compile.

## Transfer, physical test and privacy

- Only the compiled diagnostic `.ko` staged from WSL into a fresh desktop Windows temp directory. Brief known-good LAN HTTP port **43157**, bound to desktop `192.168.0.125` and the single new directory. Surface `Invoke-WebRequest` independently verified **344756 B / exact SHA**. Server process identity verified; stopped and listener closed, exact staging directory removed. No OEM firmware served over LAN.
- Original May25 2012 Motorola OEM `4.218.248.44` private file on Surface independently verified **264140 B**, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`. Existing original device NVRAM **1550 B**, no modification. Private firmware not committed.
- Fresh private trial directory on Surface: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-WIFI01-BCME-ABI-20261029-C\`. Fresh unique /run paths and one-use `.attempted` marker on replacement MZ600. SHA-verified UART COM9 transfer of firmware and lab module to RAM: both **PASS**, no radio changes during staging.
- Hardware preflight: authenticated `root@xoom-mz600`, `7.0.0-next-20260422+`, `/dev/mmcblk0p10 ext4 /`, NetworkManager and wpa_supplicant active and wlan0 `100 (connected)`, Bluetooth service inactive, no overlays, original generic firmware/NVRAM/core/WCC hashes matching exact accepted baseline. Only after all checks did one-use script stop services, unload original module, RAM-bind OEM firmware and load matched lab module; `wlan0` appeared.
- Exactly **six** instrumented read-only per-channel queries, **no scan / association / directed probing / country or power update**. Actual diagnostic console count `lab=6 fw=6`. Raw shell transcript and private receipts retained on Surface; below are sanitized numeric facts only.

## Actual native firmware responses (most important result)

`BRCMF_C_GET_VERSION` returned `rc=0, io_type=1` (the D11 family used by the running kernel). For each `per_chan_info`, the **transport layer returned 0**, but the firmware's original error was **`BCME_UNSUPPORTED = -23`**. The normal public Linux return was **`-EBADE = -52`**. Every response was explicitly marked **no valid result**, so no radar/passive/valid-channel flags can be inferred.

| Channel | Historical argument and format | Transport | Native BCME | Linux return | Valid metadata |
| --- | --- | --- | --- | --- | --- |
| 2.4GHz ch11 | `0x200b` (band+channel) | 0 | **-23** | -52 | NO |
| 2.4GHz ch11 | `0x280b` (+BW20) | 0 | **-23** | -52 | NO |
| 2.4GHz ch11 | `0x2b0b` (full D11n HT20) | 0 | **-23** | -52 | NO |
| 5GHz ch36 | `0x1024` (band+channel) | 0 | **-23** | -52 | NO |
| 5GHz ch36 | `0x1824` (+BW20) | 0 | **-23** | -52 | NO |
| 5GHz ch36 | `0x1b24` (full D11n HT20) | 0 | **-23** | -52 | NO |

**Confirm native code meaning:** pinned upstream `brcmfmac/feature.c` explicitly defines `BRCMF_FW_UNSUPPORTED 23` and uses `-BRCMF_FW_UNSUPPORTED` for true firmware feature tests. This physically rules out an incorrect chanspec encoding *alone* as the remedy among these three historically documented forms for this particular firmware/hardware state. It does **not** prove every possible alternative private iovar, firmware branch, version or response method is absent.

**Source consequence:** R3's `-EBADE`-as-unsupported inference happened to match the actual native **unsupported** result here, but its generic inference is still unsound: other native failures are collapsed to the same Linux error. Do not treat unknown future `-EBADE` as equivalent to BCME_UNSUPPORTED without provenance or a narrowly safe fallback policy.

## Automatic rollback and independent postflight

- RAM-only trial exit `rc=0`; six queries captured, no scan; cleanup trap `OEM_FIRMWARE_UNMOUNT_RC=0`; original installed firmware/NVRAM/core/WCC SHA256 restored; brcmutil, brcmfmac, WCC, WPA, NetworkManager restart calls each `rc=0`; NetworkManager `wlan0` returned `100 (connected)`.
- **Second, independent read-only COM9 postflight**, separate Python process after test script closed COM9, confirmed p10 kernel/partition, all original firmware/NVRAM/core/WCC hashes, restored modules and connected Wi-Fi; **zero overlays, zero failed postflight checks**. COM9 released again. Original p7/p8/p10 partitions/boot/TWRP never written; no persistent lab module installed.
- Saved proof in private Surface `mz600-bcme-C-private.txt`, `mz600-bcme-C-receipt.json`, `independent-postflight-private.txt`; do not publish private MAC/SSID/serial/logs or proprietary OEM firmware.

## Engineering disposition and next step

**Issue #4 remains OPEN.** The six proven old/new `per_chan_info` input variants all returned actual firmware `BCME_UNSUPPORTED`; repeated broad ABI-guessing is now low-value. Existing WIFI-01 should be refined for a **truthful legacy capability boundary**: accepted channel inventory from `GET_VALID_CHANNELS` is *not* per-channel RF permission; do not copy old permissive alpha2 `99` OEM regdomain, force US69, clear NO_IR or guess DFS. Cross-check real signed cfg80211/regdb/country/OTP rules and firmware-supported channels, preserve conservative HT20 and restrictions; explicitly qualify dynamic NO_IR/beacon hints and legitimate association before upstream acceptance. Consider whether the source should skip the unsupported per-channel iovar on **firmware-specific verified evidence** rather than collapsing arbitrary `-EBADE` to unsupported. If an entirely different firmware metadata API exists, research and demonstrate it before a new proposal.

Keep WIFI-02/03/04 unchanged (separate scan ID, event owner, MPC/readiness scopes), and **amend WIFI-01 within its one logical issue**, not a fifth patch. No owner DCO or upstream submission. The successful exact-source test is a firmware-interface finding, **not** a claim that r3 is safe or production-ready.
