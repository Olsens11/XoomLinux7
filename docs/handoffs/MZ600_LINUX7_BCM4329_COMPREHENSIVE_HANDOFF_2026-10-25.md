# XoomLinux7 / Motorola Xoom MZ600 — Comprehensive Engineering Handoff

## 2026-10-26 — definitive p7 readback (supersedes flash ambiguity)

Authenticated Debian SD-root console read-only SHA256 of the complete internal p7 boot (8MiB) returned `4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3`, EXACTLY the same SHA256 as the backed-up factory Android p7. The 6,645,760-byte p7 prefix returned `e560dea72ffd24dfcc38e9c89bddbb57bd210b0300c68bd76b46a07332d6f873`, different from Stage-B SD-root boot image. The p7 first eight bytes are ASCII `ANDROID!`. The earlier fastboot PowerShell error DID NOT change internal p7. Full physical proof captured on Surface at `captures/MZ600-P7-READONLY-SHA256-PROOF-20261026.txt` (SHA256 `59c83d3350978786193808393f1da901323e86d347f1ca645564d3900386a0f5`). All work on the tablet in this stage was read-only. Current Xoom mode: authenticated Debian 12 SD-root via temporary Stage-B kernel, BigPart p8 remains unmounted/unmodified. Before any new p7 write, use corrected fastboot wrapper capturing native stderr warning and exit status separately, then verify physical p7 readback.

## 2026-10-26 02:26 EDT — CURRENT: LINUX→FASTBOOT REBOOT DID NOT SELECT FASTBOOT; INTERRUPTED P7 BOOT FLASH, READBACK REQUIRED

**READ NEWEST [RESCUE AND FLASH AMBIGUITY CHECKPOINT](../checkpoints/MZ600_LINUX7_RESCUE_BOOTLOADER_AND_P7_FLASH_AMBIGUITY_2026-10-26.md) BEFORE ANY NEXT ACTION.** User successfully privately authenticated Debian sudo and became root, USB console disconnected; root session initially confirmed. Stage-B kernel PMC scratch reboot via verified 664-byte freestanding ARM EABI `reboot(2)` RESTART2("bootloader") utility returned to original Android, **NOT fastboot**. This route is NOT verified independent rescue; do NOT trust it. Android later recovered ADB fully with 100% battery.

The verified stock Android p7 boot backup (8MiB SHA256 `4DA4C9F1486374BB66F31C96389CD1EE3067A447E8A72AEA33B2FC24AC3985E3`) and TWRP p6 backup (12MiB SHA `EBE3F1C16CE9D79962433A60B0E63EC6E9F1D6392813601C264204D58B8BBEEC`) reverified on Surface. One-time script `captures/MZ600-v064-StageB-Persistent-SD-Rescue-Boot-Once-20261026.ps1` started a `fastboot flash boot` of proven stage-B Debian SD-root image SHA `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`. First native stderr was `Warning: skip copying boot image avb footer (boot partition size: 0, boot image size: 6645760)`, and PowerShell ErrorActionPreference=Stop converted it into terminating NativeCommandError **before command result confirmation**. **P7 CURRENT FLASH CONTENT UNKNOWN**; never infer either flashed or unchanged, and never repeat flash blindly. Fastboot stayed reachable, then same source image **temporarily fastboot booted RAM-only** to known-good Debian microSD login. This proves rescue by external host while already IN fastboot; no p8 block write.

**LIVE DEVICE NOW**: Stage-B Linux7 Debian 12.15 freshly booted from removable SD over COM9, at login prompt; previous sudo root shell was lost due reboot. Owner must log into USB console again with previously known password and `sudo -s`, then Ctrl+] release COM9. Next immediately read **p7 O_RDONLY** full 8MiB SHA256 and first 6,645,760B SHA, compare original backup vs new Stage-B image, with zero writes. If neither matches, treat flash as partial or unknown and DO NOT FORMAT P8. Fix PowerShell AVB-warning stderr handling and confirm persistent p7 and independent fastboot hardware procedure before Android p8 erase. Full verified p8 BigPart geometry/installer `--preflight` still PASS from previous session but **no destructive install** has occurred.

---


## 2026-10-26 01:45–02:00 EDT — NEWEST PHYSICAL BREAKTHROUGH: COMPLETE DEBIAN 12.15 BOOTS FROM SD WITH ORIGINAL BIGPART p8 1GiB; INSTALLER READ-ONLY PASS

**READ THIS FIRST:** [2026-10-26 Stage-B PHYSICAL PASS and p8 installer preflight checkpoint](../checkpoints/MZ600_V064_BIGPART_DEBIAN_SDRoot_PHYSICAL_PASS_INSTALL_PREFLIGHT_2026-10-26.md) contains the full results, source/test hashes, actual commands, safe-fail findings, exact physical state and next steps. User physically inserted the prepared 32GB Debian ext4 microSD. V064 Stage-A diagnostic first detected mmcblk1p1 while BigPart p8 remains 1GiB. Armed two-phase USB reboot to Android physically PASS; verified Android boot and MZ600 fastboot. One checksum-pinned Stage-B `fastboot boot` RAM-only succeeded; actual `Debian GNU/Linux 12 xoom-mz600 ttyGS0` login appeared on COM9 at **01:48:51 EDT**. Surface existing private credential workflow authenticated normal `xoom` user without displaying secret. Normal Debian root **/dev/mmcblk1p1 ext4**, `systemd` PID1, `uname -r 7.0.0-next-20260422+`. BigPart p8 start 118784 size 2097152 512B sectors, p9 start 2215936 size1048576, p10 start3264512 size59247616. Internal p8 unmouted. SD mounted and healthy. No eMMC writes or flash; original Android p7+system p8, TWRP p6 retained.

