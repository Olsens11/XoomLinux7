> **2026-10-28 INSTALLED VS REVIEW BUILD AUDIT:** [Actual Stage-D/Stage-B versus nine-patch review kernel comparison](MZ600_STAGE_D_INSTALLED_VS_NINE_PATCH_REVIEW_2026-10-28.md): identical .config and release; only two compiled Stingray DTB property differences; 14,030 common exports with three Wi-Fi CRC changes; observed V31 hardware networking is distinct from untested clean source. Old Stage-A embedded-firmware config is NOT the persistent Stage-D source. No device access or deployment.

> **2026-10-28 STORAGE-01 RFC:** [Focused BigPart source/physical-evidence distinction and test record](MZ600_STORAGE_BIGPART_SUBMISSION_FORM_RFC_2026-10-28.md), plus [separate block/partitions unsigned patch](../../patches/upstream/review-storage-bigpart-20261028/README.md). Native Tegra GPT support confirmed; explicit new opt-in, source QA, geometry tests, outstanding mainline design and exact-source hardware gates are preserved.

> **2026-10-28 BOOT-01 SOURCE REVIEW:** [Unsigned one-patch ARM MAC/ATAG RFC](../../patches/upstream/review-arm-atag-20261028/README.md) isolated from Broadcom and BigPart, checkpatch 0/0/0 and verified patch-stream SHA. Independent ARM source compilation and physical testing remain separate gates; see [review-form checkpoint](MZ600_UPSTREAM_REVIEW_FORM_SOURCE_REPLAY_2026-10-28.md).

> **2026-10-28 REVIEW SOURCE REPLAY:** [Submission-form three-DT + four-Wi-Fi source checkpoint](MZ600_UPSTREAM_REVIEW_FORM_SOURCE_REPLAY_2026-10-28.md) records exact source provenance, four independent Wi-Fi prefix compiles, byte-identical reviewed DTBs, inherited DTS formatting blocker and a successful unchanged-source full ARM build retry after a recorded GCC ICE. This is not a physical tablet milestone or final submission. [Per-maintainer registry](../../patches/upstream/REVIEW_TRACKS_20261028.md).

> **LATEST 2026-10-26 OEM WIFI SCAN WIRE FORMAT: [Original HRI39 Broadcom firmware physically returns WLC_SCAN_RESULTS ioctl51 rc0, buflen12, version108, count0 from read-only no-scan query; 5GHz firmware channels confirmed, all temporary images removed and independent original hashes verified](MZ600_V064_MOTOROLA_HRI39_LEGACY_SCAN_RESULTS_VERSION108_READONLY_PHYSICAL_PASS_2026-10-26.md). **No real passive scan or populated BSS record yet.** The [upstream-shaped scanner contract plan](../research/MZ600_BCM4329_LEGACY_SCAN_UPSTREAM_PROTOCOL_IMPLEMENTATION_2026-10-26.md) remains open.


> **LATEST MZ600 2026-10-26 5GHz:** [Original Motorola 4.218.248.20 and guarded 217 legacy valid-channel fallback physically **created native dual-band `wlan0`**; 9 firmware-supported 5GHz channels all `NO_IR`; first passive scan exposed DIFFERENT legacy `escan=-52` unsupported; strict WCC-first teardown and original Debian rollback independently verified](MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md). Keep lab path distinct from whole-chip pwrseq patch, do not misreport scan as successful.



