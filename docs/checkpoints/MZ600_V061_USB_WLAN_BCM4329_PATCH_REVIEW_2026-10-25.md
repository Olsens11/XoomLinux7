# Xoom MZ600 clean Linux v06.1: stable USB, BCM4329 WLAN0 and upstream patch review

**Date:** Sunday 2026-10-25 (US EDT). **Test source:** Exact pinned `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, no microSD, isolated clean kernel Wi-Fi/Bluetooth build. **No internal eMMC/Android flashing, formatting or writes.**  
**Separate review branch:** `wip/clean-wifi-bt-usb-20261025` and `patches/upstream/rfc` for Linux kernel changes.

## Prior diagnostic failure, corrected boot image

- v06 external-CPIO 6,547,456B image SHA256 `c8240c65bf43064b82acec516ffc863e819db314e6f5fa0033586241390e00e9` did execute Linux but photographed console showed `check access for rdinit=/init failed: -2` and `Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)`. COM9 enumerated but was nonfunctional because no PID1 was running.
- v06.1 is **built-in initramfs** generated using Linux's own `gen_init_cpio` with all identical 26 userland payload entries, no external boot-header ramdisk. The kernel `usr/initramfs_inc_data` exactly SHA256 matched the generated 643KiB built-in archive. Independent Android boot image hash, legacy header SHA-1, appended DTB and addresses passed on Surface.
- Physically tested `MZ600-CLEAN-WIFI-BT-USB-v061-BUILTIN-INITRAMFS-RAM-ONLY-UNTESTED.img`; exact image **6,547,456B**, SHA256 **`b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a`**, kernel + appended DTB **6,544,240B** SHA256 `928d16683cf44530cc7b624cfe10afdcf9bb33b9d4be855d831f85dbbf7cd664`.
- Surface confirmed expected unlocked `xoom-cdma` MZ600 and image hash. `fastboot boot` accepted **13:55:46.775**, COM9 enumerated **13:55:52.559**; first serial write timeout transient, but **13:55:55.473 USB PING/PONG succeeded**, and **13:55:56.341 BT_STATUS returned 223 characters**. Final at **13:57:01.863** COM9 present / PONG true / no USB removal throughout 75-second observation. No Wi-Fi or Bluetooth activated during boot. Normal diagnostic dashboard source includes Wi-Fi and Bluetooth status rows; visual presentation should not be marked separately photographed without user confirmation.

## Onboard Broadcom BCM4329 native WLAN bring-up (without microSD)

At 14:03 EDT USB preflight verified PING/PONG, `MMC2_STATUS` target valid, bound, **CARD BCM4329 VERIFIED**, modules unloaded. One explicit opt-in `WIFI_START` command over existing v034-derived **RAM-only USB diagnostic tool** was sent; no radio scans, DHCP, WPA, association, or region changes.

- `BRCMUTIL rc 0`
- `BRCMFMAC rc 0 debug 6` (loader source's old display string; the v06.1 packager intentionally removed unsupported `debug=` parameter because `CONFIG_BRCMDBG` disabled; do not infer debug parameter actually accepted).
- `WIFI PROBE STARTED (NO ASSOCIATION)`
- `WIFI_STATUS`: kernel `brcmfmac_wcc`, `brcmfmac`, `brcmutil` **all loaded**, automatic WCC vendor dependency satisfied with a narrow RAM-local ARM `/sbin/modprobe` helper; **`WLAN0 PRESENT`**.
- Kernel LOGS: `brcmfmac: brcmf_fw_alloc_request: using brcm/brcmfmac4329-sdio for chip BCM4329/3`; `brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: Sep 2 2011 14:48:19 version 4.220.48`. Missing optional `clm_blob` and `txcap_blob` generated warnings; **not** evidence of failed probe. RF capabilities and legal channels remain unverified.
- After Wi-Fi start, USB COM9 remains connected and diagnostic `WIFI` output reports `WLAN0 PRESENT` with `addr_assign_type=0` (permanent). Actual MAC address and full live log saved **privately**; do not publish factory identifier or overstate per-device uniqueness without separately checking against backed-up OEM MAC. No Wi-Fi interface configuration or RF transmission test was performed.
- Bluetooth is **supported as standard Linux modules and diagnostic status** but remains **NOT STARTED / HCI0 ABSENT**. The normal BCM4329B1 HCD firmware is not yet integrated into this RAM package; physical Bluetooth bring-up remains a separate test with shared-chip power sequencing concerns.

## Actual Linux upstream patch preparation, not merely build notes

- The **only current functional Linux C source difference** from pinned upstream is `arch/arm/boot/compressed/atags_to_fdt.c`: Motorola's per-device WLAN MAC ATAG `0x57464d41` copied into `local-mac-address` on `/mmc@c8000200/wifi@1`; invalid/multicast/placeholders rejected. Physically tested v06.1 source used `patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch`.
- Review candidate with indentation normalized **and otherwise equivalent logic** is saved at `patches/upstream/rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch`. This separately formatted patch **applies to clean pinned upstream** (`git apply --check` exit 0 on Oct25). Kernel `scripts/checkpatch.pl --no-tree` reports **0 style warnings**, **1 missing Signed-off-by error**; no DCO identity fabricated. The independent normalized diff has not separately been physically booted and must not be labeled as tested exact bytes.
- Upstream patch tracker at `patches/upstream/README.md`. New source board DTS created as lab derivative and Android boot packaging remains project-local pending true DT compatible/binding review. Embedded initramfs, USB upload/init, private firmware and the restricted modprobe tool are **not kernel source patches** and should not be submitted as such. No country map, arbitrary fabricated MAC, speculative regulator/LPO, external microSD fault fix or FM implementation included in upstream candidate.
- Submit only with original author DCO signoff and explicit request. Pending: patch cover letter, bindings/API review, formal mailer series, maintainers routing, cross-compile of normalized exact patch, and later BT/SDIO one-variable hardware qualification.

## Private artifacts / rollback

- Image and manifest on Desktop WSL: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts-embedded-v061/`, plus Desktop Windows and Surface downloads. Known-good no-SD clean v04 SHA256 `da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b` remains unchanged.
- Guarded USB boot launcher Surface `captures/Xoom-V061-Embedded-WiFi-BT-USB-Once.ps1`; guarded one-shot WLAN script `captures/Xoom-V061-BCM4329-WIFI-Start-Once.ps1` (syntax verified).
- PRIVATE logs `captures/MZ600-V061-embedded-firstboot-PRIVATE.log`, `captures/MZ600-V061-WIFI-BT-READONLY-PRESTART-PRIVATE.txt`, `captures/MZ600-V061-WIFI-FIRST-START-PRIVATE.txt`, `captures/MZ600-V061-WLAN0-IDENTITY-PRIVATE.txt`.
- Neither Android boot p7, system p8 nor TWRP recovery p6 were modified; earlier factory SHA comparison and normal boot passed. Avoid unnecessary reboots; the v06.1 kernel remains live with WLAN0 and diagnostic USB.

**Acceptance level:** RAM-only clean Linux v06.1 PID1 and USB PASS, Broadcom Wi-Fi driver firmware initialization + WLAN0 presence PASS; Bluetooth HCI and Wi-Fi RF operation pending; upstream candidate patch source apply/style preflight PASS except intentionally unsigned DCO, not yet submitted.
