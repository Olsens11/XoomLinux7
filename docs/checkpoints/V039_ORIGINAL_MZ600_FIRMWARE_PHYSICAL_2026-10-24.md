# v039 physical — authentic 2011 Motorola firmware one-variable test

**Date:** October 24, 2026. **Result:** OEM firmware RAM upload and startup verification PASS; **SDIO Function 2 still FAILED -62**. Original generic firmware restored and verified; no flash, reboot, kernel/DTB/power/PMU/NVRAM change, network scan/association, or exposure of per-unit identifiers. Tested replacement MZ600 running existing temporary-boot v034 with v038 diagnostic brcmfmac module staged in RAM.

## Preflight and strict single-variable design

Compare two private BCM4329B1 firmware images:
- Known generic Linux 7 baseline: `brcmfmac4329-sdio.bin`, **253,748 bytes**, SHA256 **`d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`** (same as v026 baseline; CRC32 `B4092AA6`).
- Early **Motorola MZ600 HRI39/HRI66** `fw_bcm4329.bin`, **261,317 bytes**, SHA256 **`7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`**, BCM4329B1 firmware `4.218.248.20`, built Jan 12, 2011. Original companion `bcm4329.ko` matches Linux `2.6.36.3-g2a65edc` generation.

Both files were staged privately on Surface Book 2 using authorized device file transport; independently verified full SHA256 and length **before touching Xoom RAM**. Generic firmware was staged as explicit rollback and confirmed accessible locally. Neither image has been committed to this public repository.

The **only independent hardware variable** is Wi-Fi firmware image. v038 module, Linux 7 kernel, original generic textual NVRAM, MMC2 AUTO profile, Bluetooth unloaded, v034 USB server and chip power/regulator/pin sequencing stayed unchanged. No user-level network connection, scanning or association initiated.

## Physical experiment

1. Existing USB `WIFI_STOP` state confirmed; upload Motorola private firmware through guarded `UPLOAD FIRMWARE` to existing RAM filesystem path `/lib/firmware/brcm/brcmfmac4329-sdio.bin`. Device ACK: `UPLOAD DONE SIZE 261317 CRC32 0x44E3938F`, **RAM_ONLY_UPLOAD_VERIFIED**.
2. `WIFI_START` loaded brcmutil and the existing **v038** brcmfmac observer, both rc0. Firmware loader reported `brcm/brcmfmac4329-sdio.bin found`, expected textual NVRAM found, CLM blob optional absent.
3. v038 recorded the same RAM/processor handoff:
   - `PRE_CM3_RELEASE arm_up=0 ram_base=00000000 ram_size=294912 nvram_packed=672 tail_read_rc=0 token_matches=1`;
   - `POST_CM3_RELEASE arm_up=1`; `PRE_F2_REQUEST arm_up=1`;
   - `XOOM_V038_MAILBOX write_rc=0 sdpcm_protocol=4`;
   - `ChipCommon rev=29 PMU rev=6`, `PMUStatus=0xAE` at release and `0xBE` before F2, `res_state=0x003FE63E`, `res_pending=0`, ChipCommon pullups/pulldowns 0.
4. The SDIO bus again requested F2, with **IOEx=06 / IORx=02; `enable F2: err=-62`** after normal 3-second timeout. Firmware-side diagnostic printed `firmware not built with -assert`; that is not independent proof of firmware execution or a fatal assertion.
5. `WIFI_STOP` returned brcmfmac and brcmutil rc0; the original generic firmware was **immediately restored** through guarded RAM upload. ACK `UPLOAD DONE SIZE 253748 CRC32 0xB4092AA6`, the known original value. Final `MMC2_STATUS`: USB COM9 responsive, target valid, BCM4329 verified, MMC2 bound, AUTO profile 0, driver modules unloaded.

Private sanitized logs retained locally on Surface as `v039-oem-fw-trial1-sanitized.log`. No original firmware bytes, board calibration bytes, MAC addresses or serial values included in Git.

## Interpretation

**Ruled out for this one-variable trial:** the hypothesis that merely replacing the current generic image with Motorola's **original matching-generation 2011 BCM4329B1 firmware**, while preserving current generic NVRAM, repairs the F2 timeout. It does not. This also shows that the diagnostic ROM/SOCRAM and MCU reset-release sequence tolerates either firmware up to the common F2 failure boundary. It does **not** establish that either firmware executes its intended initialization to completion.

**Not ruled out:** Motorola firmware's behavior with exactly Motorola's complete device-specific calibration/regulatory/identity configuration, physical full POR timing, board-specific ATAG/platform MAC handoff, internal CM3 hangs or firmware/host mailbox semantics. Changing firmware did not change power sequencing or driver callback chronology.

## Parameter-by-parameter NVRAM reference comparison

Current Linux `firmware-reference-v07` and `firmware-reference-v08-OEM-MZ600-private` text NVRAM references are byte-identical (**1550 bytes**, SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`). A private parsed-key/value comparison against original Motorola HRI39 `bcm4329.cal` (1595 bytes raw) found **51 Linux keys**, **54 Motorola unique keys**, all 51 common keys having **identical values**, and precisely three Motorola-only keys: `macaddr`, `ccode`, `regrev`. This validates equivalence of shared *reference text values*, not per-unit identity provenance or final runtime firmware consumption.

In the actual 2.6.36 Motorola [`board-stingray-wifi.c`](https://android.googlesource.com/kernel/tegra/+/2a65edc/arch/arm/mach-tegra/board-stingray-wifi.c) ~178–226:
- A distinct **`ATAG_STINGRAY_MAC`** (`0x57464d41`) bootloader handoff populates `stingray_mac_addr` via `parse_tag_wlan_mac`; an uninitialized fallback generates address suffix bytes and the platform callback `stingray_wifi_get_mac_addr` returns it.
- `stingray_wifi_control` exports **`.get_mac_addr`**, set_power/reset/carddetect and memory-preallocation callbacks.
- **This pinned 2.6.36 board source does not export `.get_country_code`**. Earlier generic summaries mentioning country callback must not be attributed to this specific build. The OEM `ccode`/`regrev` NVRAM values are separate from this board's MAC callback.
- Source confirms capability to provide platform MAC; **the exact external caller, compiled flags, and precedence versus `macaddr` in NVRAM are still to be traced**. Do not copy OEM MAC or arbitrary regulatory fields from one tablet to another.

## Next evidence gate

Before any configuration change, audit source/compiled symbols for `wifi_get_mac_addr`, `dhd_custom_get_mac_address`, actual MAC injection and NVRAM strip/firmware expectations under Motorola 2.6.36 versus Linux 7. Resolve per-device MAC provenance for replacement MZ600 from a legitimate on-unit source without publishing identity. Consider one controlled NVRAM experiment only when the omission and genuine regulatory context are understood. Otherwise instrument a strictly read-only firmware-alive/CM3 internal marker with a documented source-derived register; do not infer CPU execution merely from `arm_up=1`.

**Acceptance:** private OEM version verified; guest RAM firmware upload CRC PASS; physically observed alternate FW startup PASS through CM3 release and mailbox; F2 FAIL -62; rollback generic CRC PASS; modules unload and MMC2 bound PASS.
