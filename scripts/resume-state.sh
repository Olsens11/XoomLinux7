#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo '=== XoomLinux7 project state ==='
cat "$root/runtime/PROJECT_STATE.env"
echo '=== Git ==='
git -C "$root" status --short
git -C "$root" branch -vv
git -C "$root" worktree list
echo '=== Next ==='
echo 'Read START_HERE.md, docs/status.md and docs/hardware/WIFI_BCM4329.md'
