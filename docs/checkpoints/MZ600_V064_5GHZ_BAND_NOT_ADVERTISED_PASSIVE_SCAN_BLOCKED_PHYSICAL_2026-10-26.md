# MZ600 Linux 7 v06.4 — 5 GHz bands missing from active PHY, scan correctly skipped: PHYSICAL DIAGNOSTIC

**Date:** 2026-10-26. **Unit:** experimental replacement MZ600; live internal Debian 12.15 armhf, `7.0.0-next-20260422+`, `/dev/mmcblk0p8 ext4`, USB COM9. **Critical owner hardware baseline:** Android previously **connected to 5 GHz Wi-Fi on the same physical device/radio**. Treat modern Linux 7 software/firmware/NVRAM/initialization differences as primary suspect, not a categorical BCM4329 hardware limitation. Do not assume the exact Android private firmware+NVRAM+driver version equals the current Debian stack.

## 5 GHz scan request, live regulatory checks

User asked to try 5 GHz scan after previous [persistent Debian 2.4 GHz 19-BSS scan physical PASS](MZ600_V064_PERSISTENT_DEBIAN_BCM4329_WLAN0_PASSIVE_SCAN_AND_ORDERED_TEARDOWN_PHYSICAL_PASS_2026-10-26.md). Live preflight confirmed kernel/root, COM9 root UID0, mmc2 SDIO 1/2/3, firmware and NVRAM, six-byte factory MAC property, DBus socket+daemon active, WPA/NetworkManager/iwd inactive, no initial `wlan0` or Broadcom modules. `iw reg get` shows `country 00` with passive 5170–5250 MHz region (and other 5GHz passive/DFS ranges). Signed upstream regdb and .p7s selected, but **regulatory permission alone does not establish PHY hardware or firmware channel capability**. No domain override, alternate NVRAM swap or RF power change.

Host kernel-independent `iw` scan syntax supports `passive` and explicit `freq`. Authored and `bash -n` tested [bounded 5 GHz PHY-check/conditional-scan](../../scripts/host/xoom/test-v064-wlan-5ghz-phy-passive-scan-once-20261026.sh), SHA pinning / authenticated COM9 preflight and independent USB readback; serial runner private transcripts retained on Surface.

### Attempt A — hardcoded PHY name exposed a *test harness* failure, not Wi-Fi or 5 GHz RF failure

First source `...-once-20261026.sh` SHA256 **`8883da0113e3e3e8b9f31390163967db29ab75f1207a6071ec487c7376fe2cba`**, COM9 118 framed lines, driver loaded; `wlan0` **PRESENT**. Attempt then called `iw phy phy0 info` but returned **`command failed: No such file or directory (-2)`**: PHY indices are dynamic across driver reloads (earlier test had phy0, not guaranteed). No 5GHz scan was attempted. On script `trap EXIT`, `ip link down` and ordered `brcmfmac-wcc`, `brcmfmac`, `brcmutil` `modprobe -r` each rc=0; verified no wlan0 and no brcm modules. Corrected harness to discover current `wiphy` from `iw dev wlan0 info`, not to change kernel or NVRAM.

### Attempt B — corrected dynamically resolved PHY and REAL no-5GHz result

Corrected script SHA256 **`51b9abe4d29222142286d0f9adae00e364fd4aa2638d9498f93c8355a4479661`**, 122 framed lines, Xoom COM9 root/ABI/rootfs PASS. Actual printed tokens:

