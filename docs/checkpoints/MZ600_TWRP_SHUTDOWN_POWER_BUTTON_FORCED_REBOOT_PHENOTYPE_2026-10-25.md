# Xoom MZ600 shutdown/power-on anomaly: forced reboot restores boot, 2026-10-25

**Evidence type:** physical user observation, read-only TWRP/ADB diagnostics, and cross-check against Motorola's original user manual. **No eMMC, recovery, SD, kernel, or partition write made.** microSD remains removed.

## The physical observation (14:43 EDT)

Following unsuccessful v06.2 temporary Linux RAM boot, screen was dark and pressing ordinary Power briefly blinked a red indicator beside the rear camera. User deliberately recovered TWRP, selected **Shut Down** from TWRP, then attempted what appeared to be a fresh cold power-on. **Ordinary Power still only produced the red-light blink**. Holding **Volume Up + Power** caused the Motorola boot image to appear, and the user entered the normal TWRP recovery menu.

**Important correction:** This sequence is **not proof of a genuine PMIC/BCM4329 electrically cold start**. The original Motorola XOOM user manual explicitly states Power/Sleep + Volume Up held longer than 3 seconds is the tablet's **forced reboot** for unresponsive states. Source: https://manualzz.com/doc/6500062/motorola-xoom-tablet-user-manual (section *Troubleshooting > Force a reboot*). Historical reports of black display with normal Power ineffective and Power+Volume Up restoring normal reboot were published as early as May 2011: https://www.droid-life.com/2011/05/02/tip-xoom-wont-turn-on-stuck-with-a-black-screen-try-this-trick/ . This is a *preexisting device-class failure phenotype* and does not establish BCM4329 as its origin, nor establish our project as the first cause.

## Connected recovery verification — read only

Surface ADB verified the actual authorized replacement MZ600:
- `ro.hardware=stingray`, `ro.twrp.version=3.1.1-0`, and OEM `androidboot.modelno=MZ600` kernel boot argument. The TWRP-generated userland may generically report `wingray`, but hardware boot identity is independently known.
- Ran guarded Surface `C:\Users\olsen\xoom-linux-rom\captures\Xoom-MZ600-Capture-Pstore-ReadOnly-After-v062.ps1`: SUCCESSFUL script execution, **but recovery has no mounted/available `/sys/fs/pstore` and no `/proc/last_kmsg`**. It neither mounted nor cleared anything. **Absence of readable crash records does not prove no Linux panic.**
- Recovery battery sysfs: capacity **82–83%**, `voltage_now=7915360` (about 7.915V for this two-cell pack), `current_now=-493500` in the recovery driver's units, temperature `292` (29.2°C if tenths of C), `status=Not charging`, `health=Good`, and `AC_online=0`. These values argue against a battery simply at 0%, but do not rule out load-dependent voltage sag, gauge inaccuracy, or a hardware fault.
- Saved recovery `dmesg` privately on Surface at `captures\MZ600-TWRP-Kernel-After-PowerButton-PRIVATE-20261025.txt` (approximately 36,108 chars). It shows CPCAP PMIC microcode loading, `input: cpcap-key` detected, `cpcap_key ... device probed`, and `cpcap_rtc` registered, but the currently running recovery kernel's log **does not establish the previous failed Linux reset reason**. Do not upload raw logs or per-device private identifiers to public GitHub.
- No further Linux boot, Wi-Fi firmware activation, radio scan or BT test was conducted during this examination.

## Updated causality / competing hypotheses

1. **System fails to complete orderly power-off / remains hung**: ordinary Power fails, documented emergency reset works; the issue also followed explicit recovery Shut Down. Need distinguish OS shutdown request, Tegra PMC/CPCAP power-cut, and boot ROM reset logic, not presume shutdown physically succeeded.
2. **BCM4329 combo retained power/reset or shared rail vote**: viable mechanism after v06.1 loaded firmware and WCC modules were left loaded; mainline board lacks independently validated OEM U4 shared rail, WLAN WL_REG_ON and BT control handling. But the symptom existed in 2011 on stock-era Xoom, so don't declare the radio kernel implementation guilty. A real rail-off measurement or verified state-independent test is required.
3. **Power button/PMIC/low-voltage transient or vintage Xoom hardware**: recovery CPCAP key probe PASS and status GOOD indicate basic key driver and battery telemetry available but do not prove the initial boot key path or supply rails behave correctly. The failed Xoom has other known physical key/charging quirks; keep tests minimal, no disassembly needed at this stage.
4. **v06.2 built-in executable/boot-layout regression**: v06.1 and v06.2 differ only in init executable payload, which also changes compressed kernel; one v06.2 boot attempt with no COM9 cannot independently establish intrinsic bad image.
5. **External microSD not required**: absent for both v06.1 working and v06.2 unsuccessful attempts, therefore not a necessary factor for their contrast.

## Next A/B evidence plan

