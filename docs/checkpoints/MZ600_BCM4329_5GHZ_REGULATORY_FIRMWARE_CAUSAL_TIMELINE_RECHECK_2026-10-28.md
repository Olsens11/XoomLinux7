# MZ600 BCM4329 — regulatory-vs-firmware 5GHz cause chronology recheck (2026-10-28)

## Why this checkpoint exists

The owner recalled that 5GHz started working when the **region/regulatory settings** were corrected and asked us to use the project's existing actual physical evidence, rather than treating a previously solved firmware-bandlist question as undiscovered. This checkpoint is a **retrospective source-record audit**, not a fresh hardware A/B run. The prior nine-patch kernel remains running on MZ600 p10 with working 2.4GHz connection. Current Wi-Fi driver source candidate WIFI-01 r2 and an isolated lab-count diagnostic are distinct, **not installed**. The historic logs remain authoritative for their as-of physical conditions.

For the broader V17–V28 firmware/scan progression and host event handoff evidence, see the companion [firmware/regulatory causal-history reconciliation](MZ600_BCM4329_5GHZ_REGULATORY_FIRMWARE_CAUSAL_HISTORY_RECONCILIATION_2026-10-28.md); this document focuses specifically on isolating the regulatory and firmware variables and the NO_IR test-gate side effect.

## Four differentiating physical tests (2026-10-26)

| Condition | Changed variable | Effective firmware/driver band evidence | Interpretation |
| --- | --- | --- | --- |
| Generic `4.220.48` + exact 1,550B installed calibration, omitting OEM bootstrap `ccode`/`regrev` | Control, firmware and board static | Firmware `WLC_GET_BANDLIST` **count=1, first=2** (2.4GHz only); `chanspecs` 11×2.4GHz, 0×5GHz; separate earlier readback cited effective US rev0 | Generic did not advertise 5GHz |
| **Same generic** `4.220.48` + exact 1,569B original OEM calibration minus only OEM `macaddr` | **Country/regrev** `US/69` at firmware bootstrap; original PA/board fields unchanged | Firmware country iovar was later read back as effective **US rev69**; bandlist **still count=1, first=2**, 11×2.4GHz channels | **US/69 alone not sufficient** to enable 5GHz in this firmware variant. Do not infer regulatory setting is immaterial to other stages |
| Original Motorola HRI39/HRI66 `4.218.248.20` + `US/69` matching calibration | **Both firmware and country/regrev relative to generic control changed together** | Actual bandlist **count=2, 5GHz=1, 2.4GHz=2**; country readback `US, rev69`; legacy valid-channel query **11×2.4GHz + 9×5GHz**; later channel36 passive WLC_SCAN ioctl50 and results ioctl51 actual envelope PASS | First dual-band milestone paired OEM firmware **and** OEM regulatory NVRAM; it **does not isolate which was necessary**. It does prove firmware's 5GHz hardware capability with validated channels |
| Later Motorola OEM May 25 2012 `4.218.248.44` + **same unchanged 1,550B installed calibration as generic control** | **Firmware binary changed alone**, board/factory identity/NVRAM unchanged | Firmware bandlist **count=2, first=1, second=2**, `GET_VALID_CHANNELS` **11×2.4GHz + 24×5GHz**; wiphy fixed 5GHz entries 24 NO_IR + 5 disabled; independent rollback | **Firmware identity alone affects advertised 5GHz support in this exact MZ600 environment**. This removes the mistaken inference that US/69 is universally required to expose 5GHz; it does not negate meaningful regulatory effects on legal operations |

The known firmware versions and binaries use **different Broadcom branches**. Generic September 2011 `4.220.48` is not “newer OEM” merely because 4.220 is greater than 4.218. OEM May 2012 `4.218.248.44` is a **later build date**, successfully shown on the actual test Xoom.

## Later 5GHz scan breakthrough (critical subsequent physical evidence)

The May2012 2012 OEM firmware not only advertises 5GHz; the earlier project's **V17** on 2026-10-27 performed a **real native Linux7 5GHz ch36 ESCAN**, delivered genuine Event69 terminal SUCCESS (status0), completed with `aborted=0`, returned two BSS and `iw` in **661ms**. V17 varied event-observer subscriptions **and** kept an otherwise quiescent Bluetooth module stack loaded; it did **not** isolate which change caused that success. The same firmware still lacked terminal delivery in prior V14/V16 under those different test conditions.

The **V18 ten-scan controlled mask series** subsequently found that **all 10** 5GHz tests received real Event69 status0 SUCCESS at low-level firmware-event ingress, but **eight** did not deliver SUCCESS to the cfg80211 handler and timed out. This disproves the simplistic theory that 5GHz firmware never generates its terminal event; the host ingress-to-worker/interface mapping/ownership path is a key area for WIFI-02/WIFI-03 acceptance. V21 later proved targeted owner-routing of a genuine terminal can recover previously misrouted events (not a fabricated success). This issue is **distinct from regulatory band/channel permissions** and from the second-scan firmware `BCME_NOTUP` state.

Sources: [V17 real 5GHz native terminal](MZ600_V17_2012_5G_CH36_WIDE_EVENT_MONITOR_REAL_ESCAN_TERMINAL_SUCCESS_661MS_PHYSICAL_PASS_2026-10-27.md), [V18 ten tests at ingress](MZ600_V18_PARAMETRIC_MASK_TEN_SCANS_FIRMWARE_TERMINAL_AT_INGRESS_NOT_HANDLER_2026-10-27.md), [V21 owner routing](MZ600_V21_TERMINAL_OWNER_LAB_SWITCH_AB_PHYSICAL_PASS_2026-10-27.md).

## Other regulatory interaction observed October 27

