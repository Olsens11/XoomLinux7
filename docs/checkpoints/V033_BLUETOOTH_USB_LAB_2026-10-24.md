# v033 — USB-controlled Motorola BCM4329 Bluetooth RAM test

**Status, 2026-10-24:** BUILD, HOST STAGING, and INDEPENDENT VERIFICATION PASSED. This does not by itself establish a physical Bluetooth power-on or a Wi-Fi repair. **NEVER FLASH**.

## Frozen v025 baseline and validated candidate

- v025 SHA256: `142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb`; size 6,662,144 bytes. Rollback preserved on Surface Book 2.
- v033 candidate: `MZ600-v033-BLUETOOTH-USB-TEMPBOOT-ONLY.img`; SHA256 `6806f2aa87abbfecf0b2f8a3625292de5366a4a52370d10e61cd53204069fb45`; size 6,979,584 bytes, under 8MB limit. Surface independently verified image and rollback hashes.
- Linux zImage bytes, Android boot address/command-line fields, all original Wi-Fi modules, Broadcom firmware, NVRAM and MMC2 code remain identical to v025. Only BT-node DT properties and external RAM initramfs differ.
- BT node delta: Motorola plus Broadcom compatible, `motorola,shared-u4-power` opt-in, shared regulator supply pointing to MMC2's existing U4-backed vmmc, 32,768-Hz clock correctly named `lpo`, and `status=okay` (BT driver remains a module, not loaded at boot).
- MMC2 max-frequency **25,000,000Hz legacy**, host pre-reset delay 100ms and Wi-Fi pwrseq post-reset delay 300ms remain unchanged. No system/recovery storage mounts or writes.
- New rootfs: freestanding no-NEON Cortex-A9-tested `/init` plus six modules (`ecc`, `ecdh_generic`, `cmac`, `bluetooth`, `btbcm`, patched `hci_uart`) in `/bt`. The first full module build revealed missing ECDH dependencies; rebuilding with ECC/ECDH/CMAC linked successfully. All module vermagic fields matched Linux `7.0.0-next-20260422 ARMv7`.
- Original `drivers/bluetooth/hci_bcm.c` restored byte-for-byte after the module build, SHA256 `3cdaf7e671babfc131f94909c009de0450e6da628786b2f9d9220c85d862bda2`.
- Independent verifier passed Android boot header SHA1, original kernel binary identity, all original rootfs files other than `/init` unchanged, six module bytes, modified BT DT properties and clock, and existing MMC2 properties.

## Explicit USB command safety protocol

`BT_STATUS`: show module and HCI status. `BT_START`: load six modules in dependency order, only when Wi-Fi unloaded and card/USB preflight passes; never calls HCI up. `BT_ON`: explicitly request HCI device 0 power-up through HCI ioctl; blocked while Wi-Fi driver present. `BT_OFF`: issue HCI device down. `BT_STOP`: unload in reverse order, only after BT power down, require all six modules absent. While BT is loaded, Wi-Fi start, RAM uploads and MMC2 reinit refuse conflicting operations.

Bluetooth modules do **not** auto-load during boot. Host v033 client checks that the USB HELP response advertises the new BT commands before sending them; its negative dry-run on existing v025 correctly stopped at this guard with no Bluetooth command.

## Controlled physical test plan

Preserve the original v025 image on Surface. Confirm the replacement Xoom identity through Android ADB, reboot to fastboot and validate `xoom-cdma` and unlocked status, then use `fastboot boot` **only**, never `fastboot flash`. Verify USB, `BT_STATUS` (unloaded), MMC2; execute `BT_START` first, check new driver binding and controller GPIO actions. Request `BT_ON` only if previous state is safe; inspect regulator-vote/reset timestamps, then `BT_OFF`, `BT_STOP`, and verify MMC2 and module cleanup. Any physical result must be documented separately.

## Reproduction

- `scripts/experiments/v033-build-init-source.py` and `src/diag-init/phase1-v033/init.c`
- `scripts/experiments/v033-build-bt-deps.sh` (source restore on failure)
- `scripts/experiments/v033-build-init.sh` (ARM no-NEON QEMU selftest)
- `scripts/experiments/v033-package-tempboot.py` (frozen v025 kernel + BT DT + new external ramdisk)
- `scripts/experiments/v033-independent-audit.py` (separate verifier)
- `scripts/host/surface/Xoom-v33-BluetoothLiveLab.ps1` (v033-specific USB preflight/client)

**No root-cause claim:** prior physical v031 found BT serdev child registered but unbound, and the WLAN SDIO F2 ready bit remains missing with timeout `-62`. Adding a Bluetooth power driver does not automatically fix that independent WLAN failure.

## Physical test completed
v033 successfully temporary-booted the replacement Xoom; USB new PID1 and dormant BT status validated. Six BT modules load, but hci_uart module registration itself automatically powers the chip: kernel logs show U4 regulator vote ON, U0 reset released and the BCM4329B1 responding. The BT firmware .hcd patch file is missing. A userspace HCIDEVDOWN argument-by-pointer bug caused -19; subsequent BT_STOP correctly unloaded all modules, logged reset assert and U4 regulator vote OFF. Wi-Fi F2 still times out -62 after the BT cycle. See [exact physical record](V033_BLUETOOTH_PHYSICAL_2026-10-24.md). No flash.
