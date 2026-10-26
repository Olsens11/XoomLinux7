# MZ600 v06.4 — official Debian D-Bus six-package offline install, system bus PHYSICAL PASS

**Date:** 2026-10-26. **Device:** experimental replacement Motorola MZ600, persistent Debian 12.15 armhf on internal `/dev/mmcblk0p8 ext4`, Linux `7.0.0-next-20260422+`, USB COM9 root console. **Outcome:** six signed-index-metadata-matched Debian Bookworm packages installed offline; system D-Bus socket and daemon live; actual `dbus-send` system-bus RPC completed. **Not a Linux kernel or BCM4329 whole-chip patch.** No Wi-Fi/BT restart, load, scan, association, boot flash, reboot or partition reformatting.

## Root cause and package resolution

After the separate [114 ABI modules physical install PASS](MZ600_V064_114_ABI_MODULES_INTERNAL_P8_ATOMIC_INSTALL_PHYSICAL_PASS_2026-10-26.md), read-only inspection found PID1 systemd running yet no `/run/dbus`, `dbus-daemon` executable, nor `dbus-broker`; `dbus` and its executable/configuration dependencies were not installed. The prior `wpa_supplicant.service` failed because the system bus socket did not exist. `libdbus-1-3` was installed but was not a daemon.

A **live on-device** `apt-get -s -qq --no-install-recommends install dbus` specified exactly **six** missing packages:
`dbus`, `dbus-bin`, `dbus-daemon`, `dbus-session-bus-common`, `dbus-system-bus-common`, `libexpat1`; no additional dependencies. The live `apt-cache show` metadata provided the exact official Debian Bookworm apt filenames, versions, sizes and SHA256. Surface downloaded via `https://deb.debian.org/debian/` and checked **each package SHA and byte count** against the device's apt-cache metadata before creating a six-regular-file basename-only gzip tar.

| Bookworm package | Architecture | Installed version | On-device APT metadata SHA256 |
| --- | --- | --- | --- |
| dbus | armhf | 1.14.10-1~deb12u1 | `319e1802a831f3f3921a1751afe948173bf4d04c402356e2560828649e262b58` |
| dbus-bin | armhf | 1.14.10-1~deb12u1 | `d2dd421c4c18ea67a7c4184bf31f73fd16a580048ed4b7b483eeb5886c79e8d3` |
| dbus-daemon | armhf | 1.14.10-1~deb12u1 | `8238913c664752e69b4c0f2fdb0a4208808ad02fcaa90661ab80bd1f4440fd96` |
| dbus-session-bus-common | all | 1.14.10-1~deb12u1 | `b19cb8e3581d6b09ff3f46fee23de2813811353228c666c9d1ad885598062e43` |
| dbus-system-bus-common | all | 1.14.10-1~deb12u1 | `2111d3d0c98ac68ee973274058447e6fab1c359fec1d4bb195f5fcc5833a19e2` |
| libexpat1 | armhf | 2.5.0-1+deb12u2 | `e1cbf8b00e34295cd92865747abf80999218b6511ddc68daffd6b0e5f9fe0d63` |

**Bundle:** Surface-only `captures/dbus-bookworm-offline-20261026/MZ600-Bookworm-DBus6-APT-MATCHED-OFFLINE-ONLY-20261026.tar.gz`, **606,850 bytes**, SHA256 **`5b59275308ffe4993783bb8f4e566e290e34246d03da3ba1af8255aabb252e4e`**. Exact six package paths, six regular tar members, no links. Surface private manifest tracks package SHA and physical transfer.

## Physical transfer and guarded on-device installation

- Authenticated COM9 root shell UID0 and exact p8/kABI preflights passed.
- Host sent 791 base64 lines to `/run/mz600-bookworm-dbus6-matched-offline-20261026.tar.gz` **RAM-only**. Xoom performed its **own** SHA-256 of the decoded archive and returned `SUCCESS_ON_XOOM_RAM_ARCHIVE_SHA_PASS_NO_DBUS_PACKAGES_INSTALLED`; host uploader exit0.
- A separate on-device readback reconfirmed 606,850-byte archive SHA, Debian 12.15, armhf, clean `dpkg --audit`.
- Canonical reviewed script `scripts/host/xoom/install-bookworm-dbus6-offline-once-20261026.sh`, `bash -n` PASS on Desktop WSL; source SHA256 `ddf35533bfc5989f7aa4f3e7395b7921eff2b017e6643c45ca72c51b2886af6d`. SHA-pinned owner-console one-shot heredoc wrapper SHA256 `c820beb79e2c41bca49e74260ba8bceef282f3dc0821bcb842ba2b08beed81f7`; Bash inner SHA matched canonical. One guarded serial sender delivered all 83 framed lines to the Xoom after live root/ABI/architecture proof.
- Actual privileged shell validated: archive SHA again, six exact allowed member paths, no other staging path, all six **inner per-deb SHA**, `dbus-daemon` metadata, and clean dpkg baseline. Installed offline using `DEBIAN_FRONTEND=noninteractive dpkg -i` (all six); after `dpkg --audit` clean and six packages individually `Status: install ok installed`, printed:

