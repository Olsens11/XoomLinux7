# Native USB diagnostics

v04 introduced Linux USB gadget CDC ACM, usable from Surface as a virtual serial port. `PING` responded with running kernel diagnostic version, supporting read-only STATUS/BOOTLOG/SDIO inspection. v05–v06 integrated maXTouch input, native crosshair/grid with touch mapping.

v014 extends this small freestanding initramfs PID1 with in-RAM hot-load diagnostics: `PING`, `WIFI_STATUS`, `WIFI_START`, `WIFI_STOP`, `WIFI_RETRY`, `WIFI_DEBUG N`, and `UPLOAD BRCMFMAC N`, `UPLOAD BRCMUTIL N`, `UPLOAD FIRMWARE N`, `UPLOAD NVRAM N`. The upload target set is constrained to known RAM paths, caps size to 1MiB, and reports CRC32; upload does not automatically execute module code.

v014 physically booted and loaded/unloaded modules, but its binary upload failed due to canonical tty. v015 physically passed raw USB mode, CRC firmware/module upload, debug control and hot-retry; native wlan0 remains absent.

See [Wi-Fi investigation](WIFI_BCM4329.md), [checkpoints](../checkpoints/README.md).
