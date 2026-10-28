# XoomLinux7 — comprehensive handoff: hardware fastboot restored, cold BigPart p8 preserved on microSD and Surface

**Date:** 2026-10-28 (America/New_York). **Device:** experimental *replacement* Motorola Xoom MZ600 Stingray CDMA, **not** the protected original Xoom.

**Project:** [Olsens11/XoomLinux7](https://github.com/Olsens11/XoomLinux7), branch `wip/clean-wifi-bt-usb-20261025`. This handoff supersedes the **last-known-status** assertions in the earlier [preinstallation handoff](MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md), but that handoff, the kernel source manifests, original physical observations, and safety/workflow documents remain essential historical authority.

> **LATEST PHYSICALLY VERIFIED STOPPING POINT — READ FIRST.**
>
> 1. The user's **direct hardware-key fastboot entry works**. The previous *boot-menu Fastboot* selection briefly disappeared and returned to normal Linux without fastboot, but the direct key sequence displayed `Starting Fastboot protocol support`. Surface then **actually detected the same verified MZ600** in fastboot, `product=xoom-cdma`, `unlocked=yes`, `secure=no`.
> 2. On the Surface, a hash-guarded `fastboot boot` **temporarily booted the preexisting proven Stage-B BigPart-aware Debian from the rescue microSD**. Both sending and booting returned `OKAY`, exit 0; **no flash**.
> 3. Authentic USB COM9 login on the temporary Linux confirmed Debian 12.15, kernel `7.0.0-next-20260422+`, **root `/dev/mmcblk1p1` ext4**, and internal 1GiB BigPart `/dev/mmcblk0p8` **unmounted**.
> 4. The previously armed one-shot **cold backup** service actually ran. Its guards passed, wrote full **1,073,741,824B** `p8-cold.img` to rescue SD, SHA-compared copy and raw p8, ran offline read-only e2fsck, wrote `RESULT.txt` and `SHA256SUMS`, and attempted a software mode return. Surface subsequently saw the **original persistent internal Debian**, COM9 and Wi-Fi return.
> 5. User explicitly reauthenticated a **root shell** on the Surface COM9 and disconnected console with **Ctrl+]**, enabling controlled read-only verification. Root identity, MZ600 DT model, current internal p8 root, all virtual partition boundaries, rescue SD present/unmounted were physically rechecked **PASS**.
> 6. The rescue SD was temporarily mounted **read-only with journal replay disabled** at `/run/mz600-p8-cold-inspect-ro`. The backup directory contained `RESULT.txt`, `SHA256SUMS`, `e2fsck-readonly.txt` and complete `p8-cold.img`. A second full-image SHA check returned `p8-cold.img: OK`. **After verified transfer to Surface, that read-only SD mount was safely unmounted and its temporary mountpoint removed.**
> 7. **Verified cold backup SHA256 = `a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346`**, exact size 1,073,741,824 bytes. This is **NOT** the earlier live-mounted p8 hash.
> 8. **Important qualification:** saved `e2fsck -fn` completed five passes with **one free-block-count discrepancy**: `Free blocks count wrong (119757, counted=119756). Fix? no`. Do **not** call ext4 metadata perfectly clean or imply a tested restore. Raw bytes are SHA verified, **including an independent Surface off-device copy**, but filesystem/restore validation on a disposable duplicate is still required before destructive writes.
> 9. **OFF-DEVICE TRANSFER PASS:** A private pinned-TLS one-time Xoom-to-Surface receiver captured `p8-cold.img` to a separate Surface folder (not overwriting old `p8.img`); **Surface reopened and SHA-256 rehashed all 1GiB, MATCH**. Original SD metadata `RESULT.txt`, `SHA256SUMS`, `e2fsck-readonly.txt` preserved on Surface; one-time receiver stopped. Installed p7/p8/p6/p9/p10 and OEM GPT unchanged. New nine-review kernel / Debian image / BigPart TWRP **not deployed**.

## Immediate operational state and safety

