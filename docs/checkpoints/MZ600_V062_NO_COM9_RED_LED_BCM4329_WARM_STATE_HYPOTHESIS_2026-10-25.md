## Resolution of image-validity question — successful physical retest at 17:28 EDT

**Later evidence supersedes any implication that v06.2 is unbootable.** The **exact same** SHA256 `bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8` image physically booted successfully from a verified original-Android baseline via RAM-only `fastboot boot` at **17:28:27 EDT**. COM9 enumerated at 17:28:33, PID1 USB PING/PONG passed at 17:28:35, and COM9 remained stable over the 75-second observation with no disconnects; second independent read-only USB session confirmed BCM4329 onboard SDIO device present but **Wi-Fi and Bluetooth modules NOT LOADED**.

The earlier 14:25 no-COM9 failure is a **single unsuccessful attempt in a different prior state**, not a demonstrated image-specific defect. The new boot result **proves v06.2 is boot-capable** but neither identifies why the first attempt failed nor proves a specific PMIC/BCM4329/USB-VBUS issue. User independently reported recovering normal Power-only startup after **disconnecting both USB and external power** first; separate effects were not isolated. Full immutable pass checkpoint: [MZ600 v06.2 controlled boot PASS](MZ600_V062_CONTROLLED_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md).

**Current acceptance:** v06.2 Linux PID1/USB physical PASS; Wi-Fi WCC shutdown routine physical execution **PENDING** (neither WIFI_START nor WIFI_STOP was sent during successful retest). Do not repeat stale "v06.2 physical boot failed" characterization without separating that original attempt from the subsequently successful retest.

# v06.2 boot attempt with no USB after BCM4329 use — image validity unresolved

**Date:** 2026-10-25 (EDT), physical device MZ600, microSD **removed**, no eMMC flashes. **Status: unresolved.** This checkpoint records **one failed physical boot attempt** following a different working image's BCM4329 initialization. **The v06.2 candidate itself has not been demonstrated defective or inherently unbootable; repeatability and independence from prior chip/system state are untested.**

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

Script `scripts/forensics/compare-v061-v062-boot-images-20261025.py` examined the exact saved, SHA-pinned physically working v06.1 image and the v06.2 image from the unsuccessful attempt and embedded CPIO blobs:

- **Device tree exactly byte-identical**, DTB SHA256 both `a352337e2a8554322a83ca430cb0632b7a1fb390cd15137a0c5f895169ee7c37`.
- **Android bootload addresses, all other header fields and raw kernel command line byte-identical**, including `rdinit=/init` and lack of `root=SD`.
- **All 26 embedded initramfs files preserved; only the `/init` file bytes differ.** All Wi-Fi and BT .ko module payloads, WCC helper, firmware, board calibration and executable modes/uid/gid are identical. The changed `/init` was compiled -Werror, ARM Cortex-A9, non-NEON and passed a QEMU nonPID1 selftest.
- Recompression from the one changed `/init` makes compressed zImage sizes differ: v06.1 **6,483,136** vs v06.2 **6,485,464** bytes. This is an image-composition delta, **not an independently changed kernel source patch**.
- Both images are Android-format boot images with zero external ramdisk and valid structures, under original 8MiB partition limit. This is an offline integrity PASS, **not proof of RAM boot stability**.
- Lab userspace's `run_init()` mounts devtmpfs/proc/sysfs/tmpfs, framebuffer and polls USB; it does **not call `wifi_start()` or `bt_start()` during startup**. Radio module loading occurs on explicit USB commands only. Nevertheless, the Linux kernel enumerates SDIO and handles regulators before PID1, so a partially retained BCM4329 hardware state remains possible even without loading the Wi-Fi module.

## Competing hypotheses (NONE validated)

1. **Warm-state / shared-combo-chip power-reset sequencing:** after a session with Wi-Fi firmware active and WCC userspace unload failing, Linux rebooted to Android and returned to fastboot. BCM4329 WLAN/BT may not have had a full independent power/reset cycle. Motorola OEM coordinated shared U4 vote, WL reset U2, BT reset U0, BT shutdown I7 and low-power oscillator are not yet fully integrated in mainline board power management. But original Android successfully booted between experiments and no actual rail/reset measurement is available, so **do not assert the chip is the cause**.
2. **Possible v06.2 image-/init-size regression / early Linux fault (not established):** the sole intentional change is the later-called userspace `wifi_stop()`, but it changes the embedded kernel payload and its compressed layout. A packing/memory/bootloader interaction or other nondeterministic early startup issue has not been excluded. QEMU nonPID1 test does not validate PID1 execution under Tegra 2.
3. **Generic warm reboot / PMIC/CPU/USB/gadget state:** previous black-screen cases occurred even on diagnostic images without Debian SD root. Need pstore/kernel display logs, not the red LED as a diagnosis.
4. **External removable microSD controller:** the SD was absent during both v06.1 (PASS) and v06.2 (FAIL); its presence does not explain this paired result. BCM4329 onboard SDIO is a separate host/function.

## Next controlled, minimally invasive experiment

