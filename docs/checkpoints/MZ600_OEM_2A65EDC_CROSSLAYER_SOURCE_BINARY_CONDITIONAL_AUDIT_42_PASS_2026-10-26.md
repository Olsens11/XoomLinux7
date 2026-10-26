# MZ600 original Motorola 2a65edc — complete-source interaction audit (42/42 source and ELF checks PASS)

2026-10-26. Offline-only inspection on authorized Raspberry Pi ps-to-vnc-dev of *actual HRI39 OEM driver* and pinned Motorola original source. Current Linux 7 source compared read-only on Desktop. **No device/radio, firmware, GPIO, reboot, or regulatory operation.** Companion project-wide design: [Motorola OEM cross-layer system audit](../research/MZ600_BCM4329_MOTOROLA_OEM_WORKAROUND_CROSS_LAYER_SYSTEM_AUDIT_2026-10-26.md).

## Strong provenance and reproducibility

- Actual early MZ600 HRI39/HRI66 Linux kernel is 2.6.36.3-g2a65edc. Matching-generation Motorola public kernel source is **2a65edc**; do not merge it with later 2.6.39 BCMDHD and July 2011 Motorola commits.
- Real HRI39 compiled bcm4329.ko is 264,038 bytes SHA256 **4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f**, verified on the Pi before deriving symbols.
- New [fail-closed source+ELF verifier](../../tools/forensics/audit_mz600_oem_system_lifecycle.py) locks down seven source file SHA256 hashes and OEM module hash, checks exact branch functions/conditionals, then validates original compiled ELF symbols.
- Actual on-Pi execution: **42/42 PASS, 0 FAIL**. Sanitized local JSON: /tmp/mz600-oem-crosslayer-checks-20261026.json; SHA256 **830cb83239f4b084e3a60324510702a77bda06f45cbdb4fff7487ba4ce9ccd3d**. No private firmware, NVRAM, per-device MAC or Bluetooth pairing data in result.
- Exact original Makefile SHA256 **57260ea887ef12166a87083046d0dc03a84ba4145935ca4ae592f63599dafec0**; dhd_custom_gpio.c SHA256 **3be537d72d2426ac56f2c4b397272f07b6b1276865fb2be557121da81ac873e5**. Existing pinned original driver/board/siutils hashes matched.
- Reproduction: python3 tools/forensics/audit_mz600_oem_system_lifecycle.py --oem-root [private extracted source-2a65edc directory] --oem-module [private HRI39-bcm4329.ko path] --json [new output JSON path].
- **Proof level:** source-byte, textual control ordering, and compiled ELF symbol presence. It is NOT evidence that each compiled callback was invoked on boot, every hardware waveform occurred, or later OEM Bluetooth behaviors were present.

## Major newly proven compiled-condition resolution

- Early MZ600 Makefile includes -DCUSTOMER_HW2, -DGET_CUSTOM_MAC_ENABLE, -DOOB_INTR_ONLY and -DHW_OOB.
- Exact-generation dhd_linux.c lines 64–191 include wifi_probe, wifi_remove, wifi_set_power, wifi_set_carddetect, wifi_add_dev and wifi_del_dev **only under CUSTOMER_HW2 AND CONFIG_WIFI_CONTROL_FUNC**. The real HRI39 ELF includes *all these function symbols*; thus this platform-control code was COMPILED into the original shipped driver. Runtime call frequency remains unmeasured.
- dhd_module_init invokes generic dhd_customer_gpio_wlan_ctrl(WLAN_POWER_ON), THEN registers Wi-Fi platform driver/waits semaphore, THEN registers SDIO driver. Crucial: **under CUSTOMER_HW2, generic WLAN_POWER_ON and POWER_OFF cases in dhd_custom_gpio.c do not call wifi_set_power or make a second U4 vote**. Those case bodies only call customer physical power helpers under a *different CUSTOMER_HW* conditional. The platform wifi_probe → wifi_set_power is the intended physical activation.
- Distinct WLAN_RESET_ON/OFF cases under CUSTOMER_HW2 DO contain wifi_set_power calls, but a grep of the available pinned Broadcom subtree found no corresponding direct call to the generic hook with RESET_ON or RESET_OFF; external callers and actual runtime are not proven absent.
- wifi_probe: wifi_set_power(1,0) BEFORE wifi_set_carddetect(1). wifi_remove: wifi_set_power(0,0) BEFORE wifi_set_carddetect(0). These are exact early OEM rules; do not transpose later Broadcom teardown order.
- dhd_module_cleanup first unregisters SDIO bus, THEN unregisters Wi-Fi platform driver, which invokes platform removal when bound; init failure uses distinct fail_2/fail_1/fail_0 unwinds, not a generic module-stop shortcut.

## Fully connected source-to-Linux mapping

