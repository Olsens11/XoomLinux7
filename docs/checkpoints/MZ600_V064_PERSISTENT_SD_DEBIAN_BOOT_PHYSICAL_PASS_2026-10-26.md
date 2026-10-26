# MZ600 v06.4 — **PERSISTENT Linux7 Debian microSD boot PHYSICAL PASS**, readback remaining

**When:** Monday October 26 2026 02:42–02:46 EDT. **Device:** replacement Motorola Xoom MZ600 Verizon Stingray CDMA. **Protected original tablet not touched.**

## Confirmed successful milestones

- Before write, Surface independently SHA-256 verified the original Android **p7 boot backup** full 8,388,608 bytes `4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3`, **p6 TWRP recovery backup** 12,582,912 bytes `ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`, and physically proven Stage-B **BigPart Debian microSD boot image** 6,645,760 bytes SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`. Earlier whole-p7 on-device readback exactly matched factory backup, proving aborted previous flash did not modify p7.
- Stage-B Debian SD-root still worked before modification: COM9 `id -u = 0`, `uname -r = 7.0.0-next-20260422+`, `findmnt /` `/dev/mmcblk1p1 ext4`, BigPart p8 2,097,152 sectors, p7 16,384 sectors, systemd PID 1. Root command `sync; /sbin/reboot --force --force` safely rebooted to original Android; Surface ADB verified `ro.hardware=stingray`, `ro.product.device=stingray`, `sys.boot_completed=1` and battery 100%.
- Corrected explicit-once host flash wrapper: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-v064-Persistent-Debian-SD-Boot-Fastboot-Once-20261026.ps1`. Unlike prior version it uses `Start-Process -PassThru -Wait -RedirectStandardOutput -RedirectStandardError`, keeping warnings separate from the native exit code. Before flash it validated actual ADB serial **170061c243805617**, Android identity, 100% battery, 3 file hashes, then `adb reboot bootloader`; saw same serial and verified **fastboot product xoom-cdma, unlocked=yes**.
- Issued exactly **one** `fastboot flash boot <Stage-B image>`, targeting only p7. Native **exit code 0**, `Sending` and `Writing` both acknowledged `OKAY` in captured stderr; no further flashes, no p6 recovery, p8 system, p9 cache, p10 userdata, or GPT commands. Host flash log `captures/MZ600-V064-Persistent-Debian-P7-Flash-20261026-PRIVATE.log` and stdout/stderr captures in same directory. Success 2026-10-26 **02:44:24 EDT**.
- Followed with **ordinary `fastboot reboot`**, specifically **NOT fastboot boot**. Device produced real `Debian GNU/Linux 12 xoom-mz600 ttyGS0` + `xoom-mz600 login:` over COM9. **`PERSISTENT_P7_NORMAL_REBOOT_LOGIN_PASS=True`** after approx 32 sec. Evidence `captures/MZ600-V064-Persistent-Debian-P7-NormalBoot-20261026.log`.
- Used existing host `downloads/xoom-debian-serial-first-login-probe.ps1` private workflow (which does not print credential) to log into normal unprivileged user `xoom`. Physically verified **Debian 12.15**, `uname -r 7.0.0-next-20260422+`, **SD root /dev/mmcblk1p1 ext4**, USB /dev/ttyGS0, BigPart **internal p8 1GiB**, p7 8MiB and `ls -l /dev/mmcblk0p7: brw-rw---- 1 root disk`. Xoom ordinary user does **not** belong to disk group, so independent raw p7 SHA readback still requires owner to enter **`sudo -s` locally in interactive Surface USB console**. **DO NOT falsely state raw p7 on-device readback has passed after this flash.**

## Current status and safety constraints

