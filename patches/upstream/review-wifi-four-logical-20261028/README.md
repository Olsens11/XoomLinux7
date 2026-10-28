# BCM4329 Wi-Fi RFC — four logical review commits

**Status: UNDER SOURCE QA, NOT SUBMITTED.** Base: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. No human signoff; placeholder draft author. Private Motorola firmware, NVRAM, credentials and board deployment are excluded.

This is an alternative patch boundary to the earlier [three-patch Wi-Fi v2](../review-wifi-v2-20261028/README.md), **not** an additional patch series to stack onto it. The source tree at the tip of the earlier 3-patch series and of the initial 4-patch series was confirmed identical by direct Git diff across the two local kernel worktrees on 2026-10-27. Rewording the 4-patch commit messages does not change kernel code.

| Member | One logical issue | Independent result |
| --- | --- | --- |
| 1/4 | Affected BCM4329 firmware rejects `chanspecs`; use bounded legacy channel list without broadening regulatory rights | Independent channel enumeration |
| 2/4 | A fixed ESCAN sync ID cannot reject a late completion for the previous request; generate/check request identity | Independent stale-success protection, no exceptional owner remap |
| 3/4 | Valid terminal Event69 reports unmapped bsscfg; recover only matching current primary STA terminal | Depends on 2/4, preserves normal events, no partial-result remap |
| 4/4 | Legacy firmware is DOWN after idle MPC; restore readiness conditionally before another scan | Independent `WLC_GET_UP`/`WLC_UP` recovery |

**Why split 2 and 3?** Transaction validation alone is usable and does not reroute an event. Recovery of a misplaced terminal can safely depend on the previously introduced scan identity. This follows the kernel's accepted model of logically separate, bisectable changes. A single combined patch remains the fallback if independent prefix testing reveals a correctness defect.

**Checks and caveats:** The original three-patch source replay and full ARM build PASS belong to the v2 series. The new four-way RFC has **four passing sequential ARM driver-prefix compiles and a passing unchanged-source full zImage/DTBs/modules build** in an isolated clean worktree. The first full build hit a GCC internal segmentation fault; a -j4 retry of the identical source completed successfully. All four wireless patch descriptions now pass strict checkpatch 0/0/0; the independent DT extraction still has inherited style defects. Exact hashes and negative evidence are in the dated checkpoint. The source is **not** the physically installed V31 lab source and has **not** been tested as these exact patches on hardware. Scan cancellation, timeout, late events, multiple interfaces, teardown, power management and 399-second association all require explicit further review. Do not mail this RFC or add human `Signed-off-by` without the owner's examination and approval.

**Submission format:** four `git format-patch`-style drafts, one cover draft and a `series` ordering file. No hypothetical driver feature, cosmetic experiment log or generated kernel module belongs in a patch. Event code0/16 association work remains separately unproven. See the [per-maintainer source tracker](../REVIEW_TRACKS_20261028.md) and [G01–G12 gates](../candidate/SUBMISSION_REQUIREMENTS.md).
