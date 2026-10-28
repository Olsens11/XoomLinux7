# MZ600 V31 pre-flash preservation and disposable Debian first-boot image — 2026-10-28

**Status:** original running MZ600 unchanged; private encrypted-transfer backup
verified for eight raw image captures; off-device 2 GiB disposable test
root filesystem image built, hash-locked, e2fsck PASS. **NO FLASH, NO
DEVICE REBOOT, NO PARTITION WRITE AND NO FIRST BOOT OF THE NEW IMAGE.**

This is a **deployment/OS milestone**, not another Linux kernel
upstream patch or firmware redistribution. Preserve this record along
with the existing Stage-D, V31 and nine-review source checkpoints.

## Live source verified before any new deployment

A new root-console read-only USB COM9 preflight physically returned:
- `uname -r = 7.0.0-next-20260422+`.
- `/dev/mmcblk0p8` is the active ext4 root, mounted read-write.
- Internal `/dev/mmcblk0` is 32,010,928,128 bytes (62,521,344 sectors).
- p7 8MiB boot, BigPart p8 1GiB, p9 512MiB,
  p10 28,929.5MiB. Separate 32GB microSD remains untouched.
- `/dev/fb0` is `tegradrmfb`; DRM LVDS-1 status **connected**;
  `/dev/tty0` and `/dev/tty1` exist;
  `getty@tty1` and `serial-getty@ttyGS0` are **active**.
- Atmel maXTouch touchscreen reports an input event node; it is not
  yet translated into a text keyboard. Existing kernel bootargs
  already include `console=tty0`, and retain obsolete V06.4
  `gpt_sector=`; the clean nine-review BigPart parser instead needs
  `gpt xoom_bigpart=1`.

## Private pre-flash live raw captures — all received and rehashed

Location: **the owner's Surface Book 2 private backup workspace**
(`xoom-linux-rom/private-backups/MZ600-V31-PREFLASH-20261028/`).
Transferred from the physically running MZ600's authenticated COM9
root shell over a temporary, certificate-public-key-pinned TLS
connection to a Surface-local receiving process. This mechanism
requires no persistent program, root SSH key, disk write, or package
installation on the tablet. Backup TLS listeners were shut down
afterward. The raw image bytes are **NOT on GitHub or in ChatGPT**.

| Local private image | Bytes | Re-verified SHA-256 |
| --- | ---: | --- |
| `p7.img`, installed Android-format Linux boot | 8,388,608 | `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c` |
| `p8.img`, current Debian ext4 root, live RW capture | 1,073,741,824 | `49aa3f3094df05b2f16aaa590fbb4d10cb29144647d28e57261cd19ab563f4a9` |
| `p9.img`, current cache partition | 536,870,912 | `034e9157bc85ff4d9bdff0e395da7ee2db31a4ff8f4b602ad21940e1b8af52fa` |
| `boot0.img`, eMMC boot area 0 | 2,097,152 | `c22364f520348801756a323320af312badd9828812b5474baf6577b5d0d144d2` |
| `boot1.img`, eMMC boot area 1 | 2,097,152 | `ba07d590ab506d16b83b7801bae738da865a72f57bf4e61f0e97e57f2f755030` |
| `head32m.img`, independent first-32MiB read | 33,554,432 | `6efbef9153f93aaeb96a95086d14deace013cd60a917c3138c16939c2b1073f0` |
| `head64m.img`, complete first 64MiB incl. low-level p1–p7 | 67,108,864 | `68ef635674149822109f6687708f9992322f2af263de419270162b633d0d8f51` |
| `tail16m.img`, includes OEM relocated GPT | 16,777,216 | `fb41be791b3858553b0ff34ef7381a892ebfc4c2fc4c6f7156b0c1e01058aab8` |

The backup validator **reopened all captures, checked exact sizes,
recomputed SHA-256, checked p7's `ANDROID!` image signature, p8's
ext4 superblock magic and the OEM alternate GPT `EFI PART` header
and its header CRC at LBA **62,513,151**. The first half of
`head64m.img` is **byte-identical** to `head32m.img`, captured
separately. The current p7 raw image hash also matches the
historically physically read-back Stage-D p7 hash.

**Critical limitation:** p8 was captured with the original ext4 root
**mounted read-write**. Its full transfer and stored bytes are
verified, **but its on-disk journal/filesystem state is not proven
offline-consistent**. For a real pre-flash restoration guarantee,
capture p8 again from a known verified recovery or RAM-only
environment with internal p8 **unmounted** and verify the cold
image and restore procedure before writing any tablet partition.
These captures are **not a complete 32GB eMMC backup**: p10 userdata
was not imaged. Do not assume p10 may safely be repartitioned or
overwritten. The 64MiB head/tail files are forensic reference
artifacts, not blanket restore commands.

A private `backup-verification.json` accompanies the images; no
factory MAC, serial, Wi-Fi network identity or SSH credential is in
this public checkpoint.

