# MZ600 Linux 7 v06.4 — original Motorola HRI39 firmware advertises 5GHz, legacy ioctl 217 enumerates channels (physical)

**Date:** 2026-10-26. **Scope:** single experimental MZ600, permanent Debian p8, Linux `7.0.0-next-20260422+`; original full-chip Linux7 patch series remains separate and unsubmitted.

## Previous country A/B and identity boundary

- Instrumented normal generic `4.220.48` firmware with current 1550B calibration: effective **US rev0**, one **2.4GHz** band, 11 2.4GHz chanspecs, zero 5GHz. Exact US/69 bootstrap calibration 1569B: effective **US rev69 accepted**, **STILL only 2.4GHz**. Both tests cleaned and independent COM9 verified files/DBus/modules; [readback proof](MZ600_V064_BCM4329_COUNTRY_IOVAR_EFFECTIVE_US0_VS_US69_BANDS_STILL_2G_PHYSICAL_2026-10-26.md).
- Original Motorola HRI39 and HRI66 firmware **4.218.248.20** 261317B SHA256 **`7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`** recovered from private original Pi images, transmitted securely by existing authenticated Surface SSH/SCP, then COM9 gzip and SHA-verification into **Xoom RAM only**, `/run/mz600-hri39-original-fw-only-20261026.bin`. Proprietary bytes not published to GitHub. Reconstructed matching OEM NVRAM minus old bootstrap MAC, 1569B SHA `6de236d4d097f4996e1fef31d538757bfd9f4024cbcf2ade8bbaa97c040e53c4` (country US/rev69). Modern pinned `brcmfmac/firmware.c` uses `eth_platform_get_mac_address` to replace embedded bootstrap MAC with actual per-device FDT MAC, not a shared OEM MAC.

## Experiment 1 — REAL OEM firmware bandlist: first 5GHz confirmation

[One-shot original HRI39 matched firmware+NVRAM RAM-overlay](../../scripts/host/xoom/test-v064-original-motorola-hri39-wifi-firmware-ram-ab-20261026.sh), SHA256 **`63fa6ab641d46de7c6e92f5762fbd8ff71d5dfb6336c11d4daaa53bf08f02b21`**, complete physical root COM9 test. Both `/lib/firmware/brcm/brcmfmac4329-sdio.bin` and `.txt` **temporarily bind-overlaid from /run**, no installed file write. Dynamic `phy7`; loaded original firmware signature:

```text
Firmware: BCM4329/3 wl0: Jan 12 2011 13:48:56 version 4.218.248.20
MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
MZ600_5G_DIAG_WIPHY has2g=1 has5g=1
MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=5553 ccode=5553 rev=69
brcmf_construct_chaninfo: get chanspecs error (-52)
brcmf_setup_wiphybands: brcmf_construct_chaninfo failed (-52)
brcmf_cfg80211_attach: Setting wiphy bands failed (-52)
brcmf_bus_started: failed: -12
brcmf_sdio_firmware_callback: brcmf_attach failed
```

**Important distinction:** firmware effectively supports 5GHz and returns both real band identifiers. But modern Linux **assumes firmware accepts newer `chanspecs` iovar** and fails to register `wlan0` because this old version rejects it, with kernel `-EBADE=-52`. The 5GHz hardware was previously confirmed by owner Android successful associations. No 5GHz scan possible yet.

## Experiment 2 — READ-ONLY legacy channel enumeration, no channel activation

Historical [Motorola/Froyo Broadcom `wl_iw.c`](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/b4ace791eb574f589c53be582ea0d14e1a85ff09/bcm4329/src/wl/sys/wl_iw.c) uses `WLC_GET_VALID_CHANNELS` **command 217**, a `wl_uint32_list_t`, and **sets count to buffer capacity before querying**. Verified in the pinned Linux7 source `fwil.h` macro `BRCMF_C_GET_VALID_CHANNELS =217`. This is not a fabricated list.

