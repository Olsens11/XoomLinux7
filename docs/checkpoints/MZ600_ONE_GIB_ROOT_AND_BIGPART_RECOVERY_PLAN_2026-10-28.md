# MZ600 — 1 GiB BigPart root feasibility and recovery strategy (2026-10-28)

**Actual offline result: SUCCESS. No Xoom device writes/reboot/flash.** This
revises the previous question about fitting a 2 GiB ext4 *container image*
into 1 GiB p8. A container's nominal capacity is not the allocated contents.

## Measured complete test-root filesystem

Source: private WSL `XoomLinux7-test-root-bookworm-armhf-20261028.img`,
2,147,483,648 bytes, SHA256
`b7180b88dfacf29b41bdb515d4d1a5226855fb2065ca8423ea69029a1362a70d`.
It is built with 41 official Debian ARMhf packages, private MZ600 BCM4329
firmware/NVRAM, 114 nine-review matched modules, user-selected temporary
test-root password and NetworkManager/nmtui. Source retained unchanged.

**Read-only `resize2fs -P` estimated minimum 217,408 × 4096 blocks
= 890,503,168 bytes (849.25 MiB).** Created a **separate file copy**
(not a device), ran offline `e2fsck -fy`, `resize2fs FILE 262144`,
then `truncate -s 1073741824`. A further offline five-pass
`e2fsck -fn` passed. Its exact size matches BigPart p8, 2,097,152 ×
512B = 1,073,741,824B.

Result file (PRIVATE, not in GitHub):
`/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/XoomLinux7-test-root-1GiB-BigPart-20261028.img`
- Exact bytes: **1,073,741,824**
- SHA256: **9cf413dcf1305e3dbabc13dc2d478ad5d481bfb4da2260cee1de16a59f9c6d31**
- ext4 label `XOOMTEST`, filesystem clean
- block count **262144**, free blocks **116787**,
  used blocks **145357**, block size **4096**
- 13,727 used inodes / 65,536 total, 5-pass fsck PASS
- Approx **567.8 MiB allocated**, **456.2 MiB free** within
  the 1 GiB partition. No need for a new 2 GiB partition scheme
  for the *current* test image.

**This new 1GiB root has not been booted and is NOT permission to
overwrite the installed p8.** Ext4 fsck confirms structural integrity
but not complete app/runtime functionality or bootloader readiness.
Keep 2 GiB source and 1 GiB shrunken derivative independently hashed.

## BigPart vs proposed 'SuperBigPart'

Current BigPart is an IN-MEMORY reinterpretation of factory GPT:
p8 start 118784 size **2097152 sectors** (1GiB),
p9 start 2215936 size **1048576 sectors** (512MiB),
p10 start 3264512 size **59247616 sectors** (~28.93GiB).
Actual on-disk alternate GPT still contains original factory geometry.
The proposed 2GiB p8 would require a NEW coherent virtual mapping
and all consumer kernels/recovery/tools to agree, while leaving
p1..p7 and OEM GPT untouched. It would move p9/p10 starts, invalidate
existing p9/p10 virtual mapping, and entail new backup/test gates.
This change is unnecessary for the current ~568MiB root and is
NOT part of the nine-patch upstream RFC.

## Recovery compatibility

The original TWRP 3.1.1-0 on the tablet is non-BigPart. Past
read-only recovery checks showed its kernel seeing factory p8 256MiB,
p9 ~169MiB and p10 starting 989184, a range overlapping today's
expanded Debian p8. TWRP has historically auto-mounted /data RW;
**do not boot that recovery while protecting the installed Debian p8**.

Historic external **TWRP 2.8.6.0 Wingray BigPart** releases are
documented, but their labels say MZ604/MZ606, not the user's
Stingray MZ600; no candidate has been booted or verified in
the current work. Do not blindly flash such an image or run its
format/partition-conversion procedure on the MZ600.

Use a safer order:
1. Preserve the already verified live capture and p6 original TWRP
   backup. Independently verify an available **Stage-B BigPart-aware,
   Debian microSD-root** temporary boot image SHA256
   `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`
   (6,645,760B). Stage-B was physically proven on this MZ600:
   `fastboot boot` brought Debian from removable `mmcblk1p1`
   with internal `mmcblk0p8` **UNMOUNTED**, correct BigPart extents
   and ttyGS0 COM9 login.
2. User enters **fastboot only**, with the verified existing rescue
   microSD. Check device identity, media and SHA before any
   `fastboot boot`. Never `fastboot flash` at this stage.
3. Once booted to Stage-B, prove `findmnt` shows root on microSD and
   **no mount on any internal mmcblk0p8**. Then create **cold**
   1GiB p8 bit-copy and SHA record, safely send to private Surface or
   use a separately identified free location on SD. Do not rely on
   a live RW capture as a cold restore-quality snapshot.
4. Only **after** the cold p8 copy verifies, test a candidate
   BigPart-aware recovery using `fastboot boot` first, never p6
   flash first. Prove correct p8/p9/p10 sectors and no automatic
   mounts or format steps. Check MZ600/Stingray identity,
   touch, ADB/USB, SD, recovery partition size <=12MiB.
5. If a BigPart TWRP candidate passes all read-only tests and
   original p6 recovery raw image/restore is verified, separately
   authorize permanent **p6-only** flash and readback; never
   use its “repartition,” wipe or conversion UI without backups.
   Preserve known V31 kernel p7/p8 and do not overwrite p10.
6. A 1GiB rootfs deployment to p8 itself remains a **separate**
   explicit destructive decision, after filesystem-consistent
   rollback and boot qualification.

## Result

**1 GiB test root image = BUILT, SHA LOCKED, FIVE-PASS FSCK PASS.
Cold p8 and BigPart recovery physical validation = OPEN.
No new GPT scheme, no boot/recovery flash, no mounted-device writes.**
