# MZ600 v06.4 resumed — safe gzip host verification PASS, COM9 still held (2026-10-26)

**Classification: HOST-ONLY verification; no new tablet transfer, installation, reboot or flash.** Replacement MZ600 only. Protected original untouched.

## Continuity sources and baseline
Read docs/handoffs/MZ600_LINUX7_FULL_TRANSITION_HANDOFF_2026-10-26.md and latest matching-module missing-xz, 114-module build, permanent p7 SHA, stable fstab UUID, cross-boot partition GUID, WCC and Bluetooth checkpoints. Later physical proof outranks older pending claims. On Desktop WSL the development branch wip/clean-wifi-bt-usb-20261025 had clean worktree and HEAD 2586918. The repo validator returned 501 filesystem entries, errors=0.

Previously physically established, **not freshly inspected on tablet in this turn**: permanent Stage-D normal Debian 12.15 boot, Linux 7.0.0-next-20260422+, internal /dev/mmcblk0p8 ext4, verified image-prefix and full p7 SHA. Do not redo kernel build, reflash p7 or change GPT.

## Actual Surface checks
Files under C:/Users/olsen/xoom-linux-rom/downloads were independently SHA256/size checked:
- SAFE-OFFLINE.tar.gz (full file MZ600-v064-Linux7-7.0.0-next-20260422plus-matching-modules-SAFE-OFFLINE.tar.gz): **2798775 bytes**, SHA256 **5e051de2a1cf9875414886966a1ff00cf3ec5ba038b0688e7f7750ea2594a409**.
- MZ600-StageD-matching-modules-GZIP-SAFE-USB-RAM-upload-20261026.py: 7868 bytes, SHA256 **14f71ffd67ea17c75976e827ad5d2956b514d868f58d49c6c5109729aecfeef1**.
- MZ600-StageD-matching-modules-GZIP-SAFE-USB-RAM-upload-20261026.cmd: 490 bytes, SHA256 **d692b11fba7656a0b637561976a9015df810600552e7b4adada8cb1bf367ea8b**.

Read all 189 lines of Python sender. It verifies tar safety/no links, 114 ABI-matched ko entries, 3645 serial frames, the actual target's UID0/kernel/internal p8 ext4 root and an unused volatile target. It SHA-checks the transferred archive on Xoom before declaring success; it does not install or load modules, reboot, or modify p7. Existing safe uploader success JSON is **ABSENT**. COM9 is enumerated but owner-opened Open-Xoom-USB-Console.cmd and Start-Xoom-USB-Console.ps1 processes are **still active** as of an independent second check; do not kill/bypass these.

## Gate and next operation
1. Owner presses **Ctrl+]** inside the existing Surface console window, freeing COM9 without rebooting or exiting the Xoom root shell.
2. After confirming its handle released, execute the existing SHA-pinned native gzip-safe CMD uploader **once**. Demand actual on-Xoom verified SHA, successful exit and the dedicated new JSON log (not the earlier xz uploader result). Volatile target is /run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz.
3. Reattach user console. Reverify UID0, uname exact ABI, internal p8 ext4, archived bytes and SHA, space, depmod, absence of new /lib/modules/7.0.0-next-20260422+ and integrity of preexisting legacy modules. Inspect old orphan /lib/modules/.stage-v064-* after the failed xz extraction before any cleanup.
4. Extract gzip into a new uniquely named staging folder, count 114 ko, check Broadcom files and modules.dep, no unsafe symlinks, atomic guarded move **only** into the new kernel-specific module directory, depmod, and **modprobe -n -v** dry run. No live radio before separate controlled test.
5. Record the actual remote transfer/install in new physical checkpoint(s), update full handoff, status and runtime. Keep user credentials, GUIDs and MACs private.

**Actual newest evidence:** safe gzip exists and matches hash locally; transfer not yet verified; matching modules not yet installed. No new physical device commands were issued this turn.