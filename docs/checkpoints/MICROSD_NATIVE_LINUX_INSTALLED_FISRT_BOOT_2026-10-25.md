# 32GB microSD: native Debian root installed and expanded — first temporary Linux boot unconfirmed

**Date:** October 25, 2026. **Target:** verified *replacement* Motorola Xoom MZ600 (not the protected recovery Xoom). **Evidence classes:** physical microSD and filesystem PASS, bootloader temporary-boot command PASS, **Linux OS boot / USB NOT YET CONFIRMED**. The internal Android `boot`, `system`, `userdata`, and TWRP `recovery` have **not been modified**.

## Approved scope and media identity

User explicitly approved erasing/reformatting the inserted **empty** 32GB microSD FAT32 `DISK_IMG` partition to install Linux. Recovery ADB one-device uid0 confirmed `TWRP 3.1.1-0`. First inspection proved:
- removable card: type **SD**, **61,067,264 sectors of 512B**, original FAT32 p1 at LBA64 and length 61,067,200; DOS-MBR valid `55AA`, type `0x0B`.
- FAT filesystem mounted **read-only**; `df` said **16KiB used**, no listed files. Unmounted before writing.
- 16MiB read-only tests at beginning, 100MiB and 10,000MiB offsets completed.
- original 512-byte MBR saved off-device, SHA256 `29e1bb4263738efbcaf87a02b6a908c0db6f2f8ab53f9d7972e31fa55cf23acf`. Exact signature, card CID and unique identifiers remain in private local records; **do not publish**.

## First authorized write — SD MBR only

Source and guard file stored **privately** on Surface at
`C:\Users\olsen\xoom-linux-rom\private-backups\replacement-mz600-2026-10-25\prepare-sd-mbr-20261025.py`,
`install-sd-mbr-guarded.py`, and original/new MBR binaries (not public).

Both full old MBR SHA256 and runtime removable type/size, recovery identity, mounted state and **different internal eMMC** size were verified immediately before writing. **Only 512 bytes at first sector of the removable card** were written, retaining the original DOS disk signature and boot code, and changing the four-entry table to one 0x83 Linux partition, starting LBA **2048** (1MiB aligned) with **61,065,216 sectors**, all others unused. Post-write first-sector SHA256 was **`b3de013157cdbe04e446de49fad3ce02308209bef641aeeb21013bc8c0bb79ab`**.

**Critical lesson:** A recovery reboot changed enumeration. Before reboot SD was `mmcblk1` and eMMC `mmcblk0`; after reboot SD became **`mmcblk0`**, internal eMMC **`mmcblk1`**. ***Never target storage solely by mmcblk number after reboot***. The guarded installation and resize scripts rediscover the SD by `/sys/block/mmcblk*/device/type=SD` and exact capacity, matching new p1 start/size and MBR SHA before opening a block device. After reboot, kernel verified p1 start 2048/size 61065216, FAT32 gone, `fdisk` reported partition type 83. Android remained on internal eMMC and recovery automatically mounted internal `data`/`cache`, not SD.

## Exact Linux OS data transfer and write

