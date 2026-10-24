# START HERE — XoomLinux7

This is the **session handoff**, not a historical narrative. Begin with [AGENTS.md](AGENTS.md).

1. Read [docs/status.md](docs/status.md) and [runtime/PROJECT_STATE.env](runtime/PROJECT_STATE.env).
2. Read [docs/README.md](docs/README.md) for the subsystem map.
3. Review [docs/checkpoints/README.md](docs/checkpoints/README.md) for last actual hardware results.
4. Check [docs/hardware/WIFI_BCM4329.md](docs/hardware/WIFI_BCM4329.md) if working on SDIO/F2.
5. Check [docs/architecture/UPSTREAM_POLICY.md](docs/architecture/UPSTREAM_POLICY.md) for source authority.
6. On each machine, run `scripts/resume-state.sh` then `python3 tools/check_repository.py` and inspect `git status --short`, `git branch -vv`, `git worktree list`.
7. Resolve current DUT identity, USB status, and user approval **before** any hardware command.

**Current next action:** v015 raw USB/upload/hot-reload infrastructure is physically verified on the replacement MZ600. Investigate BCM4329 F2 readiness via scoped uploaded modules and OEM reference. No wlan0, no permanent writes.

**Do not assume:** a kernel build is a boot test; an SDIO card is a functional wlan0; an embedded firmware file is legally redistributable; a branch has write access because a public clone succeeded.

Historical original source: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Our maintainable integration lives here.
