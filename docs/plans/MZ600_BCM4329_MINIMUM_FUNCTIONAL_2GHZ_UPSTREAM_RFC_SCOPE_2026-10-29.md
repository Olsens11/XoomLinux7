# Decision: minimum functional BCM4329 Wi-Fi upstream RFC — 2.4 GHz first

**2026-10-29 | Owner-approved scope decision | DESIGN ONLY. No kernel patch amended, no firmware/radio or Xoom state changed.**

## Why we changed direction

Our work is the *initial upstream integration* of original Motorola Xoom BCM4329 firmware and board behavior on pinned Linux 7, not an incremental patch to an already fully supported modern radio. Comparisons with accepted follow-up fixes alone understate the necessary foundation. We compared with Linux 3.2's original BCM4329-capable `brcmfmac` architecture: existing SDIO, firmware I/O, cfg80211, historical scan protocol, connection/authentication, and channel presentation. The design should reuse those established Linux interfaces, not build a separate proprietary driver or a speculative recovery service.

The owner's rationale: **get a credible, usable minimum implementation in front of upstream maintainers before adding features whose correct design may depend on upstream feedback**. Even before merging, an **RFC** can ask for review. Initial RFC readiness and eventual approval/merge are distinct milestones.

## Agreed initial functional target — demonstrable, not inferred

1. **Normal boot:** the Motorola Xoom MZ600 automatically powers/initializes BCM4329, loads the correct nonredistributed OEM firmware and device-specific calibration/NVRAM and registers `wlan0` via existing SDIO `brcmfmac` and `cfg80211`. No diagnostic overlays, magic manual commands or special user-space recovery scripts.
2. **Ordinary 2.4 GHz connectivity:** list networks in `iw` and NetworkManager, repeat scans without stale scan completion or firmware-NOTUP lockup, connect using a commonly supported WPA2 network, obtain a DHCP address, exchange data, disconnect/reconnect, and reproduce behavior across reboots/module lifecycle. Test exactly what is claimed on real device; a source-only compile is not acceptance.
3. **Minimal truthful firmware compatibility:** use a bounded legacy channel-discovery fallback for proven unsupported `chanspecs` only, distinguish native `BCME_UNSUPPORTED=-23` from other values that normalize to Linux `-EBADE=-52`; adhere to existing `brcmfmac`/`cfg80211` ownership and one logical issue per patch. Do not invent country metadata or change shared per-interface error-mode state.
4. **Basic safe regulatory policy:** respect immutable board/calibration/hardware exclusions, actual firmware restrictions and applicable Linux regulatory requirements. **No unverified active 5 GHz transmission**. Determine in source and physical tests whether excluding unsupported 5GHz entirely from initial operation is required; **NO_IR alone is not equivalent to banning all STA transmissions**. Do not confuse a `GET_VALID_CHANNELS` inventory with DFS/passive, power or regulatory authorization; do not force US/69 and do not trust the Broadcom PHY custom `99` domain to supply absent DFS/passive rules.
5. **Reproducible upstream-review package:** one logical issue per patch, full deterministic boot/build from pinned Linux source, exact original firmware provenance (without redistributing proprietary blobs), build and runtime traces, negative/regression tests, known limitations, issue-linked amendment/rollback records, no fabricated DCO or maintainer acceptance.

## Explicitly not required for first RFC

- Full 5 GHz STA association, active scan, DFS or radar functionality until permissions and firmware policy are verified; track as a **separate follow-up with documented limitations**. If 5 GHz support is intentionally deferred, don't falsely advertise it as complete, and prevent unsafe operations.
- A driver-maintained last-known regulatory channel snapshot, firmware-generation cache, asynchronous retry worker, custom recovery engine or speculative fail-closed blanket shutdown. The existing r7 source study and 19/19 exact-C sanitized host fault tests demonstrate that the legacy helper does not partly modify channel flags on query failures, and that the `void` notifier logs failed requery; **they do not demonstrate a physical failure that requires new recovery machinery**. Keep documented as follow-up questions; revisit when observed behavior, regulator safety or maintainer feedback justifies it.
- Bluetooth/FM bring-up, sophisticated power savings, all firmware revisions, all regional variants or unusual error recovery. Existing shared chip power design must not preclude them later.

## Evidence versus pending proof

**Known from physical work:** Original MZ600 Debian Linux7 runs from internal p10, functioning generic BCM4329 2.4GHz network has been demonstrated; original Motorola 2012 firmware exposes both bands and returns valid channel inventory under same US/US/rev0 with original NVRAM. A past OEM scan showed 5GHz APs. **Not automatically proven for the clean new RFC build:** repeat-scan/association across all paths, 2.4GHz functional stability with selected OEM firmware, complete legal per-PHY 5GHz behavior, or correct handling of all regulator changes.

**Source-only work:** r7 (four logical WIFI patches within the original nine patch reference) full ARM zImage/DTBs/modules compile PASS, imported symbol CRC 259/259, 19/19 source-extracted C host fault checks PASS. This is engineering evidence, **not hardware RFC acceptance**. R7 includes conservative complexity from earlier phase; do **not** automatically assume r7 is the minimal patch that should be submitted. Preserve r7 and its r6 rollback as historical research references while deriving a smaller functional candidate and testing it.

## Proposed RFC sequence

- Freeze/retain r7 research exactly as-is, including source hashes, full build and issue #4 notes.
- Trace necessary hardware/DT and firmware compatibility versus original Linux 3.2/mainline code; select the **minimum tested functional subset** of existing review members. Do not remove necessary safety/transport error semantics merely to reduce line count.
- Establish a clean reproducible 2.4GHz normal-use physical test matrix and explicit 5GHz non-support/regulatory stop policy, then validate it before describing anything as usable or safe.
- Perform full isolated ARM/kernel build, module/DT integrity tests, hash-pinned and owner-approved temporary device test with independent rollback; ensure unchanged working Xoom baseline until authorized. No silent flash or firmware-country changes.
- Prepare an RFC cover letter identifying which capabilities are demonstrated, why the patch set is organized by single logical issues, exact supported device/firmware evidence, safety boundaries, and targeted maintainer questions (legacy `chanspecs` fallback, regulatory `NO_IR`/DFS metadata, repeated scan lifecycle). Avoid claiming acceptance or posting to mailing lists without explicit owner instruction.

## Issue and rollback discipline

- Owning Wi-Fi patch issue: [WIFI-01 #4](https://github.com/Olsens11/XoomLinux7/issues/4). If an existing patch is *actually amended*, post before/after exact patch/source identifiers, old/new behavior, evidence, test results, known limitations and **rollback instructions** to its issue, with a later separate actual build/physical QA update. Track other patches on their own owning issue.
- This decision is **scope-only**; no existing patch or Xoom device has been changed, so there is **no patch rollback yet**. The preserved [r7 review directory](../../patches/upstream/review-wifi-four-logical-20261029-r7/README.md) and earlier r6 remain existing rollback/research anchors.
- Acceptance sequence: **A** working/safely restricted 2.4GHz baseline, **B** documented initial upstream RFC (review requested, not merged), **C** review-driven revisions and eventual merge, **D** additional 5GHz and chip-function development with a stable foundation.

**Next step before coding:** Confirm that selected firmware, 2.4GHz scan/connection and the safe exclusion of unverified 5GHz behavior can be reproduced with the simplest existing upstream interfaces. Then derive a minimum review patch; do not resume speculative recovery work.
