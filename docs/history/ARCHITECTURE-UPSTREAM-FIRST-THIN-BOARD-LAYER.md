# Architecture decision: upstream-first, minimal board support (2026-10-23)

## Objective
Develop a portable, maintainable native ARMv7 Linux environment for Motorola Xoom MZ600 / Stingray, respecting and building upon upstream Linux, open Xoom device-tree / kernel work, OEM reference evidence and our proven TWRP recovery toolkit. Keep the interface between hardware and mainstream Linux as thin as the hardware permits.

## Architectural boundaries
1. **Use existing Linux drivers and subsystem APIs by default.** Tegra SDHCI + MMC/SDIO; Broadcom `brcmfmac` + cfg80211/nl80211; `atmel_mxt_ts` + input/evdev; DRM/KMS/fb as supported; ALSA/ASoC; USB gadget; regulator, GPIO, RTC, power_supply, thermal, clocks, and device-tree bindings.
2. **Board-specific integration is declarative where possible:** upstream-quality Stingray DTS/DTSI changes for actual GPIO polarity, supplies, pinctrl, clocks, regulators, SDIO power-sequencing, calibration/firmware identifiers and per-device data sources. Keep the main kernel generic; avoid patching core Linux subsystems.
3. **Any necessary code changes should be minimal, well-scoped, and upstreamable** drivers or binding fixes, not an Android-compatibility shim or proprietary interface. Establish independent evidence on hardware before altering board logic. Review upstream conventions and maintain authorship/license provenance. Contribute practical improvements upstream when appropriate.
4. **Hardware identity belongs to each device.** No reference-device Wi-Fi MAC in shared kernel, DTB, firmware, initramfs, default rootfs, logs or public artifacts. Read current Xoom's factory identity from hardware or established per-device source via standard Linux mechanisms; compare with Android/OTP evidence; do not mistake firmware defaults or locally generated addresses for a verified factory MAC.
5. **Firmwares and board calibration are distinct.** Mainline BCM4329 firmware is preferred if compatible; board NVRAM comes from trustworthy board evidence with device-unique lines excluded; regulatory/country parameters must be correct for jurisdiction and kernel regulatory subsystem, not blindly inherited from `ccode=XY` recovery or `ccode=US` OEM template. No transmit/association until identity and applicable regulatory settings verified.
6. **Keep the diagnostic program a temporary development tool, not a mandatory HAL.** Final ARMHF Linux userland uses standard interfaces, standard tools, normal packaging, and open firmware/config provenance. The Xoom could run minimal busybox or Debian without a custom toolkit service.
7. **Hardware preservation and testing:** use only explicit replacement MZ600 serial `170061c243805617`; the original reference device `02804102421F7517` is read-only. Preserve boot/recovery/logo through nonpersistent fastboot boot until proven safe rollback. Cross-compile no-NEON ARMv7; USB serial as debug fallback.
8. **Respect project ancestry:** distinguish Linux upstream, existing Tegra/Stingray ports, Motorola BSP/OEM artifacts and our own additions in history and documentation; honor licenses and submit generalizable corrections upstream.

## Current native Wi-Fi checkpoint
v08 RAM-only Linux boots, USB CDC serial and touch UI operational. Tegra SDHCI mmc2 enumerates Broadcom SDIO card with three functions. Upstream `brcmfmac` detects **BCM4329 revision 3** and requests firmware `brcm/brcmfmac4329-sdio`; no `wlan0` yet. Firmware binary and a MAC-free/ccode-free board reference are built into kernel. Early kernel logs note `cfg80211: failed to load regulatory.db`, but this alone doesn't explain why no network interface. Next inspect SDIO function driver binding, asynchronous firmware request/response, firmware runtime and regulator/clock sequencing using upstream logging **before** adding any hardware shim or changing GPIOs. Read-only stock Android on replacement confirms valid unicast global wlan0 MAC when Wi-Fi is enabled; it is saved privately on Surface for comparison after Linux wlan0 appears.

## Primary references
- Desktop WSL `/home/xoomdev/xoom-linux-rom/linux-src`, Linux source pinned `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
- Desktop `C:\Users\olsen\XoomLinux\Phase1\MZ600-native-WiFi-OEM-recovery-portability-plan-2026-10-23.md`.
- Pi `/home/ps2/xoom-phase1/`, original Android Wi-Fi firmware and OEM reference extractions documented there.
- Surface `C:\Users\olsen\xoom-linux-rom\captures\MZ600-170061C243805617\v08-filtered-early-boot-wifi.txt`.