> **2026-10-26 5GHZ PHYSICAL NEGATIVE FINDING:** [Android 5GHz supported per owner's same-unit experience, but Linux7 native BCM4329 PHY advertises only 2.4GHz; dynamic phy2 5GHz entries=0, 5GHz scan skipped; NVRAM aa5g=1, 5GHz PA entries; driver teardown and USB healthy](MZ600_V064_5GHZ_BAND_NOT_ADVERTISED_PASSIVE_SCAN_BLOCKED_PHYSICAL_2026-10-26.md). Pin source `cfg80211.c` obtains bandlist from firmware; actual bandlist **not** read yet. Use existing [149-page Broadcom index](../research/BCM4329_DATASHEET_PAGE_INDEX.md) and OEM firmware references, not forced 5GHz channels or regulatory overrides.
# Diagnostic checkpoint ledger — v01 through v014


> **LATEST EARLY OEM BT/WLAN CODE 2026-10-26:** [Replaced earlier 42-check source coverage with 51/51 exact 2a65edc original Motorola Bluetooth RFKill+Wi-Fi+original ELF static gates PASS; BT initial BLOCK shares untyped U4 with WLAN, possible startup-order hazard; no observed runtime issue](MZ600_OEM_2A65EDC_BLUETOOTH_WLAN_SHARED_U4_51CHECK_SOURCE_AUDIT_2026-10-26.md). Exact earlier 42/42 remains valid intermediate proof; new [source auditor](../../tools/forensics/audit_mz600_oem_system_lifecycle.py) includes early BT pin, LPM and rfkill call graph. Whole-chip provider not deployed.



> **2026-10-26 OEM SOURCE+SHIPPING ELF VERIFIED:** [Exact early MZ600 HRI39 2.6.36.3 Motorola board+Broadcom source, compiled startup power/carddetect branch, OEM six-cap workaround, matching SDMMC2 tap=6, DHD warm reset, early suspend — 42/42 SHA-pinned source+ELF checks PASS](MZ600_OEM_2A65EDC_CROSSLAYER_SOURCE_BINARY_CONDITIONAL_AUDIT_42_PASS_2026-10-26.md). [Reusable static audit tool](../../tools/forensics/audit_mz600_oem_system_lifecycle.py). Important: OEM generic WLAN_POWER_ON is NOT double power vote under CUSTOMER_HW2; matching-generation BT source still partial. No live hardware altered.



> **LATEST 2026-10-26 5GHz FIRMWARE PROOF:** [One-run RAM-only brcmfmac diagnostic exact ABI; firmware GET_BANDLIST count=1 2.4GHz-only, chanspecs 11x2GHz/0x5GHz, wiphy no5G; clean unload and original boot p7/hash preserved](MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md). Not a 5GHz enablement fix, not a deployed whole-chip provider. Compare OEM firmware/NVRAM/regulatory data next; do not force unsupported channels. Lab patch source [0002](../patches/lab/0002-brcmfmac-log-firmware-bandlist-and-chanspec-band-counts.patch).


> **LATEST MZ600 WI-FI PHYSICAL 2026-10-26:** [Normal persistent Debian p8 BCM4329 wlan0 PRESENT / iface UP / passive 2.4GHz scan exit0 with 19 BSS / driver firmware v4.220.48 / WCC-first clean teardown / USB+D-Bus maintained / p7 checksum unchanged](MZ600_V064_PERSISTENT_DEBIAN_BCM4329_WLAN0_PASSIVE_SCAN_AND_ORDERED_TEARDOWN_PHYSICAL_PASS_2026-10-26.md). Two scan results tagged 2442 MHz despite explicit scan frequencies 2412/2437/2462; causal explanation not yet proven. **The experimental whole-chip pwrseq patch series is still NOT deployed or physically qualified**; don't conflate.

> **CURRENT USERSpace MILESTONE 2026-10-26:** [Six Debian Bookworm D-Bus packages hash-matched, RAM-only USB transferred, physically dpkg-installed, systemd D-Bus socket/daemon active and real ListNames RPC PASS; WLAN/WPA still failed and not restarted](MZ600_V064_DEBIAN_DBUS_OFFLINE_SIX_PACKAGE_INSTALL_SYSTEM_BUS_PHYSICAL_PASS_2026-10-26.md). BCM4329 patch series tracked separately in [whole-chip integration ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md) and [multi-device release gate plan](../plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md).

> **2026-10-26 POST-INSTALL PHYSICAL READ-ONLY:** [SDIO 3 functions, onboard Wi-Fi firmware and six-byte factory FDT MAC verified; PID1 systemd degraded, WLAN unit previously failed missing WCC, WPA failed missing system D-Bus socket; no radio activation](MZ600_V064_POST_MODULE_INSTALL_READONLY_SDIO_WIFI_SYSTEMD_FORENSICS_2026-10-26.md).

> **CURRENT 2026-10-26 PHYSICAL INSTALL PASS:** [114 ABI-matched `.ko` modules safely extracted to new versioned Debian p8 module tree; atomic move, depmod and `modprobe -n` dry-runs PASS; independent Xoom re-count verifies 114 and legacy tree intact](MZ600_V064_114_ABI_MODULES_INTERNAL_P8_ATOMIC_INSTALL_PHYSICAL_PASS_2026-10-26.md). No radio load, scan or association yet; earlier install-pending statements are historical.

> **Latest remote attempt, 2026-10-26:** [Unattended installation not executed: COM9 held by existing owner console, second serial client rejected, unmanaged console cannot accept Desktop Commander input](MZ600_V064_UNATTENDED_INSTALL_COM9_CONSOLE_EXCLUSIVE_2026-10-26.md). No new tablet writes; prior SAFE gzip RAM receipt still PASS.

> **2026-10-26 install script STAGED, not run:** [Guarded ABI-114 gzip on-device installer passes offline Bash syntax and awaits user-owned root console; transfer to RAM is already SHA-verified](MZ600_V064_GZIP_MODULE_INSTALLER_OFFLINE_STAGED_OWNER_CONSOLE_PENDING_2026-10-26.md).

> **2026-10-26 PHYSICAL SUCCESS:** [SAFE gzip 114-matching-module archive uploaded to Xoom RAM, SHA256 verified ON the device, sender exit0; no module install yet](MZ600_V064_SAFE_GZIP_RAM_UPLOAD_PHYSICAL_SHA_PASS_2026-10-26.md). This supersedes prior COM9-busy transfer blockers; next step is guarded p8 module tree install after owner-console verification.

> **2026-10-26 resumed continuation:** [New host revalidation checkpoint: exact SAFE gzip and uploader hashes PASS, 501-entry repo validator PASS, COM9 still held, new gzip upload/install NOT VERIFIED](MZ600_V064_NEXTCHAT_SURFACE_REVALIDATION_SAFE_GZIP_COM9_STILL_HELD_2026-10-26.md). The next physical action remains owner Ctrl+] in Surface USB console (no reboot), then guarded RAM-only upload and post-upload p8 module install.

