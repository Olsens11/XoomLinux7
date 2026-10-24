# Verified project state — imported 2026-10-24

> **Verification labels are intentionally strict.** This is the working status as recovered from measured local outputs; it does not imply all parts were independently re-run at repository initialization.

## Source
- Upstream: `https://github.com/xoom-linux/linux.git`, pinned commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (Wingray DTS contribution, June 12, 2026).
- Kernel output reports `7.0.0-next-20260422`. ARMv7 Cortex-A9 Tegra2, no NEON.
- `tegra20-motorola-stingray.dts` is the upstream Wingray DTS with model/compatible strings changed; `-usbdiag` additionally changes USB0 to peripheral mode. Shared Wi-Fi nodes are unchanged.

## Hardware-qualified behavior (replacement MZ600)
- Temporary-boot Linux v013: serial USB diagnostics (`PONG XOOM-LINUX V13`), framebuffer/display, touch/grid, MMC/SDIO diagnostics.
- Touch v05 recorded 273 frames and 29 event reports; v06 touch crosshair confirmed physical mapping. Small transient lag at quick swipes, not considered worth special work on throwaway test UI.
- Wi-Fi: BCM4329 rev3 enumerated as `mmc2:0001` (three functions), correct F1 signature `0x9934329`, firmware transfer initiated. **No wlan0 and no working native wireless connection.**
- Blocker: `brcmf_sdio_firmware_callback enable F2: err=-62` (approx 3s ready timeout), including alternative OEM firmware, regulatory database integration, SDIO CCCR revision and high-speed host experiments.
- v012 instrumentation was built; separate conclusive physical v012 capture was not found.

## Latest build
- v014 RAM-only LIVE-LAB image staged and independently hashed on Surface: `MZ600-stingray-diagnostic-v14-LIVE-LAB-TEMPBOOT-ONLY.img`, 6,656,000 bytes; SHA256 `65846a0928feed535e81a0898bc186d48d12a96c40f36719d6b56a8a3589f670`.
- **v014 was physically temporary-booted 2026-10-24**: USB PING and STATUS PASS; Broadcom WIFI_START and WIFI_STOP PASS; BCM4329 F2 still times out -62; no wlan0. Binary firmware upload FAIL due to canonical TTY echo/buffering; session recovered without a reboot.
- **v015 was physically temporary-booted on 2026-10-24 and accepted for USB/live-lab use**. STATUS included USB RAW READY. Raw firmware uploads of 4,096 and 264,140 bytes returned matching CRC32; RAM module uploads of 17,828 and 460,140 bytes matched CRC32. Uploaded modules loaded, debug-level change was confirmed, WIFI_RETRY performed unload/load, and WIFI_STOP unloaded both. **WLAN0 remains absent; Wi-Fi F2 problem is not fixed.** See V015_RAW_USB_LAB_2026-10-24.md.
- Built image, private binaries and exact device logs remain on development machines, not in public Git.

## Next gate
1. Treat v015 as qualified RAM-only USB diagnostic baseline; no permanent flash.
2. Reproduce the BCM4329 F2 ready timeout using uploaded driver modules and controlled changes, comparing register/firmware/clock traces to OEM reference.
3. Before RF scans or associations, validate per-device MAC/calibration and regulatory provenance.
4. Do not confuse usable live-lab infrastructure with actual wlan0 or association success.

See [Wi-Fi report](hardware/WIFI_BCM4329.md), [checkpoint log](checkpoints/README.md), [roadmap](roadmap.md).

## Repository workspace and import verification (2026-10-24)
- GitHub main commit `ea38127` imported 133 reviewed original source files. Desktop verification compared all 133 against `evidence/import-source-sha256.txt`: **133/133 SHA-256 match, 0 mismatches**.
- One historical note containing MAC-like material was excluded from public source pending review; private copy retained at source.
- Three development machines have cloned repositories and dedicated tracked Git worktrees. Desktop and Pi continuity checker: **0 errors**. Surface fresh checkout line-ending differences were resolved and both trees left clean.
- Separate SSH ed25519 deploy keys are registered with write permissions. **Actual SSH auth, remote branch creation, and remote branch deletion passed from Desktop WSL, Raspberry Pi, and Surface**, with one independent branch per machine. Temporary access-test branches were removed afterward; see [dated access verification](checkpoints/GIT_ACCESS_2026-10-24.md).
- Surface v014 diagnostics client and safe USB probe scripts imported separately, without firmware or raw device-specific scripts.

## 2026-10-24 validated update
See [v014 physical testing](checkpoints/V014_USB_LAB_2026-10-24.md), and [v015 candidate manifest](../releases/v015-manifest.txt). v014 remains safely running, v015 pending physical qualification.

