# MZ604 W1 physical milestone — MZ604 stock firmware boots; brcmfmac attach fails

**As-of 2026-10-31 approximately 04:24–04:36 EDT.** This is the physical follow-up to [the earlier firmware-absent baseline](MZ604_I0_PHYSICAL_DEBIAN_LOGIN_PASS_W1_FIRMWARE_MISSING_2026-10-31.md). Earlier findings remain true at the time recorded, but the *current* firmware state changed. No patch/reboot/scan/association during this W1 experiment.

## Actual running device and exact sources

- Owner's Wi-Fi-only **MZ604 Wingray**, Debian 12 Bookworm ARMHF, Linux `7.0.0-next-20260422+`, actual Surface **COM10** `xoom` autologin and `sudo -n` UID0 **I0 PHYSICAL PASS**, /dev/loop0 root. Known p7 USB-peripheral diagnostic boot DTB, p8 mini-root and p6 TWRP untouched; original p10 Debian rollback retained. **I1 software reboot from TWRP is unreliable** (red LED/off); manual Volume Up+Power boots Linux. Don't reboot for this W1 experiment.
- Owner's **original MZ604 OEM** firmware stored privately on Surface `private-backups/MZ604-WINGRAY-STOCK-20261029`, not online or reused MZ600 image. Station `fw_bcmdhd.bin`: 259327 bytes, SHA256 `6c2ef077ccfe334246ee50eef21a2aa78d3ca6c696096bec11d618909940cb9e`. NVRAM `bcm4329.cal`: 1594 bytes, SHA256 `94d030b06042157817309b46dc9ebbe3e98f7acaa876979b5a480bcfe897eab8`. Calibration text contains board-specific factory identity, MAC and regulatory information: **never publish raw bytes, MAC, SSID or vendor firmware**. APSTA binary not used.
- Source `sdio.c` on untouched pinned Linux `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` defines `brcmfmac4329-sdio` with `.bin`, `.txt`, optional `.clm_blob`; source `firmware.c` accepts ASCII key/value NVRAM, comments and skips RAW1. No fabricated MAC/region or source patch was applied.

## Private COM10 transport and exact on-device changes

- Surface host `MZ604-COM10-STAGE-PRIVATE-20261031.py` developed 1536-byte base64 chunks with ACK per chunk and SHA verification, using only built-in Bash/base64/sha256sum (target has no Python3). **2571-byte harmless test file** roundtrip host↔guest SHA PASS; then full OEM station firmware and board cal source→target SHA PASS.
- Staged files remain in guest `/home/xoom/xoomlinux7-private-staging/` (private). Source had **no `/lib/firmware/brcm`** at initial physical W1 test; firmware request failed ENOENT -2 and earlier HT clock timed out.
- With **NetworkManager and wpa_supplicant inactive**, Surface `MZ604-W1-INSTALL-PRIVATE-FIRMWARE-20261031.py` verified SHA and nonexistence of paths, then installed root-owned **0644** `/lib/firmware/brcm/brcmfmac4329-sdio.bin` and root-owned **0600** `/lib/firmware/brcm/brcmfmac4329-sdio.txt`. Both installation SHA and ownership/modes PASS. Private receipt: `inspection/MZ604-W1-FW-INSTALL-20261031T043242.txt`.

## Controlled driver re-probe — exactly what passed/failed

- Surface `MZ604-W1-CONTROLLED-REPROBE-20261031.py` issued `sudo -n modprobe -r brcmfmac` and `sudo -n modprobe brcmfmac`; both command exit=0. The matching `brcmfmac_wcc` vendor companion module auto-loaded; `brcmutil` present. No reboot, kernel flash, scan, RF channel request or network association. Private log `inspection/MZ604-W1-DRIVER-REPROBE-20261031T043321.txt`.
- Actual firmware request/boot **PASS**: `brcmf_c_preinit_dcmds` reported **`Firmware: BCM4329/3 wl0: Apr 11 2012 15:30:28 version 4.218.248.42`**. Missing `.bin` ENOENT and previous `brcmf_sdio_htclk` timeout did **not recur in that specific new probe**; not proof earlier timeout was exclusively due to firmware absence.
- Next `brcmf_c_process_clm_blob: no clm_blob available (err=-2)` and `brcmf_c_process_txcap_blob: no txcap_blob available (err=-2)`, then **`brcmf_sdio_firmware_callback: brcmf_attach failed`**. **No wlan0**. Missing optional blobs are **NOT proven** to cause attach failure. The exact `brcmf_attach` stage/errno is not known; after firmware version output some preinit/station steps remain.
- Userspace discrepancy: installed Debian currently **lacks `iw`**, despite earlier off-device package plan. The `xoom` user's PATH lacks `modprobe`/`modinfo` command, but `sudo -n modprobe` succeeded. Track separately as userspace packaging, not kernel patch.
- Exact current kernel build config `CONFIG_BRCM_TRACING`, `CONFIG_BRCMDBG`, `CONFIG_DYNAMIC_DEBUG` are **not set**. Presence of `/sys/module/brcmfmac/parameters/debug` alone cannot enable compile-time-disabled debug code. No meaningful TRACE was collected.

## Next bounded steps (preserve original minimal upstream intent)

1. Do **not** reboot/reflash working p7/p8, modify bootloader, or enable watchdog crash recovery. Remote reboot selection I1 is independently OPEN; cold boot success does not prove TWRP software reboot.
2. First inspect exact source fail paths `core.c::brcmf_attach` → `brcmf_bus_started` → `common.c::brcmf_c_preinit_dcmds`, event/cfg80211 attachment, and existing host kernel ftrace/tracepoint config. Then prepare an **isolated lab-only trace-enabled matching brcmfmac module** if necessary, with exact source+vermagic, backup and rollback. The lab module is not an upstream patch. No guessing root cause from one `brcmf_attach failed` line.
3. With observed errno/stage, decide minimal correct **single-logical-problem** kernel/DT change if physically required, validate MZ604 2.4 GHz only and standard cfg80211. MZ600 old r7/V31 traces are historical references, not automatic patches. Restore/fix `iw` in userspace before scan gates; no unverified 5 GHz transmission.
4. Append short timestamped project log entry **every substantive turn**; milestone checkpoints, issue comment and full handoff. Incoming agents read ALL chronological logs as-of their dates and original evidence.
