# Clean upstream Linux 7 v06 — native Wi-Fi / Bluetooth modules and USB dashboard — OFFLINE PASS

**Date:** 2026-10-25. **Branch:** `wip/clean-wifi-bt-usb-20261025`. **Evidence class:** verified source build and host image inspection only; no new physical v06 boot, module insertion, radio start or firmware RF validation.

## Motivation and known working baseline

The identical, original clean-upstream v04 USB RAM-only image was physically booted successfully on replacement MZ600 **with removable 32GB microSD removed**. It showed framebuffer dashboard/advancing uptime; Surface COM9 USB PING/PONG and LOGS worked across multiple sessions; after >217 seconds the kernel was still responsive. Previously same v04 image with SD inserted dropped COM9. Preserve no-SD v04 binary immutable, use RAM-only tests. The user's objective is now integrate real standard Wi-Fi and Bluetooth support into a clean Linux kernel + dashboard, using USB for incremental testing and **no SD**.

## Isolated clean source and minimal identity patch

Created a **distinct git worktree** `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/linux`, pinned upstream `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, with exact preexisting known booting v04 Stingray USB0-peripheral DTS, build-only Makefile target, and the previously proven Motorola **per-device WLAN MAC ATAG → /wifi@1 FDT** converter patch `patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch`. The MAC is obtained from each tablet's bootloader, **not hard-coded or published**. No speculative whole-chip GPIO, 25MHz SDIO cap, clocks, regulatory US/69, regulator votes or FM changes.

For size and compatibility the **earlier physically Debian-booted OS kernel configuration** (not the huge all-drivers tegra_next_defconfig from clean v04) was used as *config only*, against new pinned **unmodified upstream source** plus the identity patch. It includes USB G_SERIAL, signed-regdb CFG80211 **built-in**, BRCMFMAC/BRCMUTIL as **modules**, normal separate WCC vendor module, Bluetooth HCI UART as module, no NEON, pstore/ramoops and ARM appended DTB/ATAG. `CONFIG_BRCMDBG` disabled; USB loader passes **no unsupported module debug argument**. This new kernel is not byte-identical to v04 and therefore requires separate boot safety validation.

Physical original v04 unaffected; factory p7/p8 unchanged and Android rollback intact.

## Build, provenance and exact hashes

Reproducible build source: `scripts/experiments/build-clean-wifi-bt-v06-kernel-20261025.py`.

**Offline clean kernel+modules build PASS**, compiler GCC ARM 14.3; kernel zImage 5,825,808 bytes, appended same-source Stingray DTB 61,104 bytes; combined **5,886,912 bytes**, SHA256 **`c81765bb8c43c44bc232da932d5547c32516c3c8259bd3e796ab6bf1f9b9dbfe`**. Linux release `7.0.0-next-20260422+`. Full in-tree `make modules` PASS, `Module.symvers` generated, matching `vermagic 7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8` for Wi-Fi, WCC and HCI UART modules.

RAM private initializer/boot packager: `scripts/experiments/package-clean-wifi-bt-v06-usb-20261025.py`. Reuses the established v034 USB upload and control program (armhf no-NEON) and source-identical, physically proven v04 framebuffer dashboard; restores original screen by default while leaving old GRID SHOW/HIDE optional mode. Adds live **BLUETOOTH** status row beside Wi-Fi and other hardware lines. BT reports HCI0 ACTIVE only when `/sys/class/bluetooth/hci0` physically exists, otherwise NOT ACTIVE. Wi-Fi reports `wlan0` presence, not RF association. Existing v034 BT_START/ON/OFF/STOP/STATUS, Wi-Fi START/STOP, bounded binary module/firmware NVRAM USB uploads, RAM only, read-only syslog and confirmation-gated reset commands retained.

The driver remains **upstream standard** rather than a custom monolithic WCC hack: separate `brcmfmac-wcc.ko` packed with normal `brcmfmac.ko` and `brcmutil.ko`. A tiny freestanding ARM `/sbin/modprobe` handles only `brcmfmac-wcc` kernel request_module and loads only the fixed path from its cpio or uploaded RAM staging. It is an **unproven userspace shim**, not a kernel source patch, and requires a physical module attach test before accepted. Standard Bluetooth dependencies ecc/ecdh_generic/cmac/bluetooth/btbcm/hci_uart are **rebuilt from same exact kernel**, not copied stale. Firmware and 1550B original generic NVRAM drawn from **previous private RAM initramfs**; no licensed blobs, unique MACs or credentials checked into public source. No RF on boot: modules load only after USB commands.

C source built with `-Werror` and `-mfpu=vfpv3-d16`, verified **NO NEON**, QEMU nonPID1 selftest PASS, WCC helper ELF compiled, cpio newc/gzip parsed and verified. Module version strings and package internal entries independently inspected.

Final boot image: `MZ600-CLEAN-WIFI-BT-USB-v06-RAM-ONLY-UNTESTED.img`, **6,547,456 bytes** (<8MiB p7 capacity); SHA256 **`c8240c65bf43064b82acec516ffc863e819db314e6f5fa0033586241390e00e9`**. Boot header kernel+DTB **5,886,912 bytes**, compressed ramdisk **657,360 bytes** (contains init, private Broadcom firmware/NVRAM, all matching Wi-Fi/BT modules and WCC loader). Independent Surface Android boot-image structure and header SHA-1 PASS; SHA checks matched on Desktop WSL, Desktop Windows, Surface.

Artifact locations:
- Desktop WSL: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts/`.
- Desktop Windows: `C:\Users\Olsen\MZ600-CLEAN-WIFI-BT-USB-v06-RAM-ONLY-UNTESTED.img`.
- Surface Windows: `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-CLEAN-WIFI-BT-USB-v06-RAM-ONLY-UNTESTED.img`.

