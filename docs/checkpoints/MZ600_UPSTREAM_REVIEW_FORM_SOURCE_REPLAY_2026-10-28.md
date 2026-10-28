# MZ600 Linux 7 — Submission-form source replay, 2026-10-28 UTC

**Status: REVIEW-FORM SOURCE REPLAY + FULL ARM BUILD PASS, DT STYLE/SCHEMA AND PHYSICAL GATES OPEN; NO tablet deployment.** This checkpoint is a source/build milestone, **not** a physical Wi-Fi acceptance test, complete-device release, signed submission or evidence that the tablet runs the newly cleaned patches.

## Objective and source provenance

Owner requirement: maintain the entire BCM4329 kernel work as independent, upstream-style maintainer-routed patches **during** development, including exact-source builds, with no actual posting until the complete Wi-Fi/BT/SDIO/power/board integration is ready and separately approved.

- Pinned developer kernel base: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
- Project review branch: `wip/clean-wifi-bt-usb-20261025`.
- **DT source:** `patches/upstream/review-stingray-dt-20261028/series` (3 independently formatted RFC commits: ARM binding, common Xoom dtsi extraction, Stingray wrapper).
- **Wi-Fi source:** `patches/upstream/review-wifi-four-logical-20261028/series` (4 independently formatted unsigned RFC commits: legacy channels, transaction identity, genuine terminal owner routing, conditional firmware readiness).
- **Source equivalence:** A direct Git diff between initial four-way review tip `7ac943336` and prior three-way Wi-Fi tip `2404fdf7d` returned empty. The four-way branch changes commit boundaries, not final source code. Patch descriptions 2/4 and 3/4 were subsequently wrapped to satisfy strict checkpatch; no source hunks altered.
- Source worktree on DESKTOP-R16QJD4 WSL: `qa-submission-shape-source-20261028`, isolated from tablet/host experimental source; build output separate as `qa-submission-shape-build-20261028`.
- Cross compiler: ARM GNU Toolchain 14.3.Rel1 arm-none-linux-gnueabihf; known v06.4 Debian-p8 `.config` copied to a fresh output folder; ARM target.
- Full raw QA logs retained privately on desktop under `qa-submission-shape-{report,continuation,final}-20261028.txt`. Never put private network identifiers/firmware or raw device logs in public Git.

## Measured test sequence

1. Independent clean Git worktree created from the exact base; DT 1/3 and 2/3 replayed. The replay halted on strict `git diff --check` for inherited Wingray whitespace moved to the common dtsi. Failure retained in its first log; **this is a real style gate**, not a runtime error.
2. Resumed without hiding the failed check, applied DT 3/3; ARM `make dtbs` **PASS**. Existing earlier DT-equivalence inspection is separately recorded in the DT review directory. **DT 2/3 inherited format/whitespace failures OPEN**, as are `dt_binding_check` and `dtbs_check`.
3. Applied four independently scoped Wi-Fi source patches in order. **Each cumulative Wi-Fi prefix compiled `drivers/net/wireless/broadcom/brcm80211/brcmfmac/` independently** (0001 then 0002 then 0003 then 0004), using the same ARM cross compiler and config; this is per-prefix driver compilation, not a full kernel build or runtime test at every prefix.
4. Strict `checkpatch.pl --no-tree --no-signoff --strict` initially found overlong prose in Wi-Fi 2/4 and stopped the first run. Commit prose rewrapped; subsequent direct strict checks of Wi-Fi 2/4 and 3/4 each yielded **0 errors, 0 warnings, 0 checks**. No change to any code hunk.
5. Full matched `make -j8 zImage dtbs modules` from the replayed review-source tree **failed** after 559 seconds when GCC 14.3.1 suffered an internal compiler segmentation fault at generic `include/linux/errseq.h` while compiling `sound/soc/soc-link.c`. The WSL host reported ~7.1GiB available memory after the failure; no kernel source diagnostic or code compilation error was established. The failure is preserved in `qa-submission-shape-final-20261028.txt`.
6. Without touching source, configuration or patches, retried **the identical Git source commit `8d3406a4aed456b052a3d815601d4edcffb91f3e`** with `make -j4 zImage dtbs modules`: **PASS**, exit code 0, 2026-10-28 02:46:14 UTC; captured in `qa-submission-shape-gcc-ice-retry-20261028.txt`. This supports a transient compiler failure but does not conclusively establish its root cause.

### Final fresh build artifacts (same review-form source)

