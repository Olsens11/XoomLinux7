# MZ600 v06.4 — safe gzip 114-module archive transferred to Xoom RAM, physical SHA PASS

**Date:** 2026-10-26, following the full continuity handoff. **Target:** experimental replacement Motorola Xoom MZ600. **Scope:** verified RAM-only USB transfer; **NOT** kernel module installation or live radio testing.

## Host and device actions

Owner explicitly reported **COM9 free** after using Ctrl+] in the existing Surface USB console, without rebooting. Surface checked no conflicting console script process, COM9 present, the safe gzip SHA/size exact, and no prior gzip success JSON.

The **original**, previously audited, checksum-pinned command launcher was executed ONCE using Surface Desktop Commander:

`C:\Users\olsen\xoom-linux-rom\downloads\MZ600-StageD-matching-modules-GZIP-SAFE-USB-RAM-upload-20261026.cmd`

Uploader script SHA256 `14f71ffd67ea17c75976e827ad5d2956b514d868f58d49c6c5109729aecfeef1`, CMD SHA256 `d692b11fba7656a0b637561976a9015df810600552e7b4adada8cb1bf367ea8b`.

Actual physical uploader output:
```text
Local archive verified: 2798775 bytes, 114 correct-release modules
Xoom root UID, kernel release, internal ext4 root and unique RAM path: PASS
Transferred 256 / 3645 base64 lines
...
Transferred 3584 / 3645 base64 lines
SUCCESS: Xoom RAM-only module bundle SHA-256 PASS; NO installation yet.
Remote tar path: /run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz
GZIP_SAFE_RAM_UPLOAD_SHA_VERIFIED_ON_XOOM
Process completed with exit code 0 (runtime: 45.70s)
```

**Validated source and receiver:**
- `MZ600-v064-Linux7-7.0.0-next-20260422plus-matching-modules-SAFE-OFFLINE.tar.gz`, 2,798,775 bytes, **SHA256 `5e051de2a1cf9875414886966a1ff00cf3ec5ba038b0688e7f7750ea2594a409`**.
- The sender's actual preflight confirmed Xoom root shell **UID0**, running Linux **`7.0.0-next-20260422+`**, mounted Debian root **`/dev/mmcblk0p8 ext4`**, and a new unused `/run` transfer path. Full 3,645-line base64 transfer ACKed and Xoom-side SHA256 verification returned success.
- Surface persisted dedicated success receipt `downloads/MZ600-StageD-modules-GZIP-SAFE-RAM-upload-20261026-verified.json`; separately reopened and verified fields: `outcome=XOOM_RAM_ONLY_SHA_VERIFIED`, exact SHA, bytes, kernel release and volatile destination; `installed=false`, `drivers_loaded=false`. Success-log file SHA256 `6146aea7dd464c2ea1fb0282dfbe3181da9ef0084df430e30d52dd6f00e9124b`.
- COM9 still enumerated following upload. The sender closed its serial handle.

## Safe boundary: what was NOT changed

No `tar -xzf` installation yet; no `/lib/modules/7.0.0-next-20260422+` staging or move in this operation; no depmod; no modprobe; no Bluetooth/Wi-Fi radio activity; no reboot; no eMMC p7, GPT, p6 recovery, p8 filesystem partitioning or firmware changes. This result supersedes only the previous `COM9 busy / safe gzip upload pending` state. The earlier unusable `.tar.xz` may remain under `/run`, and a failed tar-xz hidden stage may exist on p8; inspect and preserve before cleanup.

## Next controlled installation gate

1. Restore owner-operated root USB console (the serial sender freed COM9). Read-only confirm `id -u=0`, exact kernel `7.0.0-next-20260422+`, `findmnt /=/dev/mmcblk0p8 ext4`, `stat=2798775`, SHA256 of the **gzip-specific** `/run` file equals `5e051de2...`, p8 free space and `depmod/gzip/tar` availability.
2. List `/lib/modules`, confirm preexisting legacy `7.0.0-next-20260422` survives untouched and new `7.0.0-next-20260422+` is absent. Inspect any old hidden `.stage-v064-*` directory and **do not blindly remove**.
3. Execute a fail-closed one-shot atomic install of **only** the matching kernel module tree, extracting tar.gz with strip-components=3 to a new hidden staging folder. Require 114 regular .ko, correct Broadcom drivers and modules.dep, then atomic move to new ABI-specific path; `depmod -a 7.0.0-next-20260422+` and `modprobe -n -v brcmfmac` dry run. Do **not** live-load radios before an explicit bounded test.
4. Record actual installation output in the next checkpoint, reconcile runtime and full handoff, and run repo validator. Do not claim modules installed merely because this RAM transfer passed.

**Milestone: SAFE GZIP RAM UPLOAD PHYSICAL SHA PASS; MATCHED MODULES PERMANENT INSTALL STILL PENDING.**