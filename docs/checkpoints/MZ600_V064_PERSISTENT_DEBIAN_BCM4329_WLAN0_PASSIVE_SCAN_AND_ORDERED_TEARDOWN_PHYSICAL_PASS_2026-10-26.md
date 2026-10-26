# MZ600 v06.4 — PERSISTENT Debian BCM4329 wlan0, passive Wi-Fi scan, ordered teardown: PHYSICAL PASS

**Physical date:** 2026-10-26, via Surface USB COM9 root shell on the **experimental replacement** Motorola Xoom MZ600. **Scope:** normal *persistent internal p8 Debian* Linux 7 runtime, not temporary v06.x initramfs and NOT a deployment test of the experimental whole-chip pwrseq provider. Owner explicitly requested live `wlan0` bring-up and Wi-Fi scan and noted previous red-LED problems were usually associated with restarting; **NO reboot or flash occurred**.

## Source, software and device preflights

- Canonical reproducible guarded test script: `scripts/host/xoom/test-v064-wlan0-passive-scan-bounded-20261026.sh` (GitHub active branch `wip/clean-wifi-bt-usb-20261025`), bash syntax checked via Desktop WSL and repository validator passed.
- Exact source script SHA256 **`12c1656a11317eede8f856f1685e95bb1d4262c19fb2c3ac47ee3191ad113425`**.
- SHA-pinned 103-line Surface owner-terminal heredoc `captures/MZ600-V064-WiFi-WLAN0-PassiveScan-OneShot-OWNER-20261026.txt`, SHA256 **`8169256e846daf972e1569610dc2101cc30461ae0d6381c2373d76417bb4a0b8`**, inner SHA rechecked against canonical.
- A strictly one-shot Python COM9 runner revalidated active **UID 0**, `uname -r=7.0.0-next-20260422+`, root `/dev/mmcblk0p8 ext4`. Source matched before any active test command.
- Standard `dbus.socket` and `dbus.service` now active from [official Debian D-Bus repair](MZ600_V064_DEBIAN_DBUS_OFFLINE_SIX_PACKAGE_INSTALL_SYSTEM_BUS_PHYSICAL_PASS_2026-10-26.md); `wpa_supplicant`, NetworkManager and iwd were inactive before activation.
- Three Broadcom modules NOT loaded initially; `wlan0` absent; mmc2 SDIO `mmc2:0001:1` present; factory original bootloader FDT MAC property exactly six bytes, no actual value printed. Broadcom `.bin` and NVRAM `.txt` present.
- `iw` v5.19 `scan` help **explicitly supports passive scan with selected frequencies**. World regdom `country 00`; upstream-signed regulatory.db and .p7s selected via standard Debian alternatives. No `iw reg set`, `ccode/regrev` modifications, fabricated MAC or country override.
- 2.4GHz channels 1, 6 and 11 chosen as conservative test frequencies within the OEM US/MZ600 1–11 restrictions. No forced AP association, DHCP, WLAN credentials or arbitrary extended 5GHz operation.

## Physical console result — FIRST installed-p8 Debian live WLAN test

Real native Xoom terminal output, following one `modprobe brcmfmac-wcc` (resolving brcmfmac+brcmutil), short wlan0 wait, phy/identity checks, `ip link set wlan0 up`, and **one** `iw dev wlan0 scan freq 2412 2437 2462 passive` under a 35-second watchdog:

```text
MZ600_WIFI_BOUNDED_PREFLIGHT_BEGIN
MZ600_WIFI_BOUNDED_PREFLIGHT_PASS
MZ600_WIFI_DRIVER_LOAD_BEGIN
MZ600_WIFI_WCC_MODPROBE_RC0
MZ600_WIFI_WLAN0_PHYSICAL_PRESENT
MZ600_WIFI_ADDR_ASSIGN_TYPE_PERMANENT_PASS
MZ600_WIFI_ALL_3_DRIVER_MODULES_LIVE
MZ600_WIFI_PHY_2G_CHANNELS_1_6_11_PRESENT
MZ600_WIFI_WLAN0_LINK_UP_REQUEST_SUCCESS
MZ600_WIFI_PASSIVE_SCAN_2G_START
MZ600_WIFI_PASSIVE_SCAN_COMMAND_RC=0
MZ600_WIFI_SCAN_PRIVATE_BYTES=51104
MZ600_WIFI_SCAN_PRIVATE_SHA256=aae3f1fb5df8799fefa8dbe653093ae8f5a22b0278fcf1d0d354b4e594c41ce1
MZ600_WIFI_PASSIVE_SCAN_BSS_COUNT=19
MZ600_WIFI_PASSIVE_FREQ=2412 BSS=8
MZ600_WIFI_PASSIVE_FREQ=2437 BSS=4
MZ600_WIFI_PASSIVE_FREQ=2462 BSS=5
MZ600_WIFI_PASSIVE_SCAN_PHYSICAL_SUCCESS
MZ600_WIFI_BOUNDED_CLEANUP_BEGIN rc=0
MZ600_WIFI_LINK_DOWN_REQUESTED rc=0
MZ600_WIFI_UNLOAD_brcmfmac-wcc rc=0
MZ600_WIFI_UNLOAD_brcmfmac rc=0
MZ600_WIFI_UNLOAD_brcmutil rc=0
MZ600_WIFI_BOUNDED_CLEANUP_VERIFIED_DRIVER_UNLOADED_WLAN0_ABSENT
MZ600_WIFI_PASSIVE_SCAN_BOUNDED_TEST_FINAL_PASS
HOST_RESULT=FULL_PASS
```

