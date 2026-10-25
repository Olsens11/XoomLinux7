# Motorola Xoom MZ600 / BCM4329 — comprehensive breakthrough milestone and native OS handoff
**Milestone date:** October 24, 2026  
**State:** PHYSICAL native WLAN interface breakthrough / OFFLINE native Linux OS build PASS / PERSISTENT INSTALLATION NOT PERFORMED  
**Primary purpose:** This is the project-preservation document. Read it first after a conversation transition, before selecting further experiments, touching a tablet, preparing an OS image, or contacting upstream.

> **Top-line breakthrough:** Linux 7 and the stock BCM4329 hardware on the **replacement Motorola Xoom MZ600** successfully produced native `wlan0`. We found **two independent software blockers**: (1) removal of Motorola’s firmware *bootstrap MAC field* had caused wireless-side firmware initialization to fail and SDIO F2 readiness to time out; (2) our minimal diagnostic environment lacked the required separate upstream Broadcom WCC plugin. A controlled 26-byte NVRAM-only experiment changed F2 from `-62` to `0`, and an experimental inlined *upstream* WCC provider then allowed `wlan0`. We are transitioning that proof to an ordinary Debian ARMhf Linux installation with **dynamic per-device MAC identity**, modular WCC, and standard USB login. Android preservation and reliable switching back are explicit requirements. **No permanent installation, Android partition replacement, RF association, or hardware modification has occurred.**

## 0. Evidence legend and what must not be overstated
- **PHYSICAL PASS / FAIL:** returned by the replacement Xoom's real USB diagnostic interface or kernel logs.
- **SOURCE-VERIFIED:** inspected OEM/mainline code or board specification; does not, by itself, prove a particular bootloader/runtime condition.
- **OFFLINE PASS:** compiled/built, hash-verified, inspected by build-host tools; **not a physical boot or connected-radio acceptance test**.
- **UNVERIFIED:** pending test. Distinguish *WLAN interface creation* from real identity, RF, regulatory, scanning, association, DHCP, coexistence and sustained performance.
- **Do not retroactively interpret** a healthy PMU snapshot as a sampled electrical voltage waveform, `arm_up=1` as an instruction-pointer trace, or a pointer into RAM as proof that every NVRAM field was accepted. The v041 message-trace `0` pointer was incorrectly classified as valid because SOCRAM starts at zero; v042 corrected it to NULL.
- **No invented hardware identity.** Real replacement-Xoom factory MAC address, serialized calibration, Wi-Fi credentials, passwords and proprietary firmware stay private; no generic production MAC may be copied from another device or OEM reference image.
- The user's explicit hardware constraint: **no additional capacitors or any hardware components**. OEM hardware works; this is a software bring-up and OS development project.

## 1. Source and machine map — where to resume
| Subject | Canonical location / reference |
| --- | --- |
| Project GitHub | https://github.com/Olsens11/XoomLinux7 |
| Accepted integration state | `main` branch; do **not** merge experimental changes without a documented gate |
| BCM4329 historical research | `research/bcm4329-oem-lifecycle-trace-20261024` |
| Normal OS workstream | **`os/mz600-native-rootfs-wifi-20261024`** — branch carrying this report |
| Kernel upstream | https://github.com/xoom-linux/linux at `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` |
| Kernel ABI | `7.0.0-next-20260422`, ARMv7 Cortex-A9 (Tegra 2), no NEON |
| Development desktop WSL | `/home/xoomdev/xoom-linux-rom` (Ubuntu 22.04 under Windows) |
| Canonical build source | `/home/xoomdev/xoom-linux-rom/linux-src` |
| Clean OS output | `/home/xoomdev/xoom-linux-rom/os-build/kernel` and `os-build/artifacts/` |
| Staged Debian root | `/home/xoomdev/xoom-linux-rom/os-build/bookworm-armhf-root` |
| Private first-boot credentials | `/home/xoomdev/xoom-linux-rom/os-build/private/xoom-firstboot-login.txt`, owner-restricted **0600**, do not publish |
| OS branch desktop worktree | `/home/xoomdev/xoom-linux-rom/os-build/xoom-os-repo` |
| Surface Book 2 | Windows, USB serial diagnostics COM9 for temporary v034 boot; COM number not guaranteed for normal OS |
| Raspberry Pi | `/home/ps2/xoom-phase1`, OEM/recovery evidence and original private image extracts |
| Original protected Xoom | Separate recovery/toolkit device: **do not perform OS partition tests on it** |
| Experimental replacement Xoom | The only tablet on which v040–v045 and future OS validation may take place |

Read [repository guardrails](../../AGENTS.md), [START_HERE](../../START_HERE.md), [current status](../status.md), [state variables](../../runtime/PROJECT_STATE.env), [physical WLAN v042–v045 checkpoint](V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md) and [offline native OS build checkpoint](NATIVE_OS_OFFLINE_BUILD_PASS_2026-10-24.md) before executing device commands. The first two project files may contain earlier `v020` or diagnostic-era snapshot language; **this milestone supersedes older assertions that F2 is universally unresolved**.

