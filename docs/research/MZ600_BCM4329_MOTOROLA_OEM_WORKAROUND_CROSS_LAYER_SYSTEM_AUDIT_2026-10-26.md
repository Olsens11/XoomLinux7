# MZ600 BCM4329 — Motorola OEM six-field SDIO workaround and complete cross-layer integration

**2026-10-26 — specific owner correction:** Motorola had a *known chip-specific workaround* for incorrect BCM4329 SDIO capability reporting. We must examine **everything Motorola coordinated around it**—not presume that importing one MMC field, one firmware file, or one power-reset routine reproduces the working OEM system. This audit reopens the original project evidence and links it to current Linux 7 5 GHz debugging. It is source/previous-test analysis, not a new hardware experiment.

## Original OEM identity — distinguish revisions

- Actual early MZ600 HRI39/HRI66 boots used Linux **2.6.36.3-g2a65edc** with identical private 264,038-byte Motorola Broadcom DHD *bcm4329.ko*, SHA256 **4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f**, original *fw_bcm4329.bin* **261,317 bytes** SHA256 **7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a** and OEM *bcm4329.cal*. Match against public Motorola Tegra source **2a65edc**, not an arbitrary Froyo or 2.6.39 source. Original private .cal and firmware stay private.
- Separate later OEM Wingray **2.6.39.4-g4e32b94**, BCMDHD and 264,140-byte firmware reflect **different-generation** behavior. Generic adjacent Broadcom driver code is useful, not proof of exact original production compile flags.
- Current Linux 7 runs **7.0.0-next-20260422+**, generic 253,748-byte BCM4329 **4.220.48** firmware and version-matched upstream *brcmfmac*, *brcmutil*, *brcmfmac-wcc*. The working current MMC core source SHA256 **cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6** has no historical v018 quirk marker.
- Source audit of matching-generation OEM startup and ELF previously passed 27 offline checks, but shipping preprocessor flags and true electrical timing are not fully verified. Keep separate source, ELF, modern source and physical evidence.

## Motorola's SPECIFIC workaround: all six SDIO capabilities

Motorola's original board file *arch/arm/mach-tegra/board-stingray-wifi.c* supplied these hardcoded embedded-SDIO card capabilities to compensate for BCM4329's **incorrect reported SDIO revision 1**:

| capability | Motorola |
| --- | ---: |
| sdio_vsn | 2 |
| multi_block | 1 |
| low_speed | 0 |
| wide_bus | 0 |
| high_power | 1 |
| high_speed | 1 |

The OEM board also treated WLAN SDIO as **built-in**, provided the host OCR voltage range **1.65–1.95 V**, and used explicit software card-present callbacks. Where the override is applied matters: Linux 7 normal SDIO CCCR parsing can override premature changes. Previous partial experiments v010, v011 and v013 did not reproduce the complete six-field behavior.

**The prior v018 experiment DID physically apply all six fields** in a controlled board+BCM4329-scoped patch *after MMC CCCR/CIS/fixups and before high-speed host negotiation*. Raw CCCR was 0x11; parsed SDIO version 1→2, high_speed 0→1, raw SPEED 0x01→0x03, host legacy timing→SD high-speed. Yet enabling F2 still produced -62 on **both** v018 trials. The workaround affected real host state but **was not sufficient to bring the chip up under those other test inputs**.

Present-day Debian 2.4 GHz interface and 19-BSS scan work WITHOUT v018 source inserted. Therefore **do not claim six-field quirk is proven necessary for current 5 GHz failure**; equally, its interaction with OEM initialization, high-speed stability and eventual multi-device qualification must not be forgotten. Never add the override globally to all cards without a justified compatible-ID/machine match.

## OEM functional dependencies and Linux 7 discrepancies

