# I0 — supervised MZ604 Debian account restoration (prepared, not executed)

**As of 2026-10-30 12:05 EDT. This is an OFFLINE-ONLY plan, not a physical result.** Do not reboot into recovery while the owner is absent; MZ604 is currently at Linux Debian COM10 login but both accounts have locked password hashes. The owner accepts occasional physical restart, not bootloader risk. **No EBB/BCT/p1/GPT or p6 TWRP writes.**

## Offline preflight already completed

On Desktop WSL, the original MZ604 staged ext4 `MZ604-WINGRAY-DEBIAN-EXT4-ROOT-UNTESTED.img` is **2,146,435,072 bytes** with verified SHA256 `8c3daf6b39ea8df166b243568336254d7d60c0819ee895ccaa68afd4cbaec4ed`. The read-only `debugfs` check confirmed:

- `root` and `xoom` are **LOCKED** in `/etc/shadow` — no recoverable password.
- `xoom:x:1000:1000::/home/xoom:/bin/bash` exists.
- The default `%sudo` policy exists, but `xoom` is **NOT a member of the sudo group**.
- This is a **staged reference** image check, not a new read of the live p10 filesystem. The actual installed file must be inspected independently.
- Re-runnable read-only preflight: Desktop `C:\Users\olsen\xoom-linux-rom\inspection\MZ604-ACCOUNT-READONLY-PREFLIGHT-20261030.py`. It reads only off-device files, never touches the tablet.

## Owner-supervised procedure and stop gates

1. With owner physically near the tablet, use its established hardware recovery keys to enter **existing p6 TWRP**; do not first attempt unqualified Linux `reboot recovery`. On Surface verify actual `adb devices -l`, exact model/identity, TWRP version and target partition mapping. Beware MZ600 COM9 is a distinct tablet.
2. Identify live userdata and `/data/xoomlinux7/rootfs.ext4`. Verify exact live file size/hash independently; confirm expected mount/loop behavior. Keep TWRP p6, stable p7 and p8 unchanged.
3. Capture a fresh full, independently SHA-verified **live** Debian-image backup and copies of its passwd/shadow/group/sudoers before ANY edit. Validate there is storage and a recoverable restore method. Stop if metadata/identity differs unexpectedly.
4. Privately provision a **new owner-chosen xoom password** and add only the necessary xoom sudo-group membership. Use a supported, audited method after inspecting the actual TWRP/loop capabilities; do not blindly run Debian chroot if its kernel ABI is incompatible. Never store a password or hash in public source/logs, unattended command lines or private log output. Do not enable root password SSH as a shortcut.
5. Verify changes on a disposable filesystem copy first (syntax, file modes/ownership, filesystem consistency). Make authorized minimal live filesystem changes only after backup and exact safeguards; sync and cleanly unmount.
6. Return via unchanged default p7 to Debian; verify actual COM10 authenticated `xoom` login, `id`, working `sudo -v`, privileged Linux shell, mounts, kernel identity and serial getty. Confirm normal Debian reboot returns to same authenticated state. Record separate physical evidence and update logs/status/issue.
7. Only after I0 PASS, test Linux→TWRP reboot **with owner still physically present**, then p8 root selection. Leave kexec until standard boot paths are proven. Do not develop elaborate watchdog/crash recovery.

**Fail-closed:** missing backup, surprising SHA, invalid identity, group/mode mismatch, filesystem errors, unsupported password tool, lost serial, or a safety-tool block means STOP. The preflight does not authorize live mutation. See [infrastructure plan](REMOTE_TEST_INFRASTRUCTURE_PLAN_2026-10-30.md), [reading map](AGENT_READING_MAP.md) and [actual Oct30 checkpoint](../../checkpoints/MZ604_PERSISTENT_LINUX_COM10_PHYSICAL_2026-10-30.md).