## Off-device first-boot Debian image

Private WSL workspace: `clean-wifi-bt-usb-20261025/`.

1. Fresh **separate Debian Bookworm armhf rootfs copy** from the old
   developer reference, never from mounted p8; an explicit marker
   prevents root-password or image-provisioning operations against
   unrecognized locations.
2. **41 signed Debian Bookworm armhf packages**, including
   NetworkManager 1.42.4 / `nmtui` / `nmcli`, `ping`, `curl`,
   `wireless-regdb`, `systemd-timesyncd`, and dependencies
   downloaded, SHA verified and **actually installed/configured** in
   disposable root using QEMU ARM binfmt chroot. Initial missing
   timesyncd dependency was corrected by re-resolving the package
   bundle; the final install PASS is for the updated 41-package set.
3. Exclusive `wlan0` ownership: NetworkManager **enabled**;
   legacy `systemd-networkd` and per-interface
   `wpa_supplicant@wlan0` **disabled**. Generic supplicant D-Bus
   integration retained. `systemd-timesyncd`,
   `getty@tty1`, `serial-getty@ttyGS0` all **enabled**.
4. Requested **temporary disposable-image-only root password**
   was set and privately verified; no plaintext password committed.
   Root SSH login and SSH password authentication **disabled** by
   test-root sshd drop-in. Installed MZ600 root/user passwords
   were unchanged.
5. Private MZ600-specific `brcmfmac4329-sdio.bin` and NVRAM
   `.txt` copied into **test root only**, SHA match to private
   staged source. NOT included in the upstream patch series or
   public offline bundle.
6. **114 newly matched kernel modules** installed via the exact
   clean nine-review kernel `make modules_install` into
   `/lib/modules/7.0.0-next-20260422+/`; `depmod` PASS.
   `modprobe --show-depends brcmfmac` resolves the new
   `brcmutil.ko` + `brcmfmac.ko` from that same module tree,
   not the physically installed V31 Wi-Fi module.
7. A **2GiB regular-file ext4 image** for use with a **separate
   test/removable root**, NOT internal 1GiB p8, was generated using
   `mkfs.ext4 -d` from the disposable root; offline five-pass
   `e2fsck -fn` **PASS**, 13,727 inodes and 149,716/524,288
   blocks. File:
   `XoomLinux7-test-root-bookworm-armhf-20261028.img`.
   SHA256:
   `b7180b88dfacf29b41bdb515d4d1a5226855fb2065ca8423ea69029a1362a70d`.
8. The updated **41-package nonprivate offline bundle** is:
   `XoomLinux7-FirstBoot-Online-Console-v2-20261028.tar.gz`;
   SHA256 `224a72c2b09cf3eb9eb073f8df8d68a50a1994459d1317c44e33fa3b15cfbfb2`.
   This generic bundle **does not contain root password
   or proprietary Broadcom firmware**. Conversely, the private
   *assembled test rootfs image* does; never upload it to GitHub.
9. Local screen console baseline is physically verified at the
   device-model/fbcon level, but **human-visible pixels and touch
   typing on the new kernel/OS combination are not yet tested**.

## Stage gates before any change to physical eMMC

- **PASS:** eight private live raw backup captures, sizes, hashes,
  lower-head redundancy and alternate GPT CRC.
- **PASS:** separate Debian armhf test root assembled, temporary
  local root password configured, matching private firmware/modules,
  NetworkManager and systemd services prepared.
- **PASS:** private 2GiB ext4 test image created and offline fsck.
- **OPEN / HARD STOP:** a read-only **cold p8 backup** with filesystem
  quiescent and an independently verified restoration procedure.
- **OPEN / HARD STOP:** complete p10 backup if any future flash or
  repartitioning would touch p10.
- **OPEN:** construct verified new private boot artifact (kernel,
  board DTB, ramdisk, correct `gpt xoom_bigpart=1` and removable
  root PARTUUID) without copying the obsolete `gpt_sector` option.
- **OPEN:** stage the 2GiB test image on an explicitly identified
  spare medium, not the current installed p8 or unbacked-up microSD.
- **OPEN:** physical framebuffer tty1 pixels, interactive typing,
  NetworkManager association/DHCP/HTTPS, reproducible quick
  reconnections, BCM4329/Bluetooth/power integration tests.
- **OPEN:** actual upstream review/signoff. No patch is submitted.

**Nothing was flashed, rebooted, mounted read-write, reformatted or
installed on the Xoom during this milestone.** Boot and storage
fallbacks are preserved. The backup USB/TLS receivers were stopped
after verification.

Related: [offline kit](../../packaging/firstboot/README.md),
[nine-source review manifest]
(../../patches/upstream/INTEGRATION_SOURCE_MANIFEST_20261028.json),
[read-only BigPart test plan]
(../plans/MZ600_STORAGE_BIGPART_REVIEW_SOURCE_RAM_TEST_PLAN_2026-10-28.md).
