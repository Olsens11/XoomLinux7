# Motorola Xoom replacement MZ600 — Linux7 Debian persistent boot: PHYSICAL READBACK SHA PASS

**2026-10-26 about 02:55 EDT.** Experimental replacement **only**. Do not touch the protected original. This checkpoint supersedes the previous persistent-p7 SHA-pending status.

## What was physically proven

After the user's local login to normal **persistent** Debian SD-root and local `sudo -s` entering root (password never disclosed), the Surface opened the Xoom's USB gadget serial console COM9. With the live console reporting `root@xoom-mz600:/home/xoom#`, a conditional, **read-only** command verified `id -u=0`, `/ = /dev/mmcblk1p1`, `/sys/class/block/mmcblk0p7/start=102400`, `size=16384` (8MiB), `/sys/class/block/mmcblk0p8/size=2097152` (1GiB BigPart), and p7 not mounted. The output explicitly included `MZ600_P7_READONLY_GATE_PASS`, then:

```text
MZ600_P7_READONLY_GATE_PASS
b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba  -
05e62cd6964659984e84ac36a316e6ed023e66b456bf9081e6395f13127276cf  /dev/mmcblk0p7
 41 4e 44 52 4f 49 44 21
MZ600_P7_READONLY_END
```

The first SHA is `head -c 6645760 /dev/mmcblk0p7 | sha256sum` (**exactly matches** the original proven Stage-B Linux7 BigPart + Debian SD-root image SHA256 `b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba`). The second SHA is `sha256sum /dev/mmcblk0p7` over the whole 8MiB p7 partition (correctly different from the shorter image). The third line is the `ANDROID!` legacy boot header in hex. Therefore the **persistent boot flash was written correctly and read back accurately on physical internal eMMC**. In preceding checkpoint ordinary `fastboot reboot` (not temporary boot) already reached actual Debian 12 USB console and authenticated SD-root user shell. Together these prove a genuinely persistent Debian boot path independent of Android's /system, **as long as prepared microSD stays inserted and healthy**.

**Private raw capture:** Surface `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V064-PERSISTENT-P7-POSTFLASH-READONLY-20261026.txt`. Host capture file SHA256 `94bb4580e04a64d2c8b8b6e9b37eb7011796e4c5c34f74e5fc400b79ff097629`. That capture includes the exact read-only shell command and both output hashes. A PowerShell presentation Boolean in the first automation printed `READ_ONLY_GATES_PASS=False` because its regex did not recognize the CR/newline variation, but the literal hardware response in the captured source clearly printed `MZ600_P7_READONLY_GATE_PASS`; never confuse the display-parsing bug with a device-gate failure. SHA comparison `STAGE_B_IMAGE_PREFIX_HASH_MATCH=True` and complete read were correct and independent.

**No new writes to p7, p8, GPT, TWRP, cache or userdata occurred during verification.** Only p7 was intentionally flashed previously, as recorded in [persistent SD boot checkpoint](MZ600_V064_PERSISTENT_SD_DEBIAN_BOOT_PHYSICAL_PASS_2026-10-26.md). Original factory Android p7 8MiB backup remains safe on Surface, SHA `4da4c9f1486374bb66f31c96389cd1ee3067a447e8a72aea33b2fc24ac3985e3`, and p6 TWRP 12MiB backup SHA `ebe3f1c16ce9d79962433a60b0e63ec6e9f1d6392813601c264204d58b8bbeec`.

## Current exact state and next gate

- **Replacement MZ600** running normal persistent p7 **Linux7 Debian 12.15** with **SD ext4 root /dev/mmcblk1p1**, authenticated **root** over USB COM9. BigPart p8 system **1GiB** visible and not formatted/installed; cache p9 512MiB, userdata p10 28,929.5MiB. Original Android p7 now deliberately replaced by Stage-B Linux SD-root boot; original full p7 saved privately.
- **p7 flashing + ordinary boot + on-device readback all PHYSICAL PASS**. This is a major milestone; never call p7 unverified again.
- **Still NOT proven:** Linux's `reboot bootloader` path previously returned to Android rather than fastboot; after p7 replaced, do not infer it now enters fastboot. Broken Volume Down button on this replacement heightens recovery risk. Independent physical fastboot/recovery escape should still be validated *before* erasing Android /system.
- Internal BigPart p8 Debian installation not started; standard native Debian installer on SD `/home/xoom/mz600-bigpart-install-debian-from-sd-20261026.sh` current SHA256 `d597e8b6c1cf7b83126d1db3bc82d726e26e8df61a12c87695da7b5d47a38e43`; final read-only `--preflight` **PASS exit 0** after persistent boot. `--install` **NEVER RUN**. Offline private prepared Stage-C p8-root `fastboot boot` candidate SHA256 `15feced18d384ec532b7e3d9fb04463eac14c445909fadb5798920ee661571c8` still **NOT BOOTED**. Do not format p8 until recovery plan and safety gates resolved.
- Wi-Fi `wlan0` still absent, `iw scan` pending; D-Bus/systemctl failed earlier. Separate later development tasks.
