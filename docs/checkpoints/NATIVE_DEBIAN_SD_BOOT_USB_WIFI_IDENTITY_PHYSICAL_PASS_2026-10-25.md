# PHYSICAL PASS: Debian 12 microSD boot, USB serial login and BCM4329 interface

**Date:** 2026-10-25. **Machine:** replacement Motorola Xoom MZ600, Tegra 2. **Boot mode:** temporary `fastboot boot`; Android eMMC boot/system/data/TWRP partitions remain unchanged.

## Executive finding

A photo provided by the user shows **`Debian GNU/Linux 12 xoom-mz600 tty1`** and an active **`xoom-mz600 login:`** prompt. The same boot has now been authenticated via the live USB COM9 serial console, using first-boot owner credentials loaded privately from Desktop WSL (never disclosed or committed). Kernel, independent microSD root, systemd, getty, USB gadget and BCM4329 module integration are **PHYSICALLY VERIFIED**, not merely built offline.

The successful temporary image is `xoom-linux7-SDROOT-nonempty-ramdisk-TEMPBOOT.img`, **6,645,760 bytes**, SHA256 **`c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c`**. It contains the clean Linux7 zImage and appended USB0 peripheral Stingray DTB, plus a valid non-empty gzip CPIO ramdisk retaining proven v034 contents **except /init was renamed to init.v034.disabled**. The root specification is the private, physically validated card-specific `root=PARTUUID=...-01 rootfstype=ext4 rootwait rw init=/sbin/init`. This runs the real Debian filesystem and normal init instead of the v034 diagnostic program.

**Important nuance:** This demonstrates that this variant works, not that the earlier zero-byte ramdisk was definitively the only cause of the earlier failure. Earlier empty-ramdisk boot attempts displayed only the last bootloader screen, with no live USB. The clean-kernel + v034 diagnostic ramdisk did display a kernel console and enumerate the root card, but its deliberately missing root selector caused a VFS panic. The new non-empty/no-init variant demonstrably proceeds to Debian login.

## Live host-side checks

Surface COM9 reports a present, healthy `USB Serial Device` with USB VID/PID **0525:A4A7**, corresponding to our Linux gadget. Sending carriage return to COM9 returned a fresh `xoom-mz600 login:`; generated `xoom` credentials were passed only in-process from a restricted Desktop WSL file over the pre-authorized private host connection. Interactive read-only Debian shell commands succeeded.

### Direct device observations

| Probe | Physical result |
| --- | --- |
| `uname -r` | **7.0.0-next-20260422** |
| `cat /etc/debian_version` | **12.15** |
| `findmnt -n -o SOURCE,FSTYPE,TARGET /` | **`/dev/mmcblk1p1 ext4 /`** |
| `ps -p 1 -o pid,comm,args` | **`1 systemd /sbin/init`** |
| `readlink -f /sbin/init` | `/usr/lib/systemd/systemd` |
| `ls /dev/ttyGS0` | **present**, active USB serial getty |
| `ls /sys/class/net` | `lo, sit0, ip6tnl0, wlan0` |
| `ip -br link` | **wlan0 present, DOWN**; no RF/connection trial |
| `/proc/device-tree/mmc@c8000200/wifi@1/local-mac-address` | **present** |
| Binary compare of DT MAC to `/sys/class/net/wlan0/address` | **DT_INTERFACE_MAC_MATCH** (address never printed/published) |

The last two checks strongly support the intended Motorola bootloader factory-MAC tag → early ATAG-to-FDT converter → upstream brcmfmac NVRAM identity path. The public kernel DTB and generic calibration contain **no static/copy-pasted MAC address**. A cryptographically independent proof of factory-assigned identity has not been claimed; this is an exact match between the live FDT and interface.

**Do not hardcode SD as mmcblk1.** It has appeared under both mmcblk0 and mmcblk1 across different boots. The correct private DOS-MBR PARTUUID reliably selected the ext4 root.

### Loaded modules / firmware (physical)

`lsmod`:
`brcmfmac_wcc 12288 0`; `brcmfmac 237568 1 brcmfmac_wcc`; `brcmutil 12288 1 brcmfmac`.

`dmesg`:
- `brcmf_fw_alloc_request: using brcm/brcmfmac4329-sdio for chip BCM4329/3`
- `brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: Sep 2 2011 14:48:19 version 4.220.48`
- `brcmf_c_process_clm_blob: no clm_blob available (err=-2), device may have limited channels available`
- `brcmf_c_process_txcap_blob: no txcap_blob available (err=-2)`

This confirms upstream modular WCC and a native WLAN0 interface in the **installed operating system**, not merely v045's temporary diagnostic driver. It **does not** qualify RF scan, association, DHCP, country code, transmission limits, stability or coexistence.

### systemd and other nonfatal issues

Photo shows deferred probes related to `sound-hdmi` and `tegra-mc`, plus late regulator messages `ud/ucsi/vrf2/vrfref/usb: disabling`. These were **not fatal**: Debian, systemd, getty, live USB and wlan0 all started. The line `usb: disabling` must not be interpreted as proof the USB controller stopped.

As the unprivileged `xoom` owner, `systemctl is-enabled` and `systemctl is-active mz600-wlan.service` returned `Failed to connect to bus: No such file or directory`. A follow-up read-only probe proves systemd **is** PID1 and `/run/systemd/private` exists, but `/run/dbus` does not. Investigate system D-Bus and user permissions (not a kernel-boot failure). Do not infer that the service itself failed from those unprivileged commands alone.

## Acceptance matrix

- **PASS physical:** full ext4 root from microSD, real Debian 12.15 userspace, systemd PID1, tty1 login, COM9/ttyGS0 working and authenticated shell, upstream WCC + brcmfmac + brcmutil, firmware 4.220.48, wlan0 enumerated, DT/wlan0 MAC byte match.
- **NOT YET TESTED:** Wi-Fi RF/regulatory validation, scan, association, DHCP, internet, endurance, Bluetooth coexistence, general UI/touch behavior under Debian, persistent Linux boot selection, reboot-repeatability.
- **NEEDS REVIEW:** optional CLM/TXCAP blobs and country-channel limitations; normal D-Bus system bus and service management; deferred sound/tegra warnings.

## Next safe work

1. Preserve this successful temporary boot and current logs; record project runtime status and hashes.
2. Investigate normal systemd/D-Bus service state, plus regulatory constraints, using read-only serial commands. Never disclose factory MAC or private password.
3. Before transmitting, qualify legitimate regulatory settings/board calibration rather than add guessed overrides. Then explicitly validate native WLAN scan/association and DHCP.
4. Only after successful repeatability consider a reversible persistent Linux boot choice. Android internal boot/system/userdata and TWRP remain unchanged; any future eMMC write needs its own explicit approval.
5. Prepare minimal xoom-linux upstream contribution when tests are repeatable and production identity is established.

This checkpoint **supersedes previous 'normal Debian boot unconfirmed' assertions** for this boot image, while preserving all experimental evidence and previously archived milestone files.
