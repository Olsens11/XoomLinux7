# Diagnostic checkpoint ledger — v01 through v014

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
