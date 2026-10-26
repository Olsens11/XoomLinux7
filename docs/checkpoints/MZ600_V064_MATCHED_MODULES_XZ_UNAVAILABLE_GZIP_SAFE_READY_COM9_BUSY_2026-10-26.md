# MZ600 Debian module installation — XZ missing, safe gzip replacement prepared (2026-10-26)

**Device:** authorized experimental replacement Motorola Xoom MZ600. Existing persistent Debian 12.15 boot from internal p8 and byte-verified Stage-D p7 remain protected and unchanged.

## Physical failure and exact scope

Owner ran a guarded root shell extraction of the SHA-verified 114-module `/run/mz600-v064-stageD-matched-modules.tar.xz` package. Device returned `/run/mz600-v064-stageD-matched-modules.tar.xz: OK`, then GNU tar failed: `tar (child): xz: Cannot exec: No such file or directory`, `tar: Child returned status 2`. Script used `set -euo pipefail`, so this abort happened immediately before any `mv`, `depmod`, or driver load. **No new final `/lib/modules/7.0.0-next-20260422+` install is verified and no radio activation, boot flash, or reboot occurred.** A hidden `.stage-v064-XXXXXXXX` temporary directory may have been created under `/lib/modules`; assess safely before removing. Existing unmodified `/lib/modules/7.0.0-next-20260422` remains the original old-version module tree.

Inspection of offline Debian armhf rootfs on Desktop WSL confirmed `/usr/bin/gzip` exists, but `/usr/bin/xz`, Python 3 and BusyBox were absent. So the safe correction is the same module tree repacked as a gzip-compressed tar that native Debian GNU tar can read; do NOT try to install unsupported xz binary or replace the deployed kernel.

## Offline repacking and Surface verification

Desktop WSL rebuilt gzip tar from the exact existing v064 ABI-matching staged module tree: initial gzip archive was 2,810,684 bytes, SHA256 `cb20ecdeac3f37d865a60aa2408ecb33c00fbcd873708206a34fe48e96395ab9`. Its member count proved 114 `.ko` files. Transferred all 3,660 base64 lines to Surface and independently verified the reconstructed tar SHA and size.

Strict Surface uploader local archive audit found **one development-only symlink** in initial gzip tar: `lib/modules/7.0.0-next-20260422+/build` pointing to the Desktop WSL kernel build path. Rather than allowing unsafe symlinks, Surface Python offline sanitizer removed that exact known link and rewrote a new, separate safe tar. All other entries are regular files or directories strictly under the expected kernel-release prefix, and 114 `.ko` files are present. Final SAFE gzip bundle:

- Surface path: `C:\Users\olsen\xoom-linux-rom\downloads\MZ600-v064-Linux7-7.0.0-next-20260422plus-matching-modules-SAFE-OFFLINE.tar.gz`
- **2,798,775 bytes**
- **SHA256 `5e051de2a1cf9875414886966a1ff00cf3ec5ba038b0688e7f7750ea2594a409`**
- **189 safe members**, exactly **114 `.ko` files**, and no links.

New dedicated Surface Python USB serial RAM-only uploader (does not install/load drivers):
`C:\Users\olsen\xoom-linux-rom\downloads\MZ600-StageD-matching-modules-GZIP-SAFE-USB-RAM-upload-20261026.py`,
SHA256 `14f71ffd67ea17c75976e827ad5d2956b514d868f58d49c6c5109729aecfeef1`. It checks the exact SHA/size, safe tar member paths/types and all 114 modules; sends 3,645 base64 lines via COM9 with 16-line ACKs and on-device SHA readback to separate volatile `/run/mz600-v064-stageD-matched-modules-gzip-safe.tar.gz`. Matching native Surface CMD wrapper `MZ600-StageD-matching-modules-GZIP-SAFE-USB-RAM-upload-20261026.cmd`. Python syntax check and local archive validation **PASS** (3,645 frames). No remote installation.

## Exact outstanding blocker

Owner still has the existing USB root console holding COM9. Attempted executing new CMD uploader: archive validated locally, then COM9 open failed with Windows `PermissionError(13, Access is denied)` before transferring any bytes. Uploader exited `GZIP_SAFE_RAM_UPLOAD_NOT_VERIFIED`; no remote success log was written. **Do not claim gzip RAM transfer or module install was completed.**

**Next owner action:** press **Ctrl+]** in the active Surface Xoom USB terminal to cleanly release COM9 without rebooting. Then rerun the prepared native gzip-safe RAM-only CMD uploader. Demand on-Xoom `SHA256 5e051de2...` over the new `.tar.gz` before any installation. For final scoped install, first verify original module directory and staged leftover, confirm correct UID0 and internal root. GNU tar should use its existing `gzip` support, extract 114 regular `.ko` into a new hidden staging directory, verify and atomically rename to `/lib/modules/7.0.0-next-20260422+`, then `depmod` and **dry-run-only** dependency inspection. Preserve legacy module directory and boot partition.

**Status:** original `.tar.xz` still SHA-verified in Xoom RAM; no modules installed; safe replacement `.tar.gz` staged and verified on Surface; RAM transfer waits on COM9 release.