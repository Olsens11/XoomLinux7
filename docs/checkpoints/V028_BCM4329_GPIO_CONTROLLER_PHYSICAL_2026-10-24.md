# v028 — BCM4329 Bluetooth/WLAN Tegra20 GPIO controller readback

**2026-10-24, replacement MZ600, known v025 RAM boot.** Read-only module. No reflash or reboot; normal brcmfmac firmware startup occurs. Source: `scripts/experiments/v028-build-controller-readonly.py`.

## Verified binary and USB transfer

- ARM `brcmfmac-v028-forensic-readonly.ko`: **465700 bytes**, SHA256 `6ba10e6e7094e143cae7d5a0108f4723e5dbdf235c586bf619d8c55236e2f9e2`.
- Surface verified the file size and SHA256 independently of the Desktop build.
- USB RAM upload: `UPLOAD DONE SIZE 465700 CRC32 0x521308A4`.
- Kernel source `sdio.c` restored after build: SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab`.
- Console connection remained alive. Observations were recorded at approximately kernel monotonic t=12049.6 s; **not** at chip initial power-on.

## Direct Tegra20 register evidence

Linux driver `drivers/gpio/gpio-tegra.c` implements `GPIO_CNF`, `GPIO_OE`, `GPIO_OUT` and `GPIO_IN` offsets 0, 0x10, 0x20, 0x30, with Tegra20 bank stride 0x80 and port spacing four bytes. v028 read those registers by OF mapping `nvidia,tegra20-gpio`, **without requesting the GPIO or writing any control register**.

| Signal | Tegra number | CNF (GPIO mode) | OE (output) | OUT latch | IN register |
| --- | ---: | ---: | ---: | ---: | ---: |
| I7, BT_REG_ON / OEM BT_SHUTDOWN | 71 | 0 | 0 | 0 | 0 |
| U0, BT_RST_N | 160 | 0 | 0 | 0 | 0 |
| U1, BT_WAKE | 161 | 0 | 0 | 0 | 0 |
| U6, BT UART_WAKE | 166 | 0 | 0 | 0 | 0 |
| U2, WL_RST_N | 162 | 1 | 1 | 1 | 1 |
| U4, WL power | 164 | 1 | 1 | 1 | 1 |

**Interpretation:** This proves that, at the snapshot, I7/U0/U1/U6 were not configured in the Tegra GPIO block (`CNF=0`). It explains the earlier `gpiod_get_direction()=-22`: in this kernel, the driver explicitly returns `-EINVAL` for clear CNF. The input and output register zeroes when CNF=0 do **not** verify electrical levels at Broadcom pads. U2 and U4 were configured high outputs, their register IN bits also high; that still isn't a calibrated analog measurement.

The Broadcom chip's two regulator controls are ORed, so this snapshot reduces the likelihood of a *Tegra GPIO block-driven* high on I7 but cannot prove that BT_REG_ON is electrically low. No separate UART/BT driver-binding proof was obtained.

## Live bus behavior and final condition

The module saw the pwrseq LPO software clock enabled at 32768 Hz, MMC2 host `power_delay_ms=100`, and the **same F2 timeout**: `IOEx=06`, `IORx=02`, `clkcsr=d2`, `-62` roughly 3 seconds after F2 enable attempt. No `wlan0`.

Following the run, `WIFI_STOP` was executed. A subsequent `MMC2_STATUS` reconfirmed **target valid, card BCM4329 verified, MMC2 bound, AUTO profile 0, and Broadcom modules unloaded**. The Xoom remains on v025 RAM boot.

## Questions still requiring separate evidence

- Whether another Tegra pinmux function, external pull-up, bootloader setting or leakage sets I7 electrically high.
- Whether Bluetooth serdev/HCI UART is loaded or bound, and whether it could later reconfigure I7.
- Whether U4/U2 ever truly cycle during MMC rebind, and if an actual internal POR occurs.
- The 38.4 MHz normal reference, 32k LPO delivery, VDDC ramp and Cortex-M3 execution.