> **NEXT-CHAT START:** [Master October 26 full continuity handoff](../handoffs/MZ600_LINUX7_FULL_TRANSITION_HANDOFF_2026-10-26.md) integrates persistent eMMC boot, Wi-Fi/BT experiments, exact module build and the missing xz / SAFE gzip ready checkpoint. Follow the new master handoff before using any older “pending” statements.


> **Latest 2026-10-26:** [Post-interruption host recovery and Stage-D 114 matching-module offline QA PASS; verified Surface transfer, COM9 exclusive serial console blocks RAM upload; no Xoom modules installed or loaded](MZ600_V064_STAGE_D_ABI_MODULES_OFFLINE_QA_USB_UPLOAD_WAITING_COM9_2026-10-26.md). Press Ctrl+] in Surface Xoom terminal to release COM9 before next USB transfer.


> **LATEST 2026-10-26 — COMPLETE:** [Permanent Stage-D Debian 12.15 internal eMMC boot NORMAL restart PASS and actual p7 6,645,760-byte image readback SHA256 **exactly matches** `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`; full 8MiB p7 SHA256 `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`; `/dev/mmcblk0p8 ext4 /` physically verified. **NO p7 SHA readback pending.**](MZ600_V064_STAGE_D_PERSISTENT_P7_FULL_PHYSICAL_SHA_VERIFIED_2026-10-26.md).


> **LATEST 2026-10-26:** [Owner ran native one-shot CMD and flashed p7 Stage-D: fastboot Sending+Writing OKAY native exit0; normal reboot (NOT fastboot boot) reached Debian 12.15 USB login with internal `/dev/mmcblk0p8 ext4 /`, **persistent internal root BOOT PASS**; postflash p7 raw SHA readback pending owner sudo](MZ600_V064_STAGE_D_PERSISTENT_P7_FLASH_PREFLIGHT_STAGED_2026-10-26.md).


> **LATEST 2026-10-26:** [Stage-D repeat temporary fastboot boot PASS: Debian 12.15 runs from internal p8, but the kernel-reported p8 GPT PARTUUID differs from previous Stage-D and failed Stage-E image. Internal root fstab now stale again; stable ext4 UUID available. No persistent flash](checkpoints/MZ600_V064_STAGE_D_RETEST_P8_GPT_PARTUUID_CHANGES_ACROSS_BOOTS_2026-10-26.md).


> **NEW PHOTO 2026-10-26:** [Stage-E framebuffer directly confirms `Waiting for root device PARTUUID` at ~1.008sec after BigPart p8 enumeration, not a Debian userspace issue; repeatable PARTUUID lookup failure vs working `root=/dev/mmcblk0p8` Stage-D](MZ600_V064_STAGE_E_LIVE_GUID_TEMPBOOT_UNRESPONSIVE_2026-10-26.md). Next: fresh Stage-D temp boot, inspect p8 GPT GUID for cross-boot stability.


> **LATEST 2026-10-26:** [Stage-E live-GPT-PARTUUID internal-root temporary fastboot boot accepted but Debian login NOT observed, COM9 serial timeouts. Prior Stage-D direct /dev/mmcblk0p8 internal-root PHYSICAL PASS remains valid; firmware rescue preserved, root GUID issue still unresolved](MZ600_V064_STAGE_E_LIVE_GUID_TEMPBOOT_UNRESPONSIVE_2026-10-26.md).