```text
MZ600_5G_PREFLIGHT_PASS
MZ600_5G_WCC_MODULE_LOAD_RC0
MZ600_5G_WLAN0_PRESENT
MZ600_5G_DYNAMIC_WIPHY_INDEX=2
MZ600_5G_PHY_PRIVATE_SHA256=35922b8ebfdcb2808df918d0dbd0b1992a37e58f6ff57bc64f2c3bdb6565bd07
MZ600_5G_PHY_CH_36_NOT_AVAILABLE
MZ600_5G_PHY_CH_40_NOT_AVAILABLE
MZ600_5G_PHY_CH_44_NOT_AVAILABLE
MZ600_5G_PHY_CH_48_NOT_AVAILABLE
MZ600_5G_PHY_TOTAL_5000_6000_MHZ_ENTRIES=0
MZ600_5G_NO_ENABLED_NONDFS_LOW_BAND_CHANNELS
MZ600_5G_CLEANUP_BEGIN rc=0 state=UNSUPPORTED
MZ600_5G_LINK_DOWN_RC=0
MZ600_5G_UNLOAD_brcmfmac-wcc_RC=0
MZ600_5G_UNLOAD_brcmfmac_RC=0
MZ600_5G_UNLOAD_brcmutil_RC=0
MZ600_5G_CLEANUP_VERIFIED_NO_WLAN0_NO_BRCM
MZ600_5G_NO_PHY_CHANNELS_SCAN_SKIPPED_CLEAN
HOST_5GHZ_RESULT=NO_CHANNELS_CLEAN
```

**Physical conclusion:** current firmware/driver registers only Band 1 (2.4GHz), 11 permitted channels 1–11; channel 12–14 disabled; **there is no 5GHz Band 2, and zero entries 5000–6000MHz in `iw phy phy2 info`**. No Wi-Fi scan was attempted (correct safety behavior). Driver up/down cleanup all rc0. Wiphy index **2** because previous unload/reload increments counter; hardcoded `phy0` is a host test bug, not necessarily an upstream kernel bug.

Snapshot captured Xoom volatile `/run/mz600-v064-5ghz-phy-discovered-20261026-private.txt`: **2852 bytes**, SHA256 `35922b8ebfdcb2808df918d0dbd0b1992a37e58f6ff57bc64f2c3bdb6565bd07`. Private scan output file **NOT created** in attempt B because scan skipped.

## Additional read-only NVRAM / physical state audit

Private kernel NVRAM source `/lib/firmware/brcm/brcmfmac4329-sdio.txt` exists and uses historically known identity-stripped MZ600 board calibration. **DO NOT publish entire per-device firmware/NVRAM**. Read-only selected key introspection showed:

```text
aa2g=1
aa5g=1
boardtype=0x4ff
boardrev=0x10
boardflags=0x200
sromrev=3
xtalfreq=38400
cctl=0x0
ag0=1
ag1=4
pa1b0=4106
pa1b1=64563
pa1b2=65144
pa1maxpwr=42
rxpo5g=0
```

No `ccode=` or `regrev=` key surfaced in the selected grep; do not assume that the firmware’s regulatory country/revision has been proven on-device. **Important:** `aa5g=1` and 5GHz PA calibration entries make a missing 5GHz antenna declaration less likely, but they do **not** prove the active firmware enabled and authenticated 5GHz RF paths. Owner's Android 5GHz connection evidence provides independent hardware-level evidence.

Independent read-only COM9 posttest: kernel exact; `/sys/class/net` contains only `ip6tnl0 lo sit0`; `/proc/modules` no brcm; D-Bus service+socket active. No reboot, Wi-Fi RF scan, association, kernel patch, module overwrite, TWRP/p7/GPT write or regulatory override.

## Indexed datasheet and OEM provenance: relevant sections

The user's existing full [149-page datasheet index](../research/BCM4329_DATASHEET_PAGE_INDEX.md) and [36-requirement implementation audit](../research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md) remain the **primary hardware reference**; index validated at last desktop regression (**149 pages / 36 requirements**). The original uploaded PDF, rather than the index paraphrase, is specification authority.

- **p2–3, p18–19:** chip architecture/dual WLAN RF function and shared resources.
- **pp42–46:** WLAN PHY, RF path, calibration and link between MAC/PHY init and radios.
- **pp47, 62–63:** WLAN Cortex-M3 firmware and DHD host/device protocol; not enough to have file present or driver loaded.
- **pp64–70:** shared PMU reset state, 38.4MHz XTAL/reference, 32kHz LPO; avoid fabricating new reset sequences on working 2.4GHz path.
- **pp79–84:** RF/PA control and supply pins / variant board wiring; validate real board identity rather than copying third-party NVRAM.
- **pp106–115:** specifically **5GHz RF receiver pp110–111** and **5GHz transmitter p114**; demonstrates silicon architecture anticipates 5GHz, but capability bands are still firmware/board/regulatory dependent.
- **p132–134:** shared WL_REG_ON/BT_REG_ON and resets; a scan failure is not automatically an entire-chip POR problem.

