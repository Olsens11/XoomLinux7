# Motorola MZ600 OEM Wi-Fi driver recovered — HRI39/HRI66 source and binary provenance

**Date:** 2026-10-24  
**Scope:** Source and artifact forensics only; replacement and protected Xoom hardware not rebooted, flashed, or modified in this investigation.  
**Priority:** Linux 7 BCM4329 native Wi-Fi F2 startup; Bluetooth/FM are shared-chip resource considerations.

## 1. Correct the OEM generation boundary

The October 21 private OEM archive on Raspberry Pi (`/home/ps2/xoom-phase1/private/oem-reference-20261021/`) preserves two **actual early MZ600 Android builds**, HRI39 and HRI66, as ext4 `system.img` and Android `boot.img`. Direct read-only inspection established:

| Artifact | HRI39 | HRI66 | Comparison |
| --- | --- | --- | --- |
| Kernel | Linux `2.6.36.3-g2a65edc` (Feb 7 2011) | same | identical extracted zImage SHA256 prefix `511deaf56bc064e2` |
| `/system/lib/modules/bcm4329.ko` | 264,038 bytes | 264,038 bytes | **SHA256 identical** `4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f` |
| `/system/vendor/firmware/fw_bcm4329.bin` | 261,317 bytes | same | identical SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a` |
| `fw_bcm4329_apsta.bin` | 249,307 bytes | same | identical hashes |
| `fw_bcm4329_mfg.bin` | 262,058 bytes | same | identical hashes |
| `/system/etc/wifi/bcm4329.cal` | present | present | device-unique content **not published** |
| `/system/etc/firmware/bcm4329.hcd` | present | present | proprietary binary **not published** |

**The older MZ600 OEM driver is a loadable `bcm4329.ko`, not the later `CONFIG_BCMDHD=y` built-in driver.** The separately archived `sources/wingray/kernel` unpacks to Linux `2.6.39.4-g4e32b94` and contains BCMDHD symbols and `fw_bcmdhd.bin` / `bcm4329.cal` references. Treat these as **two distinct OEM generations**. Do not describe a 2.6.39 defconfig as the proven build configuration for 2.6.36.3 HRI39/HRI66.

## 2. Original kernel-module identification

The HRI39/HRI66 `bcm4329.ko` copies are relocatable ARM EABI5 ELF modules, not stripped, with symbol table and limited debug sections. `modinfo` confirms:

- `vermagic: 2.6.36.3-g2a65edc SMP preempt mod_unload ARMv7`
- Broadcom SDIO modalias includes vendor `02D0`, devices `4329` and `4319`
- Functions include `dhd_module_init`, `dhd_bus_start`, `dhd_bus_init`, `dhdsdio_download_firmware`, `dhdsdio_download_state`, `bcmsdh_sdmmc_probe`, `wifi_set_power` and `wifi_set_carddetect`
- Debug compile-unit path: `/usr/local/google/kernel/android-tegra-moto-2.6.36/tegra-moto/drivers/net/wireless/bcm4329/bcm4329.mod.c`.

That last path is a build-path reference, **not** confirmation that the module embeds the complete corresponding driver C source.

## 3. Pinned exact-generation Motorola source

Public Android Tegra Git repository accepts historical commit **`2a65edc`**, matching the kernel version suffix. Relevant files were individually fetched by Gitiles into the **private** Pi reference workspace, with their source digests:

| Motorola source at `2a65edc` | SHA256 |
| --- | --- |
| [`dhd_linux.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_linux.c) | `d9eaaad014d25fbac09c46e92ff09c0c70aefa027f657d2979e088fc9d44ae92` |
| [`dhd_sdio.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/dhd_sdio.c) | `e8ad9ef7bac25f6ba82140e1b44387ce537bd484bfbfe38289b923eadba2d016` |
| [`bcmsdh_sdmmc_linux.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/bcmsdh_sdmmc_linux.c) | `71045837a31be59c21adda19f4b74ac6f88743d1712e9ad4ff77f6d192044410` |
| [`board-stingray-wifi.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray-wifi.c) | `e8b92a268bca6bc1c7798159d731117022223c45e8926b7307987e9b74ccb494` |
| [`board-stingray.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray.c) | `916df985cbba4d5abc855772388042dd6d0f9f99418dcbd6e452fbb35d0b63e7` |

