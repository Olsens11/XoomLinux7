# Motorola Stingray BCM4329 — OEM call-graph and lifecycle trace (v3)

**Date:** 2026-10-24. **Goal:** bring BCM4329 WLAN up on the replacement MZ600 under Linux 7, preserving portability and correct whole-combo-chip resource ownership. Bluetooth/FM are dependencies to account for, not feature-delivery blockers. **Research only**: no image built, no commands sent to tablet, no persistent flash. This report extends the [v2 lifecycle inventory](MOTOROLA_BCM4329_OEM_LIFECYCLE_RECONSTRUCTION_V2.md).

## Evidence discipline and version caveat

- **M — Motorola board source:** historical Motorola Stingray kernel merge/diff `eb4e253d7d76f6093ef50597e909157c21803842` (July 2011); this is genuine *source behavior* but is not proof that the particular production MZ600 booted this exact revision/defconfig.
- **B — Broadcom family source:** a 2010–2011 Android-era BCM4329 DHD driver from either `kernel/common@6444e59e` or `hardware/broadcom/wlan@froyo`. These offer concrete call graphs; **they have not yet been proven byte-identical to Motorola's shipped `bcm4329.ko`**. Never silently fuse these branches into one confirmed runtime.
- **A — Android device config:** AOSP `device/moto/wingray` `init.stingray.rc` (versioned AOSP device tree; do not infer every factory build ran the same services).
- **L — Linux 7:** `Olsens11/XoomLinux7` documentary/source and physical v025, v026, v028, v031, v033 checkpoints. Actual source path references must be confirmed against the private compiled tree before a code patch.
- **H — hardware observed:** per-Xoom physical diagnostic report. Controller software reads and U4 *votes* are not proof of power-rail voltages or internal POR.
- **I — hypothesis / gap:** requires further evidence.

### Primary primary-source links

- Motorola Stingray board integration: https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842%5E2..eb4e253d7d76f6093ef50597e909157c21803842/
- Early Motorola board evolution: https://android.googlesource.com/kernel/tegra/+/13b7fba9ceae2289d828208d6fbb19d7caddefdd%5E%5E%5E2..13b7fba9ceae2289d828208d6fbb19d7caddefdd%5E%5E/
- BCM4329 DHD kernel/common source: https://android.googlesource.com/kernel/common/+/6444e59eb90ee05bdc0d51e0dabd82515688cf58/drivers/net/wireless/bcm4329/dhd_linux.c
- BCM4329 DHD Froyo bus implementation: https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/dhd/sys/dhd_sdio.c
- *Older* Android 2.0.1 variant of DHD (different teardown order!): https://android.googlesource.com/platform/hardware/broadcom/wlan/+/android-2.0.1_r1/bcm4329/src/dhd/sys/dhd_linux.c
- Motorola Android service definitions: https://android.googlesource.com/device/moto/wingray/+/77e93514b350cdeb5624d5e4588ea0f449cc92af/init.stingray.rc
- XoomLinux7 v033 physical: https://github.com/Olsens11/XoomLinux7/blob/main/docs/checkpoints/V033_BLUETOOTH_PHYSICAL_2026-10-24.md
- XoomLinux7 v026 hardware/firmware trace: https://github.com/Olsens11/XoomLinux7/blob/main/docs/checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md

## A. Cold boot / registration (Motorola board M)

1. `tegra_stingray_init()` calls `stingray_sdhci_init()` and later `stingray_wlan_init()` (source diff near line 8931–8935); exact initcall-order and bootloader inherited pin states remain unmeasured.
2. `stingray_wlan_init()` calls `stingray_wlan_gpio()`, `stingray_init_wifi_mem()`, then `platform_device_register(&stingray_wifi_device)` (diff ~7787–7792).
3. `stingray_wlan_gpio()` requests U2 WLAN reset, drives it **LOW**, requests WLAN IRQ input (U5); the separate shared U4 power line is managed by board-level init/regulator logic.
4. `stingray_wifi_device` is named `bcm4329_wlan`, with platform callbacks `.set_power`, `.set_reset`, `.set_carddetect`, `.mem_prealloc`, `.get_mac_addr`, `.get_country_code`.
5. SDHCI declares an embedded card with a software presence status callback, a registration-notification callback, and a six-field embedded SDIO capability structure (not merely an SDIO version override).

