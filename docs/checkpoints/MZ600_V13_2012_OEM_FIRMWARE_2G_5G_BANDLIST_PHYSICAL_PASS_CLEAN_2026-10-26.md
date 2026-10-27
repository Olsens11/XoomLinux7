# MZ600 V13 May-2012 OEM BCM4329 firmware-only A/B: dual-band 2G+5G PHYSICAL PASS, clean rollback

**Date:** 2026-10-26. **Evidence:** actual Surface owner-executed one-shot COM9 serial transcript and JSON receipt; completed physical no-scan check on installed Xoom MZ600 Debian 12.15, kernel `7.0.0-next-20260422+`. This note supersedes V13 **staged only** state documented in [offline staging checkpoint](MZ600_V13_2012_OEM_ESCAN_CANDIDATE_OFFLINE_AND_SURFACE_STAGE_2026-10-26.md).

## Result: yes, newer OEM firmware exposes both bands on same hardware

The 264140-byte, hash-pinned **BCM4329 B1 Motorola-related May 25 2012 firmware `4.218.248.44`**, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, was RAM-only bind-overlaid over the baseline Debian firmware during a single read-only-bandlist test. The installed 1550-byte calibration/NVRAM was left untouched. Existing original factory MAC/FDT path was not changed. Previously qualified ABI-matched 343200-byte passive-only-wiphy diagnostic module was loaded in RAM (`ff19d91726f406468d6cc9516d43a851f6a7a22d403259094ae376041671db29`), then original broadcom WCC loader.

### Actual fresh live diagnostic markers

```text
MZ600_V13_PREFLIGHT_START
MZ600_V13_FIRMWARE_AND_MODULE_VERIFIED_NVRAM_UNCHANGED
MZ600_V13_TEMP_2012_FIRMWARE_OVERLAY_PASS
MZ600_V13_WCC_LOAD_RC=0
MZ600_V13_WLAN0_PRESENT
MZ600_V13_PHY_2G=14 PHY_5G_TOTAL=29 PHY_5G_NO_IR=24 PHY_5G_DISABLED=5
MZ600_V13_FIRMWARE_BAND_DIAGNOSTICS_BEGIN
MZ600_V13_DMESG_LINES_BEFORE=633
[56391.314787] brcmfmac: brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: May 25 2012 17:56:21 version 4.218.248.44
[56391.336714] brcmfmac: brcmf_setup_wiphy: MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
[56391.346592] brcmfmac: brcmf_setup_wiphy: MZ600_5G_DIAG_WIPHY has2g=1 has5g=1
[56391.367295] ieee80211 phy20: brcmf_construct_chaninfo: get chanspecs error (-52)
[56391.371652] brcmfmac: brcmf_construct_chaninfo: MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=35 2g=11 5g=24 other=0 max=383
[56391.374786] brcmfmac: brcmf_construct_chaninfo: MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK chip=4329 fw2g=11 fw5g=24 no_ir=1 ht20_only=1
MZ600_V13_FIRMWARE_BAND_DIAGNOSTICS_END
MZ600_V13_NO_SCAN_NO_LINK_UP_NO_ASSOCIATION
```

Important count distinction: **firmware** reported 35 valid channels total (11 2G + 24 5G) via older channel-list fallback. **Linux wiphy** had 14 2G entries registered and 29 5G entries (24 tagged NO_IR and 5 disabled); wiphy entries are a fixed/processed kernel view and not equal to firmware-supported band counts. Do not report 14 2G channels as firmware permitted. `BANDLIST count=2 first=1 second=2` means firmware advertises 5G and 2G; `WIPHY has2g=1 has5g=1` corroborates both bands.

### Cleanup (root script and independent verification)

```text
MZ600_V13_CLEANUP_START rc=0 state=OBSERVATION_COMPLETE
MZ600_V13_LINK_DOWN_RC=0
MZ600_V13_UNLOAD_brcmfmac-wcc=0
MZ600_V13_UNLOAD_brcmfmac=0
MZ600_V13_UNLOAD_brcmutil=0
MZ600_V13_UMOUNT_FIRMWARE_RC=0
MZ600_V13_ORIGINAL_FILES_AND_RADIO_RESTORED
MZ600_V13_NO_SCAN_A_B_COMPLETED_AND_CLEAN
__MZ600_V13_OWNER___TEST_RC_0__
```

Surface JSON:
```json
{
  "firmware_candidate": "4.218.248.44",
  "root_bash_rc": 0,
  "independent_poststate_ok": true,
  "script_cleanup_ok": true,
  "permanent_install": false,
  "scan_requested": false
}
```

The independent post-run host-side COM9 check verified original installed generic firmware SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, installed calibration SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`, installed module SHA256 `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`, no firmware/calibration bind mounts, no wlan0, and no loaded broadcom/BT modules. **No changes to disk, boot partition, regulatory DB, MAC identity, firmware files, or kernel.**

Private complete receipt on Surface only:
- `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V13-2012-FW-STAGED-20261026\mz600-v13-owner-COM9-private.txt`
- `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V13-2012-FW-STAGED-20261026\mz600-v13-owner-receipt.json`

Do not copy the full potentially private serial transcript to public Git. No derived SSID/BSSID/MAC exposed in this checkpoint.

## Interpretation: firmware path now makes a simpler completion solution plausible

The known older (original HRI39 4.218.248.20) firmware supports 5GHz but rejects ESCAN `-52` and working 5GHz legacy ioctl50/51 scan only finishes at ~10s timeout without Event26. The installed generic (4.220.48) firmware does normal modern escan with 2.4G 19-BSS but enumerates 2G only, even after OEM country/regrev bootstrap. The newly verified later OEM **4.218.248.44** firmware presents **both bands on the same Xoom** and contains `escan` in its compiled binary. This removes the previously blocking *lack of 5GHz band availability in newer firmware*, but **does not yet prove ESCAN works**, that Event69 terminal SUCCESS is generated, or that any network is received on 5G. The `chanspecs` iovar still fails `-52`, and older channel fallback remains necessary.

## Exact next gate

**Do NOT replay the consumed V13 one-shot.** First source-review modern Linux7 brcmfmac ESCAN request format vs May2012 firmware, event69 subscription and RX routing, and current driver fallback's NO_IR behavior. Then create a **new** unique SHA-pinned RAM-only owner-operated *single-channel* 5180MHz channel36 **passive-only** test, with strict no-probe/no association, effective firmware 5G band and channel readback, full bounded timeout, and independent cleanup. Capture whether `brcmf_run_escan` returns 0 versus -52, whether event69 terminal SUCCESS arrives, `iw` exit and elapsed time, and only count/safe BSS structures. Maintain all original files, NVRAM, module ABI, BCDC, BT, dynamic factory MAC and 2G baseline. If Event69 success, prefer standard modern escan over new HRI39 iscan worker; keep original HRI39 legacy/iscan as controlled fallback.

Project sources: [preflight and code staging](MZ600_V13_2012_OEM_ESCAN_CANDIDATE_OFFLINE_AND_SURFACE_STAGE_2026-10-26.md), [earlier firmware comparison](../research/MZ600_BCM4329_2012_DUALBAND_ESCAN_FIRMWARE_CANDIDATE_PRIORITY_2026-10-26.md).
