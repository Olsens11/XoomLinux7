# v039 physical — original Motorola MZ600 HRI39 Wi-Fi firmware, controlled RAM-only comparison (2026-10-24)

**Outcome:** **PASS for verified private OEM firmware transfer, RAM-only test, log capture and exact generic firmware rollback. FAIL for native Wi-Fi**: SDIO Function 2 remains `-62`, CCCR IOEx `0x02→0x06`, IORx stuck `0x02`; `wlan0` absent. This is the first controlled physical Linux 7 trial of the *original early-MZ600* Wi-Fi image (not the May 2012 `fw_bcmdhd.bin` previously evaluated). User explicitly authorized a reversible experiment after reviewing alternative suggestions.

## One changed variable and protected baseline

- Original Motorola [MZ600 HRI39/HRI66](../research/MZ600_HRI39_HRI66_OEM_DRIVER_RECOVERY_2026-10-24.md) production Wi-Fi firmware: `/system/vendor/firmware/fw_bcm4329.bin`, BCM4329B1, **261317 bytes**, embedded `4.218.248.20` dated January 12, 2011, SHA256 **`7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`**. Extracted privately from a verified original Motorola Android `system.img`; firmware bytes **not committed**.
- Known generic rollback firmware: LibreELEC `brcmfmac4329-sdio.bin`, **253748 bytes**, embedded `4.220.48.0`, SHA256 **`d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`**, CRC32 **`B4092AA6`**, previously qualified in v026 and v037.
- Both file SHA256/size values independently verified at source and again on Surface Book 2. No unique MAC, calibration, proprietary firmware bytes or identifiers included in public Git.
- **Unchanged for the experiment**: pre-existing temporarily booted Linux v034 kernel / board DT, v037 `brcmfmac` diagnostic module (462212 bytes SHA256 `2d24bf221f04ada352ccc52efd1041717f25852e730dd54d6285862a02b35bf5`), companion `brcmutil`, existing 1550-byte **Motorola-board configuration with identity/regulatory fields omitted** NVRAM text, MMC2 AUTO profile, full-chip GPIO/reset/power, and CPU firmware download algorithm.
- Private firmware is board-family appropriate but is not assured compatible with a modern Linux `brcmfmac` unless checked. No scan, association, DHCP, regulatory RF transmission, or invented MAC.
- USB RAM transfer under `UPLOAD Kind=FIRMWARE` replaced only the temporary `/lib/firmware/brcm/brcmfmac4329-sdio.bin` payload, with **UPLOAD DONE SIZE 261317 CRC32 0x44E3938F**. No Xoom reboot or flashing.

## Physical original-firmware observation

The existing guarded USB on Surface (COM9) returned `WIFI_START BRCMUTIL rc=0; BRCMFMAC rc=0`. Sanitized log saved privately as `C:\Users\olsen\xoom-linux-rom\downloads\v039-early-OEM-fw-trial-sanitized.log`:

```text
brcmf_sdio_firmware_callback Enter: dev=mmc2:0001:1, err=0
XOOM_V037 phase=T2_BEFORE_CM3_RELEASE pmuctl=012b03bc/0 clkcsr=c8/0 ioex=02/0 iorx=02/0
XOOM_V037 phase=CM3_ACTIVATE_BEGIN
XOOM_V037 phase=CM3_ACTIVATE_DONE
XOOM_V037 phase=T3_AFTER_CM3_RELEASE pmuctl=012b03bc/0 clkcsr=c8/0 ioex=02/0 iorx=02/0
XOOM_V037_MAILBOX write_rc=0 sdpcm_protocol=4
XOOM_V037 phase=T4_PRE_F2_REQUEST pmuctl=012b03bc/0 clkcsr=d2/0 ioex=02/0 iorx=02/0
XOOM_V037_RES phase=T4_PRE_F2_REQUEST ccrev=29 pmurev=6 stat=000000be/0 res=003fe63e/0 pend=00000000/0
XOOM_V037 phase=T5_POST_F2_RESULT pmuctl=012b03bc/0 clkcsr=d2/0 ioex=06/0 iorx=02/0
brcmf_sdio_firmware_callback enable F2: err=-62
brcmf_sdio_firmware_callback failed: dev=mmc2:0001:1, err=-62
```

Additional `Status` returned `WLAN0 ABSENT`. `brcmf_fw_complete_request` reported optional `.clm_blob` missing, which is expected to be optional in this original BCM4329 case; the binary and NVRAM request callback succeeded with `err=0`. The log demonstrates source-controlled release and mailbox write and shows no F2-ready response; it cannot prove on-chip instruction execution or that this firmware was accepted internally.

## Rollback actually performed and verified

1. USB `WIFI_STOP`: **`brcmfmac_rc=0 brcmutil_rc=0`**.
2. RAM-only `UPLOAD Kind=FIRMWARE` restored original generic `brcmfmac4329-sdio.bin`, with successful USB integrity check **`UPLOAD DONE SIZE 253748 CRC32 0xB4092AA6`**, matching original v026 and LibreELEC hashes.
3. USB `MMC2_STATUS`: `TARGET VALID`, `BOUND YES`, `CARD BCM4329 VERIFIED`, `DRIVER MODULES UNLOADED`, `AUTO profile 0`, COM9 responsive.
4. No changes to Android/TWRP, eMMC, protected original Xoom, kernel image/DT, user identity data, calibration, or shared Wi-Fi/Bluetooth regulator.

## What is ruled out (narrowly)

- A **simple substitution** of the authentic January 2011 OEM firmware image for the generic 4.220.48.0 firmware, with the same modern Linux driver and identity-stripped Motorola board NVRAM, **is not sufficient** to resolve the F2-ready timeout.
- Combined with [v038](V038_MMC2_RUNTIME_PM_HOLD_PHYSICAL_2026-10-24.md), two previously untested plausible interventions now have real physical negative results: hold host platform runtime-active over firmware/F2, and swap matched historical OEM Wi-Fi firmware individually.
- This does **not** rule out an OEM firmware plus different chip reset/bootloader handoff, correct same-unit identity/calibration, hidden firmware CPU handshake, or OEM driver-specific memory placement. It also does not prove a physical host clock fault is impossible.

## Next discriminating evidence

Prefer a vetted *read-only* Cortex-M3 wrapper reset-state and end-of-SOCRAM four-byte NVRAM token/placement observer (v040), using the documented Motorola versus Linux 7 SRAM semantics. Verify core power/clock and token placement without dumping variables, MAC or firmware contents, then measure at before/after core release and before F2. Investigate authentic whole-chip POR only after shared U4 / WL_REG_ON / BT_REG_ON pin ownership is proven. No unsupported NVRAM `keep_img`, `sd_drivestrength` or `clkreq` changes or fabricated MACs in this test.

**Result labels:** firmware authenticity PASS; upload private hash/CRC PASS; single-variable source control PASS; F2 FAIL (-62); cleanup and generic rollback PASS.