- Live hardware: replacement MZ600 running **persistent** Debian GNU/Linux 12.15 from **internal `/dev/mmcblk0p8 ext4 /`**, kernel `7.0.0-next-20260422+`, Wi-Fi `wlan0` up with link, Surface COM9 reachable at 115200. The last host probe after Stage-B returned found root **UID 0** on COM9. Reconfirm at next entry: serial shell sessions can end.
- Rescue microSD: `/dev/mmcblk1p1` ext4, original Stage-B Debian root. Verification used `ro,relatime,norecovery` at `/run/mz600-p8-cold-inspect-ro`. **After successful off-device transfer, the temporary mount was unmounted and removed. Current rescue SD remains present, unmounted.**
- The cold backup's one-shot trigger marker **was removed/disarmed** when the service ran. It should **not automatically run again** on unrelated future Stage-B boots unless explicitly rearmed. Check the actual SD marker every time before booting. **The private Surface cold copy is now complete and independently verified.**
- Previous GPIO restart investigation: Linux `reboot(2) bootloader` with normal high-priority G3 GPIO returned to Linux rather than fastboot; root-only unbinding GPIO and trying PMC-only reboot (10:41 EDT) also failed, leaving device unresponsive until hardware intervention. These failures are **historical**; direct hardware fastboot is now **PHYSICALLY PASS** and the owner can use it. **Do not re-run GPIO/PMC reboot experiment or pretend the Linux-only reboot mode is fixed.**
- **Do not boot the existing TWRP**; its factory p10 starts **inside** the current expanded BigPart p8, and older recovery auto-mounted `/data` RW. Recovery p6 still contains TWRP 3.1.1-0 with **non-BigPart kernel**. Never flash an unvalidated Wingray-only recovery or downgrade to TWRP 2.x.
- Do not overwrite p8. The cold image is now held on **both rescue SD and private Surface**, independently SHA-verified on both. **Next critical gate:** test filesystem consistency and rollback against a throwaway **Surface copy**, preserving the two immutable originals. Treat the 1-block free-count mismatch explicitly.
- **Protected original Xoom and every other test device remain untouched.** No p6, p7, p8, p9, p10, boot0/boot1, GPT or firmware writes without separately scoped owner authorization plus backups/restore proof. Privacy: no raw private images, Wi-Fi credentials, device-unique data, proprietary firmware or test root passwords in public Git.

## Quick state matrix

| Milestone | Current evidence and result |
| --- | --- |
| Persistent old V31/Stage-D p7 + p8 Linux | **PHYSICAL PASS**, after return from rescue SD |
| Hardware-key fastboot + Surface identity | **PHYSICAL PASS** for actual MZ600 |
| Boot-menu-selected fastboot | Failed to remain in fastboot in user's observation; do not generalize |
| Software `reboot bootloader` | **FAIL**, both original GPIO and PMC-only trial; not solved |
| Verified Stage-B `fastboot boot` | **PHYSICAL PASS, RAM TEMPORARY, NO FLASH** |
| Stage-B microSD Debian / internal p8 unmounted | **PHYSICAL PASS** |
| Cold p8 copy on microSD | **PHYSICAL PASS**, one-shot script `RESULT.txt` present, SHA compare source vs file |
| Independent full-file SHA on microSD | **PASS** (`sha256sum p8-cold.img; sha256sum -c SHA256SUMS`), matching `a572...` |
| Offline image `e2fsck -fn` | Five passes completed; **ONE FREE-BLOCK COUNT DISCREPANCY**, no repair |
| Cold backup private off-device copy | **PASS** — private pinned-TLS 1GiB transfer, reopened/rehashed on Surface, identical SHA, original metadata copied, SD safely unmounted |
| End-to-end restore of cold p8 | **OPEN / HARD STOP before overwrite** |
| New nine-review kernel | Clean source + cross-build **PASS**, physical kernel boot **OPEN** |
| 41-package test Debian 1GiB ext4 | Assembled + independent offline SHA / fsck **PASS**, physical boot **OPEN** |
| MZ600 BigPart-aware TWRP 3.1.1-0 | Baseline audit **PASS**, new image **NOT BUILT / NOT FLASHED** |
| New persistent p6/p7/p8 deployment | **NONE** |
| Upstream Linux review posting | **NOT SUBMITTED; no fabricated human DCO** |

## Where all the evidence resides

