# v06.4 (v064) — executable next-conversation build instructions: Wi-Fi scan, real terminal, Bluetooth keyboard

> **NEW storage-path expansion (2026-10-25 evening EDT):** User permits an internal eMMC installation replacing Android on the replacement MZ600, and optional BigPart if needed. The 256MiB factory p8 cannot hold Debian, but existing p10 userdata has ~29.34GiB and is the preferred future normal ext4 root **without repartitioning**. See [new internal root and safety implementation plan](MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md). Earlier no-eMMC/no-SD RAM-only restrictions in this pre-existing plan describe the *proven baseline* and still apply to the current v06.3 image; they do not prohibit the separately gated new user-approved architecture. **Do not execute p10/p7 writes until Linux7 partition mapping, full userdata backup and independent recovery have passed.** v06.4 still must pass standard iw scan, real on-screen terminal and Motorola keyboard typing. No v06.4 image or internal installation exists yet.


**Specification created 2026-10-25. Status: PLAN ONLY; no v06.4 image has been built, transferred or physically booted.** This document is the next-session implementation contract. Work from the physically qualified **v06.3** Linux 7 RAM-boot image and complete handoff; do not replay the old unsuccessful BCM4329 SDIO F2 branch. User explicitly expects functional software now, not yet another firmware-only or diagnostic-display-only version.

## 0. Resume precisely and safely

1. First read [comprehensive handoff](../handoffs/MZ600_LINUX7_BCM4329_COMPREHENSIVE_HANDOFF_2026-10-25.md), [AGENTS.md](../../AGENTS.md), [the v06.3 physical PASS](../checkpoints/MZ600_V063_PHYSICAL_PASS_HCD_HCI_AND_BLUETOOTH_TO_WIFI_2026-10-25.md), [official ARMHF iw staging](../checkpoints/MZ600_NL80211_ARMHF_IW_STAGED_AND_TERMINAL_PLAN_2026-10-25.md), [patch tracker](../../patches/upstream/README.md), and [runtime current state](../../runtime/CURRENT_LINUX7_STATE.env).
2. User has authorized development and previously repeatedly approved temporary, hash-verified boots. **Before any new physical boot, check the user's current go-ahead, actual target serial/model/unlocked state and hardware readiness**; do not apply permanent writes implicitly. Original MZ600 XoomToolkit recovery tablet protected; use replacement MZ600 only.
3. On Surface read-only: enumerate COM ports, USB PID1 `PING`→`PONG XOOM-LINUX V20`, `WIFI_STATUS`, `BT_STATUS`, `MMC2_STATUS`. At last documented 19:25 EDT **v06.3** running, COM9 responding, wlan0/hci0 absent (radio modules unloaded), BCM4329 on onboard SDIO verified. **Do not reboot now just to confirm documentation**. Re-discover port, do not assume it is always COM9.
4. Desktop Git WSL worktree has uncommitted kernel changes (see handoff). Never git clean/reset. Follow [DEVELOPMENT_WORKFLOW](../process/DEVELOPMENT_WORKFLOW.md), sync working branch **wip/clean-wifi-bt-usb-20261025** with `git pull --ff-only` after checking status, verify pinned upstream `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` and exact built DTB, maintain isolated artifact directories.

## 1. User-facing acceptance contract: do not call v06.4 finished before this

**Required actual functions (physical observations, not package presence):**

