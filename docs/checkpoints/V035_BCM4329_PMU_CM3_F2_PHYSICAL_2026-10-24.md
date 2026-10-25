# v035 physical test — BCM4329 PMU/Cortex-M3/F2 startup timeline (October 24, 2026)

**Result:** **PASS** for a bounded read-only register-observation instrument and USB/RAM module transfer on the replacement Motorola Xoom MZ600, across three attempts. **FAIL** for Wi-Fi: SDIO F2 never ready (IORx=0x02, error -62) on all three. **Most useful finding:** first observer run saw `PMUControl` change after CM3 release and before F2 request; warm module-only reloads retained the resulting value. This does **not** prove that onboard firmware instructions ran or that the physical chip power rails were cycled.

## Procedure, provenance and safety

- Base device Linux **v034**, already booted with temporary `fastboot boot` at an earlier documented session. **This test did not reboot or flash anything**; the kernel, DTB, existing generic firmware, and existing generic NVRAM stayed frozen.
- On desktop Ubuntu-22.04 WSL, built `brcmfmac-v035-pmu-cm3-readonly.ko` using [v035 builder](../../scripts/experiments/v035-build-readonly-pmu-cm3.py), against pinned [Linux7 kernel `2404d273...`](https://github.com/xoom-linux/linux/tree/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3).
- Checked original source SHA256 `sdio.c = 74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab`, `chip.c = 932e25c75f9ea5247194dfdb78c6b41a457af68d7a558935a7b5489bf548aa9d`. Builder modified only these two local sources temporarily for compilation; restored **byte-exact** sources in `finally`, independently rechecked.
- Built ARMv7 ELF `brcmfmac-v035-pmu-cm3-readonly.ko`, **461440 bytes**, SHA256 **`da7a6dc972e3700440c5296814102537402caf62e317a1e3e8d798f6927d4ff4`**, vermagic `7.0.0-next-20260422 SMP mod_unload modversions ARMv7 p2v8`.
- Transferred to Surface Book 2 through authorized desktop tools as compressed/base64 staging; rebuilt exact module SHA256 and size on Surface, then used already qualified v034 USB client to upload **only** the module to `/run/brcmfmac.ko` (RAM filesystem).
- Xoom USB acknowledged **`UPLOAD DONE SIZE 461440 CRC32 0xE8435C0C`**, matching Surface host. `WIFI_START` loaded `brcmutil` and v035 `brcmfmac` successfully (`rc=0`). No firmware or NVRAM upload, no F2 readiness emulation or RF scan/association.
- Additional instrumentation performs `ktime_get_ns()` event logging and non-destructive reads of existing `pmucontrol`, Function 1 `CHIPCLKCSR`, SDIO Function 0 `IOEx`/`IORx`, plus CM3 activation event brackets. It **adds no PMU/GPIO/regulator/core reset writes**; the existing driver continues its normal startup writes. These added reads do affect runtime timing slightly; they are not transparent electrical probes.
- For complete read-only kernel log capture, made a Surface-local copy of v034 host client and changed the LOGS read termination from opening header to `=== END LOGS ===`. Private sanitized files `v035-trial1-sanitized.log`, `v035-trial2-sanitized.log`, `v035-trial3-sanitized.log` kept on Surface. They contain only marked diagnostic events and F2 failures; no raw calibration or MAC identifiers committed.

## Three real hardware trials

Notation: `PMU` = read `pmucontrol` register; `CLK` = F1 CHIPCLKCSR; `IO` = F0 IOEx/IORx. Each of the four register read error values at each sampling event was **0**. The first run was **not** a new power-on reset; it was the first v035 module load into a device already running v034.

| Trial | T0 PMU / CLK before existing reload write | T1 PMU / CLK after | T2/T3 PMU / CLK at CPU release | T4/T5 PMU / CLK at F2 | T3→T4 elapsed | F2 result |
| --- | --- | --- | --- | --- | ---: | --- |
| **1, first load** | `01770180 / 61` | `01770180 / 61` | `01770180 / 48` | `012B03BC / D2` | **31.920 ms** | `-62` |
| **2, warm reload** | `012B03BC / E1` | `012B03BC / E1` | `012B03BC / C8` | `012B03BC / D2` | **0.782 ms** | `-62` |
| **3, warm reload** | `012B03BC / E1` | `012B03BC / E1` | `012B03BC / C8` | `012B03BC / D2` | **0.837 ms** | `-62` |

All three at T0..T4: `IOEx=02`, `IORx=02`. At T5: `IOEx=06`, **`IORx=02`**. Host driver `sdio_enable_func(F2)` timed out after ≈3.00s with `-62`. `wlan0` remains absent (inherited state; no working Wi-Fi demonstrated).

### Exact critical event order — first run

- T0 (kernel t≈5537.180331s): `PMUControl=0x01770180`; ChipClkCSR `0x61`.
- T1 (≈5537.180529s): immediately after the existing Linux 7 PMU reload write, **PMUControl still `0x01770180`**. The added observer does not modify that write.
- T2 before CM3 release (≈5537.280360s): PMUControl unchanged, clock `0x48`.
- `CM3_ACTIVATE_BEGIN` (≈5537.280491s), `CM3_ACTIVATE_DONE` (≈5537.281329s), T3 (≈5537.281549s): PMUControl still `0x01770180`.
- T4 before F2 request (≈5537.313470s): PMUControl has changed to **`0x012B03BC`**, clock `0xD2`. ~31.920ms elapsed from T3. The observer did **not** capture the exact intervening writer/instruction.
- T5 after 3-second F2 wait (≈5540.315667s): PMUControl `0x012B03BC`, `IOEx=06`, `IORx=02`; `enable F2: err=-62`.

### Warm reload differences — replicated twice

After `WIFI_STOP`, the already-staged v035 module was started again *without MMC2 detach/rebind or reboot*. Both trial 2 and trial 3 started with **`PMUControl=0x012B03BC`**, the ending value of trial 1, and **no further PMUControl transition was observed** at any recorded stage. Their early clocks were `0xE1` then `0xC8`, rather than the first trial's `0x61` then `0x48`. The CM3-release-to-F2 interval fell from ~31.9ms to ~0.8ms. All still ended with F2 `-62`.

These observations are evidence of **state retention across driver unload/reload** and show that two driver loads were **not equivalent initial chip conditions**. They do not establish that U4 never fell physically, that analog PMU rails retained voltage, or that a fully cold hardware reset would reproduce either path. Linux 7's existing regulator `boot-on`/MMC ownership makes this an important separate question.

## Interpretation and surviving hypotheses

**Source-evidence crosscheck:** [v4 OEM comparison](../research/MZ600_BCM4329_OEM_VS_LINUX7_F2_STARTUP_AUDIT_V4.md) established that Motorola's original `si_doattach` deliberately defers internal PMU programming to firmware, while modern `brcmfmac` sets PMU resource-reload control. The initial v035 T0→T1 register readback did **not** change; the meaningful register transition occurred later, after CM3 release. That is **consistent** with firmware-driven or autonomous on-chip resource initialization, but **cannot prove the Cortex-M3 executed firmware instructions** or identify the exact writer: host/kernel writes through other paths, autonomous hardware effects, or register-window/mapping issues must be ruled out. A normal registered-write audit is the next step.

The observations also **do not prove PMU state retention is causing F2 failure**, because F2 fails with both the initial and retained PMU values. The distinct first-run ~32ms interval may be firmware/internal initialization, an asynchronous bus/clock wait, or logging/host effects. It is a newly exposed timing boundary to investigate.

## Next discriminating actions

1. **Source trace of every host-side write capable of modifying PMUControl** from T3 to T4, including indirect backplane accesses, dynamic windows and other kernel actors; instrument write provenance only if necessary after source proof.
2. Read-only captures of documented PMU resource state/clock availability and CM3 core wrapper status at T3/T4, after validating exact BCM4329 chip-revision register semantics; avoid clear-on-read and disruptive registers.
3. Independently test a **genuine board-level power-down/reset** only once WLAN and Bluetooth shared-regulator consumers, ORed WL/BT_REG_ON, GPIO ownership and recovery paths have been audited. Never infer POR from module reload or regulator vote alone.
4. Separately assess original **January 2011 firmware 4.218.248.20** using the same-device (not transplanted) calibration provenance; do not change firmware and PMU in one trial.
5. Preserve existing `v025` verified temporary boot fallback and `v034` known-good USB runtime; `v035` is diagnostic only, no wlan0.

## End-of-session device verification

After the third trial, `WIFI_STOP` returned `brcmfmac_rc 0 brcmutil_rc 0`. Follow-up USB `MMC2_STATUS` on COM9 returned **`TARGET VALID`**, **`BOUND YES`**, **`CARD BCM4329 VERIFIED`**, **`DRIVER MODULES UNLOADED`**, and `AUTO profile = 0`. No reboot, flash or partition write occurred. Kernel remains temporary-boot v034; the v035 module binary is only staged in RAM.

**Acceptance labels:** v035 *compile PASS / USB upload CRC PASS / physical read-only observation PASS / repeatability 3 trials PASS / unload and stable MMC2 PASS / WLAN F2 FAIL (-62).* Do not promote v035 to a working-Wi-Fi kernel release.