Built [legacy channel read-only probe](../../scripts/experiments/build-v064-bcm4329-legacy-valid-channels-probe-20261026.py) via existing exact kernel MODVERSIONS tree; new diagnostic `.ko` 342560B SHA **`cd136e797e2a20ac58334708f218dcae672ec69cd2979eb897a033f806684ba2`**; combined lab patch SHA **`543380a3fea6c7a7ca5fb1eefa6c4ab24b7c9434cbe46c43a861acd57ef6af8a`**; old source+both baseline module binaries restored exactly after build. Signed/authenticated `devdesktop` SCP to Surface, then independently checked RAM-only COM9 transfer to Xoom. No radio was loaded during transfer.

Ran [read-only original FW with legacy query test](../../scripts/host/xoom/test-v064-original-motorola-hri39-legacy-valid-channel-probe-20261026.sh), SHA256 **`ef6d1619faa0589b13e90b61774b3af49ec8d2a47f6622b6acce5015c0b88b13`**, again with original HRI39 4.218.248.20 + OEM US69-calibration-minus-bootstrap-MAC loaded via temporary RAM file overlays, no flash/reboot/scan or per-device identity overrides. Dynamic `phy8`. **Actual firmware response**:

```text
MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
MZ600_5G_DIAG_WIPHY has2g=1 has5g=1
MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=5553 ccode=5553 rev=69
MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=20 2g=11 5g=9 other=0 max=383
MZ600_HRI39_LEGACY_WLAN0_NOT_CREATED
```

**Physical result:** original OEM firmware truly returns **twenty** valid channel numbers via its supported legacy ioctl: **eleven 2.4GHz, nine 5GHz**. We now have a documented way to construct wiphy channel inventory **from firmware-supported channel numbers**, not by forcing a static 5GHz whitelist. The test **deliberately kept original `chanspecs` error and did not enable any channels**: no wlan0 expected.

### Exit and rollback status

Both OEM experiments: WCC `modprobe` returned 0 but cfg80211 registration failed, `wlan0` absent. Each test had WCC→brcmfmac→brcmutil `modprobe -r` rc=0, both OEM calibration and firmware RAM overlays `umount` rc=0, script checked original firmware `.bin`, calibration `.txt`, and original installed brcmfmac `.ko` exact SHA, no `wlan0` or Broadcom modules. `HOST_DIAG_RESULT=FULL_PHYSICAL_PASS` means the **bounded diagnostic and rollback**, **not that Wi-Fi association or scanning succeeded**. COM9 continued working and no reboot was issued. If future physical post-test independent audit is done, record it separately; never invent one.

## Safe next patch principles

1. Proposed distinct Linux7 **legacy-brcmfmac channel-enumeration compatibility patch** for BCM4329 with firmware that rejects `chanspecs` but supplies `WLC_GET_VALID_CHANNELS`. MUST scope to affected chip/firmware; retain standard modern logic for other devices. If channel query fails, retain error.
2. Build channel inventory only from actual firmware-provided channel numbers and kernel's predefined band channel tables. Do **not** override globally disabled/unsupported channels or signed regulatory domain.
3. Old firmware lacks modern per-channel radar/passive flags. **Conservatively set `IEEE80211_CHAN_NO_IR` for every fallback-listed channel**, disable HT40/80/160 per-channel and apply radar restrictions for known DFS ranges; subject all channels to Linux cfg80211 regulatory restrictions. This enables only passive discovery, not transmission. These are requirements for any experimental fallback, not yet a tested patch.
4. Verify actual on-device channel enumeration, factory MAC, regulatory world/domain, and only THEN attempt a bounded passive scan on legal 5GHz channels such as 36/40/44/48 if firmware supplies them; no association. Regression retest generic 4.220.48 2GHz scan and module unload; retain rollback.
5. Long-term full-chip shared U4/I7/U0/U2/LPO provider, Motorola six-field SDIO quirk and OEM PMU policy are **separate tracks** and all require multi-unit MZ600/MZ602/MZ604 qualification prior to upstream review.

**Classification:** OEM firmware real 5GHz band+9 valid channels PHYSICAL PASS; modern brcmfmac legacy API compatibility root cause isolated; wlan0/5GHz passive scan still PENDING; no permanent software or kernel change.
