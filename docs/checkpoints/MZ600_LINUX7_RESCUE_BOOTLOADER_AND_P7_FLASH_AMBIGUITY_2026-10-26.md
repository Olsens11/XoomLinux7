# MZ600 Linux7 independent recovery attempt and interrupted p7 flash — DO NOT INFER FLASH SUCCESS

## 2026-10-26 — definitive READ-ONLY p7 boot partition readback after interrupted fastboot attempt

Owner again signed in using private Debian credentials and `sudo -s`; shell `root@xoom-mz600:/home/xoom#` confirmed; remote read-only COM9 `id -u` = 0, `findmnt -n -o SOURCE,FSTYPE /` = `/dev/mmcblk1p1 ext4`, and internal p7 `/sys/class/block/mmcblk0p7/{start,size}` = `102400` / `16384` 512-byte sectors (**8MiB**). No p7 mount.

Physically read p7 without modifying it:
```bash
sha256sum /dev/mmcblk0p7
# 4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3 /dev/mmcblk0p7
head -c 6645760 /dev/mmcblk0p7 | sha256sum
# e560dea72ffd24dfcc38e9c89bddbb57bd210b0300c68bd76b46a07332d6f873 -
od -An -tx1 -N 8 /dev/mmcblk0p7
# 41 4e 44 52 4f 49 44 21  [ASCII ANDROID!]
```
**CONCLUSIVE RESULT:** exact whole-partition SHA256 matches stock original Android p7 8MiB private backup `android-HMJ37-boot-p7.img`. Stage-B image prefix expected SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba` is NOT present. The earlier PowerShell AVB warning terminated the flash BEFORE modifying p7; the ambiguity is **fully RESOLVED**. A second read-only root proof rechecked both SHA values; complete capture stored privately Surface `captures/MZ600-P7-READONLY-SHA256-PROOF-20261026.txt` (capture SHA256 `59c83d3350978786193808393f1da901323e86d347f1ca645564d3900386a0f5`). No internal eMMC writes or formats. Current replacement MZ600 physically running known Stage-B Debian 12 on inserted SD via USB COM9 at authenticated root prompt. Private login credential not displayed/logged. No need to retry flash until corrected host wrapper verified; next stage must capture fastboot stdout and stderr independently and check actual exit/status, verify writes by subsequent independent p7 readback before persistent reboot.


**Local time 2026-10-26 02:19–02:26 EDT.** Replacement experimental MZ600 only. This is the newest operational status and supersedes the live-stage-B/root-session claims in the earlier 01:48 checkpoint.

## Root access obtained by owner

User entered Debian sudo password privately in their own Surface USB console. Terminal showed root@xoom-mz600:/home/xoom#. Console disconnected with Ctrl+] (COM9 then opened remotely), and UID 0 independently confirmed on Linux7, /dev/mmcblk1p1 ext4 SD-root, internal BigPart p8 2,097,152 sectors.

## Linux-to-bootloader rescue probe — NOT ACCEPTED AS PASS

Kernel7 Tegra PMC notifier handles Linux REBOOT_CMD_RESTART2 with command bootloader, sets PMC scratch bit 30. Built tiny freestanding ARM32 EABI syscall 88 program scripts/experiments/mz600-arm32-reboot-to-bootloader-20261026.c. Executable 664 bytes SHA256 451847d8acda2526c93a7b02d4694f3e80fefacce6281417ce75ee4ee6a0bf14 compiled and independently verified on Desktop/Surface/on-device /tmp RAM. Validated UID 0, SD root, exact BigPart p8 and ELF hash before executing sync plus Linux RESTART2 bootloader.

At 02:19:56 EDT USB ttyGS0 disconnected. Expected MZ600 fastboot did NOT appear during ~50-sec verification window. Next surface scan showed original Android via ADB, ro.hardware=stingray, ro.product.device=stingray and sys.boot_completed=1; **reboot completed but bootloader mode selection FAILED**. Thus independent Linux reboot-to-bootloader is NOT proven and must not be used as rescue assumption. Android boot still works. Relevant private evidence Surface captures/MZ600-V064-Linux-PMC-Reboot-to-Fastboot-20261026-PRIVATE.log. No eMMC writes during this probe. OEM Android can still adb reboot bootloader, but that depends on current Android /system, which will disappear after p8 install.

## First persistent p7 Stage-B SD boot flash — STATUS UNVERIFIED / INTERRUPTED

After verifying original Android healthy and 100% battery, stock boot p7 backup 8,388,608B SHA256 4DA4C9F1486374BB66F31C96389CD1EE3067A447E8A72AEA33B2FC24AC3985E3 and original TWRP p6 backup 12,582,912B SHA256 EBE3F1C16CE9D79962433A60B0E63EC6E9F1D6392813601C264204D58B8BBEEC, an authorized one-shot PowerShell script Surface captures/MZ600-v064-StageB-Persistent-SD-Rescue-Boot-Once-20261026.ps1 entered fastboot verified product xoom-cdma unlocked.

At 02:24:42 it issued only fastboot flash boot <verified Stage-B image 6,645,760B sha b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba>. Fastboot printed **Warning: skip copying boot image avb footer (boot partition size: 0, boot image size: 6645760)** on stderr. PowerShell ErrorActionPreference Stop converted native stderr into a terminating NativeCommandError, aborting the script before recording a Sending/Writing OKAY status or reboot. **Do NOT assume flash was successful or that p7 is unchanged.** No other partition was targeted or modified by the script.

Surface fastboot was still connected. An independent SHA-checked **fastboot boot** of the same established Stage-B SD image (temporary RAM-only, no flash) succeeded, and Debian 12 ttyGS0 login reappeared. **CURRENT LIVE DEVICE** is fresh Stage-B temporary Linux7 Debian on 32GB microSD, at xoom-mz600 login prompt (new login needed). The current contents of p7 remain **UNKNOWN UNTIL READ-BACK**.

## Required next gate (safe, read-only)

1. Owner signs in via Surface interactive USB console using their known Debian password. Password never enters the chat, logs or repo; sudo -s to become root again. Then Ctrl+] releases serial. Session from before reboot is gone.
2. With verified root SD and p8 BigPart, hash raw internal p7 **read-only**. Compare complete 8MiB SHA to stock private boot backup; also compare first 6,645,760 bytes to staged Stage-B candidate to detect success. Use head -c 6645760 /dev/mmcblk0p7 | sha256sum or dd status none; *never write to /dev/mmcblk0p7 in this step*. Readback output kept private. If neither expected, p7 is ambiguous/partially written; keep bootable RAM-only SD Debian and do not format p8.
3. Before any further persistent p7 write, adjust PowerShell wrapper to capture stderr without terminating on harmless AVB-footer warning, check actual fastboot exit/status, then verify physical p7 readback. Never retry blindly.
4. Need reliable Android-independent recovery path. Broken Volume Down noted; owner has previously physically entered fastboot with Volume Up+Power, but this rescue after loss of Android /system should be revalidated. Persistent Stage-B boot from SD may provide normal boot after /system replaced if p7 flashed and verified, however Linux RESTART2-to-bootloader currently returns to Android and is not a reliable recovery mechanism.
5. **No p8 format, no internal Debian root install, no TWRP write, no GPT modification.** Stage-C internal p8 boot candidate still offline only. Continue using prior preflight-passed p8 installer only after all rescue gates.
