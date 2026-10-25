# v06.2 fails to enumerate USB after BCM4329 use — forensic status and controlled next tests

**Date:** 2026-10-25 (EDT), physical device MZ600, microSD **removed**, no eMMC flashes. **Status: unresolved.** This checkpoint records a reproducible failed candidate rather than claiming a BCM4329 kernel defect.

## Immediately preceding successful state

- Clean upstream Linux 7 v06.1 `MZ600-CLEAN-WIFI-BT-USB-v061-BUILTIN-INITRAMFS-RAM-ONLY-UNTESTED.img`, SHA256 `b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a`, **physically passed** RAM boot, USB PING, dashboard, ~75-sec stability.
- Onboard BCM4329 detected via SDIO; explicit `WIFI_START` successfully loaded `brcmutil`, `brcmfmac` and distinct `brcmfmac_wcc`, initialized OEM firmware, and produced `wlan0`. No scan, association or RF test.
- Subsequent attempted `WIFI_STOP` returned `brcmfmac_rc -11`, `brcmutil_rc -11`, drivers remained loaded. This is an expected symptom of module refs when `brcmfmac_wcc` is still referencing `brcmfmac`. `BT_START` deliberately **not** attempted after unload failure.
- The initial scripted USB PING “failure” during this teardown proved to be a **host PowerShell helper returning a progress line together with the port response**; PRIVATE raw log showed genuine `PONG XOOM-LINUX V20`. The host parsing issue was fixed, and subsequent PING passed. Do not attribute this false-negative to the tablet.
- The authorized two-stage USB `REBOOT` + `CONFIRM REBOOT` returned from Linux to original stock Android; host independently confirmed `ro.product.device=stingray` and `sys.boot_completed=1`. No forced power loss, no proof the BCM4329 was fully power-cycled. Wi-Fi modules had been loaded when Linux rebooted.

## v06.2 build and physical result

- The **only intended v06.2 source change** was a lab-userspace `wifi_stop()` routine: unload `brcmfmac_wcc`, then `brcmfmac`, then `brcmutil`, and abort/report if busy; does not execute at startup. Upstream kernel source/base/config otherwise unchanged.
- Exact tracked lab patch: `patches/lab/0001-v062-broadcom-wcc-unload-order.patch`. Reproducible source/build: `scripts/experiments/build-clean-wifi-bt-v062-wcc-unload-20261025.py`.
- v06.2 private kernel-embedded initramfs built via Linux `gen_init_cpio`, includes a newly compiled static no-NEON `/init`. Offline build, QEMU non-PID1 selftest, SHA, Android boot-header SHA1/DTB structure PASS, image size **6,549,504 bytes**.
- v06.2 image `MZ600-CLEAN-WIFI-BT-USB-v062-WCC-UNLOAD-RAM-ONLY-UNTESTED.img` SHA256 **`bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8`**. At **14:25:45 EDT** user-authorized guarded `fastboot boot` accepted; after 75-second observation **NO COM9 enumeration or PONG at all**. Surface also had no ADB or fastboot target after. No automatic reboot, kernel/RF start command, flash or SD access followed.
- User reports **black/off screen and red camera LED blink on pressing Power**, similar to other failure episodes. This does **not alone prove shutdown vs hang vs panic/early fault**. The tablet is NOT currently remotely reachable. Physical user intervention required for subsequent diagnostic access.

## Offline binary forensics (actually executed, PASS)

Script `scripts/forensics/compare-v061-v062-boot-images-20261025.py` examined the exact saved, SHA-pinned physical-good v06.1 and failed v06.2 images and embedded CPIO blobs:

- **Device tree exactly byte-identical**, DTB SHA256 both `a352337e2a8554322a83ca430cb0632b7a1fb390cd15137a0c5f895169ee7c37`.
- **Android bootload addresses, all other header fields and raw kernel command line byte-identical**, including `rdinit=/init` and lack of `root=SD`.
- **All 26 embedded initramfs files preserved; only the `/init` file bytes differ.** All Wi-Fi and BT .ko module payloads, WCC helper, firmware, board calibration and executable modes/uid/gid are identical. The changed `/init` was compiled -Werror, ARM Cortex-A9, non-NEON and passed a QEMU nonPID1 selftest.
- Recompression from the one changed `/init` makes compressed zImage sizes differ: v06.1 **6,483,136** vs v06.2 **6,485,464** bytes. This is an image-composition delta, **not an independently changed kernel source patch**.
- Both images are Android-format boot images with zero external ramdisk and valid structures, under original 8MiB partition limit. This is an offline integrity PASS, **not proof of RAM boot stability**.
- Lab userspace's `run_init()` mounts devtmpfs/proc/sysfs/tmpfs, framebuffer and polls USB; it does **not call `wifi_start()` or `bt_start()` during startup**. Radio module loading occurs on explicit USB commands only. Nevertheless, the Linux kernel enumerates SDIO and handles regulators before PID1, so a partially retained BCM4329 hardware state remains possible even without loading the Wi-Fi module.

