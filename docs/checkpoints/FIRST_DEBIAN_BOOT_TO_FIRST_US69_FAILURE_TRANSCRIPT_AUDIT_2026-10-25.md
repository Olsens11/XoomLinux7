# Historical transcript audit: first Debian success to first USB-dropout incident

**Date reviewed:** October 25, 2026  
**Source:** User-provided prior-conversation transcript covering the earlier successful Debian USB session, wireless-regdb installation, initial MZ600 US/69 test and first reported black-screen/red-camera-LED event.  
**Cross-check:** Read the original Surface `Start-Xoom-MZ600-US69-TempBoot.ps1` launcher and its desktop `.cmd` wrapper; compare against earlier repository checkpoints and later controlled replay tests.

## Facts demonstrated by the first successful session

- MZ600 had booted Linux 7 with a working Debian 12 interactive `xoom@xoom-mz600` session carried over USB CDC/COM9. The user could execute sudo commands and read interface/iw responses, so this was not merely a bootloader, diagnostic framebuffer or early USB enumeration.
- Debian's `wireless-regdb` package `2026.05.30-1~deb12u1` was verified by an expected SHA256, successfully unpacked and installed, and the upstream signed `regulatory.db` and `.p7s` alternatives resolved. The Debian prompt returned. This is not evidence that RF scanning, connection or transmission worked.
- Linux global regulatory domain was **country 00 (world)** while the Broadcom `phy#0` advertised **country 99 (driver custom)**. Distinguish these rather than conflating them with a country code selected by the user. The test did **not** demonstrate US 69 acceptance or legal on-air operation.
- The authoring of a separate US/69 DTS test image and private OEM calibration file was reported after the healthy session, but only the DTS country map was placed into the temporary candidate; the OEM-calibration file with `ccode=US`/`regrev=69` was explicitly **not installed** at that stage. Do not mistake proposed calibration for deployed firmware settings.

## Exact transition to first observed failure, now cross-checked against original script

The original Surface desktop launcher invoked `downloads/Start-Xoom-MZ600-US69-TempBoot.ps1`. Its gates:
1. Verify image hash/size, open existing COM9 Debian shell; confirm shell prompt and `/sys/class/net/wlan0/operstate=down`.
2. Issue **`sudo reboot`** to Debian, wait for USB disappearance, then independently wait for **stock Android** ADB on the known MZ600, with `ro.product.device=stingray` **and `sys.boot_completed=1`**.
3. Only after Android boot is verified, issue `adb reboot bootloader`, confirm unlocked xoom-cdma, re-check image SHA and `fastboot boot` the US/69 candidate. No flash, partition write or SD root change.
4. Confirm whether COM9 enumerated once; does not require a sustained Debian shell login before printing completion.

The user-shared recovered launcher output says `Target: unlocked Motorola xoom-cdma` and successful fastboot transfer/boot, followed by `Debian USB COM9 enumerated: True`. Because the script **cannot reach this line without its stock Android identity/boot-completed check passing**, this is strong evidence that **Android fully booted after the Debian reboot and before the first failed Linux US/69 test**. This lowers confidence in the idea that a D-Bus warning during Debian shutdown directly skipped or corrupted the reboot transition. The transcript's `Failed to connect to bus: No such file or directory` still deserves proper userspace cleanup, but was **not** a demonstrated fatal reboot failure.

USB enumeration was only transient. The user then physically observed black/off LCD and short red camera LED on power press, and forced recovery via Power+Volume Up to stock Android; battery full. No kernel panic or root cause recorded.

## Evidence that initial regulatory DT change was not the sole cause

Later controlled boot of **the exact SHA-verified former good Debian image** reproduced COM9 ~1-second arrival/removal. Separate v034 RAM diagnostic (no Debian SD root) also lost COM9 in ~0.5s; clean upstream minimal v04 RAM diagnostic with original v04 USB tool stayed enumerated ~13.38 seconds but had no protocol reply; same kernel+DTB with v05 SD breadcrumb /init had a ~1-second COM9, with the host **successfully opening COM9 then first write failing** `A device attached to the system is not functioning`. The latter excludes a simple permanent host COM9-exclusive-open conflict as sufficient explanation, but **does not distinguish** kernel reset, PMIC/CPU idle, USB gadget/PHY, display state or power issues.

Live TWRP readback **factory boot p7 and system p8 exactly match original SHA256 factory backups**. Normal original Android 3.1 HMJ37 boot into the original read-only `/system` was physically confirmed. Linux-from-SD selection existed only as a cmdline in temporary `fastboot boot` image, not as a persistent boot partition redirection. This materially narrows the boot-location hypothesis.

## Hypotheses and tests — evidence-ranked, NOT confirmed diagnosis

1. **Early power state / wake / CPU idle / CPCAP / watchdog and kernel panic:** investigate possible Linux-only hang or power-down after USB enumeration. Look for ramoops panic/oops and later watchdog/reset reason, and compare `cpuidle.off=1` / `no_console_suspend` in future single-variable test if evidence points that way. No proof of suspend or power loss currently.
2. **USB device gadget / ChipIdea / console path:** independently capture exact port open/write error and Linux-owned USB state before host detach. Desktop host records a genuine write failure after successful COM9 open on v05.
3. **Kernel init / memory/EMC / variant-specific DT:** Xoom family RAM SKU and frame-memory/ramoops locations should be compared against OEM, and early UART console extracted where possible. Broken native RAM SKU timing is plausible but unproven.
4. **Broadcom interactions:** WLAN/BT shared power or firmware transition might influence the first US/69 boot; however repeat failures with unmodified proven and minimal RAM images argue against treating radio-country mapping as a sufficient root cause. Do not apply experimental firmware fixes until stable baseline established.

## Immediate next step

After user physically recovers TWRP, inspect the external SD filesystem for **private** v05 alternating `XOOM-USB-BOOT-DIAG-A.log` and `B.log` using verified removable SD identity and **read-only `ro,noload`** mount; existing Surface script `captures/Xoom-Capture-V05-SD-Logs-ReadOnly.ps1` was prepared and syntax-checked but not yet run. Check TWRP `/sys/fs/pstore` and kernel preserved RAM buffer if accessible; don't assume persistence across reboot. If no logs, strengthen earliest-stage UART/boot breadcrumbs before risking another blind boot.

**Upstream quality rule:** Keep clean `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` baseline, add only evidence-supported board-specific fixes in separate patches. Do not modify original eMMC boot/system as a debugging shortcut; retain factory recovery until an independent fallback is proven.