## 2. Actual hardware and shared-chip layout
- Model: Motorola Xoom **MZ600 Stingray**, Tegra20. Device Tree was derived from the upstream **Wingray** reference; variant differences matter.
- Integrated Broadcom **BCM4329 / CYW4329 revision 3**: Wi-Fi over SDIO; Bluetooth over HCI UART; shared internal PMU and core resources. Not a standalone Wi-Fi-only chip.
- Wi-Fi host is **Tegra SDMMC2**, `c8000200.mmc`, identified as Linux **`mmc2:0001`**; other eMMC storage controller is **SDMMC4** (not WLAN).
- The chip enumerated SDIO functions and responded over F1 throughout the failing tests. Firmware F2 enable was `IOEx: 0x02→0x06` and `IORx: 0x02→0x02` during failure, returning `-ETIME (-62)` after about three seconds.
- In the MZ600 board's Linux DT, `reg_wifi_vdd` is nominal switched 3.3 V with active-high GPIO **U4** (sourced by `vdd_3v3_sys`); `VWLAN1` 1.8–1.9 V is from Motorola **CPCAP** and is used for SDIO I/O; **U2** is Wi-Fi reset; Tegra PMC LPO used for the 32.768 kHz low-power clock. Do not conflate GPIO control, a regulator framework vote or a PMU resource register with measured electrical waveforms.
- OEM whole-chip rules matter. Motorola's `change_power_brcm_4329()` uses shared reference-counted U4 power gating; BT shutdown and WL_REG_ON / BT_REG_ON interactions were researched. These remain relevant when enabling Bluetooth and suspend/coexistence, but **were not the cause proven by the controlled v044 fix**.
- Source references: [Motorola OEM lifecycle and callgraph](../research/MOTOROLA_BCM4329_OEM_CALLGRAPH_TRACE_V3.md), [BCM4329 datasheet 149-page index](../research/BCM4329_DATASHEET_PAGE_INDEX.md), [datasheet compliance audit](../research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md). Use original datasheet for specific 110 ms-after-VDDC-settled contract; those timing constraints are *not* a reason to add hardware.
- The proven USB0 variant source `tegra20-motorola-stingray-usbdiag.dts` switches USB0 to Tegra UDC **peripheral** mode. Its filename includes `usbdiag` for historical reasons; the OS keeps only the correct USB hardware DT setting, **not** the original diagnostic userspace program.

## 3. Diagnostic history before the breakthrough
| Revisions | Hypothesis / experiment | Physical outcome |
| --- | --- | --- |
| v01–v06 | Core ARMv7/Linux startup; framebuffer and Atmel maXTouch touchscreen; USB CDC, touch grid/crosshair mapping | Temporary Linux boot, USB, touchscreen and display support demonstrated |
| v07–v013 | Native brcmfmac, various Broadcom firmware/NVRAM, SDIO high-speed/CCCR behavior | Chip detected; F2 timed out; no `wlan0` |
| v014 | USB diagnostic module load/unload | USB control worked; canonical TTY transfer corrupted binary upload |
| v015 | Raw TTY and CRC-checked firmware and module upload | Verified high-integrity transient diagnostic transport; F2 still `-62` |
| v016–v020 | SDIO IOEx/IORx instrumentation, OEM six-field SDIO capability override, AUTO/MOTOROLA capability switching, 25 MHz clock, card reinit | Correct settings often became physically effective, yet **F2 still failed** |
| v021–v026 | Firmware/NVRAM provenance and packed variables, PMU/LPO availability, host timing and 300-ms pwrseq, virtual fault-model checks | Transfer and staging verified, F2 failed; **Linux device-specific MAC callback unavailable** was recorded but its significance not yet recognized |
| v027–v034 | Integrated Wi-Fi/BT shared-chip lifecycle and UART HCI, GPIO reset/clock, firmware execution attempts | BT on/off worked; v034 repaired `HCIDEVDOWN` argument ABI (index by value, not pointer); WLAN F2 remained unsolved |
| v035–v037 | PMU/resource/CM3 handoff and SDPCM mailbox read-only instrumentation | ALP/HT and resource snapshots and SDPCM mailbox write returned success, but F2 still failed |
| v038 | Hold actual SDMMC2 host runtime PM active over firmware and F2 callback | `pm_runtime_resume_and_get() rc=0`, reference held, release balanced; **F2 still -62** |
| v039 | Replace only generic firmware with authenticated original MZ600 HRI39 January 2011 `fw_bcm4329.bin`, same NVRAM and driver | Correct OEM bytes transferred, **F2 still -62**; exact generic firmware restored |
| v040–v041 | Cortex-M3 core and SOCRAM token/shared header observations | Correct NVRAM token at RAM tail; core released; firmware published valid SDPCM shared pointer/version 3; F2 still failed |
| **v042–v043** | Read only verified firmware shared structure and console ring | **Recovered actual firmware initialization failure `err: 21`** |
| **v044** | Change **one variable:** append Motorola authentic generic `macaddr` bootstrap line, no other changes | **F2 READY, return `0`**, then separate WCC missing-module failure |
| **v045** | Link unchanged upstream WCC vendor operations into RAM-only test module | **Native `wlan0` PRESENT** on physical replacement Xoom, no RF operations |

Negative results are evidence and remain archived. In particular, do not re-try low clock, runtime-PM awake, simple OEM firmware substitution, adding random NVRAM `keep_img` / `clkreq` / `sd_rxreg` / `sd_txreg`, regulator rewiring or guessed MACs as if these were untested. A proposed `sdhci.debug_quirks=0x40` is **BROKEN_ADMA**, not low-speed clock gating; never mistake it for a frequency control. Details: [v038](V038_MMC2_RUNTIME_PM_HOLD_PHYSICAL_2026-10-24.md), [v039](V039_ORIGINAL_MZ600_FW_PHYSICAL_2026-10-24.md), [power investigation](../research/MZ600_BCM4329_STARTUP_RAIL_DROOP_AUDIT_2026-10-24.md).

