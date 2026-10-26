# MZ600 v06.4 — guarded on-device matching-module installer staged; NOT run

**Date:** 2026-10-26, after the on-Xoom SAFE gzip RAM upload checksum PASS. **Status:** OFFLINE script authored and syntax-validated, **no module installation executed**.

The complete 114-ABI-matching module archive physically reached Xoom RAM and returned `GZIP_SAFE_RAM_UPLOAD_SHA_VERIFIED_ON_XOOM` with sender exit0. The new installed target `/lib/modules/7.0.0-next-20260422+` has not yet been verified or created; no live radio tests.

## Reproducible installer

Added `scripts/host/xoom/install-v064-stageD-matching-modules-once-20261026.sh` to the active development branch. Desktop WSL `bash -n` check **PASS** and repository validator `Checked 505 filesystem entries; errors=0`, clean checkout at commit `f2ae3de`. The Linux source-script SHA256 as computed on Desktop WSL is `43df19ca162d13735841b860469def7d6cc1603b078a68f04aaf29aef5585dbb`.

The script is intended for the **owner-operated ROOT USB COM9 serial console** (not remotely executed). It guards exact UID0, ABI, Debian 12.15, internal p8 mount/start/size/ext4 UUID, p7 geometry, old and new module-tree absence/presence, archive SHA/byte count and 189 members, 128MiB free space, available tools. It prints older hidden xz-failure staging candidates **without deleting them**. Only after checks does it create a new unique hidden staging directory under `/lib/modules`, extract safe gzip, demand 114 regular .ko, no links/special files, Broadcom modules and depmod metadata, then atomically move to a **new** `/lib/modules/7.0.0-next-20260422+`. It executes `depmod -a` and only `modprobe -n -v` dependency dry-runs; no live module insert, Wi-Fi scan, boot, reboot, GPT/partition formatting or p7 writes. Any failure leaves diagnostic staging for operator inspection and reports if the atomic move had already happened.

A 95-line owner-paste wrapper with Bash heredoc was written on Surface at `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V064-SAFE-GZIP-114-Modules-OWNER-PASTE-ONCE-20261026.txt`. The remote file-write operation reported 95 lines; **a separate attempted Surface integrity check was blocked by remote tool safety checks**, so do not claim an independent hash for that Surface wrapper. The canonical source file in GitHub has passed Desktop WSL shell syntax and is preferred for provenance. No serial command from this installer has been transmitted to the tablet.

The already established `Open-Xoom-USB-Console.cmd` was launched on Surface to restore the owner interactive window (COM9 still enumerated); the host separately observed its running PowerShell console process. If the owner has no root prompt, they must authenticate privately via `sudo -s` as before. Owner may review/copy-paste the wrapper into the terminal. Do not evade remote safety checks to automate privileged serial execution.

**Next accepted evidence:** actual on-Xoom output markers from the owner's run, including `MZ600_V064_PREFLIGHT_PASS`, `MZ600_V064_STAGING_VERIFIED_MODULES=114`, `MZ600_V064_MATCHED_MODULES_ATOMIC_MOVE_PASS`, `MZ600_V064_DEPMOD_PASS`, `MZ600_V064_MODULE_DRY_RUN_PASS_NO_RADIO_LOAD`, and `MZ600_V064_MODULE_INSTALL_COMPLETE_ABI_114`. These are **expected, not yet observed**. Update status/handoff/runtime only after physical evidence, preserve old module directory and boot p7.