> **LATEST 2026-10-26:** [Internal Debian p8 `/etc/fstab` root PARTUUID repaired to **live kernel-reported p8 GPT GUID**, exact saved backup + unchanged-other-lines proof and original permissions preserved. Stage-D p8 boot still running; Stage-E corrected-GUID TEMP boot image prepared, NOT BOOTED or FLASHED](MZ600_V064_STAGE_E_FSTAB_LIVE_P8_GUID_CORRECTED_2026-10-26.md).


> **NEWEST 2026-10-26 Stage-D BREAKTHROUGH:** [Native Debian 12.15 **PHYSICALLY BOOTS FROM INTERNAL p8** with `root=/dev/mmcblk0p8`, USB login & `findmnt /` PASS. Earlier PARTUUID saved was wrong vs ALL current kernel partition GUIDs; current installed fstab mismatches p8. Correct live-GUID Stage-E image staged OFFLINE, no flash](MZ600_V064_STAGE_D_INTERNAL_P8_DEVNODE_BOOT_PHYSICAL_PASS_2026-10-26.md).


> **LATEST SCREENSHOT PHYSICAL DIAGNOSIS 2026-10-26:** [Stage-C kernel prints `Waiting for root device PARTUUID=...` while showing BigPart p8 and p1–p10 detected; evidence points to kernel root identifier resolution, Stage-D direct p8 block-device boot queued TEMP only](MZ600_V064_STAGE_C_INTERNAL_P8_TEMPBOOT_NO_LOGIN_2026-10-26.md).


> **LATEST PHYSICAL 2026-10-26 ~03:42 EDT:** [Stage-C internal p8 root temporary fastboot boot ACK, but USB COM9 never yielded Debian login (105 sec), write timeout; stage C NOT verified, p7 rescue unchanged](MZ600_V064_STAGE_C_INTERNAL_P8_TEMPBOOT_NO_LOGIN_2026-10-26.md). Need owner to reset and normal-boot from persistent p7 with SD inserted before diagnostics.


> **2026-10-26 ~03:30 EDT — NEWEST INTERNAL INSTALL:** [Experimental MZ600 classic BigPart p8 ext4 1GiB now contains Debian 12.15; after controlled installer stops, manually completed p8 fstab/mountpoints, unmounted and **e2fsck -fn exit0**. Stage-C internal-root BOOT STILL PENDING; kernel modules uname/vermagic mismatch found](MZ600_V064_BIGPART_INTERNAL_DEBIAN_P8_FILESYSTEM_INSTALLED_FSCK_PASS_2026-10-26.md). Persistent p7 microSD Debian fallback validated unchanged.


> **HARDWARE CORRECTION 2026-10-26:** [Owner repaired BOTH replacement MZ600 DC charging jack AND volume button; manual fastboot/TWRP recovery works, outdated broken-button assumption must not block internal Debian installation](MZ600_REPLACEMENT_HARDWARE_REPAIR_VERIFIED_BY_OWNER_2026-10-26.md).


> **NEWEST PHYSICAL PROOF 2026-10-26 02:55 EDT:** [Persistent Linux7 Debian SD p7 ordinary boot AND raw on-device p7 first-6,645,760B SHA EXACTLY MATCHES known Stage-B image; full 8MiB hash and all safety guards recorded](MZ600_V064_PERSISTENT_P7_PHYSICAL_READBACK_SHA_PASS_2026-10-26.md). p8 unchanged, no destructive install; independent bootloader rescue not yet proven.


> **LATEST PHYSICAL 2026-10-26:** [Permanent p7 Linux7 Debian 12 SD-root NORMAL FASTBOOT REBOOT physically PASS (no temporary boot), native flash exit 0, Sending+Writing OKAY](MZ600_V064_PERSISTENT_SD_DEBIAN_BOOT_PHYSICAL_PASS_2026-10-26.md). Current device at authenticated unprivileged Debian microSD shell, p7 post-flash raw hash still pending private root authentication. p8 unchanged.


> **LATEST SAFETY CHECKPOINT (2026-10-26 02:26 EDT):** [Linux→fastboot reboot mode FAILED (returned Android); persistent p7 boot flash AMBIGUOUS due native AVB warning/PowerShell exception; device recovered to RAM temporary SD Debian and p7 requires read-only hash before any further writes](MZ600_LINUX7_RESCUE_BOOTLOADER_AND_P7_FLASH_AMBIGUITY_2026-10-26.md). Do not format p8 yet.


> **LATEST PHYSICAL (2026-10-26):** [Full normal Debian 12.15 SD-root Linux7 Classic BigPart boot + USB authenticated console, correct 1GiB p8 and read-only p8 installer preflight PASS](MZ600_V064_BIGPART_DEBIAN_SDRoot_PHYSICAL_PASS_INSTALL_PREFLIGHT_2026-10-26.md). Device currently booted real Debian from inserted SD. Original eMMC untouched; requires owner sudo authorization and independent boot rescue before destructive install.