| Original stage and source location | Source/ELF grounded behavior | Modern Linux 7 mapping or gap |
| --- | --- | --- |
| Board GPIO prepare: board-stingray-wifi.c ~239–255 | U2 reset requested output LOW, U5 IRQ input; platform device registered | MMC2 pwrseq U2 and U5 IRQ in DTS; compare actual pre-power chronology |
| Host SDMMC2 calibration: board-stingray.c ~925–934 | Tegra controller sdhci-tegra.1 **tap delay = 6** chosen for trace propagation | **Positive source match:** v06.4 tegra20-motorola-stingray-clean-usb.dts sdmmc2 has nvidia,default-tap = 6 (line ~1319). Do not patch this as missing. Live register readback remains separate |
| Motorola six-field SDIO workaround: board-stingray-wifi.c ~91–153 | Incorrect reported SDIO version 1 corrected to sdio_vsn=2, multi_block=1, low_speed=0, wide_bus=0, high_power=1, high_speed=1. OCR 1.65–1.95V, built-in flag, logical card-detect status/register callback | Controlled **v018 PHYSICAL** applied all six fields and host negotiated high-speed, but firmware F2 still -62 twice. Current working v06.4 MMC core has no v018 code. Necessity for 5GHz not established |
| DHD module init: dhd_linux.c ~2530–2610 | Under compiled conditions: generic GPIO hook (no second HW2 vote) → platform registration + wait → SDIO registration + wait | Linux7 built-in MMC platform/pwrseq and modular brcmfmac differently ordered; log actual supply stable / first CMD5 only if investigating |
| Platform probe: dhd_linux.c ~119–141 | Power ON callback before logical card-detect ON | Modern SDIO enumeration/pwrseq does not natively duplicate this callback |
| Power delay: board-stingray-wifi.c ~155–168 | 100ms → U4 shared vote → 100ms → U2 reset release → 200ms | Current U4 regulator-boot-on, MMC pwrseq 300ms, CLK_BLINK LPO. Internal POR, BT I7 and supply settlement need independent evidence |
| Shared physical power: board-stingray.c ~894–913 | Spinlocked untyped shared U4 count, saturated at 2, U4 LOW only when count goes zero | Generic fixed regulator + proposed named WLAN/BT pwrseq owner; do not reproduce untyped U4 vote bugs |
| Firmware loading / F2: dhd_sdio.c | ARM/SOCRAM reset, firmware + NVRAM, ARM release, SDPCM HT clock/mailbox, F2 IOEx/IORx | Modern equivalent mostly exists. v043 console exposed missing bootstrap identity; v044 one-field NVRAM correction made F2 ready; v045 WCC then wlan0 |
| PMU/ChipCommon: siutils.c | OEM firmware is allowed PMU init; conditional GPIO pull-up/down clearing | Current Linux requests PMU RES_RELOAD and differs in pull cleanup; physical readback and cross-function safety required before any change |
| Firmware bands / calibration | Original per-board calibration includes aa5g, PA fields and US country/rev; per-device ATAG factory MAC separate from startup MAC | Current generic firmware 4.220.48 actually reports one 2GHz band and exactly 11 2GHz chanspecs; 5GHz remains missing despite Android history. Compare OEM FW/NVRAM pair and country handling before any patch |
| Normal teardown: dhd_linux.c ~2520–2530 | First unregister SDIO, then unregister platform, platform remove drives power OFF before card-detect OFF | Current WCC-first module unload is clean, but shared internal chip power-down not proven |
| Runtime reset: dhd_sdio.c ~5733 onward | dhd_bus_devreset stops watchdog/bus, releases dongle, and on restart resets client, reattaches, re-downloads FW and enables F2 | Standard Linux module unload/reload is NOT proven equivalent to firmware devreset or full PMU POR |
| Suspend/resume: dhd_linux.c ~529–629 | Platform wifi_suspend and wifi_resume are no-ops; **separate dhd_set_suspend exists in shipping ELF** and changes WLC_SET_PM, packet filters, DTIM and roam_off | Cannot conclude OEM Wi-Fi suspend is a no-op; compare with Linux7 cfg80211 and WLAN/BT power ownership under suspend |

## Exact original vs later Bluetooth generation caveat

Early 2a65edc board-stingray.c registers a bcm4329_bluetooth platform device. The cached *early* source subset currently lacks the entire corresponding Bluetooth rfkill implementation. The extensive U4/I7/U0 BT rfkill callback reconstruction in existing Motorola callgraph also uses later 2011 Motorola source. **Do not silently claim those later callback internals ran in HRI39.** Recover exact-generation BT source and original compiled module/config before assigning its implementation the same provenance as the Wi-Fi driver.

## What this changes in our patch strategy

- Current 2.4GHz wlan0 and 19-BSS scan work; the owner-confirmed old Android 5GHz association means software configuration is the primary research target.
- The six-field workaround was *real* and originally compiled in the OEM board, but it has already been physically tested and shown insufficient for a previous F2 issue. Do not apply the same quirk on an assumption it fixes 5GHz.
- The exact original Makefile+ELF resolve previously uncertain customer power/control compile branches and avert an incorrect duplicate-U4-vote model.
- Current DTS **already reproduces OEM tap=6**; avoid pointless re-patching this verified source match.
- Firmware 5GHz absence is measured at the **firmware GET_BANDLIST/chanspec API**. Investigate genuine Motorola firmware and its matching startup/regulatory/calibration sequence; leave signed DB, device-unique MAC and RF safety limits intact.
- The proposed Linux7 whole-chip pwrseq owner/BT cohabitation and multiprocessor test series remain independent and unqualified. No upstream review yet.

**Next gates:** (1) locate matching 2a65edc Bluetooth rfkill code and build flags; (2) physically or from built DTB verify modern SDMMC2 tap/clock/regulator semantics; (3) privately compare *complete, matched* early OEM FW+cal vs current generic FW+sanitized NVRAM; (4) instrument only unknown transitions, then one reversible experiment at a time, with 2.4GHz regression, safe cleanup and later multi-device acceptance.