**Surface** (`SURFACE-BOOK-2`): directly connected USB cable, Windows fastboot and COM9, private raw backup directory `%USERPROFILE%\xoom-linux-rom\private-backups\MZ600-V31-PREFLASH-20261028\`, pre-existing p6 recovery backup under `...\private-backups\replacement-mz600-2026-10-25\`, and exact local scripts under `...\inspection\`.

- `inspection/MZ600-StageB-Fastboot-Boot-ColdP8-20261028.ps1` — exact device, image byte count and SHA guard, only `fastboot boot`, physically executed PASS.
- `inspection/MZ600-P8-Cold-Verify-Root-Preflight-20261028.py` — genuine root UID0, original internal p8 root and 10-partition BigPart geometry, SD unmounted; **physical PASS**.
- `inspection/MZ600-Cold-P8-Mount-ReadOnly-Metadata-20261028.py` — validated root and geometry, created mount `/run/mz600-p8-cold-inspect-ro`, `ro,noload`, read manifest and fsck report; **PASS**.
- `inspection/MZ600-Cold-P8-Independent-SD-SHA-20261028.py` — independently read whole SD image, compared checksum and `SHA256SUMS`; output **`p8-cold.img: OK`**, `MZ600_SD_SHA_INDEPENDENT=PASS`; SHA `a572...`. ~99 seconds, exit 0. **Subsequent private Surface destination `private-backups/MZ600-V31-P8-COLD-20261028/p8-cold.img` (exact 1GiB) re-opened and rehashed PASS; the source SD mount was then unmounted.**
- `inspection/mz600-cold-p8-backup-with-return-20261028.sh`, `inspection/mz600-cold-p8-backup-20261028.service` — source of the SD one-shot backup; underlying private SD backup files verified via root COM9.
- The old Surface live backup `p8.img`, SHA256 `49aa3f3094df05b2f16aaa590fbb4d10cb29144647d28e57261cd19ab563f4a9`, was captured **while mounted RW**. **Never overwrite it with the new cold image or conflate their SHA.**

**On rescue microSD**, previously read via a temporary RO mount (now safely unmounted; not a Git file):
`/run/mz600-p8-cold-inspect-ro/var/backups/MZ600-V31-P8-COLD-20261028/`
- `p8-cold.img` — 1,073,741,824 bytes, SHA256 **`a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346`**.
- `SHA256SUMS` — one matching record for p8-cold.img.
- `RESULT.txt` — literal `MZ600_COLD_P8_BACKUP_PASS`, byte count, SHA, source p8, root microSD and `p8_mounted=NO`.
- `e2fsck-readonly.txt` — `e2fsck 1.47.0`, full five passes, `Free blocks count wrong (119757, counted=119756). Fix? no`, `xoom-system: 12880/65536 files ... 142387/262144 blocks`. Do not discard this warning.
- `/var/log/mz600-cold-p8-20261028.log` on the SD root records full transfer and readback event trace.

**Desktop GPU Windows + WSL** (`DESKTOP-R16QJD4`, Ubuntu-22.04):
- Public Git checkout: `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project`.
- Private kernel and Debian integration workspace: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`.
- Latest committed public status and patch manifests remain on branch `wip/clean-wifi-bt-usb-20261025`.
- Remote Desktop Commander is available; **always enumerate devices and use their current IDs** rather than presuming the prior agent process remains alive. For commands on Desktop WSL, use `wsl.exe -d Ubuntu-22.04 -- ...` or `-u root` only when necessary. For writing WSL files, Desktop Commander UNC `\\wsl$\Ubuntu-22.04\...`. Surface hosts the physical COM9.

## Essential reading sequence for the next conversation

**Do not rely solely on this handoff or the top of historical files.** Historical assertions such as "cold backup not captured", "fastboot unavailable" or "SD one-shot armed" are now superseded by the physical tests documented above. Source-of-truth decisions, QA and preservation policies still apply.

1. **`AGENTS.md`, `START_HERE.md`, `docs/process/DEVELOPMENT_WORKFLOW.md`**. Establish user/agent rules, exact source provenance, recordkeeping, owner permissions, protected-original-device restrictions and check-before-flash process.
2. **This handoff**, then [the immediate physical checkpoint](../checkpoints/MZ600_STAGEB_FASTBOOT_COLD_P8_CAPTURE_PENDING_RESULT_2026-10-28.md). **That earlier checkpoint was written BEFORE the authenticated root SD mount and independent full 1GiB SHA verification; it is a chronological record, not the final result.**
3. [The canonical comprehensive preinstallation chapter](MZ600_XOOMLINUX7_PREINSTALLATION_CHAPTER_COMPLETE_HANDOFF_2026-10-28.md), especially §§1–9, 11–15, which contain deep project reasoning and earlier full milestone inventory. **Its fastboot/cold-backup stopping-point text is stale.**
4. [The 08:19 software reboot fall-through](../checkpoints/MZ600_REBOOT2_BOOTLOADER_PHYSICAL_NORMAL_LINUX_FALLBACK_2026-10-28.md), [GPIO/PMC source analysis](../checkpoints/MZ600_FASTBOOT_REBOOT_GPIO_PRIORITY_ROOT_CAUSE_CANDIDATE_2026-10-28.md), [actual live preflight](../checkpoints/MZ600_REBOOT_GPIO_PMC_LIVE_UNPRIVILEGED_PREFLIGHT_PASS_2026-10-28.md), [10:41 PMC-only hang](../checkpoints/MZ600_GPIO_PMC_UNBIND_FASTBOOT_PHYSICAL_HANG_2026-10-28.md). **Hardware-button fastboot succeeding does not solve software reboot-to-bootloader.**
5. [V31 preflash preservation](../checkpoints/MZ600_V31_PREFLASH_PRESERVATION_AND_TEST_ROOT_2026-10-28.md), [one-GiB test root and recovery gates](../checkpoints/MZ600_ONE_GIB_ROOT_AND_BIGPART_RECOVERY_PLAN_2026-10-28.md), [TWRP 3.1.1-0 recovery audit](../checkpoints/MZ600_TWRP_3110_BIGPART_BASELINE_AUDIT_2026-10-28.md).
6. [Installed Stage-D vs nine-review exact-source audit](../checkpoints/MZ600_STAGE_D_INSTALLED_VS_NINE_PATCH_REVIEW_2026-10-28.md), `patches/upstream/INTEGRATION_SOURCE_MANIFEST_20261028.json`, `patches/upstream/REVIEW_TRACKS_20261028.md`, `patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md`. Do not confuse review-source build PASS with actual physical boot.
7. `packaging/firstboot/README.md`, `packaging/firstboot/manifest.json`, [offline Debian/COM9/screen kit checkpoint](../checkpoints/MZ600_FIRSTBOOT_WIFI_COM9_SCREEN_KIT_2026-10-28.md), [V31 physical WPA/HTTPS pass](../checkpoints/MZ600_V31_FIRST_REBOOT_AUTOCONNECT_FULL_STACK_PASS_2026-10-28.md).
8. [Previous comprehensive Wi-Fi/patch handoff](MZ600_XOOMLINUX7_COMPREHENSIVE_CANONICAL_PATCH_AND_WIFI_HANDOFF_2026-10-27.md) and other older milestone records for BCM4329 silicon/OEM implementation, event protocol, control paths and branches.
9. `docs/process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md`, `docs/process/EVIDENCE_AND_PRIVACY.md`, `docs/status.md`, `docs/README.md`, `runtime/PROJECT_STATE.env` for operator workflow, privacy, changes and indexes. Read current repository HEAD before relying on a remembered hash.