**LATEST OFFLINE (2026-10-25 late evening):** [v064 BigPart-aware Debian 12 microSD-root installer boot image built and SHA-verified](MZ600_V064_BIGPART_DEBIAN_MICROSD_INSTALLER_STAGE_B_OFFLINE_2026-10-25.md). **NOT physically booted;** device remains live in previously physically validated v064 stage-A RAM-only. Reinsert previously prepared microSD before first stage-B test.


**LATEST PHYSICAL (20:57 EDT):** [MZ600 Linux7 v064 Classic BigPart RAM temporary boot, USB PONG and exact kernel virtual p8 1GiB/p9 512MiB/p10 28,929.5MiB PASS](MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md). Current device is v064 RAM-only, not TWRP. No block writes or internal Debian install.


> **NEWEST PHYSICAL (Oct25 20:47 EDT):** [Verified OEM relocated GPT at LBA 62,513,151 with 64-bit ARM O_RDONLY probe while in TWRP, original partition geometry intact](MZ600_BIGPART_TWRP_PHYSICAL_GPT_LLSEEK_PROOF_2026-10-25.md). Device presently in **TWRP 3.1.1-0 ADB root**, not v06.3 Linux. BigPart read-only kernel stage-A is being compiled offline; no partition formatted or flashed.


> **LATEST OFFLINE Classic BigPart MZ600 evidence (Oct25 late evening):** [Original Xoom BigPart layout matches exact replacement MZ600 factory p8/p9/p10; 1GiB p8 Debian root selected](MZ600_V064_ORIGINAL_BIGPART_LAYOUT_MATCH_OFFLINE_2026-10-25.md). Original kernel patch and host geometry-check PASS; **no new on-device kernel, BigPart recovery, partition-format or Linux install**. This supersedes the p10-root plan; v06.3 is still last checked physical kernel.


> **Newest OFFLINE v06.4 work:** [2026-10-25 ARMHF userspace closure, image budget and missing package preflight](MZ600_V064_ARMHF_PACKAGING_PREFLIGHT_OFFLINE_2026-10-25.md), `OFFLINE PREFLIGHT PASS`, **NO NEW IMAGE OR HARDWARE TEST**. The most recent physical result remains v06.3 HCD/HCI then sequential Wi-Fi PASS.


> **Newest physical qualification (Oct 25, 2026, 19:13 EDT):** [Exact v06.3 RAM boot and BCM4329B1 HCD/HCI followed by Wi-Fi PHYSICAL PASS](MZ600_V063_PHYSICAL_PASS_HCD_HCI_AND_BLUETOOTH_TO_WIFI_2026-10-25.md). Earlier same-image [no PONG/red-LED attempt](MZ600_V063_INITIAL_RAM_BOOT_NO_PONG_RED_LED_RECURRENCE_2026-10-25.md) remains historical and unexplained. For next work see [v06.4 functional iw scan, terminal and keyboard implementation contract](../plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md) and [full handoff](../handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md). The old v01–v041 table below is a **chronological history**, not the current clean v06.3 capability list.


**Evidence labels:** `BUILT` offline successful build; `BOOTED` device reached Linux; `PHYSICAL` observed test behavior; `FAILED` negative feature test; `UNVERIFIED` no independent hardware proof. This table is a timeline, *not* a single escalating success rating.

| Rev | Key result | Evidence classification |
| --- | --- | --- |
| v01 | Tegra20 zImage/DTB compile, earliest Linux init failure due missing /init | BUILT / BOOT INVESTIGATION |
| v02 | Freestanding ARMv7 PID1 and initramfs built | BUILT |
| v03 | Replacement MZ600 Stingray startup and basic diagnostics | BOOTED |
| v04 | CDC ACM USB serial and `PING`, framebuffer, MMC, DRM/thermal | PHYSICAL |
| v05 | Atmel maXTouch event2: 273 frames / 29 reports, coordinate mapping | PHYSICAL |
| v06 | Grid + crosshair physical touch mapping, temporary UI | PHYSICAL |
| v07 | Native `brcmfmac` driver/firmware integrated; no `wlan0` | BOOTED / WIFI FAILED |
| v08 | 3 SDIO funcs, BCM4329 rev3 F1 signature, F2 `-62` timeout; two FW variants | PHYSICAL / WIFI FAILED |
| v09 | Signed regdb staged, F2 unchanged | PHYSICAL / WIFI FAILED |
| v010 | OEM SDIO CCCR v1→v2 forced; F2 unchanged | PHYSICAL / WIFI FAILED |
| v011 | SDIO high-speed mode tested; F2 unchanged | PHYSICAL / WIFI FAILED |
| v012 | SDIO F2 IOEx/IORx instrumentation built | BUILT; independent physical log NOT FOUND |
| v013 | Tegra `.init_card` high-speed hook; last confirmed `PONG ... V13`; F2 unchanged | PHYSICAL / WIFI FAILED |
| v014 | Physical USB boot and Broadcom load/unload PASS; F2 -62; canonical TTY binary upload FAIL | PHYSICAL PARTIAL PASS |
| v015 | Raw tty + CRC binary upload verified (4 KiB, 264 KiB firmware, 17 KiB and 460 KiB .ko), uploaded module lifecycle and retry PASS; wlan0 absent | PHYSICAL USB/DIAGNOSTIC PASS; WIFI NOT WORKING |

