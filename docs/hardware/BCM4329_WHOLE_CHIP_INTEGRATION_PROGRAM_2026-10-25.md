# BCM4329 whole-chip integration program — Stingray Linux 7

**Created:** 2026-10-25. **Branch:** `wip/bcm4329-whole-chip-integration-20261025`.
**Status:** Source-only corrections; NO Linux image rebuilt, deployed, booted or flashed in this branch. Not a claim of functional RF. Mainline and current working OS branch unchanged.

## Project acceptance principle

Achieve full *native Linux 7* support for the BCM4329 combination device and submit narrowly scoped, reviewable changes to xoom-linux/linux. The original Android installation stays intact as OEM evidence until its relevant board/firmware/configuration details are documented and Linux functions have been physically validated. The Linux microSD image is a development environment; eventual primary OS resides on eMMC. Do not hardcode a particular test-unit MAC or country into family-wide code.

## Latest physical state and boot blocker

The known-good Debian 12 ext4 microSD boot previously ran PID1 systemd, USB ttyGS0/COM9 and separate upstream `brcmfmac_wcc` + `brcmfmac`, with `wlan0` present and the dynamic ATAG/FDT/interface MAC matching. No RF scan, connection or coexistence was demonstrated. On Oct 25 BOTH that exact original temporary boot image and a separate US/69 DTB variant showed about one second of USB COM9 enumeration followed by disappearance. The user currently sees a black/off screen, and pressing power briefly blinks a red LED near the camera. Read-only Surface present-device enumeration shows no currently connected Motorola Xoom, COM9 or Linux gadget. Cause unknown; do NOT ascribe to US69, Wi-Fi or Bluetooth without logs. Android previously recovered via Power+Volume Up. Do not issue more uncontrolled boot loops.

First capture a real console/SD-persistent journal/ramoops record of the failure with bounded diagnostics. A non-booting host invalidates Wi-Fi/BT acceptance testing. Preserve original known-good boot SHA256 c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c, full microSD root, existing Android/TWRP partitions and OEM references. No internal eMMC writes or Radio TX.

## Architecture and ownership

| Function | Kernel integration | Hardware gates / work |
| --- | --- | --- |
| Shared combo-chip power | Standard regulator, clk and (if consumers can cooperate) Linux pwrseq, **single GPIO owner** | OEM U4 WLAN/BT shared vote vs I7 BT_REG_ON; U2 WLAN reset vs U0 BT reset; 32.768 kHz LPO; 38.4 MHz reference, power/suspend/resume sequences |
| WLAN | Upstream SDIO MMC host + pwrseq; `brcmfmac` + distinct `brcmfmac_wcc`; `cfg80211`/`nl80211` | SDIO F2 err=0 on physical v044, `wlan0` on v045 and Debian. Exact per-device MAC via bootloader ATAG/FDT; legitimate board NVRAM and regulatory mapping; safe scan, authentication, DHCP, connection, roaming, coexistence and lifecycle tests |
| Bluetooth | Upstream UART serdev + `hci_bcm`/`btbcm`/BlueZ | v033 physically recognized BCM4329B1 HCI, shared U4 votes observed, but Motorola-specific `bcm4329.hcd` patch was not loaded. OEM HRI39/HRI66 patch 17,770 bytes differs from LibreELEC patch 17,332 bytes; firmware is separate from WLAN .bin. Validate chosen firmware, address, scan/connect/pair, audio profiles, RF coexistence, suspend and regulator release |
| FM RX/TX | **Potential** Broadcom FM function behind HCI or I²C; if truly connected, implement standard V4L2 radio interface and ALSA/ASoC audio routing with normal kernel resource management | Silicon supports FM and RDS, but OEM MZ600 antenna/RF path, FM pin supply, I²C or vendor HCI opcode support, interrupt/audio wiring and routing are NOT established. Do not invent live device-tree resources or claim a driver from silicon capability alone. FM TX is deferred pending radio/regulatory/board qualification; no over-the-air TX experiments |

Do not turn the BCM4329 into a monolithic Linux Wi-Fi/BT/FM protocol driver. Use normal interfaces and only add board/chip-specific coordination where necessary. Avoid duplicate ownership of U4, U2, U0, I7, clocks or supplies. The `src/chip/stingray-bcm4329-pwrseq.c` code is an unlinked compile-only prototype lacking live MMC and HCI consumers; enabling it is not a fix until those consumer connections and DT binding are valid.

