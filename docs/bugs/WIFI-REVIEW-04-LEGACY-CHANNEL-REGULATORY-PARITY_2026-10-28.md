> **Source-only candidate update, 2026-10-28 (not a resolved physical defect):** [WIFI-01 revision 2](../../patches/upstream/review-wifi-four-logical-20261028-r2/README.md) now mirrors the baseline's *optional* `per_chan_info` radar/passive query on validated legacy channels. Strict per-commit lint and ARM brcmfmac-prefix compile PASS; no runtime command/response or regulatory result proven. Preserve this original as-of report, keep [GitHub #4](https://github.com/Olsens11/XoomLinux7/issues/4) OPEN until hardware/firmware acceptance and error fallback are verified. [Exact QA](../checkpoints/MZ600_WIFI01_R2_PER_CHAN_RESTRICTION_SOURCE_QA_2026-10-28.md).

# WIFI-REVIEW-04 — BCM4329 fallback does not reproduce firmware per-channel restriction checks

**Status 2026-10-28:** **CODE-PATH DIFFERENCE PROVEN; REGULATORY IMPACT UNPROVEN.** This is a **patch-introduced safety review concern**, not evidence of unlawful emission or a tested hardware defect. **Priority: HIGH before accepting WIFI-01 or expanding 5GHz tests.** No corresponding issue filed in the public xoom-linux/linux tracker at audit time. Patch under review: WIFI-01 `b2e17d21f52a2870d30daffb8af20a7369ef15a3`, `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`.

## Source difference

**Original upstream normal path**: `brcmf_construct_chaninfo()` reads `chanspecs`, then for each permitted 20MHz channel asks `per_chan_info`; if available, maps `WL_CHAN_RADAR` to `IEEE80211_CHAN_RADAR | IEEE80211_CHAN_NO_IR` and `WL_CHAN_PASSIVE` to `IEEE80211_CHAN_NO_IR`.

**Our legacy fallback**: On BCM4329 `chanspecs == -EBADE`, queries bounded `WLC_GET_VALID_CHANNELS`, validates numeric channels, marks unsupported channels disabled and ORs `NO_HT40/NO_80MHZ/NO_160MHZ` into supported entries. This path **does not query `per_chan_info`** or equivalently import firmware-only passive/radar restrictions. It does not directly clear existing `cfg80211` restriction flags, which is a meaningful safety property, but **retaining existing flags is not automatically equivalent to applying additional restrictions known only to firmware**.

## What we know and do not know

- Proven: exact source branch difference, and 2.4GHz channel-11 association, current `phy0` has no 5GHz band. Earlier HRI39 firmware test advertised 5GHz channels with `NO_IR`.
- Unknown: whether this legacy firmware implements `per_chan_info`, which precise channel restrictions it reports, whether its own firmware enforces passive/radar limits independently, and whether the current kernel/regdb already has equal or stronger restrictions for all exposed channels.
- Therefore **do not claim existing transmissions are illegal, or even that this branch is currently active on this boot**. Trace the exact fallback branch with a read-only or sandboxed test if firmware supports such introspection; prioritize source/regulatory review before any re-enable of channels.

## Acceptance test plan

1. Compare pre-patch and post-patch `iw phy` channel/NO_IR/DFS flags for same firmware+NVRAM without forcing invalid transmissions.
2. Establish firmware `per_chan_info` support and results in a controlled diagnostic; if unsupported, design conservative restrictions that respect country/regdb/firmware requirements and do not *guess* legal TX authorization.
3. Write source-level tests for known permitted, passive/NO_IR, radar/DFS, disabled and unknown channels; check that fallback does not broaden authorization or accidentally enable bandwidth.
4. Revalidate on at least the original MZ600 firmware revision and new firmware version. Keep this issue separate from creating a missing 5GHz wiphy band.
5. Only after these checks decide whether WIFI-01 needs a revision; maintain one logical issue per patch, no forced regulatory code.

Reference: [Formal upstream provenance audit](../checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md), [earlier exact nine-patch live audit](../checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md). No device changes were made while authoring this issue.
