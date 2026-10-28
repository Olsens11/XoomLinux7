> **SUBSEQUENT WIFI VALIDATION AND ISSUE TRIAGE (2026-10-28):** [Formal exact-nine-patch review and physical backend audit](checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md), [internal issue ledger](bugs/README.md). Verified installed `brcmfmac` / WCC SHA equals exact clean nine-source build. Current radio **2.4GHz 2462MHz** (previous 5GHz inferred solely from SSID), 5GHz PHY band absent. Connection/downloads PASS; scan callbacks/regulatory/station metrics and alternate Xoom regressions OPEN. Historical entries below remain as-of snapshots.

> **ENGINEERING STATUS SNAPSHOT AS OF 2026-10-28:** [Living active test record](ACTIVE_TEST_STATE.md) and [physical Bluetooth A/B checkpoint](checkpoints/MZ600_REVIEW9_P10_RECOVERY_SURFACE_OEM_BLUETOOTH_FIRMWARE_AB_2026-10-28.md). Native p10 Linux, 5GHz NetworkManager association, COM9, on-LCD VT2 passed; generic HCD HCI initialized but Bluetooth discovery/bonding failed; OEM HCD clock/reset timeout reproduced then rolled back; radio OFF and Wi-Fi intact. Older states below are historical. Record every new hardware experiment before updating conclusions.

> **LATEST PHYSICAL MILESTONE — 2026-10-28: NINE-PATCH LINUX 7 + FULL BOOKWORM P10 BOOT PASS.** [First live exact-review kernel USB COM9 login proof, all 1GiB p10 Debian filesystem hashes and TWRP fsck, temporary fastboot boot only](checkpoints/MZ600_NINE_REVIEW_LINUX7_P10_BOOKWORM_FIRST_PHYSICAL_BOOT_PASS_2026-10-28.md). The 1GiB new Debian filesystem is installed in **p10** (remaining p10 unexpanded); p7 original V31 and p8 working fallback **untouched**, p6 TWRP BigPart retained. Actual COM9 `xoom-mz600 login:` verified; **logged-in uname, new BigPart runtime geometry, Wi-Fi/BT/modules remain OPEN**. Older notes claiming nine-review Linux not booted or p10 empty are historical. Next use owner credential for serial login and run non-destructive runtime checks.

> **LATEST PHYSICAL MILESTONE — 2026-10-28:** [Original TWRP 2.8.6.0 BigPart successfully written to MZ600 p6 only, exact SHA readback and independent reboot into installed recovery PASS; eMMC p8/p9/p10 BigPart sector mapping and root ADB PASS, Debian p8 read-only ext4 mount PASS](checkpoints/MZ600_TWRP_286_BIGPART_P6_INSTALL_AND_PERSISTENT_BOOT_PASS_2026-10-28.md). Old p6 rollback safely retained; clean nine-patch Linux and new Debian NOT installed. Next: disposable p8 cold-image restore/fsck rehearsal, then temporary nine-patch exact-source boot. Internal RW mounting/repair/backup-restore untested; recovery automatically mounts rescue SD RW, later remounted RO.

> **CURRENT COMPREHENSIVE HANDOFF 2026-10-28:** [Fastboot, Stage-B cold p8 on SD and Surface verified, kernel patches, Debian, recovery architecture, and ordered next steps](handoffs/MZ600_XOOMLINUX7_FASTBOOT_COLD_P8_VERIFIED_HANDOFF_2026-10-28.md). Next: **offline disposable ext4 fsck/restore test**, then BigPart-aware TWRP 3.1.1-0 RAM boot. No flash.

> **LATEST 2026-10-28 VERIFIED OFF-DEVICE COLD BACKUP:** [The full 1GiB unmounted internal-p8 cold image was SHA256-reverified on rescue microSD, pinned-TLS copied to Surface, then independently rehashed on Surface; all metadata saved and rescue SD unmounted RO](checkpoints/MZ600_COLD_P8_OFFLINE_IMAGE_VERIFICATION_2026-10-28.md). One-block ext4 free-count mismatch noted; no perfect-clean fsck or test restore yet. No device flash.

> **PRIOR 2026-10-28 FASTBOOT AND SD COLD BACKUP:** [Hardware-button fastboot confirmed; exact Stage-B `fastboot boot` PASS, SD-root Debian and unmounted p8 confirmed; cold backup reached SHA comparison; normal internal Debian COM9/WLAN recovered; backup RESULT.txt not yet read](checkpoints/MZ600_STAGEB_FASTBOOT_COLD_P8_CAPTURE_PENDING_RESULT_2026-10-28.md). Do not flash until verified cold copy + restore.

> **HISTORICAL 2026-10-28 — NO-FASTBOOT/NO-LINUX AFTER GPIO-UNBIND (NOW RECOVERED):** [Root-authorized single one-shot hardware A/B negative result, precise timestamps, host observations, remaining recovery gates](checkpoints/MZ600_GPIO_PMC_UNBIND_FASTBOOT_PHYSICAL_HANG_2026-10-28.md). Live GPIO restart driver unbound successfully, no fastboot in 130 seconds; no COM9 or Wi-Fi returned. **Physical rescue required.** No flash, backup or new Linux deployment.

