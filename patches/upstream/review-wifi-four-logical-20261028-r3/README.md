# BCM4329 Wi-Fi four-member review candidate, r3 — 2026-10-28

**UNSIGNED, UNSUBMITTED, SOURCE-ONLY.** One logical issue per patch; issue count does not imply patch count. This four-member r3 series replaces r2 for a future test and is NOT applied on top of r2. Original baseline: xoom-linux/linux commit 2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3. Historical r1/r2 and installed exact nine-review remain unchanged.

## New physical evidence motivating this revision

The May 2012 Motorola OEM BCM4329 firmware returned two valid frequency bands and a legacy 35-channel list, but **all 35** per_chan_info calls in WIFI-01 r2 failed. The zero returned radar/passive counters mean metadata was unavailable, not that no channels are restricted. The lab test stopped before any scan and restored all original radio/network components. [Exact checkpoint](../../docs/checkpoints/MZ600_WIFI01_R2_OEM2012_PHYSICAL_PERCHAN_UNSUPPORTED_R3_CANDIDATE_2026-10-28.md).

## Scope of amendments

**WIFI-01 only**: Keep optional per-channel firmware radar/passive flag import if supported; where it fails, retain existing restrictions and conservatively set NO_IR for 5GHz channels instead of assuming unrestricted operation. Cache recognized unsupported errno (-EOPNOTSUPP or -EBADE) to avoid repeated rejected IOCTLs. Still respects valid-channel bounds and HT20 limits; never forces country, increases power, clears NO_IR or enables new channels. A better firmware ABI answer may require a future revision within this patch. This is a candidate defensive policy, not final proof of regulatory compliance.

**WIFI-02, WIFI-03, WIFI-04**: Stable patch IDs identical to r2; same scan-generation, Event69 owner and conditional firmware-UP logical changes. No fifth fixup patch.

## Mandatory historical reuse gate: v05 worked, V28 retired the blanket workaround

The original [Oct26 v05 HRI39 passive-only fallback](../../docs/checkpoints/MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md) and [V13 May2012 firmware physical proof](../../docs/checkpoints/MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md) already used broad NO_IR as a **conservative diagnostic policy**, which exposed 5GHz channels without initiating radiation. But [V28 native cfg80211 scanning](../../docs/checkpoints/MZ600_V28_NATIVE_CFG80211_SCAN_AFTER_LAB_GATES_REMOVED_2026-10-27.md) **deliberately removed blanket lab-only NO_IR and single-channel/passive admission gates** to restore ordinary scan behavior; Linux beacon hints legitimately change NO_IR on non-radar 5GHz channels. Therefore the present r3 proposal must NOT be treated as automatically restoring production regulatory correctness: it uses NO_IR on 5GHz **only if firmware metadata is unavailable**, does not impose the old single-channel/scan-policy restrictions, and remains a SOURCE-ONLY, potentially limiting experiment until effective regdb/country behavior and passive/normal scan are tested. More foundational chronology in [2026-10-28 physical/history checkpoint](../../docs/checkpoints/MZ600_WIFI01_R2_OEM_2012_PERCHAN_PHYSICAL_AND_HISTORY_2026-10-28.md). An exact iovar error readout is needed to rule out a host argument-format problem, which could remove the need for broad NO_IR entirely.

## Offline tests completed

- Four source commits on isolated branch review/wifi01-unsupported-perchan-20261028. WIFI-01 commit 6f3efe860, tip 8c874fd38. Four exported mail patches listed in series.
- Each patch passed strict checkpatch without a human signoff (0 errors, 0 warnings, 0 checks), and git diff --check PASS.
- Linux ARM GNU toolchain 14.3.1 with matching exact-nine build config: olddefconfig PASS, prepare PASS, full brcmfmac directory-prefix build PASS.
- brcmfmac cfg80211.o SHA256 4d7bc9c6b35eb7d2c2ab25b7cb574c4a330b2b9469434bd857aa10a31020dc00 and aggregate brcmfmac.o SHA256 ef5a40f77fa81e274da3cfba0bd124d671af2126c4f453b509abe96ca727cf35.
- **Not yet performed:** full nine-member r3 integrated zImage/modules build, runtime verification of r3, exact legacy iovar errno, effective regulatory test, legal passive scan, sustained Wi-Fi+BT acceptance, source submission.

Do not treat compiler success as a physical acceptance result. The owner will personally sign when ready. Preserve protected boot partitions, p10 running Linux, COM9 and historical firmware archives.
