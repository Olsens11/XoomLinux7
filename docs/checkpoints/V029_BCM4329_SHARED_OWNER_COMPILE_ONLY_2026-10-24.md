# v029 — BCM4329 shared-owner compile-only checkpoint (2026-10-24)

**Not a booted fix.** The physical Xoom stays on the verified v025 temporary kernel; MMC2 bound, AUTO, Wi-Fi modules unloaded, and F2 still times out -62.

## Verifications

- The base running kernel configuration has `CONFIG_POWER_SEQUENCING` disabled.
- An **isolated** build configuration enabled `CONFIG_POWER_SEQUENCING=y`; `olddefconfig`, `prepare`, `modules_prepare`, generic `drivers/power/sequencing/core.o`, and `src/chip/stingray-bcm4329-pwrseq.o` compiled using the Linux 7 ARM toolchain. Object compilation is not successful module linkage or hardware integration.
- The experimental `src/chip/tegra20-stingray-bcm4329-owner-v029.dtsi` was appended to a private board-DTS copy and passed GCC preprocessing plus DTC compilation. The resulting DTB reports `status=disabled`, a resolved `shared-supply` reference and LPO clock `<0x26 0x03>`. No boot DTB or canonical DTS changed.
- The preview inherits the **unqualified** 46,153,846 Hz MMC2 base frequency; the real v025 image is 25 MHz legacy. Never substitute the preview DTB for a tested boot image.

## Consumer integration cannot be assumed

The provider defines named WLAN and Bluetooth targets sharing a common supply/clock unit, but **neither subsystem acquires these targets yet**. Linux's MMC path uses `mmc-pwrseq-simple` and Bluetooth `hci_bcm` uses its own regulator and GPIO APIs. A DTS node alone is inert.

- `mmc-pwrseq-simple` has a **void** pre-power hook. A failed new shared-power operation cannot be safely propagated by inserting it there without redesign.
- `hci_bcm` already uses `regulator_bulk_enable/disable` for Bluetooth `vbat` and `vddio`. Current `vbat` uses `vdd_3v3_sys`; Motorola OEM Bluetooth and Wi-Fi both voted on U4. A narrow implementation candidate is routing Bluetooth's shared-power vote through the already-owned U4-backed regulator, after validating the board and rollback.
- `hci_bcm` would also toggle I7 (`shutdown`) and U0 (reset) on binding. Motorola's rfkill callback instead held I7 low in both branches. **Do not load or enable Bluetooth merely to test power** until the I7/U0 pinmux and ownership are deliberately resolved.
- The shared power provider must not request U4 itself: the fixed-regulator driver already owns that GPIO.
- Broadcom's ORed `WL_REG_ON`/`BT_REG_ON` controls do not prove full power-off from software votes alone.

## Source and reproduction

- Provider: `src/chip/stingray-bcm4329-pwrseq.c`.
- Disabled device-tree fixture: `src/chip/tegra20-stingray-bcm4329-owner-v029.dtsi`.
- Kbuild/Kconfig prototype: `src/chip/Makefile`, `src/chip/Kconfig`.
- Rebuild test: `bash scripts/experiments/v029-compile-shared-owner.sh`.
- Physical evidence: [v028 GPIO controller checkpoint](V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md).
- Background: [Motorola OEM shared-chip reconstruction](../research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md).

## Next gates

1. Trace actual BT serial driver binding and pinmux/clock ownership without requesting pins.
2. Design an **error-propagating** MMC and Bluetooth regulator vote interface, separate from I7/U0 GPIO control, and compile test.
3. Qualify source DTS, produced DTB, power-event logs, and v025 rollback before an actuating RAM-only boot.
4. Do not label GPIO register 0 as an electrical LOW when CNF=0, and do not claim root cause while F2 remains -62.
