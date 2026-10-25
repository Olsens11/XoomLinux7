# MZ600 US/69 temporary boot — physical USB transient then device missing (2026-10-25)

## User report and ground truth

User said “Looks like it failed to connect” following launch of the desktop-side `Xoom - Boot MZ600 US69 Test.cmd`.

Remotely inspected SURFACE-BOOK-2 using Desktop Commander. Source test image unchanged and SHA-256 verified `33dd667d97544c2343b7806fa53b19d5b6c94d3153cdcfd671852b6373bc28ae`, 6,645,760 bytes.

**Actual launcher window text recovered read-only through Windows UI Automation** (redacted all credentials; none present in the reported messages):

```text
Verified MZ600-US test image: SHA-256 OK, no flash commands.
This boot candidate adds only brcm,ccode-map=US-US-69 to a separate DTB.
Confirmed wlan0 is DOWN.
Requesting a clean Debian reboot; Linux root filesystem remains intact.
sudo reboot
[sudo] password for xoom:
Failed to connect to bus: No such file or directory
Debian disconnected for restart. Waiting for the original Android ADB connection...
Android / Stingray confirmed. Re-entering fastboot.
Target: unlocked Motorola xoom-cdma. Performing RAM-only fastboot boot...
Sending 'boot.img' (6490 KB)  OKAY [ 1.104s]
Booting                       OKAY [ 1.376s]
Finished. Total time: 2.493s
Boot command completed. Watch for Debian login on the Xoom.
Debian USB COM9 enumerated: True
Temporary US/69 Device Tree variant is ready for read-only verification.
```

**What this proves:** the launcher reached stock Android through ADB, confirmed exact target `stingray` then unlocked `xoom-cdma` fastboot, and executed a successful **RAM-only** `fastboot boot` of the hash-verified US69 image. The host then detected COM9 momentarily; therefore this was not a simple absent flash or failed fastboot transfer. However **Linux PID1, Debian root, live DT map and WLAN are NOT independently verified for this new boot**. COM9 appearing alone is insufficient. The earlier `Failed to connect to bus` originated from `sudo reboot` on known-good Debian (previously missing system D-Bus) but did not stop the actual reboot to Android. That message should not be confused with the *new kernel's* failure.

## Host USB follow-up: device disappeared almost immediately

Immediately after the user's report, remote host inspection found:
- `[System.IO.Ports.SerialPort]::GetPortNames()` — **no ports**.
- `adb devices -l` — no device.
- `fastboot devices` — no device.
- `Get-PnpDevice` retained previous COM9 Linux USB gadget `USB\VID_0525&PID_A4A7` as **Unknown / not present**.
- `DEVPKEY_Device_LastArrivalDate` **2026-10-25 07:54:54 local**, `DEVPKEY_Device_LastRemovalDate` **2026-10-25 07:54:54 local**: USB enumerated and disappeared within the granularity of one second.
- Host currently has no device-side diagnostic transport. Attempts to obtain USB controller event entries did not yield useful records.

**Plausible causes (NOT established):** Xoom kernel panic or reset later in startup; a USB gadget/controller reset; insufficient power, intermittent cable or dock supply; unrelated board hardware failure. The only new Device Tree property is `brcm,ccode-map = "US-US-69"`, verified by decompilation before boot; it is a hypothesis but not proof of causality.

## Preservation and immediate recovery guidance

**No flashing or formatting occurred.** Internal Android boot/system/recovery and the verified Debian microSD ext4 root remain intact. The Xoom may be halted or looping with no remote interface, so don't send blind commands. Original known-working image is still on the Surface:
`C:\Users\olsen\xoom-linux-rom\downloads\xoom-linux7-SDROOT-nonempty-ramdisk-TEMPBOOT.img`, SHA256 `c84172c23e149bf8f215eb78284efeb46aa0a13090df4c159a7ab5d3c2a8cb8c`.

The user is away from the physical tablet. When it can be inspected, **first photograph its existing screen** before resetting. If a kernel panic is visible, save exact error and timestamps. If a dead screen/bootloader and host still has no USB interface, manual force-power reboot is necessary; use known-good Android boot → verified original RAM-only boot image as fallback. The Xoom has a faulty Volume Down button, so previous hardware recovery relies on **Power + Volume Up**; never request `fastboot flash` or an internal partition format as first response.

The technical next test should capture host PnP arrival/removal and USB console messages during early boot, ideally paired with on-screen photograph, before attributing the issue to the `US-US-69` mapping. Comparing to the known-good boot image on the same unchanged cabling and supply will isolate variant vs physical effects.

## Status

- New US69 variant **TEMPBOOT SEND OKAY, BOOT OKAY**.
- New variant **COM9 ENUMERATED BRIEFLY, THEN DISAPPEARED WITHIN ONE SECOND**.
- New variant **DEBIAN PID1 / WIFi FIRMWARE US69 COUNTRY ACCEPTANCE UNCONFIRMED**.
- Baseline physically proven Debian/COM9 successful in previous test; keep it as recovery image.
- Regulatory signed package installation previously user-confirmed; SD root untouched in this trial.

## Recovery helper staged, not executed

Created a one-click **known-good baseline** recovery launcher on Surface desktop:
- `C:\Users\olsen\OneDrive\Desktop\Xoom - Restore Known Good Debian.cmd`
- `C:\Users\olsen\xoom-linux-rom\downloads\Xoom-Restore-Known-Good-TempBoot.ps1`

Checks exact known-good SHA256 and 6,645,760-byte size, target serial identity, Android Stingray when coming from ADB, and `xoom-cdma` unlocked in fastboot, then uses **`fastboot boot` only**. When no authorized Xoom ADB/fastboot transport is detected, it stops without doing anything. **Offline syntax preflight PASS; no USB transport present, so recovery launcher was NOT run to boot**. Leave tablet unmodified while physically inaccessible.

The user remains away from the device, so physical framebuffer state and actual kernel panic information remain unknown. Avoid attributing USB loss to country-map property until contrasted to baseline under the same power/cable conditions.
