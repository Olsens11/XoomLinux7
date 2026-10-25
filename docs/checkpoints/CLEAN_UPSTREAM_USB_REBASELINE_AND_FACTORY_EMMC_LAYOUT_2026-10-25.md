# Clean upstream reboot baseline and factory-layout decision — 2026-10-25

**Branch:** `wip/clean-upstream-usb-rebaseline-20261025`
**Physical device:** replacement Motorola Xoom MZ600, currently black screen/red camera LED after a temporary v034 test. Physical tablet not accessed during this build. Original Android recovered earlier and is still the designated OEM reference environment.

## Why this reset is justified

- Oct 25 physically tested `MZ600-v034-HCI-IOCTL-TEMPBOOT-ONLY.img` SHA256 `9850361687f6d121119a0c3399cdc0abaa68d8e9714238aba5bb9b7207a0af39`, 6,979,584 bytes, in RAM by verified `fastboot boot`. USB CDC COM9 appeared at 11:23:28 ET, stayed continuously present at most 0.5 seconds, then disappeared. No flash. This is a self-contained USB diagnostic PID1; it does **not** need the Debian SD root. Therefore SD-card rooting is not a necessary condition for this symptom.
- The known-good Debian SD boot image and US/69 derivative separately lost USB within one second. The USB dropout mechanism remains unproven. Do not call it a Wi-Fi or regulatory failure.
- From a recovered Android run, ADB root read-only examined partition devices: **32GB removable SD = `mmcblk0` type SD, sectors 61067264** and **internal eMMC = `mmcblk1` type MMC, sectors 62521344**. These device numbers reverse on some Linux boots; never assume an index. This agrees with historical factory GPT and ext4-removable card MBR without evidence of changed internal partitions.
- Private host-side exact backup images already available: `private-backups/replacement-mz600-2026-10-25/android-HMJ37-boot-p7.img` (8,388,608 bytes), `android-HMJ37-system-p8.img` (268,435,456 bytes), `twrp-recovery-p6.img` (12,582,912 bytes), reserved first 25 MiB and card's previous MBR. Do not publish or replace these files. This **does not claim** a comprehensive verified factory restore of all eMMC partitions or a tested backup restoration.
- **Factory eMMC partition layout is already present**, by previously captured partition evidence and the fact only the removable card was repartitioned. There is no partition-table restoration procedure to perform on eMMC now.
- Android **system GPT partition p8 is 256 MiB**, smaller than the initially 449 MiB of Debian contents and the 768 MiB staged root image; a normal Debian root **cannot be installed there unchanged**. User's proposal to run from internal system is a target to be designed after a successful RAM-only diagnostic control, not authorization to blindly overwrite eMMC or shrink root content unsafely. If replacing Android as the primary OS, a planned Linux-native eMMC layout can eventually resize/reallocate the large userdata capacity, with preservation and recovery checks first. Do not mistake preserving the *stock layout* for being able to fit a full native OS in stock p8.

## Clean baseline engineering

- **Exact upstream:** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Detached WSL Git worktree at `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/linux`; original upstream checkout untouched. Build outputs isolated in `clean-upstream-usb-20261025/build`.
- **Kernel config:** upstream `tegra_next_defconfig` plus only requirements needed for ARM appended DTB/ATAG, USB gadget + CDC ACM (`CONFIG_USB_G_SERIAL`, ChipIdea Tegra UDC), devtmpfs and existing pstore capability; no NEON; no embedded custom initramfs; no Wi-Fi/BT driver code edits.
- **USB tool:** previously available minimal v04 read-only freestanding ARMv7 `/init`, with known `PING`, `STATUS`, `LOGS`, `CPU`, `MEM`, `USB` and other commands; 4.8 KiB CPIO ramdisk supplied externally in Android boot image. This is the smallest useful *first* control. It is not the v034 active BLE and firmware upload lab. Add the larger USB-tool features later only after the tiny tool is stable.
- **Board DT:** copy original 1,712-line upstream Wingray description and change exactly four matters in an isolated generated test derivative: model string, `motorola,wingray` → `motorola,stingray`, USB0 controller compatible to Tegra UDC, and PHY+controller USB mode to peripheral. No SDIO clocks, Bluetooth clocks, MAC injection, regulatory maps, power sequencing or pin overrides are added. The generator verifies exact anchor counts; modified DTS and a one-line Makefile target live only in the separate WSL worktree.
- **Packaging:** `mkbootimg` Android temporary boot image, appended DTB, external gzip CPIO with `/init`. Validate boot header, SHA1, DTB, CPIO, image size before anything physical. **UNTESTED** until separately documented. Never run `fastboot flash` on this image.
- **Patch queue (not yet enabled):** ① dynamic Motorola bootloader MAC ATAG→FDT + generic brcmfmac, ② SDIO legacy max 25 MHz, ③ BT PMC 32.768k named LPO vs normal 38.4 MHz ref, ④ real Motorola HCD patch firmware via standard `hci_bcm` load, ⑤ shared U4 and BT reset ownership (source-only prototype requires real consumer integration), ⑥ family-aware radio/regulatory calibration. Each gets a separate compile/physical verdict, and where possible MZ604 cross-test.
- **FM:** retain the chip architecture and power model but do not add imaginary FM antenna/transport/audio routing; inspect Motorola board implementation before any V4L2 FM driver candidate.

## Next physical A/B only after artifact offline validation

1. User physically recovers Xoom using documented Power+Volume Up, confirms Android, no flash.
2. Verify correct ADB identity and boot completion, Android eMMC baseline, attached power and verified image SHA. One `fastboot boot` of clean minimal USB, host USB arrival/departure timestamp, visible screen/dashboard, and one PING/STATUS handshake if USB stable. Keep a complete immutable capture and no automatic retries.
3. If clean baseline drops USB, do **not** add Wi-Fi patches. Compare upstream kernel config/boot settings, machine pinmux, CPCAP PMIC/battery/ADC, suspend/wake, USB gadget and RAM timing, and obtain panic/ramoops or external serial evidence.
4. If clean baseline stays alive, add one independent patch per test, beginning with the minimal diagnostic functions needed for read-only state and then MAC/SDIO firmware, shared Wi-Fi/Bluetooth and regulatory path.
5. Once the RAM-only kernel is stable, plan either (a) an intentionally tiny diagnostic root in p8 (reversible backed-up target, **not** Debian) or (b) Linux-native internal repartition and complete Debian root; get a separate explicit, partition-specific eMMC write approval and test the restoration path first.

## Evidence

- `docs/checkpoints/MZ600_BASELINE_REPRODUCES_US69_USB_DROPOUT_2026-10-25.md`
- `docs/checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md`
- v034 physical source checkpoint and test image SHA listed above.
- User's live correction `usb tool` means the existing Xoom CDC-ACM/diagnostic protocol; preserve this facility in the rebaseline.
- No source-only candidate is a qualified upstream patch until built, physically run and matched against comparable board models.