**Definitive M behaviors:** board prepares a *reset-asserted* WLAN and exposes a platform control interface and logical card detect. **Open:** precise relative order of initial U4 voltage, 32.768-kHz clock readiness and U2 assertion, including bootloader-to-kernel handoff.

## B. WLAN power / card-presence caller chain (M + B, not yet shipping-build-qualified)

Contemporary Broadcom `dhd_linux.c` (`kernel/common@6444e59e` lines ~153–168, ~2638–2700) supplies:

```
DHD module insertion
   dhd_module_init()
      dhd_customer_gpio_wlan_ctrl(WLAN_POWER_ON)        [separate customer hook]
      wifi_add_dev()                                   [if CUSTOMER_HW2 & CONFIG_WIFI_CONTROL_FUNC]
         platform_driver_register("bcm4329_wlan")
            wifi_probe()
               wifi_set_power(1, 0)
                  wifi_control_data->set_power(1)        [if configured]
                     Motorola stingray_wifi_power(1)
                        mdelay(100)
                        change_power_brcm_4329(true)    [U4 shared vote]
                        mdelay(100)
                        gpio_set_value(U2, 1)           [release WLAN reset]
                        mdelay(200)
               wifi_set_carddetect(1)
                  Motorola stingray_wifi_set_carddetect(1)
                     stingray_wifi_cd=1
                     notify SDHCI status callback if registered
               up(&wifi_control_sem)
      wait for platform-probe handshake
      dhd_bus_register()                               [SDIO bus driver registration]
      wait for SDIO driver probe/attach handshake
```

The exact placement of `dhd_customer_gpio_wlan_ctrl(WLAN_POWER_ON)` is **important**. Its effect under the shipping combination of `CUSTOMER_HW2` and `CONFIG_WIFI_CONTROL_FUNC` **must be independently checked**; otherwise claiming that Motorola issued either one or two power votes would be speculative. Inspect `dhd_custom_gpio.c` and the *actual* MZ600 defconfig before implementing an equivalent.

**Unambiguous Broadcom source order at platform probe:** **power first, then logical card detect**, with board callback doing the ordered 100/100/200-ms sequence.

**Version discrepancy:** in older AOSP `hardware/broadcom/wlan@android-2.0.1_r1` `wifi_remove()` does `set_carddetect(0)` **before** `set_power(0)`; in `kernel/common@6444e59e` it performs `set_power(0)` **before** `set_carddetect(0)`. These are *different revisions*. Do not select a teardown order without pinning Motorola's actual driver.

## C. Chip firmware / WLAN CPU sequence (Broadcom DHD family B)

Source: Froyo `dhd_sdio.c` lines approximately 2162–2250, 2437–2504, 4840–4865, 5254–5326; wrapper `dhd_bus_start` in DHD Linux driver.

```
DHD driver attach / open
  dhd_bus_start(dhdp)
    if bus DOWN and firmware + nvram paths present:
       dhd_bus_download_firmware(...)
          dhdsdio_download_firmware(...)
             dhdsdio_clkctl(CLK_AVAIL)
             _dhdsdio_download_firmware(bus)
               dhdsdio_download_state(TRUE)
                 set ALP-only mode
                 select ARM7S or ARMCM3 core; disable ARM
                 select SOCRAM core; reset SOCRAM
                 clear final RAM word
               download firmware image to chip RAM
               process / download NVRAM vars
               dhdsdio_download_state(FALSE)
                 verify SOCRAM core up
                 write NVRAM and size/length token in RAM
                 select SDIOD/PCMCIA core; clear intstatus
                 select ARM core; si_core_reset(...)
                 drop ALP-only restriction
                 busstate = DHD_BUS_LOAD
             dhdsdio_clkctl(CLK_SDONLY)
    dhd_bus_init(dhdp)
       demand backplane CLK_AVAIL; verify state
       force HT clock in CHIPCLKCSR
       write SDPCM protocol version into host-to-dongle mailbox
       write CCCR IOEx to enable F1 + F2
       poll CCCR IORx for 3 s until F2 ready
       if success: setup SDIOD core, interrupt mask, watermark, bus DATA
```

