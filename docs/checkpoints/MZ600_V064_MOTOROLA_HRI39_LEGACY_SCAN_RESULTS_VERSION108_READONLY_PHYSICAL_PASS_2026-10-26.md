# MZ600 OEM BCM4329 firmware confirms scan-results version 108 (physical)

**2026-10-26; exact installed Linux 7.0.0-next-20260422+, experimental MZ600, Debian 12.15 p8, root COM9.** One read-only firmware GET ioctl; **no Wi-Fi scan, active probing, association, boot flash or reboot**.

## Original problem and protocol prediction

Motorola original HRI39/HRI66 BCM4329 firmware 4.218.248.20, 261317 bytes, original SHA256 **7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a**, plus original US/69 NVRAM without OEM bootstrap MAC, physically returned dual-band and 20 valid channels (11 x 2GHz, 9 x 5GHz) via legacy ioctl 217. Lab v05 exposed wlan0 and nine 5GHz NO_IR channels but old firmware rejected modern escan with -EBADE (-52).

The published [Broadcom Froyo BCM4329 protocol header](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/include/wlioctl.h) declares BSS version **108**; modern Linux7 driver hardcodes **109**. The version actually returned by Motorola firmware was not previously measured.

## Reproducible lab diagnostic and guarded physical test

[New v6b ABI-exact builder](../../scripts/experiments/build-v064-bcm4329-read-only-legacy-results-header-20261026.py) uses the same offline reproducible v05 fallback and adds a single firmware **BRCMF_C_SCAN_RESULTS = 51 GET** after successful channel enumeration. It initializes the reply buffer size and logs only return code, length, version and count; **does not send WLC_SCAN, request a scan, parse or print SSIDs/BSSIDs**. A first offline compile failed on an implicit u8-pointer assignment, source/build module hashes were restored, cast was fixed and a fresh v6b one-shot build passed.

- Exact ARMv7 MODVERSIONS lab brcmfmac module: **343,552 bytes**, SHA256 **8a60a84cd4edcee10a1d81c42258d1ffa68bde60f7f4723a18a0ade14ce83ceb**.
- Combined diagnostic source diff SHA256 **098f1442c49ebb58a330650ff4b5671b8e89ff874672e8315b3f091ea7af12e3**.
- Existing original installed brcmfmac ABI module SHA256 **9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb** remains unchanged.
- Module transferred Desktop WSL to Surface through existing authenticated devdesktop SSH/SCP, then via framed COM9 gzip+base64 to Xoom **/run/mz600-v064-readonly-scanheader-v6b-once.ko** with tablet-independent size/SHA verification. No new firewall rule or permanent install.
- [Guarded one-shot firmware+calibration RAM test](../../scripts/host/xoom/test-v064-hri39-readonly-legacy-scan-results-header-20261026.sh) SHA256 **da28b556323ccb198b2683dbae7c1807743530a924f583fca03a036d520517a9**, validated Bash syntax and exact one-shot host wrapper.
- Stock OEM HRI39 firmware and matching OEM NVRAM minus old bootstrap MAC **1569 bytes** SHA256 **6de236d4d097f4996e1fef31d538757bfd9f4024cbcf2ade8bbaa97c040e53c4** were bind-overlaid from RAM only before driver initialization, preserving the device's own FDT factory MAC.

### Actual physical firmware output

    MZ600_HRI39_SCANHEADER_BASELINE_SHA_PASS
    MZ600_HRI39_SCANHEADER_CALIBRATION_RECONSTRUCTION_SHA_PASS
    MZ600_HRI39_SCANHEADER_WCC_LOAD_RC=0
    MZ600_HRI39_SCANHEADER_WLAN0_PRESENT
    MZ600_HRI39_SCANHEADER_DYNAMIC_PHY=12
    MZ600_5G_DIAG_BANDLIST count=2 first=1 second=2
    MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=5553 ccode=5553 rev=69
    MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=-52 legacy_rc=0 total=20 2g=11 5g=9 other=0 max=383
    MZ600_5G_DIAG_SCAN_RESULTS_HEADER rc=0 buflen=12 version=108 count=0

**Conclusive result:** the physical HRI39 firmware accepts legacy scan-results ioctl 51 and independently reports an empty **12-byte header with BSS wire-version 108**. Count=0 because NO SCAN was started. This **does NOT** validate a populated BSS record structure, IE offsets, channel-result content, normal scan-completion event or passive scanning.

The test also printed PHY_5GHZ_FREQ_COUNT=29 via iw phy enumeration, but this number **includes DISABLED frequencies**. It is not evidence of 29 usable channels. The actual firmware-supported 5GHz set remains nine channel numbers from ioctl 217.

### Script cleanup and independent COM9 verification

All guarded cleanup steps returned **RC=0**: link down, unload brcmfmac-wcc -> brcmfmac -> brcmutil, unmount temporary calibration and original firmware overlays; script printed original files/radio restored and FULL_PHYSICAL_PASS.

A separate later COM9 read-only audit independently confirmed running kernel and internal p8, only ip6tnl0/lo/sit0 interfaces, **no Broadcom modules**, no .bin or .txt bind overlays, exact original installed calibration SHA **a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb**, original generic firmware SHA **d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93**, original installed .ko SHA above, and both D-Bus socket and service active. No reboot or p7 writes; the p7 raw hash was not re-read.

## Upstream-quality next work

1. Treat 108 as **physically confirmed on-chip**, not a guess. A [September 25, 2026 upstream proposal](https://lists.openwall.net/linux-kernel/2026/09/25/1158) separately broadens modern 109 to 109–112; status not confirmed merged. Do NOT globally substitute 108 for 109. Version-specific result parsing must validate full BSS record and IE bounds based on an actual **populated** response.
2. Separate logical change per patch, bisectable. Existing channel fallback remains lab-only, no scan implemented. A complete legacy WLC_SCAN(50) + WLC_SCAN_RESULTS(51) passive-only lifecycle needs cfg80211 request ownership, bounded wait/completion, cancellation and teardown; NO_IR and regulatory enforcement must be preserved. **Do not mark a real legacy scan passed.**
3. Existing [22-case synthetic host safety model](../../tools/forensics/test_bcm4329_legacy_scan_contract.py) covers result envelope and exactly-once request completion, but it is NOT KUnit, NOT an in-kernel parser, and not full BSS/IE layout validation.
4. Keep [legacy scan protocol and logical-patch plan](../research/MZ600_BCM4329_LEGACY_SCAN_UPSTREAM_PROTOCOL_IMPLEMENTATION_2026-10-26.md) distinct from the shared BCM4329 WLAN+BT power and Motorola SDIO quirk patch series, with multi-Xoom acceptance and owner submission approval required.

**Status: firmware ioctl51 header v108 PHYSICAL PASS, safe restored baseline, no scan or installed change.**
