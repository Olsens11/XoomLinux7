> **SUBSEQUENT NINE-PATCH VALIDATION EVIDENCE, 2026-10-28:** [Formal source/build/hardware test](docs/checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md) and [three internal Wi-Fi issue reports](docs/bugs/README.md) supersede earlier inference that an SSID with “5G” meant a 5GHz radio. Actual association is **2.4GHz 2462MHz**; advertised 5GHz band absent. Preserve live COM9/Wi-Fi, no regulatory forcing or unattended scan/reload. Full patch lifecycle testing and human DCO still OPEN.

> **NEWEST DATED STATE SNAPSHOT AS OF 2026-10-28:** Begin with [docs/ACTIVE_TEST_STATE.md](docs/ACTIVE_TEST_STATE.md), then its linked dated checkpoints. This replaces older state labels below, **not** the safety/engineering rules. At every experiment, record hypothesis, exact source/firmware hashes, test commands, actual PASS/FAIL/OPEN evidence, rollback, and next one-variable discriminator; synchronize both runtime state files, indexes and [status](docs/status.md) in the same commit. Conversation memory is not evidence.

> **MANDATORY HISTORICAL-REUSE GATE (owner's standing rule, 2026-10-28):** **Before designing a solution for any newly observed issue, search this project's existing issue comments, dated physical checkpoints, failed experiments, code revisions, source builders, handoffs, OEM/Linux upstream examples and private measurement indices for a comparable problem and prior treatment.** Document which earlier methods worked, failed, or were deliberately abandoned; distinguish current exact source/firmware/hardware from old versions. **Adapt an established fix within an existing patch's logical scope where justified; don't add a new patch, repeat a consumed one-shot, or undo a later intentional decision merely because a prior workaround once passed.** Make a traceable evidence link in the current issue and checkpoint, then choose only the smallest new discriminator. See [mandatory lookback procedure](docs/process/DEVELOPMENT_WORKFLOW.md#mandatory-historical-reuse-gate-2026-10-28).

# XoomLinux7 agent operating contract

> **LATEST CONTINUITY (2026-10-28):** [Read comprehensive hardware fastboot + cold p8 verified handoff FIRST](docs/handoffs/MZ600_XOOMLINUX7_FASTBOOT_COLD_P8_VERIFIED_HANDOFF_2026-10-28.md). Direct hardware fastboot, Stage-B removable-root, physical cold unmounted p8 backup, SD full SHA, private pinned-TLS off-device Surface copy/full SHA and safe SD unmount **all PASS**; one-block ext4 free-space discrepancy remains, no restore tested, no flash. Older GPIO/PMC hang and no-cold-backup warnings below are historical, not current state. Maintain all original-device, privacy, kernel upstream and physical safety rules.

> **URGENT 2026-10-28 10:44 EDT PHYSICAL REBOOT TRIAL:** [Negative GPIO-unbind/PMC-only reboot result](docs/checkpoints/MZ600_GPIO_PMC_UNBIND_FASTBOOT_PHYSICAL_HANG_2026-10-28.md). Root-authorized one-shot GPIO reset driver unbind **physically PASS**, but no fastboot within 130 seconds, and Linux COM9/WLAN did not return. **The experimental replacement MZ600 is presently unreachable by remote software**. Do not attempt further reboot/flash, do not claim the experiment solved fastboot. Owner physical power/volume recovery required, followed by read-only verification. Original MZ600 remains protected; p8 cold backup still OPEN. All prior handoffs remain valid historic evidence.

> **CURRENT 2026-10-28 CHAPTER-BREAK CONTINUITY:** Read [the comprehensive preinstallation handoff](docs/handoffs/MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md) **before any device operation**. Actual installed Stage-D/V31 Debian is still the reference on p7/p8; new nine-patch kernel + firstboot rootfs are offline-built only. Most recent bootloader-mode reboot **failed to enter fastboot but returned to ordinary Linux**, and the rescue SD has an **armed, unexecuted one-shot cold p8 backup service**. Current TWRP 3.1.1-0 is non-BigPart and unsafe for casual mounts. No cold p8 snapshot or new installation/flash has occurred. The old v06.3 "current" paragraphs below are chronological history, **not** today's current system status. All hardware, privacy, DCO and upstream rules below remain binding.

> **CURRENT v06.3 verified 2026-10-25, 19:25 EDT:** Replacement MZ600 is running RAM-only Linux 7 with USB PONG, onboard BCM4329 detected, both radio stacks currently unloaded. This exact v06.3 image physically loaded the private Broadcom HCD patch path, registered hci0, completed HCI UP/DOWN, then loaded wlan0 and cleanly unloaded both stacks. Actual Wi-Fi scanning, Motorola Bluetooth keyboard pairing and a real terminal **are not yet implemented**. Next engineering contract: [v06.4 functional build instructions](docs/plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md) and [complete evolving handoff](docs/handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md). **All hardware safety, original-MZ600 protection, privacy and Linux upstream/DCO rules below remain binding.** All Oct24 current-state labels below are historical.


> **2026-10-25 continuity notice:** [Current comprehensive hardware/source handoff](docs/handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md) documents physically booted clean v06.2 with Wi-Fi wlan0, Bluetooth hci0 and sequential BT→Wi-Fi PASS. It supersedes the old Oct24 *version/status* labels below. **All original safety, device protection, privacy, provenance and upstream submission constraints remain fully in force.**

**Read this document first, then [START_HERE.md](START_HERE.md), [docs/status.md](docs/status.md), [runtime/PROJECT_STATE.env](runtime/PROJECT_STATE.env), [docs/README.md](docs/README.md), and the relevant hardware/architecture pages.**

## Authority and integrity
- Repository source, state ledger, immutable experiment records, and measured device results outrank recollections or a conversation summary.
- Separate **built**, **checksum verified**, **temporary-booted**, **diagnosed**, **network-connected**, **permanently installed**, and **fully qualified**. Do not conflate states or infer success from version numbers.
- At initial repository import, v013 was the hardware baseline. v014 then physically booted (USB and module lifecycle PASS, binary upload FAIL). v015 now physically qualifies raw USB transfer and module hot-reload; BCM4329 wlan0/F2 remains unresolved.
- A failed successor does **not** supersede the last successful test. Keep negative evidence and rejected hypotheses.
- Update docs/status.md and runtime/PROJECT_STATE.env **in the same change** as any new accepted state. Preserve dated checkpoint records.
- Cross-link documentation from docs/README.md and each applicable directory README; no undocumented orphan experiments.

## Hardware safety
- **Protected original MZ600:** the recovery-toolkit device is not a native-kernel experimental DUT.
- **Replacement MZ600:** diagnostic images use **temporary `fastboot boot <verified-image>` only**, after checking actual device identity and image SHA. Never flash partitions unless the user independently and explicitly authorizes a specific persistent write.
- Never execute `fastboot flash`, `dd of=/dev/block`, partition formatting, or bootloader relocking as a convenience.
- Preserve TWRP, original Android and partitions. Keep USB and powered-dock/battery issues in mind.
- Confirm which Xoom is attached every session; serials/unique MACs stay in private machine records.

## Privacy and publication
- GitHub repository is **public**. Never commit SSH private keys, tokens, passwords, SSIDs, real per-device MAC addresses, QR pairing credentials, OEM/private firmware, extracted partition images, proprietary vendor packages or unreviewed raw captures.
- Commit open upstream-derived DTS with proper SPDX/authorship; upstream Linux remains external and pinned, not copied wholesale.
- Public board NVRAM must remain **MAC-free and generic**, and cannot silently set a per-device regulatory identity.
- Do not enable Wi-Fi RF transmission before per-device identity, regulatory domain and calibration provenance are resolved.

## Engineering
- Upstream-first: generic drivers/subsystems, small board-specific DTS/driver changes, proper Linux interfaces; prefer device-tree descriptions over unconditional core-driver hacks.
- Maintain each experiment's hypothesis, exact source delta, reproducible build method, image SHA, physical evidence, and rollback.
- Need for diagnosis does not justify leaking secrets or permanently mutating tested partitions.
- v014 introduces RAM-only USB live module/firmware staging; an upload is **not** a successful module load or network test.
- Keep long-term Windows 95/QEMU work separate from native kernel/SDIO bring-up.
- Clean-room or license-respecting reference use: Motorola OEM/TWRP code is hardware evidence, not an automatic blanket license to republish binaries.

## Git and worktrees
- `main` is integrated, documented, and qualified state; independent changes on dedicated branches/worktrees (`wifi/*`, `usb/*`, `docs/*`, `hardware/*`).
- One writer per branch; branches can be checked out on different machines **only** with coordinated rebases/pushes. Never force push main.
- Every machine has its own SSH identity and host alias. GitHub write access is only confirmed after the key has been added as a **write-enabled** repository deploy key and a non-destructive push test succeeds.
- Use `scripts/resume-state.sh` and `python3 tools/check_repository.py` when starting work.
- Do not rewrite the upstream contributor's history. Provenance: [upstream source](https://github.com/xoom-linux/linux) at `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.

## Hardware acceptance refinement, 2026-10-24
Motorola supplied a **complete six-capability embedded SDIO override**. Previous v010–v013 fixes do not establish equivalent behavior; v017 measured actual mismatch. Never call Wi-Fi fixed until F2 ready + \`wlan0\` + correct MAC/regulatory identity + network stability are physically demonstrated, repeatedly. Compilation and kernel module init rc=0 do not establish Wi-Fi success.

## Current BCM4329 truth: 2026-10-24
v018 reproduced Motorola complete six-capability SDIO configuration and SD-HS timing on physical hardware but F2 stayed -62 twice. v019 changed ONLY the compiled diagnostic DTS SDMMC2 max-frequency cap and physically measured 25MHz, F2 still -62 twice. Both variants are unsuccessful Wi-Fi experiments; v015 remains accepted as RAM-only diagnostic infrastructure. Do not infer firmware CPU startup from a successful RAM download. See v018/v019 checkpoint links in docs/checkpoints/README.md.

## Runtime testing acceptance
The v020 RAM-only diagnostic environment is physically qualified for guarded MMC2 reinit and AUTO/MOTOROLA capability switching. It is not a Wi-Fi fix; no working wlan0. eMMC (mmc0) and unrelated mmc1 must never be unbound; never publish private firmware/MACs. Profile switches are pending until successful re-enumeration; check kernel trace.