**High-value equivalence:** old DHD has essentially the same F2-ready handshake that modern `brcmfmac` reaches and fails. Our v026 physical Linux 7: bin 253748 bytes CRC matching reference, NVRAM packed 672 bytes, firmware RAM transfer/readback works, `IOEx=0x06`, `IORx=0x02`, `-62`, no `wlan0`.

**Critical unproven step:** both vendor `si_core_reset` and modern `brcmf_chip_cm3_set_active()` release the core without an independent *execution acknowledgement*. Old source has no guarantee from just reaching `DHD_BUS_LOAD`; nor does modern source. The first discriminating trace should cover the ARM Cortex-M3 reset/readback, clock/PMU state transitions, mailbox writes/readbacks and *firmware-originated readiness*, not merely another file copy.

**Strong qualifier:** these detailed internals are positively evidenced in the public Broadcom Froyo driver, *not yet demonstrated to be identical instruction-for-instruction to the exact Motorola binary*. Proof requires shipped-source branch/config or private image binary and unobtrusive logging; do not call all steps M without that reconciliation.

## D. Shared U4 and Bluetooth path (Motorola M)

The OEM `change_power_brcm_4329(bool)` holds a spinlock and a shared, **untyped** integer count. Every true request asserts Tegra U4 then increments the count (capped at 2); every false request decrements if positive, and drives U4 low only if count reaches zero. The board calls it from two function families found in the cited merge:

- `stingray_wifi_power(on)` — U4 shared vote + U2 reset and 100/100/200 ms pacing.
- `bcm4329_bt_rfkill_set_power(blocked)` — when **unblocked**, acquire U4 vote, drive U0 BT reset high, keep I7 shutdown low; when **blocked**, release U4 vote, keep I7 low, drive U0 reset low.

`bcm4329_bluetooth_probe` explicitly enables/requests U0 and I7, then **calls `bcm4329_bt_rfkill_set_power(NULL,true)` to establish initial BT blocked state** before registering rfkill. BT low-power setup requests U1 BT_WAKE as output and U6 HOST_WAKE as input with a wake IRQ and timer/Android wake lock. `bcm_bt_lpm_exit_lpm_locked()` asserts BT_WAKE and schedules delayed release; host wake IRQ bookkeeping affects suspend/wake, not necessarily U4. In Android userspace the disabled `hciattach` service invokes `brcm_patchram_plus` with `bcm4329.hcd` on `/dev/ttyHS2` at 3M baud, `--enable_hci`, `--enable_lpm` and PCM configuration. Its precise start trigger and production image patch contents are not established here.

**Subtle correctness risk in historical M code (not a claimed observed bug):** because count is untyped, an initial Bluetooth `blocked=true` callback can decrement a count previously acquired by WLAN if the call order permits WLAN to have voted first. The code has no per-consumer ownership ledger. That makes **typed WLAN and BT reference counts** a correctness improvement worth preserving in Linux 7 even as we emulate OEM timing. The startup ordering on shipping builds must be pinned before claiming this happened.

**v033 physical L:** Motorola-gated Linux `hci_bcm` successfully exercised U4 vote ON/OFF and identified BCM4329B1 on UART. `BT_START` module binding was *not* electrically passive; HCI ioctl `BT_OFF` had pointer-vs-integer ABI bug and returned -19, but module removal correctly released U4. After BT unload, WLAN F2 still -62. This does **not** mean a true chip power-off occurred, because WLAN/MMC may retain its own U4 vote.

## E. Stop, unload, suspend/resume, failure exits — do not treat as one generic "off"

