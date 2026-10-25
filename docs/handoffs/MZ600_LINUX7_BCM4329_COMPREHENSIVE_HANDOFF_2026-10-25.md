# XoomLinux7 / Motorola Xoom MZ600 — Comprehensive Engineering Handoff

**Snapshot:** Sunday, October 25, 2026, evening EDT.  
**Project:** [Olsens11/XoomLinux7](https://github.com/Olsens11/XoomLinux7), active branch `wip/clean-wifi-bt-usb-20261025`.  
**Purpose:** Give the next ChatGPT conversation enough verified project state, reasoning, decisions, provenance, architecture, test history, hardware boundaries, paths, tooling and next steps to continue without repeating previous work.  
**Confidence policy:** Distinguish physical proof from offline build, inference, old historical results, and untested capabilities. Public sources may lag newer private tests. No private MACs, host authentication details, passwords, Wi-Fi SSIDs or firmware contents are reproduced here.

---

## 1. Executive state — read this first

The user is developing **native Linux 7.0 on Motorola Xoom tablets**, especially an **experimental replacement MZ600 Stingray**, using the existing upstream `xoom-linux/linux` project rather than rewriting the kernel. The active objective is to support the **entire Broadcom BCM4329 combo chip** (Wi-Fi, Bluetooth, shared power/reset/clock ownership, and eventually any genuinely supported FM function). The project should evolve into a conventionally installed, fully useful Debian-based Linux operating system, with functioning Wi-Fi, **an actual Bluetooth Motorola keyboard**, a **real on-screen terminal**, input/display/audio/power, and eventually upstream submission-quality Linux patches. Windows 95 emulation is a separate future idea, **not the current priority**.

**Latest VERIFIED running device:** The replacement MZ600 is still running the **v06.2 Linux RAM-only boot image**. It is USB-connected to the Surface Book 2 through **COM9 CDC ACM**; the serial diagnostic program replied `PONG XOOM-LINUX V20` on a fresh read-only check late on Oct 25. `MMC2_STATUS` confirms the **BCM4329 is present** on its onboard SDIO bus. Wi-Fi modules are **unloaded** (`wlan0` absent) and Bluetooth modules are **unloaded** (`hci0` absent). The 32 GB removable microSD is **physically absent** as part of isolated clean tests. **No flash, format, or permanent partition write was performed** in the recent clean Linux work.

**Physical breakthroughs actually established on v06.2:**

- It **boots**, loads diagnostic PID1, exposes a working USB CDC ACM console, and remains responsive.
- Wi-Fi: `WIFI_START` loads `brcmutil`, `brcmfmac`, and `brcmfmac_wcc`, initializes Broadcom firmware **4.220.48** and creates `wlan0`.
- Wi-Fi teardown: `WIFI_STOP` correctly unloads **`brcmfmac_wcc` → `brcmfmac` → `brcmutil`**, each return code `0`; `wlan0` disappears, USB PONG remains.
- Bluetooth: `BT_START` loads six dependent modules and the UART/serdev driver identifies **BCM4329B1** and creates **`hci0`**. `BT_ON` returns **`HCI_DEV_UP rc 0`**. `BT_OFF` returns **`HCI_DEV_DOWN rc 0`**. `BT_STOP` removes all six modules with `rc 0`; USB PONG survives.
- **Whole-chip sequential transition:** Bluetooth was started, brought down and unloaded; **then Wi-Fi initialized again on that same running kernel**, created `wlan0`, and unloaded cleanly. This **does not** demonstrate simultaneous Wi-Fi/Bluetooth coexistence or full electrical chip power-off.

**Not achieved yet:** No nearby Wi-Fi network scan, network association/WPA/DHCP, proven legal full-channel RF operation, Bluetooth firmware HCD patch application on physical hardware, Bluetooth keyboard pairing/typing on Linux, usable interactive on-screen terminal, simultaneous Wi-Fi+Bluetooth, FM, proven shared-rail POR, good suspend/resume, or permanent Linux eMMC install.

**Prepared OFFLINE but NOT physically booted:** v06.3, a v06.2-derived boot image with one additional privately supplied **BCM4329B1.hcd** firmware file. Separately, a standard Debian 12 **ARMHF `iw` 5.19** package for real `nl80211` scanning has been downloaded, SHA-verified and executed with QEMU. **`iw` is NOT yet included in v06.3 or on the currently running v06.2.**

**Next user requirements:** Before another build, take Wi-Fi as far as possible; the existing v06.2 can't scan because it lacks an `nl80211` client, so move to **standard `iw`** in the next build. The **next build should expose a real terminal on the tablet usable with the Bluetooth keyboard** if pairing succeeds. The user insists the **entire physical BCM4329** remains the unit of architectural analysis; record changes as preliminary **actual patch candidates**, not just prose notes.

---

## 2. The new assistant's required reading order

1. **This handoff** and the latest Oct 25 measurements below.
2. [`AGENTS.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/AGENTS.md) — operating agreement: device protection, upstream-first source, safety, privacy and state integrity. Its Oct 24 *version labels* are outdated; its safety contract is not.
3. [`START_HERE.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/START_HERE.md), [`docs/README.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/README.md), [`DEVELOPMENT_WORKFLOW.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/process/DEVELOPMENT_WORKFLOW.md), [`DOCUMENTATION_AUTHORITY.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/process/DOCUMENTATION_AUTHORITY.md), worktree/key policy.
4. **Newest positive physical measurements:** [`MZ600_V062_WIFI_WCC_ORDERED_UNLOAD_PHYSICAL_PASS_2026-10-25.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_V062_WIFI_WCC_ORDERED_UNLOAD_PHYSICAL_PASS_2026-10-25.md) and [`MZ600_V062_BCM4329B1_BLUETOOTH_HCI_LIFECYCLE_PHYSICAL_PASS_2026-10-25.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_V062_BCM4329B1_BLUETOOTH_HCI_LIFECYCLE_PHYSICAL_PASS_2026-10-25.md).
5. **Next software plan:** [`MZ600_NL80211_ARMHF_IW_STAGED_AND_TERMINAL_PLAN_2026-10-25.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_NL80211_ARMHF_IW_STAGED_AND_TERMINAL_PLAN_2026-10-25.md).
6. Earlier Oct 25 facts: v06.1 startup/WLAN success, v06.2 first failed boot attempt **and later identical-image successful retry**, and USB/power red-LED checkpoint. Read the repo [`patches/upstream/README.md`](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/patches/upstream/README.md) and actual patches.
7. [Upstream policy](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/architecture/UPSTREAM_POLICY.md), [platform design](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/architecture/PLATFORM.md), [BCM4329 page index](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/research/BCM4329_DATASHEET_PAGE_INDEX.md), [requirement audit](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md), [chip ownership design](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md), [cross-subsystem fault tree](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/research/BCM4329_CROSS_SUBSYSTEM_FAULT_TREE.md).
8. Historical OEM analysis files in Library: **`MOTOROLA_BCM4329_OEM_LIFECYCLE_RECONSTRUCTION_V2.md`**, **`MOTOROLA_BCM4329_OEM_CALLGRAPH_TRACE_V3.md`**, relevant `CYW4329HKUBGT`/`4329_DS105_R` datasheet. **CYW20702 is a different device and not authoritative for BCM4329 pins/timing**.

**Crucial stale-document warning:** Top-level repo README, START_HERE, large parts of docs/status.md and runtime/PROJECT_STATE.env still describe the **October 24 experimental-kernel SDIO Function2 -62 timeout / `wlan0` absent / v015/v020**. Those are valid *historical* failures but **NOT the current clean v06.2 state**. They must be reconciled and indexed as a documentation-maintenance task, not silently relied upon. Latest physical checkpoint beats stale status prose.

---

## 3. Hardware roles and hard safety boundaries

- **Original MZ600**: Protected original **modified TWRP 3.1.1-0 XoomToolkit** device and OEM reference. It has its own recovery UI/packages (Wi-Fi, Time Sync, SSH/SFTP, Desktop Commander, Bluetooth HID) and should NOT be used as the native Linux experimental DUT.
- **Replacement MZ600**: Active Linux 7 DUT with unlocked fastboot product **`xoom-cdma`**, normal Android and TWRP retained; experimental images launched with **`fastboot boot IMAGE` ONLY**, never `fastboot flash`. The replacement has had charging/power-key quirks; the OEM dock is a reliable charger on one tested unit. Physically remove microSD for controlled Linux tests. Normal Power-only startup behavior must be tracked.
- **Other Xooms**: Several MZ604 Wi-Fi, MZ602 3G and MZ617 Xyboards are available as future A/B controls. **Never assume the MZ600 kernel image and appended DTB can be booted safely on MZ604/MZ602/MZ617 without confirming exact board/fastboot product/device tree.**
- **Surface Book 2 (Windows)**: Connected to the physical DUT USB, runs Windows fastboot/ADB, **COM9** CDC ACM (port may change), host Python and PowerShell. Authorized **Remote Desktop Commander** gives remote file/terminal access. Surface path `C:\Users\olsen\xoom-linux-rom\downloads\` holds verified boot images; `captures\` holds private logs/one-shot scripts.
- **Desktop (Windows + WSL Ubuntu-22.04)**: High-performance kernel builder; WSL account **`xoomdev`**, Arm GNU Toolchain **14.3.Rel1** `arm-none-linux-gnueabihf`, QEMU armhf and Git workspace. Authorized Remote Desktop Commander access.
- **Raspberry Pi**: historical recovery/OEM reference and Git worktree; availability in a future chat must be checked.

### Absolute project rules

**No flashing/partition edits without a new explicit user authorization**: never `fastboot flash`, formatting, `dd of=/dev/block`, altering BOOT/SYSTEM/USERDATA/RECOVERY, bootloader relock or arbitrary internal block writes. The clean experimental images remain RAM-only and original stock Android/TWRP stays intact. Verify private device identity, image hash, model and unlocked state before **any** RAM boot. Keep SD out when reproducing clean tests.

No passwords, per-device serial, MAC, Wi-Fi SSID/BSSID, QR secrets, proprietary HCD firmware bytes, calibration, ROM dumps or deploy keys in public repo/checkpoints. Raw logs stay private on Surface; publish sanitized interpretations and hashes. Honor source licenses and the Linux Developer Certificate of Origin; no fabricated Signed-off-by lines.

---

## 4. Project rationale, kernel and board architecture

**Upstream first:** Linux project [`xoom-linux/linux`](https://github.com/xoom-linux/linux) pinned source SHA **`2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`**. Kernel reports **`7.0.0-next-20260422+`**. CPU is Tegra 2 dual **Cortex-A9 ARMv7 with NO NEON**; build artifacts/userspace must not execute NEON, despite valid VFP hardware and ARMHF ABI. The repo should contain only relevant board-specific changes/scripts/patches with attribution; do not vendor whole upstream source.

**Linux core infrastructure:** `sdhci-tegra`, MMC/SDIO, `brcmfmac`+`brcmutil`+`brcmfmac_wcc`/cfg80211/nl80211, `hci_uart`+`btbcm`/serdev, CPCAP regulators, Tegra clocks/GPIO/reset/pwrseq, framebuffer/DRM, maXTouch, USB CDC ACM, evdev, VT, framebuffer console. Standard software policy belongs in userspace wherever possible.

**WLAN:** onboard Broadcom vendor **0x02d0**, device **0x4329** on internal **SDMMC2** controller `c8000200.mmc`, functions mmc2:0001:1 and :2; **do not confuse with the removable microSD or internal eMMC**. `brcmfmac` creates **`wlan0`** when firmware initializes. WCC module must unload **before** brcmfmac, which must unload before brcmutil.

**Bluetooth:** BCM4329B1 chip identified through **UARTC `serial@70006200`**, standard `brcm,bcm4329-bt` serdev device tree node and Linux `hci_uart`/btbcm driver. Six dependency modules: `ecc`, `ecdh_generic`, `cmac`, `bluetooth`, `btbcm`, `hci_uart`; off/unload in reverse. Bluetooth HCI device is **hci0**.

**Shared physical chip:** Motorola OEM coordinated WLAN and BT power using a **shared U4 supply-enable reference count**. WLAN **U2** reset/REG_ON, BT **U0** reset, **I7** shutdown, **U1** BT wake, **U6** host wake, WLAN **U5** host wake, **32.768 kHz** shared LPO/PMC CLK_BLINK, CPCAP/regulator votes. Current DT has simple WLAN reset pwrseq and BT UART child. **Driver unload rc0 is not proof of rail-off/POR**. The user specifically wants board implementation based on a comprehensive OEM lifecycle and datasheet, not ad hoc independent Wi-Fi/BT GPIO guesses. FM is mentioned in the chip datasheet but **physical wiring/driver are unproven**; do not invent an FM node.

**OEM vs Linux firmware:** Motorola HRI39/HRI66 OEM kernel 2.6.36.3-g2a65edc + private 2011 `bcm4329.ko` and firmware/calibration (one old firmware version 4.218.248.20). Clean Linux Broadcom firmware emits **`BCM4329/3 wl0 ... version 4.220.48`**. MAC address must come from same device (bootloader vendor ATAG, not hardcoded shared value); calibration and country data private and audited; don't claim regulatory compliance solely from interface registration.

**Boot layout:** Current small static diagnostic **PID1 `/init`** and supporting ARM modules/firmware/device nodes are packed with kernel's own **`usr/gen_init_cpio`** and **embedded into zImage by `CONFIG_INITRAMFS_SOURCE`**. Legacy Android! boot image has **zero external ramdisk**, zImage + appended actual compiled Stingray DTB. It runs without SD. USB CDC ACM `/dev/ttyGS0` ASCII protocol exposes commands, screen/touch debug and guarded module operations. **This is NOT yet a normal Debian interactive environment** and has no `iw`, `bluetoothctl`, shell or general arbitrary-upload command.

---

## 5. Historical Oct23/24 development and why the CLEAN pivot mattered

Before Oct25, many Phase1 kernel variants established Linux framebuffer/crosshair/touch, SDIO/USB and firmware upload/reload tooling. v015 **USB raw binary transfer with checksum** and v020 **MMC2 on-demand card reinit/profile switching** were physically demonstrated. Older BCM4329 tests often wrote Function2 enable IOEx 02→06 but observed IORx stuck 02 and **-62 timeout**, no wlan0. Real negative controls included Motorola six embedded SDIO capability fields, legacy 25MHz rate, 100ms extra reset spacing, reference 32k LPO, alternate OEM firmware/NVRAM, regulatory and runtime PM; none alone fixed F2. v035–v041 read-only PMU, ALP/HT resource, firmware-CM3 release, SDPCM mailbox and NVRAM startup research refined fault hypotheses. v033 BT controller probe and v034 fixed **HCIDEVUP/DOWN device index passed by value, not pointer**. The OEM full-chip owner proposal was largely compile-only, not proven linked into the clean Linux kernel.

A prior Debian ARMHF rootfs on SD and USB terminal was experimented with, but **current clean v06.2 is on RAM-only built-in initramfs with no SD**. Do not claim permanent Debian installation from that separate experiment.

**Critical pivot:** The Oct25 fresh clean Linux build (upstream driver/modules, carefully staged chip firmware, proper built-in CPIO, no removable SD) actually initializes BCM4329 and gets wlan0. The old -62 behavior is historically true **but is not the current clean v06.2 result**. The exact causal difference between earlier failed trees/hardware states and clean working tree was **never isolated**, so do not assert a single upstream bug was solved by a specific old workaround.

---

## 6. Exact immutable boot images

| Boot candidate | Bytes | SHA256 | Status |
|---|---:|---|---|
| Clean no-SD v04 USB baseline | 7,870,464 | `da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b` | **Physical USB/PID1 PASS**, preserved rollback |
| v06 **external** RAM CPIO | 6,547,456 | `c8240c65bf43064b82acec516ffc863e819db314e6f5fa0033586241390e00e9` | **Physical kernel panic**, missing `rdinit=/init` and VFS unknown-block(0,0) |
| v06.1 **built-in** CPIO | 6,547,456 | `b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a` | Physical USB/PING, Wi-Fi firmware and **wlan0 PASS**; old stop failed (-11) |
| **v06.2 WCC teardown** | **6,549,504** | **`bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`** | **CURRENT LIVE PHYSICAL PASS:** Linux/PID1/USB, Wi-Fi and Bluetooth lifecycle, sequential BT→Wi-Fi |
| **v06.3 private HCD** | **6,561,792** | **`07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`** | **OFFLINE/HASH/HEADER PASS ONLY. NEVER physically booted**; one extra HCD CPIO file |

**v06 initramfs panic:** Linux actually started and enumerated storage, then printed `check access for rdinit=/init failed: -2` and VFS panic. COM9 may enumerate without a working PID1. v06.1 embedded the CPIO via kernel compilation (rather than external Android ramdisk). Verified `usr/initramfs_inc_data` exact SHA and Android header/DTB. **Don't convert it back to an unproven external ramdisk**.

**v06.2 change:** Only diagnostic static `/init` `wifi_stop()` code changed, unloading **WCC → brcmfmac → brcmutil** with failure checks. Other 25 initramfs members, DTB and kernel source logic identical to v06.1; image re-compressed. Exact laboratory patch saved under **`patches/lab/0001-v062-broadcom-wcc-unload-order.patch`**; physically tested PASS.

**v06.3 change:** Extra file `/lib/firmware/brcm/BCM4329B1.hcd`, no code change to kernel/DTB/diagnostic. Private HCD file **17,332 bytes**, SHA **`7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`**, 98 parsed Broadcom HCI vendor commands (syntax validated, not hardware compatibility). Kernel BT driver tried `brcm/BCM4329B1.motorola,stingray.hcd` then `brcm/BCM4329B1.hcd` (among four), so basename matches fallback. **Firmware binary itself never committed publicly**. HCD is prepared in a private local directory and has NOT loaded on the Xoom yet.

---

## 7. October 25 physical test timeline and outcomes

**~13:55 v06.1 RAM boot:** Surface independently checked image SHA, target product/unlocked. `fastboot boot` accepted; COM9 appeared and true PID1 USB `PING/PONG` passed for 75 seconds. Onboard mmc2 BCM4329 verified. `WIFI_START` loaded brcmutil/brcmfmac/WCC (rc 0) and `wlan0` appeared; firmware reported 4.220.48. No scan. `WIFI_STOP` attempted brcmfmac/brcmutil while WCC held module references, returned **-11**. Led to v06.2 userland fix.

**~14:25 first v06.2 boot attempt:** Same later-proven image accepted by fastboot but COM9 never appeared during 75-second window. A blinking red LED near the camera appeared with ordinary Power; Power+Volume Up forced boot. **Do NOT call v06.2 bad; one attempt in a different previous chip/USB/power state failed.**

**Power-on anomaly:** Original stock Android and TWRP were accessible via forced reboot. Normal Power-button starts failed **even after shutting down from both TWRP and stock Android**. TWRP battery telemetry ~82–83%, ~7.915V, AC offline; it exposed **no accessible pstore or `/proc/last_kmsg`**, so no prior Linux crash trace. **User unplugged BOTH power cable AND USB cable, then pressed ordinary Power ALONE; it started normally**. Critical exact observation: both cables changed at once, so neither USB VBUS nor charging input isolated as cause. Power+Volume Up is documented Motorola **forced reboot**, NOT verified full PMIC cold power cycle. Claims of a confirmed PMIC latch, DS2781 calibration corruption, or battery failure are **unsupported**. A similar historical stock Xoom black-screen workaround existed in 2011.

**~17:28 v06.2 identical image re-test:** After normal Power-only startup recovered, stock Android was verified and v06.2 temporary RAM boot accepted. COM9 ~6 sec later, PONG/BT_STATUS, 75s stable with no disconnects. Proved exact v06.2 **CAN boot**; no radio started yet.

**~17:40–17:41 v06.2 WLAN lifecycle:** `WIFI_START` brcmutil rc0, brcmfmac rc0, WCC loaded, `wlan0 PRESENT`, firmware 4.220.48. `WIFI_STOP`: **WCC rc0, brcmfmac rc0, brcmutil rc0**. All modules absent, wlan0 absent. Poststop PONG/COM9 PASS. Missing optional `clm_blob` / `txcap_blob` messages (err -2) did not prevent interface creation, but are **NOT proof full legal channel support**. `debug 6` was a display string, not a verified accepted module parameter.

**~17:47–17:52 v06.2 native Bluetooth:** `BT_START` loaded **ecc, ecdh_generic, cmac, bluetooth, btbcm, hci_uart**, all rc0. `hci0 PRESENT`, chip BCM4329B1 ID41 build0000. Kernel logged **firmware Patch file not found** (v06.2 contains no HCD). `BT_ON` gave **HCI_DEV_UP rc0**, `BT_OFF` **HCI_DEV_DOWN rc0**. `BT_STOP` unloaded all six rc0 in reverse order; HCI0 gone, PONG/COM9 remained healthy. **No inquiry, pairing, keyboard or HCD tested.**

**~18:05–18:06 sequential whole-chip use:** On the **same uninterrupted v06.2 kernel** after BT stop, one WIFI_START again gave firmware 4.220.48, all modules loaded and **wlan0 PRESENT**. One WIFI_STOP unloaded WCC, brcmfmac, brcmutil all rc0; wlan0 gone, USB PONG true. **Sequential BT→Wi-Fi PASS; not simultaneous operation.**

**~18:18 read-only refresh:** Linux 7 still active, COM9 PONG, onboard BCM4329 present, Wi-Fi modules absent, Bluetooth modules absent. No flash/reboot or further chipset activation.

---

## 8. Wi-Fi: software control and the exact next requirement

**The user asked:** Once kernel creates `wlan0`, should standard Linux software perform scanning/connection? **Yes.** Standard layers are BCM4329 firmware/SDIO and `brcmfmac` → kernel `cfg80211`/`nl80211` → userspace **`iw`** (phy capability and scan) → **`iwd` or `wpa_supplicant`** (authentication/association) → DHCP/IP/DNS → optionally **NetworkManager** as higher-level orchestrator later in full Debian. Don't add a bespoke driver-specific network scanner to the kernel or prematurely drag NetworkManager into tiny CPIO.

Actual v06.2 has **CONFIG_CFG80211=y**, `CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y`, and WEXT disabled. USB mini diagnostic **does not support scanning or arbitrary program execution**; no `iw`, `ip`, or shell exists on-device. Seeing `wlan0` does not mean scans were performed, and `iw dev wlan0 scan` may transmit probe requests. Regulatory and per-device MAC/calibration must be correct; never invent channels/country or expose the SSIDs/BSSIDs publicly.

**Successfully downloaded official Debian 12 ARMHF `iw` package:** `iw_5.19-1_armhf.deb`, **93,300 bytes**, SHA **`fd1f6c926853505b0eb03a3afb4c6b68e4350f42b140fe6c5295012eeca872ee`**. Extracted ARMv7/ARMHF ELF32 executable **207,052 bytes**, no NEON requirement. Dependencies already in separate Debian armhf rootfs: `libnl-genl-3.so.200`, `libnl-3.so.200`, `libc.so.6`, `ld-linux-armhf.so.3`. Tested **`qemu-arm -L ARMHF_ROOTFS iw --version`** -> `iw version 5.19`. **Staged OFFLINE only**, not included in v06.3. Reproducer in repo: `scripts/experiments/stage-debian12-armhf-iw-20261025.py`.

**Next scan test design:** new versioned initramfs includes `iw`, its complete dynamic linker/libs, an `ip link set wlan0 up` capable tool, and a bounded way to execute real commands via USB or terminal. Preflight PING/MMC2, load Wi-Fi, observe wlan0, query phy, bring interface UP, perform **one actual scan**, record channels/count/signals/driver errors (raw SSIDs/BSSIDs PRIVATE), unload in proven dependency order, verify PONG. Then build standard auth stack for real connection. Any scan is RF-active and must honor signed regulatory constraints. No invented available network list.

---

## 9. Bluetooth keyboard, HCD, and real on-device terminal

**Physical native Linux Bluetooth success thus far:** Actual BCM4329B1 HCI registration plus HCI_UP/HCI_DOWN and clean module unloading. Firmware patch request missing in v06.2; no keyboard pairing or input has happened yet in Linux. Earlier customized TWRP recovery toolkit **did** pair the OEM Motorola Bluetooth keyboard, proving the hardware/keyboard can work in that different environment; do not imply native Linux inherits those keys/services.

**v06.3 HCD** is a deliberate **single added file** experiment; consider booting it alone before mixing more userspace changes, so one can observe HCD patch accepted/rejected and chip revision/build details with a clean causal test. The image and guarded **`Xoom-V063-HCD-USB-Once.ps1`** launcher have been checked but **not executed**. Don't upload HCD disguised as generic Wi-Fi firmware: v06.2 USB UPLOAD uses a narrow, intentional allowlist.

For real keyboard: standard **BlueZ bluetoothd + D-Bus/`bluetoothctl` agent** or a proven minimal BR/EDR pairing implementation; capture PIN/passkey interaction securely; kernel **CONFIG_BT_HIDP=m**, use evdev and real input keymap. Test letters, Shift, Backspace, Enter, unusual Motorola symbol keys and missed key-up after disconnect. No persistent bond without approved nonvolatile storage (RAM state disappears at reboot; external microSD presently removed).

**User specifically wants next build's UI to contain a USABLE terminal if keyboard works**. Kernel already has **CONFIG_VT=y**, **CONFIG_FRAMEBUFFER_CONSOLE=y**, **CONFIG_UNIX98_PTYS=y**, **CONFIG_INPUT_EVDEV=y**; but current framebuffer PID1 is a temporary grid/dashboard, **not a shell**. Add a cross-compiled ARMHF shell (BusyBox ash/working Debian shell), appropriate device nodes/tty/getty or framebuffer terminal, scrollable text output, keymapping, stdin via HIDP keyboard, and a reliable **USB serial shell/debug fallback** if pairing or input breaks. Maintain reversible USB diagnostics; don't swap a working control plane for an untested only-keyboard UI.

**Whole BCM4329 future acceptance** requires simultaneous Wi-Fi network scan/connection **while Bluetooth keyboard active**, verified shared regulator/power reset ownership, wake/LPO/sleep and ability to power down and start normally. Current v06.2 deliberately rejects starting BT while Wi-Fi modules are loaded and vice versa; sequential success doesn't prove concurrency.

---

## 10. Actual source/build locations and standard host workflows

**GitHub**: public [`Olsens11/XoomLinux7`](https://github.com/Olsens11/XoomLinux7), active experimental branch **`wip/clean-wifi-bt-usb-20261025`**. `main` is not necessarily the Oct25 experimental branch. Preserve independent worktrees and one writer per branch. Older copies of `docs/status.md` and `runtime/PROJECT_STATE.env` require reconciliation when graduating current successes.

**Desktop WSL workspace:** `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`:
- `linux/` exact upstream pinned kernel with expected **dirty** edits: `arch/arm/boot/compressed/atags_to_fdt.c`, `arch/arm/boot/dts/nvidia/Makefile`, **untracked** `arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts`. **DO NOT run blind git reset/clean/restore.** Capture these as real patches.
- `build/` kernel out-of-tree config and artifacts; after building v06.3, **CONFIG_INITRAMFS_SOURCE points to v063 archive**. Rebuilding previous v06.2 without restoring the original config path could produce a different image. Verify exact DTB and kernel archive, not just edited source.
- `artifacts-embedded-v061/`, `artifacts-embedded-v062/`, `artifacts-embedded-v063/`: pinned generation-specific built images, generated source/CPIO and manifests. v063 CPIO/image contain private vendor firmware and stay OFF public repo.
- `artifacts/`: baseline USB diagnostic code source.
- `userspace-network/bookworm-armhf-iw/`: official Debian `iw` .deb, extracted `sbin/iw`, manifest and SHA.
- Separate `/home/xoomdev/xoom-linux-rom/os-build/bookworm-armhf-root/` Debian 12 ARMHF libraries; `/home/xoomdev/xoom-linux-rom/private-firmware/BCM4329B1.hcd` private file.
- Integration repo working copy: `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project/`; its local HEAD at the late audit was **253ee87** and **remote branch may be ahead**. Inspect branch and `git pull --ff-only` before new commits, do not overwrite concurrent work.

**Surface folders:** `C:\Users\olsen\xoom-linux-rom\downloads\` for verified v04/v061/v062/v063 images; `captures\` for one-shot PowerShell test scripts and PRIVATE logs. Examples: `Xoom-V062-WCC-USB-Once.ps1` (verified physical launcher); `Xoom-V062-WIFI-Start-Stop-Once.ps1`, `Xoom-V062-BT-Start-Stage1-Once.ps1`, `Xoom-V062-BT-ON-OFF-Once.ps1`, `Xoom-V062-WiFi-after-BT-Once.ps1`, `Xoom-V063-HCD-USB-Once.ps1` (prepared, NOT run), `Xoom-Verify-Clean-V063-ReadOnly.py`. Candidate private HCD also at `C:\Users\olsen\Downloads\BCM4329B1.hcd`.

**Public source scripts** on active Git branch:
- `scripts/experiments/build-clean-wifi-bt-v061-embedded-20261025.py`
- `scripts/experiments/build-clean-wifi-bt-v062-wcc-unload-20261025.py`
- `scripts/experiments/build-clean-wifi-bt-v063-private-hcd-20261025.py`
- `scripts/experiments/stage-debian12-armhf-iw-20261025.py`
- `scripts/forensics/compare-v061-v062-boot-images-20261025.py`
- `scripts/upstream/audit-staged-rfc-patches-20261025.sh`
- `patches/lab/0001-v062-broadcom-wcc-unload-order.patch`
- `patches/upstream/rfc/series` and `0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch`

**Safe read-only serial reconnection example, Surface PowerShell:**

```powershell
$p = [IO.Ports.SerialPort]::new('COM9', 115200)
$p.DtrEnable = $true
$p.RtsEnable = $true
$p.ReadTimeout = 800
$p.WriteTimeout = 800
try {
    $p.Open()
    $null = $p.ReadExisting()
    $p.Write(('PING' + [char]10))
    Start-Sleep -Seconds 2
    $rx = $p.ReadExisting()
    if ($rx -notmatch 'PONG XOOM-LINUX') { throw 'USB diagnostic unavailable' }
    $p.Write(('WIFI_STATUS' + [char]10))
    Start-Sleep -Seconds 2
    $status = $p.ReadExisting()  # Keep SSIDs/MACs/private values private.
} finally { $p.Dispose() }
```

**USB command classes:** read-only `PING`, `STATUS`, `CPU`, `MEM`, `STORAGE`, `INPUT`, `THERMAL`, `USB`, `LOGS`, `BOOTLOG`, `SDIO`, `CMDLINE`, `GRID`, `WIFI`, `WIFI_STATUS`, `BT_STATUS`, `MMC2_STATUS`. Explicit state-changing commands: `WIFI_START`, `WIFI_STOP`, `BT_START`, `BT_ON`, `BT_OFF`, `BT_STOP`; v06.2 rejects overlap. Higher-risk: `WIFI_RETRY`, `MMC2_PROFILE/REINIT/BIND`, `UPLOAD`, `REBOOT`, `POWEROFF`. Power commands arm a 20-second window then require separate `CONFIRM REBOOT` / `CONFIRM POWEROFF`. **Avoid casual shutdown given the USB/charger anomaly**. The UART baud reported by the kernel for BT is separate from Windows COM9 USB 115200 configuration. Never mix diagnostic output/progress with a function's raw returned PONG (a prior PowerShell helper had a false-negative due to this).

**Rebuild discipline:** Actual compiled DTS/DTB, kernel config, ARM GNU 14.3 toolchain, no NEON, module vermagic, full CPIO entry metadata, SHA256, Android legacy header `ANDROID!` and old SHA1, external ramdisk=0, appended DTB, boot cmdline and boot size under previously used ~8 MiB. Vary one source/program/firmware input at a time for root-cause work; if deliberately combining scan+terminal+HCD in the next build, label it a **multi-feature integration candidate** and preserve independent v06.3 single-delta HCD baseline. No automatic flashing.

---

## 11. Linux patch candidates, provenance, upstreaming policy

The user wants **actual Linux patches maintained as we go** for exact reproduction and eventual submission. The work is preliminary and can be reordered/refined, but must NOT exist solely as memories or hidden worktree edits.

**Current RFC kernel source patch:** Motorola Stingray bootloader WLAN MAC vendor ATAG **`0x57464d41` → `local-mac-address` on FDT mmc2/wifi@1** so it uses the individual board identity, not a fabricated/copy-and-paste MAC. Original tested source `patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch`. Formatted candidate `patches/upstream/rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch`: `git apply --check` against exact pinned source PASS, `scripts/checkpatch.pl` **zero style warnings**, one outstanding **missing Signed-off-by** error; user has not signed Linux DCO, and formatted bytes were not separately physically booted. **No upstream submission has been made**.

**Unstaged/upstream-targeted source work:** true Stingray DT and Makefile addition, USB0 gadget configuration, pin/reset/power/clock/CPCAP binding changes require scoping and separate review against a pristine upstream base. Current experimental DTS `tegra20-motorola-stingray-clean-usb.dts` is not a polished production DT. Add source patch candidates only from validated cause/behavior, not guesses.

**Lab-only userspace patch PHYSICAL PASS:** `patches/lab/0001-v062-broadcom-wcc-unload-order.patch` adjusts diagnostic `/init` to unload WCC before brcmfmac/brcmutil, does not patch Linux kernel C. v06.3 additional HCD and `iw` staging are **artifact/userspace dependencies**, not kernel patches. Proprietary firmware should NOT be committed.

**Future submission gates:** separate coherent commits on exact original Linux upstream; `git format-patch`, `git apply --check`, `git diff --check`, `scripts/checkpatch.pl`, actual ARM compile, DT binding checks, scope-specific negative controls and physical test; `scripts/get_maintainer.pl`, current MAINTAINERS, license/SPDX/author provenance, **actual contributor's DCO signoff**, explicit user approval before submission/email. No claimed external maintainer review or acceptance. Keep dated test checkpoint alongside each candidate.

---

## 12. Power/red-LED/USB condition: critical unresolved issue

The replacement MZ600 showed black display and **red camera-side LED when Power was pressed** after one v06.2 RAM boot attempt, despite high battery and without writing partitions. **Power + Volume Up** forced boot. Problem persisted after shutting down through **TWRP and stock Android**, so not exclusive to a Linux shutdown function; both could have inherited earlier state. TWRP read-only `pstore`/`last_kmsg` unavailable, DS2781 battery telemetry ~82–83%, 7.915 V, CPCAP power-key recognized. The user explicitly **unplugged BOTH external power AND USB before normal Power-button press**, after which **Power alone booted normally**. A later test of identical v06.2 image succeeded. This strongly supports an intermittent or state-dependent startup condition, but **does not establish USB backfeed, BCM shared rail fault or PMIC latch** because two connectors were disconnected together, and time elapsed. Motorola Power+Volume Up is a **forced reset, not known full electrical cold start**. Historical stock Xoom reports show similar symptoms. Do not disconnect internal battery, reset calibration EEPROM, force arbitrary voltage or assert safety latch on speculation.

If repeated, log USB/power/dock state, screen/LED and exact timing. Compare **both cables absent → USB-only → external-power-only → both**, with matched stock-Android power-off conditions, one variable at a time. Investigate Tegra USB0 UDC/OTG VBUS and CPCAP charger detection together with BCM4329 U4 shared rails and firmware state. The project needs a real evidence-gated regulator/pwrseq shutdown model, not blind register writes.

---

## 13. Recommended prioritized next tasks

**A. Immediate environment/documentation verification:** Read current checkpoints and this handoff. On Surface (connected Desktop Commander) check COM-port enumeration/ADB/fastboot state, read-only `PING`, `WIFI_STATUS`, `BT_STATUS`, `MMC2_STATUS`, `STATUS`; do not reboot stable Linux just to inspect. On Desktop check current branch/worktree, artifact manifests/hashes and effective `.config`; don't git-clean the intentionally dirty kernel DTS/ATAG. Update stale living status/README/start-here state references and link this handoff from documentation indexes.

**B. Finish standard Wi-Fi scanning:** Use staged official Debian 12 ARMHF `iw` plus runtime loader/libraries and `ip link set wlan0 up` equivalent in new reproducible RAM image; provide bounded USB scan or real on-device shell. Once built/verified and safely booted, perform **one scan** under real regulatory constraints, log error codes, nearby BSS privately and public counts/frequencies redacted. Then install `iwd` or `wpa_supplicant`/DHCP later to actually connect, with user's network credentials private.

**C. Bluetooth HCD + Motorola keyboard:** The **single-variable v06.3** with private HCD is ready but unbooted; test it on physical MZ600 with guarded `fastboot boot` **only after explicit user request and normal power preflight**, log firmware patch acceptance and safe BT_ON/OFF/STOP. Add BlueZ+agent, HIDP input path, passkey/pair, verify `/dev/input/event*`, actual keyboard keys, disconnect and reconnection. Keep bonding keys secure; RAM-only no persistence unless a user-approved backing store exists.

**D. User's next-build terminal:** Add a real visible framebuffer/VT terminal and ARMHF shell, keyboard input and keymaps with USB serial shell fallback, **not just decorative diagnostic screen**. The user explicitly wants to type commands on the Xoom if Bluetooth keyboard is working. Preserve current robust USB diagnostics and avoid hardware-only lockout. If new build combines iw+terminal+HCD, note multi-variable integration and keep prior images immutable.

**E. Full chip/coexistence and power:** Physically prove simultaneous Wi-Fi networking and BT keyboard; then OEM-equivalent shared U4 reference voting, WLAN U2 and BT U0/I7 reset states, wake U1/U6/U5, LPO/PMC clock, battery/USB effects, suspend/resume, clean normal Power restart. FM only if OEM driver/wiring evidence supports it. Continue tests on other Xooms only with correct product/DTB validation.

**F. Broader Linux installation:** Standard Debian rootfs, secure networking, input, display/brightness, battery/charging, audio, storage and eventual eMMC Linux primary system with documented Android rollback; **no persistent installation has been authorized** in the current phase. Track source changes as real patches all along.

---

## 14. Experiment acceptance template and common pitfalls

Every experiment should record: hypothesis + alternative explanations; exact upstream SHA, patch/source delta, effective compiled DTB, `.config`, private firmware hashes and toolchain; offline compile/ELF no-NEON/QEMU limited smoke test; target identity, power/USB/SD state; one non-destructive bounded operation; raw PRIVATE log + sanitized timestamped observable result; final module status/USB PONG and rollback; honest statuses (**built**, **offline hash verified**, **physically booted**, **driver probed**, **RF scan**, **network connected**, **Bluetooth paired**, **power-qualified**, **persistent install**). Historical negative trials remain part of the record. Do not infer hardware signal levels from source alone, do not conflate module unload with rail power down, do not mistake USB enumeration for PID1, and do not mistake official armhf iw QEMU version output for actual Xoom RF compatibility.

Useful references: GitHub `scripts/resume-state.sh`, `python3 tools/check_repository.py`, source/build manifests, branch/worktree lists and the private Surface logs. Do not push simultaneous conflicting branch changes or force-push main. Real kernel patch candidates must be retained when code is perfected and upstream submission must be deliberately requested by the user.

---

## 15. Exact links and hashes for quick follow-up

- [Repo branch](https://github.com/Olsens11/XoomLinux7/tree/wip/clean-wifi-bt-usb-20261025)
- [Upstream patch queue](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/patches/upstream/README.md)
- [MAC-ATAG RFC](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/patches/upstream/rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch)
- [WCC ordered unload lab patch](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/patches/lab/0001-v062-broadcom-wcc-unload-order.patch)
- [v06.2 Wi-Fi PASS](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_V062_WIFI_WCC_ORDERED_UNLOAD_PHYSICAL_PASS_2026-10-25.md)
- [v06.2 Bluetooth PASS](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_V062_BCM4329B1_BLUETOOTH_HCI_LIFECYCLE_PHYSICAL_PASS_2026-10-25.md)
- [iw staged / terminal plan](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_NL80211_ARMHF_IW_STAGED_AND_TERMINAL_PLAN_2026-10-25.md)
- [Red LED + USB/power condition](https://github.com/Olsens11/XoomLinux7/blob/wip/clean-wifi-bt-usb-20261025/docs/checkpoints/MZ600_TWRP_SHUTDOWN_POWER_BUTTON_FORCED_REBOOT_PHENOTYPE_2026-10-25.md)

**Boot image SHA256:** v06.1 `b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a`; **v06.2 current** `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`; **v06.3 offline** `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`. **Private HCD SHA** `7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`. **Official armhf iw .deb SHA** `fd1f6c926853505b0eb03a3afb4c6b68e4350f42b140fe6c5295012eeca872ee`.

**Final reminder to the next agent:** Native Linux 7 v06.2 **works now** as USB/PID1 and standard separate Wi-Fi/Bluetooth hardware interfaces; both have been brought up and down cleanly; Wi-Fi also restarted successfully after Bluetooth in the same session. The next step is **real network scanning and a keyboard-driven on-screen terminal**, while validating private HCD and whole-chip power/coexistence using controlled experiments. Never flash or use the protected original Xoom; preserve exact working images, source patches, private firmware provenance and intermittent USB/charger/red-LED history.