# v032 — correct Bluetooth LPO role in disabled board preview

**2026-10-24, SOURCE-ONLY**, based on v031's physical confirmation that both the generic Bluetooth `txco` and WLAN `ext_clock` resolve to the **same 32768-Hz Linux clock**. No changes were made to the running Xoom or its boot image.

## Proposed change and rationale

Existing Xoom DTS Bluetooth child supplies `clocks=<&tegra_pmc TEGRA_PMC_CLK_BLINK>` but names that 32.768-kHz provider `"txco"`. The Wi-Fi pwrseq references the same provider as `ext_clock`, and v031's physical kernel reports `CLOCKS_SAME_HANDLE=1`, both 32768 Hz. Linux 7 `hci_bcm` distinguishes the optional `"lpo"` clock (32.768 kHz) from optional `"txco"` (normal reference).

`src/chip/tegra20-stingray-bcm4329-bt-lpo-v032.dtsi` is a **disabled** board overlay that retains all of v030's shared-regulator and Motorola compatible/opt-in properties but adds:

```dts
clocks = <&tegra_pmc TEGRA_PMC_CLK_BLINK>;
clock-names = "lpo";
status = "disabled";
```

This corrects the clock role without asserting that the BCM4329's **normal crystal/TCXO frequency is known**. The normal oscillator must be independently traced via Motorola OEM board design and chip PMU before enabling Bluetooth.

## Reproducible checks

Run `python3 scripts/experiments/v032-check-lpo-overlay.py` on the Desktop with the Linux 7 source and GCC+dtc installed. The script builds a private DTS/DTB copy in `phase1-v032-bt-lpo` and checks:

- Bluetooth remains disabled; clock name is `lpo`, not `txco`.
- Bluetooth and WLAN clock specifiers refer to the same provider phandle.
- Bluetooth's new `shared-supply` resolves to the exact existing MMC2 `vmmc-supply` U4 regulator.
- Opt-in compatible and property remain; default `vbat/vddio` declarations are not overridden.
- I7/U0 GPIO references remain present but have **not** been requested/driven.
- Linux 7 HCI driver supports distinct `lpo` and `txco` clock handles.
- The canonical MMC2 legacy-limit mismatch remains **unfixed** in the private preview (46,153,846 Hz). **This preview is NOT bootable or a substitute for the physical v025 25-MHz control.**

**12/12 checks PASS**. Private experimental DTB SHA256: `467c7ac1818271deaf62da6d6326b20cd59337756ed38db50c10b922ebbb5bb2`. Original canonical board DTS and kernel unchanged.

## Unverified before activation

A compile-only DT binding is not a physical clock test. Neither normal reference-clock hardware, LPO chip-pad delivery, Tegra PI7/U0 pinmux activation, shared rail power-off, nor Cortex-M3 execution is proven. The v030 HCI driver object is not yet linked or deployed. Review exact DT schema for the added Motorola properties and avoid duplicate U4 ownership.

See [v031 live clock and binding checkpoint](V031_BLUETOOTH_BINDING_CLOCK_PHYSICAL_2026-10-24.md), [v030 shared U4 candidate](V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md) and [full datasheet audit](../research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md).
