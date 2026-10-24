# v030 — Motorola BCM4329 Bluetooth shared U4 vote candidate

**Status: COMPILE-ONLY; NOT DEPLOYED.** 2026-10-24, Linux 7 Motorola Xoom MZ600.

## Purpose

Reconstruct the Bluetooth half of Motorola's original shared chip power coordination while preserving the current working SDIO/MMC owner. In the OEM downstream design both WLAN and Bluetooth voted on the shared U4 power enable. Generic Linux `hci_bcm` instead supplies BT from `vbat`/`vddio` and may drive I7 as a separate enable. This candidate adds an **explicit regulator API consumer vote** on existing U4-backed `reg_wifi_vdd`. It does not directly request U4, modify normal `vbat`/`vddio`, or replace `brcmfmac`.

## Files

- `patches/experiments/v030-stingray-hci-bcm-u4.patch`: targeted change to Linux 7 `drivers/bluetooth/hci_bcm.c`, **not applied** to canonical source.
- `scripts/experiments/v030-prepare-stingray-bt-u4.py`: regenerates this patch from the exact Linux 7 source and stages an isolated compiler copy; does not change the kernel source file.
- `scripts/experiments/v030-compile-and-dtb.sh`: reproduces ARM object and disabled DTB compilation; no device operation.
- `scripts/experiments/v030-check-stingray-bt-u4.py`: 21 static contract checks, not runtime tests.
- `src/chip/tegra20-stingray-bcm4329-bt-u4-v030.dtsi`: **disabled** Bluetooth child variant for syntax and phandle verification. No active DTB, kernel or firmware image produced.

## Motorola-only behavior

1. Both the explicit `motorola,stingray-bcm4329-bt` compatible and opt-in boolean `motorola,shared-u4-power` must be present; the fallback `brcm,bcm4329-bt` compatible maintains driver matching. Other Broadcom Bluetooth devices retain existing behavior.
2. Probe acquires the **existing** U4 GPIO-controlled regulator through `devm_regulator_get(dev, "shared")`, reading `shared-supply` in DT. Bluetooth's existing `vbat` and `vddio` consumers remain unchanged.
3. On Bluetooth on: one `regulator_enable` vote on shared U4 happens **before** normal regulator enable, clock operations and reset release. The vote is tracked to avoid double-counting if a previous error unwind could not release it.
4. If the normal power-on sequence fails, the code unwinds the shared vote and reports any secondary disable error. On Bluetooth off, the BT reset and wake control are changed first, then the shared vote is released, then normal clocks and regulators are disabled; a failed shared-regulator disable returns an error rather than claiming a completed transition.
5. On this board only, **I7 stays logically LOW** on both Bluetooth power transitions, matching the OEM BT rfkill policy. U0 remains the active-low Bluetooth reset. The default generic initial `GPIOD_OUT_LOW` for U0 would momentarily deassert active-low reset upon GPIO acquisition; the Motorola path instead requests `GPIOD_OUT_HIGH` so BT starts held in reset. This source-level improvement remains untested on physical silicon.
6. Kernel monotonic event logs (`XOOM_V030`) mark U4 vote on/off and commanded U0 reset transitions. A logged command is not proof of delivery to chip pads or of actual internal regulator state.

## Exact artifacts and checks

- Original Linux 7 `hci_bcm.c` SHA256: `3cdaf7e671babfc131f94909c009de0450e6da628786b2f9d9220c85d862bda2` (unchanged after builds).
- Final v030 patch SHA256: `c1876693d9f89c510287555ad828aa3fe3ff8e29041fb7c54e5686bc7309ff60`.
- Private ARM `hci_bcm.o` SHA256: `93eeb08011b0aac3fe0aae41395dc2f5655523ca6a87426826a8bb071275124f` (ELF 32-bit ARM EABI5 relocatable).
- `git apply --check` passed against Linux 7; kernel **object compilation** passed. Full driver/module link, load, and runtime Bluetooth behavior were **not** verified.
- Compiled experimental board DTB contains both compatible strings, Motorola opt-in, valid `shared-supply` phandle, and `status=disabled`. It still inherits the unqualified canonical 46.15 MHz SDIO frequency; it must NOT be used as a boot image. The physical v025 image remains limited to 25 MHz legacy SDIO.
- **21/21 static contracts passed**, including regulator ownership, reference-counting guards, rollback, Motorola reset default, unchanged generic behavior and disabled DT state.

## Explicit limitations and next gates

- **Bluetooth is not bound or active in the current tested state**, so a Bluetooth regulator vote cannot independently fix Wi-Fi's ongoing Function 2 `-62` timeout. This candidate is primarily infrastructure and OEM parity.
- A Motorola I7 policy of LOW is supported by the historical rfkill callback, but pin-level wiring, voltage, pinctrl startup state and whether the reset command reaches the chip still need physical or chip-side validation.
- There is still no enabled common `pwrseq` provider/consumer hookup; the shared regulator core supplies the first common resource vote, not complete whole-chip state coordination. The v029 disabled owner prototype is separate.
- `regulator-boot-on`, other consumers and Broadcom's ORed REG_ON inputs mean that releasing these software votes does not prove a real 1.25 V VDDC power cycle.
- Before enabling a UART child or loading this patched driver on real hardware: audit pinctrl for I7/U0/U1/U6, confirm normal oscillator versus 32k LPO clock assignment, review required DT bindings, validate supply mapping against OEM source, preserve v025 USB rollback, and instrument the *first* power/reset and F2 attempt using one monotonic timeline.
- Do not combine this experiment with MMC SDIO CCCR, oscillator, firmware, NVRAM, or power-delay modifications.

## Hardware baseline

At this checkpoint, the Xoom is still on v025 temporary Linux 7, USB alive, MMC2 bound and BCM4329 enumerated, `AUTO` profile 0, and Broadcom Wi-Fi modules unloaded. No partition flashed, BT pin reconfigured, or live regulator vote changed.
