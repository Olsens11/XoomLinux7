# MZ600 v06.4 — after ABI-114 module install: read-only SDIO, firmware, systemd and service-failure forensics

**Date:** 2026-10-26. **Device:** experimental replacement MZ600 on persistent internal Debian 12.15, Linux 7.0.0-next-20260422+, p8 ext4. **Test mode:** physical COM9 root shell **read-only diagnostics only** following the separately proven [114-module installation PASS](MZ600_V064_114_ABI_MODULES_INTERNAL_P8_ATOMIC_INSTALL_PHYSICAL_PASS_2026-10-26.md). No Wi-Fi/BT module activation, no RF scan, no service restart, no reboot, no p7/GPT modifications.

## Independent postinstall driver and root verification

Actual COM9 command readback:
- `uname -r`: `7.0.0-next-20260422+`
- `findmnt -n -o SOURCE,FSTYPE /`: `/dev/mmcblk0p8 ext4`
- `find /lib/modules/7.0.0-next-20260422+ -type f -name '*.ko' | wc -l`: **114**
- Matching `modules.dep`: exists and nonempty; legacy `/lib/modules/7.0.0-next-20260422` tree: preserved.
- `ls /sys/class/net`: `ip6tnl0 lo sit0`; no `wlan0`. `cat /proc/modules | grep brcm`: no matches, expected after dry-run only.

## Physical passive SDIO, firmware, factory MAC checks

- `/sys/bus/sdio/devices` enumerates `mmc2:0001:1`, `mmc2:0001:2`, `mmc2:0001:3` on the onboard combo chip.
- On internal p8: `/lib/firmware/brcm/brcmfmac4329-sdio.bin` is present (253,748 bytes), and `brcmfmac4329-sdio.txt` is present (1,550 bytes). Presence is **not** proof of actual firmware load.
- Per-device DT factory MAC at `/sys/firmware/devicetree/base/mmc@c8000200/wifi@1/local-mac-address` exists with exactly **six bytes**, without revealing identity.
- `/etc/systemd/system/mz600-wlan.service` exists and defines a factory-MAC-validated one-shot service: `ConditionPathExists` for the per-device DT property, `ExecStart=/usr/local/libexec/xoom-check-factory-wlan-mac`, `RemainAfterExit=yes`, `WantedBy=multi-user.target`.
- Regulatory `regulatory.db` and `regulatory.db.p7s` are symlinked via alternatives. **No new country mapping, RF scan, DHCP or connection** was applied or validated. Earlier signed/regulatory checkpoint limits remain in force.

## systemd and D-Bus actual state

- `ps -p 1`: **PID 1 systemd**, `/sbin/init` resolves to `/usr/lib/systemd/systemd`.
- `/run/systemd/system` exists. Private socket `/run/systemd/private` and `/run/systemd/notify` exist.
- **`/run/dbus/system_bus_socket` and `/run/dbus` are ABSENT**.
- `systemctl is-system-running` returned **`degraded`**, not “healthy”.
- `systemctl --failed` lists **`mz600-wlan.service`** and **`wpa_supplicant.service`**, both failed. WLAN unit is enabled but failed; no successful auto-start on current boot.
- Read-only `systemctl show`: WLAN **`Result=exit-code, ExecMainStatus=1`**; WPA **`Result=exit-code, ExecMainStatus=255`**.
- Live boot journal unambiguously explains **WLAN unit's failure before module install:** factory MAC validation actually succeeded, then `modprobe: FATAL: Module brcmfmac-wcc not found in directory /lib/modules/7.0.0-next-20260422+`. This is a **previous startup event**, not a failed postinstall retry; the matching module is now installed/dry-run resolved.
- Live boot journal unambiguously explains **WPA unit's failure:** `dbus: Could not acquire the system bus ... Failed to connect to socket /run/dbus/system_bus_socket: No such file or directory`, followed by `Failed to initialize wpa_supplicant`. Presence of PID1 and its private sockets therefore does not imply system D-Bus is working.
- `dpkg -s dbus` / `dpkg -s dbus-daemon` status-line probes did not display an installed package status in this session. Earlier explicit `dpkg-query` returned “no packages found matching dbus-daemon,” but one combined query on Surface was affected by PowerShell string expansion. Independently inspect available offline .deb packages and package database before choosing a package; no package install attempted.

## Next safe steps

1. Treat module version mismatch as **fixed**, not a reason to rebuild/reflash. Preserve p7 and BigPart p8/GPT.
2. Plan **bounded manual Wi-Fi load/unload** separately, after checking regulatory and factory-MAC guard. Known clean v06.2 diagnostic initramfs brought up `wlan0` and correctly unloaded WCC `->` brcmfmac `->` brcmutil, but that is a different userspace from installed Debian. Do not interpret service startup history as a new module-load result.
3. Given that the owner is away and device has known red-LED/PMIC/USB power-state sensitivity, **do not automatically restart `mz600-wlan.service` or force a radio test unattended** without an explicit recovery/watchdog plan. No RF scan or association prior to trusted MZ600 US regulatory mapping and firmware acceptance.
4. For D-Bus, independently inspect Debian package/runtime dependencies and compare rootfs available binaries with the earlier Debian microSD; source official packages through signed Debian indexes if an install is required. `systemctl --failed` may remain failed until services are explicitly restarted or reset; module installation does not retroactively reset a failed service.
5. Checkpoint each subsequent *physical* service change and userland validation; no repetition of proven installation steps.

**Physical findings:** kernel module installation remains PASS; SDIO device and firmware files present; factory DT MAC exactly six bytes; systemd PID1 active but degraded; two failed services have distinct grounded causes; live WLAN/RF and system D-Bus not yet qualified.

## Final independent read-only p7 and ext4 UUID integrity proof

Following all module installation and passive diagnostics, a separate root COM9 on-Xoom **read-only raw partition checksum** returned:

```text
head -c 6645760 /dev/mmcblk0p7 | sha256sum
fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8  -
sha256sum /dev/mmcblk0p7
901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c  /dev/mmcblk0p7
blkid -s UUID -o value /dev/mmcblk0p8
c2fb0167-7143-4186-b284-c86d6c09ea64
grep -E ^UUID= /etc/fstab
UUID=c2fb0167-7143-4186-b284-c86d6c09ea64 / ext4 errors=remount-ro 0 1
```

Both the 6,645,760-byte Stage-D image prefix and **full physical p7 8MiB SHA256 exactly match the pre-module-install permanent boot verification checkpoint**. The internal p8 ext4 UUID and fstab root selector are unchanged and mutually consistent. This is direct post-install hardware integrity evidence, not merely a lack of write commands. No reboot, filesystem repair, GPT edit or p7 write.
