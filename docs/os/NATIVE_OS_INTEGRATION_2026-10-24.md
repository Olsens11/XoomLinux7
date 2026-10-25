# Native Linux 7 OS on the Motorola Xoom MZ600 — installation workstream

**Status, 2026-10-24:** OS integration development started on `os/mz600-native-rootfs-wifi-20261024`. ARMhf Debian Bookworm **two-stage rootfs bootstrap passed**; staged 323 MiB *before kernel modules*, original generic firmware and 1550-byte exact proven calibration staged; USB ACM getty enabled; MAC-gated upstream Wi-Fi service configured. Clean native kernel build **is being validated**. None of these steps constitutes an installed or boot-tested OS. No eMMC partitions, Android, recovery or original Xoom have been modified.

## Requested direction

The active development target is **the installed Linux root filesystem on the replacement Xoom**, not the temporary fastboot diagnostic environment. Keep only established native hardware support and a basic **USB serial login**. Preserve the upstream Linux subsystem drivers and normal Linux userspace; remove `XOOM_V0xx` diagnostic probes, private console dumps, temporary RAM upload client, and v045's inline WCC workaround.

Kernel source is pinned to `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, kernel identity `7.0.0-next-20260422`. Actual board: MZ600 Stingray/Tegra20, not Wingray or a generic laptop. Kernel retains existing display, Atmel touch, CPCAP, MMC2 Wi-Fi, SDMMC4 eMMC, UART BT, regulators, clocks and USB gadget config from the proven v034 temporary kernel. **No new physical components or regulator changes.**

## Build outputs and integration

- Native armhf OS root: `$B/os-build/bookworm-armhf-root`; boot intended to mount genuine GPT partition `system` (TWRP fstab calls it Android `/system`, corresponding to p8 in previous backups). Stage rootfs independently; *never* mount/write the target directly during image creation. Original OS contents must be backed up before any future write.
- Stable kernel config: existing Linux 7 config with **`CONFIG_INITRAMFS_SOURCE=""`** and otherwise same board drivers; no embedded temporary diagnostic initramfs. Kernel `zImage` appended with `tegra20-motorola-stingray-usbdiag.dtb` (existing proven USB0 UDC/peripheral-mode hardware description, not the old diagnostic userland) and packaged as a normal boot image with `root=PARTLABEL=system rootfstype=ext4 rootwait rw init=/sbin/init`.
- Userland: Debian Bookworm armhf (ARMv7 hard-float, no NEON assumption), systemd, udev/kmod, native Wi-Fi tooling `iw`, `wpa_supplicant`, iproute2, openssh package. **No credentials or automatic association preconfigured**.
- USB: kernel's **standard `CONFIG_USB_G_SERIAL=y`**, rootfs enables stock systemd `serial-getty@ttyGS0.service`. The host COM number may change from the diagnostic environment's COM9. This is a login-capable normal OS, not the custom USB `PING/UPLOAD` diagnostic protocol.
- Firmware: original exact 253748-byte generic BCM4329 SDIO 4.220.48 binary SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93` staged locally, **not** checked into public Git. The public OS calibration file `configs/os/brcmfmac4329-sdio.stingray-calibration-no-identity.txt` is **1550 bytes** SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`, exactly the configuration used in v026 through v043, omitting `macaddr`, `ccode`, and `regrev`. Regulatory provisioning is deferred to policy.
- Upstream modular Wi-Fi: clean `brcmutil.ko`, `brcmfmac.ko`, **separate `brcmfmac-wcc.ko`** built from the pinned source and installed via `make modules_install`/depmod. v045 proved `wlan0` when WCC was linked temporarily; the installed OS will use the ordinary plugin architecture. No `XOOM_V` debug code in final brcmfmac module.
- MAC validation: `mz600-wlan.service` is enabled; `blacklist brcmfmac` prevents opportunistic alias auto-load before identity validation, while allowing explicit `modprobe`. Service checks binary `/sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address` is six bytes, nonzero, unicast, not unprogrammed Motorola fallback, and then loads WCC and brcmfmac. Logs never print the raw MAC.

## Generic factory-MAC conversion (kernel source patch)

`patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch` is the **only targeted kernel code alteration**. The *normal ARM decompressor* `atags_to_fdt.c` checks Motorola vendor tag `ATAG_STINGRAY_MAC = 0x57464d41`, takes the original six-byte value that old `board-stingray-wifi.c` used, validates it, and places it in **the actual Wi-Fi child Device Tree node** (`/mmc@c8000200/wifi@1`) as `local-mac-address`. Upstream Linux 7's existing `brcmf_fw_nvram_strip` calls `eth_platform_get_mac_address(dev, mac)` and adds that address to the packed NVRAM **before firmware CPU release**, which is exactly the missing step physically proven by v044.

**Important unverified gate:** Motorola's ATAG is documented in OEM source, but we have **not yet physically proven that the normal installed OS bootloader path passes that tag through this modern appended-DTB converter** on the replacement device. If the bootloader gives a preexisting FDT instead, the converter returns early. If ATAG missing/invalid, no MAC gets invented; Wi-Fi service skips/fails and USB login remains available. Actual target's unique identity must be verified privately before allowing RF. A fallback factory provider, if needed, must also be from the *same unit*, not the original ROM's common bootstrap macaddr.

## Offline build and deployment order

1. `bash scripts/os/build-clean-kernel.sh` as `xoomdev` in desktop WSL. Uses a temporary exact-source-hash-guarded kernel patch, a **separate OS kernel output tree**, the already-verified Stingray USB0-peripheral DTS variant (the only one that exposes g_serial on the physical USB connector), no diagnostic initramfs. Restores pristine source on exit, checks separate WCC output.
2. Build/stage Debian Bookworm armhf into `$B/os-build/bookworm-armhf-root` with `debootstrap --foreign --arch=armhf --variant=minbase` followed by ARM QEMU-assisted second stage. We successfully completed both stages.
3. `sudo bash scripts/os/configure-rootfs.sh "$B/os-build/bookworm-armhf-root" "$B/firmware-reference-v07/brcm/brcmfmac4329-sdio.bin"`. Verified safe source hashes and enabled USB getty/MAC-gated Wi-Fi.
4. `sudo bash scripts/os/install-kernel-modules.sh "$B/os-build/bookworm-armhf-root"`. Installs actual clean kernel modules plus separate upstream WCC and depmod data.
5. Provision an owner account **privately**, with a unique password or key and no default credentials. Test under ARM user-mode emulation. A locked, unprovisioned rootfs **MUST NOT** be deployed. Don't ask the user to send a password to ChatGPT.
6. `sudo bash scripts/os/package-native-os.sh "$B/os-build/bookworm-armhf-root"` produces uninstalled offline `xoom-linux-system.ext4` and `xoom-linux-boot.img` plus SHA256SUMS and a prominent NOT_INSTALLED marker. Images are candidates pending target partition-capacity proof.
7. **STOP before any persistent write.** Reverify connected replacement Xoom's exact GPT partition identities and capacities in a *read-only* session, verify and preserve original Android system/boot backups off-device, obtain the user's explicit permission for the exact named `system` and `boot` writes, and leave separate `recovery` and userdata untouched.
8. After an approved installation: first test ttyGS0 login and systemd root, then inspect the private FDT MAC status (only validity publicly), verify separate WCC registers, `wlan0` is created, and confirm no network RF scan/association until unique MAC/regulatory provenance is accepted. Cold/warm restart, SDIO/BT coexistence and input/display follow.

## Current acceptance boundaries

- **PHYSICALLY PROVEN:** v044 verified missing NVRAM bootstrap MAC caused F2 -62, v045 loaded upstream-equivalent WCC and reported real `wlan0`; temporary-boot test was safely reverted.
- **BUILD/FILE-STAGED:** Debian ARMhf second stage completed and exact firmware/calibration + getty/Wi-Fi service populated.
- **NOT PROVEN:** OEM ATAG observable on the replacement unit under normal installed OS boot; clean OS kernel boot; actual native system partition root mount, getty login over new gadget, upstream separate WCC module load, production-MAC `wlan0`, scans/association/long-term stability.
- **NOT DONE:** rootfs/boot partition installation. Original Xoom and replacement Xoom data have not been overwritten.

## Upstream cooperation

Base reference: [xoom-linux/linux](https://github.com/xoom-linux/linux), with original Wingray DTS. Once the normal OS and per-unit factory MAC path pass physical tests, prepare a small attributable PR/issue explaining (a) BCM4329 firmware console `wireless side err21` from absent bootstrap MAC, (b) confirmed F2 `-62` to F2 `0` transition with only NVRAM MAC added, (c) separate WCC module packaging requirement, (d) the *minimal* bootloader ATAG/FDT integration and working Wi-Fi evidence. No proprietary firmware, device MAC, raw logs or calibration secrets in upstream contribution. Do not contact the maintainer or claim a production fix until these gates pass.

## Revision: Android-preserving, directly mounted Linux root (2026-10-24)

**Supersedes the original `system`-replacement destination.** User wants conventional Linux installation and a reversible Android return, while preserving existing Android files. The new build target is a **dedicated Linux ext4 GPT partition labeled `xoom-linux`**, first choice a safe independently provisioned internal partition if its availability can be proven; second choice a microSD partition if internal repartitioning would put Android data at risk. Linux runs directly from its own block filesystem with `root=PARTLABEL=xoom-linux rootfstype=ext4 rootwait`; `/etc/fstab` uses the same label. **No loop-file / pivot_root hack, and no Android `system` overwrite.**

Previous 2026-10-24 images with `root=PARTLABEL=system` were offline-valid only for the now-rejected system-replacement plan. **Never flash them.** Regenerate image and hashes for `xoom-linux`. This is still **NOT an approved partition creation**: same-unit GPT data and stable free space are unknown. The generated 768 MiB ext4 root image is a candidate *payload* and must fit a separately allocated ≥768 MiB GPT partition without overwriting Android's system/userdata/cache/recovery.

The target remains a legacy device with no qualified on-device boot selector. The Android boot image must be preserved off-device, and the ability to restore/select it must be proven before any persistent boot modification. Switching boot images is distinct from altering Android's system files. This plan is recorded in [comprehensive breakthrough](../checkpoints/BCM4329_BREAKTHROUGH_AND_NATIVE_OS_MILESTONE_2026-10-24.md).