- **Physical normal persistent p7 Stage-B SD Debian boot: PASSED.** This proves Linux7 can boot without Android /system on normal boot path, assuming removable Debian microSD remains inserted.
- **Physical raw p7 post-flash SHA: PENDING ROOT ACCESS.** Expected readback `head -c 6645760 /dev/mmcblk0p7 | sha256sum` exactly equals `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`; p7 is an 8MiB partition while boot image is 6,645,760B, so full p7 SHA differs from image SHA. When privileged verify p7 sector size/start, SD root and unmounted p8, capture first bytes `ANDROID!`. No writes for validation.
- **Current physical tablet mode:** newly **persistently booted** Linux7 Debian microSD, at normal authenticated `xoom` shell over COM9; `sudo` root has **NOT** been reauthenticated after latest reboot. No root password should ever be exposed, fetched or logged; owner can log in to Surface console and `sudo -s` then Ctrl+] release.
- **NO p8 Debian root installed or formatted.** Original Android **boot partition p7 is now intentionally replaced by Linux Stage-B**, but original p7 backup is safe on Surface. TWRP p6 unchanged and GPT original. Earlier BigPart Linux7 in-memory remap still physically produces p8 1GiB, p9 512MiB and p10 ~28,929.5MiB; standard TWRP 3.1.1-0 is not BigPart aware and must not format p8.
- `systemctl` D-Bus still unavailable; `wlan0` absent in current SD boot, `iw scan` unresolved. Linux `reboot bootloader` RESTART2 still routes to Android (not fastboot), so it is *not* a reliable rescue route. A normal persistent Stage-B boot from p7 now exists, but independent bootloader/recovery key route should be tested separately before erasing p8 (Volume Down physically damaged).
- Source root installer `scripts/experiments/mz600-bigpart-install-debian-from-sd-20261026.sh` SHA256 `e265a0e8f7baae66311788d37ea504dc4e9785530139423428b15a1f41a28650`, previously achieved **`--preflight` exit 0**, but **`--install` never run**. Offline prepared Stage-C internal p8-root boot image SHA256 `15feced18d384ec532b7e3d9fb04463eac14c445909fadb5798920ee661571c8` **NOT booted**.
- Proposed next: authenticated privileged p7 readback matching Stage-B; optionally test another ordinary warm reboot from Debian into persistent Debian (note normal restart from Linux previously went to Android because p7 was Android, but now p7 is Debian). Then validate recovery plan and guarded p8 installer. **Do not erase Android /system until independent rescue is good and physical readback passed.**


## Additional post-persistent-boot read-only p8 installer preflight PASS

Without root, after successful ordinary boot from p7 into Debian-on-SD, re-ran the exact previously pinned microSD installer `/home/xoom/mz600-bigpart-install-debian-from-sd-20261026.sh --preflight`, with an explicit shell return-code marker. Actual result:

```
INFO_P8_UDEV_SYMLINK_MISSING_KERNEL_GPT_UUID_VERIFIED
MZ600_BIGPART_PREFLIGHT_PASS
ROOT=Debian-12.15-SD-ext4 KERNEL=Linux7
TARGET=P8_BIGPART_1G P9_CACHE_512M P10_DATA_28929_5M
ALL_PROTECTED_P1_TO_P7_UNCHANGED=PASS
SD_ROOT_USED_KIB=465916 TARGET_UNMOUNTED=PASS
IDENTITY_AND_PARTUUID_VERIFIED=PASS
READ_ONLY_NO_FORMAT_NO_MOUNT_NO_TRANSFER
RECHECK_RETURN_0
```

**Important clarification:** output `ALL_PROTECTED_P1_TO_P7_UNCHANGED=PASS` is an unfortunately misleading historical script label: preflight verifies partition **geometries and that it performs no writes**, NOT hashes or persistence of previous p7 contents. **p7 was intentionally flashed with Debian SD Stage-B**, so never interpret that line as proof p7 Android contents unchanged. Correct this label in public script and on SD before future p8 destructive execution. The source allocated footprint is now **465,916 KiB** and still fits 1GiB p8. Current unprivileged shell cannot read `/dev/mmcblk0p7` (root:disk mode 0660); owner's local `sudo -s` is required for raw boot-image readback.

