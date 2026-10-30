> **2026-10-30 I0 READY ARTIFACT STATUS:** [Detailed Surface V2 files and supervised TWRP installation sequence](I0_TWRP_DEPLOYMENT_READY_2026-10-30.md) now exists, all SHA checked (no device write). Owner physically enters TWRP; agent verifies live backup, installs ONLY new Debian autologin root, proves COM10/sudo/normal reboot, then separately qualifies recovery reboot and optional p8 selector. Avoid unnecessary p7/p8 writes. [Original offline evidence checkpoint](../../checkpoints/MZ604_I0_SURFACE_V2_DEPLOYMENT_OFFLINE_READY_2026-10-30.md).

> **2026-10-30 OWNER ACCESS REFINEMENT:** [Development-stage auth policy](../../process/DEVELOPMENT_AUTHENTICATION_POLICY_2026-10-30.md) now directs passwordless local COM10 access/sudo where possible; where a project login password cannot be avoided use `1234`. This is approved policy, **not yet a live device configuration**. Preserve no-bootloader-writes and physical-reset-accepted scope below.

# MZ604 practical remote test infrastructure — approved strategy (2026-10-30)

> **READ BEFORE ANY DEVICE BOOT, FLASH OR KERNEL EXPERIMENT.** This is INTERNAL DEVELOPMENT INFRASTRUCTURE, **not an upstream BCM4329 patch**, and it must not expand indefinitely. Follow [the current MZ604 RFC](README.md), [milestones](MILESTONES.md), [future-agent reading map](AGENT_READING_MAP.md), [project log](../../project-log/README.md), [project rules](../../process/DEVELOPMENT_WORKFLOW.md), and the October 30 [physical checkpoint](../../checkpoints/MZ604_PERSISTENT_LINUX_COM10_PHYSICAL_2026-10-30.md). All states below are **as of 2026-10-30**, not permanent.

## Owner decisions and stop limits

- Preserve **bootloader/EBB/BCT/GPT absolutely**. Do not modify them to implement reboot or A/B boot. Preserve **p6 TWRP 3.1.1-0** and its exact verified backup. The owner explicitly prefers the occasional need for physical restart to any risk of damaging the bootloader.
- Do **not** invest in an elaborate automatic crash-detection, bootloader-recovery or watchdog framework. A crash before USB initializes may require physical buttons; that is an accepted limitation. Never call kexec, p8 rescue or a compiled watchdog a guarantee of unattended recovery.
- Preserve current verified **p7 Linux7 + embedded initramfs + COM10 UDC Wingray DTB** as default. Do not routinely flash experimental kernels into p7. Use existing p8 boot-stage code and p10 loop-backed Debian images, with clear default/candidate selection and independently checked backups.
- On approved, privileged Linux, test standard **reboot** and later **recovery** semantics cautiously. The previous MZ600 GPIO/PMC unbind/reboot experiment did NOT produce fastboot and lost remote access; do not infer all `reboot bootloader`/`reboot recovery` requests are supported. First recovery-selection experiment must be physically supervised.
- Use **kexec only as a candidate** for alternative kernels after proving an identical known-good kernel/DTB/serial bootstrap and a physical reset fallback. `CONFIG_KEXEC=y` is BUILD evidence only; actual Tegra20 kexec is UNTESTED. If unreliable, stop and revise plan without modifying bootloader.
- Remote infrastructure is a **bounded prerequisite** for the BCM4329 RFC; when stable selection, access and rollback are sufficient, prioritize real MZ604 firmware/SDIO/cfg80211 evidence and minimal 2.4GHz upstream patch work.

## Verified as-of hardware and separation of concerns

MZ604 Wingray `xoom-wifi`, unlocked, bootloader 1050, previously returned Motorola `(00000008)` for two `fastboot boot` trials. Successful **owner-operated p7 flash** of separate USB-peripheral study boot candidate SHA256 `56741fcc04f83dd7fb7a7e794e9c5ec21a8a21348401bb686a2d4abc4741c6a2`, with `nvidia,tegra20-udc` + peripheral controller/PHY, produces Windows **COM10**. Early initramfs mounts p8; stage2 mounts p10 `/data/xoomlinux7/rootfs.ext4` and reaches Debian systemd login. The original p8 script's absolute-symlink `/newroot/sbin/init` check was corrected, backup `xoom-start.sh.pre-serial-fix` preserved; `serial-getty@ttyGS0` enabled in Debian. Linux root login is **NOT AUTHENTICATED**: original staged image's `/etc/shadow` records `root:!*` and `xoom:!` (deliberate unprovisioned accounts, as recorded in the 2026-10-29 baseline build document). **Do not claim Wi-Fi is broken or working:** actual MZ604 Linux BCM4329 SDIO/firmware/scan results have NOT been measured.

Read-only private backup locations/SHA and no-repartition contract: see [physical checkpoint](../../checkpoints/MZ604_PERSISTENT_LINUX_COM10_PHYSICAL_2026-10-30.md), and on the Surface `C:\Users\olsen\xoom-linux-rom\inspection\MZ604-LINUX7-INTERNAL-PHYSICAL-CHECKPOINT-20261030.md`. The latter is an earlier as-of checkpoint, so its initial "boot unverified" claim was superseded by the COM10 session.

## Proposed implementation and acceptance gates (not yet PASS)

