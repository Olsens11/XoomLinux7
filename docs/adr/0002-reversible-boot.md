# ADR 0002 — Temporary hardware qualification before installation
Date: 2026-10-23 (imported 2026-10-24). Status: ACCEPTED.

Use separate replacement MZ600 as native Linux DUT. Temporary `fastboot boot` only; preserve TWRP, Android partitions and original recovery-toolkit Xoom. Hash-check exact candidate before boot. Keep physical test logs, negative observations and verified fallback. Future persistent installation requires a new explicit approval, full rollback and readback plan.
