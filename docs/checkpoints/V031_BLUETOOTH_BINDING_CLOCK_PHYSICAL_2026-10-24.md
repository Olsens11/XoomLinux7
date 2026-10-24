# v031 — physical Xoom Bluetooth binding and shared clock verification

**Date:** 2026-10-24. **Device:** replacement Motorola Xoom MZ600, existing v025 Linux 7 temporary RAM boot. This is a **read-only observer**, NOT a Bluetooth activation or BCM4329 fix.

## Experimental method

1. Rebuilt `brcmfmac` from the SHA256-pinned Linux 7 source with v021/v028 instrumented observer, adding Linux serdev controller/child/bound-driver inspection and actual clock-provider handle comparison.
2. Source builder: `scripts/experiments/v031-build-bt-binding-readonly.py`. It compiles in the private Linux build directory and restores original `sdio.c` bytes in `finally`.
3. Module `brcmfmac-v031-forensic-readonly.ko`: **468460 bytes**, SHA256 **`2e0b23244bd0f971f9562d0cbc61fea776c6c8a0e05afb9170f8e69c479365df`**.
4. Surface Book 2 independently verified the module SHA256 and byte count. USB RAM upload reported `UPLOAD DONE SIZE 468460 CRC32 0xB7F1D370`.
5. Ran one ordinary Wi-Fi probe with read-only inspection injected before Function 2 readiness. Retrieved kernel logs through established V20 serial USB protocol. Ran `WIFI_STOP`, then verified `MMC2_STATUS`. **No reboot, partition flash, regulator/GPIO write by the observer, Bluetooth module load, clock enable/disable, or Bluetooth state change.** Normal brcmfmac probe does download firmware and release the WLAN core as in previous tests.

## Actual runtime evidence, exact observation

| Item | Linux runtime result |
| --- | --- |
| UART OF node `/serial@70006200` | `UART_OF_AVAILABLE=1` |
| Child node `bluetooth` | `BT_CHILD=1 BT_OF_AVAILABLE=1` |
| Child compatible | `brcm,bcm4329-bt` |
| Registered Linux serdev controller | `UART_SERDEV_CTRL=PRESENT` |
| Registered serdev child | `CHILD=PRESENT` |
| **Driver bound to Bluetooth child** | **`DRIVER=NONE BT_BOUND=0`** |
| BT `txco` provider clock resolution | `BT_TXCO_CLK_RC=0` |
| WLAN `ext_clock` provider resolution | `WIFI_LPO_CLK_RC=0` |
| Live provider clock identity | `CLOCKS_SAME_HANDLE=1` |
| Live clock rates | `BT_RATE_HZ=32768 WIFI_RATE_HZ=32768` |
| WLAN U4 and U2 | GPIO CNF=1, OE=1, OUT=1, IN=1 |
| BT I7, U0, U1 and U6 | GPIO CNF=0, OE=0, OUT=0, IN=0 (not electric pin-level proof) |
| MMC2 after enumeration | `clock=25000000 timing=0` (legacy), `power_delay_ms=100` |
| Wi-Fi failure | F2 `IOEx=06 IORx=02`, `clkcsr=d2`, `result=-62` |

Recorded monotonic time for the combined read-only snapshot: `SNAPSHOT_BEGIN t_ns=16564701263000`, `SNAPSHOT_END t_ns=16564702487000`. The registered/unbound serdev observation is `t≈16564.7117 s`, well after boot, **not** an initial cold power-on waveform.

## Interpretation and limitations

**Strong new negative evidence:** the present Function 2 failure happens while the Broadcom Bluetooth serdev child exists but **is not bound to any driver**. That means no `hci_bcm`-owned runtime regulator voting or reset sequencing is presently occurring. Merely providing the v030 Motorola shared-U4 patch cannot change the current F2 outcome until a Bluetooth consumer is intentionally activated.

**Confirmed clock-role discrepancy:** in actual Linux clock provider state, Bluetooth's `txco` and Wi-Fi's LPO reference **the exact same 32768-Hz clock handle**. The actual Bluetooth driver treats `lpo` as a separate optional resource from normal `txco`. For correct board description, label this shared 32k provider **`lpo`**, not `txco`, until a separately verified normal-frequency oscillator is modeled. The Linux handle match does not verify chip-pad clock waveform or the physical 38.4-MHz normal reference.

**Unresolved:** a missing Bluetooth driver **does not** prove the external `BT_REG_ON` pad LOW: bootloader pinmux, external pullups, board wiring, or leakage could still matter. Tegra GPIO CNF=0 makes input register zeros unsuitable as electrical measurements. Nor does it prove that the internal BCM4329 core lost power on warm MMC2 rebind.

Linux pinctrl source clarifies that **PI7 is Tegra `GMI_WAIT`**, while U0/U1/U6 are GPIO-only pads. Proper GPIO acquisition during future Bluetooth activation would change these controllers' runtime states. Do not force these pins via arbitrary physical-address pokes.

## Post-test device condition

Ran `WIFI_STOP`, response `brcmfmac_rc 0 brcmutil_rc 0`. Then confirmed USB COM9 responsive, MMC2 target valid, BCM4329 verified, bound yes, modules unloaded and `xoom_mmc2_profile=0` (`AUTO`). No reboot or flash.

## Next gate

The next active experiment must use a **separate, rollbackable RAM boot** with fully reviewed GPIO owner transition, corrected 32k LPO clock name, exact 25-MHz legacy MMC2 control, and a USB-triggered Bluetooth test path that is off by default. Do not bind standard `hci_bcm` to the Xoom simply to make the chip reset before supply and pin sequencing are reviewed.

Reference: [v030 compile-only BT shared-U4 checkpoint](V030_BT_SHARED_U4_COMPILE_ONLY_2026-10-24.md) and [BCM4329 shared-chip research](../research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md).
