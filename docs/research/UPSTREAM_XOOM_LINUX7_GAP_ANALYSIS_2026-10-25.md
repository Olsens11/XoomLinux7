# Upstream xoom-linux vs XoomLinux7: reuse audit and actionable goals

**Date:** 2026-10-25
**Review branch:** `wip/bcm4329-whole-chip-integration-20261025`
**Original upstream:** [xoom-linux/linux](https://github.com/xoom-linux/linux), `main` at `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (2026-06-12), pinned in XoomLinux7.
**User objective:** full hardware integration through native Linux 7, preserving Android temporarily as the original OEM hardware reference; once ready, replace Android as the main eMMC OS. The 32 GiB removable Debian ext4 root is a temporary development installation.
**Safety:** This is a source/document review, not a physical boot or eMMC modification. Existing Android, TWRP, Linux SD and private OEM evidence remain unchanged.

## How this was audited

- Queried upstream GitHub default branch, commit history, repository list and issues; the organization currently exposes the `linux` repository as its matching project, and only a `main` branch was found. No published later kernel head than the pinned June 12 revision was found. This is not a claim about collaborators' unpublished work.
- Read `arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dts` and `arch/arm/configs/tegra_next_defconfig` from upstream, plus upstream `drivers/bluetooth/hci_bcm.c`, `drivers/media/radio/Kconfig`, and `brcmfmac/of.c`.
- Programmatically compared the 1,712-line upstream Wingray DTS to the 1,722-line Stingray DTS in this development branch with an exact line-level LCS diff: **18 added lines, 8 removed lines, 26 change lines total**. Differences are exactly: four opening Stingray disclaimer/comment lines, board model/compatible string, the BCM4329 Bluetooth `lpo` clock-name correction, and the BCM4329 SDIO 25 MHz maximum correction. All remaining shared board descriptions are currently identical. The separate USB-diagnostic Stingray DTS has the same two source fixes and USB-specific modifications.
- Reviewed the physically dated October 24–25 XoomLinux7 checkpoints, not stale top-of-file progress headers or older `docs/roadmap.md` open boxes.

## Reuse matrix — code description is not hardware acceptance

| Hardware / layer | Exists in upstream xoom-linux | XoomLinux7 new evidence / work | Remaining qualification |
| --- | --- | --- | --- |
| Tegra 2, pinmux, CPU/regulators, CPCAP PMIC | Extensive Wingray device tree and standard drivers | Linux 7 executes on replacement MZ600; Debian PID1 boots on SD | Cold/warm boot reliability; physical board and RAM variant; suspend/resume/poweroff; cross-model behavior |
| eMMC and microSD | SDMMC4/3 described, MMC drivers available | MicroSD ext4 written/readback SHA verified, expanded; Debian root physically booted; PARTUUID avoids unstable `mmcblkN` numbers | Boot repeatability; final main-OS internal layout AFTER OEM harvest + explicit write authorization |
| Display / touch | Tegra DRM, LVDS and Atmel maXTouch nodes | Diagnostic text framebuffer and touch crosshair physically passed, Debian login visible | Native brightness, blank/wake, sustained touch, modes, suspend, backlight PWM |
| USB | Tegra EHCI/PHY nodes | RAM boot + USB serial COM9 authenticated Debian session demonstrated | USB COM9 vanished in one second on both original-known-good and US69 boots; diagnose kernel/power/USB before further tests |
| WLAN data path | SDMMC2, `mmc-pwrseq-simple`, Broadcom `brcmfmac`, `cfg80211`; all wiring already described | v043 firmware-console root-cause evidence, v044 F2 `err=0` using OEM bootstrap default, v045 `wlan0`; Debian `wlan0` with separate `brcmfmac_wcc`; dynamic ATAG-to-FDT hardware MAC byte-matched to interface | Stable connection/scan/association/DHCP, calibrated country code, RF limits, profile usability, suspend/coexistence. Do NOT redo F2 research already physically settled |
| WLAN identity | Upstream driver expects FW/board identity; Wingray DTS has no Stingray MAC ATAG conversion | XoomLinux7 board-scoped `patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch`, physically FDT MAC/interface equality. Bootstrap default and unique interface identity deliberately separate | Audit factory identity provenance on each model; upstream-friendly DT/ATAG genericization and patch review, never hardcode test-unit MAC |
| WLAN clocks | Upstream 46.15 MHz max even in legacy mode | v022/v025 measured 25 MHz legacy, did not itself cure F2; development branch caps max-frequency at 25 MHz | Compile, DT binding validation, on-target observed clock/timing, later negotiated high-speed support; review Wingray and Stingray scope |
| Bluetooth transport | UARTC serdev node, `hci_bcm` and HCIUART_BCM configuration already exist | v033 BCM4329B1 HCI recognition with temporary shared-U4 regulator-vote handling, v034 fixed HCI down ioctl; OEM patch file identified | Correct private Motorola `bcm4329.hcd` 17,770B load and integrity, `hci0` operational, BlueZ discover/pair/reconnect/profiles, wake and BT+Wi-Fi coexistence |
| Bluetooth LPO/normal reference | Existing upstream BT DTS names PMC 32.768k CLK_BLINK as `txco`; `hci_bcm` recognizes separate `txco` and `lpo` | Source-only relabel `lpo` in two Stingray DTS files on WIP branch | DT build and physical check, separately determine 38.4 MHz normal oscillator; do not invent missing clock GPIOs |
| Combo shared power | Upstream U4 fixed Wi-Fi regulator; separate U2 WLAN reset, I7 BT shutdown, U0 BT reset; no integrated two-consumer manager | Motorola OEM U4 refcount documented; `src/chip/stingray-bcm4329-pwrseq.c` compile-only prototype, no live MMC+BT consumers | One authoritative owner; implement consumer links and DT schema before activation; verify no duplicated GPIO claims and real chip OFF vs function reset; test each state |
| FM | BCM4329 silicon supports FM features, but no demonstrated FM control/RF/audio wiring in upstream Wingray DTS; no dedicated BCM4329 FM platform driver identified by this audit | Datasheet index and preliminary FM assessment | Determine whether Xoom board actually routes antenna/FM interfaces; only if physically usable add suitable V4L2/ALSA and vendor firmware control; otherwise safe idle, document unavailable. TX cannot be assumed legal |
| Audio | Tegra/CPCAP ALSA SoC pieces and audio routing in DTS | No native audio physical PASS documented | Explicit upstream `TODO: Sound is not working`; codec, amp, microphone/headset and routing validation |
| Backlight | TI LP8550 I2C implementation and LED power | Display output operational in temporary diag | Upstream explicitly says PWM controls not working; only register-based brightness configured; investigate proper PWM/blank/wake path |
| Battery/charging/ADC/power key | CPCAP battery, regulators, ADC and power button nodes and drivers | Android 100% charged after recovered failure; NOT native Linux measurement | Upstream WIP ADC reads timeout -110 (2026-06-08 commit) and device-tree TODO that enabled ADC interferes with power-button IRQ; native power_supply, charging, suspend and reset require independent integration |
| RAM timing | Tegra EMC frequency tables | Linux kernel ran, no independent RAM SKU check | Upstream TODO implements only Elpida 40 nm; OEM contains other Elpida 50 nm / Samsung tables. Important possible system stability issue, no causal proof |
| Sensors | Atmel touch, AK8975 magnetometer, KXTF9 accelerometer, NCT1008 thermal nodes | maXTouch test; other sensors not yet independently tested | Validate orientations, temperatures, interrupts, thermal throttling, use standard IIO/input interfaces |
| Cameras / cellular / dock | No general working camera/3G support proven by this audit | Intentional Stingray cellular omission so far | OEM-specific board and kernel reference harvest; design native camera path if feasible; modem safely managed or deliberately disabled; dock detection/charging tested |

**Important qualifiers:** Upstream presence of source code and Kconfig entries is NOT proof physical functionality. An MZ600 test is not yet an MZ604/MZ602 pass; keep common wiring common but board-specific identities, calibration, radio and RF policies scoped. The existing Linux DTS still carries upstream bugs/TODOs and should not be treated as inherently correct.

## Prioritized, nonduplicative work queue

### P0 — unblocking tests (mandatory before Wi-Fi/BT RF work)

- [ ] **P0.1** Recover repeatable Debian temporary boots from Android, preserving `fastboot boot` RAM-only workflow and USB COM9 control; verify known SHA and SD card PARTUUID.
- [ ] **P0.2** Instrument persistent evidence: SD-backed systemd journal/controlled initramfs breadcrumbs and kernel `ramoops`/pstore where safe; preserve kernel console and watchdog, panic, suspend, PMIC/button/USB events. Host PnP COM9 single-second disconnect is symptom, not crash proof.
- [ ] **P0.3** Audit source and OEM evidence of CPCAP ADC/power-button IRQ interaction, regulator shutdown, EMC RAM SKU timings, USB PHY/gadget and screen-off transitions. Test one hypothesis per boot with original-known-good control.
- [ ] **P0.4** Capture Android OEM configuration, firmware, circuit pin mapping and reference runtime for the affected components while it remains bootable. No eMMC writes.
- [ ] **P0.5** Build and DT-validate the *source-only* 25 MHz SDIO and Bluetooth 32k `lpo` fixes as separate reviewable patches. Do not interpret build success as physical validation or combine these with a crash-fix experiment.

### P1 — full Broadcom integration

- [ ] **P1.1 WLAN platform:** promote proven F2 bootstrap identity + true per-device ATAG/FDT identity and standard separate WCC module into reproducible clean builds; use existing `brcmfmac`, not a fork. Unprivileged userspace e.g. `iwd`/`wpa_supplicant`, `systemd-networkd` or NetworkManager; install missing system D-Bus if needed.
- [ ] **P1.2 WLAN regulatory:** verify signed `wireless-regdb` active in kernel, OEM MZ600 `US/69` firmware-country mapping acknowledged by firmware, board PA calibration, legal channel and TX limits. MZ600 US defaults must not be copied to all Xoom variants; verify actual PHY before RF tests.
- [ ] **P1.3 WLAN operational:** permitted scan, association/authentication, DHCP, throughput, reconnect, runtime unload/load, cold/warm startup, sustained operation and suspend/resume.
- [ ] **P1.4 Bluetooth firmware/transport:** configure `hci_bcm` with the verified Motorola BCM4329B1 HCD, native clocks/secure HCI identity, shared regulator semantics and correct serdev GPIO ownership; prove `hci0` full functionality through BlueZ, pairing, reconnection and profiles.
- [ ] **P1.5 Whole chip:** reconcile Motorola reference-counted shared U4 ownership and OR'd WL/BT REG_ON, separated resets, normal 38.4 MHz reference and 32k LPO; integrate existing Linux regulator/clk/pwrseq consumer interfaces with exactly one owner per pin, validating Wi-Fi only, Bluetooth only and both simultaneously, wake/suspend/restart.
- [ ] **P1.6 FM:** evidence-first schematic/OEM firmware/audio/antenna/transport audit. Implement standard V4L2/ALSA only if board support demonstrable; otherwise explicitly inert function with no bogus kernel device. No FM transmission experiments without regulatory/board approval.
- [ ] **P1.7 Generalize:** separate core/chip behavior from MZ600-specific DT, preserve factory calibration and IDs privately; validate on Wingray and other Xoom variants before claiming family support.

### P2 — remaining native OS acceptance

- [ ] **P2.1** CPCAP ADC/battery/charging and power-button IRQ; test accurate battery readings, charge states, low battery and watchdog.
- [ ] **P2.2** Display/backlight PWM, touchscreen blank/wake, accelerated graphics and standby.
- [ ] **P2.3** Audio codec, speakers, microphones, headphone jack and switching.
- [ ] **P2.4** Sensors, thermal trip behavior, RTC, LEDs, buttons, dock/USB host/OTG, and all usable cameras.
- [ ] **P2.5** Variant-sensitive EMC timing tables and power-state stability, plus cellular radio controlled safe state.
- [ ] **P2.6** Complete OEM reference inventory and restore images, test installation/recovery story; then and only then propose an eMMC Linux primary-OS layout and seek explicit authorization to overwrite Android.

### P3 — upstream contribution quality gates

- [ ] **P3.1** Keep each fix a minimal patch against exact xoom-linux upstream commit or a current upstream revision, not a wholesale independent driver copy.
- [ ] **P3.2** Run `make dtbs_check`, compile affected kernels/modules and static checks, inspect source-to-compiled DTB equivalence; capture reproducible logs from hardware.
- [ ] **P3.3** Mark proofs as SOURCE, BUILD, DEVICE REGISTER, RF FUNCTION, SUSPEND, or CROSS-VARIANT. Only make supported claims.
- [ ] **P3.4** Split DTS, MAC provenance, Bluetooth clock/shared-supply, WLAN regulatory/firmware-name and optional FM changes into reviewable logical commits; no private MAC, passwords, proprietary firmware binaries or captured Wi-Fi identities in Git.
- [ ] **P3.5** Submit upstream once patches are attributable, validated and appropriately licensed; retain XoomLinux7 development diagnostics separate from upstream shipping code.

## Direct upstream references

- [Wingray device tree](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dts)
- [Tegra defconfig](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/arch/arm/configs/tegra_next_defconfig)
- [Broadcom Bluetooth hci_bcm](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/bluetooth/hci_bcm.c)
- [Broadcom firmware country and DT parser](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.c)
- [CPCAP ADC WIP commit](https://github.com/xoom-linux/linux/commit/450c7de8a4c68324d9d18341c7c82f0133c903b5)
- Local physical evidence: `docs/checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md`, `MZ600_BASELINE_REPRODUCES_US69_USB_DROPOUT_2026-10-25.md`, `V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md`, `V033_BLUETOOTH_PHYSICAL_2026-10-24.md`, `docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md`.

**Summary:** Reuse the complete xoom-linux Wingray foundation and standard Linux frameworks. Our unique gaps are board-sensitive identity/firmware/regulatory integration, true Bluetooth and Wi-Fi radio operation with shared power correctness, and stable power/boot hardware acceptance. Stage source fixes separately, preserve Android until its OEM role is complete, and track evidence rather than duplicate previously proven experiments.
