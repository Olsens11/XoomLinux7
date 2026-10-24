# Motorola Xoom MZ604 — modern Linux cross-build workspace
Prepared on DESKTOP-R16QJD4 under Ubuntu-22.04 WSL2 (user xoomdev), 2026-10-23.

## Sources and state
- Primary candidate: https://github.com/xoom-linux/linux, **exact** commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, a Linux 7.0-dev tree patched for Xoom.
- Source archive: `~/xoom-linux-rom/xoom-linux-2404d273.tar.gz`, SHA256 `4162c783023f38a9a56fd162b3ae622307ecafdd2be02a8451fcb98c4a511a1d`, gzip integrity tested and extracted into `~/xoom-linux-rom/linux-src/` (1.8 GiB approx).
- The attempted partial `~/xoom-linux-rom/linux/` Git clone was aborted after slow fetch; use `linux-src/` for now. Rehydrate Git metadata later for patches as needed.
- Initial build config: `~/xoom-linux-rom/build-wingray/.config`; based on `tegra_next_defconfig`, then `CONFIG_NEON=n` and debug info disabled, followed by `olddefconfig`. Includes Tegra20, ARMv7, eMMC/SDMMC, input, DRM/Tegra, CPCAP and Broadcom Wi-Fi drivers.
- Xoom board DTB target: `nvidia/tegra20-motorola-wingray.dtb` — compiled successfully in initial pass.
- First build wrapper `~/xoom-linux-rom/build-wingray.sh`, initial log `build-wingray-20261023.log`; run was stopped gracefully mid-build to increase parallel jobs and resume from completed objects. Resume script `C:\Users\olsen\xoom-resume-wingray.sh`; resume log `build-wingray-resume-20261023.log`.
- This is **build-only**. Nothing is flashed, no device was queried. Original Xoom on Surface USB must remain untouched. A new MZ604 must be positively identified and isolated first.

## Build tools
- The normal Ubuntu cross-GCC 11 toolchain was initially installed, and the first build uses `arm-linux-gnueabihf-`.
- To avoid conflict with existing Android recovery builds' `gcc-multilib` and `g++-multilib`, standalone **Arm GNU Toolchain 14.3.Rel1** downloaded (HTTPS from Arm-hosted blob) and extracted under:
`~/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/`
- Original standalone archive SHA256: `3ec0113af5154a2573b3851d74d9e9501a805abf9dfa0f82b04ef26fa0e6fc35`; passed `xz -t`.
- Its compiler is `.../bin/arm-none-linux-gnueabihf-gcc`, version 14.3.1. For future *fresh* builds, use `CROSS_COMPILE=/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-`.
- Restore `gcc-multilib` and `g++-multilib` after initial GCC11 compile ends; Ubuntu apt will remove gcc11 ARM cross-compiler packages but the standalone toolchain remains available. **Do not restore during a live GCC11 build.**
- WSL has around 7.7 GiB memory and the Windows host 12 logical CPU threads. `-j8` available with care for memory.

## Xoom hardware and ROM constraints
- Source's DTS includes Xoom eMMC, microSD, BCM4329 Wi-Fi/BT, Atmel maXTouch touchscreen, LVDS panel and CPCAP PMIC.
- DTS includes unfinished comments and battery node disabled; power/charging/sound are **not proven working**. Do not use as unattended daily ROM until tested.
- Board DTS currently reserves 256 MiB CMA out of 1 GiB RAM, likely worth optimizing for Electron after display is validated.
- User's desired layout: Debian ARMHF on SYSTEM, Windows95 emulator + VM image on USERDATA, standard TWRP on RECOVERY, custom Linux kernel on BOOT; no BigPart by default.
- Original MZ600 had ~8 MiB boot partition and 12 MiB recovery; sizes on NEW stock MZ604 MUST be verified before creating and flashing an Android-style boot.img.
- First safe hardware milestone: stock device identity/serial verified, TWRP backed up, minimal diagnostic kernel boot with console, no userdata mount, and rollback available.
- Windows95 ARMHF package's Electron and FFmpeg contain NEON instructions, so no guarantee of successful native execution on Tegra2 without compatibility work.

## Verified completed ARM kernel build — 2026-10-23
- `build-wingray/arch/arm/boot/zImage`: **5,653,872 bytes**, SHA256 `bc754bee0b87ef68cfbd7f29be5fae1a66c0d3b3a56e76db73c1ff1279e0df19`.
- `build-wingray/arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dtb`: **61,056 bytes**, SHA256 `c833f45e529dedaa70ff5f79e61f639236748c1be608020206039e1c834b6eef`.
- `artifacts/wingray-kernel-dtb-NOT-FLASHABLE.bin`: appended DTB to zImage, **5,714,928 bytes**, SHA256 `f36bca6eba4056c5bf498566a4393d3fbe15563f95876b1569641e787a4d8bdb`. This file is NOT an Android boot.img and MUST NOT be flashed by itself.
- `tegra20-wingray-phase1.config`: SHA256 `c43df07b16662a9d2d63c2b895757c66f25c93050d923d4058e142de5b1364b7`; disables NEON, unused ST sensor hub, XFS, Btrfs, F2FS, media and PCI/ATA; retains Tegra20, DRMTegra, CPCAP, touchscreen, ext4, SD/MMC, devtmpfs. Initial generic `tegra_next_defconfig` preserved as `tegra-next-initial.config`.
- Initial broad kernel build compiled its device tree, but a non-Xoom ST sensor-hub driver `st_sensor_hub.c` failed to include `linux/of_gpio.h`; disabling `CONFIG_IIO_ST_HUB_DRIVERS` fixed this without changing the source.
- During a later eight-job run GCC 11 had a transient internal Segmentation Fault compiling `drivers/gpu/drm/tegra/nvjpg.c`; same object compiled successfully on a single-job retry. The final compressed kernel was compiled at `-j4` and log explicitly ended `Kernel: arch/arm/boot/zImage is ready`. Its wrapper reported a later input-file read error because a Windows-mounted shell script was edited while bash was still reading it; the build output and log were independently checked and verified. For future execution, run scripts copied into WSL storage, not editing a script concurrently from Windows.
- Ubuntu's `gcc-multilib` and `g++-multilib` packages were restored and `gcc -m32 -c` successfully tested, protecting older Android builds.
- Independent standalone Arm GNU Toolchain 14.3 was tested **after** restoring multilib with Cortex-A9, `-mfpu=vfpv3-d16 -mfloat-abi=hard`, producing a verified ELF32 ARM EABI object. `build-wingray-gcc14.sh` stages a **separate**, not-yet-executed GCC14 kernel build under `build-wingray-gcc14/`. It must be run explicitly for a fresh toolchain build.
- Original surface-connected Xoom was not queried or modified. No adb/fastboot calls, flash, kernel boot or hardware test was performed.

### Next critical milestone
Identify a NEW MZ604 physically isolated from original MZ600, back up original partitions, install standard TWRP, and prepare a minimal initramfs plus verified model-specific Android boot.img for a supervised nonpersistent/rollback-ready diagnostic boot. Verify actual new-device partition sizes first. Audio/charging/battery driver gaps remain unresolved; source compilation is NOT hardware support verification.