> **2026-10-28 GPIO/PMC LIVE MZ600 PREFLIGHT PASS:** [Unprivileged COM9 login restored; read-only live kernel bindings and BigPart geometry confirmed; SHA-pinned RAM-only script on-tablet preflight PASS](checkpoints/MZ600_REBOOT_GPIO_PMC_LIVE_UNPRIVILEGED_PREFLIGHT_PASS_2026-10-28.md). Root-only GPIO unbind remains blocked by sudo authentication; **no reboot/flash or cold p8 backup**.

> **2026-10-28 GPIO/PMC REBOOT ROOT-CAUSE CANDIDATE:** [Xoom gpio-restart priority 200 outranks Tegra PMC −128](checkpoints/MZ600_FASTBOOT_REBOOT_GPIO_PRIORITY_ROOT_CAUSE_CANDIDATE_2026-10-28.md). Prepared [reversible, root-authorized, dry-run-first GPIO unbind test](../scripts/experiments/mz600-gpio-restart-bypass-20261028.sh). Confirmed in source, **not yet physically retested**; COM9 is at login after earlier normal-Linux reboot and noninteractive SSH authentication denied. No driver unbind, flash or reboot this session.

> **CURRENT COMPREHENSIVE HANDOFF — NEW INSTALLATION CHAPTER, 2026-10-28:** [Exact MZ600 stopping point, decisions, live baseline, nine-patch build, all image variants/backups, rescue-SD automation, TWRP 3.1.1-0, failed fastboot trial, phased gates and next-session instructions](handoffs/MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md). **Read this first;** newest negative physical test did not reach fastboot, no cold p8 image or new boot/flash exists.

> **2026-10-28 SOFTWARE BOOTLOADER REBOOT PHYSICAL TEST:** [Actual guarded MZ600 reboot-to-fastboot attempt](checkpoints/MZ600_REBOOT2_BOOTLOADER_PHYSICAL_NORMAL_LINUX_FALLBACK_2026-10-28.md): ARM reboot(2) requested bootloader, COM9 dropped, but **no fastboot device appeared for 120s**. The Xoom returned to ordinary Linux (network ping and COM9 login confirmed). Rescue microSD has an armed one-shot cold-p8 agent; **not triggered**, no flash or cold backup. Hold further reboot-mode trials until semantics understood.

 > **2026-10-28 REMOTE NO-BUTTON FASTBOOT/RECOVERY PATH:** [Software-requested Tegra PMC reboot mode, Stage-B cold-p8 backup and recovery rollback plan](plans/MZ600_REMOTE_NO_BUTTON_FASTBOOT_COLD_BACKUP_RECOVERY_2026-10-28.md): Linux7 source confirms reboot(2) `bootloader`/`recovery` mode support; Surface COM9 root, SD presence and two SHA-pinned proven images confirmed read-only. The separate physical trial above showed reboot-to-bootloader was **not honored**; this entry documents the earlier source-only plan.

> **2026-10-28 TWRP 3.1.1-0 BIGPART RECOVERY AUDIT:** [Exact installed p6 Android boot image / ramdisk forensic audit and BigPart 3.1.1-0 build gates](checkpoints/MZ600_TWRP_3110_BIGPART_BASELINE_AUDIT_2026-10-28.md): existing 3.1.1-0 recovery backup is verified twice, 431 CPIO entries inspected, factory-fstab and obsolete legacy mount suffixes identified; available 2020 3.1.1 Xoom release explicitly says noBigPart. **Retain 3.1.1-0 UI**, produce and RAM-boot/test a Stingray-safe BigPart kernel with correct p8/p9/p10, then consider only p6 write after cold backup and rollback verification. No flash.

> **2026-10-28 ONE-GIB BIGPART TEST ROOT PASS:** [Shrink/verify and safe recovery roadmap](checkpoints/MZ600_ONE_GIB_ROOT_AND_BIGPART_RECOVERY_PLAN_2026-10-28.md): exact nine-review Debian test filesystem successfully copied and shrunk from nominal 2GiB to **1GiB**, 5-pass offline ext4 fsck PASS, 456MiB free, SHA `9cf413dcf1305e3dbabc13dc2d478ad5d481bfb4da2260cee1de16a59f9c6d31`. No 'SuperBigPart' layout needed for this image. Historic BigPart-enabled TWRP candidates are Wingray-specific and NOT yet validated on MZ600; first get cold p8 backup by **verified temporary Stage-B BigPart microSD boot** with internal p8 unmounted, then test compatible recovery using `fastboot boot` before any p6 flash. No device changes.

> **2026-10-28 PREFLASH V31 BACKUP + DISPOSABLE DEBIAN IMAGE:** [Current verified backup/build milestone](checkpoints/MZ600_V31_PREFLASH_PRESERVATION_AND_TEST_ROOT_2026-10-28.md): eight private raw image captures on the Surface including original p7/p8/p9, eMMC boot areas, first64MiB and GPT-containing tail independently SHA256-rehashed; OEM GPT CRC passes. Separate Bookworm armhf image fully assembled with 41 signed packages, NetworkManager/nmtui, timesyncd, ping, private MZ600 firmware, 114 review-matched modules, owner-chosen temporary root password and exclusive Wi-Fi services. 2GiB ext4 test image `b7180b88...` fsck PASS, intended **for separate test media, NEVER the installed 1GiB p8**. Live MZ600 framebuffer LVDS/tty1 confirmed. **Cold unmounted p8 backup, independent restore check, spare media and new-image physical boot are HARD GATES; no flash or device reboot.**

