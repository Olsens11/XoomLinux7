# MZ600 cold p8 raw Debian preservation — physical completed backup verified (2026-10-28)

**New physical result: the internal Debian p8 was imaged with the source partition completely UNMOUNTED while Debian was temporarily booted from the proven BigPart rescue microSD, and the raw 1 GiB image stored on the card has been independently re-read and SHA-256 verified.** No internal p6/p7/p8/p9/p10, GPT or bootloader flash; original known-working Debian Linux p8 restored by ordinary p7 boot after the one-shot rescue script.

## Access and read-only check

Owner explicitly entered sudo password directly in the Surface's existing COM9 interactive terminal, then pressed Ctrl+] to detach. No password was extracted, transmitted into chat, or printed.

Root COM9 identified `id -u=0`, model **Motorola Xoom (Stingray MZ600 minimal USB diagnostic)**, Linux **7.0.0-next-20260422+**, root `/dev/mmcblk0p8 ext4 /`. Physical internal disk has **62521344 sectors**. BigPart virtual geometry checked exactly: p8 `118784/2097152`, p9 `2215936/1048576`, p10 `3264512/59247616` (start/count sectors).

Existing rescue `/dev/mmcblk1p1` was not mounted. Under root, created only a temporary mountpoint in `/run` tmpfs, and mounted it with `mount -t ext4 -o ro,noload /dev/mmcblk1p1 /run/mz600-p8-cold-inspect-ro`. `findmnt` showed `ro,relatime,norecovery`, with **no replay of the rescue card's journal** and no internal p8 mount changes.

## On-card files and observed results

Path on rescue SD:
`/var/backups/MZ600-V31-P8-COLD-20261028/`
- `p8-cold.img`: exact **1,073,741,824 bytes**
- `RESULT.txt`: `MZ600_COLD_P8_BACKUP_PASS`, `bytes=1073741824`, `root=/dev/mmcblk1p1`, `source=/dev/mmcblk0p8`, `p8_mounted=NO`
- `SHA256SUMS`: **a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346**
- `e2fsck-readonly.txt`: 5 ext4 checks completed with one accounting discrepancy, described below.
- No `p8-cold.img.partial` remains.

Independent fresh `sha256sum p8-cold.img` and `sha256sum -c SHA256SUMS` was executed on the running MZ600, with the SD mounted read-only, and printed:
```
a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346  p8-cold.img
p8-cold.img: OK
```
The original script had also computed the source /dev/mmcblk0p8 raw SHA and compared it with its captured file before renaming the final image and writing RESULT.txt.

### Mandatory fsck qualification

Saved check `e2fsck -fn p8-cold.img.partial` with ext4 journal replay disabled did all five passes but reported:
```
Warning: skipping journal recovery because doing a read-only filesystem check.
Free blocks count wrong (119757, counted=119756).
Fix? no
xoom-system: 12880/65536 files (1.4% non-contiguous), 142387/262144 blocks
```
This is a **one-4KiB-block free-space accounting mismatch**. The raw image hash and full length are correct, but **DO NOT claim the ext4 filesystem is perfectly fsck-clean or that an actual restore has been tested**. Do not alter the original raw backup; any journal replay/repair must be tested against an expendable *copy*, not the golden image or live p8. Root cause of free counter mismatch has not been determined.

## Off-tablet transfer and cleanup

One-use, private, public-key-pinned TLS receiver on owner's Surface, authenticating expected device IP and one-time token, rechecks the exact uncompressed 1GiB length and **expected cold image SHA before atomic rename**:
`C:\\Users\\olsen\\xoom-linux-rom\\private-backups\\MZ600-V31-P8-COLD-20261028\\p8-cold.img`.
This copy is separate from the previous live RW `MZ600-V31-PREFLASH-20261028\\p8.img`. Any .partial file is **not a completed off-device backup**.

**Transfer COMPLETED and independently verified.** TLS receiver reported `COLD_P8_SURFACE_TRANSFER_PASS 1073741824 a5726126eb55ff54045dd565b1bdcff07e246aa679ee485448363f78a82f4346`, and the Xoom-side COM9 sender reported `MZ600_TRANSFER_HTTP=200`, `MZ600_TRANSFER_EXIT=0`. The one-use receiver closed successfully. Surface then **reopened the final NTFS file** and independently ran SHA-256, confirming `SURFACE_FILE_BYTES=1073741824`, `SURFACE_FILE_SHA=A5726126EB55FF54045DD565B1BDCFF07E246AA679EE485448363F78A82F4346`, and `SURFACE_FILE_REOPEN_MATCH=True`. The Surface destination contains `p8-cold.img`, `backup-transfer-verification.json` plus bytewise copies of the original SD `RESULT.txt` (171B), `SHA256SUMS` (78B), and `e2fsck-readonly.txt` (437B), all transferred directly over authenticated COM9 without private credential disclosure. The source rescue SD's temporary read-only `ro,relatime,norecovery` mount was **unmounted successfully** (`MZ600_RO_SD_UNMOUNT_PASS`, exit zero), and its `/run` mountpoint removed. The internal Debian system remained booted from `/dev/mmcblk0p8` throughout this metadata/host-transfer step. **Off-device exact raw backup preservation PASS; fsck perfect-clean and restore exercise STILL OPEN.**

Host-only scripts on Surface `inspection/`:
- `MZ600-P8-Cold-Verify-Root-Preflight-20261028.py`
- `MZ600-Cold-P8-Mount-ReadOnly-Metadata-20261028.py`
- `MZ600-Cold-P8-Independent-SD-SHA-20261028.py`
- `MZ600-Cold-P8-TLS-Receiver-20261028.py`
- `MZ600-Cold-P8-TLS-Sender-COM9-20261028.py`
- `MZ600-Cold-P8-Copy-Metadata-From-SD-20261028.py`
- `MZ600-Cold-P8-SD-ReadOnly-Unmount-20261028.py`

**Future gate**: Independent off-device filesystem viability/restore test performed against disposable copy, not live partition; preserve p6 factory TWRP and stage any BigPart-aware TWRP via `fastboot boot` before p6 flash. New 1GiB Debian test image remains off-device and unflashed. Do not change p10 or factory GPT.