**New physical environment limits:** `systemctl` fails to contact bus, no `wlan0` currently; do NOT claim full wireless scan. E2fsprogs binaries `/sbin/mkfs.ext4`, `e2fsck`, `blkid`, `resize2fs` and GNU tar are installed, rsync absent. Source SD Debian filesystem uses ~457,700 KiB = ~447MiB, fits 1GiB p8.

**Prepared Stage C INTERNAL p8 ROOT BOOT** 6,645,760B, private Surface SHA256 `15feced18d384ec532b7e3d9fb04463eac14c445909fadb5798920ee661571c8`. Created offline with [Stage C builder](../../scripts/experiments/stage-v064-bigpart-internal-root-boot-from-proven-sd-20261026.py) using exact private p8 GPT PARTUUID captured read-only from kernel sysfs and stored only on Surface. Image differs from physically proven Stage B ONLY in header root selector, Stage B kernel and ramdisk unchanged. **NOT BOOT TESTED; p8 not yet installed; DO NOT BOOT Stage C UNTIL p8 HAS VALID FULL DEBIAN**.

**Prepared guarded native p8 installer on SD** `/home/xoom/mz600-bigpart-install-debian-from-sd-20261026.sh`; exact public [version](../../scripts/experiments/mz600-bigpart-install-debian-from-sd-20261026.sh), SHA256 `e265a0e8f7baae66311788d37ea504dc4e9785530139423428b15a1f41a28650`, verified after serial transfer. `--preflight` completed **FULL READONLY PASS / EXIT 0** on Xoom with all exact system/cache/userdata and protected partitions, root SD, space 457700KiB, target unmounted and kernel GPT PARTUUID proof. The first two read-only attempts stopped safely on regex and minimal-udev missing p8 /dev/disk/by-partuuid symlink; fixes applied/retested. `--install` **NOT RUN**, would format BigPart p8 via standard `mkfs.ext4`, tar-clone SD Debian root and adjust only cloned fstab. NO BLOCK DEVICE WRITES YET.

**IMPORTANT BLOCKER:** real `sudo -n id` said password required. Local user must authenticate `sudo` interactively on Surface USB serial console (existing `Start-Xoom-USB-Console.ps1`), NOT send password in chat; automatic credential retrieval tool call was blocked by safety check, DO NOT circumvent. **MORE IMPORTANT BEFORE ERASURE:** p7 currently stock Android and becomes unbootable after p8 formatting. Replacement has defective Volume Down and intermittent red LED startup, so independent **non-Android bootloader/recovery route and ideally persistent proven stage-B SD rescue p7** must be established/tested using root privileges before destructive install. Prior TWRP p6 still has stock 256MiB p8 view and must NEVER write BigPart 1GiB target. Stage C temporary boot and persistent switch only after internal ext4 install and filesystem checks.

**CURRENT EXACT DEVICE: real Debian 12.15 on SD via stage-B TEMPORARY Linux7 BigPart boot, xoom logged into ttyGS0 COM9; original p6/p7/p8 on eMMC unchanged.** Private credentials/GPT GUID and Broadcom HCD not published. All previous project goals remain: standard Debian terminal (now PASSED via USB, tty1 earlier), actual nearby `iw scan` and Motorola BT HID pairing outstanding.

---


## 2026-10-25 late evening — OFFLINE v064 STAGE B BIGPART-AWARE DEBIAN MICROSD INSTALLER BUILT (NOT PHYSICALLY BOOTED)

Source/build advancement: Physically successful v064 BigPart stage-A RAM-only is CURRENT on replacement MZ600 (p8=1GiB, p9=512MiB, p10=28,929.5MiB; USB PONG). We built a separate v064 stage-B **real Debian SD-root** boot image by reproducing the previously PHYSICAL PASS Debian 12.15 microSD boot path with same unmodified private PARTUUID/root selector, original validated external CPIO ramdisk and new physical-PASS BigPart kernel/DTS (CONFIG_MOTOROLA_XOOM_BIGPART=y, empty built-in initramfs). The image was not booted.

Stage B image: 6,645,760 bytes, SHA256 b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba. Proven earlier microSD boot SHA c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c. Root ext4 768MiB SHA 0aafdddccf58c5259007f272fb7878c417006629f5cb678c6d5e0f361ef8376e. No host/device source reset, no hardware commands in this stage. Independent SHA matched Desktop and Surface. New builder [stage-B SD-root image](../../scripts/experiments/build-v064-bigpart-debian-sdroot-stageB-20261025.py). [Full checkpoint](../checkpoints/MZ600_V064_BIGPART_DEBIAN_MICROSD_INSTALLER_STAGE_B_OFFLINE_2026-10-25.md).

