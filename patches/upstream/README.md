# Upstream Linux patch preparation — Motorola Xoom (Stingray MZ600)

**Policy:** Every working Xoom kernel change must be kept in a **separate, reviewable Linux source patch**. Laboratory boot images, userspace diagnostic programs, user-specific MAC addresses, private firmware/calibration blobs and logs **must never be mistaken for Linux kernel patches**. Nothing in this directory is automatically sent to maintainers.

## Current RFC queue (not submitted)

| Order | Patch | Source area | Status |
| --- | --- | --- | --- |
| 0001 | [WLAN MAC vendor-ATAG to device-tree bridge](rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch) | `arch/arm/boot/compressed/atags_to_fdt.c` | **Local source compile and hardware probe PASS; RFC review pending; no DCO signoff** |

The formatted RFC patch is the **exact intended logic** of the WIP source patch [`patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch`](../os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch), with *indentation normalized for upstream review*. The physically booted source used the WIP version. Don't claim the separately formatted RFC file was itself flashed, booted or validated byte-for-byte as a separately compiled artifact. Its `git apply --check` against clean pinned upstream passed on Oct 25, 2026. `checkpatch.pl`: **zero whitespace/style warnings; one expected missing `Signed-off-by` error**, since the contributor's DCO acknowledgement must never be invented.

### Physical validation stages — 2026-10-25

- Pinned original `xoom-linux/linux` SHA `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` and clean Wi-Fi/Bluetooth module rebuild from physically proven Debian config. No speculative radio power/clocks/regulatory patch mixed in.
- First new v06 USB RAM boot failed at `rdinit=/init`, photographed Linux kernel panic. This was a **boot-image/initramfs integration issue**, not a driver source bug.
- v06.1 uses Linux's `usr/gen_init_cpio` to embed the original Wi-Fi/BT userspace/archive into the **kernel-built initramfs**, with zero external ramdisk. Boot SHA256 `b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a`. **Actual physical RAM boot, framebuffer/USB PID1 PING/PONG, BT_STATUS and 75-second stable COM9 PASS**, no flash.
- After USB status preflight, chip ID **BCM4329 detected** at onboard SDIO `mmc2`, driver unloaded. Exactly one opt-in `WIFI_START` sent over USB with microSD physically removed; `brcmutil rc 0`, `brcmfmac rc 0`; upstream `brcmfmac_wcc` dependency loaded automatically; `wlan0 PRESENT`; firmware boot log reports `BCM4329/3 wl0` and `version 4.220.48`. `/sys/class/net/wlan0/addr_assign_type` reported `0` (permanent), though independent byte-for-byte comparison to the protected factory MAC must be maintained privately before formal identity claims. COM9 remained usable. **No RF scan, association, DHCP, country-code override, or transmission test.**
- Bluetooth dashboard and status control included, but `hci_uart` and HCI0 were **NOT initialized**; no Bluetooth functionality yet proven. The original Motorola-specific HCD firmware is missing from v06.1 CPIO; do not claim full Bluetooth hardware readiness.

## Experimental boot-version status — avoid conflating attempts and images

| Image | Offline verified | Physically proved USB/PID1 | Latest observation | Image attribution |
| --- | --- | --- | --- | --- |
| v06.1 embedded | YES | **YES**, Wi-Fi firmware + `wlan0` | Wi-Fi shutdown failed because WCC dependency remained loaded; reboot through Android worked | Working under tested state |
| v06.2 WCC teardown | YES | **UNKNOWN** — no successful boot yet | **One unsuccessful RAM boot attempt:** no COM9, black/red-LED after v06.1 had previously initialized BCM4329 | **Undetermined**; possible retained chipset/PMIC state, early boot issue, or image-specific change |

**Do not call v06.2 inherently bad or a failed patch.** Its kernel/DTS/boot cmdline, firmware, and .ko modules are identical to v06.1; only built-in diagnostic `/init` differs. That routine's `wifi_stop()` is invoked by USB command, not at startup. The fact that one attempt failed is not proof of a source regression. The precise failure chronology and future matched-state tests are in [v06.2 investigation checkpoint](../../docs/checkpoints/MZ600_V062_NO_COM9_RED_LED_BCM4329_WARM_STATE_HYPOTHESIS_2026-10-25.md). Preserve artifact hashes and track physical attempt outcomes independently from offline build and release quality.

