# ADR 0003 — Git authority, per-machine worktrees and write identities
Date: 2026-10-24. Status: ACCEPTED.

Establish public Olsens11/XoomLinux7 as canonical integration/source/documentation project. Pin external contributor kernel at a commit; do not vendor massive Linux tree into main. Use distinct machine-local branches/worktrees for builder, hardware console and research. Per-machine separate GitHub write-enabled deploy keys (never put private keys in Git). Last tested evidence is distinct from last built candidate, and documentation check is required for state promotion.
