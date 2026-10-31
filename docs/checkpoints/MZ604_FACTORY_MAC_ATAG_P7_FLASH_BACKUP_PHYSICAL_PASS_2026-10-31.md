# MZ604 factory WLAN MAC trial — full p7 backup and guarded flash physical PASS

2026-10-31 ~06:50–06:54 EDT. Kernel BOOT and factory MAC propagation are NOT YET TESTED. Private backup, original OEM identity and full identifying traces remain on Surface, not in Git.

## Preflight
- Owner physically entered p6 TWRP 3.1.1-0. Unique Wingray MZ604 ADB identification, TWRP recovery version, 8 MiB /dev/block/mmcblk1p7 and p10 /data RW PASS.
- Original p7 7,104,512-byte boot-image prefix SHA256: 56741fcc04f83dd7fb7a7e794e9c5ec21a8a21348401bb686a2d4abc4741c6a2. Host known-good image independently matches.
- Proposed MAC/ATAG-to-FDT p7 image size 7,104,512 and SHA256: 5d551454044454cd79792e092389daf5a493c7992ecb7030c1659d6a78eb206a. Lab source: patches/lab/2026-10-31-mz604-motorola-xoom-atag-factory-wlan-mac-to-fdt.patch.

## Complete verified 8 MiB backup
- Existing safety script inspect PASS. Initial backup implementation failed fail-closed because adb exec-out is unsupported on this TWRP (0 bytes, error: closed). ADB shell -T also reported device only supports allocating a pty. No p7 write during failures.
- Read-only ADB pull directly from /dev/block/mmcblk1p7 returned exactly 8,388,608 bytes (exit 0), written privately to Surface.
- Full backup SHA256 = 5a60a8f005eef7cb5970325cf1cc0deaaba4a70133ce1173064df2a2c242444b. INDEPENDENT live entire 8 MiB partition read-only SHA256 MATCH; first 7,104,512-byte file prefix matches known-good boot image.
- A second host copy and JSON receipt privately retained under Surface private-backups/MZ604-P7-PHYSICAL-LIVE-20261031-FULL-SHA-VERIFIED. Existing flash script validates that receipt.

## p7 flash result
- Original guarded MZ604-TWRP-P7-MAC-TRIAL-SAFE-20261031.py flash --receipt ran: identity and host images PASS, complete backup receipt PASS, live current p7 known-good SHA PASS, new unique staging path on /data/xoomlinux7 and staged SHA PASS.
- Precisely 7,104,512 bytes written to p7 only, sync and postwrite p7 boot-region SHA PASS. Script exit 0, NO automatic reboot.
- Separate independent TWRP ADB postflight confirmed Wingray, TWRP 3.1.1-0 and candidate p7 region SHA256 = 5d551454044454cd79792e092389daf5a493c7992ecb7030c1659d6a78eb206a.
- No bootloader, EBB, BCT, GPT, p6, p8 changes. The staging file on p10 is an ordinary non-rootfs file.

## Next acceptance / safety
- Owner physically supervises TWRP Reboot > System. Historical TWRP software reboot may power off/red-camera-LED; owner has previously successfully used Volume Up + Power to achieve normal boot.
- Once COM10 returns, read-only compare local-mac-address at /proc/device-tree/mmc@c8000200/wifi@1/local-mac-address, wlan0 address, and private original factory calibration MAC. Public document reports match/mismatch, no MAC bytes. Ensure address is unicast and not generic Broadcom placeholder.
- Candidate MAC path unproven on MZ604 until actual boot and checks. Do not misclassify a red LED boot handoff issue as MAC source failure.
- If kernel does not boot, physically re-enter p6 TWRP, validate identical device and full backup receipt, then explicit known-good p7 restore with guarded procedure. Preserve all protected partitions.