## Authoritative BigPart physical geometry

The OEM Motorola relocated GPT header sits at **LBA 62,513,151**, with independently validated header CRC in the saved raw backup. Current Linux7 BigPart is **in-memory reinterpretation only**, not an on-disk GPT rewrite. Hardware: internal `/dev/mmcblk0` **62,521,344 × 512B = 32,010,928,128 bytes**, name previously `MMC32G`; rescue SD `/dev/mmcblk1` (current root-capable p1 `/dev/mmcblk1p1`).

| Partition | Classic BigPart Linux-visible first LBA | Sectors | Size | Safety |
| --- | ---: | ---: | ---: | --- |
| p6 | 77824 | 24576 | 12MiB | Existing non-BigPart TWRP 3.1.1-0, private raw backup exists |
| p7 | 102400 | 16384 | 8MiB | Existing Stage-D persistent Linux boot; backed up |
| p8 | **118784** | **2097152** | **1GiB** | Current valuable internal Debian ext4 root; now backed up cold on SD |
| p9 | **2215936** | **1048576** | **512MiB** | Captured in earlier private reference; do not overwrite |
| p10 | **3264512** | **59247616** | **~28.25GiB** | **Not fully backed up**; never repartition/overwrite |
| eMMC boot0/boot1 | separate hardware areas | N/A | 2MiB each | Earlier private raw backup, no modification |

The *non-BigPart recovery* sees factory p8 only 256MiB, p9 ~169MiB, p10 beginning **LBA 989184** and potentially mounts p10 as `/data` even though that range physically overlaps the expanded Debian system. It is **not** safe for backups, fsck, mounting or flashing until its kernel and init both become BigPart-aware.

`p8-cold.img` is a block-for-block **1GiB image** of the *previous installed Debian*, different from the newly built *1GiB disposable root candidate*. Never confuse these two images, their SHA or their provenance.

## Previous live backups and firmware/device preservation