The v06.2 fix remains a **laboratory userspace patch**, not an upstream Linux C patch, at `patches/lab/0001-v062-broadcom-wcc-unload-order.patch`. Do not submit it as a kernel change. Potential Broadcom shared-rail/reset work remains **hypothesis only** until evidence supports a separate focused kernel patch.

## Not yet candidate Linux patches

1. **Stingray board DTS split from Wingray**: working USB0 UDC/peripheral and hardware identity are created by the isolated build generator. For proper upstream submission make a stand-alone `arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dts` (+ DTS Makefile) series. Validate binding compatibility, UART/BT clock, board PMIC, pinmux and mode-specific nodes rather than forwarding a lab file named `*-clean-usb.dts`. The generic `motorola,stingray` compatible is already used by lab builds; inspect potential binding changes separately.
2. **SDIO speed & shared combo power**: the 25 MHz cap, Bluetooth LPO wiring and chip power/reset coordination are still experimental. Keep them in WIP engineering notes until one-variable, physical A/B evidence justifies separate hardware patches.
3. **Bluetooth firmware**: OEM HCD `BCM4329B1.hcd`, userspace tools and distribution/licensing belong in firmware packaging documentation, **not in source patch commits**. Review `hci_bcm` binding and physical transport after actual HCI0 tests.
4. **Regulatory US/69 settings**: do **not** include experimental country map/calibration data in upstream patches until verification with signed regulatory data and region/radio restrictions.
5. **Built-in initramfs and dashboard**: `v06.1` initramfs packaging corrects **our own boot-image delivery**, not a defect in upstream kernel C code. USB diagnostic buttons/firmware upload/modprobe helper are laboratory userspace and should be maintained separately, never sent as a Linux kernel patch.
6. **MicroSD sensitivity**: previous same v04 kernel was stable with card absent but had transient COM9 with card present; root cause unproven. No kernel patch should be submitted from correlation alone.

## Submission workflow and gates

1. Create a small `git commit` per logical kernel change on a **fresh checkout of the exact upstream base commit**. Preserve original failing and successful boot artifacts separately and record their SHA256.
2. `git format-patch --base=<upstream base> -o <review-dir> <base>..HEAD`; check actual `git diff --check`, `git apply --check` against pinned unmodified source and `scripts/checkpatch.pl`. Maintain patch series order and real commit message (what/why/rationale, tested hardware).
3. Run the proper cross-compile tests with `ARCH=arm` and Cortex-A9/no-NEON restrictions; validate DTS with dtc, compile modules **from same kernel tree/config**, and run boot/USB/driver tests. Mark each as offline compile, physical boot, probe, RF functionality, or not tested—not all as “passed.”
4. Obtain actual contributor author name/email and a conscious Developer Certificate of Origin agreement. Only then attach that person's real `Signed-off-by`; do not fabricate name/email, `Tested-by`, reviewer consent or endorsement.
5. Run `scripts/get_maintainer.pl` at the pinned tree and inspect current MAINTAINERS before selecting To/Cc; the initial bridge touches ARM decompressor and the locally inspected output points at ARM maintainers and `linux-arm-kernel`. Recheck ownership against the actual base tree selected for submission.
6. Prepare cover-letter RFC first if reviewer guidance on vendor ATAG translation or DT board binding is necessary. **Never submit, push to upstream or send email without explicit request.**

## Canonical evidence and private captures

- [v06.1 physical panic correction checkpoint](../../docs/checkpoints/MZ600_V06_KERNEL_PANIC_MISSING_INIT_AND_V061_EMBEDDED_CORRECTION_2026-10-25.md)
- [v06 offline native Wi-Fi/BT build](../../docs/checkpoints/CLEAN_UPSTREAM_MZ600_WIFI_BLUETOOTH_USB_V06_OFFLINE_PASS_2026-10-25.md)
- Surface private logs: `captures/MZ600-V061-embedded-firstboot-PRIVATE.log`, `captures/MZ600-V061-WIFI-FIRST-START-PRIVATE.txt`, `captures/MZ600-V061-WLAN0-IDENTITY-PRIVATE.txt`. Do not upload private logs verbatim.
- Use the human-edited public progress record [WLAN and submission milestone](../../docs/checkpoints/MZ600_V061_USB_WLAN_BCM4329_PATCH_REVIEW_2026-10-25.md) once the tests are reconciled.

**Upstream-ready means checkpatch, clean upstream apply, current intended commit signed by its real author, and honest test status; v1 is an RFC candidate, not yet approved for sending.**