The revision, symbol families, and historical build path establish a **strong provenance match**. Bit-for-bit source-to-module reproducibility has **not** yet been demonstrated and must not be presumed.

## 4. Reconstructed original MZ600 Wi-Fi startup path (source derived)

1. **`dhd_module_init()`** in `dhd_linux.c`, ~2531: customer power callback call; with board-control build flags, register platform driver, await `wifi_control_sem`, then register SDIO bus driver and await attachment.
2. **`wifi_probe()`**, ~126: register IRQ resource and board callback pointer, call `wifi_set_power(1,0)` **before** `wifi_set_carddetect(1)`, then release the platform semaphore.
3. **`stingray_wifi_power(1)`** in `board-stingray-wifi.c`, ~155: delay 100 ms, call `change_power_brcm_4329(1)`, delay 100 ms, drive Tegra U2 WLAN reset released, delay 200 ms. `stingray_wifi_set_carddetect(1)` sets logical presence and notifies registered MMC callback.
4. **`dhd_bus_register()` / SDIO attach**: `dhdsdio_probe()` establishes bus/core and interrupts; at `dhd_sdio.c` ~4899 it calls `dhd_bus_start()`.
5. **`dhd_bus_start()`**, `dhd_linux.c` ~2176: if bus down, invoke `dhd_bus_download_firmware()`, then invoke `dhd_bus_init()`, and verify final state `DHD_BUS_DATA`.
6. **`_dhdsdio_download_firmware()`**, `dhd_sdio.c` ~5615: `dhdsdio_download_state(TRUE)` keeps ARM in reset; download firmware code from chosen path; download NVRAM; `dhdsdio_download_state(FALSE)` releases ARM.
7. **`dhd_bus_init()`**, `dhd_sdio.c` ~2723: request backplane clock, set `SBSDIO_FORCE_HT`, write SDPCM version to mailbox, request F1+F2 via CCCR IOEx, poll IORx against both enabled bits, and only on ready configure interrupt mask and enter `DHD_BUS_DATA`.

**This is the actual same-generation Motorola source call chain**; whether every conditional compile path was active in the shipping module still requires compiled-config/call-site proof. The raw firmware files and .cal values must remain private. The measured Linux 7 failure IOEx `02→06`, IORx remains `02`, marks the precise readiness boundary shared with this OEM code.

## 5. Shared supply semantics

`change_power_brcm_4329(bool)` at `board-stingray.c` ~894 serializes U4 access with `spin_lock_irqsave`. Enable drives U4 high and increments count (saturating at two); disable decrements if positive and only drives U4 low at zero. It is a shared vote **without typed consumer ownership**. Cross-subsystem order must be traced, rather than assuming all counter transitions reproduce a cold POR.

In the same original `dhd_linux.c`, `wifi_remove()` calls power-off then carddetect-off; `dhd_module_cleanup()` unregisters the SDIO bus then removes the platform driver. Driver and platform callbacks must be compared against the actual module parameters and compilation flags.

## 6. Implications for Linux 7 and next exact evidence gates

- Treat **2.6.36 MZ600** as the first-order baseline; study later **2.6.39 Wingray/BCMDHD** as an evolutionary, separately versioned reference.
- Use the actual OEM Wi-Fi firmware binary `fw_bcm4329.bin` and matching *same-device* calibration as **private** reference inputs; do not publish binaries or identity data.
- Compare original SDIO/PMU/CPU activation transitions to Linux 7 `brcmfmac` before changing timings. Firmware transfer/readback alone is not proof of firmware CPU execution.
- Recover active compile flags/config and source-to-symbol provenance for `bcm4329.ko`; inspect exact code around `dhdsdio_download_state`, PMU setup and failed F2 path, both OEM and Linux 7.
- Establish whether the device boots in an inherited powered state and whether U4+I7 can ever simultaneously request true internal regulator off; distinguish regulator vote from physical power state.
- Compare suspend/resume, error recovery, and Bluetooth vote ordering in the original 2.6.36 branch before hardware activation.
- Protected original Xoom remains untouched; replacement currently remains on temporary Linux v034 per latest verified [checkpoint](../checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md). **This research did not live-check its current state.**

**Evidence classification:** extracted OEM ext4 paths, byte sizes, binary hashes, ELF attributes, and Linux version are **artifact verified**; source functions and callback order are **source verified**; physical pad voltages, OEM runtime event order, compiled conditionals, and firmware execution remain **open**.