## Pending BCM4329 qualification (2026-10-24, v016 on v015 environment)
A read-only hotloaded v016 Broadcom module physically recorded IOEx \`0x02→0x06\`, IORx \`0x02→0x02\`, clock CSR \`0xD2\`, \`-62\` timeout, still no wlan0. Source restored byte-identically. Previous v010/v011/v013 capability interventions are now considered **partial exploratory tests**, not OEM-equivalent accepted fixes. Next: read the RAW CCCR and EFFECTIVE parsed six card capabilities and host timing, then test a board-scoped complete Motorola equivalent with a valid control. [Evidence](checkpoints/V016_F2_IOEX_IORX_PHYSICAL_2026-10-24.md).

## v017 diagnostic evidence, no Wi-Fi promotion
v017 RAM-hotloaded read-only module verified actual raw CCCR and final card/host flags: raw CCCR 0x11, Linux version 1, high-speed 0 versus Motorola OEM version 2, high-speed 1. Host clock 46,153,846 Hz at legacy timing. F2 still -62, no wlan0. See [v017](checkpoints/V017_CCCR_CAPABILITIES_PHYSICAL_2026-10-24.md). This is **not a fixed Wi-Fi checkpoint**; v015 remains the proven diagnostic loader.

## v018 completed OEM capability counterfactual, 2026-10-24
The **complete board/chip-scoped Motorola six-field override** was applied after CCCR/CIS parsing and physically confirmed by the v017 read-only module. Final version=2 and highspeed=1, SDIO SPEED=03, host timing=2 (SD HS), clock remains 46,153,846Hz. With the same OEM firmware and generic NVRAM, two trials still had IOEx=06/IORx=02 and F2 timeout -62; no wlan0. **The full OEM card capability override alone does not solve Wi-Fi.** [Exact evidence](checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md). v015 remains the stable diagnostic infrastructure.

## v019 25MHz physical A/B, 2026-10-24
A full Motorola six-field-override v018 kernel with the actual USB diagnostic DTS SDMMC2 max-frequency capped to 25MHz was rebuilt and temporary-booted as v019. DTB decompilation confirmed only one property difference; the first draft altering an unused source file was caught and NOT booted. Actual host clock **25,000,000Hz**, SDIO version 2/high-speed 1 and host timing 2. Same OEM firmware, generic NVRAM and v017 diagnostic module. Two attempts: IOEx=06/IORx=02, **F2 -62 and no wlan0**, unchanged. [v019 checkpoint](checkpoints/V019_SDMMC2_25MHZ_AB_2026-10-24.md). v015 remains accepted as diagnostic infrastructure; no Wi-Fi repair promoted.

## v018 supplementary recheck and on-demand design (2026-10-24)
Another physical v018 run (identical image SHA) confirmed six Motorola capabilities active, SDIO SPEED=03, host high-speed timing=2 and F2 -62 with IOEx=06, IORx=02. This instance measured **25 MHz actual MMC host clock**, whereas the earlier recorded v018 run measured 46.15 MHz despite v018 DTB max-frequency=46.15 MHz. The discrepancy needs a controlled investigation, not silent reconciliation. [Supplementary evidence](checkpoints/V018_RECHECK_2026-10-24.md). On-device read-only SDIO command shows the Wi-Fi platform device `c8000200.mmc` supports driver bind/unbind, which motivates a [guarded on-demand reinitialization design](architecture/MMC2_ON_DEMAND_DESIGN.md). **That capability has NOT been implemented, and F2 is not fixed.**

## v020 physically qualified on-demand MMC2 controls (2026-10-24)
**Latest accepted experimental diagnostic baseline v020**, with v015 retained as prior USB fallback. The replacement MZ600 successfully temporary-booted exact SHA256 b08863d6be4ae15f757eb9bfa8089d3a2d23859fc3ea63c4f119f4be9430ebf3. Without reboot, MMC2 reinitialized using unchanged AUTO, then MOTOROLA (all six effective fields changed), then AUTO again. A separate attempt with loaded Broadcom drivers was correctly denied; the Surface host client now waits for terminal PASS or error. Final state: AUTO, module list empty, card bound. **F2 still times out -62 and wlan0 remains absent.** Detailed [checkpoint](checkpoints/V020_MMC2_ON_DEMAND_PHYSICAL_2026-10-24.md). Rebind is not proven full electrical power cycle.

## v020 post-test stability caveat
After completing and documenting successful runtime MMC2 AUTO/MOTOROLA/AUTO tests, the Surface later observed a temporary loss of Linux USB CDC, followed by the replacement MZ600 appearing in Android ADB mode, then Linux v020 CDC again. Read-only Linux uptime at final recovery was only 83.96 seconds, whereas the prior session had passed 250 seconds. This confirms a **later session restart** but does not establish its cause. No deliberate reboot was issued by this workflow after initial v020 boot. v020 on-demand functionality physically passed; **long-running session stability is NOT yet qualified**. See v020 physical checkpoint.

A second v020 image (SHA256 e23e3dea2a0996bb7d63c8e7158715ad6799b57f45e4dcc3fcab454b528bc6bb) was independently staged, temporarily booted and tested; it passed AUTO/MOTOROLA/AUTO re-enumeration with F2 still failing. The earlier v020 manifest SHA is different; [see distinct-image test provenance](checkpoints/V020_SECOND_IMAGE_VERIFICATION_2026-10-24.md). Long-duration stability remains unresolved.

## v020 additional build measured 2026-10-24
A separate v020 temporary image (6,662,144 bytes, SHA256 96f01d72782cd3ab6574b806a0d84b1874ec0f98bbe865c74365623ba7148067) passed five guarded MMC2 rebinds on the replacement MZ600, including two full AUTO->MOTOROLA->AUTO cycles and a correct DENIED PREFLIGHT with modules loaded. Effective capabilities read back correctly. Final state AUTO, MMC2 bound, BCM4329 present and modules unloaded. Native Wi-Fi still F2 -62/no wlan0; long-duration stability and build reproducibility not qualified. See [additional v020 checkpoint](checkpoints/V020_ADDITIONAL_BUILD_AND_REINIT_2026-10-24.md).

## 2026-10-24, v021 evidence-based OEM checks
Private original BCM4329 NVRAM has 53 identical shared settings to the current generic calibration; only original MAC is omitted. Physical same-kernel F2 trials with standard firmware in AUTO and Motorola-era firmware in AUTO and MOTOROLA all failed with IORx=02/-62. Firmware was restored in RAM and AUTO profile selected after. Existing Motorola U4 power/U2 reset 100/100/200ms timing versus mmc-pwrseq, and BCM4329 32.768kHz LPO required clock remain high-priority; the read-only v021 PMC clock-provider observer built and staged but **was not uploaded to hardware**, so no actual runtime clock state is claimed. See [v021](checkpoints/V021_OEM_FW_AND_LPO_HYPOTHESIS_2026-10-24.md).

## BCM4329 datasheet review (2026-10-24)
Section 11 p51: maximum 25MHz for default SDIO; Xoom measured 46.15MHz @ ios.timing=0, an out-of-spec test condition. v019 ran 25MHz **high-speed** (timing=2), so the precise AUTO/default <=25MHz experiment is **still pending**. Additional requirements: >=110ms after core VDDC settles before SDIO access, CMD/DAT 10-100k pull-ups, and correct 32k/PMU reset/power behavior; SPI-specific boot register procedure is NOT transferable to SDIO. [Datasheet evidence](research/BCM4329_DATASHEET_SECTION11_REVIEW_2026-10-24.md). No new physical test or native WLAN success is claimed.

## v022 datasheet Section 11 A/B qualification, 2026-10-24
Temporary-boot v022 differs from known v020 boot image only in compiled SDMMC2 max-frequency limit (46153846→25000000, four DTB bytes) and Android boot checksum (20 bytes). Surface SHA256 verified \`2be2f5094149f242a5a9e5d290f7505d9b312ae4bfba8dbc74e1f7362995c6b3\`. Physical AUTO, legacy \`ios.timing=0\`, actual \`ios.clock=25000000\`, same 253748-byte standard firmware and 672-byte NVRAM; **three** fresh MMC2/card/driver trials all returned F2 -62, IOEx 06, IORx 02; wlan0 absent. Final MMC2 valid/bound, AUTO profile 0, modules unloaded, USB alive. [Full evidence](checkpoints/V022_AUTO_LEGACY_25MHZ_PHYSICAL_2026-10-24.md). LPO/true reset/supply-settling still unverified.

## Completed v021 LPO test — 2026-10-24
The previous offline-only v021 observer physically ran on v022: host/device USB CRC verified 462492-byte module; Linux reports wifi pwrseq clock rate=32768 enabled=1 while the F2 probe still gives IOEx 06 / IORx 02 / -62, no wlan0. This is software clock-provider state, not pin-level waveform proof. Modules unloaded, MMC2 bound, AUTO profile. See [physical checkpoint](checkpoints/V021_LPO_CLOCK_PHYSICAL_2026-10-24.md).

## v025 physically tested MMC2 pre-reset delay (2026-10-24)
The Linux 7 MMC host's default 10ms pre-reset delay was physically measured. Separate 300ms \`wifi-pwrseq\` property applies **after** reset release; earlier assumption it was a power stabilization interval was wrong. v025 added *only* \`/mmc@c8000200/post-power-on-delay-ms = 100\` in an otherwise byte-identical v022 kernel/ramfs and verified image SHA256 \`142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb\`. On replacement MZ600 v024 observer measured effective host \`power_delay_ms=100\`, clock 25MHz legacy 0, regulator/GPIO software states plausible; three physical tests (first boot plus two MMC2 rebinds) all F2 timeout -62; no wlan0. Left device AUTO, MMC2 bound, modules unloaded. [V025 physical checkpoint](checkpoints/V025_PRE_RESET_100MS_PHYSICAL_2026-10-24.md). U4 regulator-boot-on remains a potential masking factor; audit power sequencing and firmware core release next.

## Virtual Linux 7 forensic lab v1 (2026-10-24)
Desktop WSL now runs a one-command QEMU ARM userspace provenance lab against exact v025 image SHA256 142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb. Separate ARM FDT parser validates MMC host delay 100ms, pwrseq 300ms, SDIO max 25MHz, regulator wiring. Host audited 12 Linux source consumer locations plus real embedded firmware/NVRAM/module paths. Python and ARM/QEMU NVRAM parsers yield byte-identical 672-byte data; seven fault injections detected. Not full Tegra/BCM4329 machine emulation, Wi-Fi fix, or runtime firmware request proof. Open issues: previous diagnostic wrong pwrseq sysfs path; regulator-boot-on power cycling, MAC provenance, and selected board-specific firmware path unverified. [Lab report](research/VIRTUAL_FORENSIC_LAB_V1_2026-10-24.md). Physical F2 still -62, no wlan0.

## Physical v026 runtime provenance — 2026-10-24
The corrected read-only brcmfmac v026 module (467412 bytes, SHA256 5b4b28b9aa7d8a1708a190dfd85fee5274f7c6eba82c1bc3bb5bbe9d50d7c690) loaded through RAM USB on the replacement MZ600. Linux tried board-specific then generic firmware/NVRAM; the actual returned generic binary was 253748 bytes CRC32 B4092AA6, source NVRAM 1550 bytes CRC32 FAFCC93A, packed NVRAM 672 bytes CRC32 596925B1. All match the v1 offline model fingerprints. Platform MAC lookup unavailable (no MAC printed). F2 still IOEx=06/IORx=02/-62, wlan0 absent; regulator real power cycle remains unproven. Modules unloaded; MMC2 bound, AUTO. [Detailed hardware result](checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md).

## Complete BCM4329 datasheet reference audit and v027 survey — 2026-10-24
Indexed all 149 pages of Broadcom 4329-DS105-R / Cypress Rev F and cross-checked 36 source/hardware contracts; produced shared BT/WLAN power/clock/PMU fault tree. New read-only 31-assertion source-vs-v025-DTB contract checker found **1 direct checked-in source discrepancy**: base SDMMC2 max-frequency 46153846 Hz vs 25MHz legacy-mode ceiling, while verified v025 compiled DTB is 25MHz. Compiled BT child `txco` and WLAN pwrseq `ext_clock` share clock phandle/index 26/3; clock role must be audited, not assumed correct. Physically ran v027 (464584 bytes SHA256 12e355a0e2db6ffe6481612825b5292bbbf6010653155e11525adc31d8756d3e): U2/U4 valid high outputs, I7/U0/U1/U6 direction queries **-22** so raw values not proof of BT power state; F2 still -62. Returned MMC2 bound, AUTO, modules unloaded. [Page index](research/BCM4329_DATASHEET_PAGE_INDEX.md), [matrix](research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md), [v027 test](checkpoints/V027_BT_WLAN_GPIO_READONLY_PHYSICAL_2026-10-24.md).

## BCM4329 chip-level shared ownership reconstruction — 2026-10-24
Read the OEM Stingray shared power callback: both WLAN and Bluetooth call change_power_brcm_4329 with spinlock-protected count and shared U4 output; legacy BT rfkill callback explicitly drives I7 LOW in both branches and toggles U0 reset. Current Linux 7 gives U4 solely to MMC fixed regulator and I7 to generic hci_bcm; CONFIG_POWER_SEQUENCING not enabled and no coordinated MMC+BT consumer. A pure OFFLINE logic model now covers shared regulator OR/UNKNOWN states, independent vs Motorola shared-U4 policies, 110ms from known supply stabilization, reset safety and vote lifecycle. **20 unit tests passed; no new kernel driver or physical change.** [Detailed architecture](research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md). F2 still -62 in v025. The OEM divergence warrants a staged read-only pinmux, driver-binding and ownership audit before an actuating test.
