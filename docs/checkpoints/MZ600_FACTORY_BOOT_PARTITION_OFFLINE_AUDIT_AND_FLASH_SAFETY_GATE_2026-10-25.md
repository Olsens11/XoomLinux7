# Factory boot-partition health audit and installed-kernel safety gate — 2026-10-25

**Context:** User reports the clean-upstream RAM-only USB trial ended with a black screen and blinking red camera LED. User proposes fixing boot partition / moving to normal installed Linux. No device is presently reachable by Surface ADB or fastboot, and no new boot partition readback is possible while it is in this state.

## Evidence: physical failure

Clean upstream 7 kernel from exact xoom-linux SHA `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (only device-tree Stingray+USB, read-only v04 USB tool, and unrelated ST hub config omitted) was accepted by `fastboot boot` RAM-only. COM9 presence ~13.38s, PING did not respond, then USB gone. User directly confirmed same dark screen with blinking camera red LED. **No eMMC flash, format, or partition change was performed.** This means the internal boot partition is *not read by the test kernel to acquire its kernel image*, so corruption of that partition is not an evidenced root cause of the RAM boot black screen.

## Offline boot-partition evidence

Surface stored images:
- `private-backups/replacement-mz600-2026-10-25/android-HMJ37-boot-p7.img`, **8,388,608B**, SHA256 `4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3`
- `backups/MZ600-170061C243805617/stock-boot-before-linux.img`, exact same hash.
- `backups/MZ600-170061C243805617/current-boot-readback-20261023.img`, exact same hash.
- The recorded p7 GPT size is 8192KiB. Factory p8 system is only 256MiB; OS Debian 768MiB development image cannot fit it unchanged.
- TWRP recovery p6 separate, 12MiB backed up. Internal eMMC original partition scheme never overwritten during microSD experiments. On prior recovered Android and TWRP, stock boot worked (physical).
- Python inspection of stock boot and candidate headers: both have `ANDROID!` magic, 2048 page size, kernel address `0x10008000`, ramdisk address `0x11000000`, second address `0x10f00000`, ATAG address `0x10000100`; stock kernel 2,827,292B and ramdisk 147,915B; clean candidate kernel+DTB 7,860,816B and external CPIO 4,855B; clean image totals 7,870,464B and header ID matches its rebuilt SHA-1. Stock factory and TWRP legacy boot header hash do not match the *simplified* modern re-hash check; this is not evidence of damaged images because both booted physically and are mutually consistent with factory copies. Investigate OEM boot header hashing conventions rather than declaring stock corruption.
- October 25 successful Debian journal `Kernel command line` proves bootloader supplies OEM memory, fbmem, ramconsole, LP0 vector, serial and RAM variant boot args, and appends our custom diagnostic arguments. Thus no evidence that the custom image displaced vital bootloader board memory args during the successful Debian run.
- The user/device history records a **broken Volume Down button** in `scripts/history/v01/package-MZ600-stingray-v01.sh`; classic Motorola Xoom selection of fastboot during a failed boot relies on Volume Down, so an unbootable flashed `boot` can be materially harder to recover. See Motorola Xoom 2011 fastboot recovery references, and require a tested button-independent fastboot/recovery entry before replacing boot. `adb reboot bootloader` only works when Android/TWRP Linux is already running.
- Standalone Surface read-only verifier written and PowerShell syntax-checked: `C:\Users\olsen\xoom-linux-rom\captures\Xoom-MZ600-Verify-Factory-Boot-ReadOnly.ps1`. It checks the private exact MZ600 ADB identity, `ro.hardware=stingray`, removable/internal geometry, `by-name/boot` symlink, and computes **live p7 SHA256** against the factory reference without writing anything. **NOT EXECUTED** because device remains dark/unreachable. Do not assert current boot p7 hash until this read is performed.

## Decision and follow-up

**No supported evidence that p7 boot partition is corrupted. Do not flash yet.** A more standard installed Linux `boot` test is worthwhile as a separate hypothesis—`fastboot boot` vs installed bootloader execution—but it must follow a real independent recovery demonstration and explicit partition-specific permission because it replaces the factory Android entrypoint.

1. Recover TWRP or Android with Power + Volume Up; keep stock boot, recovery and backups.
2. Re-run read-only p7 hash verification. If matches, mark factory boot healthy and do not describe overwriting Linux as a *repair*. If differs, capture a new backup and identify why before writing.
3. Test and document hardware recovery into **fastboot or TWRP without relying on functioning Volume Down or a healthy internal boot image**. If unavailable, do not risk flash of p7.
4. Prefer enhanced USB diagnostic serial recorder, external UART/kernel early-console and proper reserved `pstore/ramoops` logging to establish reset/power cause. Existing kernel config `CONFIG_PSTORE_RAM=y` does not prove an actual ramoops DT reserved RAM backend.
5. Only then design one-partition Linux boot trial with exact hash/size, by-name p7 target, tested restoration of exact factory 8MiB image, immutable TWRP p6, no alterations to p8 or userdata. Commit minimal patches, keep OEM evidence.

**No physical or partition writes performed in this audit.**
