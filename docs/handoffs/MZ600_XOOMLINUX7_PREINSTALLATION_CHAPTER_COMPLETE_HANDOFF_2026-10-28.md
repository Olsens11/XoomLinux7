# XoomLinux7 — comprehensive preinstallation chapter handoff: MZ600, Debian Bookworm, Linux 7, BigPart and TWRP

**Checkpoint date:** Wednesday, 2026-10-28, after the 08:19–08:22 EDT physical remote reboot-to-bootloader trial.

**Repository:** [Olsens11/XoomLinux7](https://github.com/Olsens11/XoomLinux7)

**Working branch at handoff preparation:** `wip/clean-wifi-bt-usb-20261025`; last completed checkpoint commit before this document: `713ecbd`.

**Pinned external kernel:** [xoom-linux/linux](https://github.com/xoom-linux/linux) `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, Linux `7.0.0-next-20260422+`.

**This document's role:** comprehensive transition from **validated development and OS packaging** to the **carefully gated attempt to install and physically qualify a new Linux 7 image** on the experimental replacement Motorola Xoom MZ600. It is not a flash authorization, boot confirmation, or upstream submission.

> **READ THIS FIRST — EXACT STOPPING POINT.** The replacement MZ600 still boots its **previously proven, persistent Stage-D / V31 Debian 12.15** from **p7 boot + BigPart p8 ext4**. After a software `reboot(2)` request with `bootloader` on 2026-10-28, **normal Linux returned**, but **fastboot never enumerated** during a full 120-second watch. COM9 provided a normal `xoom-mz600 login:` prompt and the device responded to WLAN ping. We **have not** cold-backed-up p8, entered temporary Stage-B again, booted the clean nine-patch kernel, booted the new Debian image, built a BigPart TWRP 3.1.1-0 replacement, or flashed anything in this phase. A guarded one-shot cold p8 backup service **was deliberately staged on the rescue microSD and is still ARMED**; it will be eligible to execute on the next appropriate microSD-root Stage-B boot. Do not confuse that preparation with a completed backup. **Do not boot the existing factory-layout TWRP** while protecting the current BigPart filesystem.

## 1. Owner intent and binding decisions

The owner is entering the **next chapter: install and test the clean Linux 7 + Debian candidate without losing the working MZ600 reference**. This is not a request to restart the Wi-Fi bring-up project, discard the review series, or perform a destructive install immediately.

1. Retain a **standard persistent Debian armhf main OS** on the Xoom. The successful existing installation uses **internal p8 as root** and p7 as boot; the owner prefers that conventional arrangement over RAM-only demonstrations.
2. Retain the **classic Xoom BigPart** kernel-visible geometry: p8 **1 GiB**, p9 **512 MiB**, remaining p10. Do **not** invent "SuperBigPart" just to accommodate a nominally 2 GiB test-image file; its actual data fit into an independently checked 1 GiB derivative.
3. Preserve the existing V31 boot, modules, firmware, system, and all unique per-device calibration/identity for comparison, debugging and rollback. **Cold, unmounted p8 backup and a verified restore route are hard gates before any p8 overwrite.** The eight earlier live raw captures are valuable but not a cold filesystem-consistent snapshot.
4. Target **TWRP 3.1.1-0** with a correct **BigPart-aware recovery kernel**, not a downgrade to older 2.x BigPart builds. Existing TWRP 3.1.1-0 is factory-layout and unsafe to boot casually while protecting enlarged p8.
5. Because the owner may be away from the Xoom, prefer **button-free software-controlled** Linux→fastboot→temporary boot, and possibly Linux→recovery once a safe recovery exists. A real attempt has just established that the current `bootloader` reboot request is **not honored as fastboot**, despite returning to working Linux. Avoid blind repetitions or claiming a fully proven remote loop.
6. On a fresh Debian test image provide **NetworkManager + `nmtui`**, DHCP, `ping`, `curl`, CA certificates, wireless regulatory data and time sync; provide a visible local console plus the existing reliable **USB ttyGS0/Surface COM9** fallback. The owner requested a simple temporary local root password, configured **privately only in the disposable test root**; do not publish it or enable password-based root SSH.
7. Preserve **exactly one logical issue per upstream review patch**, maintain independently routed and bisectable DT, ARM, wireless and block/GPT series, and do not promote lab-only behavior into the clean series. The current review patch set has **nine** members, with builds passing but **physical verification and upstream approval still OPEN**.
8. **Protected original Xoom** is not the experimental device. No changes to other MZ600/MZ604/MZ602/Xyboard units without model-specific validation.

## 2. Essential reading order for the next conversation or agent

Begin by checking current HEAD, the present physical device state and changed files; historical next-task wording elsewhere is often stale.

1. **`AGENTS.md`**, **`START_HERE.md`** and **`docs/process/DEVELOPMENT_WORKFLOW.md`** — authority, original-device protection, evidence, build and Git rules. Their older "CURRENT v06.3" top notes are historical; this new handoff plus dated 2026-10-28 checkpoints supersedes them on *status*, not on safety policy.
2. **This entire handoff** — authoritative starting point for the new installation chapter, including pending rescue-microSD one-shot behavior.
3. **`docs/checkpoints/MZ600_REBOOT2_BOOTLOADER_PHYSICAL_NORMAL_LINUX_FALLBACK_2026-10-28.md`** — latest actual physical negative test, host timing, prepared rescue SD service, and proven return to ordinary Linux.
4. **`docs/plans/MZ600_REMOTE_NO_BUTTON_FASTBOOT_COLD_BACKUP_RECOVERY_2026-10-28.md`** — original intended remote flow and its caveats. **Read together with step 3; the bootloader transition in that plan has now actually failed.**
5. **`docs/checkpoints/MZ600_V31_PREFLASH_PRESERVATION_AND_TEST_ROOT_2026-10-28.md`** — exact eight-image private live backup hashes, GPT CRC, private original firstboot build and hard stop.
6. **`docs/checkpoints/MZ600_ONE_GIB_ROOT_AND_BIGPART_RECOVERY_PLAN_2026-10-28.md`** — canonical 1 GiB rootfs derivative, measured ext4 blocks/free space, BigPart recovery considerations and original Stage-B rescue route.
7. **`docs/checkpoints/MZ600_TWRP_3110_BIGPART_BASELINE_AUDIT_2026-10-28.md`** — actual p6 extraction, original TWRP 3.1.1-0 ramdisk, why fstab-only edit is insufficient, and kernel/mount/size requirements for replacement recovery.
8. **`docs/checkpoints/MZ600_STAGE_D_INSTALLED_VS_NINE_PATCH_REVIEW_2026-10-28.md`** — exact installed-vs-new kernel provenance, DT semantics, symvers CRC differences, and mandatory new BigPart boot args.
9. **`patches/upstream/INTEGRATION_SOURCE_MANIFEST_20261028.json`**, **`patches/upstream/REVIEW_TRACKS_20261028.md`**, and **`patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md`** — nine source patches and per-maintainer release gates. OS packaging and old Vxx lab changes are not extra upstream patches.
10. **`packaging/firstboot/README.md`**, **`packaging/firstboot/manifest.json`**, **`docs/checkpoints/MZ600_FIRSTBOOT_WIFI_COM9_SCREEN_KIT_2026-10-28.md`** — reproduction of Debian offline kit, private firmware separation, password only in disposable image, NetworkManager and local terminal.
11. **`docs/checkpoints/MZ600_V31_FIRST_REBOOT_AUTOCONNECT_FULL_STACK_PASS_2026-10-28.md`** — actual V31 WPA2/DHCP/DNS/NTP/HTTPS success and the ~399-second association defect.
12. **`docs/handoffs/MZ600_XOOMLINUX7_COMPREHENSIVE_CANONICAL_PATCH_AND_WIFI_HANDOFF_2026-10-27.md`** and the older full-transition/V19/V20 handoffs — full prior driver research and experimental rationale. These remain valuable background, **not** the current deployment stopping point.
13. **`docs/process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md`**, **`docs/process/EVIDENCE_AND_PRIVACY.md`**, **`docs/README.md`**, **`docs/status.md`**, **`runtime/PROJECT_STATE.env`** — machine roles, approved transport, confidentiality and current mutable index.

Before hardware work, re-read the source document, not only this summary; validate that hash-locked files still exist and that nothing changed since the last session.

## 3. Hardware and current physical system

| Item | Last proven state / meaning |
| --- | --- |
| DUT | **Experimental replacement Motorola Xoom MZ600 Stingray CDMA**; only this unit is authorized for Linux tests |
| Protected reference | Separate original Xoom with TWRP/Toolkit; do not operate on it |
| OS | **Debian GNU/Linux 12.15 Bookworm armhf**, physically booted and running from internal eMMC |
| Kernel release | `7.0.0-next-20260422+` (also the new build release string; **not proof of binary identity**) |
| Persistent boot | p7, 8 MiB, **installed Stage-D** Linux Android-format boot image |
| Persistent root | `/dev/mmcblk0p8`, ext4, mounted **rw** while normal Debian is running |
| Internal disk | `/dev/mmcblk0`, **62,521,344 sectors × 512B = 32,010,928,128B** |
| Vendor GPT | OEM **relocated** GPT at **LBA 62,513,151**, header and CRC proven from host backup |
| BigPart p8 | start LBA **118,784**; sectors **2,097,152**; **1,073,741,824B** |
| BigPart p9 | start **2,215,936**; sectors **1,048,576**; **536,870,912B** |
| BigPart p10 | start **3,264,512**; sectors **59,247,616**; not backed up as a whole |
| Existing recovery | p6, **12,582,912B**, **TWRP 3.1.1-0 non-BigPart**, confirmed unsafe factory partition map |
| Rescue microSD | `/dev/mmcblk1p1` ext4 with existing Debian 12 SD-root; ~27 GiB free at the read-only preflight; currently **inserted**, a one-shot backup service now **armed** on it |
| USB console | Linux USB gadget serial `ttyGS0` on Surface **COM9**, 115200 baud, previously root login; **after failed fastboot transition ordinary login prompt is shown, no new authentication performed** |
| Network after test | A Surface ping to previously configured private WLAN address succeeded after the reboot; **do not infer all WPA/HTTPS checks were rerun in this boot** |
| Display | Live `tegradrmfb` framebuffer, LVDS connected, tty1 getty, touchscreen event device physically present; newly prepared UI not visually/interaction tested |
| Boot issue | Intermittent **red camera LED / incomplete reboot** occurred historically, sometimes required manual volume/power rescue; **not** observed as permanent hang in the latest test |

**VERY IMPORTANT:** Old stock recovery knows factory geometry: p8 **256 MiB**, p9 approximately **169 MiB**, p10 begins LBA **989,184**, which overlaps current expanded p8. Its prior initialization could mount `/data` rw. Never enter it for convenience without an independently protected, mode-correct strategy.

The user's intention to replace Android on the *experimental* device does not waive current Linux-backup requirements. Current p7 and p8 are now the valuable functional reference.

## 4. Existing working V31 installation — what it proves, what it does not

The installed image derives from the **Stage-B** kernel build, **not** an earlier Stage-A `CONFIG_INITRAMFS_SOURCE` experiment. The persistent Stage-D Android-format image retains an **external ramdisk**, with kernel `CONFIG_INITRAMFS_SOURCE=""`.

- Stage-D Android-format boot bytes: **6,645,760**, SHA256 **`fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`**; full 8 MiB p7 capture SHA256 **`901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`**.
- Stage-B source `zImage` SHA256 **`d0ada47734cd7686f780cb37f9abb95e354a80d333840c7979b756053fe6a9d1`**; the *new* review source `zImage` has a different hash. Never confuse build archives, Android boot images and raw partition images.
- Stage-D compiled Stingray DT description was `Motorola Xoom (Stingray MZ600 minimal USB diagnostic)`; it included `motorola,xoom-bigpart` on internal eMMC plus a legacy `gpt_sector=` boot argument.
- On physical V31 tests, normal unrestricted multichannel **ESCAN returned scan completions repeatedly** with proper generation/terminal ownership and a **conditional WLC_UP** when firmware was idled. This is a lab/proven behavior, not proof that the cleaned nine-patch modules will reproduce it.
- The **installed V31** boot-persistent network services were `wpa_supplicant@wlan0`, `systemd-networkd` DHCP, and `systemd-timesyncd`. They eventually connected and demonstrated **WPA2-PSK CCMP, DHCP, DNS, synchronized time and HTTP 200 via verified HTTPS**.
- The same boot's WPA association took **about 399 seconds**, despite DHCP following association in about **0.12 seconds**. Legacy Broadcom connection Event0/Event16 messages sometimes had invalid reported interface indices and were discarded; other hypotheses include firmware UP/MPC state. The cause is **not established**. Do not call fast reconnect, sustained stability, Wi-Fi/Bluetooth coexistence or cold boot robustness solved.
- Use the original V31/Stage-D images and filesystem as a **controlled comparator**. Do not overwrite their modules or private firmware when testing new source.

## 5. New kernel: complete upstream-review integration is BUILT, not physically booted

The new source is a **nine-patch, clean reapplication** onto the exact pinned `xoom-linux/linux` base, split by maintainer area and logical scope:

| Routing track | Members | Intended logical changes |
| --- | ---: | --- |
| Tegra DT | **3** | Compatible/bindings; shared Wingray electronics; MZ600 Stingray identity/USB board description |
| ARM boot | **1** | bounded vendor WLAN MAC ATAG → correct FDT handoff, per-device factory identity |
| Broadcom `brcmfmac` | **4** | legacy channel-list fallback; ESCAN generation; narrowly owner-attributed malformed Event69 terminal; conditional firmware UP before ESCAN |
| Block/GPT/BigPart | **1** | conservative MZ600 virtual BigPart geometry after OEM relocated GPT validation |
| **Total** | **9** | One logical issue per review patch; not one enormous cross-subsystem patch |

Canonical sources: `patches/upstream/review-stingray-dt-20261028/`, `review-arm-atag-20261028/`, `review-wifi-four-logical-20261028/`, `review-storage-bigpart-20261028/`. Integration manifest: `patches/upstream/INTEGRATION_SOURCE_MANIFEST_20261028.json`.

- Exact nine-replay kernel source tip: **`507eb069df819cb5cc801ad8be096f70d9ca7609`** (inner Linux tree, distinct from outer GitHub project commits).
- Full **ARM `zImage dtbs modules` build PASS**, fresh revision recorded 2026-10-28T08:34:59Z, toolchain ARM GNU 14.3 Rel1, matching config SHA256 **`e613d891a75e0e2e8f9b87d55fa7023936d48ecec7d3126ea6f4eeaef6dd5cef`**.
- New `zImage`: 5,826,528B; SHA256 **`570c98f1ce187f33c46cc671bb54b0e7b4837756bbec97ef721f8b4c998a5cf1`**.
- New Stingray DTB SHA256 **`c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa`**; Wingray DTB SHA256 **`4144940f352b437c340c5d37f5a4c9dcc711024ef9785746ff3bd2d1f8bab3ff`**.
- New `brcmfmac.ko` SHA256 **`5e767d47017ff9028e6c364f8325420b0fc79efd1c1e07d36595fb4fd0540d26`**; new `brcmfmac-wcc.ko` SHA256 **`eb9aa7efc8d9e356088aa9693cf1937c8c7e1a65dcd0193618915521b7a048b9`**.
- Reviewed `Module.symvers` has **14,030** exported symbols like Stage-B but **three changed Broadcom CRCs**: `brcmf_fweh_register` `1d31861b→9c21b40f`, `brcmf_fwvid_register_vendor` `be543d6e→3b7b85dd`, `brcmf_set_wsec` `3ffcd99d→16dd9685`. **Never mix new and old wireless/WCC modules based only on identical `uname -r` or vermagic.**
- The new Stingray DTB's only decompiled differences from Stage-B were a descriptive model string and removal of the undocumented `motorola,xoom-bigpart` DT property. For the revised block/GPT RFC, BigPart is **explicitly opt-in**: **`CONFIG_MOTOROLA_XOOM_BIGPART=y` plus boot arguments `gpt xoom_bigpart=1`**. Old `gpt_sector=` alone is not equivalent. A new boot image **without** the opt-in must not mount the present expanded p8 as root.
- Storage arithmetic/source tests (seven tests) and clean builds PASS; source-specific hardware BigPart, actual Wi-Fi RF behavior, BT/coexistence, DT binding/schema review, race/cancellation regressions, and human maintainer acceptance **remain OPEN**.
- **No final Android-format boot image combining this new kernel, DTB, tested ramdisk and correct new root selector has yet been built, validated or physically booted.** No patch has been submitted; no human DCO signoff is fabricated.

## 6. Debian firstboot packaging — actual prepared objects, not proposed functionality

The new userspace was built separately from the running tablet using an **isolated** Debian Bookworm armhf reference filesystem clone in a private Desktop WSL directory. The standard scripts and manifest are in `packaging/firstboot/`.

- **41 authenticated Debian Bookworm armhf packages** actually installed/configured in disposable ARMhf chroot using QEMU binfmt; includes **NetworkManager** `nmtui`/`nmcli`, wpa_supplicant D-Bus support, `iputils-ping`, `curl`, CA bundle, `iw`, `iproute2`, `wireless-regdb`, `rfkill`, `systemd-timesyncd`; bundle source hashes verified.
- Generic, **nonprivate** offline package archive: `XoomLinux7-FirstBoot-Online-Console-v2-20261028.tar.gz`; SHA256 **`224a72c2b09cf3eb9eb073f8df8d68a50a1994459d1317c44e33fa3b15cfbfb2`**. This contains no device firmware or password and has **not been installed on the tablet**.
- NetworkManager is **enabled** as sole owner of `wlan0` in the disposable root; old `systemd-networkd` and `wpa_supplicant@wlan0` instances are **disabled there only**. Original V31 p8 networking services remain unchanged. `timesyncd`, `getty@tty1` and `serial-getty@ttyGS0` are enabled on the test root.
- Public shell utilities: `xoom-wifi` (simple `nmtui connect` selector, status and scan), `xoom-net-check`, `xoom-console-check`.
- A **temporary local root login password** selected by the owner is privately set and hash-verified **only in the disposable root**. Root SSH access and password SSH authentication are intentionally disabled. Never publish the password, clone `/etc/shadow` into Git, or apply this setting to the working p8.
- The device's **private MZ600 BCM4329 firmware and calibration NVRAM** are present in that private test root only. No firmware binaries or device MAC/calibration identifiers are in upstream patch or public package archives.
- **114 matched modules** from the exact nine-source build installed in the test root, `depmod` PASS; `modprobe --show-depends brcmfmac` resolves matched `brcmutil` + `brcmfmac`. This is *offline* module dependency validation.
- The current Linux7 config includes VT, DRM Tegra, framebuffer console, touch and USB serial; on-device `/dev/fb0` and tty1 exist, but a **visible, interactive on-tablet terminal is not yet physically proven for the new image**. A touchscreen input event is **not an on-screen keyboard**; design one if stand-alone touch typing is required. Existing Windows COM9 launcher has PowerShell parser PASS, not comprehensive interactive `nmtui`/Esc/Tab/keyboard qualification.

### Private rootfs image variants — do not conflate their SHA or deployment status

All reside **only** under Desktop WSL private workspace `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`. They are data-bearing files (private firmware + temporary root password) and **must not be committed to public GitHub**.

| Image file | Bytes | SHA256 | Status |
| --- | ---: | --- | --- |
| `XoomLinux7-test-root-bookworm-armhf-20261028.img` | **2,147,483,648** | `b7180b88dfacf29b41bdb515d4d1a5226855fb2065ca8423ea69029a1362a70d` | Original separate ext4 test filesystem; offline e2fsck PASS; **not** a p8-sized image |
| `XoomLinux7-test-root-1GiB-BigPart-20261028.img` | **1,073,741,824** | `9cf413dcf1305e3dbabc13dc2d478ad5d481bfb4da2260cee1de16a59f9c6d31` | **Canonical manifest-listed 1GiB BigPart test-root candidate**; independently resized; 5-pass e2fsck PASS, 13,727 inodes in use and 116,787 free 4KiB blocks |
| `XoomLinux7-test-root-bookworm-armhf-bigpart1g-20261028.img` | **1,073,741,824** | `8a7349948b1cc0b3497068eff75345086c8845415901a1f69c68aead4bd6264a` | Additional separately produced 1GiB derivative; five-pass e2fsck PASS, 145,347/262,144 blocks in use; **not byte-identical** to canonical image |

The two 1GiB derivatives both passed offline ext4 checks but have **different hashes and minor block-accounting differences**, so choose one by exact filename/manifest before any deployment; do not silently substitute one for the other. Neither variant has been booted, subjected to live Linux package/service tests, or written to p8. **The original 2GiB container was larger than the actual data**. A read-only `resize2fs -P` estimated a **217,408 × 4KiB = 849.25MiB** minimum; exact 1GiB candidates were subsequently validated. Therefore **SuperBigPart is not needed for this release.**

## 7. Existing reference backups: eight verified raw captures, but not yet sufficient

The **owner's private Surface Book 2 backup folder** is the authoritative location, outside the public repository: `xoom-linux-rom/private-backups/MZ600-V31-PREFLASH-20261028/`. Transfer was from verified COM9 root over a temporary private, pinned-TLS receiver. Each file was independently reopened, size-checked and SHA256-rehashed.

| Capture | Size | SHA256 |
| --- | ---: | --- |
| `p7.img` | 8,388,608B | `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c` |
| `p8.img` **LIVE RW** | 1,073,741,824B | `49aa3f3094df05b2f16aaa590fbb4d10cb29144647d28e57261cd19ab563f4a9` |
| `p9.img` | 536,870,912B | `034e9157bc85ff4d9bdff0e395da7ee2db31a4ff8f4b602ad21940e1b8af52fa` |
| `boot0.img` | 2,097,152B | `c22364f520348801756a323320af312badd9828812b5474baf6577b5d0d144d2` |
| `boot1.img` | 2,097,152B | `ba07d590ab506d16b83b7801bae738da865a72f57bf4e61f0e97e57f2f755030` |
| `head32m.img` | 33,554,432B | `6efbef9153f93aaeb96a95086d14deace013cd60a917c3138c16939c2b1073f0` |
| `head64m.img` | 67,108,864B | `68ef635674149822109f6687708f9992322f2af263de419270162b633d0d8f51` |
| `tail16m.img` | 16,777,216B | `fb41be791b3858553b0ff34ef7381a892ebfc4c2fc4c6f7156b0c1e01058aab8` |

- `head32m` is byte-identical to the first half of `head64m`; the latter contains the full current p6 **12MiB TWRP recovery partition**.
- The actual p6 region extracted from `head64m` matches bytewise the separately saved old `twrp-recovery-p6.img` (12,582,912B) with SHA256 **`ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`**.
- The backup contains recognizable Android boot magic on p7, ext4 superblock magic on p8 and the relocated OEM GPT `EFI PART` header with valid header CRC at LBA 62,513,151.
- **Limitations:** p8 was copied while **mounted RW** (no cold journal-consistency guarantee); p10 is **NOT backed up**; no full-disk clone exists; a successful hash does not constitute a tested restoration; first/tail sectors are forensic reference and not generic `dd` restore instructions.
- **HARD STOP:** do not overwrite p8 or do invasive layout changes until a **separate cold, unmounted full 1GiB p8 image** is captured, its source identity/size/hash confirmed, offline ext4 read-only check is clean, and the restoration/rescue plan is independently qualified. If anyone intends p10 modifications, its separate backup is also required.

## 8. Recovery: exact TWRP 3.1.1-0 baseline and desired replacement

The full p6 backup was inspected **off-device**, not mounted or flashed.

- Android `ANDROID!` boot header; **2048B pages**; kernel **3,435,708B**; compressed gzip ramdisk **3,953,970B**; uncompressed CPIO **7,770,880B**, **431 entries**; `3.1.1-0` exists in ramdisk version text.
- Built as historical `omni_wingray-eng 4.4.4` dated July 2020 (the MZ600 was using this Wingray-family recovery).
- `etc/recovery.fstab` and `fstab.stingray` use old by-name `system/cache/userdata` semantics; `length=-4096` and `length=-16384` offsets require audit. **A fstab-only patch does not enlarge kernel block partitions.**
- Historical 2.x BigPart Wingray recovery binaries may help research but are **not an acceptable downgrade** under owner's explicit **3.1.1-0** requirement. No verified MZ600 3.1.1-0 BigPart ready-to-flash binary has yet been found.
- Necessary new kernel (compatible with Android/TWRP userspace and MZ600 board) must publish correct classic BigPart geometry, maintain p1–p7, reject unknown eMMC geometries, and block automatic system/cache/data mounts or repairs until checked. Check touch/UI, ADB/USB, microSD support, backup/restore operations and image size **≤12MiB**.
- Preserve verified p6 rollback image; **first try the new recovery using temporary `fastboot boot` if the bootloader accepts it**, and inspect geometry and absence of internal mounts. Only with evidence and separately approved p6-only write may we replace recovery from *running Linux* using exact verified bytes and read-back SHA.
- Do **not** reboot into the old current TWRP as a shortcut to cold backup: its stock p10 start overlaps valuable BigPart p8. An MZ600-compatible BigPart-aware rescue is required.

## 9. The prepared button-free cold p8 backup path and what is armed on SD

### Intended route

Known-good **Stage-B Debian microSD-root temporary boot** was physically proven previously using `fastboot boot`:
- Surface private file: `downloads/MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img`
- 6,645,760B; SHA256 **`b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`**
- It booted Debian from removable `/dev/mmcblk1p1`, while internal p8 was unmounted, with correct p8/p9/p10 mapping and USB ttyGS0 login. This is historical **physical PASS**, not a claim it ran today.

Known-good installed-p8 **Stage-D** temporary boot fallback is also present on Surface:
`downloads/MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img`, 6,645,760B SHA256 **`fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`**; this same image's bytes are the proven persistent p7 boot payload.

### What the most recent work *actually staged*

While booted from internal p8, we inspected the removable SD **read-only** first (`mount -t ext4 -o ro,noload`, ext4 Debian 12, ~27 GiB free), then explicitly mounted it **RW** only long enough to install and hash-verify a **one-shot systemd backup unit** and helper, then synced and unmounted it. All staging writes went to **removable SD**; **no direct internal eMMC partitions changed**.

Installed on **microSD root only**:
- `/etc/systemd/system/mz600-cold-p8-backup-20261028.service`, enabled in `multi-user.target.wants`.
- `/etc/mz600-cold-p8-backup-armed-20261028` is the one-time activation marker.
- `/usr/local/sbin/mz600-cold-p8-backup-20261028.sh` (current success-only auto-return variant).
- `/usr/local/sbin/mz600-cold-p8-backup-original-20261028.sh` (first backup-only script kept for local reference).
- `/usr/local/sbin/mz600-reboot-bootloader-20261028.elf`, a **664B static ARM EABI** helper, SHA256 **`451847d8acda2526c93a7b02d4694f3e80fefacce6281417ce75ee4ee6a0bf14`**.

The one-shot unit disarms itself at the beginning; under a *correct Stage-B microSD-root boot* it checks root `/dev/mmcblk1p1`, internal disk **62,521,344 sectors**, p8 start/size **118784/2097152**, p9 **2215936/1048576**, p10 **3264512/59247616**, that p8/p9/p10 are **not mounted**, and output space. It reads internal `/dev/mmcblk0p8` to **microSD only**, target `/var/backups/MZ600-V31-P8-COLD-20261028/p8-cold.img` (using a `.partial` first); it verifies exact 1GiB size, compares **SHA256 of image and source block device**, runs `e2fsck -fn`, then emits `RESULT.txt`, `SHA256SUMS` and a pass marker. Only **after** success does it sync and invoke ARM helper to request `bootloader`. **Note: the request has now physically failed to reach fastboot from installed Stage-D**; on Stage-B it may also be ignored, may fall back to installed Linux, or may hang. Its automatic return is **not qualified**, and a user may want to disable the staged service before any unrelated SD boot.

The next conversation MUST detect whether this marker/service still exists **before initiating any microSD-root boot**. The service was still **armed** after the unsuccessful installed-Linux reboot test; no `RESULT.txt` or cold p8 image was created in that test. The Surface remote watcher is **not left running**. No automatic follow-up has been scheduled.

**Security/operational note:** This staged agent was created outside the normal reviewed upstream patch process. Before execution, re-audit its exact on-SD bytes and behavior: mount source resolution, e2fsck exit handling, output directory creation, available space, one-shot disarm and success-only return, and root privileges under Stage-B. Do not equate "staged" with "fully physical-validated."

## 10. October 28 physical reboot trial — exact failure and recovery evidence

The owner explicitly authorized trying remote mode transition without button presses while away. Source `drivers/soc/tegra/pmc.c` recognizes `bootloader` and `recovery` reboot reason strings by setting Tegra PMC scratch bits. A preexisting tiny ARM helper source `scripts/experiments/mz600-arm32-reboot-to-bootloader-20261026.c` uses `reboot(2)` with `LINUX_REBOOT_CMD_RESTART2` and literal `bootloader`. The actual Motorola bootloader handling was **not yet proven**.

On **2026-10-28 at about 08:19:54 EDT**:
1. The Surface verified **exact hashes and sizes** of both Stage-B and Stage-D images, one expected tablet USB serial connection, root console on installed p8, correct BigPart geometry and presence of SD; the static ELF was SHA-verified in the Xoom's `/run` tmpfs.
2. Surface sent the **ARM `reboot(2)` helper** while root in Linux. By **08:19:56** the USB gadget COM9 connection had dropped, consistent with a hardware reboot.
3. Surface polled `fastboot devices` for **120 seconds**. **It never saw the expected MZ600 fastboot interface.** The host watcher **stopped safely**: no `fastboot boot`, no `fastboot flash`, no recovery boot, no storage writes.
4. Windows subsequently again enumerated **Linux COM9**; the tablet answered a WLAN ping; a non-destructive Ctrl-C in COM9 produced `xoom-mz600 login:`. Therefore the tablet returned to ordinary Linux, **not** a persistent red-LED hang.
5. The device was **not reauthenticated after reboot**, so the earlier root shell was not carried across the reset. The current last-proven state is a **login prompt**, not a claim that the old root session remains live.
6. **Cold p8 backup remains OPEN.** The removable SD one-shot backup did not run because Stage-B never booted. TWRP remains the original non-BigPart version.

**What this proves:** source support for software-requested mode does **not** guarantee this Motorola bootloader obeys it; restart itself functioned in this trial; Linux came back. **Unknown:** whether the persistent Stage-D kernel really registered/ran the reboot notifier and wrote the scratch bit, whether the bootloader ignored/cleared it, whether an OEM-specific alternate mode path is needed, and why factory bootloader mode was not entered. Do not assert a specific root cause.

**Do not repeatedly re-run the identical command while the owner is away.** The next diagnostic should first be **source- and evidence-driven**. `CONFIG_KEXEC=y` is present, but a RAM-only `kexec` to rescue SD Debian would be a *new*, unverified hardware path; do not assume it can substitute for fastboot without validation and safe fallback.

Private Surface host scripts/logs (never raw-publication):
- `xoom-linux-rom/inspection/MZ600-Linux-Fastboot-SDCold-Return-20261028.py` — exact guarded reboot/fastboot cycle and local log.
- `MZ600-COLD-P8-REMOTE-CYCLE-20261028.log` — timestamps of actual physical trial.
- `MZ600-Stage-COLD-P8-SD-Agent-20261028.py` and `MZ600-Stage-SD-AutoReturn-20261028.py` — verified removable-SD staging.
- `mz600-cold-p8-backup-with-return-20261028.sh` and associated unit/helper — private scripts. **Audit the live card before using them.**

## 11. Recovery, restore, and what to do if something goes wrong

**Current functional fallback:** current internal Stage-D p7/p8 Linux returned from the failed mode attempt. The existing p7 raw 8MiB backup and older Stage-D Android-format boot image are both hash recorded, p8 live raw 1GiB reference is privately saved, p6 original TWRP recovery bytes are independently verified. **No proof of full restore of the working p8 exists yet.**

For a *controlled* failure while in a verified fastboot session, historical working operations were `fastboot boot <SHA-verified known-good Stage-D image>` or `fastboot reboot` into preserved p7, after exact expected `xoom-cdma` identity and unlocked state. **Do not claim this can recover a red-LED hardware hang if fastboot itself never enumerates.** If the Xoom stops presenting both Linux serial and fastboot, remote commands may not help; manual power/volume operation or hardware recovery may be required.

**Prohibited without separately verified backups, exact target and authorization:** raw factory GPT rewrite; partition-table format/convert; p6 recovery flash; p7 boot flash; p8 reformat/overwrite; any p9/p10 modification; automatic stock TWRP mounts. A "working root password" in a disposable test image does not authorize changing installed root credentials.

## 12. Operator/tooling workflow and privacy

**Roles:**
- **Windows desktop** `DESKTOP-R16QJD4` with WSL `Ubuntu-22.04`, project Git at `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project`, private test build/material under `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`.
- **Surface Book 2** `SURFACE-BOOK-2`: USB COM9 and Windows fastboot/ADB, owner-private backups and trial log, USB-origin verification. A separate tool device name may refer to a *different* system; rediscover authorized devices before selecting one.
- **Experimental Xoom**: current Debian root on internal p8 and inserted microSD; reboot currently at ordinary Linux login.

**Rules:** Use Desktop Commander's current connected device list and appropriate device to access real project files. Read `AGENTS.md` and transfer SOP. Don't guess a file path, hashes, tool arguments or live serial identity. When using the ordinary *Wi-Fi/driver laboratory transfer*, follow the documented Desktop→Surface SHA-verified port-43157 SOP; the special one-shot private TLS backup and USB COM9 RAM staging were **specific preservation experiments**, not blanket replacements for that protocol. Avoid simultaneous COM9 owners and non-deterministic commands. A previous remote script has already ended; its historical process PID is not a live watcher.

**Public Git:** README, build scripts, kernels/patches and sanitized evidence only. Keep private: raw p6/p7/p8/p9/boot0/boot1/GPT/p10 images, device serial/MAC, SSID/PSK, firmware/NVRAM blobs, SSH credentials, root password, and user-specific paths. Do not publish a "sanitized" file without reviewing it. Never add human `Signed-off-by` without actual human DCO authorization.

## 13. Next chapter: ordered execution plan with explicit gates

### Phase A — finish the handoff and nondisruptive audit (NOW)

1. Freeze and index this chapter document; run repository checks and commit/push. Leave the working MZ600 operating system undisturbed.
2. Verify latest Git HEAD, all private image sizes/checksums, backup manifest and whether another agent/user changed the tablet since the latest physical test.
3. Inspect the latest failure receipt and the kernel's *actual reboot notifier registration* and Motorola bootloader convention (including read-only source/OEM comparisons). Determine why restart2 `bootloader` was not effective before attempting another mode transition.
4. Audit the SD-root one-shot backup service as already armed and plan its safe disarm/re-arm behavior. **Do not let a future unrelated boot into Stage-B unintentionally trigger p8 backup and reboot.**
5. If applicable, explore a **strictly reversible kexec strategy** on paper/offline. `CONFIG_KEXEC=y` is necessary but not sufficient; memory/device reset and UART survival are unproven.

### Phase B — cold reference backup without damaging current installation

6. Choose a proven entry path into **BigPart-aware SD-root Debian** with the full 1GiB p8 exposed and **unmounted** (historically Stage-B via temporary `fastboot boot`). Do not enter the old non-BigPart TWRP.
7. Before execution, confirm exact DUT, rescue SD, boot image hash, p8/p9/p10 sector map, no p8 mounts, adequate output capacity, systemd one-shot and root privilege. Arrange ability to recover a reset hang if owner remains away.
8. Capture full **1,073,741,824B** cold `/dev/mmcblk0p8` to uniquely named private storage; verify readback SHA and count, offline ext4 `e2fsck -fn`, keep original live snapshot and copy important cold backup to a second host. Write a **new dated immutable cold-backup checkpoint**; do not mark PASS if the one-shot merely staged or failed.
9. Verify a rollback/restoration procedure (including p7/boot hash and recovery path) before allowing any destructive p8 write.

### Phase C — make recovery genuinely BigPart-aware (separate track)

10. Source a buildable, license-respecting **TWRP 3.1.1-0** userspace + compatible MZ600 kernel; adapt the exact classic BigPart parser and fail-closed mount logic. Confirm p6 size under 12MiB, touch/ADB/USB, and no silent system/cache/data automount.
11. Prefer a **temporary recovery boot** with clean read-only sector enumeration and no formatting; reject wrong partition mapping. Preserve old p6 until a passing physical test and explicit authorization for p6-only installation/readback.
12. If the user still prefers on-device in-place p6 update from Debian, it is technically feasible but **must not be the first unvalidated use of a new recovery image**.

### Phase D — construct, test, and only then install the nine-review Linux candidate

13. Keep new nine-patch kernel `507eb...`, matched modules and the two distinct 1GiB root candidates identified by exact hash; choose one canonical root image and inspect `fstab`, module/firmware locations, network manager, SSH safety and root login behavior offline.
14. Build a private Android-format boot image using **exact clean zImage + Stingray DTB + external ramdisk + explicit `gpt xoom_bigpart=1`**, with a valid normal Linux root selector. First use a **separate test medium and temporary boot** or another explicitly reversible route, not overwrite working p8. Validate full image size, cmdline and per-component checksum independently.
15. Physical read-only firstboot: prove exact partition starts/sizes, `/dev/mmcblk0p8` interpretation, expected root origin, `uname -r`, actual kernel/module CRC coherence, serial getty, framebuffer/tty1, display/touch, firmware identity, no accidental internal auto-mount or writes.
16. Then activate **NetworkManager / `nmtui`**, prove SSID selection, WPA2 event path, association, DHCP, DNS, NTP, verified HTTPS, real connect/reconnect latency, valid 2.4/5GHz scanning, and regulatory requirements. Do not borrow V31 physical pass to certify new code.
17. Revisit BCM4329 Wi-Fi connection-event Event0/Event16 parsing and 399s association only with narrow source/hardware evidence. Keep Bluetooth/power and other-device regression work tracked; no "complete chipset" claim until these pass.
18. Only after cold reference + verified recovery + rollback + successful new boot, request separate authorization for exact persistent p7/p8 writes and hash/readback tests. Do **not** silently overwrite current reference during preparatory work.

### Phase E — kernel patch review and upstream submission (parallel, but independent)

19. Keep DT-01..03, BOOT-01, WIFI-01..04 and STORAGE-01 as correctly scoped logical review changes. Run `tools/validate_upstream_review_series.py`, clean replay, individual `checkpatch.pl` and appropriate per-prefix ARM builds; complete DT schema, block-parser geometry, cfg80211 ownership/cancellation, Wi-Fi/BT/power physical validation.
20. Separate non-kernel firstboot/recovery/firmware packaging from upstream patches. **No human DCO or actual mailing-list submission until owner approves and full implementation gates are met.**

## 14. State matrix — do not promote preparations to physical results

| Milestone | Evidence level | Status at this chapter boundary |
| --- | --- | --- |
| Installed p7 + p8 Debian boots | Physical on MZ600 | **PASS; returned to normal Linux after latest reset** |
| V31 WPA2→DHCP→DNS→NTP→verified HTTPS | Physical on installed older source | **PASS on prior boot; association ~399s unresolved** |
| Eight private live eMMC reference images | Host receipt and independent rehash | **PASS, but p8 live RW and p10 absent** |
| p6 current TWRP 3.1.1-0 rollback bytes | Off-device byte comparison | **PASS** |
| New nine-patch kernel + DTBs + modules | Offline full cross-build | **PASS; not physically booted** |
| 41-package Debian firstboot / private firmware / matched 114 modules | Private offline chroot | **PASS; not deployed on MZ600** |
| 2GiB original + two distinct 1GiB ext4 test images | Private SHA and five-pass fsck | **PASS; none physically booted** |
| Device-connected framebuffer tty1, USB COM9 | Installed baseline physical | **PASS for devices/gettys; full new on-screen UI/touch typing OPEN** |
| Rescue SD one-shot cold backup service | Physically staged on removable SD | **ARMED; execution NOT TRIGGERED** |
| Software `reboot(2) bootloader` | Actual MZ600 physical trial | **Normal Linux reboot PASS; fastboot entry FAIL** |
| Cold/unmounted p8 reference backup | Physical/host | **NOT CAPTURED — HARD STOP** |
| New BigPart TWRP **3.1.1-0** | Source and hardware | **NOT BUILT / NOT TESTED / NOT FLASHED** |
| New nine-review kernel + new root boot | On-device | **NOT BOOTED** |
| Permanent new p6/p7/p8 deployment | Device | **NO FLASH; NOT AUTHORIZED HERE** |
| Upstream patch posting | Maintainer/human signoff | **NOT SUBMITTED** |

## 15. Instructions for the next assistant/conversation

**Do not begin by asking the owner to explain what happened.** Read the ordered records above and validate current code/files. The user expects concrete, carefully checked execution, not repetitive planning. The most important immediate task is to **understand the failed software transition and safely obtain a cold p8 image**, with no accidental triggering of old factory TWRP or destructive commands. Remember:

- New source/OS is ready for **installation qualification**, not already installed.
- Fastboot entry from installed Linux **failed once**; **ordinary Linux returned**.
- Rescue SD **contains an ARMED one-shot backup service**; inspect before booting it.
- A **real cold p8 image** and verified restore plan are mandatory before flash.
- TWRP **3.1.1-0** is the required version; the current image is **non-BigPart**.
- Classic 1GiB BigPart is enough for the new Debian root.
- Check exact private artifact filenames and SHA; **two 1GiB variants exist**.
- Keep Wi-Fi V31 hardware proof separate from the new nine-patch build's **offline-only** validation.
- Keep the protected original Xoom untouched, do not expose private assets, and do not fabricate a success, human signoff or upstream approval.

**No work automatically continues after this handoff.** Every later action must be performed in a future explicitly authorized interactive session with current host/device verification.

---

### Provenance and related documents

This chapter is a **consolidation and index of separately preserved immutable evidence**, not a substitute for it. Exact commands/raw device-specific receipts stay on authorized private hosts. Principal public source records are linked in sections 2, 4–10, and 13. The previous comprehensive Wi-Fi/patch engineering history remains in `docs/handoffs/MZ600_XOOMLINUX7_COMPREHENSIVE_CANONICAL_PATCH_AND_WIFI_HANDOFF_2026-10-27.md` and older archive files. Revision/commit of this handoff is recorded in its Git history, not asserted in advance in its own body.