- V25 repeat-scan lab gate required channel36 `IEEE80211_CHAN_NO_IR` to remain set. After an initial 5GHz scan and reception of a beacon, regulatory `handle_reg_beacon()` could clear that flag under applicable rules. The lab guard rejected the **second** scan with userspace `-EPERM`. **This was a test-policy artifact**, not firmware losing Band 2 or evidence that Linux violated RF restrictions. Do not reintroduce or force a NO_IR flag in production to accommodate an obsolete test gate.
- V26b **removed only the obsolete lab prerequisite** and left kernel/regulatory constraints intact. The second scan reached firmware but failed `-52`. V27 decoded exact vendor firmware code `-4 = BCME_NOTUP` (readiness); V28 removed the whole private single-channel/passive test gate, completed one **normal multichannel scan 12 BSS** on the 2012 OEM firmware, then the next native scan failed again. **Repeat-scan firmware state is distinct from regulatory authorization.**
- Same 2012 firmware's channel1 2.4GHz passive ESCAN Event69 actual SUCCESS was physically proven (179ms). Channel36 5GHz ESCAN Event69 PARTIAL and real valid BSS records without terminal also existed in V14/V16, while V21's controlled event-owner routing delivered genuine firmware terminal SUCCESS when event if/bsscfg indices were nonstandard. Don't conflate loss of a terminal event, missing Band 2, and firmware `BCME_NOTUP` on later requests.

## Consequence for present nine-patch integration

1. **Do not repeat previously consumed generic bandlist/US69 experiments** or pretend band capability is unmeasured. Existing documented physical A/B evidence is sufficient to direct work toward the 2012 OEM firmware path, with original NVRAM, matched modules, and proven regulatory/identity guardrails.
2. WIFI-01 r2 is **not yet qualified**. Its optional `per_chan_info` query is a plausible same-logical-patch correction, but must be tested on the **legacy-`chanspecs`-rejecting OEM** firmware. Compare original passive/radar flags and effective country/region readbacks. The generic 4.220 firmware likely won't exercise the legacy fallback and is not the main test of WIFI-01.
3. **Do not unconditionally set US/69** on every Xoom; only OEM-proven per-variant, per-country regulatory mapping, signed regdb, firmware rules and antenna calibration authorize channels. No simple country setting overrides firmware's unsupported bands or legal limits.
4. Preserve the distinction between kernel bandlist support (#1), regulatory channel restrictions/WIFI-01 (#4), ESCAN owner/completion (#5/#6), firmware readiness/repeated scans (#7/#13). Issues can share evidence without requiring one new patch each.
5. A full **lab-only** original nine-integrated kernel + WIFI-01 r2 + read-only `GET_BANDLIST`/`chanspecs`/`per_chan_info` numeric summary was newly **built** in isolated WSL workspace 2026-10-28 (no deployment). The complete ARM build's `zImage`, Stingray/Wingray DTBs, WCC and brcmfmac module hashes are recorded privately under `qa-bcm4329-banddiag-r2-nine-build-20261028/full-build-artifact-manifest-20261028.txt`; the old exact nine-source manifest remains valid and unchanged. Since generic `GET_BANDLIST` is already proved, **avoid an unnecessary disruptive boot just to reproduce it**. If this isolated diagnostic is used later, it must specifically test previously unmeasured behavior, especially legacy OEM per-channel restrictions, under the preserved COM9/fallback approval process.

## Primary dated evidence

- [Original HRI39 firmware with OEM US/69, 2G+5G bandlist, legacy channel count (physical)](MZ600_V064_HRI39_OEM_FIRMWARE_TWO_BANDS_LEGACY_VALID_CHANNELS_20_PASS_2026-10-26.md)
- [Generic firmware 2.4GHz-only bandlist and chanspec proof](MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md)
- [Generic with OEM US/69 boot calibration still 2.4GHz](MZ600_V064_OEM_US69_BOOTSTRAP_NVRAM_A_B_PHY5GHZ_UNCHANGED_OWNER_PHYSICAL_2026-10-26.md)
- [OEM calibration content exact three-field difference](MZ600_OEM_HRI39_HRI66_COUNTRY_REGREV_CALIBRATION_EXACT_DIFF_2026-10-26.md)
- [May 2012 OEM firmware-only dual-band on same MZ600, unchanged NVRAM](MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md)
- [2.4GHz ESCAN terminal real SUCCESS 179ms](MZ600_V15_2012_OEM_2G_ESCAN_EVENT69_TERMINAL_SUCCESS_179MS_PHYSICAL_PASS_2026-10-26.md)
- [5GHz Event69 PARTIAL and no terminal in controlled V16](MZ600_V16_2012_5GHZ_ESCAN_PASSIVE_500MS_MORE_PARTIALS_NO_TERMINAL_PHYSICAL_2026-10-27.md)
- [V21 terminal owner recovery A/B](MZ600_V21_TERMINAL_OWNER_LAB_SWITCH_AB_PHYSICAL_PASS_2026-10-27.md)
- [V25–V27 NO_IR beacon hint lab artifact, then firmware BCME_NOTUP](MZ600_V25_TO_V27_SECOND_SCAN_REGSTATE_AND_FIRMWARE_NOTUP_2026-10-27.md)
- [V28 normal multichannel scan then failed second](MZ600_V28_NATIVE_CFG80211_SCAN_AFTER_LAB_GATES_REMOVED_2026-10-27.md)

**Verdict as of this retrospective audit:** Regulatory mapping was plausibly a meaningful early condition and **definitely affected subsequent lab scan gates**, but controlled evidence shows **neither US/69 alone sufficient nor OEM May2012 firmware needing that extra US/69 bootstrap to advertise 5GHz**. Firmware choice, regulatory permissions, per-channel mapping, scan completion and readiness are different layers; investigate each without retesting solved facts.
