# MZ600 v06.4 — OEM US/69 NVRAM bootstrap A/B on installed Debian: firmware still reports 2G only (OWNER PHYSICAL)

**Date:** 2026-10-26. **Evidence class:** owner-pasted actual COM9 root console transcript; experiment executed physically on experimental replacement Motorola Xoom MZ600, Linux `7.0.0-next-20260422+`, Debian 12.15 on internal p8 ext4. **No subsequent independent shell audit is claimed** beyond the script's output/cleanup verification. The owner ran the prepared one-shot exactly once.

## Hypothesis and strictly controlled variable

The original Motorola HRI39/HRI66 calibration is 1,595 bytes; current identity-preserving Debian reference calibration is 1,550 bytes, byte-for-byte original **without three fields**: OEM bootstrap `macaddr`, country `ccode=US` and regulatory revision `regrev=69`. The previous firmware-enumeration diagnostic using current generic firmware version **4.220.48** physically reported `BRCMF_C_GET_BANDLIST count=1 first=2 second=0` and `chanspecs total=11 2g=11 5g=0 other=0`; `wlan0` appeared but 5 GHz channel list was absent. Owner confirmed historical 5 GHz connections on the same physical hardware in Android.

The **single tested difference** here: reconstruct the exact original Motorola calibration **minus only its OEM bootstrap MAC**, SHA256 `6de236d4d097f4996e1fef31d538757bfd9f4024cbcf2ade8bbaa97c040e53c4`, **1,569 bytes**; temporarily bind-mount this RAM file over `/lib/firmware/brcm/brcmfmac4329-sdio.txt` **before driver/firmware initialization**, then read firmware-band diagnostics. The script did **not** change the active `.bin` firmware, OEM/factory MAC handling, MMC/pwrseq, PMU, kernel, installed modules, the global Linux country via `iw reg set`, or boot partition. No Wi-Fi scan, association, DHCP, channel enabling or reboot.

### Owner's COM9 console — actual execution receipts

Preflight and A/B initialization markers:

```text
MZ600_US69_PREFLIGHT_BEGIN
MZ600_US69_BASELINE_VALIDATED
MZ600_US69_OEM_VARIANT_EXACT_HASH_MATCH
MZ600_US69_MOTOROLA_COUNTRY_AND_REV_ACTIVE_AT_FW_BOOTSTRAP
MZ600_US69_BRCMUTIL_LOADED
MZ600_US69_READONLY_DIAGNOSTIC_BRCMFMAC_LOADED
MZ600_US69_WCC_LOADED
MZ600_US69_WLAN0_PRESENT
MZ600_US69_WIPHY_ID=4
MZ600_US69_PHY_5GHZ_FREQ_COUNT=0
MZ600_US69_DIAGNOSTIC_RECORDS_BEFORE=1 AFTER=2
MZ600_US69_NEW_FIRMWARE_BAND_DIAGNOSTICS_BEGIN
[21854.637947] brcmfmac: brcmf_setup_wiphy: MZ600_5G_DIAG_BANDLIST count=1 first=2 second=0
[21854.647159] brcmfmac: brcmf_setup_wiphy: MZ600_5G_DIAG_WIPHY has2g=1 has5g=0
[21854.672970] brcmfmac: brcmf_construct_chaninfo: MZ600_5G_DIAG_CHANSPECS total=11 2g=11 5g=0 other=0
MZ600_US69_NEW_FIRMWARE_BAND_DIAGNOSTICS_END
```

The **control condition** before this overlay test had **identical** band/chanspec response (`count=1 first=2`, `total=11 2g=11 5g=0`). Hence OEM country and revision lines **alone did not make the running generic firmware expose 5 GHz**, even when the NVRAM file was substituted *before* loading the radio modules.

**Important evidence limit:** The log verifies an exact-hash replacement calibration file was visible at firmware bootstrap and that firmware still reported only 2 GHz. It **does not independently read back the on-chip firmware's *effective* country code/regulatory revision**. The firmware could accept, translate, ignore, or override the country/regrev settings; all remain open until a compatible read-only firmware iovar investigation. Do not claim a verified internal firmware `US/69` effective state merely from successful file overlay.

