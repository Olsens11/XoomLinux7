# Stage-D internal Debian persistent p7 boot conversion — safety preflight passed, one-shot flash staged, WAITING FOR MANUAL FASTBOOT

**2026-10-26. Experimental replacement Motorola Xoom MZ600 ONLY.** The owner explicitly authorized making the twice-tested Stage-D direct-internal-root image persistent in boot p7. **STATUS OF THIS CHECKPOINT: PREPARED, NOT FLASHED, NO REBOOT.** Do not mistake a staged script for executed flash.

## Physical read-only checks performed

- Surface revalidated private full **8MiB factory Android boot p7 backup** `private-backups/replacement-mz600-2026-10-25/android-HMJ37-boot-p7.img` SHA256 `4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3`, exact 8,388,608B.
- Private **12MiB TWRP p6 recovery backup** `twrp-recovery-p6.img`, exact 12,582,912B SHA `ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`.
- Proven **persistent Stage-B SD-root boot rescue** `downloads/MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img`, 6,645,760B, SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`.
- **Stage-D internal-root candidate, boot-proven twice via temporary fastboot boot:** `downloads/MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img`, 6,645,760B, SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`. Despite retained original filename saying "UNTESTED", Stage-D **was physically booted twice**, COM9 Debian 12.15 login and `findmnt / = /dev/mmcblk0p8 ext4 /` confirmed. Only cmdline root selector differs from Stage-B. Stage-C/Stage-E GPT PARTUUID candidates FAILED and are NOT approved for persistent flash.
- At the start of this authorized conversion, the Xoom was physically **running Stage-D Debian 12.15 on internal `/dev/mmcblk0p8`** and owner had privately obtained root over COM9. A guarded read-only Xoom serial audit confirmed `id -u=0`, kernel release `7.0.0-next-20260422+`, `/dev/mmcblk0p8 ext4 /`, p7 start LBA102400 size16384 sectors (8MiB), BigPart p8 start118784 size2097152 (1GiB), and p8 `blkid UUID=c2fb0167-7143-4186-b284-c86d6c09ea64` equals installed `/etc/fstab` root `UUID=` field.
- **Critical real readback gate:** `head -c 6645760 /dev/mmcblk0p7 | sha256sum` returned `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`, proving the permanent p7 is STILL Stage-B SD-root rescue at this checkpoint, before intended conversion. The host parser failed an anchored `id -u` regex because of tty ANSI prompt/spacing, but all literal device readout values were correct. This was a host-formatting issue, **not** a failed device test.
- The module ABI/version mismatch remains **unfixed**: runtime `7.0.0-next-20260422+`, module tree/vermagic `7.0.0-next-20260422` (no plus). Wi-Fi and systemd D-Bus unresolved, but Stage-D internal Debian boots; not being represented as a fully functioning driver stack.
- Surface still saw **COM9 present / no fastboot device**, because user had not physically entered fastboot yet. Linux7 software `reboot bootloader` was previously untrusted. Owner reports repairing DC charging jack and volume button; has repeatedly entered fastboot and recovery manually.

## Flash script is staged, but not yet run

On Surface at:

`C:\Users\olsen\xoom-linux-rom\captures\MZ600-V064-Persist-StageD-InternalP8-Boot-ONCE-20261026.ps1`

SHA256 **`35b6761327b902a03d4cc63ec6a9716720412292a865d899a66dd387d3a6a32d`**, PowerShell AST syntax validation **0 errors**. This is a **one-shot flash-only** script, not an automatic reboot. It checks 4 local hashes/sizes, Stage-D cmdline `root=/dev/mmcblk0p8 rootwait rootfstype=ext4 init=/sbin/init`, rejects if COM9 is present instead of manual fastboot, checks **exact** fastboot serial `170061c243805617` and exactly 1 device, `getvar product=xoom-cdma`, `getvar unlocked=yes`. It refuses to overwrite existing evidence logs, executes **one** `fastboot flash boot <Stage-D>` via `Start-Process` to capture stderr separately and obtain native exit code, and requires both Sending and Writing with at least two `OKAY` acknowledgements. On any failure remains at fastboot without auto reboot. No p6, p8, p9, p10 or GPT write command in script.

**IMPORTANT:** Script has NOT run; private flash log `captures/MZ600-V064-STAGED-PERSISTENT-P7-StageD-FLASH-20261026.log` does not exist yet. Do not claim successful flashing or new persistent boot from this checkpoint.

## Next operator action