## 4. Firmware execution evidence — exact observed addresses, limits and interpretation
v040/v041 proved that the Broadcom Cortex-M3 did more than simply exit reset:
- SOCRAM base **`0x00000000`**, size **294,912 bytes / 288 KiB**.
- NVRAM packing is **672 bytes** from a 1,550-byte prepared plain-text reference. **Before** reset release, last 4 SOCRAM bytes read back the correct size-and-complement token; after F2 timeout the last word changed to an aligned in-range shared-memory pointer.
- Core state `arm_up` read **0 before** reset release and **1 after**; still **1** at failed F2 wait. This reports wrapper/reset-state, not the instruction pointer.
- SDPCM shared structure flags first 4 bytes: **`03 00 00 00`** (version 3), trap/assert bits clear at snapshot.
- v042 exact shared pointer **`0x0002B134`**, above lower 128KiB (≈172KiB offset), **not** a magic-header `bcma sh_info` structure.
- Console struct pointer **`0x00046A54`**; console ring buffer **`0x0004664C`**, length **1024 bytes**, write index **242**; valid bounded read of 128 bytes showed 122 printable bytes and 3 newlines.
- Msgtrace pointer at shared-header offset +24 **`0x00000000`** (NULL). v041 erroneously labeled it "in RAM" because RAM started at zero; v042 corrected this.
- v043 bounded 256-byte firmware console excerpt reported:
  
  `RTE (SDIOCDCIR) 4.220.48 on BCM4329 r3 @ 38/80/80 MHz`  
  `sdpcmdcdc0: Broadcom SDPCMD CDC driver`  
  `reclaim section 0: Returned 35055 bytes to the heap`  
  **`Failed to init wireless side, err: 21`**  
  `reclaim section 1: Returned 22674 bytes to the heap`

This console is a device-observed, internal firmware symptom. A contemporary open-source Broadcom `brcmsmac` attaches `err=21` to missing `macaddr` in `wlc_bmac_attach`, but the closed BCM4329 firmware error-code table is not independently proven byte-for-byte identical. The **one-variable v044 F2 success** provides the much stronger causal evidence.

Raw logs, proprietary bytes and possible MAC values were retained only on private developer machines, not committed to GitHub. Detailed report: [v042–v045](V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md).

## 5. Definitive two-step native Wi-Fi fix
### Problem A — bootstrap MAC missing before firmware starts
Motorola source documents that an initial **default MAC address must exist in OTP or NVRAM for BCM4329 firmware bring-up**. After initialization its board callback `get_mac_addr` supplied the **per-device** identity derived from private OEM `ATAG_STINGRAY_MAC = 0x57464d41`. Original HRI39 and HRI66 `/system/etc/wifi/bcm4329.cal` both contain the **same** valid, unicast default `macaddr`; that **is a common bootstrap value**, not proof of the replacement Xoom's unique factory address.

Our modern 1,550-byte baseline NVRAM was deliberately stripped of `macaddr`, `ccode` and `regrev` pending provenance. The CRC32 of the exact plain-text baseline is **`FAFCC93A`**, SHA256 **`a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`**. Packed size is 672 bytes.

**v044 controlled PHYSICAL trial:** append *exactly one 26-byte* `macaddr=...` line from a verified original Motorola calibration to that identical baseline. Trial NVRAM length **1576** bytes, CRC32 **`DFC494F0`**, SHA256 **`e53cd5312000a7a099e7d14930164eb0e9cf865fa1f8d786e6cbee959c430d94`**. No other NVRAM, firmware, GPIO, clock, board or kernel setting changed. **F2 enable returned `0`**, where unchanged calibration repeatedly returned **`-62`**.

The ordinary host-side uploader intentionally prohibited identity-bearing files. A one-off local *exact-size and SHA-pinned* exception was created for the single experimental file, while retaining all country-code/regrev restrictions; **that exception was deleted**, standard guard restored, and the normal MAC-free NVRAM uploaded again after test. Never carry the exception into production.

### Problem B — WCC plugin absent in minimal diagnostic initramfs
After F2 became ready, the driver hit **`brcmf_fwvid_request_module: mod=wcc: failed -2`** and **`brcmf_attach: brcmf_fwvid_attach failed`**. This is Linux-side missing module loading (`-ENOENT`), separate from firmware F2.

**v045 PHYSICAL trial:** link the *unchanged upstream* `wcc/core.c` vendor operations into the experimental `brcmfmac.ko`, bypassing external module request in the temporary bare initramfs. With the same authentic bootstrap NVRAM, USB status reported **`WLAN0 PRESENT`** and kernel logged **`brcmf_net_attach wlan0: Broadcom Dongle Host Driver`**. No scan/association/DHCP was attempted.

**Clean OS implementation** instead installs/upstream-loads the **separate** `brcmfmac-wcc.ko`, plus `brcmfmac.ko` and `brcmutil.ko` and their module-dependency database; it does not ship v045's inline workaround or `XOOM_V0xx` diagnostic hooks.