### Cleanup and restore — script-verified physical PASS

```text
MZ600_US69_CLEANUP_BEGIN prior_rc=0 state=OBSERVATION_COMPLETE
MZ600_US69_LINK_DOWN_RC=0
MZ600_US69_UNLOAD_brcmfmac-wcc_RC=0
MZ600_US69_UNLOAD_brcmfmac_RC=0
MZ600_US69_UNLOAD_brcmutil_RC=0
MZ600_US69_UNMOUNT_RC=0
MZ600_US69_ORIGINAL_FILES_AND_DRIVER_STATE_VERIFIED
MZ600_US69_FIRMWARE_BAND_A_B_CAPTURED_AND_RESTORED
MZ600_US69_END
```

The successful script postcheck required original calibration SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`, original generic firmware SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, original installed brcmfmac module SHA256 `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`, overlay unmounted, `wlan0` absent, all three Broadcom modules absent. Each module unload and unmount returned 0. These are **the provided script's checks**; an independently initiated post-test COM9 readback is not yet recorded. The original physical p7 full hash was verified in earlier checkpoint; this experiment included no boot write, but do not invent a new post-test p7 hash.

Visible Windows COM9 echo had interspersed long-line/wrap fragments during paste, but the **actual execution** emitted all preflight SHA-validation receipts, full diagnostic capture, zero exit cleanup, and verified restore; no reason from available evidence to label the attempted script corrupted.

## What the negative A/B establishes and does not establish

- **Physical PASS:** exact original-without-MAC OEM calibration 1,569B was installed as a *temporary RAM-backed NVRAM overlay at firmware load*, `wlan0` initialized, PHY showed zero 5 GHz frequency entries, and kernel diagnostics again reported **only 2.4 GHz** with eleven 2 GHz chanspecs.
- **Standalone hypothesis falsified:** simply restoring `ccode=US` and `regrev=69` to the current generic firmware's boot NVRAM does **not** recover 5 GHz in the tested state. Do not repeat identical A/B without changed firmware or diagnostics.
- **Still open:** whether generic firmware truly adopts those exact regulatory settings; whether original Motorola 4.218.248.20 paired with its calibrated NVRAM initializes both bands; generic-versus-OEM firmware revisions/boardflags/OTP and chipcommon/PMU behavior; differences in Motorola's six-field SDIO quirk and shared-chip power timing; interactions that manifest only at other cold/warm reset states.
- **Safety:** do not force wiphy 5GHz channels, adopt unchecked universal `US/69` overrides, write a permanent NVRAM/firmware swap, assume the OEM bootstrap MAC can be put on all tablets, or conflate this A/B with full-chip pwrseq qualification.

## Next one-variable investigation

1. Read-only inspect **effective firmware regulatory country/revision** via carefully vetted `brcmfmac` firmware iovar query in another ABI-exact count/status-only RAM diagnostic. A missing readback is not proof of a country cause.
2. Compare *matching-generation* HRI39 **firmware 4.218.248.20** + stock matching calibration against modern generic `4.220.48`, preserving board-specific RF calibration and dynamic factory identity. **Firmware binaries differ** even though current RF calibration apart from the three fields is identical.
3. Design bounded **firmware-only** or **validated firmware/calibration pair** RAM-load experiment only after checking compatibility, image provenance, driver protocol and rollback. If appropriate, keep country/revision candidate controlled separately from firmware variable.
4. Continue the independent full-chip typed WLAN/BT power-owner patch series and Motorola six-field SDIO workaround evaluation; **neither is demonstrated as the present 5 GHz cause**. Require later physical multi-device qualification before upstream consideration.

**Final status:** OWNER PHYSICAL NEGATIVE 5GHZ A/B + VERIFIED SCRIPT CLEANUP; no 5GHz fix, no new 5GHz scan, unchanged installed Debian baseline.