**NEXT USER PHYSICAL STEP REQUIRED:** Reinsert the **same 32GB microSD containing previously verified Debian** into the replacement MZ600; it is currently absent. Only then perform SHA-pinned temporary fastboot boot of stage-B for Debian tty1/USB shell and BigPart p8 discovery. Never write p8 via stock TWRP's 256MiB view; no internal data erasure yet. After normal live Debian SD root is proven, develop/apply properly guarded native ext4 system p8 installer with 1GiB target confirmation, partition not mounted, checksum and readback, then switch to internal p8 boot. v06.4 actual iw scan/BT pairing still not implemented/tested.

---

## 2026-10-25 20:57 EDT — NEWEST: Linux7 Classic BigPart physical PASS, v064 stage-A RAM boot CURRENT

Live replacement MZ600 is now running hash-verified v064 Classic BigPart stage-A RAM-only Linux (not TWRP). One guarded fastboot boot passed; Surface COM9 PONG passed after one transient serial error. **Actual physical /proc/partitions:** p8 system 1,048,576 KiB (1GiB), p9 cache 524,288 KiB (512MiB), p10 userdata 29,623,808 KiB (28,929.5MiB); protected p1-p7 unchanged. Three acceptance flags TRUE. This is original Schischu BigPart's in-memory virtual mapping physically proven on the exact MZ600. No GPT rewrite, format, block write, flash, mounting, Wi-Fi activation or BT activation.

**Immutable new image:** 6,561,792 bytes, SHA256 626e33972bff4bcb6d4bfad895397b7ff28343a781322fad68cb96836ed94cf6. Image in Desktop artifacts-embedded-v064-bigpart-stageA and Surface downloads; builder scripts/experiments/stage-v064-bigpart-gpt-readonly-20261025.py. v063 old image hash 07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e unchanged. Privately logged on Surface MZ600-V064-BIGPART-STAGEA-TEMPBOOT-PRIVATE-20261025.log. See [new PHYSICAL checkpoint](../checkpoints/MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md).

**Next:** 768MiB Debian ARMhf ext4 image SHA256 0aafdddccf58c5259007f272fb7878c417006629f5cb678c6d5e0f361ef8376e fits enlarged p8. But stage-A diagnostic has no shell/upload installer. Stock TWRP 3.1.1-0 still sees p8=256MiB: DO NOT use stock recovery to format/write BigPart system! Integrate BigPart Linux7 kernel into the previously proven normal Debian 12.15 microSD-root/USB-console runtime, obtain standard shell/verified BigPart p8 device and only then install ext4 root to p8 with write/readback verification. Removable SD absent in current run. No actual internal Debian install or Wi-Fi scan/keyboard pairing yet. Original p7 and p6 retained.

---

## 2026-10-25 20:47 EDT — LIVE TWRP ROOT, RELOCATED GPT PHYSICALLY PROVED, v06.4 BIGPART STAGE A SOURCE BUILD IN PROGRESS

**LATEST OPERATIONAL TRUTH (supersedes 19:25 v06.3 live claim below):** Authorized replacement MZ600 was read-only checked in v06.3 USB COM9 (PING/PONG PASS, both radio module stacks unloaded), then rebooted via the existing two-stage armed+confirmed USB REBOOT. Exact stock Android Stingray boot completion passed, then verified-device ADB rebooted to **TWRP 3.1.1-0 root ADB**. TWRP is the **current live device environment**, not v06.3 Linux. Its full 62,521,344-sector internal eMMC geometry and **factory p8=256MiB, p9=169MiB, p10=30040.5MiB** were reconfirmed. No eMMC formatting/flash/partition writes occurred.

**CRITICAL NEW PHYSICAL HARDWARE PROOF:** TWRP kernel commandline `gpt gpt_sector=0x03b9dfff` (LBA **62,513,151**) and dmesg `Primary GPT is invalid, using alternate GPT.` An initial BusyBox 1.21.1 `dd` 12MiB tail capture misleadingly returned FF throughout (private SHA256 `6747318cfda6f6bb9e77ee1c229d37b1799610bc1d41e5165cc40ccf2363a7c4`); do **NOT** infer missing GPT. A specially compiled **2,180-byte**, static freestanding ARMv7 O_RDONLY+_llseek (64-bit offset) probe was hash-verified, pushed to TWRP RAM /tmp, executed and removed. It physically found **`EFI PART` at exactly LBA 62,513,151** (first 8 bytes `4546492050415254`), confirming real relocated GPT. Probe SHA256 `705db0543f03f375da4cdf2334121db457f09767c0a30086c9cc4a453cf0ac07`; source in [public read-only C probe](../../scripts/experiments/mz600-readonly-gpt-sector-armv7.c). Private Windows host backup remains private; no real GPT was modified. See [full physical checkpoint](../checkpoints/MZ600_BIGPART_TWRP_PHYSICAL_GPT_LLSEEK_PROOF_2026-10-25.md).