v014 image SHA256: `65846a0928feed535e81a0898bc186d48d12a96c40f36719d6b56a8a3589f670`. Its image and raw private test captures stay on controlled machines. Public repository records source, manifest and scrubbed summaries.

Versions are not automatically an acceptance order: last proven-on-device v013 remains the physical baseline. For individual variants such as multiple v08 firmware/reset/log tests, see [historical scripts](../../scripts/README.md) and [source map](../reference/SOURCE_MAP.md).

## Git infrastructure acceptance
- [2026-10-24 — three-device write-key and Git worktree qualification](GIT_ACCESS_2026-10-24.md). This is **repository infrastructure** acceptance, not native Linux hardware qualification.

See [v014 USB and module evidence](V014_USB_LAB_2026-10-24.md).

See [v015 raw USB transport qualification](V015_RAW_USB_LAB_2026-10-24.md).

## v016 diagnostic
- [v016 physical F2 IOEx/IORx and clock readback](V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md): diagnostic PASS, native Wi-Fi FAIL.

- [v017 read-only CCCR inventory](V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md): original reported version/high-speed mismatch reproduced; F2 timeout unchanged.

- [v018 physical Motorola six-field override](V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md): effective SDIO capability and timing correction PASS; F2 remained -62 twice.

- [v019 25 MHz physical A/B](V019_SDMMC2_25MHZ_AB_2026-10-24.md): only compiled DTB max-frequency differs; actual host clock 25 MHz; F2 -62 twice.

- [v018 supplementary live recheck](V018_RECHECK_2026-10-24.md): full Motorola capabilities remained effective, F2 timeout repeated, actual 25 MHz host clock; investigate discrepancy with earlier 46.15 MHz v018 measurement.

- [v020 physical MMC2 on-demand re-enumeration](V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md): AUTO/MOTOROLA/AUTO PASS, host completion PASS, module-loaded safety refusal PASS, Wi-Fi F2 still FAIL.

- [Second v020 image SHA and physical on-demand test](V020_SECOND_IMAGE_VERIFICATION_2026-10-24.md). This does not supersede the earlier v020 image record.

- [v020 additional distinct build and two on-demand AUTO/MOTOROLA/AUTO cycles](V020_ADDITIONAL_BUILD_AND_REINIT_2026-10-24.md).

- [v021 OEM-era firmware, calibration match, and pending LPO observer](V021_OEM_FW_AND_LPO_HYPOTHESIS_2026-10-24.md): F2 remains -62; no native Wi-Fi.

- [v022 AUTO/legacy 25 MHz, three real MMC2 trials](V022_AUTO_LEGACY_25MHZ_PHYSICAL_2026-10-24.md): timing specification pass; F2 failure persists.

- [v021 32768Hz LPO software-clock observation](V021_LPO_CLOCK_PHYSICAL_2026-10-24.md): physically run, electrical waveform not measured.

- [v025 power-on pre-reset timing control on physical Xoom](V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md): Linux effective 100ms, F2 -62 in three trials.

- [v026 physical runtime firmware/NVRAM provenance](V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md): exact file names, 3 matching CRCs, persistent F2 failure.

- [v027 physical read-only WLAN/BT GPIO survey](V027_BT_WLAN_GPIO_READONLY_PHYSICAL_2026-10-24.md): U4/U2 outputs valid; BT I7/U0/U1/U6 GPIO direction -22 and cannot safely establish their levels.

- [v028 GPIO CNF/OE/OUT/IN physical controller test](V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md): BT-side pins are not GPIO-enabled, WLAN U2/U4 high outputs, F2 still -62.

- [v030 Bluetooth U4 shared-power and passive I7/U0 compile-only checkpoint](V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md) — 21 static checks; runtime hardware still untouched.