### Generalized dynamic factory-MAC solution
Linux 7's pinned `brcmfmac/firmware.c` already calls `eth_platform_get_mac_address()` before packing NVRAM. If `/mmc@c8000200/wifi@1` contains a legitimate six-byte `local-mac-address` property, upstream code can insert that device-specific value into the chip's NVRAM **before MCU firmware release**, exactly the formerly missing step.

The sole targeted clean kernel patch is [ATAG-to-FDT conversion](../../patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch). It translates Motorola's vendor bootloader `ATAG_STINGRAY_MAC` to `local-mac-address` on the real SDMMC2 child at early normal boot, rejecting invalid/multicast/unprogrammed values. The OS `mz600-wlan.service` checks the property before loading the normal Wi-Fi modules; generic NVRAM has **no baked-in MAC** and no regulatory overrides. This is intended to work on *every* appropriately booted Xoom with its own factory address, not only the development tablet.

**NOT YET PROVED PHYSICALLY:** the replacement Xoom's ordinary bootloader actually passes that Motorola tag to our modern appended-DTB converter at power-on. A pre-existing FDT or missing vendor ATAG could bypass conversion; failing closed is correct. Do not declare production MAC restoration complete until observed on the device without disclosing its address. A stock bootstrap-only MAC in the generic OS image is **not an acceptable fallback** for normal radio use.

## 6. Wi-Fi, Bluetooth and mechanical source safety boundaries
- The accepted v034 HCI fix was a *userspace ioctl ABI* correction: `HCIDEVDOWN` receives HCI device index by value, not an int pointer. v034 produced `BT_OFF rc=0` and unloading BT modules after `BT_STOP` released the shared U4 vote. It was not a change to Bluetooth controller ROM and should be preserved as a known source lesson.
- Motorola's shared WL_REG_ON, BT_REG_ON, U4, U2, BT shutdown and reset-order semantics must be honored for coexistence; **do not conflate** independently running WLAN/BT power with the combined chip's actual POR. This did not need speculative modifications for v045's success.
- The replacement Xoom is the only target for system OS development. The separate original Xoom hosts the extensive TWRP recovery/toolkit project and **must remain untouched**.
- Source-only experiment builders temporarily modified exact SHA-pinned kernel files for `brcmfmac` observers, then restored them byte-for-byte. All returned module hashes, USB upload CRCs and final driver unload states are documented in [v040/v041](V040_V041_CM3_NVRAM_SHARED_STRUCTURE_PHYSICAL_2026-10-24.md) and [v042–v045](V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md).
- No hardware or regulator change has been made; no capacitor installation is authorized or part of the solution.