```text
MZ600_DBUS6_RAMPKG_AND_DEPENDENCY_PREFLIGHT_PASS
MZ600_DBUS6_SIX_PACKAGES_INDIVIDUAL_SHA_PASS
MZ600_DBUS6_OFFLINE_DPKG_6_OF_6_PHYSICAL_PASS
MZ600_DBUS6_PACKAGE_INSTALL_COMPLETE_NO_WIFI_RESTART
DBUS6_INSTALL_RESULT=PHYSICAL_PASS
```

- During the `dbus-daemon` package's earlier setup order, a `systemd-tmpfiles` snippet briefly reported missing `messagebus` user; following completion of all packages, **on-device `getent passwd messagebus` and `getent group messagebus` BOTH succeeded**. Therefore this warning was transient in the package order, not an unresolved missing account. Do not add a second ad-hoc account manually.
- `dbus.service` is static/inactive immediately after package install and Debian correctly said it was not automatically starting the service.

## Actual functional D-Bus activation PASS

The operator physically ran only the standard userspace setup:
`systemd-tmpfiles --create /usr/lib/tmpfiles.d/dbus.conf`; `systemctl start dbus.socket`; verified `test -S /run/dbus/system_bus_socket` and printed `__DBUS_SOCKET_ACTIVATED_PASS__`.

A separate on-Xoom `dbus-send --system --print-reply --type=method_call --dest=org.freedesktop.DBus / org.freedesktop.DBus.ListNames` returned a valid method-reply with `org.freedesktop.DBus` and its client ID. Independent follow-up read-only audit:

```text
systemctl is-active dbus.socket dbus.service mz600-wlan.service wpa_supplicant.service
active
active
failed
failed
ls -l /run/dbus/system_bus_socket
srw-rw-rw- 1 root root ... /run/dbus/system_bus_socket
dpkg --audit
[no output]
ls /sys/class/net
ip6tnl0 lo sit0
cat /proc/modules | grep brcm
[no output]
```

Therefore **D-Bus userland, socket and daemon ACTUALLY RUNNING** are now physical PASS. **WLAN and WPA have NOT been restarted** and retain historical failed flags from before module installation/D-Bus repair. The absence of `wlan0` and loaded brcm modules is intentional.

## Kernel whole-chip patch-series relevance and next steps

This repair was a **Debian packaging/runtime** change only. It does NOT modify `src/chip/stingray-bcm4329-pwrseq.c`, Motorola U4/I7/U0/U2 GPIO ownership, MMC2 SDIO clock/regulator integration, LPO, WCC, or Linux kernel RFC patch `0001`. Record it in [whole-chip integration ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md) as *userspace solved; no kernel patch*. All future hardware findings must feed back to the [multi-device whole-chip series gates](../plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md); upstream submission remains explicitly unauthorized.

Next controlled stage: inspect `/usr/local/libexec/xoom-check-factory-wlan-mac` and service dependency semantics read-only; prepare bounded WLAN driver start **with ordered WCC->brcmfmac->brcmutil cleanup, explicit COM9/watchdog/power recovery plan**, respecting factory MAC and signed regulatory limits. User may still be offsite; defer any uncontrolled radio restart, RF scan, regulatory override or reboot. Normal systemd D-Bus is now available for subsequent standard userspace testing.

**PHYSICAL ACCEPTANCE:** OFFICIAL DEBIAN DBUS6 OFFLINE INSTALL 6/6, SYSTEM DBUS SOCKET AND DAEMON ACTIVE, ACTUAL SYSTEM BUS RPC PASS; NO WIFI/BT LIVE TEST THIS STAGE.