1. **Do not blind-boot again now.** Ask user to describe/photograph screen *before* reset (if anything visible). If dark and red blink only, user should recover using known Power+Volume-Up combination. Keep microSD out.
2. After recovery, prioritize capture of TWRP `/sys/fs/pstore` (and `/proc/last_kmsg` if present) **read-only** and kernel logs before restarting Android. Physical ramoops memory was reserved and pstore registered in earlier Debian, but preservation through TWRP is unproven. Avoid interpreting empty pstore as no kernel crash.
3. A/B in **controlled states**: first the **exact previous physical-good v06.1** SHA image with **no SD** after a complete power-off/hardware restart (not only software warm restart), no Wi-Fi startup, verify PONG and uptime. If v06.1 also fails, a common warm-state/reset explanation becomes more plausible. If v06.1 boots but v06.2 does not, **only** infer an image difference after matching starting hardware/power states; one sequential test is insufficient because the first boot changes hardware state. Do not repeatedly boot-loop.
4. If a state issue is reproducible, prepare a **separate DTS-only** diagnostic variant disabling **only onboard BCM4329 SDIO mmc2**, not internal eMMC or external SD, in otherwise identical boot config; compare pre-PID1 boot and USB. Record exact diff and private physical results before proposing shared-power reset/pwrseq patches.
5. For upstream work, keep current WLAN MAC ATAG→FDT RFC **candidate**, not signed/submitted, and the v06.2 WCC unload fix under **lab patches only**. Do not mix chip power or reset patch into the reviewed RFC without actual hardware evidence.

**Preserve** private firmware, unique identifiers and host diagnostics off public GitHub. No filesystem repartitions or eMMC writes. Last physical-good candidate remains v06.1.

## Post-checkpoint verification: modular radio config and safe pstore collector

Offline kernel configuration reconfirmed on Desktop WSL: `CONFIG_BRCMFMAC=m`, `CONFIG_BRCMUTIL=m`, `CONFIG_BT_HCIUART=m`, `CONFIG_CFG80211=y`, `CONFIG_USB_G_SERIAL=y`, `CONFIG_MMC_SDHCI_TEGRA=y`. Thus core SDIO discovery and USB gadget can run before freestanding PID1, whereas brcmfmac/hci_uart driver modules only load on explicit requests in this RAM environment. The diagnostic `run_init` does not invoke WIFI_START or BT_START automatically.

Read-only TWRP evidence script on Surface: `C:\\Users\\olsen\\xoom-linux-rom\\captures\\Xoom-MZ600-Capture-Pstore-ReadOnly-After-v062.ps1`. PowerShell parser **PASS**, **NOT EXECUTED** while device is in black/red-LED state. Only executes after exact authorized MZ600 TWRP 3.1.1-0 identity check; copies existing `/sys/fs/pstore` records and `/proc/last_kmsg` if readable to PRIVATE Surface host, no mount, no pstore deletion and no target writes. If no pstore is mounted/available, it reports that fact rather than trying to create/mount/reset it.

**Prioritize user’s photograph/description of the current LCD before resetting, followed by TWRP recovery and read-only pstore capture; keep microSD removed.** Never promote the current WCC shutdown fix to an upstream kernel patch. It is a lab userspace correction included in an image for which **one physical boot attempt failed**; attribution requires controlled A/B testing with matched starting power states.

## Critical interpretation correction — requested by user

**Classification rule:** Separate three dimensions in all milestones and release labels:

| Dimension | v06.1 | v06.2 |
| --- | --- | --- |
| Artifact integrity / offline build | PASS | PASS |
| Has ever fully booted with working USB/PID1 | YES | **UNKNOWN / NOT DEMONSTRATED** |
| Outcome of last physical attempt | Passed before Wi-Fi initiation | **One attempt had no COM9** |
| Intrinsic image defect | Not indicated | **UNDETERMINED** |
| Starting chip/board power state | Prior no-SD recovery and no confirmed prior Wi-Fi use in new environment | Previous v06.1 session had BCM4329 firmware running and failed WIFI_STOP, then software reboot through Android |
| Relative source difference | Original `wifi_stop()` | Shutdown routine updated, *only* embedded `/init` changed; this code is not called at boot |

**Never call v06.2 "failed release", "bad kernel", or "unbootable" based on this single observation.** Call it **offline-verified / physical attempt 1 unsuccessful / independent boot capability unverified**.

### Refined experimental plan, preserving causal attribution

- **First recover TWRP with SD removed.** Before another OS boot, try the already prepared read-only host-side pstore/last_kmsg collector; a missing log is inconclusive.
- Do a **known-good control** first: same exact v06.1 bytes and USB PING after a genuinely completed device power-off/restart, leaving Wi-Fi and Bluetooth unloaded. Confirm console, elapsed time, USB visibility, red LED, pstore; no flashing. A power-off/reboot is **not yet evidence** the BCM4329 actually lost power or reset, because shared regulator votes and pin states have not been measured.
- **Match starting conditions** for a v06.2 attempt: complete the same power-off/cold-start process before testing it, without intervening `WIFI_START` or BT changes. Compare first-stage kernel/USB screen. Only if both have comparable prior state can differences be attributed to the image more confidently.
- Later test the *state transition itself* using the same known-good image: (a) no BCM4329 initialization → reboot → identical diagnostic boot; versus (b) `WIFI_START` with OEM firmware and failed WCC unload → reboot → identical diagnostic boot. Vary only the preceding chip state. Android in between must be accounted for as a possible partial reset.
- If the failure follows **preceding radio activation** rather than image version, inspect OEM U4 shared rail vote, U2 WLAN reset, U0 BT reset, I7 shutdown and LPO clock using source/traces and a reversible board-only diagnostic patch. Don't invent a permanent kernel fix without hardware confirmation.
- Use independent physical evidence: LCD early kernel text/photo, kernel heartbeat, USB enumeration, kernel pstore, regulator/reset state if exposed. **Bootloader "Booting OKAY" and red LED alone do not prove Linux reached or failed a particular subsystem.**

All work remains WIP and repro-focused; independent v06.2 hardware boot validation is pending.