The Surface also preserves eight earlier **live source** images, independently rehashed and with redundant GPT-sector/header evidence. Directory: `%USERPROFILE%\xoom-linux-rom\private-backups\MZ600-V31-PREFLASH-20261028\`:

| Image | Bytes | SHA256 |
| --- | ---: | --- |
| p7.img | 8,388,608 | `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c` |
| **p8.img (LIVE RW)** | **1,073,741,824** | `49aa3f3094df05b2f16aaa590fbb4d10cb29144647d28e57261cd19ab563f4a9` |
| p9.img | 536,870,912 | `034e9157bc85ff4d9bdff0e395da7ee2db31a4ff8f4b602ad21940e1b8af52fa` |
| boot0.img | 2,097,152 | `c22364f520348801756a323320af312badd9828812b5474baf6577b5d0d144d2` |
| boot1.img | 2,097,152 | `ba07d590ab506d16b83b7801bae738da865a72f57bf4e61f0e97e57f2f755030` |
| head32m.img | 33,554,432 | `6efbef9153f93aaeb96a95086d14deace013cd60a917c3138c16939c2b1073f0` |
| head64m.img | 67,108,864 | `68ef635674149822109f6687708f9992322f2af263de419270162b633d0d8f51` |
| tail16m.img | 16,777,216 | `fb41be791b3858553b0ff34ef7381a892ebfc4c2fc4c6f7156b0c1e01058aab8` |

The 64MiB head includes p1-p7 and matches independent head32m first half bytewise; the alternate relocated GPT header had correct signature and CRC; p7 matched previously read-back persistent Stage-D. The p6 recovery source is separately captured at `private-backups/replacement-mz600-2026-10-25/twrp-recovery-p6.img` 12,582,912B SHA256 `ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`; its contents match p6 in head64m. The eight raw captures do **not** contain a complete p10 image and are **not a full 32GB eMMC backup**.

The new cold p8 on rescue SD is **a ninth distinct image**, and its independent **Surface copy is now verified** at `private-backups/MZ600-V31-P8-COLD-20261028/p8-cold.img`; sha `a5726126...`. It is stored in a **separate folder** from prior live-RW `p8.img`; no overwrite occurred. Private Surface also holds the SD's `RESULT.txt`, `SHA256SUMS`, `e2fsck-readonly.txt`, and `backup-transfer-verification.json`. One-time receiver terminated; original SD mount now unmounted.

## Kernel development history and newest review-source facts

**Mission:** Debian Linux 7 as the Xoom's conventional main OS, using proper Tegra/Motorola integration, BCM4329 full chip support (Wi-Fi, Bluetooth, later FM/audio/charging), per-device calibration/identity, working external/USB console and touchscreen, and a clean maintainer-quality upstream patch series. The owner demands **one logical problem per patch**, not artificial chronological Vxx fixups. Preserve clean-source independence and explicit lab-vs-review gates.

**Original physical Wi-Fi progress (older V11–V31 experiments):**
- Linux 7 BCM4329 SDIO F2 enable initially returned `-ETIME`; investigated regulator sequencing, WL_REG_ON/BT_REG_ON, 32kHz LPO, host runtime PM, clock stability, minimum >110ms after VDDC, NVRAM placement and Cortex-M3 firmware boot. The original Motorola 4.218.248.20 firmware finally scanned **5GHz channel 36 / 5180MHz**, producing four valid version-108 BSS entries exported to cfg80211. Firmware scan engine executed; terminal completion/events required separate driver work.
- Research distinguished `WLC_SCAN`+Event26, legacy `iscan/iscanresults` start/continue/abort, and `ESCAN`+Event69. The original Event26 could be missing despite scan data being available. Subsequent tested V31 lab code supported bounded unrestricted ESCAN, generation ownership/terminal matching, cautious malformed Event69 attribution and conditional WLC_UP.
- Installed V31 eventually **physically completed WPA2-PSK CCMP, DHCP, DNS, NTP and verified HTTPS 200**, but association took **~399 seconds**. Immediate cause not proved: suspect incompatible legacy connection-event header/indices, firmware state or connection path. **No clean review-source MZ600 RF/association claim** is justified from these older experimental V31 results.
- Bluetooth HCI and private BCM4329B1 HCD have historical experiments; full coexistence/BT/FM and suspend/charging are NOT finished.

**Kernel source/review provenance:**
- Public repository: `Olsens11/XoomLinux7`, branch `wip/clean-wifi-bt-usb-20261025`. Pinned upstream source `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; clean nine-patch inner Linux source tip `507eb069df819cb5cc801ad8be096f70d9ca7609`.
- **Exactly nine scoped review candidates:** DT-01..03 under `patches/upstream/review-stingray-dt-20261028`; BOOT-01 vendor MAC ATAG→FDT under `review-arm-atag-20261028`; WIFI-01..04 under `review-wifi-four-logical-20261028`; STORAGE-01 conservative in-memory Xoom BigPart under `review-storage-bigpart-20261028`. Previous `review-wifi-v2-20261028` 3-patch alternative and older monolithic experiments are archival; **do not apply both Wi-Fi variants**.
- Review intent: 3 DT commits = binding-compatible tuples, shared Wingray electronics refactor, Stingray MZ600 wrapper/USB; ARM boot = factory WLAN MAC ATAG bounded FDT handoff; Wi-Fi = WLC_GET_VALID_CHANNELS fallback, ESCAN transaction generation/ownership, malformed-index genuine Event69 completion only, conditional WLC_UP before scan; storage = MZ600 BigPart only under explicit compile-time/boot opt-in with valid relocated GPT and exact geometry.
- **Full exact-source ARM `zImage dtbs modules` cross-build PASS.** New zImage 5,826,528B SHA256 `570c98f1ce187f33c46cc671bb54b0e7b4837756bbec97ef721f8b4c998a5cf1`; Stingray DTB SHA256 `c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa`; config/kernel release `7.0.0-next-20260422+`.
- **114 exact matching new modules** compiled/installed into separate disposable Debian root and `depmod`/brcmfmac dependency checked. Installed Stage-D uses *older* Broadcom ABI/module exports (at least three `Module.symvers` CRC differences) despite identical `uname -r`. **Never mix compiled modules from these two kernels.**
- **New BigPart argument** is `gpt xoom_bigpart=1` plus `CONFIG_MOTOROLA_XOOM_BIGPART=y`; old Stage-D `gpt_sector=` and `motorola,xoom-bigpart` DT property do NOT enable the cleaned parser. A new boot artifact omitting the correct option can see factory partitions and corrupt or fail to mount p8. Verify before ever booting new kernel.
- DT schema/human maintainer review, exact-source physical boot and wifi, Bluetooth/SDIO/power interactions, P2P, cfg80211 cancellation/timeout and chipset regressions are open. **No maintainer submission, no human DCO signoff and no claim of upstream acceptance.** Recovery and OS packaging are separate artifacts, NOT additional source patches.

## Debian first-boot / Wi-Fi test OS packaging: prepared, not installed