> **2026-10-28 FIRST-BOOT CONNECTIVITY + CONSOLE KIT (OS TRACK):** [First-boot package sources](../packaging/firstboot/README.md), [manifest](../packaging/firstboot/manifest.json), [dated checkpoint](checkpoints/MZ600_FIRSTBOOT_WIFI_COM9_SCREEN_KIT_2026-10-28.md) and [Windows COM9 launcher](../scripts/host/windows/Start-Xoom-USB-Console.ps1). The final kit has 41 signed Debian Bookworm armhf packages, NetworkManager/nmtui, ping, curl, timesyncd, private firmware separation, tty1 framebuffer login and ttyGS0/COM9 rescue. Packages, 114 matched modules, and owner-selected temporary root password are installed in a separate 2GiB ext4 test image (offline fsck and SHA256 PASS), **not** the installed MZ600. On-screen interactive typing, physical new-image boot and Wi-Fi hardware tests remain OPEN. No kernel patch change.

> **2026-10-28 INSTALLED KERNEL COMPARISON:** [Stage-D physical kernel vs nine-patch source audit](checkpoints/MZ600_STAGE_D_INSTALLED_VS_NINE_PATCH_REVIEW_2026-10-28.md) confirms identical kernel .config and 7.0.0-next-20260422+ release; 2 compiled DTB differences (model, removed BigPart opt-in); 14,030 common Module.symvers entries but **three changed Broadcom CRCs**. The working Stage-D/Stage-B kernel has no embedded initramfs, same as review; earlier Stage-A config is a different artifact. New source requires separate private boot image with `gpt xoom_bigpart=1` and source-matched modules. No tablet change.

> **2026-10-28 STORAGE-01 FOCUSED RFC:** [Standalone unsigned BigPart storage patch](../patches/upstream/review-storage-bigpart-20261028/README.md) now uses native Tegra alternate-GPT discovery and a strictly opt-in in-memory p8/p9/p10 layout. [New checkpoint](checkpoints/MZ600_STORAGE_BIGPART_SUBMISSION_FORM_RFC_2026-10-28.md) records physical evidence versus untested cleaned source, standalone enabled ARM object PASS, seven geometry/literal tests PASS, and separate nine-patch source tip `507eb069df819cb5cc801ad8be096f70d9ca7609`. The initial nine-patch draft fully built; after a fail-closed geometry guard refinement, the separate fresh full ARM `zImage dtbs modules` build of this exact revised source has **PASSED** (2026-10-28 08:34:59 UTC; sha256-pinned in integration manifest); no device changes, DCO or submission. The new review source requires **`gpt xoom_bigpart=1`** on a specially prepared future test boot; unmodified live tablet image has not been changed.

> **2026-10-28 COPY-AWARE TEGRA RFC:** [The three-commit DT review](../patches/upstream/review-stingray-dt-20261028/README.md) now uses `git format-patch -C` to represent the 99% reused Wingray hardware content faithfully; all 418 earlier inherited checkpatch errors are eliminated without a hardware source change. Remaining 2 generic MAINTAINERS-file warnings and DT schema/runtime gates are documented. [New eight-patch integration source tip](../patches/upstream/INTEGRATION_SOURCE_MANIFEST_20261028.json): `abd3ebc8a7684243b6e7920704dff0f080aa84f3`, fully replayed and source-equivalent to previous eight-tip. Fresh full ARM `zImage`/DTBs/modules build **PASS**, exit 0, on exact source `abd3ebc8...`; all five principal artifacts are SHA256-pinned in the integration manifest.

> **2026-10-28 REVIEW SOURCE INTEGRATION MANIFEST:** [Exact eight-commit integrated source](../patches/upstream/INTEGRATION_SOURCE_MANIFEST_20261028.json) cleanly replayed from the pinned base, combining 3 DT + 1 ARM + 4 Wi-Fi canonical unsigned RFCs; same source is the intended next build-test baseline, not yet equivalent to complete MZ600 BigPart/p8 boot. Human submission stays on hold.

> **2026-10-28 ARM MAC/ATAG RFC:** [Standalone unsigned ARM/Tegra bootloader MAC review patch](../patches/upstream/review-arm-atag-20261028/README.md) now complements the clean Wi-Fi and board DT sources. Source-only replay and strict checkpatch 0/0/0 pass; standalone ARM zImage build **PASS** (SHA256 `b5abb9a830b1830b6931eacc45868d76e3449adc96f99ad7f5fa924ac99fdb6c`); hardware and ATAG bounds/correctness review still OPEN. [Routing](../patches/upstream/REVIEW_TRACKS_20261028.md). This RFC is not merged into the seven-patch full-source QA yet.

> **2026-10-28 SUBMISSION-FORM SOURCE BASELINE (NOT MAILED):** [Per-maintainer review tracks](../patches/upstream/REVIEW_TRACKS_20261028.md), [review-form source replay checkpoint](checkpoints/MZ600_UPSTREAM_REVIEW_FORM_SOURCE_REPLAY_2026-10-28.md), [four-logical Wi-Fi RFC](../patches/upstream/review-wifi-four-logical-20261028/README.md), [three-commit Stingray DT RFC](../patches/upstream/review-stingray-dt-20261028/README.md) and [repeatable clean replay tool](../scripts/qa_replay_upstream_review.sh) now track work during development. Four Wi-Fi cumulative module prefixes compiled independently; independent DTBs reproduced byte-for-byte; full ARM `zImage`/DTBs/matched modules **PASS** on unchanged-source retry after a recorded GCC internal compiler error. Old broad four-patch candidate is a historical integration snapshot, **not an upstream submission series**. BOOT/MAC, BigPart, PM/SDIO, BT, clean-source hardware testing and human review are open; nothing posted or flashed.