**I0: Restore authorized access.** First read-only audit current serial host, TWRP return mechanism and exact installed rootfs identity. When physically supervised, enter TWRP without changing p6; back up live `/etc/shadow`/passwd/sudoers and validate the target loop image. Use the [owner's passwordless-first development convention](../../process/DEVELOPMENT_AUTHENTICATION_POLICY_2026-10-30.md): `xoom` auto-login on COM10 with passwordless sudo; fallback project login password `1234` only if required. Keep root locked and host/network service credentials separate. Boot known-good p7, independently authenticate over COM10 and record commands/outputs. A login prompt alone is NOT I0 PASS.

**I1: Normal reboot and recovery.** From authenticated Linux verify normal controlled reboot returns COM10 + privileged login. Study Tegra/Android bootloader recovery semantics from actual OEM/Linux sources; attempt Linux→TWRP recovery **only with owner physically available**. Verify TWRP ADB and return to unchanged normal Linux. Never claim fastboot/recovery selection until a **specific physical test** passes; never test by modifying EBB/BCT/p1.

**I2: p8 root selector.** Keep stable default Debian image; stage separate experimental Debian image(s) as ordinary files in p10 only after checking free space, ext4 integrity and provenance. Minimal p8 selector reads a short validated configuration, verifies path is within allowlist, independent hash/size, filesystem and `/sbin/init` target, chooses either default, one-shot candidate, or p8 rescue, and otherwise fails to known-good rescue. No bootloader, GPT or p6 modifications. Preserve USB serial in every environment; verify every root source at runtime and after reboot.

**I3: one-shot trial + logs.** Small versioned metadata record stores default, pending one-shot trial, and explicit test-result receipt. A one-shot selection must be consumed **before** transferring into a candidate, so on a **subsequent ordinary boot** default is selected. This is NOT automatic recovery from a kernel hang. Logs on Surface and local storage should include candidate SHA/source/DTB/firmware, trial ID, port, kernel, boot/heartbeat, root image, test command rc and revert state. No SSID/MAC/credentials in public output. Reuse the existing canonical SHA-checked Desktop→Surface transport SOP, not an ad hoc file server.

**I4: alternative kernel, optional.** Investigate installed kexec-tools and exact Tegra20 reboot implementation; validate same-kernel kexec while user can physically reset. If PASS, use explicitly paired zImage+appended DTB and matched modules via one-shot tests from stable p7, with serial reconnect and rollback evidence. Do not assume BSS cleanup/USB/SDIO state after kexec is equivalent to cold boot. Always run an independent cold boot before claiming upstream reproducibility. If FAIL, do not expand into custom bootloader code.

**I5: finish infrastructure and STOP.** Demonstrate at least 2 repeatable select→stage→boot→test→return cycles for default/rescue/alternate root, same-kernel case as supported, and verified recovery selection where available. A kernel crash requiring physical reset is allowed; document limitation. Then freeze infrastructure except for blocking defects and resume W1-W6.

## I0 access-recovery readiness

Offline 2026-10-30 12:05 EDT staged-root read-only proof **PASS**: image SHA matched, root/xoom locked, xoom not in sudo group. See [supervised account recovery runbook](I0_ACCOUNT_RECOVERY_RUNBOOK_2026-10-30.md). Live account provisioning and authenticated COM10 remain OPEN; **no device operation occurred**.

## Current immediate execution sequence

1. **Today, read-only:** verify host COM10, candidate/backup SHA, stage initramfs and kernel config, account locks and TWRP recovery path; no reboot while owner is away.
2. Prepare/review TWRP [I0 account-provisioning procedure](I0_ACCOUNT_RECOVERY_RUNBOOK_2026-10-30.md) **offline only** (USB autologin + sudo NOPASSWD, fallback `1234` where necessary; never overwrite a rootfs without current backup/identity). Do not execute before safe physical access.
3. On physically supervised session: restore privileged serial login, test normal reboot, then test recovery reboot as separate gated experiments.
4. Implement minimal root selector in an isolated offline fixture, run fail-closed/path traversal/missing-image tests, then deploy only after approved backup.
5. Test optional kexec only if the above is stable. Collect true Wingray upstream BCM4329 baseline, not MZ600 inferred results.

**Stop / rollback:** Any unexpected SHA, identity ambiguity, corrupt filesystem, COM10 loss, failed recovery, nonmatching modules, unexpected regulatory behavior or an existing safety-tool denial stops that test. Do not evade blocked commands. The owner may physically reboot; restore p7/p8 from independently verified backups through TWRP when explicitly approved. Keep original TWRP p6 and original partitions intact.

## Minimal Wi-Fi upstream work stays unchanged

W0 pinned untouched upstream source complete; W1 real Wingray board/firmware/SDIO baseline is open; W2 measure legacy `chanspecs` ABI before any fallback; W3 enforce truthful 2.4GHz RF/regulatory intersection and no unverified 5GHz TX; W4 3 fresh ordinary scans and smallest required event/up-state fixes only if physically reproduced; W5 WPA2/DHCP/data/reconnect/reboot with exact source; W6 review-ready one-logical-issue-per-patch RFC, user-owned DCO/submission. Older MZ600 r7/nine-patch work and DT common-refactor are evidence, not default cherry-picks. No speculative Bluetooth/FM, cellular or crash-recovery scope.
