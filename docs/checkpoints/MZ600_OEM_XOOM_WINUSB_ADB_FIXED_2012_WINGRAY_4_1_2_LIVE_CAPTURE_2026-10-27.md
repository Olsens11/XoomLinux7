# Stock spare Xoom on Surface: WinUSB ADB fix verified; 2012 wingray Android reference, live Wi-Fi logcat started

**2026-10-27, host diagnosis and user-approved driver correction completed.** Live OEM scan capture has been started **but user has not yet reported that their manual Wi-Fi Settings refresh/scroll is done**. Do not pretend to have analyzed the completed OEM scan.

## Problem / driver evidence

- Surface detected stock Xoom USB composite (Motorola VID22B8 PID70A9) with MTP MI_00 and ADB MI_01, but current Platform Tools ADB 1.0.41 (37.0.1) returned empty `adb devices -l` despite debugging enabled.
- The MI_01 initially bound signed old Motorola `oem104.inf` `motoandroid.sys`, service `motandroidusb`, Motorola driver 1.3.0.0 Mar2013; PnP status OK but no ADB transport. Windows ranked this ahead of signed Microsoft `winusb.inf` compatible classFF/sub42/prot01. `ADB_LIBUSB=1` separate server returned empty with old driver.
- Exact non-elevated SetupAPI DRY RUN enumerated two MI_01 compatible drivers: `Microsoft ADB Device` and `Motorola Mot Composite ADB Interface`. Dry-run passed, no change, then user authorized replacing ADB binding only.

## Actual successful host-only driver operation

- Surface session was non-admin. Ran a targeted PowerShell SetupAPI driver selector **elevated via normal Windows UAC**. It requires exactly one Xoom Motorola MI_01 interface; verifies currently installed old `oem104.inf / motandroidusb`, exports that original Motorola package before change, selects **only** Microsoft `ADB Device` from SetupDi compatible list (backed by `winusb.inf`) and calls DIF_INSTALLDEVICE. Does not select MTP MI_00 or parent composite.
- Post-change Surface remote check reported `ADB_INTERFACE_INF=winusb.inf`, `ADB_INTERFACE_SERVICE=WINUSB`, `ADB_INTERFACE_STATUS=OK`.
- **Proof:** subsequent native `adb devices -l` listed **one Xoom with status `device`**, confirming WinUSB actually works with modern Windows ADB. Do not publish actual device USB serial.
- Original Motorola driver **was exported for rollback** to private host folder `C:\Users\olsen\xoom-linux-rom\captures\OEM-XOOM-ADB-DRIVER-ROLLBACK-20261027`, along with before and after driver facts. Driver package still exists in Windows driver store. Recovery: Device Manager > Mot Composite ADB Interface (now Microsoft ADB Device) > Update Driver > Let me pick > Motorola 2013 Mot Composite ADB Interface / original oem104.inf. No uninstall of other Motorola drivers, no bootloader/firmware/tablet writes, no USB debugging toggles.
- The exact host helper at `C:\Users\olsen\xoom-linux-rom\captures\xoom-oem-adb-targeted-driver-switch-20261027.ps1` was parsed successfully and dry-run tested. It must not be rerun now that WinUSB binding is active.

## Reference device identification matters

Authorized ADB read-only commands reported **Xoom `ro.product.device=wingray`**, Android **4.1.2 / SDK16**, build `JZO54K`, stock-era Motorola/Google image fingerprint `motorola/tervigon/wingray:4.1.2/JZO54K/485486:user/release-keys`, kernel from `/proc/version`: **2.6.39.4-g4e32b94** compiled Sep 10 2012. ADB shell on this ROM lacks `uname` command; use `cat /proc/version`. This is an **MZ604 Wi-Fi variant (`wingray`)**, not the experimental **MZ600 CDMA (`stingray`)**, so check chip, firmware and board revision before claiming identical low-level behavior. It is nonetheless useful historical Android framework/scan-reference behavior.
- Android `dumpsys wifi` showed Wi-Fi enabled, `mIsScanMode false`, a latest-results section and per-UID scan counters. This does not itself expose hardware-terminal Event26 or Event69.

## Live read-only capture initiated

- Host Surface PowerShell OEM observer source: [script](../../scripts/host/surface/observe-stock-xoom-oem-wifi-scan-readonly-20261027.ps1). Corrected Surface-local copy to read `cat /proc/version` instead of `uname -r`, because original Android lacks `uname`; syntax parse PASS.
- Started live capture process through Remote Desktop Commander Surface `powershell -File ...` (session PID **9088**, do not assume PID persists across restarts), path `C:\Users\olsen\xoom-linux-rom\captures\OEM-XOOM-WIFI-SCAN-READONLY-20261027\20261027-033524`.
- Positive validation: `private-live-logcat.txt` was actively being populated (156046B at first observation), `private-live-logcat-errors.txt` 0B, `private-wifi-before.txt` 15163B, identity saved. No Android Wi-Fi toggle or scan initiated by tools; waiting for **owner manually opening Settings > Wi-Fi and refreshing/scrolling**.
- The interactive script currently prompts for ENTER after owner completes the UI observations. When user says `done`, end via Remote Desktop Commander `interact_with_process` on PID 9088 with newline, then verify exit + post dump, count/timestamp relevant logcat scan begin/complete, and keep raw SSID/BSSID/MAC in private host folder only. Do not let the event capture persist unnecessarily after owner completes.
- The separate original experimental Linux MZ600 COM9 Bluetooth Python process was **not stopped or interfered with**.

## Investigative goal

Correlate OEM 2012 Android scan-start, results-available, hardware scan-complete or `iscanresults` terminal events (if visible), repeated scans, and UI security fields. Do not equate slow UI/security list updates to continuous single RF scan. Existing MZ600 Linux7 V16 accepted single-ch36 ESCAN V1 with 7 Event69 PARTIAL in first ~414ms, then ~10s silence until watchdog, whereas 2G V15 received actual terminal SUCCESS in 179ms. Stock MZ604 may differ in Wi-Fi firmware/drivers; preserve variant caveat.
