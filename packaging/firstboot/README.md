# XoomLinux7 first-boot connectivity and console kit — 2026-10-28

**Internal OS/deployment track only. NOT a kernel upstream patch series.**
**OFF-DEVICE TEST IMAGE AND SIGNED OFFLINE PACKAGE INSTALL PASS. Physical boot/flash OPEN.**
Do not modify the working MZ600 p7 boot, p8 Debian root, attached tablet
or the Debian reference root while building this package.

## Why this design

The existing V31 MZ600 physically used `wpa_supplicant@wlan0` +
`systemd-networkd` DHCP + `systemd-timesyncd` to reach WPA2, DNS,
NTP and HTTPS, but the first successful association was ~399 seconds
after boot. DHCP took ~0.12 seconds *after* association. A different
userspace manager does **not** fix the unresolved Broadcom auth/firmware
event delay; this is a usability and provisioning milestone, not a
claimed wireless-driver correction.

The official Debian Bookworm **armhf** `network-manager` package includes
`nmtui` (text menu), `nmcli` (scriptable) and DHCP support. This
prototype selects **NetworkManager as the single manager** for wlan0
in a newly built test root image. `nmtui connect` prompts to select
a discovered SSID and enter a passphrase; `xoom-wifi` is our small
wrapper. Existing factory identity and regulatory configuration stay
under kernel/firmware control. The private router SSID/PSK are entered
on-device and must not go in a Git commit or generic image.

**Never run both the existing `wpa_supplicant@wlan0` +
`systemd-networkd` ownership path and NetworkManager against wlan0.**
The new test image must disable those legacy per-interface services,
while leaving the generic D-Bus `wpa_supplicant` service available for
NetworkManager. A recovery/test image should always retain COM9 access
to revert if NetworkManager cannot associate.

## Off-device staged artifacts (DESKTOP-R16QJD4 Ubuntu WSL)

Relative to local private workspace
`/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`:

| Folder | Contents | Status |
| --- | --- | --- |
| `firstboot-network-packages-v2-20261028/` | Final **41** signed Debian Bookworm armhf dependency-closed .debs including `systemd-timesyncd`, ~9.5MB, hashes and APT logs | Signature/index/hash verification PASS; ARMhf packages **installed/configured only in disposable test root** |
| `firstboot-root-overlay-20261028/` | `xoom-wifi`, `xoom-net-check`, `xoom-console-check`, sshd restrictions, tty1 getty and NetworkManager configuration | Installed **in the new private test root only**; no files touched on the MZ600 |
| `firstboot-host-tools-20261028/` | Self-contained Windows PowerShell USB COM9 console bridge, portable .cmd launcher, SHA256SUMS | Staged; requires host PowerShell parsing/physical COM9 test |
| `firstboot-private-mz600-firmware-20261028/` | MZ600-only `brcmfmac4329-sdio.bin` and board-specific NVRAM `.txt` with SHA256SUMS | Staged PRIVATE and installed only into disposable test root; **never** commit or redistribute |

The historic root `os-build/bookworm-armhf-root` was read and **cloned**
into `test-debian-root-20261028/` (private workspace) before offline
installation. The source reference and installed tablet remain unchanged.
The private 2GiB ext4 file `XoomLinux7-test-root-bookworm-armhf-20261028.img`
was produced using `mkfs.ext4 -d`, passed offline `e2fsck -fn`, and has
SHA256 `b7180b88dfacf29b41bdb515d4d1a5226855fb2065ca8423ea69029a1362a70d`.
**This is an external/test-root file and must NOT be flashed to the
existing 1GiB BigPart p8.** The generic 41-package offline transport
bundle is `XoomLinux7-FirstBoot-Online-Console-v2-20261028.tar.gz`,
SHA256 `224a72c2b09cf3eb9eb073f8df8d68a50a1994459d1317c44e33fa3b15cfbfb2`.
No private BCM4329 firmware or root password is in that public-content
bundle; the assembled test-root image is **PRIVATE**.

## Reproducible build procedure (completed on disposable copy; not on device)

1. Use a **new, isolated copy** of the Debian Bookworm ARMhf rootfs,
   never the existing mounted internal p8, original reference root or
   a live device mount. A provisioning operator with host root access
   must verify the destination and add a marker file at its root:
   `.xoom-disposable-test-rootfs`.
2. Apply the generated overlay to that copy (preserving permissions).
   Install only the SHA-verified official `.deb` files **in the
   disposable ARMhf root**, with dependencies configured through a
   working ARM chroot/qemu or an equivalent offline image build.
   `fetch-bookworm-armhf-debs.sh` downloads packages only, and does
   not claim to install them. The target must actually contain
   `/usr/bin/nmtui`, `/usr/bin/nmcli`, `/usr/bin/ping`, and
   `/usr/bin/curl` before this gate is PASS.
3. Keep private board-appropriate BCM4329 firmware at
   `/lib/firmware/brcm/brcmfmac4329-sdio.{bin,txt}`. Do not put these
   files into the upstream source patch tree or any public tarball.
   Match signed regulatory database with the kernel regulatory
   implementation; do not hard-code a country code.
