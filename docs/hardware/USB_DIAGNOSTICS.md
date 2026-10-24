# Native USB diagnostics

v04 introduced Linux USB gadget CDC ACM, usable from Surface as a virtual serial port. `PING` responded with running kernel diagnostic version, supporting read-only STATUS/BOOTLOG/SDIO inspection. v05–v06 integrated maXTouch input, native crosshair/grid with touch mapping.

v014 extends this small freestanding initramfs PID1 with in-RAM hot-load diagnostics: `PING`, `WIFI_STATUS`, `WIFI_START`, `WIFI_STOP`, `WIFI_RETRY`, `WIFI_DEBUG N`, and `UPLOAD BRCMFMAC N`, `UPLOAD BRCMUTIL N`, `UPLOAD FIRMWARE N`, `UPLOAD NVRAM N`. The upload target set is constrained to known RAM paths, caps size to 1MiB, and reports CRC32; upload does not automatically execute module code.

The v014 transport and kernel module behavior are **proposed by source and offline build**, not verified in hardware. Preserve v013 as hardware-qualified fallback until v014 is tested. Full protocol/parsing safety, short writes and module lifecycle remain explicit test gates.

See [Wi-Fi investigation](WIFI_BCM4329.md), [checkpoints](../checkpoints/README.md).
