# Ordered roadmap

## G0 — canonical reproducible source and continuity
- [x] Establish XoomLinux7 GitHub repo, strict state/evidence docs, upstream reference.
- [ ] Complete final source/builder parity and source license review.
- [x] Register each machine's distinct SSH public **deploy key** with Write access; real create/delete test branch push passed on Desktop, Pi and Surface.
- [x] Verify local worktrees, GitHub fetch, independent push/delete permissions, and sync all machine worktrees with main.
- [ ] Add deterministic checks and release manifests for every accepted kernel image.

## G1 — validate v014 LIVE-LAB, no flash
- [x] v014 temporary boot, USB protocol, and Broadcom start/stop passed; binary transfer failed and v015 corrective candidate built.
- [x] v015 RAM-only USB and module start/stop/retry transport qualified; F2 timeout persists and has an actionable live-lab reproduction path.
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

## F2 disciplined path (new 2026-10-24)
- [x] v016 live read-only F2 register instrumentation and physical evidence; F2 still fails.
- [x] Research Motorola complete six-field embedded SDIO setup and Broadcom firmware handshake; identify why v010-v013 do not fully reproduce OEM.
- [ ] Capture raw CCCR and final parsed card capabilities and host timing before any new SDIO capability patch.
- [ ] Compare valid same-device OEM firmware and NVRAM privately.
- [ ] Perform cold/warm baseline and one-change-at-a-time Motorola equivalent with observed effective fields.
- [ ] Qualify IORx bit 2, stable wlan0, regulatory/MAC identity, repeated network operation before declaring fixed.

- [x] Read-only v017 raw CCCR, effective mmc_cccr fields and host ios captured on real replacement MZ600.
- [ ] Produce complete Motorola six-capability equivalent in appropriately scoped modern SDIO initialization, with actual post-override field+timing measurements and no unrelated clock or calibration changes.
- [ ] Separate legacy clock-only control to test 46.15MHz versus conservative rate, if OEM-equivalent test alone cannot isolate failure.

- [x] Full Motorola six-field OEM-equivalent modern MMC override physically tested (v018): parsed fields and SD-HS mode actually corrected, F2 failed twice.
- [x] v019 controlled clock-only comparison: same OEM six-field patch, cap SDMMC2 at 25MHz, measure effective speed and F2 state.
- [ ] If still failing, prioritize firmware CPU/startup, 32k reference, and private same-device NVRAM/firmware provenance before more arbitrary quirk changes.

- [x] v019 controlled clock-only comparison physically tested; effective host clock 25,000,000Hz, F2 still timed out on two trials.
- [ ] Prioritize read-only BCM4329 firmware CPU/SDPCM startup checks and exact same-device OEM firmware + NVRAM provenance; no further MMC tweaks without specific evidence.

## On-demand SDIO test architecture
- [x] Identify actual Wi-Fi MMC2 platform device `c8000200.mmc` and Linux driver bind/unbind surfaces via existing read-only USB SDIO tool.
- [ ] Add board-scoped runtime capability profile and safe USB MMC2-only reinit controls, **requiring one further experimental temporary-boot diagnostic candidate**.
- [ ] Validate no-change controller rebind, clean removal/re-enumeration, effective capability changes, rollback and no impact to eMMC/USB; do not mark available until real hardware testing passes.
- [ ] Then vary capability, clock, reset, matched firmware/NVRAM one at a time without whole-kernel reboot, with cold-boot control runs.

## v020 on-demand controller integration
- [x] Implement and test root-only Stingray BCM4329 SDIO AUTO/MOTOROLA runtime profile.
- [x] Implement and test MMC2_STATUS, MMC2_PROFILE, MMC2_REINIT with USB command allowlists.
- [x] Demonstrate AUTO to MOTOROLA to AUTO card removal/re-enumeration, verified effective capabilities, with NO kernel reboot.
- [x] Refuse reinit when Broadcom drivers loaded; host waits for terminal response.
- [ ] Test recovery under deliberately failed bind/re-enumeration and compare card reinit to actual chip power cycle.
- [ ] Extend independent clock profile safely after no-change controls; continue firmware CPU/SDPCM and matched OEM calibration research.