The OS branch [`os/mz600-native-rootfs-wifi-20261024`](https://github.com/Olsens11/XoomLinux7/tree/os/mz600-native-rootfs-wifi-20261024) has the **clean upstream Linux 7** kernel with Motorola ATAG→FDT dynamic MAC path and USB0 peripheral configuration, plus Debian Bookworm armhf userland, checked exact BCM4329 4.220.48 firmware and 1550-byte calibration, separate stock `brcmfmac-wcc.ko`, and systemd `serial-getty@ttyGS0`. No `XOOM_V0xx` Wi-Fi diagnostics or reused MAC addresses.

Offline source image `xoom-linux-root.ext4` = **805,306,368 bytes**, SHA256 **`7ab44285a110626f8533ba46fb43837827c5fa565ef48a254dd92dd432e1c746`**. Built with recovery-compatible ext4 features (disabled `64bit`, `metadata_csum`). Boot image SHA256 **`8bb0a98bab1a5043ab335a21a92fb43cf505a060d3c976e283ebdb60e1b9230d`**, normal `root=PARTUUID=<private-MBR-signature>-01 rootfstype=ext4 rootwait rw init=/sbin/init`, and matching private `/etc/fstab`. Full offline acceptance passed.

Transferred from development desktop to Surface via already-authorized **SSH/SCP over user's LAN**; root image compressed to **203,175,497 bytes**, SHA256 **`054fb1bdf7729a9afbd07c1ab5e42343dd007607d97ec650feb84ca257e34988`**. Surface decompressed and SHA-verified to original 805,306,368-byte hash; boot image hash also rechecked. Native `adb shell -T` binary-stream attempt failed with **`device only supports allocating a pty`** on old TWRP ADB, so used safer **`adb push` compressed file into TWRP `/tmp` RAM tmpfs** (203MB, capacity ~367MB). Remote `sha256sum` on staged compressed file matched. **No Android userdata staging or writes.**

Private recovery install script `C:\Users\olsen\xoom-linux-rom\downloads\install-root-to-SD-verified.sh` reverified exact SD hardware class/size, MBR hash and p1 range, unmounted status, and compressed source hash; printed `GUARD_PASS SD_ONLY=mmcblk0 DEST=/dev/block/mmcblk0p1`. `gzip -dc` piped to `dd of=SD-p1 bs=4096` wrote **805,306,368 bytes in 66.30 s (~11.6MB/s)**. **Physical first-768MiB readback SHA256 matched exactly `7ab44285...`**, and `blkid` identified ext4 `LABEL=xoom-root`. `MICROSD_LINUX_ROOT_INSTALL_PASS`.

## Full SD filesystem expansion and read-only mount

Private script `resize-SD-root-verified.sh` repeated the SD/MBR/mount protections. TWRP `e2fsck -fn` **PASS** on original 196,608-block ext4. TWRP `resize2fs 1.41.14` expanded ext4 in-place to **7,633,152 × 4096-byte blocks** (full 61,065,216-sector p1) successfully; a subsequent complete `e2fsck -fn` returned **exit 0**:
```
xoom-root: 12365/1908736 files (0.1% non-contiguous), 234684/7633152 blocks
SD_ROOT_RESIZE_COMPLETE
```
Recovery mounted the SD ext4 explicitly `-o ro,noload`, protecting the journal from writes; reported ~**30,053,428 KiB** total filesystem space, **459,556 KiB** used (~449MiB) and **28,067,304 KiB** available (~26.8GiB). Read `/etc/debian_version=12.15`, fstab with the intended **private MBR PARTUUID** root, separate `brcmfmac-wcc.ko` and enabled symlink `serial-getty@ttyGS0.service`. Mount was unmounted cleanly before bootloader test. **This qualifies the microSD OS installation, not the Linux boot.**

## First normal Linux temporary boot

With the SD installed:
- Rebooted recovery to bootloader through ADB. One fastboot device. `fastboot getvar product = xoom-cdma`, `unlocked=yes`. Original Android boot/recovery were still unchanged.
- Surface locally verified exact 5,890,048-byte boot image SHA256 `8bb0a98bab1a5043ab335a21a92fb43cf505a060d3c976e283ebdb60e1b9230d`.
- **`fastboot boot <verified-image>` returned SEND OKAY (0.860s), BOOT OKAY (1.393s)**. This confirms bootloader transfer/start request only, **not** OS boot completion.
- Subsequently, Surface returned no `adb devices`, no `fastboot devices`, no live serial COM ports, and no present USB gadget VID_0525 or Motorola / Xoom USB device. The old COM9 entry exists only as a **disconnected historical Windows PnP record**. **Linux USB getty not observed; Linux root mount and PID1 have not been physically confirmed.**
- **Do not flash p7 / boot** to “fix” this. The kernel may have failed early, hung on storage/root mount, or run without USB0 gadget enumeration; no on-device display observation yet, and the cause is **unknown**. Next: ask user what current screen shows, then debug temporary boot diagnostics with known working USB initramfs/early-logging approach. Preserve all physical evidence and accepted SD root.

## Current state / user decision

**PASS:** SD DOS-MBR alignment, ext4 root write & SHA readback, full ext4 expansion, fsck, read-only Debian inspection. **NOT VERIFIED:** normal Linux kernel boot to the microSD root, USB ttyGS0, native modular BCM4329 with unique per-device MAC, UI/input, or network. The card is installed, but the OS *has not been shown to boot*. Android boot p7, system p8, data p10 and TWRP recovery p6 **unchanged**; existing same-unit backups retained on Surface, not GitHub.

**Next actionable work:** determine current screen indication; if needed power-cycle back to Android/recovery then build temporary kernel/initramfs diagnostic explicitly geared to mounting the installed microSD root (still without modifying internal storage), fix root selector/USB startup, rerun `fastboot boot`. Never confuse bootloader's "Boot OKAY" with systemd/USB login success. User approved microSD destructive formatting, not internal flash.