The owner wants a **standard persistent Debian Bookworm armhf OS** that boots normally from p7/p8 when ultimately qualified. First test should have `NetworkManager`, `nmtui` for SSID/password selection and automatic DHCP, `nmcli`, `ping`, `curl`, `iw`, CA trust and time sync; preserve COM9 rescue and give an actually usable tablet screen/TTY. The owner explicitly requested a simple **temporary local root password in the disposable test image**. It was configured privately and root password-based SSH remains disabled; the running V31 installation's credentials were **not** changed.

In Desktop WSL private directory `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/`, an isolated Debian 12 Bookworm ARMhf root clone was created, with **41 authenticated Debian packages** installed via QEMU ARM binfmt chroot, NetworkManager as exclusive `wlan0` manager, legacy `systemd-networkd`/`wpa_supplicant@wlan0` disabled *only in the disposable root*, time sync and getty@tty1/serial-getty@ttyGS0 enabled. OEM MZ600 BCM4329 binary + NVRAM and 114 matched review-source modules added **privately**. Dependency resolution and offline userspace/package checks passed.

**Different filesystem images, do NOT confuse:**

| Private image | Size | SHA256 | Meaning |
| --- | ---: | --- | --- |
| `XoomLinux7-test-root-bookworm-armhf-20261028.img` | 2,147,483,648 bytes | `b7180b88dfacf29b41bdb515d4d1a5226855fb2065ca8423ea69029a1362a70d` | Original large ext4 regular-file test root, 5-pass fsck PASS |
| `XoomLinux7-test-root-1GiB-BigPart-20261028.img` | 1,073,741,824 bytes | `9cf413dcf1305e3dbabc13dc2d478ad5d481bfb4da2260cee1de16a59f9c6d31` | Main separately copied **1GiB** BigPart-sized derivative, resized with `resize2fs`, five-pass fsck PASS, 13,727 used inodes, 116,787 free 4KiB blocks |
| `XoomLinux7-test-root-bookworm-armhf-bigpart1g-20261028.img` | 1,073,741,824 bytes | `8a7349948b1cc0b3497068eff75345086c8845415901a1f69c68aead4bd6264a` | Another separately built 1GiB variant recorded in earlier handoff; **not byte-identical**, compare before choosing |
| **`p8-cold.img` on rescue SD** | **1,073,741,824 bytes** | **`a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346`** | **BACKUP of OLD INSTALLED V31**, not new Debian root |

The nominal **2GiB image did not imply 2GiB of files**: prior `resize2fs -P` minimum estimate ~849MiB and offline successful 1GiB resize prove classic **1GiB BigPart suffices** for the current new Debian contents. **Do not invent or apply "SuperBigPart"** just because the original sparse capacity was 2GiB. Expanding p8 beyond 1GiB would entail coordinated in-memory p8/p9/p10 mapping, recovery, backups and physical risk; no need now.

Generic 41-package offline archive `XoomLinux7-FirstBoot-Online-Console-v2-20261028.tar.gz`, SHA256 `224a72c2b09cf3eb9eb073f8df8d68a50a1994459d1317c44e33fa3b15cfbfb2`, has **no private firmware/password**. Public packaging scripts `packaging/firstboot/clone-disposable-debian-root.sh`, `install-offline-disposable-root.sh`, `build-disposable-ext4-image.sh`, README and manifest. Private assembled images **must not be pushed to GitHub**.

**Still untested:** a new correctly built Android-format nine-patch boot image, new kernel's actual MZ600 boot, module-driver runtime ABI, framebuffer pixels and keyboard/touch typing, `nmtui` on tablet, SSID association/DHCP with NetworkManager, quick reconnections, HTTPS, 2.4/5GHz channel regulations, power/BT/FM. A touchscreen input node does not constitute an implemented on-screen keyboard.

## Recovery/TWRP track: why and how

The owner wants **TWRP 3.1.1-0**, updated for **existing classic 1GiB BigPart** and usable with the Debian OS, rather than a new partition scheme or downgrade. See [TWRP 3.1.1-0 baseline audit](../checkpoints/MZ600_TWRP_3110_BIGPART_BASELINE_AUDIT_2026-10-28.md).

Private exact p6 raw recovery backup SHA256 `ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec` (12,582,912B). Existing boot image has Android magic, 2048B pages, 3,435,708B legacy kernel and 3,953,970B gzip ramdisk; uncompressed ramdisk 7,770,880B and 431 CPIO entries. Version string `3.1.1-0`; `omni_wingray-eng 4.4.4...` base. Current TWRP kernel still exposes **stock** partition layout. `recovery.fstab` contains factory by-name paths and `length=-4096/-16384` offsets. **Just changing fstab, kernel command line or a screen does not change partition extents**. Need a BigPart-capable recovery kernel with correct relocated-GPT partition parser and strict MZ600 checks, plus safe recovery init/no auto mounts.

Available historical Wingray BigPart TWRP 2.x releases and older kernel patches are research references, **not verified replacement TWRP 3.1.1-0 for Stingray MZ600**. Requirements: exactly correct MZ600 hardware/board, p8/p9/p10 map, preserve p1-p7, safe ADB/USB serial, display/touch, SD backup/restoration, image <=12,582,912 bytes. Test **temporary `fastboot boot`** with no internal automount/wipe before any authorized p6 flash. Physical direct-key fastboot now works, so reversible test path is demonstrably viable. Preserve old p6 until tested and user explicitly authorizes p6-only flash/readback.