| Layer | Original Motorola system | Linux 7 / interaction to audit |
| --- | --- | --- |
| Board initialization | Prepare U2 WLAN reset initially LOW; SDHCI embedded card and U5 IRQ setup; shared U4 supply and BT I7/U0 in other board code | Current DTS fixed U4 regulator, MMC U2 pwrseq and UART Bluetooth each claim resources. Cold-boot inherited states matter |
| Shared WLAN+BT power | Spinlocked **change_power_brcm_4329** U4 shared vote count; WLAN power callback delays **100ms, U4 vote, 100ms, U2 release, 200ms** | Current regulator-boot-on and MMC-pwrseq can produce different U4/LPO/U2 chronology. Shared BT vote and I7 may block true internal regulator off; no double GPIO ownership |
| Card detect and capabilities | Driver **wifi_set_power(1)** BEFORE **wifi_set_carddetect(1)**; callback registers physical-presence notification; six-field MMC override and host clocks | Current automatic SDIO enumeration, no v018 override. Measure first CMD5, actual host timing and voltage; do not change clocks and reset together |
| Cortex-M3 firmware start | OEM DHD ARM held in reset, RAM/SOCRAM reset, code then NVRAM written, interrupt status cleared, ARM released; firmware responds over SDPCM | Modern brcmfmac analogs exist. Firmware code copied into RAM does not prove successful on-chip initialization |
| Identity | OEM *bcm4329.cal* contains valid generic **bootstrap MAC** in NVRAM; separately obtain unique actual board MAC from **ATAG_STINGRAY_MAC**/platform callback | v043 firmware console reported *Failed to init wireless side, err:21*. v044 one-field test using authentic bootstrap identity (private, not a substitute for unique per-device identity) made F2 ready |
| WCC/host driver | OEM DHD control+vendor integration and SDPCM mailbox/CCCR F2 readiness handshake | After v044 F2 PASS, missing WCC plugin blocked WLAN; v045 WCC packaging workaround yielded first **wlan0**. Installed Debian now uses clean separate standard modules |
| PMU and chipcommon | OEM *siutils.c* says firmware handles PMU init; it **skips host PMU init**, and clears ChipCommon GPIO pull-up/down registers with a chip-revision condition | Modern probe also requests PMU control **RES_RELOAD**; broad GPIO pull clear not found in current flow. Potential cross-function interactions; read before writing, do not blindly transplant |
| ALP/HT reference/host | OEM force ALP/prep, clear SDIO pullups, force HT, SDPCM mailbox, then enable F2 and poll IORx | Modern Linux largely source-equivalent in these steps; don't invent a missing call where present. Difference may be prior power history, firmware/NVRAM or PMU effects |
| Board RF and country | OEM same-generation calibration preserves boardflags, **aa2g=1, aa5g=1**, PA values, original US **ccode=US, regrev=69** (verified in both old archives) | Current sanitized NVRAM has 5GHz antenna/PA fields but omits original ccode/regrev. Linux generic FW **GET_BANDLIST one 2G band**, chanspecs **11 2G / zero 5G**. Compare entire firmware + calibration + regulatory policy, not force iw 5GHz |
| Bluetooth/FM | OEM BT rfkill shared U4 votes, I7 LOW, U0 reset independent, U1/U6 wake, separate BT patchram/HCD; FM usage not proven | Linux hci_bcm ownership/shared LPO and full-chip provider are distinct. Check coexistence, suspend/restart and failure paths before own-use release |
| Unload/suspend/failure | OEM branch-specific power vs carddetect teardown; different DHD revisions reverse removal order | Current WCC→brcmfmac→brcmutil unload works, but not proof of full POR; reconcile warm start, suspend/resume and error handling across board and driver |

## Crucial actual experiments — no isolated-fix narrative

1. **v018 physical:** full Motorola six-field SDIO workaround worked at host/card capability layer, but F2 **-62** twice with that firmware+NVRAM set.
2. **v042–v043 physical:** read correct SDPCM shared structure and actual Broadcom Cortex-M3 console; firmware visibly ran yet reported startup failure *err:21*.
3. **v044 physical:** **one-field authentic OEM bootstrap identity** in NVRAM, other variables fixed, yielded **F2 err=0**. Still no wlan0 because **WCC plugin was missing**.
4. **v045 physical:** WCC packaging experiment reached **wlan0**; rolled back temporary changes. Later v06.x fully installed clean separate WCC modules and successfully scanned **19 BSS at 2.4GHz**.
5. **Latest Oct 26 5GHz physical:** independently loaded exact-ABI RAM-only brcmfmac diagnostic: **firmware GET_BANDLIST count=1, first band enum=2 (2GHz)**; **chanspecs total=11, 2GHz=11, 5GHz=0**. No firmware 5GHz band to expose in wiphy. Owner confirms actual same-unit Android connection on 5GHz. **Do not assume OEM SDIO workaround alone will correct this firmware-level absence**.