- [v031 physical read-only BT serdev binding and shared clock probe](V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md) — registered Bluetooth child, DRIVER=NONE, live shared 32768Hz provider, F2 -62.
- [v032 clock-role-correct Bluetooth LPO disabled DTB](V032_BLUETOOTH_LPO_ROLE_COMPILE_ONLY_2026-10-24.md) — 12 static checks, no boot change.

- v033 USB Bluetooth test image, Surface host script and reversible source audit: V033_BLUETOOTH_USB_LAB_2026-10-24.md.

- [v033 real Bluetooth power votes, BCM4329B1 identification, USB teardown and Wi-Fi F2 retest](V033_BLUETOOTH_PHYSICAL_2026-10-24.md). Includes the HCIDEVDOWN argument bug and accurate cleanup sequence.

- v034 physical corrected HCI device-down and BCM4329B1 test: V034_HCI_IOCTL_PHYSICAL_2026-10-24.md. HCIDEVDOWN rc 0, BT modules unload, U4 vote released, MMC2 bound.

- [v035 BCM4329 PMU/CM3/F2 physical event timeline](V035_BCM4329_PMU_CM3_F2_PHYSICAL_2026-10-24.md) — three read-only instrumented RAM driver trials, PMUControl 01770180→012B03BC on first load and retained 012B03BC on warm reloads; Wi-Fi F2 still -62, final USB/MMC2 clean.

- [v036 BCM4329B1 PMU-rev6 resource/clock physical trace](V036_BCM4329_PMU_RESOURCE_CLOCK_PHYSICAL_2026-10-24.md) — 2 reproducible RAM-module trials, Motorola's actual 22-bit resource map, ALP→HT, zero PMU pending and zero ChipCommon pullups; F2 still -62, safe unload.

- [v037 SDPCM mailbox write physical audit](V037_SDPCM_MAILBOX_WRITE_PHYSICAL_2026-10-24.md) — exact OEM protocol 4, successful live SDIO mailbox-write return rc0, yet F2 -62; modules unloaded and MMC2 bound.

- [v038 read-only Cortex-M3 and NVRAM end-of-RAM handoff](V038_BCM4329_CM3_NVRAM_HANDOFF_PHYSICAL_2026-10-24.md) — core down→up, 288KiB RAM, length token matches, F2 -62. Motorola reference values match all shared NVRAM fields.
- [v039 original HRI39/HRI66 Wi-Fi firmware physical A/B](V039_ORIGINAL_MZ600_FIRMWARE_PHYSICAL_2026-10-24.md) — original 2011 BCM4329B1 firmware also fails F2 -62 under unchanged Linux 7; generic firmware restored with known USB CRC.

- [v038 SDMMC2 host runtime-active F2 physical trial](V038_MMC2_RUNTIME_PM_HOLD_PHYSICAL_2026-10-24.md) — bounded PM runtime hold rc0 across firmware/F2 on actual c8000200.mmc; timeout -62 unchanged, balanced release and clean unload.
- [v039 original MZ600 2011 Wi-Fi firmware physical trial](V039_ORIGINAL_MZ600_FW_PHYSICAL_2026-10-24.md) — source-authenticated 261317-byte OEM firmware changed alone, F2 -62; rollback to generic 253748-byte image CRC32 B4092AA6 verified in RAM.

- [v040/v041 physical Cortex-M3 execution / NVRAM token / SDPCM shared header checkpoint](V040_V041_CM3_NVRAM_SHARED_STRUCTURE_PHYSICAL_2026-10-24.md) — verified CM3 down→up, NVRAM token matches, RAM tail becomes genuine v3 SDPCM shared header with no trap/assert and valid console/msgtrace; F2 still -62, safe unload.

- [v042–v045 successful BCM4329 F2 and first native wlan0 physical bring-up](V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md) — firmware console err21 exposed missing stock MAC NVRAM bootstrap field, verified F2=0 with one variable changed, upstream WCC vendor ops enabled first wlan0; original MAC-free NVRAM and modules safely restored, no RF scan.

- [Normal installed-OS Debian ARMhf and clean kernel offline acceptance — 2026-10-24](NATIVE_OS_OFFLINE_BUILD_PASS_2026-10-24.md) — 5.89MB boot image + 768MiB ext4 OS image, exact firmware, separate upstream WCC, Motorola dynamic-MAC patch, USB ttyGS0 login; **offline PASS, not installed/boot-tested**.