## Competing hypotheses (NONE validated)

1. **Warm-state / shared-combo-chip power-reset sequencing:** after a session with Wi-Fi firmware active and WCC userspace unload failing, Linux rebooted to Android and returned to fastboot. BCM4329 WLAN/BT may not have had a full independent power/reset cycle. Motorola OEM coordinated shared U4 vote, WL reset U2, BT reset U0, BT shutdown I7 and low-power oscillator are not yet fully integrated in mainline board power management. But original Android successfully booted between experiments and no actual rail/reset measurement is available, so **do not assert the chip is the cause**.
2. **v06.2 image-/init-size regression / early Linux fault:** the sole intentional change is the later-called userspace `wifi_stop()`, but it changes the embedded kernel payload and its compressed layout. A packing/memory/bootloader interaction or other nondeterministic early startup issue has not been excluded. QEMU nonPID1 test does not validate PID1 execution under Tegra 2.
3. **Generic warm reboot / PMIC/CPU/USB/gadget state:** previous black-screen cases occurred even on diagnostic images without Debian SD root. Need pstore/kernel display logs, not the red LED as a diagnosis.
4. **External removable microSD controller:** the SD was absent during both v06.1 (PASS) and v06.2 (FAIL); its presence does not explain this paired result. BCM4329 onboard SDIO is a separate host/function.

## Next controlled, minimally invasive experiment

1. **Do not blind-boot again now.** Ask user to describe/photograph screen *before* reset (if anything visible). If dark and red blink only, user should recover using known Power+Volume-Up combination. Keep microSD out.
2. After recovery, prioritize capture of TWRP `/sys/fs/pstore` (and `/proc/last_kmsg` if present) **read-only** and kernel logs before restarting Android. Physical ramoops memory was reserved and pstore registered in earlier Debian, but preservation through TWRP is unproven. Avoid interpreting empty pstore as no kernel crash.
3. A/B in **controlled states**: first the **exact previous physical-good v06.1** SHA image with **no SD** after a complete power-off/hardware restart (not only software warm restart), no Wi-Fi startup, verify PONG and uptime. If v06.1 also fails now, shared state/generic reset is stronger suspect. If v06.1 boots but v06.2 fails with same reboot conditions, investigate embedded image and init compatibility before changing BCM4329 kernel code. Stop after one informative A/B step rather than loops.
4. If a state issue is reproducible, prepare a **separate DTS-only** diagnostic variant disabling **only onboard BCM4329 SDIO mmc2**, not internal eMMC or external SD, in otherwise identical boot config; compare pre-PID1 boot and USB. Record exact diff and private physical results before proposing shared-power reset/pwrseq patches.
5. For upstream work, keep current WLAN MAC ATAG→FDT RFC **candidate**, not signed/submitted, and the v06.2 WCC unload fix under **lab patches only**. Do not mix chip power or reset patch into the reviewed RFC without actual hardware evidence.

**Preserve** private firmware, unique identifiers and host diagnostics off public GitHub. No filesystem repartitions or eMMC writes. Last physical-good candidate remains v06.1.

## Post-checkpoint verification: modular radio config and safe pstore collector

Offline kernel configuration reconfirmed on Desktop WSL: `CONFIG_BRCMFMAC=m`, `CONFIG_BRCMUTIL=m`, `CONFIG_BT_HCIUART=m`, `CONFIG_CFG80211=y`, `CONFIG_USB_G_SERIAL=y`, `CONFIG_MMC_SDHCI_TEGRA=y`. Thus core SDIO discovery and USB gadget can run before freestanding PID1, whereas brcmfmac/hci_uart driver modules only load on explicit requests in this RAM environment. The diagnostic `run_init` does not invoke WIFI_START or BT_START automatically.

Read-only TWRP evidence script on Surface: `C:\\Users\\olsen\\xoom-linux-rom\\captures\\Xoom-MZ600-Capture-Pstore-ReadOnly-After-v062.ps1`. PowerShell parser **PASS**, **NOT EXECUTED** while device is in black/red-LED state. Only executes after exact authorized MZ600 TWRP 3.1.1-0 identity check; copies existing `/sys/fs/pstore` records and `/proc/last_kmsg` if readable to PRIVATE Surface host, no mount, no pstore deletion and no target writes. If no pstore is mounted/available, it reports that fact rather than trying to create/mount/reset it.

**Prioritize user’s photograph/description of the current LCD before resetting, followed by TWRP recovery and read-only pstore capture; keep microSD removed.** Never promote the current WCC shutdown fix to an upstream kernel patch. It is a lab userspace correction with a physically failed v06.2 image; further attribution requires an A/B cold-boot test.