## Already-established important evidence

- v043 private firmware console showed `Failed to init wireless side, err: 21` with MAC-free NVRAM.
- v044 one-field authentic generic Motorola bootstrap MAC in private NVRAM made SDIO F2 ready (`err=0`); v045 loaded `wlan0` by temporary WCC-inline packaging. Production userspace uses the separate WCC module, and private *per-device* MAC is passed via the bootloader FDT route. Bootstrap identity and unique hardware identity are **different purposes**.
- Motorola OEM board driver applies a reference-counted shared-U4 power vote for Wi-Fi and Bluetooth. v033 proved HCI identification under a temporary Motorola-gated shared-vote driver, not complete Bluetooth operation.
- The 32.768 kHz Tegra PMC `CLK_BLINK` previously labeled Bluetooth `txco` is LPO, not the 38.4 MHz reference. Source-only correction is appropriate but still requires boot and power-state validation.
- BCM4329 SDIO default/legacy transfer clock rating is at most 25 MHz; current board source previously allowed 46,153,846 Hz. Controlled physical legacy 25 MHz v022/v025 tests operated but did not alone fix F2 (which turned out to need bootstrap identity).

## Source-only changes in this topic branch

1. Both MZ600 Stingray DTS variants limit `sdmmc2` `max-frequency` to **25,000,000 Hz**, leaving the existing host parent assignment otherwise untouched. Gate any future >25 MHz setting on demonstrated high-speed negotiation; benchmark throughput only after RF works.
2. Both MZ600 DTS variants relabel the Bluetooth 32.768 kHz PMC `CLK_BLINK` clock from `txco` to **`lpo`**. This does not establish the separate 38.4 MHz normal reference input or complete Bluetooth power sequencer.

These are candidate MZ600 board-description corrections, not a proven fix to the current boot problem or confirmed universal Xoom-family properties. Before upstream submission: build a DTB, run DT validation with the Linux 7 bindings, compare actual boot DTB to source, validate on hardware and inspect other Xoom models. The user's main/OS working branches remain untouched.

## Planned physical acceptance gates (no bypass)

1. Restore stable Debian boots, capture boot/suspend/panic evidence and test cold/warm repeatability. Preserve Android OEM reference until done.
2. WLAN: signed wireless-regdb accepted, OEM US-market MZ600 country/regrev verified against firmware, legal radio limits; `wlan0` has unique per-device identity; scan, connect, WPA2, DHCP, bidirectional data, uptime and power cycling; compare other variants.
3. Bluetooth: genuine Motorola patch provenance and loading; correct HCI controller address; BlueZ discovery, pairing, reconnect, profiles and concurrent Wi-Fi, suspend/wake, independent and joint chip power cycles.
4. FM: identify actual MZ600 FM RF antenna, supply/clock, pinmux/control transport, vendor opcodes, IRQ and analog/digital audio connections from OEM board source, electrical references or board inspection. Model absent wiring explicitly; add FM function driver only with hardware and control-path evidence. Test receiver first; do not transmit until legally and electrically qualified.
5. Shared state: stop/start each function separately and in combinations. Assert no double GPIO ownership, leaks, broken LPO, unintended chip shutdown or dangling wake votes. Repeat on MZ604/MZ602 where possible before generalization.
6. Split patches into logical upstream-sized commits: board DTS clock, calibrated firmware-name/identity plumbing, BT HCI shared-resource refcount or pwrseq consumer, optional FM interface, Kconfig/bindings/tests. Mark each source review, compile, live test and multi-model verification independently.

## Grounded references

- `docs/checkpoints/MZ600_BASELINE_REPRODUCES_US69_USB_DROPOUT_2026-10-25.md`
- `docs/checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md`
- `docs/checkpoints/V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md`
- `docs/checkpoints/V033_BLUETOOTH_PHYSICAL_2026-10-24.md`
- `docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md`
- `docs/research/MZ600_BCM4329_REGULATORY_OEM_LINUX7_AUDIT_2026-10-25.md`
- `docs/research/MZ600_BCM4329_FIRMWARE_LAYOUT_AND_BLUETOOTH_HCD_AUDIT_2026-10-24.md`
- BCM4329 149-page Cypress/Broadcom data sheet, Section 6 p35, Section 11 and shared-power/reset drawings; Linux kernel power sequencing docs, Broadcom Bluetooth UART DT binding, V4L2 radio API.