1. **Owner manually enters FASTBOOT** using repaired Power/Volume keys, SD card left inserted, keeping Surface USB cable attached, and reports "fastboot up". No generic software `reboot bootloader` substitution.
2. Assistant re-verifies exact Surface fastboot serial/product/unlocked status; invokes one-shot script **once**, inspects stderr/stdout, exits; if PASS then makes a separate guarded `fastboot reboot`.
3. Watch COM9 for ordinary Debian 12 login; privately sign in as xoom. Prove `findmnt -n -o SOURCE,FSTYPE /` = **`/dev/mmcblk0p8 ext4`**, not removable SD. Then owner reauthenticates `sudo -s` locally for actual **post-flash physical p7 prefix hash readback**, which must equal Stage-D image SHA `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`; full p7 8MiB hash will differ from 6,645,760B image.
4. Maintain Stage-B SD rescue image and original Android p7 backup on Surface. If Stage-D normal boot fails, use repaired physical buttons to enter fastboot and `fastboot boot` known-good Stage-B rescue and, if necessary, restore p7 Stage-B with verified one-shot fastboot flash. Leave p6 TWRP and GPT intact.
5. Update this checkpoint/handoff after real flash and physical readback. Do not conflate temporary Stage-D successes with unperformed persistent flash.


## 2026-10-26 — Flash attempt stopped before execution

Owner reported fastboot up. Surface confirmed the expected serial and the unchanged staged script SHA256. The script did not run because local PowerShell script execution was disabled, and subsequent remote commands could not be completed. The one-shot flash log was verified absent. **No p7 flash or reboot occurred in this turn.** Stage-D remains a temporary-boot-verified candidate; p7 remains the previously verified Stage-B SD-root image. Next action: obtain a permitted local execution path and confirm the target device and original safeguards before any write. Do not mark the persistent conversion as complete.

## Subsequent owner-executed native .CMD flash SUCCESS, normal internal Debian boot PHYSICAL PASS

On Monday, October 26, 2026, owner ran the prepared one-shot native Surface CMD file in Command Prompt (not through the blocked remote safety control). Actual user-provided CMD output after hash-checking original Android p7 boot backup, p6 TWRP backup, Stage-B rescue image and Stage-D internal-root image:

```text
MZ600_STAGE_D_CHECK_MODE=flash
HASH_SIZE_PASS: android-HMJ37-boot-p7.img
HASH_SIZE_PASS: twrp-recovery-p6.img
HASH_SIZE_PASS: MZ600-V064-BIGPART-DEBIAN-MICROSD-ROOT-TEMPBOOT-NOT-ON_DEVICE.img
HASH_SIZE_PASS: MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img
PREWRITE_CHECK_PASS: correct unlocked xoom-cdma; four image/backups exact size and sha256.
TARGET=p7 BOOT ONLY; p6 recovery, p8 Debian, GPT, p9/p10 and SD excluded.
FLASHING_P7_ONCE_NO_REBOOT...
Warning: skip copying boot image avb footer (boot partition size: 0, boot image size: 6645760).
Sending 'boot' (6490 KB) OKAY [1.188s]
Writing 'boot' OKAY [1.782s]
Finished. Total time: 8.656s
STAGE_D_P7_FLASH_ACK_VERIFIED_SUCCESS
NOT_REBOOTED_YET_REQUIRE_SEPARATE_NORMAL_REBOOT_AND_P7_READBACK
```

The AVB footer warning is routine for the legacy Xoom boot partition using modern fastboot tooling; Sending and Writing both succeeded. Surface independently inspected the script's physical local evidence files after execution: flash log exists, fastboot output exists, and recorded `FASTBOOT_NATIVE_EXIT_CODE=0` plus `FLASH_NATIVE_EXIT_0_SENDING_AND_WRITING_OKAY` confirms the actual one-shot write. At that point fastboot still showed exact experimental serial `170061c243805617`, USB COM9 absent.

Then assistant invoked one normal `fastboot reboot` (no `fastboot boot`), and independent Surface observation confirmed fastboot disappeared and USB COM9 returned. COM9 displayed the real banner `Debian GNU/Linux 12 xoom-mz600 ttyGS0` and login prompt. Existing approved private Surface login workflow authenticated user `xoom`. **Most important post-flash normal persistent-boot proof**:

```text
uname -r                             7.0.0-next-20260422+
cat /etc/debian_version               12.15
findmnt -n -o SOURCE,FSTYPE,TARGET /   /dev/mmcblk0p8 ext4 /
```

So Linux7 Debian 12.15 **NOW PHYSICALLY BOOTS PERSISTENTLY FROM INTERNAL eMMC p8** after the flash to p7. The launch did NOT use temporary fastboot boot. The internal root copied fstab entry still points to ext4 `UUID=c2fb0167-7143-4186-b284-c86d6c09ea64`. The p7 flash is confirmed at the bootloader protocol level and normal boot is proven; **a privileged on-device raw postflash p7 SHA256 READBACK IS STILL PENDING**, and must not be falsely marked done. Owner needs to reopen Surface USB console, `sudo -s` and supply Debian password locally (not in chat), then Ctrl+] to release COM9; assistant can run the read-only exact 6,645,760-byte p7 `head -c ... | sha256sum`, compare with Stage-D image hash `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`, and record full 8MiB p7 hash. The authenticated user shell `id -u=1000`, `sudo -n` exit 1 means privilege elevation is NOT available without owner interaction. Preserve existing p6 TWRP and SD Stage-B rescue image backups. Physical root internal p8 boot PASS, kernel modules mismatch and Wi-Fi still unresolved.