**CURRENT OFFLINE ENGINEERING, separate from hardware:** Desktop `xoomdev` pulled [isolated v064 BigPart stage-A builder](../../scripts/experiments/stage-v064-bigpart-gpt-readonly-20261025.py) and created clean detached upstream-pinned worktree `clean-wifi-bt-usb-20261025/v064-bigpart-linux` and isolated `v064-bigpart-build`. Adds classic Schischu original 1GiB system/512MiB cache mapping only under `motorola,stingray`, exact 62,521,344-sector eMMC capacity, explicit `motorola,xoom-bigpart` DT opt-in, *all 10 factory GPT extents* strict validation, and bootloader `gpt_sector` parser avoiding old prefix-collision trap. No GPT writes in kernel; uses exact v06.3 embedded PID1+USB as read-only stage. **Kernel compilation is in progress at this entry, NOT yet accepted and NO physical v064 test yet.** Full functional `iw`, real terminal and keyboard acceptance is still separate and unfinished. Preserve previous tested v06.3, original TWRP, factory Android p7/p8, private backups, and the user-approved p8 BigPart root intent.

---


## 2026-10-25 late evening EDT — FINAL STORAGE CHOICE: ORIGINAL CLASSIC BIGPART, DEBIAN ROOT ON P8 /SYSTEM (NO PHYSICAL WRITES)

**USER OVERRIDES EARLIER P10 ROOT PLAN:** user explicitly directs **original Xoom BigPart** and standard `system` partition for Linux root (`/`), rather than p10. User explicitly states **no userdata files need preserving**; data wipe is accepted. This supersedes the immediately preceding p10 Debian root design, not the protection of original MZ600 or evidence requirements. There is **no reason to create a 29GiB userdata backup**. Existing exact p6/p7/p8 and reserved boot-sector private backups remain preserved/reverified.

