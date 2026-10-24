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

Historical Surface one-shot scripts may embed absolute machine paths or network endpoints; review scripts and use them only in correct machine context.
