# v040 research and blocked MAC bootstrap diagnostic — exact Motorola pre-F2 MAC requirement

**Date:** October 24, 2026. **Status:** Motorola same-generation source, Makefile and original OEM binary **verified**; private Linux/OEM NVRAM comparison **verified**. Attempt to upload experimental `macaddr` NVRAM **blocked on Surface host before transmission** by existing NVRAM identity/regulatory guard. **No v040 NVRAM physical F2 test occurred.** No flash/reboot/power change; original Xoom untouched, replacement Xoom remains v034 temporary boot with generic firmware and original NVRAM.

## Why the MAC question is credible

The precise source is [Motorola Tegra kernel 2a65edc `drivers/net/wireless/bcm4329/dhd_common.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_common.c), lines **1223–1262**, `dhd_preinit_ioctls()`. Before invoking `dhd_custom_get_mac_address`, Motorola/Broadcom documents:

> NOTE that default mac address has to be present in otp or nvram file to bring up firmware but unique per board mac address maybe provided by customer code

This is a **source-comment statement about the OEM driver/firmware requirements**, not proof that the replacement Xoom lacks a valid OTP address, nor that all versions of modern brcmfmac require an NVRAM MAC. Significantly, `dhd_preinit_ioctls` subsequently uses `cur_etheraddr` **after firmware startup** to override with a per-board address; it is not an alternative to the initial default address in OTP or NVRAM.

Original [`dhd_custom_gpio.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_custom_gpio.c) lines 153–179 contains the conditional implementation of `dhd_custom_get_mac_address`, forwarding to `wifi_get_mac_addr` under `CUSTOMER_HW2`; [original `Makefile`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/Makefile) sets `-DCUSTOMER_HW2` and `-DGET_CUSTOM_MAC_ENABLE`. The actual HRI39/HRI66 **264,038-byte original `bcm4329.ko`** contains symbols `dhd_custom_get_mac_address`, `dhd_preinit_ioctls`, and `wifi_get_mac_addr`. Together, these give unusually strong source-to-binary proof of this original path (not a fully reproduced call-time trace).

The original [`board-stingray-wifi.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray-wifi.c) lines ~178–225 receives an **`ATAG_STINGRAY_MAC`** bootloader parameter with ID `0x57464D41` and offers the resulting unit-specific MAC through `stingray_wifi_get_mac_addr` and platform `.get_mac_addr`. Its source also contains a fallback suffix generated if not provisioned; **that fallback is not an accepted permanent identity strategy for portable Linux 7**.

Original 2011 OEM calibration has 54 distinct keys including `macaddr`, `ccode`, and `regrev`; current Linux reference has 51 distinct keys; **all 51 shared keys/values match byte-for-byte** in the reference text (not proof of same unit/actual runtime NVRAM consumption). Thus `macaddr` omission is a sharply scoped potential prerequisite. There is no `.get_country_code` platform callback in **this pinned 2.6.36 board source**. Country/revision fields exist in NVRAM, with regulatory handling separate.

## Existing safety guard blocked v040 BEFORE device file upload

The proven Surface host script `scripts/host/surface/Xoom-v34-BluetoothLiveLab.ps1`, approximately lines 120–124, rejects any `-Kind NVRAM` whose text contains a `macaddr`, `ccode`, or `regrev` assignment:

```powershell
if($text -match '(?im)^\s*(macaddr|ccode|regrev)\s*='){
  throw 'NVRAM contains device identity or country/regrev override'
}
```

A **private one-time locally administered unicast test-MAC** was generated on Surface in a copy of the original NVRAM (1576 bytes vs 1550 baseline; neither value nor actual temporary identity printed or published). The guarded upload reported **`NVRAM contains device identity or country/regrev override`** and exited **before `UPLOAD READY BYTES` or any USB data transfer**. There is therefore **no MAC/F2 experiment result** from v040. The temporary test-MAC file was deleted afterward; existing generic NVRAM rollback text retained privately. Do not bypass the guard or use a foreign MAC to obtain false confidence.

## Modern Linux per-unit MAC delivery and bootloader handoff

The pinned Linux 7 [`brcmfmac/firmware.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c), `brcmf_fw_nvram_strip()`, already supports per-platform MAC override via `eth_platform_get_mac_address(dev, mac)` and injection into the packed NVRAM. However, a search of our existing XoomLinux7 DTS/source has not identified a populated `mac-address` / `local-mac-address` or matching NVMEM provider for the replacement MZ600. A source search alone does not prove the actual machine has no other physical MAC source (chip OTP/SROM, bootloader tags, etc.).

The existing Linux 7 build config on desktop has **`CONFIG_ATAGS=y`**, **`CONFIG_ATAGS_PROC=y`**, and **`CONFIG_ARM_ATAG_DTB_COMPAT=y`**, with arm32 `atags_to_fdt` support present. Those kernel options make a **read-only /proc/atags or bootloader-handoff forensic** worth testing, but *do not prove the bootloader actually supplied the proprietary `ATAG_STINGRAY_MAC` tag or that Linux preserved it*. The v034 USB diagnostic interface currently has no command specifically reading that tag; `MMC2_STATUS` only checks controller/device binding, not MAC provenance.

**Important cross-build portability:** any future production Linux7 solution must derive the actual tablet's address from a legitimate, unit-specific factory or bootloader source, maintain a stable locally-administered fallback only when appropriate, and apply correct regulatory data separately. Never publish identifiers, hardcode a donor Xoom's MAC, or defeat host protections without an independently reviewed explicit per-device authorization path.

## v040 final verified state

The guarded `macaddr`-bearing NVRAM upload was **refused before any bytes were transmitted**; no new firmware or NVRAM activated. After deleting the experimental file, final guarded USB `MMC2_STATUS` on COM9 returned **TARGET VALID**, **BOUND YES**, **CARD BCM4329 VERIFIED**, **DRIVER MODULES UNLOADED**, and MMC2 AUTO profile 0. Known generic firmware had already been restored in v039 with 253748-byte upload CRC32 B4092AA6; no reboot or flash.

## Next safe and discriminating work

1. **Read-only first:** determine whether `/proc/atags` actually exists in the v034 temporary boot, parse binary ARM tag headers **without printing MAC bytes**, and report whether `0x57464D41` is present and has exactly six valid payload bytes. If not, inspect other legitimate OTP/NVMEM/bootloader sources through safe reads, separately distinguishing source verified versus device verified.
2. If legitimate per-unit identity is recovered, design and review a narrowly scoped firmware bootstrap MAC injection into the existing `brcmf_fw_nvram_strip` / platform provider path, not an override of the generic host's safety guard. The test should remain one-variable, RAM-only, reversible and prohibit RF association; preserve original generic firmware and NVRAM for rollback.
3. If no default MAC is present in OTP, then the original OEM source comment makes missing `macaddr` a plausible explanation for F2 failure, but **it remains only a hypothesis until physically falsified**. If present, look elsewhere.

**Acceptance labels:** original Motorola MAC requirement / build flags / compiled symbols verified; generic-reference equality verified; host guard denial verified; **MAC F2 physical test not performed**; device stable and driver unloaded.