> **ACTIVE PROCESS RULE — milestone-to-upstream integration (2026-10-27):** Every significant hardware/source discovery must be checkpointed, assigned a maintainer/work-item track, assessed against the canonical focused upstream patch, linked into the whole-chip dependency ledger, and reflected in the acceptance gates and project state **as part of the milestone**. See [mandatory workflow](process/DEVELOPMENT_WORKFLOW.md#milestone-to-upstream-integration-gate-mandatory-2026-10-27), [document authority](process/DOCUMENTATION_AUTHORITY.md), [work-item decomposition](plans/MZ600_UPSTREAM_CANONICAL_PATCH_DECOMPOSITION_2026-10-27.md), and [submission gates](../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md). The older four-patch candidate series below is **historical source-integration evidence**, not the current source-review set; [four-logical Wi-Fi RFC](../patches/upstream/review-wifi-four-logical-20261028/README.md) is the current focused review (the [three-patch Wi-Fi v2](../patches/upstream/review-wifi-v2-20261028/README.md) is a source-equivalent earlier alternative). No submission or hardware test of that clean RFC is implied.

> **HISTORICAL SOURCE SNAPSHOT (2026-10-27, SUPERSEDED FOR REVIEW):** [`patches/upstream/candidate/series`](../patches/upstream/candidate/series) and [candidate README](../patches/upstream/candidate/README.md) preserve the older broad four-change integration baseline. Its original source-apply evidence remains valid for that snapshot, but its patch boundaries are **not** the canonical upstream review tracks. Use the [maintainer-routing registry](../patches/upstream/REVIEW_TRACKS_20261028.md) and the new focused DT/Wi-Fi/ARM series for ongoing source updates.

> **LATEST 2026-10-27 V24:** [Real Event69 generation-checked first scan physically passed; successive-scans gate still open](checkpoints/MZ600_V24_GENERATION_CHECK_FIRST_SCAN_PASS_TWO_SCAN_GATE_OPEN_2026-10-27.md). The BCM4329 firmware returned newly assigned sync ID 4661, Linux accepted genuine terminal even with `bsscfgidx=16`, and completed cfg80211 scan with three BSS. Second request in the same module lifetime was blocked (`Operation not permitted (-1)`) before another generation; not yet solved. Matched companion module and controlled RAM overlay proven, all original files verified restored. **V24 is lab evidence, not a production patch.** Older V23 next-step text historical.

---

> **LATEST 2026-10-27 — LEGACY BCM4329 ESCAN TRANSACTION IDs VERIFIED:** [V23 host-chosen 0x1235/0x1236 firmware echo physical checkpoint](checkpoints/MZ600_V23_ALTERNATE_ESCAN_SYNC_IDS_FIRMWARE_ECHO_PHYSICAL_PASS_2026-10-27.md). Both real Event69 SUCCESS IDs matched Linux request, both invalid-index events were correctly delivered by V21 lab fallback, 3 userspace BSS in 1.8/1.7s, watchdog-free, final original runtime check PASS. Earlier [V22b 0x1234 echo](checkpoints/MZ600_V22B_TERMINAL_SYNC_ID_ECHO_PHYSICAL_PASS_2026-10-27.md). Production per-scan generation/race/multiif correctness remains OPEN; only tested lab module, no firmware or persistent installation change. Consult [design RFC](research/MZ600_V21_TO_UPSTREAM_EVENT69_COMPLETION_MODEL_2026-10-27.md).

---

> **LATEST 2026-10-27 V21 SCAN COMPLETION PROOF:** [V21 six-trial Event69 terminal-owner physical checkpoint](checkpoints/MZ600_V21_TERMINAL_OWNER_LAB_SWITCH_AB_PHYSICAL_PASS_2026-10-27.md). Two genuine firmware success events with unresolved interface indices **were delivered through an enabled lab-only terminal-owner correction** and produced normal Linux cfg80211 scan completion and 3 BSS each. One OFF negative control timed out. All original runtime rollback checks PASS. This is a proven lab mechanism, **not an upstream-ready patch**. Use [canonical cross-host transfer SOP](process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md).

# Documentation router

> **2026-10-27 CANONICAL CROSS-COMPUTER PROCEDURE:** [Desktop → Surface → Xoom standard SHA-verified artifact transfer](process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md), derived from verified V17–V19 commands; use for all further module tests. Related [development workflow](process/DEVELOPMENT_WORKFLOW.md).

> **START HERE — OCT 26 TRANSITION:** [Complete current XoomLinux7 engineering handoff](handoffs/MZ600_LINUX7_FULL_TRANSITION_HANDOFF_2026-10-26.md) with proven persistent eMMC Debian, partition/boot SHA, private backup map, upstream Wi-Fi/BT history, exact module build and safe gzip uploader, failed xz install, COM9 blocker, remaining tasks and next-chat runbook. Earlier handoff final paragraphs may be outdated.


> **Latest 2026-10-26:** [ABI-exact 114 Linux7 Stage-D modules built and offline-verified, Surface archive SHA256 identical to Desktop; USB RAM staging awaits release of COM9 from the existing console](checkpoints/MZ600_V064_STAGE_D_ABI_MODULES_OFFLINE_QA_USB_UPLOAD_WAITING_COM9_2026-10-26.md). Persistent internal Debian remains byte-verified; no modules deployed yet.


> **Latest 2026-10-26 — FULL VERIFIED INSTALLATION:** [Persistent internal Debian 12.15 boots normally on replacement MZ600, p7 flash confirmed byte-for-byte by physical 6,645,760B SHA and complete 8MiB SHA, running root is `/dev/mmcblk0p8 ext4 /`](checkpoints/MZ600_V064_STAGE_D_PERSISTENT_P7_FULL_PHYSICAL_SHA_VERIFIED_2026-10-26.md). All persistent-boot verification gates PASS; remaining Wi-Fi/modules and systemd work is separate.


> **LATEST 2026-10-26:** [Persistent internal Debian achieved: native CMD Stage-D flash boot p7 passed and normal reboot started Debian 12.15 from eMMC `/dev/mmcblk0p8 ext4 /`](checkpoints/MZ600_V064_STAGE_D_PERSISTENT_P7_FLASH_PREFLIGHT_STAGED_2026-10-26.md). Postflash p7 raw SHA verification awaits owner local sudo; microSD Stage-B image and OEM/TWRP backups retained separately.


> **LATEST 2026-10-26:** [Stage-D repeat temporary fastboot boot PASS: Debian 12.15 runs from internal p8, but the kernel-reported p8 GPT PARTUUID differs from previous Stage-D and failed Stage-E image. Internal root fstab now stale again; stable ext4 UUID available. No persistent flash](checkpoints/MZ600_V064_STAGE_D_RETEST_P8_GPT_PARTUUID_CHANGES_ACROSS_BOOTS_2026-10-26.md).


> **2026-10-26 latest diagnostic:** [Stage-E corrected live p8 GPT PARTUUID temporary boot fails to reach Debian login (COM9 timeout); exact root-identifier problem unresolved, no persistent flash](checkpoints/MZ600_V064_STAGE_E_LIVE_GUID_TEMPBOOT_UNRESPONSIVE_2026-10-26.md). Stage-D direct-device internal p8 Debian boot proven, persistent Stage-B microSD rescue untouched. Next obtain stalled framebuffer evidence and recover normal SD boot.


> **2026-10-26 latest Stage-E preparation:** [On currently working Stage-D internal-root Debian, original `/etc/fstab` backed up and corrected to live GPT p8 PARTUUID with complete one-line-only readback proof](checkpoints/MZ600_V064_STAGE_E_FSTAB_LIVE_P8_GUID_CORRECTED_2026-10-26.md). Stage-E internal p8 PARTUUID candidate remains TEMP-boot-only, not tested or flashed. Persistent p7 microSD Debian rescue intact.


> **2026-10-26 native internal Debian breakthrough:** [Stage-D temporary `fastboot boot` produces actual Debian 12.15 running from `/dev/mmcblk0p8 ext4 /`, verified by USB login and `findmnt`](checkpoints/MZ600_V064_STAGE_D_INTERNAL_P8_DEVNODE_BOOT_PHYSICAL_PASS_2026-10-26.md). Current root on internal eMMC p8 while p7 persistent Debian SD fallback remains intact. Old saved PARTUUID mismatched current kernel GPT; Stage-E with verified live PARTUUID prepared offline, NOT booted/flash. Next fix internal `/etc/fstab` after owner sudo, then test Stage-E TEMP only.


> **CURRENT SAFETY HOLD 2026-10-26:** [Stage-C internal BigPart p8 root temporary boot accepted by fastboot but did not reach usable Debian login; COM9 became unresponsive](checkpoints/MZ600_V064_STAGE_C_INTERNAL_P8_TEMPBOOT_NO_LOGIN_2026-10-26.md). Persistent p7 Debian microSD rescue remains flashed and verified; owner can recover by physical reset and normal boot with card inserted. Do not permanently flash Stage-C until root mount verified.


> **2026-10-26 NEW INTERNAL DEBIAN MILESTONE:** [BigPart internal p8 1GiB Debian root installed from microSD with correct internal fstab, ext4 offline fsck exit0; **internal root has NOT yet booted**](checkpoints/MZ600_V064_BIGPART_INTERNAL_DEBIAN_P8_FILESYSTEM_INSTALLED_FSCK_PASS_2026-10-26.md). Owner-repaired physical volume button permits fastboot/recovery. Next test Stage-C by temporary `fastboot boot`, and separately repair kernel/modules release/vermagic mismatch. Keep verified p7 microSD recovery boot.


> **2026-10-26 HARDWARE UPDATE:** [Experimental replacement MZ600 charging jack and volume button have been repaired; physical fastboot and recovery access confirmed by owner](checkpoints/MZ600_REPLACEMENT_HARDWARE_REPAIR_VERIFIED_BY_OWNER_2026-10-26.md). Historical notes saying the buttons are broken are obsolete. Independent software `reboot bootloader` still needs separate work; persistent Debian-on-SD boot and p7 readback pass remain valid.


> **2026-10-26 confirmed milestone:** [Persistent Linux7 Debian SD-root boot accepted, ordinary boot tested, then on-device p7 readback SHA verified exact Stage-B image match](checkpoints/MZ600_V064_PERSISTENT_P7_PHYSICAL_READBACK_SHA_PASS_2026-10-26.md). Current replacement tablet running persistent Debian from SD; p8 BigPart 1GiB still unformatted. Next: verify Android-independent recovery before destructive internal install.


> **2026-10-26 milestone:** [Persistent p7 Stage-B Linux7 Debian microSD boot successfully flashes and boots with normal fastboot reboot, normal Debian USB console](checkpoints/MZ600_V064_PERSISTENT_SD_DEBIAN_BOOT_PHYSICAL_PASS_2026-10-26.md). Current Debian on inserted SD. Independent read-after-write hash of p7 needs owner's local `sudo -s`; do not erase p8 before confirming and testing recovery.


> **SAFETY HOLD (2026-10-26):** [Independent Linux-to-fastboot reboot did not work; first persistent p7 boot flash status is unknown after native stderr/PowerShell interruption](checkpoints/MZ600_LINUX7_RESCUE_BOOTLOADER_AND_P7_FLASH_AMBIGUITY_2026-10-26.md). Xoom safely temporarily rebooted into Debian from SD. First verify raw p7 read-only SHA before any retry or p8 formatting.


> **LATEST 2026-10-26:** [Real Debian 12.15 microSD-root successfully boots with Linux 7 Classic BigPart 1GiB p8 and guarded installer passes complete read-only preflight](checkpoints/MZ600_V064_BIGPART_DEBIAN_SDRoot_PHYSICAL_PASS_INSTALL_PREFLIGHT_2026-10-26.md). Current live device stage-B Debian on SD, no partition/boot flash yet. Stage C p8-root boot prepared offline but NOT booted. Next: secure owner sudo in USB console and validate recovery independent of Android before erasing p8.


**LATEST offline candidate:** [BigPart-aware Debian microSD-root stage-B boot image hash-verified across Desktop and Surface](checkpoints/MZ600_V064_BIGPART_DEBIAN_MICROSD_INSTALLER_STAGE_B_OFFLINE_2026-10-25.md). Needs reinserted same 32GB installed Debian microSD for physical normal shell test; no format or flash.


**LATEST:** [Physical v064 original Xoom BigPart geometry PASS](checkpoints/MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md), replacement MZ600 now runs temporary BigPart-aware Linux7; stock TWRP remains 256MiB system view. No persistent writes yet.


> **NEW CURRENT LIVE PHYSICAL STATE (Oct25 20:47 EDT):** [Relocated OEM GPT physically verified from TWRP via 64-bit ARM read-only probe](checkpoints/MZ600_BIGPART_TWRP_PHYSICAL_GPT_LLSEEK_PROOF_2026-10-25.md). Current device is TWRP 3.1.1-0/root ADB, not v06.3 Linux. [Stage-A isolated BigPart kernel builder](../scripts/experiments/stage-v064-bigpart-gpt-readonly-20261025.py) running on Desktop. No BigPart partition writes.


> **Current approved storage target — CLASSIC XOOM BIGPART p8 `system` Linux root:** [implementation + hardware safety gates](plans/MZ600_V064_CLASSIC_BIGPART_SYSTEM_ROOT_IMPLEMENTATION_2026-10-25.md). The earlier p10-root proposal is superseded; no userdata backup is required by user's explicit decision. Host layout proof PASS only; no eMMC changes or boot image yet.


> **NEW storage design decision:** [2026-10-25 internal eMMC p10 Debian root / optional BigPart plan](plans/MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md). User accepts replacing Android on experimental replacement MZ600 if needed, but no partition has been modified. p10 is large enough without BigPart, pending backup and Linux7 native TegraPT visibility.


> **New v06.4 engineering checkpoint:** [offline ARMHF dependency-closure and packing preflight](checkpoints/MZ600_V064_ARMHF_PACKAGING_PREFLIGHT_OFFLINE_2026-10-25.md). The preflight script ran on Desktop WSL; no new image or physical feature pass yet.


> **CURRENT project authority — Oct 25, 2026:** [Comprehensive v06.3 physical-results handoff](handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md), [dated v06.3 hardware PASS](checkpoints/MZ600_V063_PHYSICAL_PASS_HCD_HCI_AND_BLUETOOTH_TO_WIFI_2026-10-25.md), [canonical current machine state](../runtime/CURRENT_LINUX7_STATE.env) and [v06.4 mandatory functional build instructions](plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md). **v06.3 is PHYSICALLY booted and HCD/HCI and sequential Wi-Fi validated; iw is only OFFLINE-STAGED; no actual scan, keyboard pairing, or usable terminal.** Older v015/v020/F2 evidence is historical.



**Canonical CURRENT authority:** [complete handoff](handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md) + [unique-key live state](../runtime/CURRENT_LINUX7_STATE.env) + [human-readable status](status.md); [legacy historical ledger](../runtime/PROJECT_STATE.env) retains older trial values and is not an unqualified current-state reference.

## Project and decisions
- [Project purpose and goals](PROJECT_INTENT.md)
- [Roadmap](roadmap.md)
- [Architecture and upstream provenance](architecture/UPSTREAM_POLICY.md)
- [Board platform and separation of concerns](architecture/PLATFORM.md)
- [Decision log](adr/README.md)

## Engineering / hardware
- [BCM4329 Wi-Fi, SDIO F2 fault and v014 plan](hardware/WIFI_BCM4329.md)
- [Target devices and preservation](hardware/DEVICES.md)
- [Native diagnostics and USB command interface](hardware/USB_DIAGNOSTICS.md)
- [Build, stage and temporary boot](process/DEVELOPMENT_WORKFLOW.md)
- [Source/artifact location map](reference/SOURCE_MAP.md)
- [Git worktrees and machine write keys](process/WORKTREES_AND_KEYS.md)

## Evidence and continuity
- [Chronological v01–v14 checkpoint index](checkpoints/README.md)
- [Verified device GitHub write access (2026-10-24)](checkpoints/GIT_ACCESS_2026-10-24.md)
- [Documentation authority and supersession rules](process/DOCUMENTATION_AUTHORITY.md)
- [Evidence and publishing rules](process/EVIDENCE_AND_PRIVACY.md)
- [Current state](status.md)
- [Machine-readable current state](../runtime/PROJECT_STATE.env)

When a new record is added, link it here and from its local index; update status ONLY when verified evidence changes.

- [v014 USB module hardware test and binary transfer fault](checkpoints/V014_USB_LAB_2026-10-24.md)

- [v015 physical raw USB and module hot-reload qualification](checkpoints/V015_RAW_USB_LAB_2026-10-24.md)

## BCM4329 current research
- [Motorola and Broadcom source comparison](research/MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md)
- [Controlled F2 experimental test matrix](research/BCM4329_F2_TEST_MATRIX.md)
- [v016 physical IOEx/IORx/clock snapshot](checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md)

- [v017 measured raw CCCR and parsed capabilities](checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md)

- [v018 complete Motorola six-field override: effective, but F2 still fails](checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md)

- [v019 25 MHz SDMMC2 control: actual host rate confirmed; F2 still fails](checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md)

- [On-demand SDMMC2 capability profiles and safe re-enumeration design](architecture/MMC2_ON_DEMAND_DESIGN.md) — proposed, not yet implemented.
- [Supplementary v018 recheck and actual host-clock discrepancy](checkpoints/V018_RECHECK_2026-10-24.md).

- [v020 physical no-reboot MMC2 capability profile acceptance](checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md).

- [v020 additional 6,662,144-byte hardware image and repeat MMC2 on-demand test](checkpoints/V020_ADDITIONAL_BUILD_AND_REINIT_2026-10-24.md).

- [v021 OEM firmware A/B and LPO/clock hypothesis](checkpoints/V021_OEM_FW_AND_LPO_HYPOTHESIS_2026-10-24.md): three physical F2 trials all -62; read-only clock observer built but not loaded.

- [BCM4329 full datasheet and Section 11 review](research/BCM4329_DATASHEET_SECTION11_REVIEW_2026-10-24.md): legacy SDIO clock <=25MHz, VDDC settled+110ms, pull-ups, SPI-vs-SDIO distinction.

- [v022 actual 25 MHz legacy SDIO three-trial physical result](checkpoints/V022_AUTO_LEGACY_25MHZ_PHYSICAL_2026-10-24.md): specification met, F2 still -62.

- [v021 actual LPO clock-provider measurement](checkpoints/V021_LPO_CLOCK_PHYSICAL_2026-10-24.md): software enabled 32768Hz; F2 -62 persists.

- [v025 verified 100 ms host pre-reset delay — 3 physical F2 trials](checkpoints/V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md).

- [Virtual Linux 7 forensic lab v1](research/VIRTUAL_FORENSIC_LAB_V1_2026-10-24.md): actual v025 image, two ARM/QEMU consumers, firmware/NVRAM audit, seven negative tests.

- [v026 actual runtime firmware and NVRAM provenance hardware test](checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md): generic source selection, CRC32 match, unavailable platform MAC, F2 still -62.

- [Broadcom BCM4329 complete 149-page datasheet index](research/BCM4329_DATASHEET_PAGE_INDEX.md), [36-requirement source and physical audit](research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md), and [cross-subsystem fault tree](research/BCM4329_CROSS_SUBSYSTEM_FAULT_TREE.md).

- [BCM4329 whole-chip power coordinator design](research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md): OEM shared power reference counts, two Linux consumers, resource ownership and rollback.

- [v028 read-only Bluetooth/WLAN controller register test](checkpoints/V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md) and [v029 disabled whole-chip coordinator compiled prototype](checkpoints/V029_BCM4329_SHARED_OWNER_COMPILE_ONLY_2026-10-24.md).

- [v030 Motorola Bluetooth shared-regulator and passive-reset compile-only work](checkpoints/V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md), with source patch and private DT test.

- [v031 live UART/BT binding and clock provenance](checkpoints/V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) and [v032 corrected Bluetooth LPO description](checkpoints/V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md).

- v033 Bluetooth USB-controlled temporary boot candidate: see checkpoints/V033_BLUETOOTH_USB_LAB_2026-10-24.md.

- v034 physical HCI device-down correction: checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md; v033 kernel, DTB, BT/Wi-Fi modules frozen.

- [Original MZ600 HRI39/HRI66 Wi-Fi driver and OEM-to-Linux 7 F2 audit](research/MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md) — matching-generation 2.6.36 OEM source compared against pinned Linux 7 CM3/PMU/clock/F2 startup; 27/27 offline source and ELF checks, no hardware modification.

- [BCM4329 OEM v5 firmware/PMU evidence](research/MZ600_BCM4329_V5_FIRMWARE_PMU_CM3_EVIDENCE_PLAN.md): tested read-only firmware version metadata, protected calibration differences, current USB state and next Cortex-M3/PMU observation gates.

- [v035 BCM4329 PMU/CM3/F2 read-only physical test](checkpoints/V035_BCM4329_PMU_CM3_F2_PHYSICAL_2026-10-24.md): 3 RAM-module trials established a chip PMUControl transition after CM3 release on first load and stable retained PMUControl on warm driver reloads; F2 remains -62.

- [v036 BCM4329B1 PMU resource physical checkpoint](checkpoints/V036_BCM4329_PMU_RESOURCE_CLOCK_PHYSICAL_2026-10-24.md) — OEM-specific resource-state decoding confirms ALP/HT and regulator/PLL resource votes, no pending, yet F2 remains -62 in two trials.

- [v037 SDPCM mailbox verified before persistent F2 timeout](checkpoints/V037_SDPCM_MAILBOX_WRITE_PHYSICAL_2026-10-24.md) — v4 firmware mailbox SDIO write rc=0, now focus on internal WLAN CPU firmware readiness and RAM handoff.

- [v038 on-chip ARM release and NVRAM token physically proven](checkpoints/V038_BCM4329_CM3_NVRAM_HANDOFF_PHYSICAL_2026-10-24.md); [v039 2011 Motorola firmware single-variable physical test](checkpoints/V039_ORIGINAL_MZ600_FIRMWARE_PHYSICAL_2026-10-24.md) also fails F2 and verified generic firmware rollback. Research branch only.

- [v040 authoritative Motorola MAC bootstrap and protected per-device provenance](research/V040_MOTOROLA_MAC_BOOTSTRAP_ATAG_PROVENANCE.md): candidate missing `macaddr` requirement, OEM bootloader ATAG MAC, current Linux ATAG kernel configuration; lab NVRAM override refused by host guard and not physically tested.

- [v038 MMC2 runtime-PM awake result](checkpoints/V038_MMC2_RUNTIME_PM_HOLD_PHYSICAL_2026-10-24.md) / [v039 original MZ600 firmware result](checkpoints/V039_ORIGINAL_MZ600_FW_PHYSICAL_2026-10-24.md) — two additional controlled, reversible, physically verified negative F2 results and exact generic firmware rollback.

- [BCM4329 supply transient / buffering research](research/MZ600_BCM4329_STARTUP_RAIL_DROOP_AUDIT_2026-10-24.md) — distinguish real 3.3 V, CPCAP VWLAN1 and internal 1.25 V from DTS regulators, plan scoped transient measurement before choosing decoupling additions; no physical experiment yet.

- [v040/v041 CM3 and SDPCM shared-header physical test](checkpoints/V040_V041_CM3_NVRAM_SHARED_STRUCTURE_PHYSICAL_2026-10-24.md) — firmware runs far enough to publish a version-3 shared header and console pointer, while F2 still times out.

- [v042–v045 first native BCM4329 wlan0 physically demonstrated](checkpoints/V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md) — recovered firmware console initialization error 21, proved stock bootstrap MAC unblocks F2, linked upstream WCC for experimental wlan0, safe identity-free rollback verified.

- [Native MZ600 installed-OS workstream](os/NATIVE_OS_INTEGRATION_2026-10-24.md) — staged Debian Bookworm armhf rootfs, clean kernel and factory-MAC ATAG→FDT patch, USB ttyGS0 login, standard upstream brcmfmac/WCC modules; **not flashed or hardware-verified yet**. See dedicated `os/mz600-native-rootfs-wifi-20261024` branch.

- [Native installed-OS offline build PASS checkpoint](checkpoints/NATIVE_OS_OFFLINE_BUILD_PASS_2026-10-24.md) — exact images/hashes/QA and no-flash boundary. [Future xoom-linux upstream handoff draft](os/UPSTREAM_CONTRIBUTION_DRAFT.md) (not sent).

- **[Start here: BCM4329 native WLAN breakthrough and comprehensive milestone](checkpoints/BCM4329_BREAKTHROUGH_AND_NATIVE_OS_MILESTONE_2026-10-24.md)** — definitive history, evidence, physical WLAN0 proof, current safe state, clean OS and Android-preservation decisions.
- [Android-preserving Linux root and boot artifacts — offline PASS](checkpoints/ANDROID_PRESERVING_NATIVE_OS_OFFLINE_REBUILD_2026-10-24.md) — `xoom-linux` dedicated root target, SHA-reverified images, no device writes, reversible Android requirement.

- [Native Linux installation preflight and Android rollback backups (2026-10-25)](checkpoints/NATIVE_OS_INSTALL_RECOVERY_PREFLIGHT_2026-10-25.md) — real 10-partition eMMC map, private off-device images, TegraPT warning; staged Linux remains uninstalled.

- [MicroSD Linux root target — physical media inspection and verified offline build](checkpoints/MICROSD_ROOT_OFFLINE_PREFLIGHT_2026-10-25.md) — microSD detected as independent mmcblk1; no writes or Android modification. Root ext4 installation requires media erase approval.

- **[MicroSD native Debian installation succeeded; first boot not yet qualified](checkpoints/MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md)** — complete physical SD layout and integrity, bootloader temp boot evidence, no Android flash, USB/boot remains unresolved.

- **[New milestone: real Debian 12 boots on MZ600 microSD with USB console and native BCM4329 wlan0](checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md)** — systemd, verified factory-MAC FDT/interface match, separate WCC module; no RF association yet.
