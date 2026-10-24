# XoomLinux7 agent operating contract

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
