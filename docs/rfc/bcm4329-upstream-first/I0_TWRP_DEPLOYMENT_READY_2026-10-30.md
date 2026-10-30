# MZ604 I0: READY ON SURFACE — supervised TWRP deployment and first actions (2026-10-30)

> **ACTIVE ENTRYPOINT FOR THE NEXT AGENT WHEN OWNER RETURNS HOME.** The owner will put **the dedicated MZ604 Wingray** in **existing TWRP 3.1.1-0**, with USB connected to **SURFACE-BOOK-2**. After the owner reports TWRP, the agent must take over by conducting the read-only identification/preflight, backing up current device state, and deploying ONLY the approved minimal development-access root. The owner does **not** need to discover passwords or manually copy files. The MZ604 currently remains running Linux COM10; **NO RECOVERY REBOOT, ADB INSTALL, FLASH OR DEVICE WRITE HAS YET BEEN PERFORMED** for this package. Never touch EBB/BCT/p1/GPT/bootloader or p6 TWRP.

## The exact package already on the Surface

**Directory:** `C:\Users\olsen\xoom-linux-rom\staging\MZ604-READY-V2-20261030`

**Pinned `MANIFEST.json` SHA256:** `331f36e4340ba14f78c9217f8e66cd1175c907dfacddff202c33b3161848ddb6`. The Surface independently verified all ten payload files by their bytes and SHA-256; moreover, streamed decompressed all 3 ext4 image payloads and validated each *raw* image digest and size; matched module tar contains **114 ARM kernel modules**. Source kernel checkout remains exactly pinned upstream `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` and its incremental `make ARCH=arm ... zImage modules dtbs` completed exit 0 with the pinned GNU 14.3.Rel1 toolchain. This is OFFLINE evidence, not a new hardware run.

| File name in staging directory | Purpose, evidence and disposition |
| --- | --- |
| `MZ604-I0-DEBIAN-DEVACCESS-UNTESTED.img.gz` | **PRIMARY I0 INSTALL CANDIDATE.** 155,964,835 bytes, gzip SHA256 `0fcd28f6f2fd509c7c5af51ee1384c4acaad096209619e380762bbe626a13862`; expands to 2,146,435,072-byte ext4 SHA256 `351ae328b62fce048ace29e5855425981e90f38534018c11c7cc03af6a66e0d1`. Based on verified original Debian root, with `ttyGS0` systemd/agetty **autologin xoom**, `xoom` sudo **NOPASSWD**, and fallback local password **1234**. Root remains locked. ext4 five-pass `e2fsck -fn` PASS offline. No network listener/SSH policy opened. |
| `MZ604-P7-KNOWN-COM10-BOOT-DO-NOT-REFLASH.img` | **REFERENCE/rollback only**, 7,104,512 bytes, SHA256 `56741fcc04f83dd7fb7a7e794e9c5ec21a8a21348401bb686a2d4abc4741c6a2`; this is the exact owner-flashed USB-peripheral boot candidate previously proven to expose COM10 and reach Debian login. **Do not flash p7 for I0.** |
| `MZ604-P8-BASE-STAGE2-CORRECTED-UNTESTED.img.gz` | **Standby p8 recovery artifact**, gzip SHA256 `e0f773530ca35b75a535cb521909306bea928f9311bcb4fd703cf2d71077348b`; raw 268,435,456-byte ext4 SHA256 `69268421f1fe9ce0f59fad1b5e5b71bb78e713127e5e30578d385d65061afe64`. Corrected `/newroot/usr/lib/systemd/systemd` check. Offline fsck PASS; **do not overwrite working live p8 in I0**. |
| `MZ604-P8-ROOT-SELECTOR-V2-EXPERIMENTAL-UNTESTED.img.gz` | **Optional I2 later**, gzip SHA256 `0fe697c66b0318fafd5a99f3167452bd2b22ffe2a063af855cbaf51f4ca3c64a`, raw 268,435,456-byte ext4 SHA256 `69ea9cb868470e78f17e375b927570e757b5c71db20c160386aaf34b2c4ff7a8`. Choice defaults to normal `rootfs.ext4`, consumes `boot-next` before one-time `test` or `rescue`; tests candidate hash. POSIX shell syntax, five-pass ext4 fsck, QEMU ARM BusyBox applet checks, six static selection-policy examples PASS. **No physical boot test. Not part of first I0 change.** |
| `MZ604-UPSTREAM-MATCHED-MODULES.tar.xz` | 114 module files, SHA256 `150686794b2f01d98cc811352edca29f63ef0139a8d462c1bac5110d956824a3`; use only if live kernel matches `7.0.0-next-20260422+`. The I0 Debian image already contains original matching modules; don't install blindly. |
| `MZ604-LINUX7-CONFIG-MATCHED-zImage`, `tegra20-motorola-wingray-usb-peripheral-tested.dtb`, `kernel-config.txt`, `Module.symvers`, `MZ604-xoom-start-selector-v2-CANDIDATE.sh` | Exact build/source/DT/selector artifacts and offline diagnostic evidence. The USB DTB SHA256 is `4a63058b61cb06307ed592290d7d025fcee2ee493a2ceb2ee33bb8ea65fae11d`. No first-session kernel/p7 flash. |

**Old V1 selection image:** preserved under `...\staging\MZ604-READY-20261030` **SUPERSEDED** — this earlier selector used nonexistent `/bin/mv`, `/bin/sha256sum`, etc. V2 calls compiled ARM BusyBox applets explicitly, verified under QEMU. **Use V2 folder only.**

