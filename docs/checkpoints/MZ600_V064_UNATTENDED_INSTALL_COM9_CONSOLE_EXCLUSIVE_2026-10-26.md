# MZ600 v06.4 — remote unattended install attempt blocked by existing exclusive COM9 console

**Date:** 2026-10-26. **Evidence classification:** Host-only diagnostic after owner's request to attempt installation while away. **No new on-device install, deletion, driver load, reboot, or flash.**

## Latest physically completed milestone remains intact

The original strict SAFE gzip uploader previously completed 3645 serial frames to `/run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz` and verified SHA256 `5e051de2a1cf9875414886966a1ff00cf3ec5ba038b0688e7f7750ea2594a409` **on the Xoom**, with its dedicated success JSON saved on the Surface. The current matching kernel release remains `7.0.0-next-20260422+`; installed Debian root on BigPart eMMC p8, and existing p7 boot are protected. The 114 matching modules have been built and offline-verified but have **not been installed**.

The guarded owner-console installer is version-controlled at `scripts/host/xoom/install-v064-stageD-matching-modules-once-20261026.sh`, `bash -n` validated, with owner-paste version staged on Surface at `captures/MZ600-V064-SAFE-GZIP-114-Modules-OWNER-PASTE-ONCE-20261026.txt`.

## Unattended live connection audit

Owner is away and asked assistant to run the installation. Desktop Commander reported SURFACE-BOOK-2 online. Surface physically reported:

- `COM9_PRESENT=True`.
- The earlier `Open-Xoom-USB-Console.cmd` (PID 20228) and `Start-Xoom-USB-Console.ps1` (PID 3908) were still running. This interactive PowerShell console owns the exclusive USB serial handle.
- The already verified dedicated gzip RAM success receipt exists.
- A separate read-only Python pyserial attempt to open COM9 failed with `PermissionError(13, Access is denied, 5)` before any serial command could be sent.
- A documented Desktop Commander `interact_with_process` attempt to submit benign `id -u` to PID 3908 returned `Failed to send input ... process may have exited or doesn't accept input`; that process is not managed as an input-enabled Desktop Commander session.
- Windows PnP shows the `USB Serial Device (COM9)` as OK; no USB/RNDIS network adapter presented as another Xoom command channel in this check.

**Result:** the tablet is not reachable by a second serial client while the owner's interactive console holds COM9, and that console cannot be safely controlled by the available managed-process input interface. No operator-supplied password was read, no unrelated console terminated, and no attempt was made to bypass the rejected input-control mechanism. **The pre-existing root session may still be active in that terminal; do not destroy it casually.**

## Next required transition

The existing owner Surface console must be released **normally** (Ctrl+]) by an operator who can control its window, preserving the tablet Linux root shell and avoiding reboot. Alternatively an explicitly authorized and tested console-sharing/managed bridge could be used in a future session; do not assume one is present. Then a single guarded serial transport for on-device **read-only preflight** can proceed. Installation must verify exact kernel/root, the unique gzip RAM archive SHA and length, space, old and new module directory state and orphan .stage folders before executing the versioned one-time transaction. Continue to preserve p7/TWRP/GPT and legacy module directory; do not claim `depmod` or Wi-Fi success before on-device evidence.

**Actual state at end of this checkpoint:** SAFE gzip RAM SHA PASS; permanent install **WAITING FOR INTERACTIVE SERIAL CONSOLE ACCESS**; no new tablet modifications.
