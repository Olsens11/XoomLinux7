# Motorola Xoom MZ604 Wingray: untouched-upstream kernel and network-ready baseline

**2026-10-29, source/off-device only. No MZ604 fastboot device currently detected, no tablet boot, no flash, no eMMC/SD writes, no radio tests.**

## Selection and source identity
- Motorola Xoom **MZ604 Wi-Fi-only** `motorola,wingray`. Avoid introducing Stingray variant DTS, modem USB or BigPart to the first RFC.
- Linux 7 source worktree: `/home/xoomdev/xoom-linux-rom/rfc-bcm4329-upstream-first-20261029`, commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Read-only `git status --porcelain` empty. **Zero Linux patches**.
- ARM GNU cross toolchain 14.3, config cloned from isolated original upstream Wingray reference into new out-of-tree build dir `/home/xoomdev/xoom-linux-rom/rfc-wingray-baseline-build-20261029`. Config SHA256 `3e9790c493593096eec91cc875144958fe85e41c9b3b87c473fbc33bb93523e0`; `CONFIG_ARCH_TEGRA=y`, `CONFIG_CFG80211=y`, `CONFIG_BRCMFMAC=m`, `CONFIG_BRCMFMAC_SDIO=y`, `CONFIG_USB_G_SERIAL=y`, `CONFIG_ARM_APPENDED_DTB=y`, ATAG compat enabled and NEON disabled.
- Unchanged upstream `make ... -j8 dtbs` **PASS**; original `tegra20-motorola-wingray.dtb` SHA256 `c833f45e529dedaa70ff5f79e61f639236748c1be608020206039e1c834b6eef`. DTB matches prior independent untouched-upstream reference.
- Unchanged upstream `make ... -j8 zImage` **PASS**; `zImage` SHA256 `019c16c266f43254d9b9c4642ff2d7ed951fce97d933e1ede2bac10622eb109b`.
- Unchanged upstream `make ... -j8 modules` and `modules_install` into independent off-device tree **PASS**. `brcmfmac.ko` SHA256 `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`; matching `brcmutil.ko` compiled; kernel release `7.0.0-next-20260422+`; staged modules `/home/xoomdev/xoom-linux-rom/rfc-wingray-module-tree-20261029/lib/modules/7.0.0-next-20260422+`.
- Verified an **offline-only, legacy Android-header RAM-only diagnostic image** at `/home/xoomdev/xoom-linux-rom/rfc-wingray-baseline-bootprep-20261029/MZ604-WINGRAY-UPSTREAM-RAMONLY-UNTESTED.img`; bytes **5,892,096**, SHA256 `9be975cbe4ed6ee8ee3b362775b6d36159ea10b87ebf22cb07d2662eb5c9877c`. Contains appended *unchanged Wingray* DTB plus previously prepared MZ604 freestanding PID1. Header, checksums, DTB and RAM-only cpio format validated. **Not physically booted** and **not a usable network/STA test system** because it intentionally lacks full networking userspace/firmware.

## Owner's required functional baseline: include ordinary networking utilities from the start
Do not wait for `wlan0` to work before obtaining `iw`, `ping`, a DHCP client or a supplicant. Provision a clean independent Debian Bookworm armhf root filesystem, **not a copy of the old MZ600 installed filesystem**:
- Native Linux networking stack: `NetworkManager`/`nmcli`, `wpa_supplicant`, `iw`, `iproute2`, `iputils-ping`, `isc-dhcp-client`, `dnsutils` (`dig`), `curl`/`wget`, CA certs.
- Baseline diagnostics: `kmod` (`modprobe`, `lsmod`), `rfkill`, `ethtool`, `tcpdump`, `usbutils`, `openssh-client/server`, plus SSH/network time and local shell tools.
- Install **matching Linux7 modules** from the new exact upstream build. Do not reuse MZ600-compiled modules merely because `uname -r` matches.
- The actual MZ604 BCM4329 firmware + board-calibrated NVRAM + factory MAC provenance remain **unknown** until source/physical confirmation; do not commit vendor binaries, force a fabricated MAC, or silently substitute the MZ600's firmware.
- Preserve standard `cfg80211`, wpa and NM interfaces; no custom Wi-Fi-management daemon or special userspace shim.
- Do not enable automatic scan/association until regulatory, firmware and target-identity gates. Nothing authorizes unverified 5 GHz TX. Keep new image free of saved Wi-Fi passwords, SSH identities and private device values.
- The full Debian root belongs on a separately provisioned, removable microSD (or another later owner-approved non-destructive medium), **not in the ~8 MiB legacy boot image**. Distinguish the RAM-only boot smoke test from a functional, module-equipped Debian + Wi-Fi root test.
- Debian target prep dir `/home/xoomdev/xoom-linux-rom/rfc-wingray-debian-verified-20261029`. New signed-release Debian Bookworm armhf base was downloaded using the Debian archive keyring with a validated release signature. **OFFLINE PASS 2026-10-29:** Debian Bookworm armhf second-stage bootstrap finished using signed APT metadata; `dpkg --audit` returned clean. Installed and executed `iw` 5.19, `nmcli` 1.42.4, `ping` iputils 20221126 and `ip` 6.1.0 under ARM emulation; `wpa_supplicant` 2.10, DHCP, `dig`, CA/TLS, SSH, `tcpdump`, `rfkill`, `ethtool` and supporting packages are installed. The exact newly compiled modules were copied to `/usr/lib/modules/7.0.0-next-20260422+`, with `depmod` complete; `brcmfmac` reports matching `vermagic` and dependency on `brcmutil`. NetworkManager, supplicant service and SSH server are **disabled by default** pending device/regulatory validation; no saved SSIDs or credentials. Login passwords are unset/locked and must be established privately before interactive use, without publishing secrets.

