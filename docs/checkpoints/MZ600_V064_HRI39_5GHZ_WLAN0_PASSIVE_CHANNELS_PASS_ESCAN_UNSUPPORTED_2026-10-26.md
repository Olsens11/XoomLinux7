# MZ600 Linux7: original Motorola BCM4329 dual-band `wlan0` physically achieved with passive-only legacy channel fallback; legacy scan API still fails

**Date:** 2026-10-26. **Physical board:** experimental Motorola MZ600, permanent kernel `7.0.0-next-20260422+`, Debian 12.15 on internal p8; Surface COM9 root. **Status:** 5GHz channel discovery and WLAN0 **PASS**, bounded passive-scan **NOT YET PASS** (legacy `escan` returns -52). **No reboot, flash, association, active scan, permanent module or firmware/NVRAM change.** This does not qualify the separate BCM4329 combined-chip provider or any upstream patch.

## Baseline inherited from immediately preceding OEM firmware milestone

Prior [HRI39 original dual-band firmware and legacy valid-channel ioctl test](MZ600_V064_HRI39_OEM_FIRMWARE_TWO_BANDS_LEGACY_VALID_CHANNELS_20_PASS_2026-10-26.md) proved original Motorola firmware `4.218.248.20` (261317B SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`) + exact original `ccode=US`, `regrev=69` MAC-stripped original board calibration (1569B SHA `6de236d4d097f4996e1fef31d538757bfd9f4024cbcf2ade8bbaa97c040e53c4`) booted and responded:

```text
MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
MZ600_5G_DIAG_WIPHY has2g=1 has5g=1
MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=5553 ccode=5553 rev=69
MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=20 2g=11 5g=9 other=0 max=383
```

Modern `brcmfmac` failed at new `chanspecs` iovar (`-EBADE = -52`), so older firmware did not produce wlan0 before this work. Current generic 4.220.48 firmware produces normal 2GHz wlan0+19 BSS scan; use as regression reference, not something to discard.

## New v05 lab-only kernel compatibility module — exact ABI compiled

New [reproducible v05 BCM4329 legacy-passive-only builder](../../scripts/experiments/build-v064-bcm4329-legacy-passive-only-wiphy-20261026.py) composes previous count-only diagnostics plus a *narrow original-firmware compatibility fallback* at `brcmf_construct_chaninfo()`. The only compatibility path is **BCM4329 chip ID** with modern `chanspecs` returning `-EBADE` and firmware legacy `WLC_GET_VALID_CHANNELS=217` returning success, a bounded valid channel count, 5GHz entries and no unexpected values. It maps **actual firmware channel numbers** to the original Linux 2G/5G wiphy channel tables, rather than inventing channel listings or overriding firmware bandlist.

Safety in the current lab version:
- Initialize all channels as disabled, then enable only numbered channels returned by firmware and found in the kernel's existing channel tables, unless `orig_flags` disabled them.
- **Every enabled fallback channel:** `IEEE80211_CHAN_NO_IR`, `IEEE80211_CHAN_NO_HT40`, `IEEE80211_CHAN_NO_80MHZ`, `IEEE80211_CHAN_NO_160MHZ`, and preserve original disabling flags.
- Range 5260–5720 MHz additionally radar-restricted, and kernel cfg80211 regulatory logic applies.
- **No `iw reg set`**, no firmware country adjustment after bootstrap, no persistent image modifications and no active scan. The lab branch preserves modern firmware normal path, does not claim complete regulatory qualification and is **NOT** a finished upstream patch.

Live module artifact (PRIVATE, never committed as binary): 343200B `brcmfmac.ko` SHA256 **`ff19d91726f406468d6cc9516d43a851f6a7a22d403259094ae376041671db29`**. Source diff SHA256 **`9ef957fc8c8a8d4843e35666db8d71092d06c92a456d5d17d1521d2125b7575a`**, `git apply --check` PASS against exact kernel; ARM GNU14.3, CONFIG_MODVERSIONS exact `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`. All canonical build source and original .ko restored, original module baseline SHA `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`. Transferred Desktop→Surface via existing authenticated SSH/SCP, then COM9 186-frame gzip/base64 SHA-pinned delivery into Xoom **/run only**, independent device hash PASS, not installed.

## First native test: dual-band WLAN0 and 9 NO_IR 5GHz channels PHYSICAL PASS

[Guarded v05 one-shot](../../scripts/host/xoom/test-v064-original-motorola-hri39-passive-only-fallback-20261026.sh) SHA256 `c5c18cf0fc5f1715a6fd421b0b17352c393cee65fdee62d5ce871e175310e223`: OEM FW and original-MAC-omitted matching US/69 calibration temporarily bind mounted from Xoom RAM. Root kernel/p8, all firmware/module SHA and radio-absence preflight passed. Exact v05 passive-only .ko `insmod` and standard WCC `modprobe` produced:

```text
MZ600_HRI39_PASSIVE_WCC_LOAD_RC=0
MZ600_HRI39_PASSIVE_WLAN0_PRESENT
MZ600_HRI39_PASSIVE_DYNAMIC_PHY=9
MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK chip=4329 fw2g=11 fw5g=9 no_ir=1 ht20_only=1
MZ600_HRI39_PASSIVE_PHY_5GHZ_FREQ_COUNT=29 NO_IR=9 NOT_DISABLED_NO_IR_MISSING=0
```

`29` is **the number of all static 5GHz entries shown by `iw phy`, including 20 disabled; only NINE are enabled/no-IR**. Specifically supported firmware 5GHz channels: **36 (5180MHz), 40 (5200), 44 (5220), 48 (5240), 149 (5745), 153 (5765), 157 (5785), 161 (5805), 165 (5825)**, each rendered `(no IR)`, with remaining 5GHz channels disabled. `iw reg get` showed global `country 00` world regulatory and per-phy `country 99`; world low 5170–5250 region specifies PASSIVE-SCAN. **Phy99 is a firmware-defined regulatory view, not proof of a signed US region mapping; do not silently authorize transmissions or report USA legal compliance from it.**

No scan in this first test. WCC→brcmfmac→brcmutil unload all rc0, both RAM firmware mounts umounted rc0, previous normal Debian files hash verified. Private host transcript: `MZ600-HRI39-PassiveOnly-v5-PRIVATE-RESULT-20261026.txt`, SHA `4458dc90aee032687843392c38aea65b20b5b79f8fffe8a4d7a3874c9afd233b`.

## Actual passive scan attempt(s) — first harness bug, second genuine radio API failure

The user previously asked to reach `wlan0` and try a 5GHz scan. Attempted **strictly PASSIVE** scan of only channels 36/40/44/48 after checking `NO_IR` and world 00, with no supplicant/DHCP/network credentials.

- v1 [scan harness](../../scripts/host/xoom/test-v064-hri39-5ghz-passive-scan-only-20261026.sh), SHA `42ad2cc86ac7e3a9f8fdccae46b2739cecf2b37416f927d91b635c543b6153fb`, successfully initialized OEM firmware and dual-band wlan0, verified regulatory channel entries, but emitted `bash: line 145: f_NO_IR_VERIFIED: unbound variable`. Bash interpreted `$f_NO_IR_VERIFIED` rather than `${f}_NO_IR_VERIFIED` inside a **test marker only**. **NO scan was initiated in v1**; cleanup, original firmware restore PASS. Do not repeat.
- Corrected [v2 5GHz passive scan](../../scripts/host/xoom/test-v064-hri39-5ghz-passive-scan-v2-20261026.sh), SHA `5b5a7001164d36fba3b0e540fd5b97a4a6cd11d937e78fd0cc3dc25fce0dec9a`, distinct one-time paths; **all four channel safety preflights** marked PASS, `wlan0` dynamically `phy11`, `ip link set wlan0 up` rc0; then `timeout ... iw dev wlan0 scan freq 5180 5200 5220 5240 passive` returned **exit 204** from `iw` and a private 39-byte output:
  ```text
  command failed: Invalid exchange (-52)
  ```
  Device `dmesg` independently showed:
  ```text
  ieee80211 phy11: brcmf_run_escan: error (-52)
  ieee80211 phy11: brcmf_cfg80211_scan: scan error (-52)
  ```
  Thus **NO 5GHz scan success, no BSS discovery**. Scan error is firmware interface mismatch with modern `escan`, NOT a lack of enabled physical 5GHz channels. Actual firmware-bandlist/legacy-channel fallback and `wlan0` remained successful.
- v2 private 39-byte output SHA **`8251e4097b04dab99f6705f5285a696043e2d1132a1968d746a6ee764a228d92`** (no SSIDs because failed). Private Surface v2 transcript SHA **`c1e65793f41323c8e1573ce25e80825cad58a94598119f5e9f73ed643c831024`**, result receipt JSON SHA **`a9c6e9d56e4d1c1ed3e56d7474888f5d64497d2f7c4815e1fa87a073fe1551e2`**.

**Both scan attempts safely cleaned up:** all 3 Broadcom modules modprobe -r rc0, both RAM firmware and calibration overlay unmount rc0, original FW/NVRAM and installed .ko hash verified, no wlan0. Neither scan used association, active probing, user SSID or saved network credentials.

## Independent post-test proof (not merely script markers)

Separate authenticated root COM9 read-only audit **after v2**:

```text
uname -r: 7.0.0-next-20260422+
root filesystem: /dev/mmcblk0p8 ext4
/sys/class/net: ip6tnl0 lo sit0
/proc/modules: NO_BRCM_MODULES
FW_OVERLAY_ABSENT
CAL_OVERLAY_ABSENT
firmware SHA256 d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93
calibration SHA256 a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb
installed brcmfmac.ko SHA256 9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb
dbus.socket / dbus.service: active, active
```

No p7/GPT/recovery or /lib/modules writes occurred; independent raw p7 hash **not rerun** in this checkpoint.

## Next compatibility gap — old Motorola scan initiation and results

Read-only kernel/source audit:
- Pinned Linux7 `brcmf_run_escan` in `brcmfmac/cfg80211.c` (~lines 1442–1505) **unconditionally sends `brcmf_fil_iovar_data_set(ifp, "escan", ...)`**, with v1/v2 scan structs. On original 2011 firmware this returned **`-EBADE=-52`**, which `brcmf_cfg80211_scan` propagates immediately; it never reaches a successful scan event/results.
- Motorola-era Broadcom `wl_iw.c` (public [Froyo source](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/b4ace791eb574f589c53be582ea0d14e1a85ff09/bcm4329/src/wl/sys/wl_iw.c)) instead supports **legacy ioctl `WLC_SCAN=50` plus `WLC_SCAN_RESULTS=51`**, and an optional incremental `iscan` firmware path. It also controls `WLC_SET_PASSIVE_SCAN=49` and scan results use versioned `wl_scan_results_t` with per-BSS length bounds; [older protocol struct source](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/include/wlioctl.h).
- A proper **separate, narrowly-scoped** legacy scan compatibility patch must implement a scan state machine, passive-only flag enforcement before issuing legacy `WLC_SCAN`, strictly bounded 5180–5240 channels, asynchronous/polled `WLC_SCAN_RESULTS`, correctly parsed versioned/BSS IE boundaries and `cfg80211_inform_bss` plus `cfg80211_scan_done`, timeouts/cancel/suspend/unload and error cleanup. **Do not simply replace `"escan"` with `"iscan"` or claim an ioctl scan result from raw bytes.** Avoid unverified active TX. Current proof establishes channel enumeration and cfg80211 registration, NOT scan support.
- Keep OEM full-chip shared U4/I7/U0/U2/LPO, Motorola six-field SDIO quirk, modern cfg80211 regulatory compliance and per-device factory MAC independent. Multi-device MZ600/MZ602/MZ604 qualification and owner permission before any upstream series.

**Latest milestone classification:** OEM firmware 4.218.248.20 with original board US69 calibration **dual-band native Linux `wlan0` physically PASS**; 9 5GHz firmware-supported channels exposed passive-only with existing regulatory rules; initial 5GHz passive scan **FAIL (legacy firmware `escan` unsupported -52)**. Known-good generic Debian untouched, rollback independently verified. Lab fallback **not yet fully validated for self-use or submitted upstream**.

## Exact tested lab patch retained for reproducible continuation

The complete generated v05 source diff, not merely its builder script, has now also been retained as [patches/lab/0005-brcmfmac-bcm4329-legacy-valid-channel-passive-only-fallback.patch](../../patches/lab/0005-brcmfmac-bcm4329-legacy-valid-channel-passive-only-fallback.patch). After reconstructing the final whitespace-prefixed unified-diff context line, Desktop WSL independently checked that its **SHA256 is exactly `9ef957fc8c8a8d4843e35666db8d71092d06c92a456d5d17d1521d2125b7575a`**, byte-for-byte identical to the source diff from the physically tested module build. `git apply --check` PASS against the exact pristine kernel source, 21/21 BCM4329 host tests PASS, 149/149 datasheet index and 36/36 requirement checks PASS. The tracked file remains under **patches/lab** and NOT `patches/upstream/rfc/series`.

**Future code-review caution:** this is a proof-of-function lab patch containing explanatory count-only diagnostics and broad labeling such as “Diagnostic ONLY” inherited from v04, even though v05 actually conditionally constructs passive-only channels. Before producing a clean upstream-quality series, strip diagnostic scaffolding, eliminate stale comments, scrutinize host regulatory self-management, verify firmware-supported channels cannot activate TX during driver init, and test exact scan/cancel/timeout and BT concurrency. Do not treat this as final user-facing firmware installation.
