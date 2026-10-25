# BCM4329 support/firmware-layout hypothesis and newly supplied BCM4329B1.hcd — evaluated 2026-10-24

## Scope and outcome

A proposed generic Linux repair sequence (un-blacklist `brcmfmac`, put `brcmfmac4329-sdio.bin` and `brcmfmac4329-sdio.txt` in `/lib/firmware/brcm`, then `modprobe -r; modprobe`) was evaluated against existing **measured** MZ600 Linux 7 runtime and a newly supplied `BCM4329B1.hcd` Bluetooth patch from LibreELEC.

**Result: not an applicable missing-file fix.** The v026 *physical* provenance checkpoint already demonstrated actual driver load, path resolution, returned firmware and NVRAM contents, NVRAM packing, and firmware memory readback, all prior to the F2 `-62` timeout. It is wrong to prescribe generic desktop `modprobe` or blindly copy another board's NVRAM to this RAM-only Xoom diagnostic initramfs. Keep inspecting Cortex-M3 firmware activation, SDIO startup sequencing and whole-chip power/clock/OR reset history.

## Firmware/NVRAM was present and exercised on actual replacement MZ600

[Authoritative v026 runtime provenance](../checkpoints/V026_RUNTIME_PROVENANCE_PHYSICAL_2026-10-24.md) reports:
- `brcmfmac` first searched `brcm/brcmfmac4329-sdio.motorola,stingray.bin`, did not find it and **fell back successfully** to `brcm/brcmfmac4329-sdio.bin` (generic 253748-byte firmware image).
- For NVRAM, board-qualified `brcm/brcmfmac4329-sdio.motorola,stingray.txt` was attempted before successfully returning `brcm/brcmfmac4329-sdio.txt`, **1550 bytes, CRC32 FAFCC93A**.
- Linux converted that file to a **672-byte** on-chip packed NVRAM buffer, **CRC32 596925B1**, matching independent offline packers.
- Runtime platform MAC callback was **not available**, and the generic NVRAM file does not specify an explicit MAC. This is a genuine *per-device identity provenance gap*, **not** evidence that NVRAM failed to load or the cause of F2 `-62`. Do not copy an identity or calibration from a different Xoom.
- v035–v037 subsequently validated PMU/core release and SDIO mailbox but confirmed F2 `-62` even after repeated module-only warm reloads.

[Actual v034 USB diagnostic init source](../../src/diag-init/phase1-v034/init.c) has a bounded RAM uploader for `/lib/firmware/brcm/brcmfmac4329-sdio.bin` and `.txt`, a RAM-staged module `/run/brcmfmac.ko`, and direct `WIFI_START/WIFI_STOP` commands. This is **not** a desktop filesystem using modprobe blacklist configuration by default.

