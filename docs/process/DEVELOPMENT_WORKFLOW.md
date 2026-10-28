# Build, test, publish and recover

1. `git status --short`, `git branch -vv`, `git worktree list`; read [AGENTS](../../AGENTS.md), [status](../status.md), [state](../../runtime/PROJECT_STATE.env).
2. Work in topic branch/worktree. Record hypothesis, baseline, exact source and what would falsify it.
3. Fetch [upstream](https://github.com/xoom-linux/linux) at pinned commit (script in `scripts/bootstrap-upstream.sh`). Do not edit an untracked extract and forget a patch.
4. Build with ARM GNU Toolchain 14.3.Rel1, target Cortex-A9 with no NEON; capture toolchain, config and full build command. Current legacy Phase1 builder scripts are cataloged in `scripts/history/`.
5. Record exact artifact checksum and size plus builder/manifest, using immutable paths. Private binaries are kept off Git; a GitHub Release is an option after licensing review.
6. Confirm **replacement** DUT model/serial, USB fastboot status and battery. For approved test use **`fastboot boot <hash-verified-image>`**, never flash.
7. Save separate public sanitized evidence and private original logs. Label offline vs physical; negative tests and no-change cases count as evidence.
8. Update [status](../status.md), [state](../../runtime/PROJECT_STATE.env), [checkpoints](../checkpoints/README.md), [roadmap](../roadmap.md) and relevant directory index together.
9. Run `python3 tools/check_repository.py` then commit and push on authorized branch. Do not force main.

**Mandatory desktop→Surface artifact transfer SOP:** [the proven V17–V19 SHA-verified procedure](DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md). Use its WSL→Windows staging, temporary LAN port 43157 HTTP server, direct Surface `Invoke-WebRequest`, hash verification, guarded COM9 and teardown. Do not invent new transfer methods during routine builds.

Historical Surface one-shot scripts may embed absolute machine paths or network endpoints; review scripts and use them only in correct machine context.

## Milestone-to-upstream integration gate (mandatory, 2026-10-27)

**Objective:** Keep the full BCM4329/Wi-Fi/Bluetooth/SDIO/board implementation continuously reviewable. Do not defer patch reconstruction until completion of a whole-chip feature. A successful experiment is *evidence*, not automatically an upstream patch or a qualification of unrelated source.

For **every materially new result** (positive or negative physical finding, validated source fix, clean-build/replay milestone, firmware/board interface discovery, or newly rejected hypothesis), close the work in the **same development session / same documentation change**:

1. **Checkpoint:** Write or update a dated, immutable `docs/checkpoints/` record with exact machine/DUT and kernel/source revision, firmware identity where publishable, build configuration, artifact hashes, commands/tests, measured results, negative controls, scope, rollback and unanswered questions. Keep sensitive raw logs private; link only sanitized evidence.
2. **Classify and route:** Assign the finding to one stable logical work-item ID and maintainer track (WIFI, BOARD/DT, BOOT/ARM, SDIO/MMC, PWR/regulator/clock/GPIO, BT, STORAGE/block, or internal INTEGRATION). Identify relevant source paths, maintainers/list/tree using the current target tree's `MAINTAINERS` and `scripts/get_maintainer.pl`; mark uncertain routing **OPEN**, not confirmed.
3. **Patch decision:** Record **revise existing canonical patch / add independent logical patch / prerequisite binding or subsystem change / lab-only / no source change / deferred** with a technical reason. Never use chronological Vxx lab iterations as upstream patch numbers. Preserve the prior immutable snapshot and relevant upstream examples. If implementation is mature enough, revise the original focused RFC member now (not a trailing experimental fixup), while preserving correct prefix-by-prefix bisection.
4. **Evidence gates:** Update each affected work item's G01–G12 status in [submission requirements](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md), distinguishing exact-source physical tests from V31/lab analogues, standalone compile, full build, static check, regression and maintainer review. An unchanged patch may legitimately remain **OPEN**.
5. **Integration:** Update the whole-chip dependency/interaction ledger (Wi-Fi↔SDIO↔PWR↔BT↔BOARD), the current clean-source replay/manifest references if a patch actually changed, and the next engineering gate. Maintain separate **upstream review series** for independent maintainer domains and an **internal complete-device integration sequence** with exact revisions and hashes.
6. **Discoverability and state:** In the same documentation commit, update `docs/checkpoints/README.md`, local subsystem indexes, `docs/README.md` where necessary, `docs/status.md`, `runtime/PROJECT_STATE.env`, and the relevant roadmap/handoff so the latest validated state is obvious. Resolve stale top-of-file "latest" banners instead of adding contradictory ones.

**Definition of milestone done:** evidence recorded; logical ownership assigned; canonical-patch decision recorded; acceptance gates and dependency matrix refreshed; living status/indexes aligned; repository checks run. An unresolved gate must remain explicitly open with a next test and owner track. Never block the factual checkpoint on an unfinished patch, but do not mark the integration/documentation task complete without recording why the patch is pending.

**Patch-release discipline:** A patch series is an independently versioned review product: one problem per patch, coherent multi-file changes permitted, genuine upstream commit messages, correct target base, buildable prefixes, review evidence, DCO handled solely by the human. Bindings precede code that consumes them; board DTS normally follows and routes through SoC maintainers. Work on the existing branch/worktree according to the one-writer rule, and never automatically send email, sign off, force-push, reflash, or install a test image during milestone bookkeeping.

**Standing references:** [canonical decomposition plan](../plans/MZ600_UPSTREAM_CANONICAL_PATCH_DECOMPOSITION_2026-10-27.md), [whole-chip integration ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md), [Wi-Fi RFC v2](../../patches/upstream/review-wifi-v2-20261028/README.md), [document authority](DOCUMENTATION_AUTHORITY.md), and [submission acceptance gates](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md).
