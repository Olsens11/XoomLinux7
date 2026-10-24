# BCM4329 shared-resource sequencing prototype

**Compile-only proof, not deployed to a physical Xoom.** This is a Linux 7 kernel-source experiment. The module source compiled to a 32-bit ARM EABI5 relocatable object on the Desktop. It has **not** passed full module linking or run on the device.

The implementation exposes `wlan` and `bluetooth` targets sharing a clock/regulator dependency. The resource owner uses an existing **regulator API consumer vote**, rather than requesting Motorola's U4 GPIO a second time. It does not directly claim I7, U0 or U2.

The current kernel has `CONFIG_POWER_SEQUENCING` disabled. There are not yet consumer hooks in the MMC or Bluetooth drivers or a binding/DT instance for the provider. **Adding the node alone would have no effect.** The build uses the existing Linux 7 source and outputs a 6496-byte 32-bit ARM object (SHA256 `2c57bb47078921088e1a5fc1b9ca45deecf148b723c2d82bd61f9adf6c4c8ee8`).

Before a boot, the work must: enable and build the sequencing core; add a board binding; connect both MMC and `hci_bcm` targets without duplicate GPIO ownership; audit I7/U0 pinmux and regulator votes; keep Bluetooth inactive using a Motorola-grounded passive policy; and compare the result with the v025 control. The external normal reference clock and LPO are different resources and must not be conflated.

**No active power/reset sequence has been qualified, and Wi-Fi still fails F2.** The 20 passing logic-model tests do not prove this new kernel code runs.

See [whole-chip design](../../docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md) and [BCM4329 datasheet audit](../../docs/research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md).

## v028/v029 continuation
See [v028 physical GPIO register checkpoint](../../docs/checkpoints/V028_BCM4329_GPIO_CONTROLLER_PHYSICAL_2026-10-24.md) and [v029 isolated Linux 7 compile-only checkpoint](../../docs/checkpoints/V029_BCM4329_SHARED_OWNER_COMPILE_ONLY_2026-10-24.md). The new disabled DTS preview does not bind consumers or change the Xoom. Build-only: `bash scripts/experiments/v029-compile-shared-owner.sh`.