## Ordered next-session execution plan — safest path from current stopping point

### Gate 0: verify the latest status, protect live system

- Read this handoff, `AGENTS.md`, preinstallation historical handoff and TWRP audit. Check Git HEAD + changes. Enumerate connected Desktop Commander devices and identify Surface physically connected to **replacement** MZ600; never use the original Xoom.
- Read-only COM9: prove root shell still authorized or ask owner to establish `sudo -s` through existing private USB console; verify `id -u=0`, kernel, model, **internal p8 root**, p8/p9/p10 exact sectors, USB serial, rescue SD identity and **SD unmounted**. The prior `/run/mz600-p8-cold-inspect-ro` mount was deliberately cleaned up after transfer. No live device action is needed to work with the independent Surface copy.
- **No reboot, no active USB serial shell and no new Stage-B test is needed** for immediate **offline copy-only verification** of the now Surface-resident cold image. Don't use the non-BigPart TWRP or the broken software mode-reboot path.

### Gate 1 (COMPLETED): private off-device cold p8 backup transfer, verification and cleanup

- Original temporary on-Xoom RO SD path was `/run/mz600-p8-cold-inspect-ro/var/backups/MZ600-V31-P8-COLD-20261028/p8-cold.img`; the source was independently SHA-verified and **later unmounted**. On next access verify its mountpoint state first, do not assume still mounted.
- **DONE:** copied 1GiB directly from SD RO mount to unique Surface private directory `%USERPROFILE%\xoom-linux-rom\private-backups\MZ600-V31-P8-COLD-20261028\p8-cold.img`, preserving old live `MZ600-V31-PREFLASH-20261028\p8.img` untouched.
- **DONE:** dedicated one-time public-key-pinned HTTPS receiver and COM9 sender were created as `inspection/MZ600-Cold-P8-TLS-Receiver-20261028.py` and `MZ600-Cold-P8-TLS-Sender-COM9-20261028.py`; source was the SD RO file (not live p8). Both reported PASS, HTTP 200 and exit 0. Listener terminated. Sensitive token/keys and raw image stayed on authorized hosts.
- **DONE:** Surface reopened and SHA-256 rehashed full 1,073,741,824B file, exact `a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346`. Copied SD reports `RESULT.txt` (171B), `SHA256SUMS` (78B), `e2fsck-readonly.txt` (437B) and metadata; source SD copy intact. `inspection/MZ600-Cold-P8-SD-ReadOnly-Unmount-20261028.py` subsequently unmounted SD RO.
- **DONE:** `backup-transfer-verification.json` records private capture/transport and hash verification. Keep both SD original and Surface copy immutable, and consider additional independent storage. **Next task is Gate 2 copy-only filesystem/restore validation**, not another cold backup.

### Gate 2: investigate minor filesystem discrepancy without risking unique evidence

- The **raw image bytes are authenticated and complete**; the e2fsck 5-pass report also says `Free blocks count wrong (119757, counted=119756). Fix? no` and was run **read-only**. Do not silently claim perfect ext4 consistency just because `e2fsck -fn` returned zero in the script.
- **The second Surface copy is already verified.** Create a **third, disposable duplicate** of the Surface `p8-cold.img`; run `e2fsck -fn` with a compatible toolchain and record exact diagnostics, then determine whether the one-block free counter discrepancy is journal/unmount residue, metadata accounting or something else. If warranted, perform **offline repair** on that disposable duplicate only, never the SD source or immutable Surface original; run clean five-pass fsck and a loop/test-target read-only filesystem mount/restore exercise. Preserve a record of every difference.
- Formal **restore strategy** must be written and verified: correct p8 boundaries, original p7 boot image hash and boot args, exact module compatibility, safe externally booted SD or verified recovery route, no p10/GPT writes, independent post-restore readback SHA, and recovery of access if new kernel fails. Do not proceed to p8 overwrite until accepted.

### Gate 3: finalize BigPart TWRP 3.1.1-0 recovery replacement

- Start from **exact p6 binary audit**, source review and compatible kernel build. Preserve all UI/ramdisk functions while upgrading partition parser/DT and neutralizing unsafe mounts. Do not transplant a Wingray 2.x image without source/device compatibility and validation.
- Build hash-locked recovery image fitting 12MiB. **Use hardware direct fastboot + temporary `fastboot boot`**, then verify MZ600 model, BigPart p8/p9/p10 sectors, p1-p7, no p8/p9/p10 RW mounts, TWRP ADB/USB, display/touch, SD access, fstab/restore mapping. **Do not use TWRP's install/wipe/format/conversion functions in first test**.
- Only with cold backup off-host, known-good p6 recovery image, restore procedure, passed physical temp boot and owner approval may p6-only flash/readback be attempted. Do not couple recovery installation to replacing p8.