## Physical gate (not yet performed)
1. Positively identify an **MZ604** and confirm its fastboot bootloader/unlock policy, recovery and battery before any boot command. No currently detected ADB/fastboot device on host. Historical Surface COM9 **is not** an MZ604 identity.
2. Verify the exact image SHA and use *temporary* `fastboot boot` only where supported, after explicit device-scoped approval. Never `fastboot flash` or change existing partitions.
3. Record kernel console / display, MMC enumeration, power/regulators and SDIO with the minimal diagnostic first.
4. Independently provision and validate removable full Debian root before booting the matching network-ready root path. Confirm ordinary tools and exact modules on target.
5. Only after verified supported firmware and regulatory constraints, examine `wlan0`, band/channel flags, fresh 2.4 GHz scans, WPA2 connection, DHCP, DNS and ping. Record actual failures before coding.

**Status:** upstream source/build/kernel module/static image preparation PASS. Fresh Debian userland package/media preparation, physical MZ604 boot and entire wireless feature baseline OPEN. Historical MZ600 experiments are prior art, not a Wingray hardware PASS. No owner DCO or public upstream submission.

## Offline functional media images — COMPLETE, not physically tested

A completely separate 2 GiB **file-backed** removable SD image was created and verified. **No real SD card, MMC storage, boot partition or Xoom was written.** Firmware/NVRAM from a real MZ604 remains absent and must be obtained/validated privately before radio tests.

| Artifact | Local desktop WSL file | Bytes | SHA-256 |
|---|---|---:|---|
| SD disk image (MBR + ext4 root) | `/home/xoomdev/xoom-linux-rom/rfc-wingray-debian-sdimage-20261029/MZ604-WINGRAY-DEBIAN-ARMHF-SDROOT-UNTESTED.img` | 2,147,483,648 | `e5fdd55fbab79f82fc98cd243d7f730446c8dbbfb68e7294adaab5c835d705e4` |
| ext4 partition-only reference | `/home/xoomdev/xoom-linux-rom/rfc-wingray-debian-sdimage-20261029/MZ604-WINGRAY-DEBIAN-EXT4-ROOT-UNTESTED.img` | 2,146,435,072 | `8c3daf6b39ea8df166b243568336254d7d60c0819ee895ccaa68afd4cbaec4ed` |
| Linux 7 temporary **SD-root** fastboot boot image | `/home/xoomdev/xoom-linux-rom/rfc-wingray-debian-sdimage-20261029/MZ604-WINGRAY-UPSTREAM-SDROOT-TEMPBOOT-UNTESTED.img` | 5,888,000 | `07836e502f309569b980a117b914d578f3b1afc476fd9c886214f75c59e49be9` |

- Disk label MBR `0x604a1029`, Linux partition #1 starts at sector 2048 (1 MiB), `PARTUUID=604a1029-01`. Filesystem label `XOOM604ROOT`; ext4 first-boot root. The temporary image cmdline includes `root=PARTUUID=604a1029-01 rootwait rootfstype=ext4 ro init=/sbin/init`. **This is not yet validated against the actual MZ604 bootloader/kernel MMC enumeration.**
- `e2fsck -fn` **PASS**: 13,741/131,072 inodes and 116,979/524,032 blocks; Python verification checked partition table, ext4 signature, exact partition content equality against standalone ext4 image, Android boot header, the embedded unchanged upstream Wingray kernel+DTB and absence of a ramdisk.
- The rootfs was not derived from the MZ600 filesystem, contains no saved network connections or bundled OEM radio firmware, and has disabled network daemons pending qualification. SSH host keys and machine-ID were cleared from the template; generate fresh per-device keys on deploy.
- The ~5.9 MiB **RAM-only diagnostic** remains a separate prior artifact for kernel-only smoke testing; it is **not** the primary Wi-Fi-capable baseline. The full Debian SD-root image is the functional baseline requested by the owner.
- The owner must **identify an actual MZ604**, verify unlocked/temporary boot capability and stock recovery, set local account credentials without exposing them publicly, and separately authorize actual removable-media writing and temporary boot. Physical boot, firmware, `wlan0`, scanning, WPA and DHCP remain OPEN.
