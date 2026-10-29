# BCM4329 5GHz firmware/regulatory causal-history reconciliation — 2026-10-28

## Why this checkpoint exists

Owner recalled an earlier regional/regulatory intervention at the time 5GHz began working. The newer Motorola firmware was expected to support **both 2.4 and 5GHz**. The 2026-10-28 exact-nine-review Linux/p10 presently advertises only 2.4GHz with installed generic firmware **4.220.48**, prompting issue [#1](https://github.com/Olsens11/XoomLinux7/issues/1). Rather than repeat the experiments, we read the **older Oct26–27 physical checkpoints** and reconstructed the controlled causal sequence below. All statements are **as of their experiment date**, not assertions that an older kernel or radio state still runs today.

**Most important corrected conclusion: the 2012 Motorola OEM firmware `4.218.248.44` already delivered a dual-band `BRCMF_C_GET_BANDLIST` response on the same MZ600 using the UNMODIFIED 1,550B current board NVRAM, and native Linux7 5GHz scans including actual terminal Event69 SUCCESS were subsequently proven.** Therefore dual-band radio is neither unproved nor categorically blocked by missing `ccode=US,regrev=69` in the current board file. The **specific installed generic `4.220.48` firmware** has separately been proven to advertise only 2GHz. Do not invent a 5GHz wiphy band by overriding the firmware response.

## Verified experimental sequence

| Dated test | Firmware, NVRAM condition | Critical *actual* physical evidence | Inference & limit |
| --- | --- | --- | --- |
| v064 baseline physical bandlist, Oct26 | Generic `4.220.48` (253748B), installed identity-safe 1550B NVRAM | `BANDLIST count=1 first=2 second=0`; `chanspecs total=11 2g=11 5g=0`; wiphy has2g1 has5g0 | **Raw firmware** 2G-only response—not just missing `iw` UI |
| v064 US/69 one-variable bootstrap A/B, Oct26 | **Same generic firmware**; temporary *before module initialization* calibrated 1569B NVRAM preserving original Motorola `ccode=US,regrev=69`, fixed OEM MAC excluded | `BANDLIST count=1 first=2 second=0`; 11 2G chanspecs; no 5G. Owner script cleanup PASS | **Adding US69 NVRAM lines alone did not fix generic firmware 5GHz.** The original US69 overlay script itself did not independently read back firmware country/rev, although the later HRI39 OEM firmware evidence records a separate country-iovar A/B readback of US0 versus US69 |
| v05 / v11 HRI39 OEM firmware, Oct26 | Motorola `4.218.248.20` plus its matching identity-safe original NVRAM | 2G+5G and 9 NO_IR 5G valid channels; v11 passive 5180MHz WLC_SCAN/RESULTS51 produced 4 standard cfg80211 BSS records | OEM 2011 pair dual-band working; modern `escan` unsupported (-52), legacy command/result required |
| **v13 May2012 firmware-only A/B, Oct26** | **Motorola `4.218.248.44`, 264140B**, private SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`; **installed 1550B NVRAM unchanged**, per-device FDT MAC intact | **`BANDLIST count=2 first=1 second=2`**; `wiphy has2g=1 has5g=1`; `chanspecs` -52; legacy 35 supported = **11 2G + 24 5G** | Dual band **firmware-only change proved** without US69 NVRAM overlay. No scan in v13. No permanent firmware swap |
| v14/v16, Oct26–27 | Same May2012 firmware, unchanged board NVRAM | 5G channel36 5180MHz ESCAN accepted; partial Event69 and BSS109 records; no terminal observed by handler, watchdog timed out | Initial failed scans, not proof firmware never sends terminal |
| **v17 Oct27** | Same May2012 firmware, 500ms 5G ch36 passive scan | **Real Event69 terminal status0**, normal `cfg80211_scan_done aborted=0`, **2 user BSS, 661ms** | First native successful 5G ESCAN completion. More event subscriptions *and* quiescent BT stack varied; cause not isolated |
| **v18 ten trials Oct27** | Same May2012 firmware; varying event masks | **All 10** generated timely raw incoming Event69 status0 at firmware event ingress; cfg80211 handler missed 8 | Firmware scan terminal exists; bottleneck in Linux host event routing/filter/ownership |
| v19 / v20 / v21 Oct27 | Same May2012 firmware | v19: real terminal enters worker but bsscfg1/ifp=NULL => -EINVAL; v20: headers **version2**, sometimes invalid bsscfg; v21 owner-map lab ON delivered real missing-interface terminal successfully twice | Host event-index handling is evidence-backed root-cause area, not a generic v1-header explanation |
| v25–v27 Oct27 | Same May2012 firmware; initial private scan gate insisted on NO_IR flag | v25: after a valid first scan/beacon, Linux reg beacon-hint processing could clear NO_IR, causing **lab-only second-scan -EPERM**; v26 removed only that obsolete private gate, then second real firmware request returned -52; v27 traced firmware code **-4=BCME_NOTUP** | Genuine regulatory behavior **interfered with the test gate**, while separate firmware readiness was not fixed |
| v22b / v23 / v24 Oct27 | Same May2012 firmware | Request sync ID is echoed in terminal payload; v24 generated ID/owner matching first scan PASSED | Firmware supports transaction ownership but cancellation/concurrency still open |
| **v28 Oct27** | Same May2012 firmware; normal native cfg80211 request, no temporary blanket NO_IR or one-channel gate | First *normal multichannel* `iw scan` **12 BSS / 2834ms**; second `iw scan` **-52** | Native scan broad support proven; repeat scan readiness remained broken. v27 decoded earlier second-scan firmware error as **BCME_NOTUP**. Drives WIFI-04 readiness review |

### Source checkpoint links (immutable historical records)

- [Generic 4.220.48 raw one-band proof](MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md)
- [US69 A/B negative owner physical](MZ600_V064_OEM_US69_BOOTSTRAP_NVRAM_A_B_PHY5GHZ_UNCHANGED_OWNER_PHYSICAL_2026-10-26.md)
- [Later firmware country iovar readback effective US rev0 vs US rev69, both still 2G](MZ600_V064_BCM4329_COUNTRY_IOVAR_EFFECTIVE_US0_VS_US69_BANDS_STILL_2G_PHYSICAL_2026-10-26.md)
- [May2012 firmware-only V13 dual-band success](MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md)
- [V17 Event69 terminal and cfg80211 BSS success](MZ600_V17_2012_5G_CH36_WIDE_EVENT_MONITOR_REAL_ESCAN_TERMINAL_SUCCESS_661MS_PHYSICAL_PASS_2026-10-27.md)
- [V18 all ten terminal events at ingress](MZ600_V18_PARAMETRIC_MASK_TEN_SCANS_FIRMWARE_TERMINAL_AT_INGRESS_NOT_HANDLER_2026-10-27.md)
- [V19 worker missing interface proof](MZ600_V19_EVENT69_WORKER_PRIMARY_IF_LOOKUP_FAIL_PHYSICAL_2026-10-27.md)
- [V20 header version2 physical evidence](MZ600_V20_EVENT_HEADER_V2_17_EVENTS_PHYSICAL_PASS_DMESG_ROLLOVER_RECOVERED_2026-10-27.md)
- [V21 real owner routing A/B](MZ600_V21_TERMINAL_OWNER_LAB_SWITCH_AB_PHYSICAL_PASS_2026-10-27.md)
- [V25–V27 regulatory beacon-hint gate and BCME_NOTUP readback](MZ600_V25_TO_V27_SECOND_SCAN_REGSTATE_AND_FIRMWARE_NOTUP_2026-10-27.md)
- [V24 generation/second scan open](MZ600_V24_GENERATION_CHECK_FIRST_SCAN_PASS_TWO_SCAN_GATE_OPEN_2026-10-27.md)
- [V28 native multichannel and repeat scan failure](MZ600_V28_NATIVE_CFG80211_SCAN_AFTER_LAB_GATES_REMOVED_2026-10-27.md)

## Current 2026-10-28 source/deployment relationship

- The replacement MZ600 currently runs the pinned exact nine-review Linux 7 temporary boot, with Debian/p10, 2.4GHz association/Internet, COM9, and **generic 4.220.48 firmware**. Both live firmware and live 1550B NVRAM SHA fingerprints were independently verified to match private staged copies on Oct28. This is NOT the May2012 firmware.
- [WIFI-01 r2](../../patches/upstream/review-wifi-four-logical-20261028-r2/README.md) is an **OFFLINE candidate** that adds `per_chan_info` for firmware radar/passive restrictions inside the existing one-logical-change fallback, without creating a fifth patch. Its exact-source ARM prefix build passed, but no hardware use of r2 or firmware-reported per-channel semantics is yet established.
- A lab-only **exact nine-review + WIFI-01 r2** source tree was independently built with read-only `BRCMF_C_GET_BANDLIST`, `chanspecs` and `per_chan_info` diagnostic printk; **full** ARM `zImage`, both DTBs, matched modules build returned rc0. Private source/build receipt: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-bcm4329-banddiag-r2-nine-build-20261028/`. This has **NOT been flashed, booted, installed or paired with alternate firmware on Xoom**. The old raw 4.220.48 bandlist question is **already conclusively answered** by v064 and does NOT warrant repeating an identical destructive diagnostic.
- The **May2012 firmware's full source-compatible per-channel `per_chan_info` response** is not yet established under WIFI-01 r2, even if string inspection suggests it. Legacy channel fallback still applies because May2012 returns `chanspecs=-52`.
- User expects dual-band; do not interpret the generic firmware's 2G-only response as an acceptable design limit. Better to use proven 2012 OEM firmware when legally and operationally appropriate rather than fabricate driver RF support.
- **Compatibility still to validate:** last tested v28 lab had second-scan -52 / earlier BCME_NOTUP; WIFI-04 attempts a normal conditional WLC_UP readiness correction. Exactly integrated nine+r2 with May2012 firmware, repeat scans, realistic regulatory flags, cancellation and multiple MZ600/MZ604 tests have NOT been physically proven. No human DCO or upstream filing permitted yet.

## Correct next experiment, not another generic-band diagnostic

1. **Source-only first:** inspect why May2012 firmware's `per_chan_info` might succeed or fail; compare r2 flags against baseline normal channel flags, regulatory country/NO_IR handling and v13/v28 proofs. Make diagnostics log bounded numeric return codes, not private RF identities.
2. Prepare one **new**, *owner-approved*, SHA-pinned **temporary-boot or RAM-only** test pairing the already-proven May2012 firmware with a **full ABI-matched** exact nine+r2 build; preserve p6 TWRP/p7 boot/p8 fallback/p10/COM9, same 1550B NVRAM per-device identity, no permanent installation or silent country change. Do not rerun consumed owner one-shots.
3. Test firmware dual-band **readback**, 2.4G and 5G channel flags/regulatory safety, first/second real cfg80211 scan and event generation ownership, full cleanup. Distinguish test failures in firmware initialization from scan event issues and WLC_UP readiness.
4. Make any fixes by **amending existing WIFI-01–04** when they fall within each logical scope. Use new patch only for truly independent functionality; GitHub issue count does not dictate patch count. Continue [GitHub #1](https://github.com/Olsens11/XoomLinux7/issues/1) and [#4](https://github.com/Olsens11/XoomLinux7/issues/4).
5. Only after demonstrated dual-band stable repeat scan/association and device-specific regulatory compliance consider a safe private firmware deployment strategy with provenance/license controls. Do NOT commit proprietary Motorola firmware or NVRAM bytes to public repo.

**Historical evidence is the authority.** The user's recollection was materially relevant, and the later firmware-country readback proves US rev69 was indeed accepted; **US69 by itself did not recover the generic image's 5G**, whereas **firmware-only May2012 with unchanged NVRAM DID**. This is a controlled difference, not a proven internal RF register cause. No radio configuration, reboot, flash, live module replacement or device firmware changed during the 2026-10-28 historical reconciliation.