**Host utilities:** Surface `C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-READONLY-PREFLIGHT-20261030.py` for device inspection after recovery; `MZ604-Verify-Uncompressed-V2-20261030.py` for repeatable exact archive verification. Desktop build/provenance scripts in `C:\Users\olsen\xoom-linux-rom\inspection\Build-MZ604-I0-Ready-20261030.py`, `Build-MZ604-I2-Selector-And-Modules-20261030.py`, `Build-MZ604-P8-V2-20261030.py`. Linux source/build under `/home/xoomdev/xoom-linux-rom/mz604-linux7-internal-20261030/` and private output `mz604-recovery-ready-20261030/`. No proprietary blobs, actual MAC/SSID or passwords other than public lab convention should enter GitHub.

## Exact next execution stages — all actual device work is still PENDING

### Gate R0 — the owner's only physical step

Owner boots **MZ604** into original **TWRP recovery**, keeps USB attached to Surface and informs the agent. Do not ask for a password. The agent must **not** assume TWRP is ready merely because COM10 disappears. The user already authorized handling the subsequent controlled steps; still stop for unexpected or irreversible operations.

### Gate R1 — agent runs read-only recovery preflight

1. From Surface, run `python C:\Users\olsen\xoom-linux-rom\MZ604-TWRP-I0-READONLY-PREFLIGHT-20261030.py`. Require unique ADB serial `0428004243215557`, `ro.product.device=wingray`, TWRP `3.1.1-0`; otherwise **STOP**. Explicitly distinguish MZ604 from MZ600 COM9.
2. Confirm p10 is mounted correctly at `/data`, identify actual `/data/xoomlinux7/rootfs.ext4`, its size and **current live SHA**; read mounted paths/free space. The live file may have changed after the first boot (serial-getty fix), so do not require its hash to equal the older Oct29 original image.
3. Recheck pinned Surface `MANIFEST.json`, matching compressed root SHA, and the exact uncompressed expected digest; preserve the existing earlier backups.
4. Before modifying p10, make a **fresh independent backup of the exact live rootfs** to a new private Surface folder via verified ADB pull, and compare host SHA to the device's preflight SHA. Do not overwrite the Oct29 reference, the known COM10 p7 or p6. Require sufficient p10 free space for a new ~2GiB image plus compressed staging and the prior ~2GiB image retained. Treat ADB failure, identity ambiguity, unexpected file condition or storage shortage as STOP.

### Gate R2 — agent installs ONLY the Debian access image

5. **Do not flash p7/p8/p6.** Upload the I0 compressed ext4 file to a *new temporary name* in `/data/xoomlinux7/`; check compressed SHA on device before decompressing. Decompress into a **different temporary .ext4 filename**, verify full 2,146,435,072-byte size and raw SHA `351ae328...`. Use TWRP's actual available `busybox gzip`, or if unsupported decompress on Surface and push the full verified image; do not guess capabilities or bypass tool safety blocks.
6. After verifying the fresh off-device backup and staged new root, **rename** the original `rootfs.ext4` on p10 to a non-overwriting `rootfs.before-I0-20261030.ext4` recovery anchor; rename the new fully verified image to `rootfs.ext4`, sync and check expected name/size/hash. Keep older image on device for fast TWRP rollback. Protect unique labels and never delete the original.
7. From TWRP choose normal **reboot system** into unchanged p7. **Expected but not yet observed:** Surface COM10 appears with an automatically logged-in `xoom` shell. Check `id`, `sudo -n true`, `sudo -n id`, `uname -r`, `mount`, actual 2GiB rootfs and serial-getty. If no COM10/auth, stop before extra modifications and use owner-supervised TWRP to restore the archived rootfs by verified rename.

### Gate R3 — prove basic remote control before optional selector

8. In authenticated Debian perform a supervised **normal Linux reboot** and verify COM10 autologin and passwordless sudo return. This completes I0 and the normal reboot part of I1, not recovery/kexec.
9. With owner physically available, separately test a **Linux→TWRP** reboot request using source-backed Tegra method; verify TWRP ADB and return to unchanged default Linux. If it hangs, owner physical reset is acceptable; **do not modify bootloader or invent watchdog recovery**. Keep this as independent I1 PASS/FAIL.
10. Only after a successful I0 and normal reboot, consider I2: backup current live p8, compare it with prepared corrected baseline and selector, then deploy only a justified minimal selector update with exact SHA and rollback. The V2 selector is **not hardware-qualified** and must undergo supervised trial; do not apply it in the initial Debian access recovery transaction.
11. Resume **W1 exact upstream MZ604 Wi-Fi baseline**: identify actual kernel+DTB, modules, SDIO F1/F2, OEM firmware/calibration and MAC provenance. At first collect passive, read-only evidence; obey radio-regulatory gates before scanning or any active transmission. Proceed to W2–W6 evidence-driven minimal patches, not MZ600 r7 cherry-picks.

## Required fail/rollback disciplines

- **Never touch p1/EBB/BCT/bootloader/GPT, p6 TWRP, or flash a test p7 for I0.** Owner accepts physical button reboot instead of bootloader experimentation.
- Preserve actual live roots, hashes and mount flags. Do not alter `rootfs.ext4` while Linux has it loop-mounted: only TWRP, unmounted, approved exact device.
- A candidate that passes SHA and fsck **offline** is still physically **NOT RUN**. Do not mark it booted until USB serial + privileged shell actually return.
- No fragile inline one-liner that continues after a failed command. Stage, inspect, verify, then atomically promote within same p10. If transport tool blocks, stop and report; do not work around a safety denial.
- Record a concise timestamped [project log](../../project-log/README.md) entry after each substantive turn; milestone hardware PASS/FAIL requires detailed checkpoint, issues (#18 for boot/access, Wi-Fi issues for driver), state/index synchronization and fuller handoff. Every agent reads *all* chronological logs as-of their times, plus [mandatory reading map](AGENT_READING_MAP.md).