Historical OEM firmware comparison [v039](V039_ORIGINAL_MZ600_FW_PHYSICAL_2026-10-24.md): original HRI39 January 2011 Motorola image **261317 B**, SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`, `4.218.248.20`; LibreELEC generic current **253748 B**, SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, firmware `4.220.48`. Earlier v039 OEM image test was on a different **pre-working F2** diagnostic version and failed F2 (-62); do not extrapolate that outcome to current successful p8 `wlan0` nor blindly replace current working kernel firmware. Both image streams and associated NVRAM are held PRIVATE and source-controlled for comparison.

## Most actionable root-cause discriminator: actual Linux7 `brcmfmac` band-list logic

Directly inspected pinned Linux kernel **`xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`**:

`drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c` around lines **7725–7770**, `brcmf_setup_wiphy()`, calls `brcmf_fil_cmd_data_get(ifp, BRCMF_C_GET_BANDLIST, &bandlist, sizeof(bandlist))`, then creates `NL80211_BAND_2GHZ` or `NL80211_BAND_5GHZ` only for corresponding **firmware-reported WLC_BAND_2G/WLC_BAND_5G** identifiers. Later `brcmf_setup_wiphybands()` obtains `chanspecs` firmware iovar, and `brcmf_construct_chaninfo()` enables channels that firmware supplies. `wiphy_read_of_freq_limits()` occurs after band construction.

**Thus leading hypothesis:** firmware itself reports 2G-only bandlist, rather than signed regdb filtering existing 5GHz channels. But absent actual raw `BRCMF_C_GET_BANDLIST` values and `chanspecs` readback, this remains a hypothesis; device-tree-frequency-limits should still be audited. **Never force 5GHz bands/channels into `wiphy` to defeat the firmware's answer.**

A valuable initial **kernel diagnostic patch**, only after clean source review, would log *only* raw band count/enum and sanitized 2G/5G chanspec counts at first initialization, alongside effective country/iovar status; no RF activation, unsupported channel enable, MAC/credentials or regulatory override. The diagnostic should be narrow, reversible, compile/patch-checkable, and independent of shared-chip provider changes. Alternative direct firmware interrogation via a validated private kernel diagnostic is acceptable. A/B the OEM 5GHz-supported Android firmware+NVRAM and present generic firmware+calibration in an **isolated RAM-only** test, not on the known-good persistent p7 image or live eMMC root.

## Patch-series implications and test order

1. Preserve 2.4GHz scan physical PASS and safe teardown as a regression baseline. Document **5GHz not exposed in current firmware+NVRAM+kernel** separately from whole-chip provider compile-only state.
2. Offline compare **factory Motorola** Wi-Fi firmware+board NVRAM 5GHz calibration, `aa5g`, country/regrev, boardflags and chipset revision against **actual installed** generic files, excluding any device-unique MAC/calibration keys from public outputs. Assert exact hashes.
3. Instrument `BRCMF_C_GET_BANDLIST` and `chanspecs` response without enabling unauthorized channels. Inspect DT `ieee80211-freq-limit` and rfkill/regulatory if bandlist shows 5G but wiphy omits it. Verify firmware’s country path before 5GHz scan.
4. Select **one** likely causal change for a **guarded RAM-only** A/B, preserving USB COM9 and WCC-first cleanup. If patch is a kernel bug, add a minimal firmware-consistent driver patch. If root cause is firmware/NVRAM provenance, keep it device-specific and separate from reusable shared-resource provider.
5. Repeat on at least MZ600 and independent MZ602/MZ604 variants with their own factory regulatory/calibration profile before community review; **no upstream submission yet**.

**Acceptance now:** 5 GHz PHY absent and scan intentionally skipped; two safe unloads/reloads, D-Bus/USB intact. Verified 5GHz support in owner-reported Android baseline, NVRAM aa5g/5GHz calibration present, but actual firmware band-list response still unknown. **No claim 5GHz Linux fixed or kernel patch physically qualified.**
