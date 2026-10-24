# ADR 0001 — Upstream-first thin board integration
Date: 2026-10-23 (imported 2026-10-24). Status: ACCEPTED.

Use xoom-linux/linux and ordinary Linux subsystems as the implementation base. Prefer a small Stingray device tree and tightly scoped, upstream-friendly quirks over a Broadcom driver fork or blanket MMC changes. Learn from old Motorola/TWRP implementations without copying their licensing assumptions or per-device calibration. Core Linux portability, SoC reusability and actual per-device radio identity are nonnegotiable. Existing F2 experiments remain probes until physically proven and reviewed.