**No physical v06 boot has occurred.** Live no-SD v04 remains accessible: verified multiple PING/PONGs, including after build; a brief 350-ms attempt produced no PONG because v04 USB PID1 polls ~1 sec; repeat with a 3-sec receive window got `V04_PONG_LONG_POLL=True`, `COM9_PRESENT=True`. Do not call initial short poll a failure.

## Controlled on-device acceptance plan (requires manual reboot into Android/fastboot)

Because currently running v04 USB PID1 is **read-only**, it cannot load ELF/modules/firmware or call reboot; there is no remote method to patch it alive through existing v04 protocol. User can manually reset using Power+Volume Up to stock Android, then remote host verified ADB `reboot bootloader` and **`fastboot boot`** this SHA-pinned image **RAM ONLY, NEVER FLASH**. Do not insert microSD during initial v06 control (isolate known failure variable). During first test:
1. Verify MZ600/fastboot unlocked, fixed image hash and 8 MiB limit; observe USB COM9 appearance, PING/PONG, stable dashboard and uptime for >prior failure window. Wi-Fi and BT rows initially NOT ACTIVE, no accidental modules loaded.
2. Read-only USB commands STATUS, LOGS, MMC2_STATUS, BT_STATUS, WIFI_STATUS, and identify onboard BCM4329 SDIO only after stable boot. Do not confuse removable microSD MMC slot with BCM4329's on-board SDIO path.
3. With no SD, use controlled WLAN path after verifying actual factory MAC delivered through FDT, signed regulatory domain and calibration source. Explicit WIFI_START loads in-RAM matched brcmutil and brcmfmac; the kernel invokes isolated WCC helper. Confirm F2 and wlan0. Do not scan/connect/transmit until provenance is validated.
4. BT_START/ON separately after Wi-Fi reset or unload. Match HCI0 and dashboard, log any required BCM4329B1 .hcd firmware; HCD currently missing from staging, so **Bluetooth hardware functionality is not yet physically demonstrated**.
5. Stop modules and retain reversible test image, quantify repeated stability, eventually address entire chip shared power and optional FM once physically supported.

**Status:** source/tool/firmware-and-module CPIO packaged and independently verified; physical v06 Wi-Fi/Bluetooth *UNTESTED*. The prior no-SD v04 image remains preserved as last physical successful fallback; no Android p7/p8, TWRP p6, user data or SD changes.

## Guarded first-boot launcher prepared (not executed)

Surface local file `C:\\Users\\olsen\\xoom-linux-rom\\captures\\Xoom-V06-Clean-WiFi-BT-USB-Once.ps1` exists and passed PowerShell parser syntax check. It checks candidate image exact hash/size; if stock Android is booted, confirms hardware/boot-completed then reboots to bootloader; if already in fastboot, confirms unlocked `xoom-cdma`. It invokes **only fastboot boot** (RAM-only, not flash), watches COM9 75 seconds, attempts USB PING/PONG and read-only BT_STATUS. It deliberately **never invokes WIFI_START or BT_START**, does not reset automatically, and writes private timestamped logs only on Surface. **It is not yet run** because the active stable no-SD v04 lacks a USB reboot command; requires the user physically to return to Android or fastboot first.

Final host check: v04 original still COM9 present and answers `PONG XOOM-LINUX V04` on a multi-second receive window. No need to intervene in that working session until physical one-shot test is desired. Reinsert no microSD for v06 first-boot A/B.
