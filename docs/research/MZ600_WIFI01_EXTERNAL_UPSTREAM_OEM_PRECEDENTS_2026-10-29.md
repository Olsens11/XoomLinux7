# WIFI-01 external precedent audit: preserve legacy intent through smallest upstream-compatible method — 2026-10-29

**Scope: SOURCE RESEARCH / DESIGN GATE ONLY.** No new patch, build, firmware experiment or changed tablet state in this research step. Current physical authority: [Oct 29 native firmware ABI proof](../checkpoints/MZ600_WIFI01_BCME_SIXFORMAT_NATIVE_UNSUPPORTED_PHYSICAL_PASS_2026-10-29.md) and [issue #4](https://github.com/Olsens11/XoomLinux7/issues/4). WIFI-01 r3 is still unsigned and unaccepted.

## Owner rule and decision criterion

**For every incompatible legacy mechanism, preserve the *intended* hardware/functionality/regulatory behavior and change the smallest possible piece of implementation, reusing upstream-accepted interfaces and analogous fixes before inventing an interface or rewriting common code.** Search *both* same-driver/vendor lineage and similar-driver Linux practice, with line-level references; separate historical code precedent from measured firmware behavior and from our proposal. A broad feature disable that hides an error is not an intent-preserving repair.

## Existing MZ600 measurements (not newly tested here)

- OEM May 2012 Motorola BCM4329 firmware `4.218.248.44` with original 1550-byte calibration/NVRAM. `BRCMF_C_GET_BANDLIST` dual band; `BRCMF_C_GET_VALID_CHANNELS` returned **35** current valid channel numbers (11 in 2.4 GHz, 24 in 5 GHz). `chanspecs` failed as `-EBADE` (raw BCME for *that* command not measured).
- All **six** tested `per_chan_info` channel 11/36 historical argument encodings returned transport=0, native `BCME_UNSUPPORTED=-23`, normalized `-EBADE=-52`, **no valid radar/passive flags**. No evidence that metadata can be inferred from responses. `BRCMF_C_GET_VERSION` success `io_type=1`. The experiment did no scanning or regulatory writes and restored original connected Wi-Fi.
- Existing WIFI-01 r3 does the proven `GET_VALID_CHANNELS` enumeration, limits HT20, and caches `per_chan_info` as unsupported whenever `-EBADE`. That cache is **not generally valid**: pinned `fwil.c` normalizes distinct negative BCME failures to `-EBADE`.
- Existing mainline `brcmfmac` registration sequence in pinned kernel: `brcmf_setup_wiphy()` gets firmware BANDLIST, initializes band templates, then `wiphy_apply_custom_regulatory(..., brcmf_regdom)` with broad custom `alpha2=99`, then `wiphy_register()`, **then** `brcmf_setup_wiphybands()` builds channel inventory and flags. Pinned `net/wireless/core.c:wiphy_register()` snapshots channel `orig_flags` from *registration-time* flags; `net/wireless/reg.c` uses that saved baseline on later regulatory processing. R3's channel-filter edits currently occur after registration.

## External precedents: verified source behavior and relevance

### 1. Broadcom `bcmdhd` legacy: ignore exactly unsupported `chanspecs` and preserve band setup (**same vendor, near-exact symptom**)

- **Primary source** [Android kernel/common bcmdhd `wl_cfg80211.c`, `wl_update_wiphybands()`](https://android.googlesource.com/kernel/common/+/6444e59eb90ee05bdc0d51e0dabd82515688cf58/drivers/net/wireless/bcmdhd/wl_cfg80211.c): this older Broadcom path tries `wl_construct_reginfo()`; if it returns **native `BCME_UNSUPPORTED`**, it deliberately ignores that optional newer-`chanspecs` failure and continues setting up advertised bands and older HT capabilities. Other errors remain fatal. This is direct **compatibility precedent**, not proof that all old firmware failures are unsupported.
- **Implication:** preserve upstream modern `chanspecs` path and only substitute narrow legacy discovery when truly unavailable. Distinguish native BCME status instead of assuming all `-EBADE` are unsupported. Preserve the existing registration and regulatory system.
- **Do not copy:** legacy custom `brcm_regdom alpha2 99` broad rules as proof of modern legal TX authority.

### 2. Broadcom `bcmdhd` later variants: explicit `per_chan_info` unsupported handling (**same vendor, same optional metadata**)

- **Primary source** [Android msm bcmdhd `wl_construct_reginfo`](https://android.googlesource.com/kernel/msm/+/f53d35016edb34e6fde182f2b805ffa47c175489/drivers/net/wireless/bcmdhd/wl_cfg80211.c): checks native `BCME_UNSUPPORTED` for `per_chan_info` and has a specific fallback path rather than fabricating radar/passive bits. Other Broadcom implementations decode `WL_CHAN_RADAR` and `WL_CHAN_PASSIVE` only on valid replies.
- **Implication:** unavailable metadata is an explicit capability condition. A fake firmware response/interface is not required. But any historical `dfs_radar_disabled` behavior is not automatically equivalent to correct present-day DFS authorization; **do not copy blanket flag workarounds**.
- **Project evidence:** [actual physical six-query native error test](../checkpoints/MZ600_WIFI01_BCME_SIXFORMAT_NATIVE_UNSUPPORTED_PHYSICAL_PASS_2026-10-29.md) now confirms `BCME_UNSUPPORTED` for **per_chan_info** on this OEM sample, not for all other firmware calls.

### 3. Linux Wireless regulatory processing: capabilities before register; rules evolve afterwards (**authoritative subsystem contract**)

- **Primary reference** [Linux Wireless regulatory processing](https://wireless.docs.kernel.org/en/latest/en/developers/regulatory/processing_rules.html) and [cfg80211 device documentation](https://docs.kernel.org/next/driver-api/80211/cfg80211.html).
- Drivers establish *hardware-supported channels and persistent hardware limitations* before `wiphy_register()`; cfg80211 snapshots registration-time `orig_flags` and computes restrictions using current world/country regulatory rules, notifications, DFS and beacon hints. **`orig_flags` is a kernel bookkeeping baseline, not a simulated Broadcom metadata response.**
- **Implication:** R3's after-registration `DISABLED`/HT20/unknown-5GHz `NO_IR` updates may not survive rule recalculation. Validate this with **actual pinned `net/wireless/core.c`, `net/wireless/reg.c`**, not just docs. A small pre-registration setup *may* be appropriate for truly immutable hardware limits, while country-dependent rules stay dynamic.
- **Crucial constraint:** do not blindly move all `brcmf_setup_wiphybands()` ahead of registration; it has initialization/firmware readiness and notifier dependencies and broader feature effects. Find the minimal timing/ownership alteration.

### 4. Marvell `mwifiex`: firmware bands/custom restrictions at initialization, normal notifier for later region changes (**parallel FullMAC driver, mature upstream approach**)

- **Primary source** [pinned Linux7 `mwifiex/cfg80211.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/marvell/mwifiex/cfg80211.c) around `mwifiex_register_cfg80211()` and `mwifiex_reg_notifier()`.
- Sets 5 GHz advertised band according to `adapter->config_bands`; applies optional regulatory domain **before** `wiphy_register`; after registration uses country/regulatory hint where appropriate. Its `reg_notifier` applies channel radar restrictions and, for country changes, sends domain information and TX-power settings to firmware.
- **Implication:** reuse cfg80211 as the one policy controller; firmware knows current country/calibration and driver must coordinate legitimate updates. This is an **architectural precedent**, not a drop-in BCM4329 algorithm. Do **not** copy its `REGULATORY_DISABLE_BEACON_HINTS` or country-IE flags without proving equivalent device requirements.

### 5. Atheros `ath9k`: EEPROM/hardware regulatory initialized before register, country hint afterwards (**other independently mature upstream precedent**)

- **Primary source** [pinned `ath9k/init.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/ath/ath9k/init.c) `ath9k_init_device()`: initializes regulatory from device data before `ieee80211_register_hw`, then sends applicable `regulatory_hint()` afterward.
- **Implication:** again distinguish physical device restrictions from mutable national regulatory authority; let kernel enforce interplay. Does *not* license inventing Motorola factory EEPROM/country values.

### 6. Current-channel filtering vs immutable hardware capability (**Broadcom dynamic semantics, important negative design constraint**)

- **Source** [legacy Android Broadcom `wl_get_valid_channels` and P2P scan filtering](https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/wl_cfg80211.c), and independently documented [historical Broadcom request use](https://project-zero.issues.chromium.org/issues/42450071). `WLC_GET_VALID_CHANNELS` is used as an enumeration of channels **valid in the current regulatory context** when filtering scan requests, not certified as an immutable factory chip-wide superset. Broadcom header also distinguishes `WL_CHAN_VALID_HW` from `WL_CHAN_VALID_SW` (**valid in current country**): [archived Broadcom `wlioctl.h`](https://android.googlesource.com/kernel/common/+/f02fac63308349b1dbde468adfd084fdb560eeae/drivers/net/wireless/bcmdhd/include/wlioctl.h).
- **Design warning:** simply ORing all presently unlisted channels into `orig_flags DISABLED` forever before registration could **freeze a country-specific subset** and prevent legitimate later country transitions (contrary to preserving original function). Do **not** assume the current 35-channel list is eternal hardware capability. Need source/measurement proof of whether this OEM firmware's list changes with legitimate country state, or a separate immutable hardware-band limit.
- **Security precedent:** the historical Broadcom P2P code exposed a count-validation issue when trusting firmware-returned channel counts (fixed later; Project Zero report). Our fallback must continue to validate list capacity, count, values and malformed data, and avoid duplicate-result overflow. This is not permission to query arbitrary country values or mutate the device.

### 7. brcmfmac maintainer discussion: channel rejected despite apparently valid regulatory region (**same driver, related symptom, not an implemented fix**)

- **Source** [Arend van Spriel, hostap mailing list 2024](https://lists.infradead.org/pipermail/hostap/2024-July/042820.html): `brcmfmac` `set chanspec` -52 error for a legacy 5 GHz channel; maintainer notes some invalid historical channels may be removable but other errors affect channels legitimate in some regions, requiring upstream wireless discussion.
- **Implication:** generic `-52` alone is not reliable proof of what is forbidden. Do not solve by hiding all 5GHz channels or relaxing regulatory rules to make error disappear. This is a **discussion precedent**, not tested resolution or same firmware.

## Decision matrix

| Candidate | Source/hardware basis | Disposition |
| --- | --- | --- |
| New minimal synthetic `per_chan_info` firmware API | Vendor has no measured native reply; Linux already has channel/restriction API | **REJECT** unnecessary second interface / guessed flags |
| Leave modern `chanspecs` unchanged, isolate legacy `GET_VALID_CHANNELS` branch | Broadcom old bcmdhd + actual 35-channel OEM + upstream convention | **PREFER** for missing inventory; maintain input bounds |
| Use `-EBADE` alone as unsupported and stop trying other channels | Native `fwil.c` conflates BCME failures | **REJECT** general error-classification claim |
| Install all currently valid channels as permanent immutable pre-registration `orig_flags` | Would preserve an initial snapshot, but list can be country-scoped | **DO NOT ASSUME**; decide immutable-vs-dynamic provenance first |
| Duplicate cfg80211 rules with a static US/69 or custom 99 permissive table | No proven country/power/DFS provenance for all devices | **REJECT** bypasses/duplicates kernel rules |
| Move only genuine fixed hardware restrictions before registration; leave legitimate country updates to cfg80211 and current brcmfmac notifier | Linux Wireless, mwifiex, ath9k | **PROMISING**, subject to minimal-code and real behavior audit |
| Always add permanent blanket NO_IR on 5GHz unknown metadata | Safe as diagnostic fail-closed but suppresses legitimate active operation, conflicts with V28 dynamic behavior | **LAB POLICY ONLY** until mode/regulatory semantics evaluated |

## Smallest next source-first experiment, with falsification

1. **Zero hardware mutation:** map exact pinned `brcmf_cfg80211_attach → setup_wiphy → wiphy_apply_custom_regulatory → wiphy_register → setup_wiphybands → brcmf_construct_chaninfo`, and reg-notifier reentry. Determine which channel state belongs *before* registration (intrinsic bands, immutable channel limitations) and which may change with country. Inspect `orig_flags` recalc and custom `alpha2=99` interaction, including world/passive/beacon-hint behavior.
2. **Offline fixtures**: initial + subsequent legitimate regulatory updates; firmware BANDLIST dual band, valid list size 35, missing/extra/duplicate/bad channels, missing `chanspecs`, missing `per_chan_info`, genuine DFS/radar/passive flags where available, HT20 only, modern firmware unaffected, truthful transport vs native firmware errors. Assert no new 5 GHz TX permission, no erased native restrictions, no permanent lockout of legitimately allowed channels, and no variable state mistaken for intrinsic hardware.
3. **Only if required**, amend **existing WIFI-01** (one logical channel-compatibility issue) in an isolated scratch worktree to use the native regulatory lifecycle correctly with minimal extra source code. Avoid changing shared `fwil.c` semantics, country overrides, unrelated scan patches WIFI-02/03/04, or a fifth patch. Preserve modern path.
4. Full prefix and nine-member ARM kernel/module build plus `checkpatch`, exported symbol CRC matching. Then **separate explicit hardware gate** on replacement MZ600, RAM-only, original baseline SHA check, no uncontrolled country/scan/TX change, independent rollback. MZ604 regression only after an agreed test scope and evidence. No owner DCO or upstream submission before accepted result.

**What remains unknown:** (a) whether the exact Motorola firmware's `WLC_GET_VALID_CHANNELS` list changes with legitimate firmware country transitions; (b) which *immutable* board/channel limits can be sourced from factory calibration/OTP as opposed to country scope; (c) the minimal registration-order seam in pinned brcmfmac that preserves both baseline restrictions and dynamic country evolution; (d) whether raw BCME can be distinguished for `chanspecs` without cross-request shared state. Nothing in the external precedents proves production regulatory acceptance or actual 5GHz association on the replacement tablet.
