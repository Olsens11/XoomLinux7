# MZ600 v06 physical Linux panic and v06.1 built-in initramfs corrective image — October 25, 2026

**Project branch:** `wip/clean-wifi-bt-usb-20261025`  
**Upstream Linux:** pinned xoom-linux/linux `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` + minimal Stingray/USB DTS and proven WLAN MAC ATAG→FDT patch. No speculative radio power sequence, BT clock, SDIO regulator or US/69 change.  
**Safety:** only `fastboot boot`, **no eMMC flashing or SD writes**, no Wi-Fi/BT activation.

## Physical v06 outcome: kernel panic at root init

User returned MZ600 to fastboot without microSD. Verified Surface target `xoom-cdma`, bootloader unlocked and exact v06 image SHA256 `c8240c65bf43064b82acec516ffc863e819db314e6f5fa0033586241390e00e9`, size 6,547,456B. At 13:38:28 EDT fastboot accepted RAM boot, `COM9` appeared at 13:38:34, but all USB serial writes failed `The semaphore timeout period has expired`. Final COM9 appeared present without functioning PID1 reply. A user-provided **physical photo of the actual Xoom screen** showed Linux 7 text console, normal detection of MMC/eMMC partitions and then:

```
check access for rdinit=/init failed: -2, ignoring
VFS: Cannot open root device "" or unknown-block(0,0): error -6
Please append a correct "root=" boot option; here are the available partitions:
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

This proves the Linux kernel executed, initialized eMMC, and reached root mount/initial PID1 gate. The **photo directly identifies the cause of unresponsive USB**: Linux could not access `/init`, therefore never launched our diagnostic process to answer PING. **Not a Motorola bootloader rejection, radio-driver failure, or proven SD card defect.** Earlier stable v04 without SD physically answered PONG for >217 sec; the difference is in boot-image composition/configuration. The initial first SD boot with zero ramdisk similarly could not boot userspace, while later Debian with a nonempty ramdisk physically booted. Still unknown why v06 external ramdisk was not present at the rootfs gate; no complete earliest kernel log was captured, so do not declare a specific bootloader ramdisk defect.

Both v04 and v06 configs show `CONFIG_BLK_DEV_INITRD=y`, `CONFIG_RD_GZIP=y`, `CONFIG_DECOMPRESS_GZIP=y`, `CONFIG_BINFMT_ELF=y`. v06 external gzip CPIO did contain a valid statically linked, no-NEON ARM executable `/init`, firmware, Wi-Fi and Bluetooth modules (GNU `cpio -itv` validation, exact header SHA-1 pass). File availability to Linux early rootfs, rather than source C code ELF validity, is the failing gate.

## Corrective v06.1 image — BUILT-IN initramfs, offline PASS

`scripts/experiments/build-clean-wifi-bt-v061-embedded-20261025.py` created a **single-variable boot-method fix**: use Linux kernel's own `usr/gen_init_cpio` generator to reserialize identical 26 private ramdisk entries including character devices `/dev/console` and `/dev/null` and the identical `/init` ELF, Wi-Fi firmware/NVRAM, matching `brcmfmac`/`brcmutil`/WCC and BT modules and restricted modprobe. All per-entry payload bytes were compared to the original v06 archive; original contents preserved. Generic GNU cpio was unable to directly extract character device nodes as non-root; unlike `gen_init_cpio`, it requires privileges to `mknod`, so don't mistake that host error for invalid ramdisk.

Configured `CONFIG_INITRAMFS_SOURCE` to generated canonical gzip CPIO, `CONFIG_INITRAMFS_COMPRESSION_GZIP=y`, kept `BLK_DEV_INITRD=y` and `RD_GZIP=y`. Rebuilt same pinned upstream kernel, Wi-Fi identity bridge and identical board DTS. Kernel build `usr/initramfs_inc_data` **SHA256 exactly matches source embedded archive**; archive uncompressed 1,459,200B, `/init` executable verified. Distinguishing characteristic: **Android boot header ramdisk size = 0**, because the entire initramfs now lives inside the Linux kernel, eliminating dependency on bootloader initrd ATAG memory-pointer handoff. No external SD filesystem needed.

Final **v06.1 experimental temporary boot image**:

- `MZ600-CLEAN-WIFI-BT-USB-v061-BUILTIN-INITRAMFS-RAM-ONLY-UNTESTED.img`
- **6,547,456 bytes** (fits 8MiB boot image limit).
- **SHA256 `b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a`**.
- Kernel+DTB **6,544,240 bytes**, SHA256 `928d16683cf44530cc7b624cfe10afdcf9bb33b9d4be855d831f85dbbf7cd664`.
- Embedded source archive SHA256 `55002fc3be2379b35b7ddbe90cb21aa280610b5feb6cddb0d154ae71bb51ffbf` (matches kernel assembler incbin payload).
- Source/wrapper and kernel compilation PASS, independent Surface boot-image verifier PASS including exact `ANDROID!` header, base/load addresses, DTB header, zero external ramdisk, header SHA-1 and full image SHA256.
- Offline artifact on Desktop WSL `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v061/`, Desktop Windows `C:\Users\Olsen\`, Surface `C:\Users\olsen\xoom-linux-rom\downloads\`. Preserve original v06 image and v04 last physical-good image separately.
- Existing prior Surface verifier `verify-clean-xoom-android-boot.py` intentionally ASSERTS external ramdisk length >0, and therefore rejected v06.1 **by design**. Independent verified `C:\Users\olsen\xoom-linux-rom\captures\Xoom-Verify-Clean-V061-Embedded-ReadOnly.py` PASSED; do not report first verifier's assertion as corrupt image.
- Guarded one-shot Surface launcher `C:\Users\olsen\xoom-linux-rom\captures\Xoom-V061-Embedded-WiFi-BT-USB-Once.ps1` created from v06 launcher with corrected hash/name/private log destination, parser **SYNTAX PASS**, **NOT EXECUTED**.

**No physical v06.1 test yet.** The photographed tablet was at a v06 kernel panic, and COM9 may still be listed but cannot answer; it must be manually recovered by the user via Power+Volume Up into working Android / fastboot. Do not issue USB commands to a panicked PID1 environment or mistake COM9 enumeration for software responsiveness.

## Next physical acceptance test

1. User manually returns the tablet to fastboot with microSD **removed** (unchanged controlled variable); validate exact unlocked xoom-cdma and SHA.
2. One `fastboot boot` of v06.1, **no flash**; observe dashboard, advancing uptime, USB PING/PONG and BT_STATUS/WIFI_STATUS read-only. Compare to last physical-good v04.
3. If still no `/init`, obtain entire early Linux text/ramoops before modifying boot source further. If successful, keep modules unloaded until basic uptime/USB proven; then validate Wi-Fi and BT separately with USB commands and verified OEM firmware, no RF scan/transmit until checks pass.
4. After proven stable, send minimal source-suitable upstream patches and address observed SD-card presence sensitivity separately. No internal Linux install/format until verified recovery and power paths.

**Status:** v06 physical panic confirmed; v06.1 corrective image offline verified, awaiting safe physical one-shot test.