- [COMPREHENSIVE BREAKTHROUGH MILESTONE / READ FIRST](BCM4329_BREAKTHROUGH_AND_NATIVE_OS_MILESTONE_2026-10-24.md) — consolidated physical v01–v045, firmware console err21, MAC-only F2=0, WCC/wlan0 proof, factory MAC integration, current native OS artifacts, Android preservation and all test gates.
- [Android-preserving native OS OFFLINE rebuild](ANDROID_PRESERVING_NATIVE_OS_OFFLINE_REBUILD_2026-10-24.md) — new `root=PARTLABEL=xoom-linux` target, banned Android root labels, archive of rejected old image, 768MiB standalone Linux root, new SHA hashes; no install.

- [Android 3.1 stock-kernel touchscreen comparison and OEM restore-media audit](ANDROID_3_1_TOUCHSCREEN_COMPARISON_2026-10-24.md) — qtouch I²C NACK at 0x5b and 0x35 under both TWRP/Android; HRI39/HRI66 stock images already privately archived; no disk writes.

- [2026-10-25 native OS installation preflight — actual replacement MZ600 recovery storage, same-unit Android boot/system/TWRP backups, TegraPT gate](NATIVE_OS_INSTALL_RECOVERY_PREFLIGHT_2026-10-25.md). **No eMMC install or partition formatting performed**; microSD or explicitly approved userdata decision remains.

- [32GB microSD physical preflight and normal Debian PARTUUID-root offline build, 2026-10-25](MICROSD_ROOT_OFFLINE_PREFLIGHT_2026-10-25.md) — real empty FAT32 removable media, validated DOS MBR, card-specific root selector, legacy-resizable ext4 and verified offline images; **media formatting requires explicit authorization**.

- [2026-10-25: **microSD Debian root physically INSTALLED**, full SD ext4 expanded, SHA-readback PASS; Linux first temp boot unconfirmed](MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md) — SD blocks dynamically reordered between boots, new MBR verified, staged gzip SHA, 768MiB root write/readback, fsck, ~28.7GiB usable root, temporary fastboot boot OKAY but USB/OS login absent. Android internal storage untouched.

- [First Debian SD boot still displays fastboot screen: controlled legacy ramdisk comparison ready, no EMMC writes](MICROSD_FIRST_BOOT_FASTBOOT_SCREEN_RAMDISK_COMPARISON_2026-10-25.md) — compares valid 71B ramdisk-only variant vs previously working v15 temporary-boot image; both verified and staged on Surface, physical reboot needed.

- [Fastboot image remains on screen: new Linux 7 kernel + proven v034 ramdisk temporary test READY, not yet booted](MICROSD_TEMP_BOOT_STUCK_SCREEN_DIAG_CANDIDATE_2026-10-25.md) — exact original/new boot header comparison, no live USB after bootloader handoff, diagnostic SHA and safe restart plan.

- [2026-10-25 **PHYSICAL Linux 7 framebuffer + microSD PARTUUID PROOF**](LINUX7_PHYSICAL_KERNEL_AND_MICROSD_PARTUUID_PROOF_2026-10-25.md) — user screen photo shows kernel started, partitions enumerated, correct SD UUID, and rootless hybrid panic; verbose normal Debian microSD-root image prepared and hash-verified, not yet booted.

- **[2026-10-25 PHYSICAL SUCCESS — full Debian 12 microSD root boot, systemd PID1, COM9 serial login, native modular BCM4329 wlan0 and matching dynamic FDT MAC](NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md)** — replaces former first-boot-unconfirmed status; no Android eMMC flash, RF still untested.

- **[2026-10-25 MZ600-US69 DTB-only TEMPBOOT prepared, NOT YET BOOTED](MZ600_US69_COUNTRY_MAP_VARIANT_BUILT_NOT_BOOTED_2026-10-25.md)** — exact one-property DTB diff, known-good Linux7 kernel/ramdisk, SHA-verified new image, separate no-MAC Motorola calibration, safe Surface one-click test with no flashing.

- **[2026-10-25 US/69 test actual physical attempt — transient COM9 then missing](MZ600_US69_TRANSIENT_USB_POSTBOOT_2026-10-25.md)** — bootloader reports fastboot boot OKAY, COM9 briefly enumerates and disappears within timestamp resolution of one second. Linux login/firmware country NOT confirmed. Baseline known-good retained and no flash performed.

- **[2026-10-25 baseline original Debian image ALSO reproduces one-second USB dropout after US69 attempt](MZ600_BASELINE_REPRODUCES_US69_USB_DROPOUT_2026-10-25.md)** — user recovered black-screen Xoom to Android with Power+Vol Up; battery 100% and charging; known-good RAM-only image fastboot OKAY, COM9 09:38:40–09:38:41 then absent; no persistent Debian login. Rules out attributing failure solely to US69 mapping.
