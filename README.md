# XoomLinux7 — Motorola Xoom native Linux

**Experimental, upstream-first ARMv7 Linux bring-up for the Motorola Xoom (MZ600 Stingray / MZ604 Wingray).**

This repository is the **canonical integration and engineering record** for our Linux 7.0 development. It builds on [xoom-linux/linux](https://github.com/xoom-linux/linux), not a replacement or an unattributed copy of that kernel. The original working kernel snapshot was commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (2026-06-12).

> **Current hardware authority (2026-10-24):** v014 USB temporary boot and Broadcom module load/unload **physically verified**; F2 timeout and binary USB upload remain unresolved. v015 raw-serial live-lab **physically qualified** for USB transfer and Broadcom hot-reload; Wi-Fi still has the BCM4329 F2 timeout and no wlan0. BCM4329 Wi-Fi enumerates and loads firmware but its SDIO Function 2 fails readiness (`-62` timeout). **No confirmed working native Linux Wi-Fi connection yet.**

## Start here

1. [AGENTS.md](AGENTS.md) — agent onboarding, authority and safety rules
2. [START_HERE.md](START_HERE.md) — next-session resumption
3. [docs/status.md](docs/status.md) — verified current status
4. [docs/README.md](docs/README.md) — documentation router
5. [docs/architecture/UPSTREAM_POLICY.md](docs/architecture/UPSTREAM_POLICY.md) — architecture and upstream provenance
6. [docs/hardware/WIFI_BCM4329.md](docs/hardware/WIFI_BCM4329.md) — diagnosed Wi-Fi fault
7. [docs/checkpoints/README.md](docs/checkpoints/README.md) — v01–v14 evidence and qualification
8. [docs/roadmap.md](docs/roadmap.md) — next actions

## Top-level organization

- `src/` — our original diagnostic PID1 code and **board-specific derivative** source, not an entire vendored Linux kernel
- `scripts/` — reproducible build, packaging, staging and diagnostic scripts
- `configs/` — kernel configurations and public MAC-free board settings
- `docs/` — current state, architecture, hardware, history, process and decisions
- `evidence/` — reviewed public test evidence and manifests; device-specific raw captures stay private
- `runtime/` — machine-readable project-state and authority declarations
- `patches/` — focused upstream kernel changes, when generated and verified
- `releases/` — release manifests only; large binaries in GitHub Releases or private artifact storage
- `tools/` — source tooling and local validation

## Non-destructive development

Test kernels through **`fastboot boot` on the replacement test MZ600 only**. Never flash BOOT, SYSTEM, USERDATA or RECOVERY as part of the diagnostic workflow. The original Xoom recovery-project tablet remains protected. Never commit private SSH keys, Wi-Fi credentials, per-unit MAC/calibration, OEM firmware, raw partition dumps, commercial binaries, or credentials.

**Important:** The unmodified upstream source is fetched from its own repository at the exact pinned commit. Our source/config/scripts are versioned independently to keep a manageable, attribution-correct history.

## Provenance

Upstream kernel: https://github.com/xoom-linux/linux ; Linux GPL-2.0-family licensing applies as appropriate to kernel-derived source. This integration repo retains authorship and licenses and does not claim upstream author's work as ours.