The [Linux Wireless brcm80211 documentation](https://wireless.docs.kernel.org/en/latest/en/users/drivers/brcm80211.html) lists BCM4329 in `brcmfmac` SDIO support and notes SDIO uses per-board NVRAM with filenames indicated in kernel logs. `brcmutil` is a support library, not a standalone SDIO Wi-Fi driver. The user's cited [LibreELEC repository](https://github.com/LibreELEC/brcmfmac_sdio-firmware) includes specific other-board `.txt` files, **not** a guaranteed calibrated Motorola Stingray `.txt`.

## Uploaded BCM4329B1.hcd: validated but Bluetooth, not WLAN SDIO firmware

- User-uploaded `BCM4329B1.hcd`, **17332 bytes**, SHA256 **`7fbab01012c909b9b2de0fda3a76c43fa1c5c150e08642d7d1dbaf4d5ebf887c`**.
- Full Broadcom Bluetooth patch HCI record stream parsed without truncation: **97** vendor `0xFC4C` RAM-download commands plus **1** `0xFC4E` launch command; **98 HCI commands total**.
- Byte-for-byte matches the file at [LibreELEC `BCM4329B1.hcd`](https://github.com/LibreELEC/brcmfmac_sdio-firmware/blob/master/BCM4329B1.hcd), SHA verified independently from upstream download.
- **Original Motorola MZ600 HRI39 and HRI66** images both hold `/system/etc/firmware/bcm4329.hcd`: **17770 bytes**, SHA256 **`2d68db625a3e4e32fcc30813746fb84ca37491e055ad5e5e5d43057e4f2c16ea`**, **101** `0xFC4C` commands + **1** `0xFC4E`, **102 total**. Both originals agree, but differ from new file.
- These patch payloads are **Bluetooth UART/HCI RAM patches**. They are not `fw_bcm4329.bin` or `brcmfmac4329-sdio.bin`; they do not replace Linux 7 WLAN SDIO firmware and should not be flashed or mixed into the WLAN path.
- Keep both patches private as necessary, distinguish provenance and qualification, and only compare/apply Bluetooth patches in a separate reversible BT integration experiment. Current priority remains Wi-Fi F2.

## Next evidence

1. Resume v038: observe original NVRAM final-word token and Cortex-M3 core status immediately before/after existing firmware release, **without printing raw identity/config values and without adding chip writes**.
2. Check whether the currently deployed 1550-byte generic NVRAM has the right Xoom board antenna/clock/regulatory calibration **and** has a legitimate per-device identity route. Treat this as an offline provenance question, not an invitation to transplant MACs.
3. Preserve the Jan 2011 OEM 261317-byte Wi-Fi firmware / 1595-byte calibration separately from the Bluetooth HCD; compare their RAM/NVRAM ABI with generic Linux 7.
4. Do not start tests by manipulating shared U4/WL_REG_ON/BT_REG_ON or changing ROM; current replaceable module and v034 temporary-boot rollback baseline must remain intact.

**Device status when checked:** USB COM9, MMC2 bound, BCM4329 verified, Wi-Fi modules unloaded, AUTO profile. No reboot, new flash, driver upload or power changes during this comparison.

## Follow-up: complete LibreELEC master file-tree verification

The supplied [LibreELEC repository master tree](https://github.com/LibreELEC/brcmfmac_sdio-firmware/tree/master) was enumerated with the GitHub tree API (`recursive=1`, 133 total entries; `truncated=false`) rather than relying only on the README. **No Motorola/Stingray-specific firmware or NVRAM entry exists in that tree**, nor a generic `brcmfmac4329-sdio.txt`. BCM4329 Wi-Fi references present:

- `brcmfmac4329-sdio.bin`: ordinary Git blob SHA-1 `d4c4560cddbc305afae1f92b43fa105d45fd9d5a`, 253748 bytes.
- `brcmfmac4329-sdio.solidrun,cubox-i-dl.txt`: 1287 bytes; `solidrun,cubox-i-q.txt` is a symlink to that board configuration.
- `brcmfmac4329-sdio.wand,imx6dl-wandboard.txt` and `wand,imx6q-wandboard.txt`: respectively file and symlink for another board-specific NVRAM, not proven appropriate for MZ600.
- The `*.solidrun*` and `*.wand*` `.bin` entries are symlinks back to `brcmfmac4329-sdio.bin`.
- `BCM4329B1.hcd`: 17332-byte Bluetooth HCI patch as separately parsed above.

**Independent local identity verification**: on the Desktop Ubuntu-22.04 WSL development environment, `git hash-object /home/xoomdev/xoom-linux-rom/firmware-reference-v07/brcm/brcmfmac4329-sdio.bin` returned **`d4c4560cddbc305afae1f92b43fa105d45fd9d5a`**, *exactly* the official GitHub tree object's SHA-1. Local normal Wi-Fi binary was 253748 bytes and SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`. Thus the LibreELEC main BCM4329 WLAN image is **byte-for-byte identical to our existing v07 reference image**. The existing Linux v026 physical provenance already verified the 253748-byte firmware load path, so re-downloading the LibreELEC copy cannot address an unavailable firmware file.

The distinct *later* Motorola private firmware in the same development environment has size 264140 bytes and SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`. The early 261317-byte Motorola reference is documented in v5. Do not assert the binary identity comparison alone proves what code the on-chip Cortex-M3 executes successfully; F2 remains -62.

**Consequence:** no change to modules, initramfs, firmware file layout, calibration, or physical hardware follows from the linked LibreELEC repository. Keep v038 Cortex-M3/NVRAM handoff instrumentation and board power/POR verification as independent pending tasks.
