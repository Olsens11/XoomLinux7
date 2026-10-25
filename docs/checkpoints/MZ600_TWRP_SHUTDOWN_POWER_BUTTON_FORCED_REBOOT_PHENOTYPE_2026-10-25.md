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

