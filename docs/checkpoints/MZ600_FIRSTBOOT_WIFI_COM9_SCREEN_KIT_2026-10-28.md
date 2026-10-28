# MZ600 first-boot networking, COM9 and tablet-console kit — 2026-10-28

**Project track: deployment / OS / private firmware, NOT an upstream kernel patch.**
**OFFLINE BUNDLE PASS; INSTALLATION AND DEVICE RUN OPEN.** All actions
performed on desktop offline build workspaces. No rootfs p8 modification,
no test device reboot, USB COM9 interaction, firmware flash or source
kernel patch change.

## Why this milestone

The existing Stage-D MZ600 Debian system and V31 brcmfmac physically
established WPA2, DHCP, DNS, timesync and verified HTTPS on reboot,
using `wpa_supplicant@wlan0`, `systemd-networkd` and
`systemd-timesyncd`; physical association took approximately **399 s**
due unsolved driver/legacy event behavior while DHCP was only ~0.12 s.
The user requests a complete *offline* first-boot path with
user-friendly Wi-Fi selection, ping/curl, a persistent USB COM9
console and a local tablet-screen terminal.

## Verified discoveries

- Kernel config from the *nine-review build* already enables
  `CONFIG_USB_G_SERIAL=y`, USB ACM functions, `CONFIG_VT=y`,
  `CONFIG_VT_CONSOLE=y`, `CONFIG_FRAMEBUFFER_CONSOLE=y`,
  `CONFIG_DRM_TEGRA=y`, LVDS/panel, input/touchscreen drivers.
- Debian root reference already has `getty@tty1` and
  `serial-getty@ttyGS0` enabled. It currently lacks NetworkManager,
  ping, curl and an actual touchscreen keyboard, although its older
  package state includes `iw`, WPA and networkd.
- The Surface already has a successful older COM9/115200 PowerShell
  bridge `Start-Xoom-USB-Console.ps1` documented separately. A
  portable, **no-password/no-regdb-command**, argument-selectable COM
  port variant is now versioned in project
  `scripts/host/windows/`. It passes PowerShell source parsing and
  is staged beside its .cmd launcher; it has not physically opened COM9.
- Official Debian Bookworm **armhf NetworkManager 1.42.4-1+deb12u1**
  archive was extracted in a read-only inspection directory to confirm
  real `/usr/bin/nmtui`, `/usr/bin/nmcli`, and
  `/usr/sbin/NetworkManager` binaries.
- Offline APT used only a *read-only* copy of the Debian root's dpkg
  status and signed Debian repository key, with isolated Debian sources,
  indices, archive directory and apt options. Dependency closure and
  download **PASS: 40 .deb files, 9,428,076 bytes**, all armhf/all,
  with all 40 SHA-256 checks PASS.
  Exact archive manifest SHA256:
  `b76e2f16656d05765c9cf39c7a4b84737f33f4bc257beaee89460cd450bdc0c3`.
- Local generated rootfs overlay, three test tools
  (`xoom-wifi`, `xoom-net-check`, `xoom-console-check`),
  SSH hardening and tty1 display getty drop-in are present and
  syntax-checked. No overlay files installed into Debian yet.
- A *separate PRIVATE* MZ600-only copy of
  `brcmfmac4329-sdio.{bin,txt}` with checksum manifest is staged on
  the desktop; **not committed** to Git and **not included** in the
  non-secret networking bundle. Other Xooms need firmware/NVRAM
  provenance and model-specific board calibration re-verified.
- Portable public-content offline archive (no firmware/password):
  `XoomLinux7-FirstBoot-Online-Console-20261028.tar.gz`,
  **9,428,586 bytes**, SHA256
  `33fd09b232a93c53f630e0af4b22a817f42e1a2627fe72df4a607189f141d544`,
  stored outside GitHub under desktop private workspace
  `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`.
  It contains official Debian .debs, source overlay and Windows COM9
  helper, but **no private Broadcom firmware or credentials**.

## Intent for disposable test root

Choose NetworkManager as a **single owner of wlan0** with WPA2
supplicant D-Bus integration, DHCP, DNS, saved credentials and
`nmtui connect` terminal interface. In that *new image only* disable
legacy `systemd-networkd.service` and
`wpa_supplicant@wlan0.service` service ownership before enabling
`NetworkManager.service`. Keep `systemd-timesyncd`,
`serial-getty@ttyGS0` and `getty@tty1`.

User-provided **temporary weak root password** is acceptable only in
an isolated test root, **not** the current installed Debian and not
in Git. `set-test-root-password.sh` refuses unmarked roots and
receives the password only through a non-echoed interactive prompt.
The generated sshd drop-in disables root login and password SSH;
local console login remains possible. The desktop WSL build account
currently requires interactive sudo credentials; a fresh rootfs copy
and offline armhf package configuration therefore remain
**not performed**. Do not claim the owner-selected password was
already provisioned.

The kernel supports framebuffer console on paper; **the display
binding/actual physical tty1 pixels remain unverified**. A touchscreen
alone cannot type shell commands without an onscreen keyboard/input
bridge. Initial hardware testing may use a physical USB/Bluetooth
keyboard or the already proven Surface COM9 console; touch typing is
a separate OS/UI milestone. Ensure the test kernel's on-screen
console configuration preserves independent `ttyGS0` rescue access.

## Acceptance gates

| Test | Current result |
| --- | --- |
| Official Bookworm ARMhf NetworkManager/nmtui and dependencies downloaded offline | **PASS** |
| Package integrity, architecture and checksums | **PASS** |
| Rootfs overlay script and shell source syntax | **PASS** |
| New Windows USB COM9 launcher syntax | **PASS** |
| Host-side bundle assembly and public-content SHA256 | **PASS** |
| Private MZ600 BCM4329 files staged separately | **PASS**, not for redistribution |
| New isolated Debian rootfs copied, packages installed, root passwd provisioned | **OPEN** |
| NetworkManager exclusive ownership and nmtui on MZ600 | **OPEN** |
| Physical DRM framebuffer + visible tty1 console | **OPEN** |
| Touchscreen input keyboard and any GUI terminal | **OPEN** |
| Correct MZ600 nine-review kernel/module/BigPart boot and prompt WPA2/DHCP | **OPEN** |
| Existing installed system and upstream patch series untouched | **PASS** |

## Next gated implementation

With owner-approved privileged build access, assemble a **separate
disposable image** from verified Debian root state, install the
downloaded ARMhf packages and overlay, privately provision the chosen
local root password, and confirm exclusive NetworkManager/legacy
service enablement using `systemctl --root`. Hash the resulting
image and verify sshd policy. In a controlled **RAM-only boot**
with the correct `gpt xoom_bigpart=1` if internal p8 is considered,
verify the framebuffer and tty1, COM9, kernel matched modules,
firmware readiness, then `nmtui`, DHCP/DNS and ping/HTTPS.
Do not risk persistent p7/p8 or misattribute V31's ~399s association
delay to the user-friendly network manager.

Source: [first-boot kit](../../packaging/firstboot/README.md);
integration evidence: [Stage-D vs nine-review comparison](MZ600_STAGE_D_INSTALLED_VS_NINE_PATCH_REVIEW_2026-10-28.md) and [read-only storage test plan](../plans/MZ600_STORAGE_BIGPART_REVIEW_SOURCE_RAM_TEST_PLAN_2026-10-28.md).