- Keep microSD removed, preserve current TWRP session until needed; no more blind `fastboot boot` attempts or eMMC flashes just to see whether red LED returns.
- Make a separate **normal Android/TWRP power-off → ordinary Power** baseline without any intervening Linux Wi-Fi use, recording whether actual shutdown and next boot behave normally. Avoid treating power+vol-up forced reset as a cold start.
- If stock environment also fails, classify problem as **device power-state/PMIC/reboot mechanism** rather than immediately a Broadcom driver regression. Compare power-off and reset source paths; check old Motorola CPCAP OEM driver, Tegra PMC LP0, reset reasons, battery voltage under load as accessible.
- If a truly controlled restart is possible and stock power cycling works, separately attempt known physically working exact v06.1 (without WIFI_START), then v06.2 in matched starting states, recording Motorola logo/kernel screen, USB PID1 PONG, time and any stored crash record. Do not interpret sequential runs as identical starting conditions.
- Only after firmware state dependence is demonstrated, develop an isolated kernel patch for BCM4329 shared rail/regulator and reset coordination. Keep potential upstream patches distinct from experimental USB userspace and WCC teardown.
- TWRP 3.1.1-0 does not expose pstore. Before next experiments, prioritize optional durable earliest boot evidence via kernel display/uart or explicitly planned RAM logging that can be recovered without exposing private user data.

**Release classification remains:** v06.1 has physical boot+Wi-Fi driver bring-up PASS; v06.2 has **one unsuccessful physical boot attempt, inherent validity undetermined**. No submitted upstream patches or invented DCO signoffs.

## Updated physical test: original Android shutdown reproduces red LED

**Subsequent direct user observation:** After recovering through TWRP, user selected **Reboot to System**, verified normal original Android availability by use, then selected **Shut Down from original Android 3.1**. Subsequent attempt to start normally with Power still produced the **same red camera-side LED symptom**, rather than normal startup. The user reports the red light persists in the sense that the **failure phenotype persists**; do **not** reinterpret this as the LED electrically staying continuously lit without clarification.

### Effect on hypothesis testing

- TWRP's shutdown routine is **not a necessary condition**: ordinary original Android power-off can reproduce the phenomenon too.
- Neither this Android test nor the earlier TWRP test proves PMIC rail drop, BCM4329 reset, or a truly unpowered state. Both Android and TWRP sessions followed earlier experimental Linux radio activity. A *retained board state* from a preceding Linux session is still a valid, **unproved**, shared cause.
- The current symptom may arise **before any new Linux kernel image is loaded**, at normal Power-on/reset/PMIC sequencing. That is a reason to halt repeated `fastboot boot` tests and investigate the stock-only power lifecycle; it is **not** proof that Linux images or the BCM4329 are free of faults.
- The recovery snapshot previously recorded battery 82% and approximately 7.915V, AC offline; software fuel-gauge capacity alone does not prove voltage at the instant of startup. A controlled physical test with an appropriate OEM dock charger (which was previously physically confirmed to charge this unit) is preferable to speculative reflashing or invasive battery disconnection.
- **Proposed discriminating control**: with removable SD still absent, use the OEM dock charger, verify actual charge indicator/AC-online in recovery or Android before shutdown, then compare normal Power-on after stock Android power-off versus the OEM documented Power+Volume-Up forced reboot. Record LED behavior and exact button timing. No further Linux image changes until observed baseline is recorded.
- Preserve any future OEM CPCAP/Tegra power management investigation as **separate evidence-gated source patch candidate**, not a change to the WLAN MAC RFC or experimental userspace WCC unload patch. Do not claim that root cause is a BCM4329 retained rail until a measurable board reset/power sequence or matched-state A/B supports it.


## Independent historical corroboration (Xoom-era hardware)

**Contemporaneous historical example:** On **March 12, 2011**, an original Motorola Xoom owner independently reported turning the Xoom off from a normally running system with about **70% battery** and then being unable to start it by the normal power button. The user recovered by holding **Power + Volume Up** as another person suggested, and confirmed the fix. Multiple contributors reported comparable no-start events without custom Linux. This is valuable evidence that **this failure phenotype existed on early Xoom systems**; it is not proof that our particular MZ600 has the same root cause or was unaffected by Linux. Source: https://forums.androidcentral.com/threads/help-shut-down-xoom-and-now-it-wont-boot.67229/ (posts #1, #4, #5, #6, March 2011).

**Original Motorola Xoom Verizon user guide:** Its illustrated first pages locate the charging and notification indicator lights separately on the **front** of the Xoom and identify the Power/Sleep key near the rear camera. They document holding Power/Sleep to turn on/off and Power+Volume Up for more than 3 seconds to force reboot an unresponsive tablet. **Do not classify a camera-side red blink as a documented 'battery below 15%' charging-light status; its location/meaning is not confirmed.** Source: https://storagemunicibidpro.blob.core.windows.net/pdfs/Pdfs/20200812/7e198587-ad08-436d-947d-b7c066806856.pdf (pages 2 and 4 of PDF, zero-index pages 1 and 3).

