# Contributing and development continuity

This is an experimental open-source hardware project; preserve upstream Linux authorship and GPL requirements. Discuss scope and reproducibility before broad driver refactors.

For each change provide: objective, baseline commit and exact inputs, board(s), change list, build/test commands, image hash if produced, diagnostics and failure modes, resulting verification level, affected docs/state, and tested rollback path.

Use topic branches and isolated worktrees. No direct unreviewed changes to the verified baseline. Never mislabel offline tests as physical tests. No secrets, vendor-only binaries, per-device MAC/NVRAM, tokens, firmware dumps or large generated kernel trees in Git.

Read [docs/process/DOCUMENTATION_AUTHORITY.md](docs/process/DOCUMENTATION_AUTHORITY.md) and [docs/process/DEVELOPMENT_WORKFLOW.md](docs/process/DEVELOPMENT_WORKFLOW.md).
