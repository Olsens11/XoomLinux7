# Clean upstream v04 USB-only RAM boot physical trial — 2026-10-25

**Test status:** `fastboot boot` accepted; USB CDC appeared then disappeared; no verified v04 PING. Not a kernel, USB protocol, or OS success. No flash, no internal/external partition writes or automatic recovery/retry.

## Exact artifact / source

- Source reference `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, isolated worktree; minimal Stingray board identity and USB0 UDC/peripheral DTS adaptation, stock kernel config with relevant USB options and unrelated `CONFIG_IIO_ST_HUB_DRIVERS=n` build-only omission, legacy v04 read-only USB /init in external CPIO. No experimental BCM4329 MAC/SDIO/regulatory/BT patch.
- File `MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img`, **7,870,464 bytes, SHA256 `da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b`**, size, boot-header SHA1 and CPIO verified independently on Surface; now **PHYSICALLY TRIED but functionality NOT verified**.

## Recovery-source identity and safety

At ~11:55 local, user stated tablet was at TWRP. Surface ADB device matched prior private replacement MZ600 unique USB serial. TWRP reports `ro.twrp.version=3.1.1-0`, `ro.hardware=stingray`, though TWRP's generic `ro.product.device=wingray`. Kernel cmdline contains `androidboot.modelno=MZ600`; current removable SD `mmcblk0` has SD type 61067264 sectors, internal eMMC `mmcblk1` has MMC type 62521344 sectors. This matches prior verified hardware layout. Recovery's generic Wingray label is not valid evidence to reject MZ600 identity. Guards were expanded accordingly; PowerShell one-shot syntax passed.

Used recovery `adb reboot bootloader`, validated authorized device in fastboot (`product=xoom-cdma`, `unlocked=yes`) and verified image hash immediately before invoking **only `fastboot boot`**. Fastboot sent 7686 KiB in 1.160s, responded `Booting OKAY` in 1.379s; no flash action.

## USB timeline and limits

- `COM9_FIRST_ARRIVAL=2026-10-25T11:56:54.2165392-04:00`.
- `COM9_FIRST_REMOVAL=2026-10-25T11:57:07.5982511-04:00`.
- Approximately **13.38 seconds present**, vs ~0.5 seconds observed during the previous v034 read-only diagnostic trial and ~1 second during Debian/US69 boot retries. This alone does **not** prove that the new kernel is more stable, or that previous errors were caused by SD root.
- During COM9 presence the guard script attempted to open a .NET SerialPort once per ~1.1s and printed only `SERIAL_RETRY_HHmmss`, with no detailed exception preserved. **No PONG XOOM-LINUX V04** response was received. Possible causes of open failures include a competing serial-port owner, transient PnP state, or protocol/driver conditions. No conclusion without capturing actual exception and port owner.
- Test ended `COM9_PRESENT_AT_END=False`, `V04_PING=False`, `TEST_COMPLETE_NO_FLASH_NO_AUTOMATIC_REBOOT`. Subsequent Surface `adb devices -l` and `fastboot devices` both empty, COM9 not present; no kernel logs captured. Windows System event query around trial gave no useful PnP messages.
- No subsequent physical screen/LED observation was available when this milestone was recorded. **Do not reset before documenting what tablet shows**; user can photograph state.

## Implications and next controlled experiments

The dropout reproduces across several distinct boot images including a minimal v04 USB tool without Debian SD root, so SD installation location is insufficient to explain the failure. Why USB disappears remains unknown: kernel reset/crash, CPCAP PMIC power state, suspend, USB gadget controller, screen/power-on transitions, hardware power/cable, and other causes remain candidates. The longer COM9 lifetime may reflect kernel config/init timing rather than improved stability.

Before any further boot:
1. Obtain physical screen/LED state after clean trial. If recovery needed, safely use Power+Volume Up to return to TWRP or Android.
2. Improve Surface PnP/serial recorder so exceptions, VID/PID arrival/removal, DTR/RTS, handle ownership and timing are captured while avoiding contention. Current script suppresses exception details. Inspect or stop prior lingering Xoom console clients with user impact review.
3. Arrange pre-userspace early kernel breadcrumbs with persistent pstore/ramoops or reserved-memory last-kmsg, or externally captured UART console; do not interpret absence of journal as proof of no boot.
4. Audit power button/CPCAP ADC IRQ, LVDS/backlight and RAM EMC timing variants from OEM stock while Android is available.
5. Only after stable USB/readable early logs, test BCM4329 boot one difference at a time.

**Factory partition status:** Internal eMMC partition table was never modified; p8 system = 256MiB, full Debian root cannot fit without deliberate new layout. User's long-term direction is internal main OS, not perpetual microSD boot. No storage rewriting performed in this trial.
