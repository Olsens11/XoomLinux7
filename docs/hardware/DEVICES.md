# Hardware roles and protection boundaries

| Role | Device | Purpose | Write policy |
| --- | --- | --- | --- |
| Protected reference | Original Motorola Xoom MZ600 | Advanced TWRP 3.1.1-0 XoomToolkit; proven recovery Wi-Fi/OEM behavior | Never touch as Linux DUT |
| Native Linux DUT | Separate replacement Motorola Xoom MZ600 | Nonpersistent Linux 7.0 kernel tests and USB diagnostics | `fastboot boot` only |
| Builder | Windows desktop + Ubuntu 22.04 WSL | ARM GNU 14.3 builds, initramfs images, variant source | No secrets/public calibration |
| USB console | Surface Book 2 | Physically connected test DUT, fastboot and USB CDC ACM COM diagnostics | Check actual serial before temporary boot |
| Reference archive | Raspberry Pi | OEM references, recovery build history, cross-project research | Preserve private snapshots |

Do not commit unique device serials, radio MACs, factory calibration, partition backups or pairing credentials. Live device identity is verified privately at each physical test. The Surface's USB/charger issue requires care: prior test Xoom has relied on dock for charging.

Safety is stronger than convenience: scripted rebuilds must never flash partitions implicitly. Manufacturer firmware retained as private reference only.