| Artifact | SHA-256 |
| --- | --- |
| `arch/arm/boot/zImage` | `7b16c1fd39c6d947d8551cb853dc5a8afe286edc826ca1eda3792d330f38be28` |
| `tegra20-motorola-stingray.dtb` | `c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa` |
| `tegra20-motorola-wingray.dtb` | `4144940f352b437c340c5d37f5a4c9dcc711024ef9785746ff3bd2d1f8bab3ff` |
| `brcmfmac.ko` | `5e767d47017ff9028e6c364f8325420b0fc79efd1c1e07d36595fb4fd0540d26` |
| `brcmfmac-wcc.ko` | `eb9aa7efc8d9e356088aa9693cf1937c8c7e1a65dcd0193618915521b7a048b9` |

The **two Broadcom module hashes exactly match** the earlier complete build of the *three-patch Wi-Fi v2* against the same pinned base with older platform integration snapshots. The two DTB hashes exactly match those in the independently built existing three-commit Stingray DT-review output. These are byte-level offline cross-checks, **not** proof the untested cleaned source behaves like V31 on actual radio hardware.

All four sequential Wi-Fi prefixes compiled (source commits: `1ffe51ac0`, `e25a455b3`, `8547eb87d`, `8d3406a4a`). The reusable `scripts/qa_replay_upstream_review.sh` helper was **syntax-checked with `bash -n`**, but not separately executed end-to-end; this checkpoint's actual commands were the equivalent one-shot and resumed QA scripts on the Desktop. Stored RFC email patches are exempted from Git's *outer repository* whitespace scan via local `.gitattributes`; **each applied kernel-source prefix still underwent `git diff --check`**, and the actual patch files underwent `checkpatch.pl`. The DTS moved-content style failure remains open; successful builds do not override the `git diff --check` failure in that earlier review commit. The review source intentionally omits the separate ATAG and BigPart source changes, so this output cannot yet be treated as a reproduction of the installed MZ600 p8 boot.

## Canonical patch-stream packaging qualification

After the initial source build, the alternate four-patch `series` text was found to contain **literal escaped `\\n` sequences rather than real newlines**. Its manual shell-glob replay succeeded, but the series-driven automation would have failed. This was corrected to four actual LF-delimited entries, without changing kernel source.

The corrected patch files were then replayed in an additional pristine Linux worktree, generating `24d9a3f1ccafb34285a16f9aa6da6651b555fd48`. `git diff` against the prior three-patch Wi-Fi tip was **empty**. All four messages were regenerated using real `git format-patch` commits, preserving the same code and including the corrected commit descriptions; each regenerated patch passed strict `checkpatch.pl` with **0 errors / 0 warnings / 0 checks**. The published four-way manifest was rehashed from these exact regenerated streams.

A new stdlib-only `tools/validate_upstream_review_series.py` now validates both 3-DT and 4-Wi-Fi series ordering, actual LF delimiters, complete patch files and Wi-Fi SHA256 manifest correspondence. Its own check passed for all seven patches. The reusable `scripts/qa_replay_upstream_review.sh` calls that validator before any worktree or build action. Its syntax was checked via `bash -n`. **This new reusable script has not itself completed a fresh end-to-end run yet**; this milestone's source compilation/build provenance remains the separately logged equivalent manual replay. The patch-stream metadata re-export leaves its compiled source identical.

## What remains open (no inferred passes)

- **Platform:** DTS inherited style; DT schema/ABI checks; exact board source physically booted; MZ600 vs Wingray variant behavior.
- **Boot and storage:** Real MZ600 persistent Debian p8 also depends on bootloader MAC ATAG and opt-in BigPart logic. Their older integration snapshots are **not part of this clean 3-DT+4-Wi-Fi source replay** and are not ready for upstream. BigPart `motorola,xoom-bigpart` must not be smuggled back into the shared board dtsi.
- **Wi-Fi:** Exact cleaned-source MZ600 hardware test; regulatory, stale/duplicate/cancel teardown and P2P; known slow postboot authentication and dropped code0/code16 remain unsolved.
- **Whole chip:** SDIO/PM, Wi-Fi+BT coexistence, shared power, Bluetooth and future FM are independent hardware/maintainer tracks; none are silently certified by a Wi-Fi build.
- **Mail:** Placeholder RFC author, no human `Signed-off-by`, no `Tested-by` on cleaned source, no upstream email, no user-approved posting.
- **Safety:** No COM9 client, flash, reboots, service changes, source deployment or changes to installed Xoom p7/p8 were performed in this QA.

## Routing and future milestone closure

Track each patch in [maintainer routing ledger](../../patches/upstream/REVIEW_TRACKS_20261028.md), use [G01–G12 requirements](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md), and close each subsequent milestone under [development workflow](../process/DEVELOPMENT_WORKFLOW.md). Preserve failed trials and exact hashes rather than overwriting evidence. Next: complete full build report, fix DT style as an independently reviewable change without altering DTB semantics, and bring BOOT/ATAG and STORAGE/BigPart into equally reproducible source reviews before proposing any on-device test of the full clean integration.