Battery 82% sysfs telemetry in TWRP is consistent with non-empty pack, but gauge data may be stale and doesn't measure voltage sag when CPU attempts to start. The stock Android shutdown replication, OEM forced reset, and historical contemporaneous report warrant a **power/boot ROM/PMIC/power-button control investigation before blaming brcmfmac or marking v06.2 defective**.


## Audit of third-party PMIC latch and fuel-gauge explanations (2026-10-25)

User supplied externally generated troubleshooting material asserting a **specific Xoom PMIC latching fault**, corrupted Maxim battery fuel-gauge calibration, clearing board capacitors with a 60-second Power+Volume-Up hold, and battery disconnection to reset nonvolatile calibration. **These are hypotheses or incorrect generalizations, not established findings for this hardware.**

**Verified build identity:** On connected Desktop WSL, v06.2 pinned source worktree `git diff --stat` shows the functional ARM bootloader vendor WLAN MAC ATAG→FDT bridge in `arch/arm/boot/compressed/atags_to_fdt.c` (42 added lines), build-target Makefile addition (one line), plus the untracked derived `tegra20-motorola-stingray-clean-usb.dts` board file. The lab USB `wifi_stop()` correction is confined to the embedded diagnostic `/init`, not to kernel CPCAP driver code. **No explicit PMIC-voltage, Tegra CPU regulator, battery-gauge register/EEPROM, or power-off handler patch was made for v06.2.**

**Verified exact v06.2 kernel configuration:**
- `# CONFIG_BATTERY_DS2781 is not set`. The stock TWRP recovery independently identified the existing `ds2781-battery.0` 1-Wire battery gauge and reported 82–83% charge/7.915V. Therefore the specific claim **our experimental Linux DS2781 driver wrote corrupt nonvolatile battery calibration** is inconsistent with this kernel configuration. The DS2781 is a **Maxim/Dallas 1-Wire battery gauge**; its upstream Linux source has parameter EEPROM support, but this does not mean our image wrote it. External source: https://github.com/torvalds/linux/blob/master/drivers/power/supply/ds2781_battery.c .
- `CONFIG_MFD_CPCAP=y`, `CONFIG_REGULATOR_CPCAP=y`, `CONFIG_REGULATOR=y`; the CPCAP framework/regulators **can execute in the kernel before userspace**. They were configured, but no physical rail/register readback proves an inappropriate vote or latched fault. No specific `CPCAP_REG_*` or silicon-defined PMIC fault latch has been identified in the provided symptoms.
- `CONFIG_BRCMFMAC=m`, `CONFIG_BRCMUTIL=m`, `CONFIG_BT_HCIUART=m`; modules are loaded explicitly by USB diagnostic command, not during Linux's default startup. Built-in Tegra MMC host may probe the SDIO function earlier. Thus an onboard BCM4329 power-state side effect is possible, but an automatically running Wi-Fi firmware driver **cannot** be assumed in the failed v06.2 attempt.

**Safety and factual corrections:**
- ARM CPU reboot, OS orderly poweroff, PMIC rail shutdown, peripheral reset, and actual external-battery power interruption are **different electrical state transitions**; do not label software shutdown a verified battery-disconnected cold start.
- A power-button forced reset **does not discharge capacitors while the battery remains connected**; a 60-second hold should not be presented as a Xoom-specific PMIC-clearing procedure. The documented Xoom recovery gesture is hold **Power + Volume Up for more than 3 seconds**, not a "drain" procedure.
- **Battery disconnect does not erase nonvolatile EEPROM calibration data**, which by definition retains programmed values without electrical power. Physically disconnecting aged Li-ion packs is invasive, may damage connectors or create a short, and is not justified by present evidence. No suggestion to physically manipulate or rewrite pack calibration absent independent failure evidence.
- The meaning of the **camera-side blinking red indicator** remains unconfirmed; do not assert a specific low-power protection/error code based on generic internet prose.
- OEM charger/dock trial may be a benign control if using known working equipment, but battery telemetry indicates the pack is not simply discharged. Historical stock-Xoom reports of black screen restored by Power+Volume-Up were documented in 2011 (https://www.droid-life.com/2011/05/02/tip-xoom-wont-turn-on-stuck-with-a-black-screen-try-this-quick-trick/). Those reports do not determine this unit's root cause.
- Driver and configuration audit **does not rule out accidental hardware side effects**: already-enabled CPCAP regulator drivers, Tegra clock/PMC setup and legacy board defaults can interact with shared BCM4329 power. Before a kernel patch, capture actual reset/power-off reason or isolate a reversible device-tree power owner with one variable at a time.

**Next experiment priority:** Preserve exact v06.1/v06.2 hashes and TWRP snapshot, avoid further blind Linux fastboot boots. Use known-working OEM dock for a non-invasive power baseline; compare stock Android shutdown → ordinary Power vs forced Power+Volume-Up; if normal Power remains unreliable, collect CPCAP/Tegra reset and power-key path evidence against Motorola OEM code before changing Wi-Fi firmware or testing battery disconnection.
