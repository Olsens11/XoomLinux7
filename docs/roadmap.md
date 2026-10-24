# Ordered roadmap

## G0 — canonical reproducible source and continuity
- [x] Establish XoomLinux7 GitHub repo, strict state/evidence docs, upstream reference.
- [ ] Complete final source/builder parity and source license review.
- [x] Register each machine's distinct SSH public **deploy key** with Write access; real create/delete test branch push passed on Desktop, Pi and Surface.
- [x] Verify local worktrees, GitHub fetch, independent push/delete permissions, and sync all machine worktrees with main.
- [ ] Add deterministic checks and release manifests for every accepted kernel image.

## G1 — validate v014 LIVE-LAB, no flash
- [ ] Temporary boot, verify USB protocol and RAM-only module workflows on replacement MZ600.
- [ ] Prove F2 timeout observability with recoverable Wi-Fi start/stop/retry.
- [ ] Export dated, scrubbed evidence; keep exact raw serial/device information privately.

## G2 — solve BCM4329 SDIO F2
- [ ] Compare driver/firmware/clock and power state against Motorola OEM flow.
- [ ] Test small attributable changes one at a time; no general MMC core hacks without reproducer.
- [ ] Confirm `wlan0`; only then pursue regulatory/per-device MAC and network association.

## G3 — native platform
- [ ] Controlled USB peripheral/host/OTG investigation.
- [ ] Charging/battery power_supply with CPCAP ADC fixes.
- [ ] Bluetooth and audio after core boot stability.
- [ ] Writable root filesystem, boot/install design **after** explicit authorization.

## G4 — useful OS and Windows 95
- [ ] Debian armhf root filesystem and network services.
- [ ] QEMU/alternative x86 Windows 95 emulation feasibility and preservation.
- [ ] NEON Lite instruction pretranslation/caching research kept as separate experiment.
