# XoomLinux7 first-boot connectivity and console kit — 2026-10-28

**Internal OS/deployment track only. NOT a kernel upstream patch series.**
**Offline staging PASS, image installation/physical test OPEN.**
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
| `firstboot-network-packages-20261028/` | Official signed Debian Bookworm armhf repository index and 40 dependency-closed .deb files (~9.1MiB packages), `SHA256SUMS`, package/version/architecture inventory, APT simulation and download logs | Download and SHA verification PASS; **NOT installed** |
| `firstboot-root-overlay-20261028/` | `xoom-wifi` frontend, `xoom-net-check`, `xoom-console-check`, sshd drop-in disabling root and password SSH logins, tty1 display keepalive settings, NetworkManager configuration | File generation PASS; **not installed** |
| `firstboot-host-tools-20261028/` | Self-contained Windows PowerShell USB COM9 console bridge, portable .cmd launcher, SHA256SUMS | Staged; requires host PowerShell parsing/physical COM9 test |
| `firstboot-private-mz600-firmware-20261028/` | MZ600-only `brcmfmac4329-sdio.bin` and board-specific NVRAM `.txt` with SHA256SUMS | Staged PRIVATE; **never** commit or redistribute; other Xoom devices may require different calibration |

The only existing source copy used is the *historical* reference root
`/home/xoomdev/xoom-linux-rom/os-build/bookworm-armhf-root`; its
`/var/lib/dpkg/status` was read to resolve dependencies, and its
signed Debian archive keyring was used for APT verification.
The reference root and installed tablet were not changed.

## Build and rootfs application (future disposable root, not executed)

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

**Hardware gates still OPEN:** DRM panel and `/dev/fb0` must be physically
observed; a `tty1` console service does not guarantee screen pixels;
touch events are not a physical keyboard. The first milestone targets a
*visible* terminal; tablet-only touchscreen typing requires a later
on-screen-keyboard/terminal UI and separate input driver qualification.
Run `xoom-console-check` over COM9 to gather safe screen diagnostics.

Do not confuse `ttyGS0` USB gadget serial with the physical USB-C cable
or a separate Windows kernel driver. The existing proven COM9 virtual
serial port requires no new upstream kernel patch. NetworkManager also
does not solve driver-side ~399s authentication delays.

## Review/acceptance and preservation

- Root password on an actually assembled test root: **OPEN**;
  provisioner ready but cannot run against original root.
- Offline Debian package downloads and SHA256: **PASS**.
- Rootfs overlay and host helper staged: **PASS** (not installed/tested).
- MZ600 private BCM4329 firmware staging: **PASS**, do not distribute.
- NetworkManager/nmtui package installation and service ownership: **OPEN**.
- On-screen framebuffer terminal, touch typing, and COM9 physical test of
  new helper: **OPEN**.
- Exact nine-review source, firmware, module ABI and BigPart boot:
  retain existing guarded qualification process; no device changes.

**Milestone closure:** Update the OS integration manifest, checkpoint,
versioned package list, project indices and test evidence as each new
package/tool/display gate passes. No firmware, credentials, SSIDs,
NVRAM or private licenses are allowed in the public GitHub tree.