| Event | Public source evidence | What is / isn't proven |
|---|---|---|
| DHD module insert | `dhd_module_init` calls customer GPIO ON, registers platform driver and SDIO bus driver | Generic DHD B; compile-option effects for Motorola unresolved |
| DHD platform probe | `wifi_set_power(1)` **then** `wifi_set_carddetect(1)` | Direct B source order, calls M board functions if wiring enabled |
| DHD SDIO bus initialization | force clocks, SDPCM mailbox, F2 IOEx and IORx wait | Direct B; Linux 7 physical F2 fails at same readiness boundary |
| DHD platform remove | Order differs across revisions: older card-detect-before-power-off vs later power-off-before-card-detect | **Do not invent unique OEM teardown order** |
| DHD module cleanup | `dhd_bus_unregister`, `wifi_del_dev`, customer GPIO OFF | Configuration may affect whether repeated power-off dispatches are physical callbacks |
| DHD failed module initialization | release bus/platform registrations, call customer GPIO OFF | Need shipping compiled branch to guarantee path |
| BCM4329 BT rfkill blocked | U4 vote release, I7 LOW, U0 LOW | Direct M source; may not imply internal supplies physically off |
| BCM4329 BT rfkill unblocked | U4 vote, U0 HIGH, I7 LOW | Direct M source |
| BT platform probe | request I7/U0; initially apply blocked; register rfkill and host wake/BT wake | Source behavior, not an analog pad waveform |
| BT platform remove | unregister rfkill, free pins/wakelock | No independent measured U4 final count/level for original MZ600 |
| DHD platform `wifi_suspend/wifi_resume` | family source may disable/enable OOB interrupt; other PM paths exist | Not proof WLAN supply powers down during suspend; investigate MMC, cfg80211, early-suspend, firmware power-save |
| Full system suspend/reboot | Tegra suspend platform, board GPIO retention, Android stop ordering still to trace | **OPEN** until version-pinned complete source and/or OEM runtime log |

### A separate revision hazard

Different revisions of the public Broadcom driver reverse card-detect and power-off on remove. This tells us that preserving a specific original kernel revision and build-time conditions is essential; building a synthetic "Motorola OEM" behavior by mixing snippets can be *less* accurate than our current model.

## F. Per-device identity and configuration path

Motorola kernel board code parses bootloader `ATAG_STINGRAY_MAC`; `board-stingray-wlan_nvs.c` supports Wi-Fi calibration extraction/`/proc/calibration`; board source also has a separate `ATAG_BDADDR` Bluetooth address parser in the shared board file. These are distinct identities. Never commit or copy a real per-device MAC/BD_ADDR or private calibration to the public repo.

The Android init file contains explicit disabled production/manufacturing **test control** services that insmod `bcm4329.ko` with firmware file paths and a `.cal` path; this does not fully prove the normal consumer Wi-Fi startup policy. Android's Bluetooth patchram service exists but is disabled in init and must be started elsewhere.

Linux 7 v026 shows board-specific filename attempts followed by generic `.bin` and `.txt`, platform MAC unavailable, and generic NVRAM 672 bytes. That is a fidelity gap for future RF operation; it is **not** proven to explain F2 readiness before `wlan0` exists.

## G. OEM versus Linux 7: gap matrix ordered by potential to affect F2

| Item | Motorola/Broadcom reference | Linux 7 measured or configured | Evidence gap / likely next diagnostic |
|---|---|---|---|
| Shared power | Motorola U4 untyped WLAN+BT vote, explicit delay before U2 release | U4 regulator boot-on, MMC-owned U2, v033 separate BT U4 vote | Trace real U4 *electrical* and software transitions from early boot to firmware start; not just steady 1 |
| Power/card detect | platform DHD power first, then card-detect callback | DT embedded SDIO MMC enumeration independent of WLAN module loading | Trace host first CMD5 versus U4/U2/32k chronology; ensure 110ms from stable internal supply |
| SDIO capabilities | six-field Motorola embedded SDIO override | v018 full equivalent tested, F2 failed | Do not retest capability override as if not tried |
| Host clock | OEM downstream Tegra host and SDIO timing | v022 25MHz legacy tested; F2 failed | Match readback actual pad timing only after prior steps |
| NVRAM/firmware | OEM `.cal`/board identity/platform power callbacks, vendor DHD | generic file/NVRAM CRC known; Cortex-M3 release, no execution handshake | Compare firmware match/provenance and chip core/PMU control, same-device unique data private |
| Internal start | DHD disables ARM/SOCRAM and later releases ARM; forces HT for F2 | modern brcmfmac analogous path; F2 -62 | Timestamp core reset, SOCRAM, PMU resources, mailbox version and all error paths |
| BT coexistence | RFKill U4 votes, I7 passive LOW, U0 independent reset, UART low-power | v033 identifies BT; does not prove shared POR | Use typed owner; test BT off state without accidentally powering chip |
| FM | BCM4329 silicon contains FM hardware, no traced Stingray FM userspace/driver activation | none | Search OEM configs for FM interface; retain unknown/passive, don't invent node |

