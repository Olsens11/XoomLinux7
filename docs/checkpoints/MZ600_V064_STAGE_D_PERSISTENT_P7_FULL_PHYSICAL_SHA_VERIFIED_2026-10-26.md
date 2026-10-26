# MZ600 Linux7 v064: PERSISTENT INTERNAL DEBIAN INSTALL AND PHYSICAL P7 SHA VERIFICATION COMPLETE

**Date:** 2026-10-26. **Device:** explicitly authorized experimental *replacement* Motorola Xoom MZ600; do not confuse with owner's protected original Xoom.

**MILESTONE: FINAL PHYSICAL PASS** — owner booted into Debian Linux 7 after a locally executed permanent Stage-D flash of p7; normal restart worked with internal BigPart p8 root; user authenticated to Debian and entered `sudo -s` locally over Surface COM9; **the actual p7 raw eMMC partition was then read and SHA-256 verified**, not merely host image hashed. This checkpoint supersedes earlier documentation saying that post-flash p7 SHA was pending.

## User-supplied physical root-console readback

Owner reported the following results from the live Xoom root console, using read-only commands:

```console
root@xoom-mz600:/home/xoom# id -u
0
root@xoom-mz600:/home/xoom# findmnt -n -o SOURCE,FSTYPE /
/dev/mmcblk0p8 ext4
root@xoom-mz600:/home/xoom# cat /sys/class/block/mmcblk0p7/size
16384
root@xoom-mz600:/home/xoom# head -c 6645760 /dev/mmcblk0p7 | sha256sum
fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8  -
root@xoom-mz600:/home/xoom# sha256sum /dev/mmcblk0p7
901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c  /dev/mmcblk0p7
```

**Verified:** `id -u=0`; active `/` device is internal `/dev/mmcblk0p8` ext4; p7 geometry exactly 16,384 x 512-byte sectors = **8,388,608B (8MiB)**; first **6,645,760 bytes** of **physical p7** match *byte-for-byte via SHA256* the known good Stage-D internal-root Linux7 boot image. **Stage-D source image SHA256** was `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`, and physical p7 has that exact same digest over the matching 6,645,760-byte region. **Full actual 8MiB p7 partition SHA256** now recorded as `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`. The full p7 partition hash is *expected to differ* from the shorter boot image SHA256 because it includes 1,742,848 trailing bytes.

Some characters in the echoed pasted shell commands appeared interleaved due to serial console behavior, but each actual command subsequently appeared on its own prompt and returned unambiguous outputs above. There is no reason to reflash or retry.

## How persistent internal Debian was achieved and independently boot proven

1. Previously Debian 12.15 was installed on BigPart internal `/dev/mmcblk0p8` **1GiB ext4**, physical `e2fsck` pass; `/etc/fstab` root selector corrected to stable ext4 filesystem `UUID=c2fb0167-7143-4186-b284-c86d6c09ea64`. The *GPT PARTUUID* exposed by the kernel changes between boots, so don't use it for p8 kernel root selection. Proven kernel commandline stays `root=/dev/mmcblk0p8 rootfstype=ext4 rootwait rw init=/sbin/init`.
2. **Stage-D image** (6,645,760 bytes, SHA `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`) booted **twice temporarily** from fastboot and physically returned Debian login with `findmnt /` internal p8. Separate preserved rescue images include factory Android p7 and TWRP recovery p6 (full backups on Surface) and Stage-B SD-root Linux7 boot image `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`.
3. Owner explicitly authorized permanent switch to Stage-D p7; original backups and images fully verified; owner ran native Surface `MZ600-V064-Persist-StageD-InternalP8-Boot-ONCE-20261026.cmd flash` locally because remote launch was disallowed. It verified all hashes and target fastboot serial `170061c243805617`, `xoom-cdma`, unlocked and reported **`Sending 'boot' (6490 KB) OKAY`**, **`Writing 'boot' OKAY`**, native exit0 and `STAGE_D_P7_FLASH_ACK_VERIFIED_SUCCESS`. Flash affected p7 boot only.
4. Assistant then performed ordinary **`fastboot reboot`**, not another temporary `fastboot boot`. USB COM9 returned the authentic `Debian GNU/Linux 12 xoom-mz600 ttyGS0` login, private xoom authentication passed, and live values proved `uname -r=7.0.0-next-20260422+`, Debian `12.15`, and `findmnt -n -o SOURCE,FSTYPE,TARGET /=/dev/mmcblk0p8 ext4 /`. Thus **NORMAL, PERSISTENT INTERNAL DEBIAN BOOT** independently proven.
5. **This checkpoint completes the last outstanding gate:** owner's root-console direct physical p7 readback matched Stage-D hash over full image length and recorded the full 8MiB p7 hash above. Unlike former snapshots, no raw readback step remains pending.

## Safe boundaries and future work

- **p7** now has Stage-D internal-p8-root boot persistently, verified by flash ACK, normal reboot, Debian root filesystem and physical p7 SHA. Do NOT automatically restore Stage-B SD-root to p7 and do NOT use the two failed Stage-C/Stage-E per-boot-GPT-PARTUUID images.
- **p8** is installed Debian internal ext4. **p6 TWRP**, backup images, and physical GPT were not targeted in Stage-D flash. Original Android p7 factory image and Stage-B rescue boot remain privately backed up on Surface; the 32GB microSD remains a useful recovery asset, but **a normal boot no longer uses microSD root**. Removable SD-root *recovery* would require a manually selected temporary Stage-B boot or deliberate restoration of p7; it is not the default boot.
- **Next tasks are separate from persistent installation:** Linux7 kernel/module `uname -r=7.0.0-next-20260422+` vs module folder/vermagic `7.0.0-next-20260422` (missing plus), BCM4329 Wi-Fi device/module not working, systemd/D-Bus connection error, and determining why BigPart GPT PARTUUID differs across boots. Do not paper over vermagic by simply renaming module directories. Keep native Linux work and handoff history.
- Protected original Xoom must never be modified as part of this experimental replacement-device work.

**Result: Persistent native Debian 12.15 on Motorola Xoom MZ600 eMMC p8 is FULLY VERIFIED.**
