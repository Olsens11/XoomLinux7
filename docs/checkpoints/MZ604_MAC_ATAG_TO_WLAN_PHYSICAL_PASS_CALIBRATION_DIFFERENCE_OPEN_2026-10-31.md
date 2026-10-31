# MZ604 MAC identity: vendor ATAG → FDT → brcmfmac PHYSICAL PASS; calibration mismatch requires interpretation

**2026-10-31 ~07:00–07:20 EDT**. This is a limited physical result, not an RF scan, WPA/connection or independent factory-assignment proof.

## Confirmed physical evidence
- Owner successfully cold/manual hardware-booted the experimental MAC ATAG p7 image after TWRP software reboot fell to red camera LED. Surface Linux USB COM10 present; Linux release `7.0.0-next-20260422+`, fresh dmesg identifies kernel `#3` built Oct 31 05:45 EDT, consistent with the experimental compiled zImage. Current live p8 `/mnt/xoom-system/sbin/xoom-start.sh` still mounts p10 Debian loop and executes `switch_root`; no one-shot p8 selector installed.
- Live read-only serial/Surface private comparison returned: `/proc/device-tree/mmc@c8000200/wifi@1/local-mac-address` **PRESENT, exactly six bytes**; `wlan0` **PRESENT**; **DT MAC == wlan0 MAC**; DT MAC valid unicast and neither zero nor known Broadcom 00:90:4c:12:34:56 placeholder. Do not expose actual MAC bytes in public records.
- The MAC in the original MZ604-backed-up OEM `bcm4329.cal` file was found and parsed, but **DIFFERENT** from live DT and wlan0 address. This is a *real comparison result*, not proof that either source is incorrect. A later more detailed sensitive comparison request was blocked by the remote-control security gate; no workaround or second device command issued.
- Firmware state at preceding baseline: exact Generic BCM4329 4.220.48 persisted in Debian, MZ604 original calibration retained, `wlan0` present, 2.4 GHz advertised; **active scans, association, DHCP, internet have not been tested** on this MZ604.

## Original Motorola kernel implementation: decisive provenance
- Historical Motorola `arch/arm/mach-tegra/board-stingray-wifi.c` defines `ATAG_STINGRAY_MAC 0x57464d41`, initializes a Broadcom default placeholder, obtains actual bootloader tag payload using `unsigned char *dptr = (unsigned char *)(&tag->u)`, uses `(tag->hdr.size - 2) * sizeof(__u32)` capped at `IFHWADDRLEN`, copies payload into `stingray_mac_addr`, and returns it from `stingray_wifi_get_mac_addr`. It can generate a fallback if final two bytes remain zero; **our lab patch does not intentionally reproduce this legacy random fallback**. Original source: https://android.googlesource.com/kernel/tegra/+/eb4e253d7d76f6093ef50597e909157c21803842%5E2..eb4e253d7d76f6093ef50597e909157c21803842/ , section `board-stingray-wifi.c`.
- Our lab-only 60-line patch `patches/lab/2026-10-31-mz604-motorola-xoom-atag-factory-wlan-mac-to-fdt.patch` uses the **same tag ID, same initial six payload bytes, no static fabricated fallback**, and puts the result in the already-present Xoom `wifi@1` DT node. The observed real boot result corroborates Motorola's original tag layout. This is a **dynamic bootloader-origin identity path PHYSICAL PASS**.
- The original OEM driver using the vendor ATAG instead of simply trusting a `macaddr` field in OEM NVRAM makes the observed NVRAM-vs-ATAG discrepancy **not automatically a defect**. A separate authoritative original factory-assignment confirmation is still OPEN; do not claim unique factory proof solely from `DT == wlan0`.
- Earlier MZ600 temporary Debian result similarly proved DT==wlan0 but explicitly did not independently certify factory assigned identity. Source `docs/checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md` on historical branch.

## Early reboot evidence, separate issue
- Owner's photographed TWRP→System run shows kernel startup/driver/firmware certificate messages then sudden off/red LED, no confirmed visible MZ604_INIT or stage2 marker. The exact last executed instruction is UNKNOWN.
- Subsequent manual hardware reboot succeeds and fresh dmesg recorded `MZ604_INIT` at +1.10s, `MZ604_STAGE2` and `switch_root` to p10 Debian by +1.57s, so manually rebooting does not skip p8 initramfs/stage or handoff.
- Ramoops/pstore was registered on current boot; prior read-only `find /sys/fs/pstore ...` produced no file names. Persistent panic evidence not yet obtained. Don't infer a crash code from the last visible display line.
- This boot-path/reset behavior is a different open issue from the MAC driver functionality, and should not block physically valid 2.4 GHz tests when safety gates pass.

## Next gates
1. Maintain private MAC source. If needed, independently establish OEM Wi-Fi source of truth (stock Android provenance), compare vendor ATAG assignment across cold/warm boots and units, without publishing unique IDs. Do not replace it with hardcoded per-unit MAC or a generated address.
2. W1/W2/W3: audit current user-space regulatory/firmware inventory (2.4 GHz 1–11, 12–13 NO_IR, 14 disabled was baseline). Avoid country overrides or unverified 5 GHz TX.
3. W4: three fresh ordinary 2.4 GHz scans, record channel/frequency/scan completion; do not infer network from SSID naming. W5: supervised authorized WPA2/DHCP/connectivity/reconnect using private credentials. W6: minimal upstream one-logical-issue patches, review DCO.
4. Do not alter Motorola bootloader/BCT/EBB/GPT, p6 TWRP or working p8/p10. Complete original 8 MiB p7 backup and receipt remain on Surface; candidate p7 flash/readback SHA recorded in preceding checkpoint.

**Qualification:** PASS dynamic bootloader ATAG→DT→interface; OPEN independent factory assignment; OPEN active Wi-Fi connectivity; OPEN warm-reboot-to-Linux issue.