**Result level:** Native persistent Debian driver+firmware initialization, `wlan0` physical appearance, permanent MAC *address-type flag* `0`, channel inventory, interface UP, one successful passive scan, and complete symmetric module teardown all **PHYSICAL PASS**. The permanent MAC address-type flag is NOT a byte-for-byte comparison to the protected original factory MAC; preserving dynamic FDT identity is separately checked by prior checkpoints.

## Anomalous frequency metadata — do not misattribute RF operation

A **separate read-only post-test on-device examination** of the raw private scan file independently re-counted **19 BSS blocks**, 51,104 bytes and exact same SHA256. It found:

| Result-reported frequency | Channel | BSS entries |
| --- | --- | ---: |
| 2412 MHz | 1 | 8 |
| 2437 MHz | 6 | 4 |
| **2442 MHz** | **7** | **2** |
| 2462 MHz | 11 | 5 |
| **Total** | | **19** |

**Important:** Although the invocation explicitly selected only frequencies 2412, 2437 and 2462 in `passive` mode, the Broadcom driver/firmware returned two BSS results labeled **2442 MHz**. This does **NOT** independently prove it tuned to channel 7 in this transaction. Could be firmware cache, an extra PHY report, ignored scan filter or another behavior; requires controlled kernel/firmware trace before attributing cause. The requested operation was a *passive* scan, but without a sniffer it does not prove the radio emitted zero probe frames. No active scan command was sent by our script.

The raw scan body includes private nearby SSIDs/BSSIDs. **DO NOT publish raw scan data or device MAC.** The raw file remains only on Xoom volatile `/run/mz600-v064-wifi-passive-scan-20261026-private.txt`; its checksum is public so private captures can later be correlated.

## Firmware provenance and clean shutdown

Read-only post-test boot journal:

```text
brcmfmac: brcmf_fw_alloc_request: using brcm/brcmfmac4329-sdio for chip BCM4329/3
usbcore: registered new interface driver brcmfmac
brcmfmac: brcmf_c_process_clm_blob: no clm_blob available (err=-2), device may have limited channels available
brcmfmac: brcmf_c_process_txcap_blob: no txcap_blob available (err=-2)
brcmfmac: brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: Sep  2 2011 14:48:19 version 4.220.48
usbcore: deregistering interface driver brcmfmac
```

Missing optional CLM/TXCAP files did **not** prevent init or passive scanning. Do **not** inject arbitrary blobs just to silence those notices. The clean teardown uses **WCC → brcmfmac → brcmutil**; every `modprobe -r` returned **0**, interface down returned 0, and cleanup actually checked absent `wlan0` and `brcm*` module entries.

**Independent COM9 post-audit** confirmed:
- Still authenticated UID0, kernel `7.0.0-next-20260422+`, root `/dev/mmcblk0p8 ext4`, USB shell alive.
- `ls /sys/class/net`: `ip6tnl0 lo sit0`; no `wlan0`.
- `/proc/modules`: **no Broadcom drivers loaded**.
- `systemctl is-active dbus.socket dbus.service`: **active / active**.
- Raw private scan file checksum and 19 BSS entries independently match guarded runner outputs.

No reboot or p7, p6, GPT or boot partition writes; no claim that removing drivers actually forced shared-chip full internal regulator POR. Kernel whole-chip provider remains compile-only and not integrated.

## BCM4329 full-chip Linux 7 patch-series implications

This is **an important installed-userspace physical validation of the existing generic BCM4329 drivers**, not a hardware validation of `src/chip/stingray-bcm4329-pwrseq.c`. Carry into [whole-chip patch integration ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md) and [multi-device qualification gates](../plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md).

- We can preserve existing generic `brcmfmac` functionality while addressing real U4/I7/U0/U2/LPO shared-resource coordination in minimal separate patches. Do not “fix” a resolved F2 bug merely because an early experimental v025 showed `-62`.
- Future experiments must measure shared regulator votes and Bluetooth serdev/clock/GPIO owner state rather than extrapolate from successful scan and WCC unload. Combined WLAN+BT under proposed provider **not tested**.
- Investigate unexpected `2442 MHz` returned BSSs separately with trace after setting deterministic scan cache state; no assumption that the radio scanned a forbidden channel.
- For own-use release and later review, repeat on independently identified MZ600/MZ602/MZ604 with per-unit OEM identity and calibration, automatic bounded teardown and serial reliability. **No claim multi-device patch-series qualified; no upstream submission requested.**
- Next userland milestone may be selected-network association with **user-authorized credentials**, firmware country/regrev legal verification and no auto-connection guesses. Do not autostart a network manager or leave a radio on unintentionally.

**Acceptance: PERSISTENT INTERNAL DEBIAN WLAN0 PASS; PASSIVE 2.4GHz SCAN PASS; 19 BSS; ORDERED MODULE UNLOAD AND USB/D-BUS PRESERVATION PASS.**

## Final post-scan physical boot integrity checksum

After completed scan, teardown and independent COM9 post-audit, a **separate** read-only raw-eMMC operation again returned `sha256sum /dev/mmcblk0p7 = 901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`, matching the long-preserved full 8MiB Stage-D p7 boot baseline. `blkid -s UUID /dev/mmcblk0p8` returned `c2fb0167-7143-4186-b284-c86d6c09ea64`, matching installed Debian root fstab. **No boot partition mutation or filesystem-ID drift** from Wi-Fi scanning.