## H. Explicit next-source-trace checklist (unresolved)

1. **Pin the shipped OEM driver**: locate Motorola production kernel `bcm4329.ko` provenance, exact commit/tag, defconfig `CONFIG_WIFI_CONTROL_FUNC`, `CUSTOMER_HW2`, chip rev/MZ600 board revision conditions, and `dhd_custom_gpio.c` effect of `WLAN_POWER_ON`/`WLAN_RESET_ON` to avoid double power votes in reconstructed graph.
2. **Bridge proprietary driver to board callbacks** in exactly the same branch, recording all callers of `wifi_set_power`, `wifi_set_carddetect`, `dhd_customer_gpio_wlan_ctrl`, `dhd_bus_start`, `dhd_bus_devreset`, and special recovery code; classify init, unload, rfkill, suspend, resume, fatal error.
3. **Establish electrical original-off**: identify early U4 GPIO setup in `board-stingray.c` and regulator/bootloader defaults; whether bluetooth initial block count release can occur after WLAN acquired vote; actual 32k output waveform and VDDC settled point.
4. **Inspect exact chip register programming differences** between vendor DHD and modern brcmfmac around `si_attach` PMU/PLL programming, SOCRAM and ARM release, SDPCM mailbox write and firmware-originated readiness. Focus on instructions executed *prior* to F2-ready poll; source-list each distinct write plus guard.
5. **Complete OEM suspend/resume/recovery**: trace `dhd_set_suspend`, MMC host keep-power, wake IRQ and packet filter logic, BT wake timers and `rfkill`, Android service triggers. Trace all path combinations, not just steady on/off.
6. **Inventory FM without assumptions**: find actual Motorola FM firmware/driver/Android feature manifest or record absence of evidence; only after that define a passive function policy.
7. **Source line/date pinning**: keep separate 2010 Froyo, Android 2.0.1, Motorola 2011, and later bcmdhd implementations; prioritize exact vendor revisions over adjacent AOSP examples.

## I. Safest *next* instrumentation design (not implemented)

First improve source completeness; then trace events in **one monotonic timebase** on a verified RAM-only Linux image: regulator voting U4, GPIO U2/U0/I7 configuration/output changes, CLK_BLINK LPO framework event, SDMMC2 initial power/clock and first CMD5, F1 backplane/core-reset reads, firmware request/load/NVRAM CRC, `si_core_reset` equivalent, PMU resource pending/status and SDPCM mailbox, finally IOEx and IORx. Read-only sampling of documented registers where possible; do **not** write PMU bits, force GPIO ownership, or claim POR based on software logs alone. Continue v025 rollback and original device protection. Once a discrepancy is proven, test one controlled variant at a time.

## J. Current stopping point

**What is newly closed:** platform-probe power-before-card-detect path (B), detailed vendor ARM/SOCRAM download/release path (B), exact vendor F2 handshake boundary (B), Motorola BT rfkill probe/initial-block and U4 vote behavior (M), and source-version teardown-order differences (B).

**Not yet closed:** exact shipping Motorola DHD binary/defconfig, all shared U4 callers across every version, full whole-chip POR, original firmware Cortex-M3 successful execution, and complete suspend/resume/shutdown on the physical board. No firmware executed, boot image built, GPIO touched or network claim made in this research pass.