### Gate 4: new Linux 7 nine-review kernel + Debian firstboot qualification

- Freeze exact nine-review source and test-image SHA; ensure new Android boot header/ramdisk compatible with p7 capacity and correct Stingray DTB. Include **`gpt xoom_bigpart=1`** and compatible `root=/dev/mmcblk0p8` or separately proven removable-root selector. Do **not** put the disposable 1GiB new filesystem into live p8 just to try it.
- Prefer prepare a **separate/removable test root** and `fastboot boot` temporary kernel first, using accurate media and bootargs. Existing SD is the **rescue/backup drive**, not a blank scratch target; avoid overwriting it absent backup/explicit permission. Boot exact new source with matching 114 modules and firmware, preserving physical Stage-D baseline.
- Verify serial COM9, systemd, `/dev/fb0`, tty1, local screen input, `nmtui`, WPA2/DHCP/DNS/time/HTTPS and repeated association latency, 2.4/5GHz scanning, firmware events and cfg80211 ownership, power/BT interactions. Prior V31 successful RF scan and HTTPS do **not** validate new review source.
- Only after reproducible temporary boots and verified rollback, authorize any **specific** p7/p8 persistent write. Protect GPT, p9/p10, per-device identity and recovery. Test boot/readback/hash after every phase.

### Gate 5: finish upstream review separately

- Keep nine scoped patches and per-area maintainer routing independent; perform exact-source replay, checkpatch, DT binding, ABI checks, full ARM build, test specific dependencies physically. Handle slow association, BT, power and scan lifecycle as their own justified source issues, not one broad downstream dump. Submit only after owner approval and **human-supplied DCO**.

## Tooling instructions for a fresh assistant

- **Desktop Commander** tools are available through `functions.exec`: discover `mcp__Remote_Desktop_Commander__list_devices`, `start_process`, `read_process_output`, `read_file`, `write_file`, `edit_block`, etc. Tool names normalized on `tools`; inspect `ALL_TOOLS` for schemas. Run `list_devices({})` before selecting Surface or Desktop. Do **not** run `functions.exec` in parallel with other tools.
- Desktop WSL: invoke `wsl.exe -d Ubuntu-22.04 -- <command>` on `DESKTOP-R16QJD4`; root when necessary `wsl.exe -d Ubuntu-22.04 -u root -- <command>`. Complex PowerShell/WSL nested quoting can cause breakage; write small `.sh` via WSL UNC to exact private source tree and invoke it explicitly. Read/commit public docs in `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project`.
- Surface: physical Xoom USB serial port `COM9`; fastboot executable in installed Google Platform Tools, detect actual location. Existing `%USERPROFILE%\xoom-linux-rom\downloads\Start-Xoom-USB-Console.ps1` allows owner root auth. **One COM9 serial owner at a time**; Ctrl+] releases existing interactive console. Python 3.13 and `pyserial` available. Check prompt and exact MZ600 identity before sending commands; don't record password.
- Surface cold-backup guarded probes are under `%USERPROFILE%\xoom-linux-rom\inspection\`, including the passing `MZ600-Cold-P8-Independent-SD-SHA-20261028.py`, later pinned-TLS receiver/sender, metadata capture and successful RO-SD-unmount script. Their PIDs are historical. **For the immediate offline investigation prefer the verified Surface `MZ600-V31-P8-COLD-20261028\p8-cold.img`**, not a new device mount or COM9 transaction. Use exact private paths and preserve source evidence.
- **No auto/background actions remain promised or guaranteed**; continue only in actual future turn with freshly verified device state. Do not claim task completeness from a file name or previous tool PID. Preserve all milestones as evidence in sanitized GitHub docs with references and update `START_HERE.md`, README/handoff indices and `runtime/PROJECT_STATE.env`.
- **Avoid publishing** passwords, private raw binary images, OTP/factory MAC, device full serial, SSID/PSK, HCD/firmware/NVRAM, proprietary backup data and remote authentication material. Source code, redacted facts and hashes may be committed. Never automatically `Signed-off-by` another person's kernel patch.

## Closure summary for seamless continuation

**Fastboot hardware recovered; BigPart Stage-B microSD-root temporary boot physically worked; unmounted raw p8 backup exists on rescue SD; both microSD and the separate Surface 1GiB copy have been independently rehashed with exactly matching SHA256; original backup reports preserved, temporary RO-SD mount unmounted, old persistent Debian healthy; NO flash occurred.**

**The task to take up FIRST in the next chat is:** use the now independently verified **Surface cold image** to create a **disposable third copy**, investigate/possibly repair the single ext4 free-block-counter mismatch on **that copy only**, and document a credible p8 restoration and rollback test. Next prepare and **temporary fastboot-boot** a BigPart-aware TWRP 3.1.1-0 candidate; no p6 flash until backup/restore and recovery read-only tests pass. The original SD is **currently unmounted** and both verified original raw copies stay immutable. Kernel/new Debian integration and upstream review follow the staged plan above.
