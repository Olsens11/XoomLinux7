# v034 — HCI ioctl ABI correction and physical BCM4329 test

**Date:** October 24, 2026. **Result:** v034 temporary Linux boot and corrected Bluetooth HCI device-down operation **PASS on replacement Xoom**. Device in known safe state at end; no partition writes or flash. WLAN F2 remains unresolved from previous v033 test; it was not unnecessarily retested in v034.

## Root cause of v033 BT_OFF -19

Linux 7 `net/bluetooth/hci_sock.c` `hci_sock_ioctl()` handles `HCIDEVUP` and `HCIDEVDOWN` by directly calling `hci_dev_open(arg)` and `hci_dev_close(arg)`; argument is **HCI device index by value**, not a pointer to an int. v033's freestanding PID1 incorrectly called `iof(fd, ..., &dev)`, so the kernel used that address as the index and returned `-ENODEV (-19)`. The v034 source instead calls `iof(fd, ..., (void *)(uintptr_t)dev)`, with index 0 for `hci0`. No kernel-side or Broadcom radio firmware change was needed for this correction.

Also corrected misleading v033 USB messages: `BT_START` now acknowledges that Linux HCI UART module registration **can automatically power Bluetooth**, the USB status flag is named `BT_USB_ON_REQUESTED_FLAG`, and `BT_OFF` no longer treats -19 as successful shutdown. New host client refuses BT commands unless v034-specific HELP signature `V034_HCI_IOCTL_BY_VALUE` is present.

## Exact artifacts

- v033 frozen parent: 6,979,584 bytes, SHA256 `6806f2aa87abbfecf0b2f8a3625292de5366a4a52370d10e61cd53204069fb45`.
- v034 candidate `MZ600-v034-HCI-IOCTL-TEMPBOOT-ONLY.img`: **6,979,584 bytes**, SHA256 **`9850361687f6d121119a0c3399cdc0abaa68d8e9714238aba5bb9b7207a0af39`**.
- Kernel+DTB frozen exactly from v033 SHA256 `05ec405506d4c96459787f00581acf7385caa207b43d8f4632f22e8af824a395`. v025 verified 25MHz legacy MMC2 and 100ms host/300ms pwrseq sequencing unchanged. All six Bluetooth modules, all Wi-Fi modules and BCM4329 firmware/NVRAM bytes identical to v033.
- v034 init ARM ELF bytes SHA256 `c1dedbfcd60626b2258df91052c4f197713b59947143be4c215285d74d6e25d1`; RAM gzip SHA256 `7e4eeca0119914693ac243c1cf50d6ef9b36a40d78cf016c32e4b8b136af967b`.
- Independent audit passed Android image-header SHA1, original v033 kernel/DTB/CMDLINE identity, same set of newc entries, **only changed init**, HCI argument-by-value source guard and ABI HELP marker. Surface separately verified exact image SHA and PowerShell script syntax.
- Rollback remains physically proven v025 image (6,662,144 bytes) SHA256 `142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb`.

## Live hardware execution

1. From safely shut down v033 test, guarded USB requested reboot, verified Android ADB identity for replacement MZ600, rebooted bootloader, verified fastboot `product=xoom-cdma`, `unlocked=yes`, target unique. Only command used to install environment was **`fastboot boot`** with SHA-verified v034 image. No flash.
2. v034 USB COM9 returned, v034-specific `BT_STATUS` confirmed no HCI modules or controller and state flag zero.
3. `BT_START` loaded all six modules with return code 0; USB message now correctly says `AUTO HARDWARE INIT MAY HAVE OCCURRED`. `BT_STATUS` showed HCI0 PRESENT and six modules loaded; USB-specific BT_ON requested flag 0.
4. Kernel read BCM4329B1 over UART again, chip id 41, features 0x04, firmware version `002.002.023`, build 0000. It still looked for a missing optional `.hcd` patch.
5. **Corrected v034 `BT_OFF` returned `BT OFF HCI_DEV_DOWN rc 0`, `BT OFF HCI_DEV_DOWN COMPLETE`**, compared with -19 under the same v033 kernel and modules. This proves the userspace ABI correction on actual Xoom.
6. `BT_STOP` then removed all six modules rc0, and kernel emitted `BT_RESET_REQUEST release=0` and `BT_U4_VOTE_OFF`. Logged startup U4 vote ON and reset release at t≈31.925s; shutdown/unload U4 vote OFF and reset assert at t≈76.064s. There is **not enough event timing evidence to attribute the U4 vote release specifically to `BT_OFF` rather than to `BT_STOP`**; the latter is where teardown was previously observed.
7. Final USB BT_STATUS: HCI UART NOT LOADED, HCI0 ABSENT, both USB flags zero, `/proc/modules` empty. Final MMC2_STATUS: target valid, BCM4329 verified, MMC2 bound, AUTO profile 0, Broadcom modules unloaded, USB reachable.

## Boundaries and next research

- A kernel-level regulator vote ON/OFF and UART chip-identification response do not prove BCM4329 internal 1.25V VDDC fully shut off, pin voltages or true power-on reset. U4 may remain asserted by active MMC power/regulator boot-on and other consumers. No analog measurements were taken.
- The HCI `.hcd` patch file is absent; Bluetooth HCI initialization progress and chip identity do not establish fully functional patched Bluetooth/RF.
- Wi-Fi F2 previously failed -62 after the entire v033 Bluetooth cycle. This v034 test intentionally isolated the ioctl fix rather than rerunning F2 without a new mechanism.
- Next highest-value work: trace chip internal PMU resource availability, 38.4MHz normal reference, WLAN Cortex-M3 execution and F2-ready handshake. Keep v025 fallback and v034 corrected shutdown path.

## Reproducibility

- `src/diag-init/phase1-v034/init.c` — the corrected freestanding no-NEON userspace.
- `scripts/experiments/v034-make-source.py`, `v034-build-init.sh`, `v034-package-hci-ioctl.py`, `v034-independent-audit.py` — generator, compiler, packaging and independent verifier.
- `scripts/host/surface/Xoom-v34-BluetoothLiveLab.ps1` — v034-specific USB HELP guard and success handling. Physical result was obtained with its `BT_STATUS`, `BT_START`, `BT_OFF`, `BT_STOP`, `LOGS`, `MMC2_STATUS` actions.
- [v033 baseline physical test](V033_BLUETOOTH_PHYSICAL_2026-10-24.md) and [whole-chip Motorola architecture](../research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md).
