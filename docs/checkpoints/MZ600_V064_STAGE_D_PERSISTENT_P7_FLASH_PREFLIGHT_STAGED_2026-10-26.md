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