1. **Standard Wi-Fi scan** using normal Linux interfaces: the BCM4329 Wi-Fi driver loads, creates `wlan0`, can set it UP, `iw phy`/nl80211 works, and one **real scan** returns an AP/BSS result or a precise, diagnosed regulatory/RF error. Display scan results in actual terminal AND report sanitized BSS count/channels/signals over USB; do not publish local SSIDs or BSSIDs. If it cannot scan, label **FAIL/PARTIAL** with errno; do not claim scan pass from wlan0.
2. **Real Xoom on-screen terminal and shell**: visible on TFT framebuffer/console or tested VT, executable normal ARMHF commands, keyboard stdin/stdout, Enter/Backspace, screen clearing/scrolling, and **working USB-shell/diagnostic fallback without relying on Bluetooth**. A custom static diagnostic display or blinking cursor with no shell is NOT acceptance.
3. **Motorola Bluetooth keyboard path**: BCM4329B1 private HCD still loaded successfully, HCI controller up; standard BlueZ/DBus or a proven classic-HIDP pairing agent supports user-controlled discovery and PIN/passkey authentication, pairing/trust/reconnect, and typed text on the real on-screen terminal. Record actual keyboard model/protocol and keymap as measured; do not claim success from hci0 alone. If userspace size/input/security blocks pairing, mark PARTIAL and document exactly why—avoid calling complete v06.4.
4. **Existing hard-earned behaviors must remain working**: robust Linux 7 boot/PID1, board framebuffer/touch, stable USB PONG, BCM4329/Wi-Fi start/ordered WCC teardown, Broadcom HCD Bluetooth HCI up/down and clean unload, no changes to original Android/TWRP/eMMC.
5. **Entire combo chip in scope**: protect shared U4 power vote, WLAN U2, BT U0/I7, wake GPIO, 32.768kHz reference, USB VBUS/charger anomaly, and avoid unqualified concurrent power/reset operations. **Simultaneous Wi-Fi+Bluetooth is NOT currently validated**, and v06.3 diagnostic deliberately disallows concurrent starts; enabling it is its own gated experiment with updated shared ownership, not an unannounced checkbox.
6. Distinguish Wi-Fi scan vs actual association/WPA/DHCP: after scan milestone, standard iwd or wpa_supplicant with credentials handled privately; NetworkManager is optional later, not required for low-level scan. Do not enter user's Wi-Fi passwords into code, logs, or public repo.

**Report each criterion individually PASS/PARTIAL/FAIL/NOT TESTED; retain intermediate images as separate candidates if needed.** There is no arbitrary one-build deadline—testable output and safe rollback outweigh a misleading version label.

## 2. Hardware and immutable v06.3 starting point