4. For **this disposable test root only**, run
   `set-test-root-password.sh DISPOSABLE_ROOT` as privileged operator,
   entering the temporary local root password selected by the owner. No weak password
   is prewritten into the Git repo. The overlay disables
   `PermitRootLogin` and `PasswordAuthentication` in sshd.
   This password is unsuitable for any network-exposed stable build.
5. In that same *offline disposable root* only, enable
   `getty@tty1.service`, `serial-getty@ttyGS0.service`,
   `NetworkManager.service` and `systemd-timesyncd.service`
   with `systemctl --root=DISPOSABLE_ROOT enable ...` after .deb
   installation. Disable `systemd-networkd.service` and
   `wpa_supplicant@wlan0.service` with
   `systemctl --root=DISPOSABLE_ROOT disable ...`. Avoid manipulating
   the live MZ600/host systemd instance.
6. Build only a **RAM-only, hash-verified, reversible** boot artifact
   from the exact nine-review kernel plus matched modules and this
   TEST rootfs. Preserve the required `gpt xoom_bigpart=1` bootargs
   for any internal-p8-based boot. First validation must use a safe
   temporary/non-p8 root and check the 10-partition geometry without
   write accesses. No permanent flash until explicitly approved.

## User workflow (when physically proven)

- At the tablet's `tty1` framebuffer login, or at the Surface
  COM9 shell (`ttyGS0`), log in with local root credentials.
- Run **`xoom-wifi`** to open `nmtui connect`. Pick SSID and type WPA
  password; NetworkManager saves it locally for auto-reconnect and
  handles DHCP and routes.
- Run `xoom-wifi status` or `xoom-net-check` for link/IP/route/DNS
  and optional ICMP reachability. `ping` is installed by the offline
  package kit (the prior installation did not include it).
- For lower-level diagnostics keep `iw`, `wpa_cli`, `ip`,
  `journalctl -u NetworkManager`, and `rfkill`.

## COM9 and on-device display

The matching kernel already has `CONFIG_USB_G_SERIAL=y`, USB gadget
ACM support, `CONFIG_VT=y`, `CONFIG_FRAMEBUFFER_CONSOLE=y`, Tegra DRM,
LVDS panel and input drivers. The existing Debian root already enables
`getty@tty1` and `serial-getty@ttyGS0`. The host COM9 helper is in
`scripts/host/windows/Start-Xoom-USB-Console.ps1` with
`Xoom-USB-Console.cmd`; default COM9, 115200 baud, arrow/Enter/Backspace,
Ctrl+] disconnect, optional `-Probe`. The local Surface launcher remains
untouched. Only one host process may own COM9 at once.

**Live hardware observation PASS:** `/dev/fb0` exists as `tegradrmfb`,
DRM LVDS-1 is `connected`, `getty@tty1` and `serial-getty@ttyGS0` both
report `active`, and Atmel maXTouch reports `/dev/input/event2` on the
**running installed MZ600**. Human-visible pixels on the **new image**
remain OPEN; a `tty1` service does not guarantee input and touch events
are not a physical keyboard. The first milestone targets a
*visible* terminal; tablet-only touchscreen typing requires a later
on-screen-keyboard/terminal UI and separate input driver qualification.
Run `xoom-console-check` over COM9 to gather safe screen diagnostics.

Do not confuse `ttyGS0` USB gadget serial with the physical USB-C cable
or a separate Windows kernel driver. The existing proven COM9 virtual
serial port requires no new upstream kernel patch. NetworkManager also
does not solve driver-side ~399s authentication delays.

## Review/acceptance and preservation

- Requested temporary local root password in a private **disposable**
  test root: **SET AND VERIFIED**; never applied to original root.
- Offline Debian package downloads and SHA256: **PASS**.
- Rootfs overlay **installed in disposable copy**; host COM9 helper source
  parsed successfully, new helper's physical interaction still OPEN.
- MZ600 private BCM4329 firmware staging: **PASS**, do not distribute.
- NetworkManager/nmtui packages installed and ARMhf execution sanity tests
  PASS; NetworkManager enabled, competing services disabled in disposable
  root only. Physical WPA2/DHCP connection testing OPEN.
- Live framebuffer, LVDS and both gettys confirmed. New-image visible
  terminal, touchscreen typing and new COM9 launcher physical test OPEN.
- Matched 114-module nine-review kernel installation, private firmware and
  2GiB root ext4 file fsck PASS offline. Exact kernel BigPart and Wi-Fi
  physical boot OPEN. Existing p7/p8 stay untouched. [Preflash backup](../../docs/checkpoints/MZ600_V31_PREFLASH_PRESERVATION_AND_TEST_ROOT_2026-10-28.md)
  records verified live raw images and the still-required cold p8 snapshot.

**Milestone closure:** Update the OS integration manifest, checkpoint,
versioned package list, project indices and test evidence as each new
package/tool/display gate passes. No firmware, credentials, SSIDs,
NVRAM or private licenses are allowed in the public GitHub tree.