**ORIGINAL BIGPART SOURCE FOUND:** [Schischu 2013 original BigPart kernel commit](https://github.com/Schischu/android_kernel_moto_wingray/commit/6b3d70fff905b7395fd15992c3779b27d1b6c101) changes **in-memory kernel GPT partition extents only**, not the disk GPT. Its Wingray start-sector triplet `0x1d000/0x9d000/0xf1800` matches **exactly** this replacement **MZ600 Stingray CDMA** p8/p9/p10 snapshot. Standard BigPart remap: system p8 **1GiB** start 118784; cache p9 **512MiB** start 2215936; userdata p10 **28929.5MiB** start 3264512, retains original p10 end; p1..p7 including boot+TWRP unaffected. Existing 768MiB Debian ext4 image fits enlarged 1GiB system. This is a known Xoom in-memory compatibility scheme, NOT authorization to run `sgdisk` or an unverified Wi-Fi Wingray recovery ZIP.

New read-only host auditor [classic BigPart extent proof](../../scripts/experiments/audit-mz600-classic-bigpart-layout-20261025.py) executed on Desktop: `CLASSIC_BIGPART_OFFLINE_AUDIT_PASS`, no device contact or write; JSON in Desktop `artifacts-embedded-v064-preflight/MZ600-CLASSIC-BIGPART-OFFLINE.json`. It mathematically validates all ten partitions, non-overlap, unchanged p1..p7, unchanged p10 end, device geometry and 768MiB image fit. **Next real blocker:** confirm original Xoom BigPart recovery/kernel is physically compatible with this MZ600, and ensure Linux7 can identify the relocated Tegra GPT and adopt original BigPart virtual mapping *before* formatting p8; current Linux7 has normal EFI/GPT parser but no original BigPart adaptation. Original TWRP 3.1.1-0 must not format under 256MiB stock partition map. Prior broken Volume Down + red-LED startup requires independent recovery before persistent writes. Keep Wi-Fi `iw`, shell, BT keyboard v06.4 acceptance unchanged.

**READ [NEW AUTHORITATIVE p8 BigPart install plan](../plans/MZ600_V064_CLASSIC_BIGPART_SYSTEM_ROOT_IMPLEMENTATION_2026-10-25.md) FIRST.** The older [p10-root plan](../plans/MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md) is superseded. All BigPart changes today are research + host-only proof + documentation. **No v06.4 BigPart kernel/image, hardware test or eMMC write was performed.** The last live physical baseline remains v06.3 PONG checked 19:25 EDT.

---


## 2026-10-25 evening EDT — USER EXPANDS AUTHORIZED DESIGN SCOPE TO INTERNAL DEBIAN / OPTIONAL BIGPART (NO EMMC WRITES)

**NEW USER DECISION:** It is acceptable to remove the *replacement experiment MZ600's* Android installation if necessary to build a real, functional Linux OS, and acceptable to perform a BigPart-style resize **if genuinely required**. The protected original MZ600 remains excluded. This supersedes the prior absolute Android-preservation *design preference*, not the procedural per-partition write checks. **No destructive action, reboot or radio activation was performed in this phase.**

**Previously verified exact replacement eMMC geometry now drives the decision:** p6 recovery/TWRP 12MiB, p7 boot 8MiB, p8 Android system 256MiB, p9 cache 169MiB, **p10 userdata ~29.34GiB**. Therefore the 768MiB Debian root image plainly cannot fit stock p8, but **repurposing p10 as a conventional ext4 Debian root has ample capacity WITHOUT BigPart**. Retain p8/TWRP at first; Android with its original userdata destroyed will not remain usable. We already physically booted Debian 12.15 from microSD with actual on-screen tty1 login, USB serial login, systemd and wlan0 on this replacement tablet in an earlier Oct25 checkpoint, so this is not starting the terminal from scratch. Present v06.3 isolated RAM driver qualification remains the last live check; v06.4 is still **not built**.

**Safety blockers before any write:** Existing private p6/p7/p8 and 25MiB reserved-sector backups were freshly SHA256-verified on Surface and match the documented checkpoint; there is **NOT** yet a full p10 userdata backup. Recover first, capture p10, test a boot-independent route into TWRP/fastboot (Volume Down defective; red-light startup remains unresolved). Kernel7 has MSDOS and EFI partition support but *does not have TegraPT parser in its source*, and the original NVIDIA table was not a straightforward GPT at LBA1. Prove Linux7 sees p10 with correct exact start/size, preferably via a read-only RAM-boot probe; consider proper TegraPT kernel patch rather than generic parted/repartition or hardcoded offset. Boot new Debian root from internal p10 temporarily using `fastboot boot` BEFORE any persistent p7 flash. Do not misapply Wingray/MZ604 BigPart packages to MZ600. **BigPart postponed unless internal p10 path is impossible.**

**NEW MANDATORY PLAN:** [internal eMMC p10 root / optional BigPart decision and write gates](../plans/MZ600_V064_INTERNAL_EMMC_ROOT_AND_OPTIONAL_BIGPART_2026-10-25.md). Preserve v06.4 acceptance for real `iw` RF scan, terminal/USB rescue, user-mediated Motorola keyboard pairing/typing, full BCM4329 shared-chip ownership. Last measured radio module state remains from 19:25; no new physical measurements in this turn.

---


## 2026-10-25 evening EDT — v06.4 FIRST OFFLINE PREFLIGHT MEASURED (NO NEW IMAGE)

**New engineering progress:** The authorized Desktop WSL workspace was read non-destructively; working Git branch `wip/clean-wifi-bt-usb-20261025` was clean at the initial audit and the Linux kernel tree is still upstream-pinned at `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` with pre-existing dirty DTS/atags edits preserved. The v06.3 immutable input hash passed. Public preflight script [`preflight-v064-armhf-dependency-closure-20261025.py`](../../scripts/experiments/preflight-v064-armhf-dependency-closure-20261025.py) was committed, pulled to Desktop and run successfully. Its detailed JSON remains local/private at `artifacts-embedded-v064-preflight/PREFLIGHT.json`. **No hardware action, reboot, flash, Wi-Fi scan, keyboard pairing, or new build image** occurred in this phase.

**Verified size and packages:** v06.3 is 6,561,792B, conservative boot ceiling 8,388,608B, headroom 1,826,816B. ARMHF recursive ELF closure raw/compressed-proxy sizes: dash 1,362,012/794,613B; iw 1,637,340/901,218B; iproute2 ip 2,325,572/1,320,857B; getty 1,272,344/769,738B. Dependencies overlap; proxies are not zImage delta estimates. The examined ARMHF sysroot has no BusyBox, bluetoothd, bluetoothctl, dbus-daemon, or signed regulatory.db/.p7s in checked paths. Kernel has VT/fbcon and CONFIG_BT_HIDP=m; HIDP module exists in build tree but is not in embedded v06.3 CPIO. Signed regulatory DB is required by config. A complete v06.4 packing method is therefore **not yet chosen**, and BlueZ functionality is neither staged nor accepted.

**Required continuation:** finish immutable ARMHF BlueZ/D-Bus/busybox/regulatory sourcing and transitive-dependency QA, then measure combined closure and actual zImage increase; choose self-contained or separately validated nonpersistent RAM transport; preserve private HCD and no-SD/no-eMMC guard. Next build must still satisfy genuine on-Xoom terminal, standard iw scan, and Motorola keyboard typing before claiming functional v06.4. See [new precise OFFLINE checkpoint](../checkpoints/MZ600_V064_ARMHF_PACKAGING_PREFLIGHT_OFFLINE_2026-10-25.md). The most recent device-state observation remains **19:25 EDT v06.3 PONG/idle radios**, not a new live measurement.

---


## 2026-10-25 19:25 EDT — DOCUMENTATION AUDIT & NEXT CHAT v06.4 IMPLEMENTATION ORDER

**This is the latest current operational summary; it supersedes all older interim state paragraphs further down this dated handoff.** At 19:25 EDT the authorized Surface independently verified the replacement MZ600 still running **v06.3 RAM-only Linux 7** (USB COM9 **PONG PASS**, onboard MMC2 BCM4329 VERIFIED, wlan0 and hci0 **absent because their respective stacks are unloaded**). No reboot, flash, radio activation or new image generation occurred during this documentation audit. **v06.4 is NOT BUILT yet.**

**NEXT CONVERSATION MUST READ AND IMPLEMENT:** [Complete **v06.4 functional Linux build instructions**](../plans/MZ600_V064_FUNCTIONAL_LINUX_BUILD_INSTRUCTIONS_2026-10-25.md). The plan is a build/acceptance CONTRACT rather than a generic roadmap. User specifically wants **real visible nearby networks via standard Debian armhf iw/nl80211; an interactive local framebuffer/VT shell; and the Motorola Bluetooth keyboard actually paired and sending keystrokes into that shell**, all with USB debug/terminal fallback and preservation of Wi-Fi/Bluetooth lifecycle, no flash or original-Xoom experiments. Do **not** substitute another firmware-only v06.4 and call it the requested feature build. The v06.3 HCD test was useful, but did not contain iw, BlueZ pairing userspace or a shell.

**Development handoff commands, sources and constraints** are in that plan: pinned 7.0 upstream source, known v06.3 hash, user-provided private BCM4329B1 HCD hash, SHA-pinned official Debian armhf iw v5.19 package (QEMU-smoked only), WSL Desktop workspaces, Surface COM9 guarded scripts, 8MiB Android legacy image envelope, ARMv7 no-NEON, built-in CPIO, exact DTB, per-build manifests, unique image versions and temporary fastboot boot. **Do not blindly reuse v06.3 builder unchanged** because it asserts a v06.2 base, and do not rebuild older images with v063 CONFIG_INITRAMFS_SOURCE still selected. If BlueZ+DBus+libraries exceeds RAM-boot allowance, choose a vetted nonpersistent userspace transport or separately user-approved removable SD rootfs, never silently drop functionality or write eMMC. The current v06.3 live session is useful for read-only diagnosis and must not be needlessly rebooted just to plan.

**Acceptance gates:** offline ARMHF executables and full DT_NEEDED dependencies; usable USB PONG and independent fallback shell; actual visible local terminal accepting commands; Wi-Fi start→wlan0→interface UP→**actual iw scan**→redacted AP summary→ordered WCC/brcmfmac/brcmutil cleanup; BCM4329B1 HCD/hci0 plus user-mediated Bluetooth keyboard discovery/pairing/HID typing; BT OFF/STOP; inter-radio shared power/clock/USB shutdown and eventual coexistence only after a separate gated test. Mark each capability PASS, PARTIAL, FAIL or NOT TESTED. No actual network scan, credential-based join or keyboard pairing has occurred yet.

**Current machine-readable authority:** [runtime/CURRENT_LINUX7_STATE.env](../../runtime/CURRENT_LINUX7_STATE.env) (unique fields). The older [PROJECT_STATE.env](../../runtime/PROJECT_STATE.env) retains extensive dated historical experiments and now links to current canonical values; do not parse old v018-v041 statuses as current. [docs/status.md](../status.md), [START_HERE.md](../../START_HERE.md), [README.md](../../README.md), [AGENTS.md](../../AGENTS.md), [documentation router](../README.md), [checkpoint index](../checkpoints/README.md) and [kernel patch tracker](../../patches/upstream/README.md) were cross-linked and updated.

**Power/USB intermittent issue remains unresolved:** Same v06.3 SHA first exhibited no-PONG/red LED then physically booted and loaded HCD. On recurrence removing both cables alone did NOT help; user's ~3-second Power hold after TWRP shutdown booted Android while short tap showed red light. Do not label PMIC fault, Bluetooth firmware defect, battery miscalibration or USB VBUS alone causal. Always preserve both positive/negative evidence and user observations.

**Continuity policy:** With every new physical or major offline milestone, immediately append measured results and immutable SHA/paths to THIS handoff, plus dated checkpoint, docs/status and runtime/CURRENT_LINUX7_STATE.env, update docs index/patch tracking. Keep sensitive identifiers and vendor firmware bytes off public GitHub. **No actual v06.4 build steps were performed in this documentation-audit turn.**

---


## Clarification: v06.3 was a firmware-only test, not the requested functional Linux environment

User pointed out that, despite previous discussion of **standard Wi-Fi scanning and a keyboard-usable on-screen terminal**, v06.3 contains neither. **The criticism is valid**: the assistant built v06.3 solely as a controlled HCD-firmware delta from v06.2, without including `iw`, `ip`, a shell, pairing agent or real terminal. The firmware-only scope was intentionally useful for A/B driver validation, but was insufficiently differentiated from the user's requested next *functional* build.

**Decision for subsequent work:** The next proposed image/environment must be planned around the actual user-visible capabilities, not another cosmetic dashboard version. Minimum explicit integration acceptance criteria: (1) real ARMHF `iw` (nl80211) with needed libraries and interface-up command, a user-triggered physical scan displaying BSS/channel/signal information with regulatory and privacy safeguards; (2) genuine terminal/shell on the Xoom display with input/output and USB fallback, not just test text; (3) appropriate BlueZ pairing/HID input path for the existing Motorola keyboard, staged and tested against real device capabilities. Keep the HCD-patched v06.3 as a validated rollback and isolate source changes in patch manifests; do not misrepresent optional software as already available.

**Packaging constraint:** The clean image has a roughly 8 MiB Android RAM-boot envelope. Before promising all BlueZ/D-Bus/console/runtime dependencies will fit in one initramfs, measure actual dependency and image sizes and consider a conventional Debian rootfs on approved removable storage if necessary. Never silently replace the no-microSD hardware-isolation baseline or write eMMC. Name a new candidate/version distinctly, record what functions are actually present, and test each acceptance condition physically.

**Current technical truth unchanged:** v06.3 has real BCM4329B1 firmware-path/HCI physical PASS and sequential BT→Wi-Fi PASS, but neither wireless scanning nor keyboard pairing nor terminal is implemented. The user wants these next, not another firmware-only validation advertised as meaningful OS functionality.


## 2026-10-25 19:13 EDT — LATEST LIVE RESULT: v06.3 BOOTS, HCD DRIVER PATCH, HCI UP/DOWN, BT→WI-FI PASS

**NEWEST STATE, supersedes the previous 18:53 “v06.3 NO PONG / RED LIGHT” passage and all historical statements that v06.2 is currently running.** The user recovered after the red LED recurred, and on the identical v06.3 image requested a new RAM-only fastboot boot. **The exact same SHA256 `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e` v06.3 image PHYSICALLY BOOTED** at 19:04 EDT, USB COM9/PID1 PONG passed 19:04:31 and stable 75-second observation passed 19:05:37. One early serial semaphore timeout recovered without action. Image was never flashed. **This refutes the claim v06.3 is intrinsically unable to boot**, but first failed attempt remains real and its power/USB/boot state root cause unresolved.

**New precise power-button observation:** Removing **both USB and power cables DID NOT clear** the red light this time. User booted Android using Power+Volume Up, shut it down; brief Power still red. Booted TWRP using Power+Volume Up, shut it down; brief Power again red, but **holding Power for ~3 seconds successfully booted original Android**, then Power+Volume Up entered fastboot. Do not over-attribute the earlier recovery to cable disconnection: **button hold duration and startup sequencing now matter**. This was recorded from user's direct physical actions, not inferred from a tool.

**Native v06.3 Bluetooth HCD firmware hardware PASS (bounded stage):** 19:08 EDT six modules (`ecc`, `ecdh_generic`, `cmac`, `bluetooth`, `btbcm`, `hci_uart`) loaded **rc 0**, `hci0` PRESENT, and Linux kernel logged `Bluetooth: hci0: BCM4329B1 'brcm/BCM4329B1.hcd' Patch`. Post-patch controller identification included `BCM4329B1 Generic FMRX 37.4 MHz`; USB PONG passed. **19:10** `BT_ON HCI_DEV_UP rc 0`, `BT_OFF HCI_DEV_DOWN rc 0`, then all six modules cleanly unloaded **rc 0**, hci0 ABSENT, USB PONG still PASS. The firmware was found/processed but no RF discovery, pairing, keyboard typing, or actual FM operation demonstrated.

**Whole BCM4329 sequential path STILL PASS with new HCD (19:12–19:13):** after the Bluetooth firmware/HCI session had stopped, one `WIFI_START` loaded brcmutil/brcmfmac/WCC **rc 0**, Wi-Fi firmware 4.220.48 initialized, **wlan0 PRESENT**. One `WIFI_STOP` removed **WCC rc 0, brcmfmac rc 0, brcmutil rc 0**, and wlan0 became absent. USB PONG remained PASS. **No Wi-Fi scan** yet: v06.3 has no `iw`, shell, or nl80211 userspace. Neither simultaneous Wi-Fi+BT nor electrical shared power-off was tested.

**Current confirmed DUT at 19:13 EDT:** v06.3 LIVE on replacement MZ600, no removable microSD, COM9 responsive, both Bluetooth and Wi-Fi kernel module stacks unloaded. Safely continue by developing standard Debian ARMHF `iw` scan support, `ip` interface-up handling and a real framebuffer/VT terminal plus pairing agent, while preserving v06.3 image and HCD hash. Firmware binary stays private; no flash/partition writes or upstream submissions.

**New canonical checkpoint:** [v06.3 RAM boot + BCM4329B1 HCD/HCI + Wi-Fi-after-BT PHYSICAL PASS](../checkpoints/MZ600_V063_PHYSICAL_PASS_HCD_HCI_AND_BLUETOOTH_TO_WIFI_2026-10-25.md). Raw PRIVATE Surface test logs: `MZ600-V063-hcd-firstboot-PRIVATE.log`, `MZ600-V063-HCD-BT-START-FIRST-20261025-PRIVATE.txt`, `MZ600-V063-HCD-BT-ON-OFF-20261025-PRIVATE.txt`, `MZ600-V063-WIFI-AFTER-HCD-BT-SEQUENCE-PRIVATE-20261025.txt`.

**Continuity rule:** This topmost 19:13 state supersedes the old entries BELOW. Append further measured changes at the top and update `runtime/PROJECT_STATE.env`, `docs/status.md`, and dated checkpoints after each physical test; preserve older contrary episodes as dated evidence.

---

## HISTORICAL 2026-10-25 18:53 EDT — first v06.3 NO PONG; RED LIGHT (later identical image PASSED)

**NEWER FACT OVERRIDING OLD LIVE-STATE TEXT BELOW:** At 18:50 EDT the formerly running **v06.2** successfully executed a guarded USB REBOOT and Surface verified original Android fully booted. At 18:51:28 EDT the exact checksum-pinned **v06.3 HCD candidate** (6,561,792B, SHA256 07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e) was accepted through fastboot boot on the verified replacement MZ600; no flash. COM9 appeared ~18:51:34 but first serial Write returned device not functioning; subsequent Open COM9 failed, 261 errors in observation, **NO PONG**, and Windows PnP indicated COM9 Unknown/unusable. User reported **red light again**. The tablet is not confirmed running Linux or original Android, and v06.2 is NO LONGER the currently live image.

**DO NOT BLAME HCD OR REJECT IMAGE:** v06.3 contains one added HCD file in embedded CPIO. Loading it requires BT_START, **which was never sent**. No Bluetooth or Wi-Fi activation, no scan, no subsequent device reboot. One unsuccessful boot attempt does not prove intrinsic v06.3 fault, and v06.2 had a similar prior transient no-PONG episode before it later physically passed. Compressed kernel payload/layout changes and board power/USB state remain open hypotheses.

**SAFE RECOVERY:** Stop all remote DUT operations. Ask user whether screen shows any early kernel text and take photograph before reset, if applicable. The prior successful physical recovery was **unplug BOTH USB and external power, then press ordinary Power alone**. Only if that fails consider OEM Power+Volume-Up forced reboot. Do not repeat blind fastboot boots, flash, or invoke unproven PMIC/BCM fixes. Private Surface logs: captures/MZ600-V063-hcd-firstboot-PRIVATE.log and captures/MZ600-V062-to-Android-before-v063-PRIVATE.log.

**Historical as-of 18:53 only (superseded by the later 19:13 physical PASS):** v06.2 was previously verified and no longer running; the first v06.3 attempt had no PONG/red light and HCD had not yet been requested. The exact same image subsequently booted, its HCD path was processed, HCI up/down passed, and Wi-Fi initialized afterward. Roadmap remains standard iw scanning, real framebuffer terminal and keyboard, and evidence-gated whole-chip regulator/USB power management. Full [physical checkpoint](../checkpoints/MZ600_V063_INITIAL_RAM_BOOT_NO_PONG_RED_LED_RECURRENCE_2026-10-25.md). Append findings to this handoff every turn.

---

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

**Current status:** v06.3 is now PHYSICALLY booted and its private BCM4329B1.hcd firmware path, HCI controller and subsequent Wi-Fi initialization have passed; earlier it was offline-only. Separately Debian 12 ARMHF `iw` 5.19 was downloaded, hash-verified and QEMU-smoked, but **has never run on the Xoom, and no Wi-Fi scan has occurred**.

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
| **v06.2 WCC teardown** | **6,549,504** | **`bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`** | **PRIOR v06.2 PHYSICAL PASS (protected baseline):** Linux/PID1/USB, Wi-Fi and Bluetooth lifecycle, sequential BT→Wi-Fi |
| **v06.3 private HCD** | **6,561,792** | **`07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`** | **PHYSICAL PASS on second identical-image boot:** USB/PONG, BCM4329B1 HCD path/hci0 up-down and sequential Wi-Fi/wlan0, both cleaned up; first earlier no-PONG/red-light attempt preserved |

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

**C. Bluetooth HCD + Motorola keyboard:** **v06.3 is already physically booted and its HCD/HCI and clean up/down tests PASSED**, so do not repeat that test by default. For **v06.4**, implement BlueZ/DBus or a validated pairing agent, HIDP/evdev input, passkey/PIN and user-controlled pairing; verify `/dev/input/event*`, actual keyboard typing into the real on-screen terminal, disconnect/reconnection, preserving USB fallback. See the dedicated v06.4 plan. Keep bonding keys secure; RAM-only no persistence unless a user-approved backing store exists.

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

**Boot image SHA256:** v06.1 `b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a`; **v06.2 physically proven prior baseline** `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`; **v06.3 CURRENT PHYSICAL PASS** `07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e`. **Private HCD SHA** `7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`. **Official armhf iw .deb SHA** `fd1f6c926853505b0eb03a3afb4c6b68e4350f42b140fe6c5295012eeca872ee`.

**Final reminder to the next agent:** Native Linux 7 v06.2 **works now** as USB/PID1 and standard separate Wi-Fi/Bluetooth hardware interfaces; both have been brought up and down cleanly; Wi-Fi also restarted successfully after Bluetooth in the same session. The next step is **real network scanning and a keyboard-driven on-screen terminal**, while validating private HCD and whole-chip power/coexistence using controlled experiments. Never flash or use the protected original Xoom; preserve exact working images, source patches, private firmware provenance and intermittent USB/charger/red-LED history.