- Pinned clean Linux 7 `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, Cortex-A9 **no NEON**, ARMHF sysroot Debian 12 Bookworm; build cross compiler Arm GNU 14.3 in Desktop WSL Ubuntu-22.04.
- Replacement MZ600, fastboot product `xoom-cdma`; removable 32GB SD absent during the proven tests. Kernel + appended Stingray **clean-usb DTB**, **embedded** CPIO archive, Android! legacy boot header with **external ramdisk size 0**, **fastboot boot only**.
- v06.3 source-of-truth private local artifact `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v063/MZ600-CLEAN-WIFI-BT-USB-v063-HCD-RAM-ONLY-UNTESTED.img`, 6,561,792 bytes SHA256 `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`. Do not replace or modify it. Its name retains UNTESTED from before physical qualification; measured driver capabilities are now recorded in checkpoint, not inferred from filename.
- Private firmware `/home/xoomdev/xoom-linux-rom/private-firmware/BCM4329B1.hcd`, 17,332 bytes SHA256 `7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`. Do NOT commit binary or unreviewed firmware.
- Staged `iw` package: Debian Bookworm **5.19-1 armhf**, **93,300 byte** .deb SHA256 `fd1f6c926853505b0eb03a3afb4c6b68e4350f42b140fe6c5295012eeca872ee`; ARM `sbin/iw` size **207,052B**, Debian ARMHF QEMU smoke `iw version 5.19` pass. Build workspace `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/userspace-network/bookworm-armhf-iw/`. Package reproducible staging script `scripts/experiments/stage-debian12-armhf-iw-20261025.py`.
- Existing Debian ARMHF rootfs at `/home/xoomdev/xoom-linux-rom/os-build/bookworm-armhf-root/` includes `libnl-genl-3.so.200`, `libnl-3.so.200`, `libc.so.6` and ARMHF loader `ld-linux-armhf.so.3`. No claim the live v06.3 initramfs has those.
- Useful build precedent `scripts/experiments/build-clean-wifi-bt-v063-private-hcd-20261025.py` reconstructs newc with Linux's `usr/gen_init_cpio`, modifies `CONFIG_INITRAMFS_SOURCE`, cross-compiles zImage, appends compiled DTB, regenerates Android boot hash, verifies output. **It asserts predecessor v06.2 and must be adapted to use v06.3 as immutable base**, not rerun blindly. No v06.4 builder currently exists.

## 3. Size and userspace packaging decision — resolve before building

**Measured v06.3 image:** 6,561,792 bytes. Prior *conservative* boot image envelope check: <= 8,388,608 bytes, leaving **1,826,816 bytes (~1.74 MiB)** for added **compressed** kernel+CPIO payload, not enough to assume BlueZ, D-Bus, libraries, BusyBox, network clients and terminal all fit. Measure REAL compressed deltas rather than estimating.

**First choose one of two honest packaging routes:**

- **A: Self-contained RAM image** if and only if complete set of required ARMHF binaries, dynamic loader, transitive dependency libraries, service config, input/VT utilities and scripts physically fits and boots with secure USB fallback. Strip/debug-remove only where legal/appropriate, reproducibly. Static BusyBox may be smaller than full distro, but test instruction features and library ABI.
- **B: Minimal immutable RAM boot image + standard Debian ARMHF userspace on a separately staged RAM filesystem or user-approved removable SD** if complete terminal/BlueZ stack won't fit. An audited, hash-pinned, size-limited **host→tmpfs** transfer protocol would allow nonpersistent userspace packages without eMMC writes; **do not bypass v06.3's narrow existing UPLOAD allowlist**. Alternatively use the user's 32GB SD for a conventional Debian rootfs **only after explicitly changing the previous no-SD isolation constraint with user authorization** and recognizing SD might affect hardware behavior. Never imply eMMC will be formatted/written.
- If a partial intermediate image is needed, label **v06.4-stage-A/B, not functional v06.4 complete**. Preserve v06.3 exact rollback and log why each integration is split.

## 4. Implementation work breakdown and standard Linux choices

### 4.1 Network scan (first functional acceptance gate)

1. Resolve official ARMHF `iw` dynamic closure with `readelf -l/-d`; kernel cfg80211/nl80211 config already built; ensure correct `/lib/ld-linux-armhf.so.3`, soname symlinks, ELF ABI and no NEON. Use exact official Debian SHA-pinned binary staged, never a host-x86 binary.
2. Add minimal `ip link set wlan0 up` from compatible `iproute2` or tested BusyBox `ip`, including correct NETLINK_ROUTE; kernel link-state permissions (CAP_NET_ADMIN/root where appropriate), `/proc`, `/sys`, `/dev`, `/run` mounts and pid1 side processes configured. Use `iw phy`, `iw dev wlan0 info` to probe.
**Signed regulatory database gate:** This clean kernel uses `CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y`. Supply the matching kernel-trusted **signed** `regulatory.db` as required, honor each channel's allowed/no-IR/passive flags, and capture missing/invalid database errors. Do not disable signature checking, fabricate a country/identity or force prohibited active probing simply to make scans work.

3. Add controlled `WIFI_SCAN` command or the real terminal to invoke **standard `iw dev wlan0 scan`** after existing `WIFI_START`. Require timeout, output buffer limit, graceful error/status, avoid indefinite kernel calls and preserve independent USB PING. Broadcom optional clm_blob/txcap_blob warnings mean available channels may be restricted; DO NOT fabricate regulatory DB/country overrides or change per-device MAC/NVRAM.
4. Actual scan is RF-active and can transmit probe requests. No association/authentication/credential handling needed to test discovery. Store SSID/BSSID raw output only in PRIVATE host logs; public checksum/experiment report should redact identities, include BSS count, frequencies, signal dBm, error number and PHY country/channel limitations.
5. One scan when device is stable, collect dmesg, then `WIFI_STOP` WCC→brcmfmac→brcmutil, all rc0, `wlan0` absent, USB PONG. Mark physical scan PASS only for actual BSS results or demonstrated scan invocation with zero networks as appropriately differentiated.

### 4.2 Genuine local on-screen terminal (not temporary crosshair dashboard)

1. Determine actual current framebuffer/DRM/fbcon ownership from v06.3 `/init` source, effective .config and runtime. Verify console is not covered by our bespoke framebuffer render loop, ensure live tty text visible without keyboard. Candidate: Linux VT+fbcon with `/dev/tty0` or `/dev/tty1`, `getty`/shell, termios/input, console font and scrollback. Alternative: an audited minimal userspace framebuffer text terminal if fbcon fails, but it MUST be real interactive shell.
2. Provide ARMHF shell (BusyBox `ash` or Debian `dash`) and a minimal POSIX utilities suite (mount, ps, cat, ls, dmesg, ip, etc.) suitable for system diagnostics. Explicitly create device nodes /dev/console, tty0/tty1/ttyGS0, /dev/input/event*, /dev/ptmx, and mount devtmpfs/proc/sysfs/devpts/run as required.
3. **USB recovery shell must work with no Bluetooth keyboard**; existing CDC ACM PING + guarded reboot controls should be preserved or replaced with equally robust serial shell plus control service. Never leave the board in unresponsive boot state if GUI/keyboard doesn't initialize. Avoid root remote-access default passwords or network listeners.
4. Confirm physical touch/key input and framebuffer visibility. Keyboard from evdev/console should emit actual letters, Enter, Backspace, Shift, symbols; proper detach key-up to avoid old Motorola keyboard stuck-key phenomenon. Do not require user to hold an unreliable hardware key to enable terminal.

### 4.3 Bluetooth keyboard pairing

1. Base native HCI on **v06.3 HCD**—verified kernel logged `BCM4329B1 'brcm/BCM4329B1.hcd' Patch`, `HCI_DEV_UP rc0`, HCI_DEV_DOWN rc0 and successful USB after unload. Keep candidate firmware private and hash-pinned.
2. Stage a proper ARMHF **BlueZ** `bluetoothd` and `bluetoothctl`/pairing agent (plus actual transitive libraries, D-Bus if required) or a minimal explicitly justified classical HIDP agent. Do not claim kernel HCI0 equals pairing. Check classic HIDP support `CONFIG_BT_HIDP=m` and `/dev/input/event*` paths and BlueZ service permissions.
3. Offer deliberate user-facing **pairing mode and passkey/PIN UI**. Do not auto-pair arbitrary nearby devices or log secrets publicly. Test the user's OEM Motorola keyboard as a real HID input source, including nonstandard symbols, control keys, lost key-up on disconnect, reconnection and cleaned radio unload. RAM-only bond state is volatile; persist only to an explicitly approved storage medium.
4. If simultaneous Wi-Fi+Bluetooth required to connect with keyboard and scan, **DO NOT just remove the current mutual-exclusion guard**. Design/measure shared U4 GPIO/refcount regulator ownership, U2/U0/I7 and 32k LPO/wake, then enable dual radio under a distinct experimental gate; sequential BT→Wi-Fi already physically passed and must remain regression.

## 5. Concrete new build procedure (perform in next chat; do not claim run now)

**Expected new public scripts, manifests and checkpoint outputs** (naming suggested; adjust with Git review):
- `scripts/experiments/stage-v064-armhf-userspace.py` — stage exact Debian ARMHF package versions and SHA256, recursively inspect ELF DT_NEEDED closure, QEMU smoke, no-NEON, report compressed footprint, no device access.
- `scripts/experiments/build-clean-wifi-bt-v064-functional-20261025.py` — reads immutable v06.3 input/hash and offline vetted userspace root; emits **new output directory** `artifacts-embedded-v064/`, manifest with all files/permissions/owner, exact `newc` and deterministic archive, logs distinct kernel source and config diffs. Do not copy v06.3 builder's expectation of a v06.2 base unmodified.
- `patches/lab/0002-v064-*-functional-userspace.patch` (or a correctly named series) — all diagnostic init, USB command, service launcher, VT behavior in **lab userspace**, not disguised Linux upstream kernel patches. True upstream Linux source changes should be separate RFC commits with appropriate provenance/DCO gates.
- `docs/checkpoints/MZ600_V064_FUNCTIONAL_BUILD_PREFLIGHT_*.md` and `docs/checkpoints/MZ600_V064_NL80211_SCAN_AND_KEYBOARD_PHYSICAL_*.md` — clearly distinguish offline and physical steps with return codes and privacy-reviewed output.
- If size forces external RAM tmpfs stage or user-approved SD, document separate content SHA and transport/power/capacity control; leave v06.3 image unchanged.

**Order to execute:**
1. Inspect source, local Git dirty state and current v06.3 physical PING/status; READ ONLY.
2. Check `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v063/MANIFEST.json` and current `build/.config` (note INITRAMFS_SOURCE points at v063 now); create new **isolated** v064 build/CPIO outputs rather than silently rebuilding previous versions. Verify pinned upstream/board DTS actual compiled DTB.
3. Inventory all ARMHF executable paths, DT_NEEDED and transitive libs; `qemu-arm -L /.../bookworm-armhf-root <binary> --version` for smoke, but do NOT classify emulation as physical network/BT success. Enforce Cortex-A9 / no NEON.
4. Build a real terminal + USB-fallback foundation, test QEMU functional shell on workstation and offline framebuffer/PTY interfaces insofar as supported; keep v06.3 untouched and boot image under tested size/boot header constraints.
5. Integrate `iw` and reliable `wlan0 UP` plus bounded scan with sanitized output. Add BlueZ/pairing agent/input stack within measured packaging plan, do not omit without explicit PARTIAL status.
6. Repackage kernel `CONFIG_INITRAMFS_SOURCE`, `usr/gen_init_cpio`, verify exact `usr/initramfs_inc_data`, compressed size, zImage+**same DTB unless justified**, legacy Android! header, page alignment, zero external ramdisk, correct SHA1 ID, total < 8MiB, SHA256; compare inherited CPIO members and firmware hashes with v06.3.
7. Transfer *new* image to Surface over existing authenticated host link, recompute SHA256 independently, review guarded one-shot launcher command **fastboot boot only**, verify exact device and no removable SD. Do not flash, alter internal partitions or attempt repeated blind boot loops if normal Power/red LED returns.
8. Physical qualification in order: Linux PID1/USB PONG and display; visible local shell + USB backup; BT HCD/hci0 driver; real Wi-Fi `iw phy` and **single scan**; Wi-Fi stop/USB regression; deliberate user-initiated keyboard pairing and actual terminal typing; BT stop, whole-chip sequential regression. Only then discuss concurrent radio enable with separate shared-power gate.
9. Update **the comprehensive handoff and current state ledger ON EVERY significant test**, including negative ones, rather than saving only end-of-chat summaries. Preserve raw captures privately, sanitized GitHub checkpoint and accurate acceptance labels.

## 6. Explicit reproducible smoke and physical acceptance tests

**Offline (compiler/QEMU):** real `iw --version` returns **5.19**; ARMHF console shell supports `echo`, `ls`, `ip --version` (or tested BusyBox equivalent), BlueZ `bluetoothd --version`, and loader resolves all transitive libraries. No "binaries copied but cannot execute" handoff. Boot image hash and boot header, module vermagic, unique build id, size, dev nodes, cap/config gates independently tested.

**Device (no blind scans):**
- `PING`→`PONG`, local terminal displays command output.
- Explicit WIFI_START→`wlan0`, `ip link set wlan0 up`, `iw phy`, `iw dev wlan0 scan` under actual country/channel rules, sanitized BSS summary and command status.
- WIFI_STOP must give **WCC→brcmfmac→brcmutil each rc0**, interface gone.
- BT_START→kernel HCD patch log→`hci0`→HCI_DEV_UP rc0; pairing agent user-controlled → input device → keyboard types into on-screen shell; BT_OFF/HCI_DEV_DOWN rc0 and six modules unload rc0 (when not connected).
- No loss of USB PONG or next normal Power-on; separately preserve exact power/charger/USB cable and Power-button hold duration during any red-light recurrence.
- **Do not call coexistence PASS** until Wi-Fi scanning/connection is deliberately tested while Bluetooth keyboard is connected and shared chip regulator ownership is independently verified.

## 7. Unresolved safety and source caveats

The red-light startup issue is not diagnosed. Removing USB + charger coincided with an early recovery but **did not clear** the later recurrence; user found **holding Power about three seconds after TWRP shutdown** could start Android where quick tap only flashed LED. The **identical** v06.3 image had both an unsuccessful no-PONG boot attempt and successful PONG/HCD/BT→Wi-Fi physical PASS after different startup conditions. No proof a firmware binary corrupted the chip, no evidence of corrupted DS2781 NVM, and no permanent flash write. Prefer measured one-variable power-button/USB/charger baselines to PMIC speculation.

The long-standing October 24 F2 -62 reports apply to old experimental images, not the current clean v06.3; do not restart old debugging unless regression is physically reproduced. The broad goal of **full combo-chip support includes eventual reliable shared rail reset, GPIO/clock/wake, simultaneous radio usage and possibly FM if board wiring proves it**, but these are not currently qualified.

**No Windows95/emulation project work here. No original/protected MZ600 experimentation. No push to Linux maintainers without real author's Signed-off-by/DCO and user direction. No private binary, per-device MAC, local SSID/BSSID, Wi-Fi password or Bluetooth link key on public GitHub.**

**Definition of finished v06.4:** not a filename, not a copied Debian binary, not a compile-only image, and not HCI0/wlan0 alone. It is a verified functional scanner, actual on-device terminal, and paired working keyboard (or a precise, documented PARTIAL result with a continuation plan); preserved v06.3 physical baseline; full safe USB and rollback; updated comprehensive handoff.