## 7. Exactly qualified original Wi-Fi artifacts, in private storage
| Artifact | Size | SHA-256 / CRC32 |
| --- | ---: | --- |
| Generic Broadcom 4.220.48 firmware `brcmfmac4329-sdio.bin` | **253,748 bytes** | SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`; CRC32 `B4092AA6` |
| Baseline MAC-free `brcmfmac4329-sdio.txt` | **1,550 bytes** | SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`; CRC32 `FAFCC93A` |
| Packed firmware NVRAM | **672 bytes** | CRC32 `596925B1` |
| Original Motorola Jan 2011 4.218.248.20 firmware (v039 negative comparison) | **261,317 bytes** | SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a` |
| MAC-only v044 private experimental NVRAM | **1,576 bytes** | SHA256 `e53cd5312000a7a099e7d14930164eb0e9cf865fa1f8d786e6cbee959c430d94`; CRC32 `DFC494F0` |

The published repo contains only the safe 1550-byte plain-text calibration, e.g. [`configs/os/brcmfmac4329-sdio.stingray-calibration-no-identity.txt`](../../configs/os/brcmfmac4329-sdio.stingray-calibration-no-identity.txt), and scripts/hashes—not firmware binaries, MACs, proprietary patched controller data, or credentials.

## 8. Clean OS baseline — completed, VERIFIED OFFLINE, **not installed**
- **Userspace:** Debian Bookworm ARMhf (ARMv7 hard-float; does not rely on nonexistent Tegra2 NEON), built via two-stage debootstrap in Ubuntu 22.04 WSL with QEMU-assisted second stage.
- **Kernel:** upstream-pinned Linux `7.0.0-next-20260422`, clean separate output directory; no built-in custom diagnostic rootfs; `CONFIG_BRCMDBG` disabled; all established board drivers retained including framebuffer/display, Atmel touch, SDIO, eMMC, CPCAP and USB. The original source file was restored to its pinned SHA256 after boot-MAC patch compilation.
- **USB:** Tegra USB0 UDC/peripheral DTB, `CONFIG_USB_G_SERIAL=y`, standard Debian `serial-getty@ttyGS0.service`, a locally provisioned owner account with unique private first-login password (private WSL file 0600). New OS gadget might use a different host COM number than v034 COM9. USB *systemd login* is **not physically tested**.
- **Wi-Fi:** exact verified firmware and MAC-free calibration, stock clean `brcmfmac.ko` + `brcmutil.ko` + separately packaged upstream `brcmfmac-wcc.ko`, normal `modules.dep`. The OS refuses Wi-Fi startup without verified local-mac-address.
- **Normal boot:** Debian `/sbin/init` rather than diagnostic PID1. Native ext4 filesystem, not a general emulated OS. SSH package is present but is not needed for USB access or connected/approved networking.
- **Offline checks:** Android-format `ANDROID!` header, full kernel+USB-DTB bytes in boot image, expected root command line, zero embedded diagnostic ramdisk, BCM4329 DT child, no static MAC, compiled ATAG translator, SHA-checked firmware/NVRAM, separate WCC, no `XOOM_V0xx` tracer, USB getty, first-login account, actual ext4 packaged inodes and clean `e2fsck -fn` all PASS.
- **Candidate files:** in Desktop WSL `/home/xoomdev/xoom-linux-rom/os-build/artifacts/` (UNINSTALLED):
  
  | Candidate | Byte length | SHA256 |
  | --- | ---: | --- |
  | `xoom-linux-system.ext4` | **805,306,368** (768 MiB) | `398e0991700bb1769a8d8fa01fd50b96970d9f6e4dfe7d08952a78b6ff151bb8` |
  | `xoom-linux-boot.img` | **5,890,048** | `ba50d08165376724236e959cc19e6ca8de781b488748a221b2a9bc3b48fa9967` |
  | `zImage` | — | `7174bd220b2466b695f03363832e4158899d0caca917a782903268868e07ccc7` |
  | `tegra20-motorola-stingray-usbdiag.dtb` | — | `afae7fb328bc66c0ea186ef6c8e77164c41be8588bb5d14303374a3545499959` |
  | Clean `brcmfmac.ko` build intermediate | — | `39b83c8cdded5e585c6d886df89a3c01328adf928f0798db692c63c71d152f9f` |
  | Clean `brcmfmac-wcc.ko` build intermediate | — | `740cfea66bb4eb9e7f4faab906ae4fd23ab4f6fe6b7375712773bb8610e38e7f` |

**CRITICAL ARTIFACT WARNING:** The existing 2026-10-24 boot-image candidate has `root=PARTLABEL=system` and its rootfs image was packaged assuming it would *replace* the original Android system partition. This contradicts the later Android-preservation decision. **It must NOT be flashed or installed as-is.** The *payload*, compile methodology and offline QA are valuable; produce a **new boot image targeting a verified separate Linux-only root partition** after that device/partition exists. Distinguish the current artifact's checksum from future versions.

## 9. New required architecture — preserve Android rather than overwrite it
User clarified a preference for a **standard Linux install** and the ability to switch back to Android while preserving Android's files. That is now a higher-priority design requirement than the old `system`-replacement proposal.

### Why not simply copy a second OS into existing `/system`?
- The Android `system` partition is an ext4 filesystem but already contains **Android's own `/bin`, `/etc`, `/lib`, `/system`-style layout**, depending on Android generation. Installing Debian's root directories in that same filesystem root risks overwriting names and breaking Android. It is not a conventional independent OS deployment.
- Placing Debian under e.g. `/system/linux` would preserve names but the kernel cannot simply mount a subdirectory as the independent root using only a different `root=` block-device argument. It requires initramfs staging / mount namespace / `switch_root` or similar indirection and gives both OSes a shared failure domain. **This is a possible fallback, not the preferred standard baseline.**
- A dedicated filesystem partition lets Linux mount its own ext4 **directly** with normal kernel `root=PARTUUID=...` / `root=PARTLABEL=...`, normal `/etc/fstab`, normal init, ordinary upgrades and clean isolation from Android. Reference: [Linux kernel root command-line documentation](https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html).

### Preferred deployment priority
1. **Independent Linux ext4 root partition on internal eMMC** *if* the **replacement unit** has an explicitly verified safe spare slot or an approved, fully backed up partitioning plan that does not destroy Android data. Do not presume such space exists or resize partitions casually.
2. **Dedicated Linux ext4 partition on microSD** if internal repaving is unsafe or undesirable. Linux remains a conventional directly mounted filesystem, even though the root device is removable. Verify bootloader/kernel card detect, reliability, root-device identity, and absence of conflicts with storage paths.
3. Only if the user later specifically chooses it: Linux filesystem *image file* under existing Android ext4 `userdata` or `system` with a minimal initramfs loop-mount stage. This is less standard and can fail on encryption, free-space, or mount assumptions. Do not use it by default.

### Boot selection and Android return
The Xoom is a legacy single-boot-slot design in our current evidence. **Do not promise** a modern A/B slot toggle, a GRUB-style selector, kexec, or a functional local boot menu until physically demonstrated. Separate Android and Linux **boot images** are needed, and the bootloader has to select one: e.g. via a proven vendor boot choice, an approved boot-manager mechanism, or by restoring the backed-up Android boot image. Booting Linux does **not** by itself erase Android. Replacing a `boot` image is a **persistent write** even if Android's `system` and `userdata` are untouched, so it requires an explicit per-partition user approval, exact image/partition/hash check and tested rollback method.

A Linux root in a separate partition cannot be installed safely until the replacement device's **actual GPT, free space, encryption, filesystem integrity and device identity** are determined read-only. The recovery project's historical **BigPart/noBigPart** notes refer to a **different/original Xoom**; never transfer those dimensions to the replacement unit without verifying that unit. The current `system` image and previous boot target are **OFFLINE TEST ARTIFACTS**, not approval to overwrite Android.

### Protection requirements
- Do not format, mount read-write, repartition, rename or overwrite `boot`, `system`, `userdata`, `recovery`, bootloader, or the original Xoom without explicit scoped authorization.
- Make externally stored, byte-verified backups of any partition that might be modified. A boot-image swap can switch Linux/Android **only if the Android boot image remains intact/accessible**; root data and apps will be unaffected if their partitions are untouched.
- Keep TWRP recovery and its separate recovery partition untouched unless a separate future task explicitly concerns it.
- Be prepared for USB getty path not yet tested; preserve a fallback and restore instructions **before** changing boot partition.
- **Never** use the previous `root=PARTLABEL=system` binary in an Android-preserving installation. Rebuild for a verified Linux-only root target and update `fstab`, packaging scripts, test cases and SHA manifest to match.

## 10. Exact final device state after the physical Wi-Fi experiments
Following v045:
- `WIFI_STOP` returned success unloading `brcmfmac` and `brcmutil`.
- Exact original **1,550-byte MAC-free NVRAM** restored by the guarded standard uploader: **`UPLOAD DONE SIZE 1550 CRC32 0xFAFCC93A`**.
- Original host uploader identity/regulatory override guard left intact; the one-off exact-hash test uploader was deleted.
- Staged experimental `brcmfmac` module restored to prior **v043** 465456-byte diagnostic build, upload CRC32 **`67BA0C62`**, but modules **unloaded**.
- Read-only `MMC2_STATUS` reported **TARGET VALID**, **BOUND YES**, **BCM4329 VERIFIED**, **AUTO 0**, drivers unloaded, COM9 responsive. Original temporary v034 diagnostic kernel remains on the replacement device (not a normal OS install).
- No user credentials, MAC, Wi-Fi connection, radio regulatory values, partition bytes or hardware components were changed on the device.

## 11. Pending verification matrix — next stage, without losing ground
| Gate | Needed evidence | Current state |
| --- | --- | --- |
| Android preservation | replacement-unit *own* GPT, block-size, filesystem and free-space inspection; confirm no changes to Android data | **NOT DONE** |
| Linux root location | dedicated independent GPT/ext4 root device, external microSD or safe eMMC plan | **UNDECIDED** |
| Clean OS boot image | regenerated for **non-Android** root selector; no system/data overwrite | **NEEDS REBUILD** |
| Dynamic MAC | replacement bootloader actually sends Motorola `ATAG_STINGRAY_MAC` or equivalent per-device immutable source into FDT | **NOT PHYSICALLY VERIFIED** |
| Identity quality | unicast, unique same-unit MAC; calibration/regulatory provenance privately validated | **NOT QUALIFIED** |
| Modular WCC | matching separate WCC vendor module loads through ordinary kmod and attaches | **OFFLINE BUILD PASS**, physical normal-OS test pending |
| Native Wi-Fi | F2=0, actual unique MAC, native wlan0 under clean OS | **v045 PHYSICAL proof with generic bootstrap, production untested** |
| USB | standard Linux `ttyGS0` getty and user account from normal boot | **OFFLINE PASS**, physical test pending |
| Graphics/input | display and touch preserved after root filesystem migration | **Previous diagnostic physical tests, native OS pending** |
| Bluetooth | HCI, shared power votes, coexistence and reset sequencing on clean OS | **Diagnostic proof / native OS pending** |
| Boot selection | switching safely from Linux back to original Android without system/data change | **NOT IMPLEMENTED** |
| Recovery | authenticated tested boot-restore path, off-device backups and non-destructive fallback | **NOT YET ACCEPTED** |
| Upstream contribution | small upstream-quality DT/ATAG and WCC integration, normal boots/repeatability | **Draft only; nothing sent** |

Avoid asserting a solved Wi-Fi service solely from `wlan0` creation; release acceptance requires cold/warm reboots and verified identity, USB and network behavior.

## 12. Source and artifact preservation index
- Physical v040–v041 [NVRAM token, ARM core and v3 shared header](V040_V041_CM3_NVRAM_SHARED_STRUCTURE_PHYSICAL_2026-10-24.md).
- Physical v042–v045 [exact console text, two-step WLAN fix and rollback](V042_V045_NATIVE_WIFI_BRINGUP_2026-10-24.md).
- Offline [clean kernel and Debian armhf root image/checksum report](NATIVE_OS_OFFLINE_BUILD_PASS_2026-10-24.md).
- [Native OS implementation plan](../os/NATIVE_OS_INTEGRATION_2026-10-24.md).
- [OEM source call graph](../research/MOTOROLA_BCM4329_OEM_CALLGRAPH_TRACE_V3.md) and [datasheet index](../research/BCM4329_DATASHEET_PAGE_INDEX.md).
- [Current installed-OS kernel builder](../../scripts/os/build-clean-kernel.sh); [module installation](../../scripts/os/install-kernel-modules.sh); [rootfs staging](../../scripts/os/configure-rootfs.sh); [old `system`-targeting offline packager—must revise](../../scripts/os/package-native-os.sh); [offline image QA](../../scripts/os/verify-offline-native-os.py).
- [Motorola MAC→FDT early boot patch](../../patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch); [MAC gate script](../../scripts/os/check-factory-wlan-mac.sh); [module load service](../../configs/os/mz600-wlan.service); [identity-free NVRAM](../../configs/os/brcmfmac4329-sdio.stingray-calibration-no-identity.txt).
- Experimental v042/v043/v045 builders are on the research ancestor branch and in the OS branch history, **not part of production OS**.
- Host SHA256 manifests and uninstalled binaries remain on user's WSL desktop; GitHub contains source, procedures and public hashes but no binary firmware and no credentials. If moving work between machines, verify hash and use appropriate private transfer methods.

## 13. Restore/rollback requirements
Before any permanent installation: verify that the tablet is the *replacement* MZ600, power/battery/USB stable, exact boot/system/data/GPT sizes and GUIDs, recovery backup, firmware hashes, correct kernel boot-image header, and that the host has working tools for recovery and USB. Back up the **current Android boot image** (and any partition proposed for modification) to a trusted off-device volume and verify read-back hashes; merely keeping a copy on the same eMMC is insufficient.

If a future Linux boot fails, restore the **original Android boot image** through a separately confirmed safe bootloader method and reboot Android; preserve Android's `system`/`userdata` so restoring the boot image is sufficient in principle. If bootloader/custom-boot behavior prevents that, the recovery path needs explicit testing before installing anything. Do not use a Linux install plan requiring formatting Android partitions as the fallback.

The previously qualified v034 temporary USB diagnostic environment is useful for hardware investigation but is **not** the normal OS or a boot manager. Do not mistake it for an installed dual-boot solution.

## 14. Upstream contribution plan and intellectual honesty
Potential upstream target: [xoom-linux/linux](https://github.com/xoom-linux/linux). We would like to contribute the **generalizable** per-device MAC handling and minimal module-packaging lessons. Maintainership outreach is **not sent**.

A future upstream issue/PR should present: (a) reproducible original error `IOEx=06, IORx=02, F2=-62`; (b) **firmware console** `Failed to init wireless side, err: 21`; (c) one-field Motorola OEM bootstrap MAC causing F2=0; (d) independent WCC module loader fault `-2`; (e) physical `brcmf_net_attach wlan0` when WCC vendor support is available; (f) normal-OS dynamic factory MAC mechanism once proven; (g) repeated boot/identity/USB/coexistence qualification; and (h) a minimal code patch, not the giant experimental debug history. Keep OEM firmware bytes, private MACs, raw console logs, private auth data and credentials out of public contributions.

The drafted communication is [here](../os/UPSTREAM_CONTRIBUTION_DRAFT.md). Neither mainline project nor xoom-linux maintainer has yet been contacted.

## 15. Non-negotiable project continuation checklist
1. **Start with this document and the linked v042–v045 physical report**, not early false diagnoses. Treat `wlan0` as PHYSICAL PASS *only for the v045 temporary-boot trial*.
2. Preserve *both* original Android systems' file data and partitions by default. Do not flash the legacy `root=PARTLABEL=system` image or rename/reformat existing filesystem roots.
3. Reconcile the new preferred root strategy: **dedicated Linux partition first; microSD ext4 second**. Inspect replacement tablet's GPT, available space, card capability and encryption read-only. Decide precise root selector and boot choice *from evidence*.
4. Update the packager, `fstab`, verifier, root partition label, boot image and hashes **without writing to device**.
5. Before a persistent boot-image change, create verified original Android boot backup and prove rollback. **Explicit permission for a specific target partition** is still required.
6. On first approved normal-OS boot, check USB gadget login and exact per-device MAC source **before** Wi-Fi scan/association. The MAC gate must fail safely if unavailable.
7. Qualify normal Linux userspace, kernel modules, upstream WCC, dynamic MAC, F2 readiness, `wlan0`, display/touch, BT shared power, cold/warm reboot and eventual networking.
8. Publish the minimum portable fix to the upstream maintainer **after** physical normal-OS acceptance, respecting license/provenance/security constraints.

**Permanent milestone status:** **BCM4329 native WLAN device-interface breakthrough achieved; no stock hardware modification needed.** Clean Debian/Linux 7 OS built offline. **Android preserved, future dual-boot design pending**, no eMMC write and no boot-manager feature claimed.
## 16. Later same-day acceptance update — Android-preserving package rebuilt (authoritative current files)

After the full history above was committed, the normal-OS packager was corrected and **actually rerun offline** for the user's desired preserve-Android architecture. This is a new *offline build*, **not** an installed or reboot-tested device.

- Older `root=PARTLABEL=system` boot/system images were **independently hash-checked and archived under** `os-build/archive-rejected-android-system-root-target/`, with an explicit rejected/do-not-install marker. They are *historical evidence*, not deployment candidates.
- `configs/os/fstab` and the kernel boot-image cmdline now target **`PARTLABEL=xoom-linux`**. The packager explicitly rejects Android's `system`, `userdata`, `data`, `cache`, `boot`, `recovery` and `misc` as target root names.
- A new 768MiB ext4 root was packed and named **`xoom-linux-root.ext4`**, deliberately **not** `xoom-linux-system.ext4`. The rebuilt boot image's root argument is `root=PARTLABEL=xoom-linux rootfstype=ext4 rootwait`.
- **Latest correct offline hashes:**
  
  | File under Desktop WSL `os-build/artifacts/` | SHA256 |
  | --- | --- |
  | `xoom-linux-boot.img` (5,890,048 bytes) | `40e32a9806183482b3e440ce493e505d9fa32b6f4c9dde9364f528b1b55c6756` |
  | `xoom-linux-root.ext4` (805,306,368 bytes) | `0aafdddccf58c5259007f272fb7878c417006629f5cb678c6d5e0f361ef8376e` |

- A full offline acceptance suite, including root cmdline, fstab, boot image payload, ARM FDT Motorola MAC translator, USB0 UDC, standard USB login, separate upstream WCC, privacy-free 1550-byte calibration, packed filesystem inodes, SHA hashes, and `e2fsck -fn`, returned **`NATIVE_OS_OFFLINE_ACCEPTANCE_PASS`** again after the rename.
- **No matching new Linux partition has been created or verified.** Do not try to boot the image until a separate GPT filesystem can be safely provisioned without Android damage and the boot-selection/restore method is established. All tablet partitions remain untouched.

For exact updated script/hash evidence see [Android-preserving image rebuild](ANDROID_PRESERVING_NATIVE_OS_OFFLINE_REBUILD_2026-10-24.md). This section **supersedes only** the old `root=system` paths/hashes in Section 8; all v040–v045 physically measured evidence and analysis above remain unchanged.

## 17. Latest recovery-to-Android touchscreen and factory-restore finding

The **replacement Xoom has physically booted its existing Android 3.1 HMJ37 (`trygon-userdebug`, `stingray`)** with normal Android init and zygote running. The touchscreen is not registered in `/proc/bus/input/devices`. Android's own OEM-era `qtouch` driver reports **I²C failure -121 / no ACK at address 0x5b** and cannot communicate at its bootloader address 0x35 either, exactly paralleling TWRP recovery's missing touch input. **This is not merely a TWRP GUI/touch event issue; it does not yet distinguish a retained power/reset state from a hardware connection fault.** Propose a true shutdown/disconnect/cold boot, not a storage format, as first follow-up. No cold shutdown was executed in this finding.

The Pi privately holds full MZ600 **HRI39 (Android 3.0)** and **HRI66 (Android 3.0.1)** historical factory-reference archives, each containing `boot.img`, `recovery.img`, `system.img`, and `userdata.img`, verified against historical whole-ZIP MD5 and internal ZIP CRC/image forensic manifests; original full archive Motorola signing is **not cryptographically established**. This makes eventual stock Android restoration plausible but not automatic, and it would **downgrade** today's Android 3.1 and overwrite user data if userdata was restored. Keep images in private quarantine; do not flash, format or relock. Read [Android touchscreen and stock restore checkpoint](ANDROID_3_1_TOUCHSCREEN_COMPARISON_2026-10-24.md) before changing OS priorities.

## 18. Touchscreen incident conclusively resolved by true shutdown/restart (October 25, 2026)

After Section 17's Android 3.1 versus TWRP I²C failures, the user **powered the replacement Xoom fully off and then on** and reported touch functionality restored. Surface ADB independently confirmed original Android `qtouch-touchscreen` now enumerates at **`/dev/input/event6`** with `qtouch_ts_probe: FW version is 0x10 Build 0xFF`, `Chip type matched`, `Reflash not needed`, and IRQ **362** allocated successfully. Android remains booted (`sys.boot_completed=1`).

**Status:** Touchscreen outage **RESOLVED after cold power cycle, monitor for recurrence**. This outcome argues against a permanently dead touchscreen and against reflashing Android as the first troubleshooting step; exact root cause remains unproven. There were **zero hardware modifications, touchscreen firmware reflashes, OS formats, or partition writes**. The earlier proposal to test cold power cycling is no longer pending. Detailed [resolution and pre/post evidence](ANDROID_3_1_TOUCHSCREEN_COMPARISON_2026-10-24.md).

The **BCM4329 native Linux WLAN milestone remains unaffected** and the OS build artifacts remain offline/uninstalled. Current tablet is running stock-installed Android 3.1, not the temporary Linux diagnostic environment; do not assume COM9 module-upload protocol is available without booting the temporary image.

## 19. MicroSD native OS physically installed; first boot shows retained fastboot screen (October 25 follow-up)

The user approved erasing the **inserted empty 32GB microSD**. The SD was repartitioned to standard aligned MBR ext4, verified through actual block readback (first 768MiB SHA256 matches), expanded to ~29 GiB ext4, passed full e2fsck and was read-only mounted showing Debian 12.15 and separate WCC + USB ttyGS0 service. **No eMMC partitions were written**, despite SD/MMC block numbering changing across a recovery reboot. See [installed SD milestone](MICROSD_NATIVE_LINUX_INSTALLED_FIRST_BOOT_2026-10-25.md).

First `fastboot boot` of clean normal OS returned transfer and boot OKAY on host, **but user reports the fastboot screen remained unchanged** and Windows reports no USB Serial/ADB/Fastboot afterward. **Linux OS boot not confirmed**. Comparing built images found prior working v15 diagnostic boot used nonempty boot header ramdisk + embedded initramfs, while new native OS boot uses zero external/embedded ramdisk (same DTB as proven). A controlled **71-byte no-`/init` boot-header ramdisk-only** image has been built and exact kernel/boot cmdline compared, SHA256 `d4a76ef50b52882db5237a4a2975645b8615a20ef2692d61d1ed905457306a45`, staged on Surface with the known-working v15 reference. **Neither tested on tablet yet**, no flash. Physical power cycle by user is needed to restore USB control before next temporary-only test. [Troubleshooting milestone](MICROSD_FIRST_BOOT_FASTBOOT_SCREEN_RAMDISK_COMPARISON_2026-10-25.md).
