
> **SUPERSEDED DEPLOYMENT TARGET:** This checkpoint preserves the historically accepted offline build made for the original (now rejected) Android `system` replacement scheme. Its boot image `ba50...` and root image `398e...` are archived **DO NOT INSTALL**. For the latest Android-preserving, independently named root image and boot image, see [Android-preserving rebuild](ANDROID_PRESERVING_NATIVE_OS_OFFLINE_REBUILD_2026-10-24.md), verified `root=PARTLABEL=xoom-linux`, and [master breakthrough milestone](BCM4329_BREAKTHROUGH_AND_NATIVE_OS_MILESTONE_2026-10-24.md).

# Native MZ600 OS images — completed OFFLINE build and acceptance (2026-10-24)

**State:** OFFLINE BUILD PASS / EXT4 IMAGE PASS / CLEAN KERNEL PASS / DRIVER PACKAGE PASS / USB OS GETTY STAGED / **NOT INSTALLED OR HARDWARE BOOTED**. This checkpoint is for the dedicated `os/mz600-native-rootfs-wifi-20261024` branch, not replacement of the physically accepted v045 temporary-boot evidence.

## Artifacts on user's DESKTOP-R16QJD4 (Ubuntu-22.04 WSL)

```text
/home/xoomdev/xoom-linux-rom/os-build/artifacts/
    xoom-linux-system.ext4        805306368 bytes, sparse ext4 (768 MiB)
    xoom-linux-boot.img           5890048 bytes, Android boot format
    zImage-stingray-with-dtb      normal kernel and USB0 peripheral DTB appended
    SHA256SUMS                    checksum manifest
    NOT_INSTALLED.txt             non-destructive hold marker
```

| Offline artifact | SHA-256 |
| --- | --- |
| `xoom-linux-boot.img` | `ba50d08165376724236e959cc19e6ca8de781b488748a221b2a9bc3b48fa9967` |
| `xoom-linux-system.ext4` | `398e0991700bb1769a8d8fa01fd50b96970d9f6e4dfe7d08952a78b6ff151bb8` |
| Kernel `zImage` | `7174bd220b2466b695f03363832e4158899d0caca917a782903268868e07ccc7` |
| USB0 UDC DTB `tegra20-motorola-stingray-usbdiag.dtb` | `afae7fb328bc66c0ea186ef6c8e77164c41be8588bb5d14303374a3545499959` |
| Clean `brcmfmac.ko` (unstripped build intermediate) | `39b83c8cdded5e585c6d886df89a3c01328adf928f0798db692c63c71d152f9f` |
| Clean modular `brcmfmac-wcc.ko` (unstripped build intermediate) | `740cfea66bb4eb9e7f4faab906ae4fd23ab4f6fe6b7375712773bb8610e38e7f` |

Compiled pinned kernel `7.0.0-next-20260422` against GCC14 ARM hard-float toolchain, retained Xoom hardware options, removed the embedded diagnostic initramfs and `CONFIG_BRCMDBG`, and applied **only** the Motorola `ATAG_STINGRAY_MAC`→`local-mac-address` code patch. The original `linux-src/arch/arm/boot/compressed/atags_to_fdt.c` hash was restored **`3052214e2f76ee1e3bc5226b73a2515185f20ef7e0ea279a004d8931d764a193`** after build. The early boot converter `atags_to_fdt.o` demonstrably contains the new property string, no device MAC bytes.

Kernel built with the **verified USB0 peripheral** DTB even though its historical source filename contains `usbdiag`; only the USB controller's hardware mode is relevant, not the old custom USB diagnostic userspace. Kernel uses `CONFIG_USB_G_SERIAL=y`, systemd starts serial login on `ttyGS0` and a normal armhf userspace. No fastboot protocol is required *by the installed OS itself*.