## K. Latest repository reconciliation: v034 (independent of this research)

During the source audit GitHub advanced to commit `f16fe64872bcd81b75646e9afe18bcd354f9e56d`, **v034 physically verified**. Its USB `HCIDEVDOWN` now passes device index by value (returns rc 0), the host message correctly warns that `BT_START` automatically initializes/powers Bluetooth, and `BT_STOP` verified all six module unloads and U4 release. The corrected v034 image was temporary booted, not flashed. **No new WLAN F2 experiment was performed in v034.** This means the earlier v033 ioctl bug is no longer an outstanding corrective task; the OEM whole-chip research remains open. Source: https://github.com/Olsens11/XoomLinux7/blob/main/docs/checkpoints/V034_HCI_IOCTL_PHYSICAL_2026-10-24.md .

## L. Newly resolved OEM build-configuration clue — primary driver identity (critical correction)

**Source verified, not yet a shipped-image binary verification.** Motorola's `arch/arm/configs/stingray_defconfig` in the **same kernel/tegra revision** used for our Motorola board analysis (`eb4e253d7d76f6093ef50597e909157c21803842`) explicitly specifies:

```config
CONFIG_WIFI_CONTROL_FUNC=y
CONFIG_BCMDHD=y
CONFIG_BCMDHD_FW_PATH="/system/vendor/firmware/fw_bcmdhd.bin"
CONFIG_BCMDHD_NVRAM_PATH="/system/etc/wifi/bcm4329.cal"
CONFIG_MMC_EMBEDDED_SDIO=y
CONFIG_BT_HCIUART=y
```

Authoritative file: https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842/arch/arm/configs/stingray_defconfig .

**Consequence:** For this Motorola source/config pairing, the **BCMDHD** path is the primary driver candidate, and it is configured built-in (`=y`), not necessarily a runtime-inserted `bcm4329.ko`. The earlier 2010 `drivers/net/wireless/bcm4329/dhd_linux.c` and AOSP Froyo `dhd_sdio.c` traces in sections B–D are *historical Broadcom-family reference traces*, **not yet proven to be the exact driver code or call order in this defconfig's actual boot**. Their platform-probe ordering and F2 poll semantics cannot be promoted to the definitive Stingray OEM runtime graph until checked against the contemporaneous **Motorola `bcmdhd` build and its Makefile macros and initcall handling**.

This finding also changes how to interpret the older Android `init.stingray.rc` disabled `insmod bcm4329.ko` services: those entries could be manufacturing paths or a different vendor software revision and cannot override the kernel defconfig. The configured `.cal` firmware/NVRAM paths are concrete and should be compared against same-revision `bcmdhd` file-open and country/MAC callbacks. `CONFIG_WIFI_CONTROL_FUNC=y` and `CONFIG_MMC_EMBEDDED_SDIO=y` support the presence of board platform and embedded-card interfaces, but don't by themselves establish who triggers platform-power first at runtime.

**New priority gate:** obtain the actual `drivers/net/wireless/bcmdhd/` source (or the vendor-referenced external source submodule) and `Makefile` at that **same exact revision**, then enumerate, line by line: module/built-in init order, `CUSTOMER_HW2`, `BCMPLATFORM_BUS`, `dhd_customer_gpio_wlan_ctrl` handling, platform callbacks, first power vote relative to `stingray_wlan_init` and MMC/carddetect, `dhd_sdio` reset/firmware/PMU/F2 path, and teardown/suspend/resume. If the exact driver source isn't present in the checked public tree, mark that as a provenance gap and locate Motorola's matching published source package. Keep device logs and hashes separate from vendor source assumptions.

**What this corrects:** section J's statement that the *actual* OEM platform-probe power-before-carddetect call graph is “closed” is too broad. That ordering is **verified in one historical DHD family source**, but remains **open as an exact Motorola/BCMDHD lifetime trace** for the MZ600. All direct Motorola board-source findings (shared U4 implementation, U2 callbacks, BT rfkill) remain source verified.