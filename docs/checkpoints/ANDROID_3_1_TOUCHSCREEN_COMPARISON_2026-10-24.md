# Replacement MZ600: Android 3.1 vs TWRP touchscreen failure; OEM restore readiness

**Date:** October 24–25, 2026 local observations. **State:** physically observed on replacement Xoom via Surface ADB; no device flash, format, partition writes or experimental driver changes.

## Android normal boot state (physical)

The tablet transitioned from TWRP 3.1.1-0 into its existing Android system. ADB was intermittently disconnected during USB-mode transition, then reconnected to the same already-known tablet USB transport. Confirmed Android boot:
- `getprop ro.product.device = stingray`
- `getprop ro.build.description = trygon-userdebug 3.1 HMJ37 124251 test-keys`
- `getprop sys.boot_completed = 1`; Android `zygote` running; PID1 `init`.
- Screen touch **not enumerated**: `/proc/bus/input/devices` shows accelerometer, compass, gyro, barometer, ALS, CPCAP key, Stingray keypad, **no qtouch touchscreen**.
- Original Android driver logs `qtouch_ts_probe:Read failed -121`, `qtouch_process_info_block: Cannot read info object block`, `qtouch-obp-ts: probe of 0-005b failed with error -121` (normal I²C address 0x5b). Driver also tries bootloader address 0x35 and reports NACK. The previous TWRP recovery boot had the same missing touchscreen input and I²C -121/NACK on 0x5b/0x35.
- This comparison makes a TWRP-only application/driver bug unlikely, **but it does not prove physical panel damage**. Stuck controller state, reset/power supply and board connection are plausible. No firmware flashing or register writes attempted.
- OEM source: https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842/drivers/input/touchscreen/qtouch_obp_ts.c ; its `qtouch_ts_probe` resets, tries normal info-block read, then switches to bootloader I²C address upon failure. Full cold power-down with USB/dock/charging power removed and fresh startup is the next low-risk test, before invasive software/hardware actions.

## Can original stock Android be restored after replacing installed root?

**Yes, plausibly and with strong archived reference media—but it is not a single guaranteed format command.**

The user's Pi **already privately holds** source archives:
`/home/ps2/xoom-phase1/private/oem-reference-20261021/roms/unverified-quarantine/MZ600_HRI39-source-mediafire-klylgjtuy42y625.zip` and `MZ600_HRI66-source-mediafire-hvn8jrm6e77gzw6.zip`.

Audit: `/home/ps2/xoom-phase1/private/oem-reference-20261021/MZ600-HRI39-HRI66-STOCK-ARCHIVE-RECOVERY-20261021.md`. Both archives matched contemporaneous historical whole-ZIP MD5 values, passed all member CRC checks, and extracted the complete four images: `boot.img`, `recovery.img`, `system.img` (ext4), `userdata.img` (sparse). `system.img` contains Verizon/Stingray `trygon` Android 3.0 (HRI39) or 3.0.1 (HRI66) properties with `release-keys` labels. Official original Motorola cryptographic signing of downloaded ZIP archives **was not independently verified**; keep them privately quarantined, not published or labeled fully OEM-authorized. Existing actual tablet runs Android **3.1 HMJ37**, so restoring either archived full stock reference would roll back Android versions. `userdata.img` would overwrite user data. Full restoration needs correct partition identities, image hashes, validated fastboot/recovery workflow, backup, appropriate safety checks, and explicit installation authorization. **Do not relock bootloader speculatively.**

**Important:** The Android touchscreen also fails to initialize in current Android 3.1, so reformatting/reinstalling OS storage is not presently justified as a touchscreen repair. Reflashing a full stock OS would not in itself guarantee touch controller responds electrically; first rule out a retained device state with a real power-off/cold startup.

## GPT/partition safety note

Recovery `/proc/partitions` exposed ten eMMC partitions. Old vendor/Android 2.6 tooling `fdisk` did not recognize a modern EFI GPT in its default manner. One research attempt expected an EFI header at LBA1, but **did not establish a valid EFI GPT**; do not treat absence of EFI magic at LBA1 as proof of broken storage. Actual Tegra/Motorola-specific partition metadata layout must be verified read-only before changing, adding or resizing partitions. TWRP mounted Android `data` and `cache` by default. The last-known capacity of `userdata` is ~29.3GiB, with ~28.6GiB free reported by TWRP: **filesystem free space is not unallocated physical disk space**.

**No further eMMC manipulations authorized**. Preserving the successful BCM4329 §wlan0§ milestone and the clean OS artifacts is independent of the touchscreen issue.

## Next steps, in order

1. Power Android off normally (ADB `reboot -p` if no touch), disconnect USB/dock/charger, allow a real shutdown, then turn on by button and recheck touch input and `qtouch` probe. This is a **proposal**, not an action performed in this checkpoint.
2. If still absent, audit exact touch regulator/reset source and passive I²C signals/driver bindings; avoid guessing chip address/firmware. Preserve diagnostic logs before any further reset.
3. Treat factory restore as *available potential rollback media*, not permission to flash Android or replace/repartition eMMC. Keep historical exact image archives and validations in the private Pi.