Staged Debian Bookworm armhf userspace completed both debootstrap stages under QEMU, installed `systemd-sysv`, `udev`, `kmod`, `iproute2`, `iw`, `wpasupplicant`, `openssh-server`, and `sudo`. Staging size was 323MiB before modules and ~441MiB with matching native kernel modules installed. Owner account `xoom` has a unique first-login password, **stored only in a restricted local WSL file** `$B/os-build/private/xoom-firstboot-login.txt`, never printed or published. Root password remains locked. The host-only x86 QEMU helper was excluded from the packaged ARM image.

Original physically qualified Wi-Fi artifacts:
- `brcmfmac4329-sdio.bin`, 253748 bytes SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, staged locally not committed.
- `brcmfmac4329-sdio.txt`, exactly 1550 bytes SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`, MAC/regulatory-ID-free and matched to v044/v045's **baseline**. Per-device MAC is inserted dynamically by upstream `brcmfmac` NVRAM firmware path if the Motorola bootloader ATAG reached the FDT child during early normal boot.
- `brcmfmac.ko`, **separate `brcmfmac-wcc.ko`**, `brcmutil.ko` and all kernel dependency modules installed in `/lib/modules/7.0.0-next-20260422` using standard `modules_install` and `depmod`. No inline WCC vendor workaround or `XOOM_Vxx` instrumentation.
- Installed OS `mz600-wlan.service` only explicitly loads WCC and brcmfmac after checking a valid local-mac-address property; udev alias autoload of brcmfmac is suppressed until then. This leaves the USB login usable if the MAC handoff is absent.

## Actual offline validation

[`scripts/os/verify-offline-native-os.py`](../../scripts/os/verify-offline-native-os.py) as root returned **`NATIVE_OS_OFFLINE_ACCEPTANCE_PASS`**, covering:
1. `ANDROID!` boot header, 2048-page boot image, exact combined `zImage + USB peripheral DTB` payload bytes and **zero diagnostic initramfs**, normal Linux root command line `root=PARTLABEL=system rootfstype=ext4 rootwait rw init=/sbin/init`.
2. Real DTB `/usb@c5000000` `compatible=nvidia,tegra20-udc`, `dr_mode=peripheral`; BCM4329 SDIO child found; **no static MAC in FDT**; compiled `atags_to_fdt.o` contains `local-mac-address` converter.
3. Exact generic firmware SHA256 and byte-exact MAC-free calibration SHA256.
4. Separate WCC and brcmfmac modules installed; depmod index; no `XOOM_V0xx` instrumentation in clean driver.
5. systemd USB serial-getty and identity-gated Wi-Fi unit links; non-default private account password hash present; no x86 emulator binary in final ARM OS.
6. `e2fsck -fn` on **unmounted** 768MiB ext4 file returned 0 (clean), and `NOT_INSTALLED.txt` marker present.

## Physical / installation gates NOT yet passed

- **The replacement Xoom was NOT repartitioned, flashed, rebooted or altered.** Existing Android `system`, `boot`, `userdata` and TWRP `recovery` are unchanged.
- Need a *same-unit* read-only GPT map with exact partition labels, GUIDs and capacities and verified off-device Android `boot`/`system` backups before changing any partition.
- Normal-boot availability of Motorola's `ATAG_STINGRAY_MAC` on the replacement unit **not physically proven**; if absent, the early FDT property won't exist and WLAN is deliberately disabled. The NVRAM bootstrap fix was physically demonstrated in temporary v044/v045 only.
- USB gadget `ttyGS0` normal OS userland login has not been physically tested; host COM number can change. No Wi-Fi RF scan/association/DHCP, Bluetooth coexistence or normal-installed-OS restart verification.
- Any *actual persistent write to specifically named partitions* still requires explicit separate user authorization under AGENTS.md. This package does not contain commands that mutate target storage.

**Next physical stage:** inspect/reconcile replacement Xoom's exact GPT and factory ATAG identity without exposing MAC; protect original Android backup; then obtain explicit partition-target authorization before installing the validated artifacts. Keep upstream [xoom-linux/linux](https://github.com/xoom-linux/linux) informed only after a working, repeatable normal OS boots and per-unit MAC identity is proven.