These results show OEM functionality can depend on **combined SDIO capabilities, board power/card detection, firmware bootstrap configuration, vendor module loading and regulatory/board calibration**. They do not yet isolate the present 5GHz causal setting.

## Cross-layer audit and patch development acceptance order

1. **Exact shipping source/binary/compile flags:** identify HRI39/HRI66 driver build flags **CUSTOMER_HW2**, **CONFIG_WIFI_CONTROL_FUNC**, custom GPIO hooks, firmware path, original six-field usage, original board-vote sequence and all unload/suspend conditionals; don't mistake a related Froyo branch for the production module.
2. **Trace the entire activation/teardown chain:** board boot and radio pin ownership; U4/BT votes; LPO/XTAL and timing; MMC card-present; six-field CCCR; firmware and same-device NVRAM; bootloader identity; firmware country/regrev; ALP/HT/PMU/ChipCommon; ARM firmware console; F2; bandlist/chanspecs; Bluetooth coexistence; error recovery. Mark each link SOURCE ONLY, VERIFIED PHYSICAL, or OPEN.
3. **Private comparisons:** original OEM HRI39/HRI66 firmware **4.218.248.20** vs generic **4.220.48** and separately later OEM 264140-byte image; compare actual field presence/values and initialization dependencies without publishing raw calibration, MAC, credentials or firmware blobs.
4. **Current compiled modern mapping:** inspect actual kernel source/config/DTB and physical behavior for each OEM contract, noting **which OEM differences have already been tested**. Preserve known-good 2.4 GHz scan, separate normal WCC packaging and matching ABI.
5. **Reversible isolated trials:** one variable at a time *where causally separable*, but preserve a verified **firmware-plus-calibration matching pair** if they are inseparable. Prefer SHA-pinned RAM diagnostics. Never synthesize extra 5GHz channels, force regulatory country/power, bypass chip firmware limits or write p7 for these tests.
6. **Own-use patch architecture:** optional narrowly scoped generic SDIO quirk if proven, separate Motorola DTS/pwrseq/shared-chip resource ownership, dynamic factory MAC, justified per-model firmware/calibration/regulatory handling and userspace services. Run cold/warm, SDIO and HCI, scan and clean unload **across real MZ600/MZ602/MZ604 units**. Submission only after owner approval.

## Primary records to read before next work

- [Motorola specific six-field workaround and partial-test pitfalls](MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md)
- [Full v018 OEM quirk experiment and actual F2 result](../checkpoints/V018_OEM_SIX_CAPABILITIES_PHYSICAL_2026-10-24.md)
- [Exact early MZ600 driver and firmware provenance](MZ600_HRI39_HRI66_OEM_DRIVER_RECOVERY_2026-10-24.md)
- [Matching-generation OEM cross-layer F2 and PMU source comparison](MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md)
- [Motorola all-subsystem call graph, lifecycle and BT dependencies](MOTOROLA_BCM4329_OEM_CALLGRAPH_TRACE_V3.md)
- [Firmware console, MAC-startup and WCC root-cause physical tests](../checkpoints/V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md)
- [Actual firmware 5GHz bandlist/chanspec physical diagnostic](../checkpoints/MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md)
- [Whole-chip resource ownership](BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md), [149-page datasheet index](BCM4329_DATASHEET_PAGE_INDEX.md) and [36 contracts](BCM4329_DATASHEET_REQUIREMENT_AUDIT.md)
- [Whole-chip patch series integration ledger](MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md) and [multiple-device tests](../plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md)

**Outcome:** Motorola-specific workaround confirmed from project records; complete interconnected system explicitly mapped; current functional Linux MMC still lacks v018 patch; six-field quirk not yet qualified as necessary for 5GHz. No device touched or firmware substituted in this review.
