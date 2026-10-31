# MZ604 Wingray — minimal working Wi-Fi kernel change and upstream firmware dependency

**As of 2026-10-31 — physical Debian Linux 7 2.4 GHz Wi-Fi PASS; patch series not yet submitted.**

## Bottom line

The *Wi-Fi kernel source change* needed to take existing upstream Wingray DTS + upstream `brcmfmac` + existing published BCM4329 firmware from dummy to bootloader-provided WLAN identity is **one 42-line addition in one file**, with **zero deletions**:

`arch/arm/boot/compressed/atags_to_fdt.c`

Lab patch (already compiled, deployed in p7, and physically exercised):
`patches/lab/2026-10-31-mz604-motorola-xoom-atag-factory-wlan-mac-to-fdt.patch`

Exact baseline Linux source commit:
`xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.

Desktop WSL live review of isolated experiment worktree verified `git diff --stat` = 1 file, 42 insertions; `git diff --check` PASS; separate clean RFC worktree remains at the exact unchanged source commit. No `brcmfmac` source, `tegra20-motorola-wingray.dts`, or common DT source modifications were required to get MZ604 2.4 GHz scanning/connection in the lab.

The patch recognizes Motorola's vendor `ATAG_STINGRAY_MAC=0x57464d41` from the bootloader, checks the payload length and valid unicast/non-placeholder 6-byte MAC and Xoom compatibility, and inserts it as `local-mac-address` at the existing `/mmc@c8000200/wifi@1` node. Upstream `brcmfmac/of.c` already reads this address via `of_get_mac_address`; no new driver feature needed. Historical Motorola `board-stingray-wifi.c` provides direct evidence of the vendor ATAG's format. The patch is still a **lab patch** requiring maintainers' review of where the translator belongs, ATAG validation and any cross-board effects.

## Firmware is already upstream; SHA-256 exact comparison

Required standard firmware filename:
`brcm/brcmfmac4329-sdio.bin`

Expected on installed root:
`/lib/firmware/brcm/brcmfmac4329-sdio.bin` (or distro-equivalent `/usr/lib/firmware/brcm/...`).

**Verified byte-for-byte identity:** project physical MZ604 **BCM4329 v4.220.48** binary previously measured SHA-256
`d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`.

On 2026-10-31, downloaded current upstream `linux-firmware` *Gitiles base64 file* to a private Desktop WSL temp path from
https://kernel.googlesource.com/pub/scm/linux/kernel/git/firmware/linux-firmware/+/refs/heads/main/brcm/brcmfmac4329-sdio.bin?format=TEXT
and independently base64-decoded to a SHA-256 digest:
`d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`, **exact match**.

Linux-firmware commit 5aa0b27d923ac1d2ee4f1d7becfd21c5968769a1 (2023-02-10) previously restored the BCM4329 file after another update broke NVIDIA Tegra devices by lacking a required firmware API:
https://kernel.googlesource.com/pub/scm/linux/kernel/git/hansg/linux-firmware/+/5aa0b27d923ac1d2ee4f1d7becfd21c5968769a1 .

Debian `firmware-brcm80211` bookworm package already distributes a file with this **standard name**:
https://packages.debian.org/bookworm/all/firmware-brcm80211/filelist .
The package's *specific bytes* have not been separately independently hashed; do **not** assert distro binary version/hash equality without comparing actual installed package. The upstream `linux-firmware` file *was* hashed and matches the tested one.

**Therefore:** no Linux firmware redistribution, vendor firmware source addition, new firmware naming rule, DT firmware property, or `brcmfmac` patch is needed. Document as an existing userspace firmware dependency; on installations make sure the binary's SHA is the verified version. Retain the per-device original MZ604 calibration at `/lib/firmware/brcm/brcmfmac4329-sdio.txt`; do not publish calibration or individual addresses.

## What physical hardware testing actually established

- MZ604 Wingray Linux 7 p7 MAC-ATAG boot candidate (7,104,512-byte image) physically flashed after independently SHA-verified complete 8MiB original p7 recovery copy. Debian USB COM10 and systemd root live.
- MAC is 6-byte valid non-Broadcom-placeholder, and `local-mac-address` from live `wifi@1` equals `wlan0` exactly; original MZ604 calibration's MAC differs, so independent original factory assignment remains an open factual question. No address bytes published.
- Existing upstream modular `brcmfmac` + published 4.220.48 binary + MZ604 calibration yields 2.4 GHz channel list with channels 1–11 usable, 12/13 NO_IR, 14 disabled.
- Three ordinary scans BSS counts **19 / 16 / 20**; subsequent scans 2/3 had immediate `iw` exit code zero. WPA2 association through preinstalled NetworkManager, DHCP lease/default route, IPv4 and public IPv6 ping 3/3 each (0% loss), DNS resolution. NetworkManager enabled for future boots and saved Wi-Fi profile autoconnect yes; *automatic reconnect after reboot not physically tested yet*.
- Regulatory observations: original board `ccode=XY`, `regrev=4`; global Linux US, firmware phy 99, `iw` reported 31 dBm; effective RF compliance not proven. No forced country/revision or 5GHz TX. Maintainer question, **not a speculative kernel fix**.

## Scope boundaries and upstream review questions

1. Existing stock Wingray DTS already contains `wifi@1`, regulator/pwrseq, IRQ, SDIO; existing `brcmfmac/of.c` already handles `local-mac-address`. No new wireless DT or legacy chanspec / scan/event patch is supported by *this* working firmware trial.
2. **Separate diagnostic access dependency:** the physical boot image used a USB-*peripheral* test DTB (for interactive COM10), whereas the untouched upstream Wingray DTS currently declares `usb@c5000000` as `nvidia,tegra20-ehci`, `dr_mode=otg`. This is an independent *boot/test access* customization, **not** included in the 42-line Wi-Fi code diff. It may merit its own separate DT discussion, but do not silently label the entire running boot image identical to stock upstream DTB.
3. The mini-Linux p8 startup environment and Debian p10 root image are userspace deployment artifacts, not Linux Wi-Fi patches.
4. OEM MZ604 firmware v4.218.248.42 was physically able to bootstrap but failed current `brcmfmac` modern `chanspecs` inventory. That historical ABI difficulty is not automatically a required driver patch when a pre-existing upstream firmware version physically passes; keep OEM archival and diagnosis evidence.
5. Maintainers should decide whether MAC ATAG translation belongs in generic ARM decompressor or a Tegra/Xoom-specific hook, and whether further bounds/validity checks are appropriate. One logical issue per patch, no invented supporting patch count.
6. Do not submit under the owner's DCO until reviewed and explicitly approved by the owner.

**Recommended first RFC scope: one experimentally proven vendor-ATAG-to-FDT MAC translation source patch + firmware package/source instructions and physical test evidence.**
