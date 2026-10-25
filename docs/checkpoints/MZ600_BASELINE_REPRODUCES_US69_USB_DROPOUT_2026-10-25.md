# MZ600 repeated USB dropout: known-good control reproduces US69 symptom — 2026-10-25

## User's physical observation of prior US69 candidate

After the previous `US-US-69` candidate boot briefly enumerated COM9 and disappeared, user physically found the Xoom **screen black/off**. Pressing Power elicited a **brief red LED near the camera**, but no usable on-screen Linux console. **Holding Volume Up + Power** recovered it to original Android; the displayed battery was full. Authorized Surface ADB subsequently confirmed original `ro.product.device=stingray`, `sys.boot_completed=1`, Android `verizon/trygon/stingray:3.1/HMJ37`, factory kernel `2.6.36.3-gc2bee64` and **battery 100%**, `AC powered=true`, `USB powered=false`, status charging, voltage 8286 mV, temp 23.3°C. The battery reading makes a flat battery unlikely, but **does not exclude transient voltage drops or regulator faults**.

Android /proc/last_kmsg and /sys/fs/pstore were absent, and only an old tombstone from 2026-10-23 was listed; no persisted Linux panic was recovered. Android partitions and TWRP remained accessible.

## New controlled experiment: boot original physically proven Debian image

User previously authorized the reversible RAM-only test workflow. After verifying the recovered device over exact authorized Surface ADB serial, loaded original **known-good** Debian kernel/DTB/ramdisk, using `fastboot boot` only, **not** the US/69 variant:
- Image `xoom-linux7-SDROOT-nonempty-ramdisk-TEMPBOOT.img`, 6,645,760B, SHA256 `c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c`.
- Surface-run one-shot test script: `C:\Users\olsen\xoom-linux-rom\downloads\Xoom-Compare-Known-Good-Boot-20261025.ps1`.
- `SAFE_KNOWN_GOOD_BOOT_SOURCE_ANDROID_CONFIRMED`; identified Android device `stingray`, boot completed, correct ADB serial. Entered unlocked `xoom-cdma` bootloader, verified image SHA. `fastboot boot` reported **Sending 6490 KiB OKAY ~1.075s; Booting OKAY ~1.381s**; no flash or partition changes.

Host detected `VID_0525:PID_A4A7` serial COM9 at **09:38:40–09:38:41 local, 2026-10-25**, then the device vanished: `DEVPKEY_Device_IsPresent=false`, last arrival 09:38:40, last removal 09:38:41, no stable live serial login or ADB/fastboot thereafter. Initial monitor's serial port open attempts repeatedly failed once PnP device disconnected. This is a **reproduction of the rapid USB disappearance with the exact original image that previously physically booted successfully to Debian 12 login**. Therefore the US/69 DTB-only difference is **unlikely to be the sole cause**; do not assume the country map caused crash. The original image's Debian root/session not proven during this latest attempt.

## Interpretations and next capture

Two distinct boot images (original and US/69 variant) now launch RAM-only successfully but show COM9 transient enumeration followed by disconnect within ~1 second. Together with black screen + LED physical sign and successful forced recovery to Android, candidate causes include kernel crash/poweroff, display/backlight/suspend/wake fault, USB gadget/controller instability, or platform power/reset issues. Battery 100% argues against depletion but not a transient condition. **No such cause is proven without a physical screen log or other console.**

Historical 2011 Motorola Xoom community has documented similar black-screen/unresponsive incidents reversible by Power+Volume Up, so a Xoom-specific power/wake issue is plausible independently of our US69 change (https://www.droid-life.com/2011/05/02/tip-xoom-wont-turn-on-stuck-with-a-black-screen-try-this-trick/); anecdote alone does not establish current cause.

**Safest next step**: photograph tablet screen **now** (following original-image test) before reset, even if black/red LED; report whether there is visible kernel text or fully black LCD. Do not automatically repeat test loops or flash anything. If necessary physically reset to Android and plan capture of kernel framebuffer, console panic and removable SD logs. Consider SD `systemd` persistent journal or fallback debug initramfs that logs mount/root through screen; do not write to internal eMMC. Confirm cable/dock power while testing. Preserve verified original Debian boot image, all original eMMC contents and full 32GB SD installation.

**Status:** 2/2 temporary Linux boots with ephemeral COM9 and no observed steady-state. Android recovered normally, last test is known-good original Debian image; its present physical screen state UNKNOWN until examined. 
