# Stage-D ABI-exact modules: offline build and QA PASS; COM9 port held (2026-10-26)

Device: experimental replacement Motorola Xoom MZ600. The protected original is excluded. Last known live Xoom: persistent Debian 12.15, kernel 7.0.0-next-20260422+, internal /dev/mmcblk0p8 ext4; p7 verified by prefix and full raw SHA256 in the prior permanent-boot milestone. NO boot or partition writes during this module work.

## Host connection recovery

User reported that the assistant connection was interrupted. Remote Desktop Commander independently confirmed SURFACE-BOOK-2 and DESKTOP-R16QJD4 online. The module archive survived with matching SHA256 on both hosts. Surface pyserial 3.5, matching-modules Python RAM uploader and native CMD launcher are present; Python syntax check and local archive validation passed. COM9 enumerates; no fastboot. This is NOT a device boot interruption.

## Offline build verification

Exact original BigPart Stage-D kernel build used: desktop WSL source /home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux and output v064-bigpart-debian-sdroot-build. Arm GNU Toolchain 14.3.Rel1; kernel release 7.0.0-next-20260422+; CONFIG_MODVERSIONS=y. Native Kbuild modules exit0 built 114 .ko including brcmfmac.ko, brcmfmac-wcc.ko, brcmutil.ko and Bluetooth modules. modules_install into an OFFLINE staging tree and depmod succeeded; modprobe --show-depends brcmfmac resolves brcmutil then brcmfmac. The deployed kernel zImage SHA256 remains d0ada47734cd7686f780cb37f9abb95e354a80d333840c7979b756053fe6a9d1, vmlinux SHA256 remains 02fe5350955156bdfa0020f6eefa4628c73cf7cacff50ba9058420ad22745dae.

Offline bundle: MZ600-v064-Linux7-7.0.0-next-20260422plus-matching-modules-OFFLINE-UNDEPLOYED.tar.xz. Size 1901356 bytes. SHA256 50d821138f0fe04f79855d8996a61652fa7788e48457a9ebf97409b527db11c6. Saved on Desktop WSL artifacts-v064-debian-p8-matching-modules-20261026 and Surface C:/Users/olsen/xoom-linux-rom/downloads; exact integrity match verified on both. NO module has been installed on the Xoom or loaded into its kernel.

Read-only repo verifier scripts/verify-v064-stageD-matching-modules-20261026.py passed across all 114 modules after two QA corrections: archive root directory lacking trailing slash was properly allowed without widening path access; host libkmod modinfo -F vermagic did not display 18 modules' generated metadata despite ELF readelf -p .modinfo showing valid NUL-terminated vermagic. Fallback checks actual ELF .modinfo in those cases and still requires identical kernel release and modversions. Result: 114 compatible ELF modules, fallback count 18, modprobe dependency pass, boot kernel binary hashes unchanged. This is OFFLINE metadata validation, NOT an on-device module-load or Wi-Fi confirmation.

## Surface USB RAM transfer staged but blocked

Uploader file C:/Users/olsen/xoom-linux-rom/downloads/MZ600-StageD-matching-modules-USB-RAM-upload-20261026.py SHA256 b8d1b295850bdab4edea76adb786d78231657ebcf66de3a6f1062ade197b758d. CMD launcher MZ600-StageD-matching-modules-USB-RAM-upload-20261026.cmd SHA256 2c898753f68fce2010389f3dc019b827e22122bb04e9124aa286f9105a5b92a3. These scripts send the exact SHA-checked archive only to /run RAM, with target root privilege, kernel-release, and mounted p8 checks, and do NOT install drivers or alter p7.

First launcher execution stopped during local archive path check, BEFORE opening COM9; corrected. Second execution fully PASSED local validation (1901356 bytes, 114 modules), then failed to open COM9 with Windows PermissionError(13, Access is denied). Windows process metadata identified an existing Surface Xoom USB console as serial-port holder. Attempt to send Ctrl+] through an unmanaged Desktop Commander process was rejected, so no additional terminal control was attempted. No remote RAM transfer started, and success log MZ600-StageD-modules-RAM-upload-20261026-verified.json is absent.

NEXT PHYSICAL OWNER ACTION: In the existing Surface Xoom USB console, press Ctrl+] to RELEASE COM9 without rebooting or logging out of the Xoom root shell. The assistant can then run the already prepared RAM-only CMD uploader. Require complete target SHA256 confirmation BEFORE installing anything into internal /lib/modules/7.0.0-next-20260422+. Wi-Fi radio and firmware testing will be separate, after module staging.

State at checkpoint: module build COMPLETE, offline QA PASS, Surface package integrity PASS, USB RAM upload NOT DONE (COM9 busy), internal Debian boot and flash intact.
## Follow-up: owner released COM9; RAM transfer completed with target SHA verification

Owner reported `COM9 free`. The already staged native Surface CMD uploader was executed ONCE. The actual Surface tool output:

```text
Motorola Xoom Stage-D: RAM-ONLY verified module upload over COM9.
Local archive verified: 1901356 bytes, 114 correct-release modules
Xoom root UID, kernel release, internal ext4 root and unique RAM path: PASS
Transferred 256 / 2476 base64 lines
Transferred 512 / 2476 base64 lines
...
Transferred 2304 / 2476 base64 lines
SUCCESS: Xoom RAM-only module bundle SHA-256 PASS; NO installation yet.
Remote tar path: /run/mz600-v064-stageD-matched-modules.tar.xz
USB_MODULE_UPLOAD_COMPLETE_SHA_VERIFIED_IN_RAM
Process completed with exit code 0 (runtime: 32.08s)
```

The receiver decoded and SHA-verified the entire archive on the **actual Xoom** to match `50d821138f0fe04f79855d8996a61652fa7788e48457a9ebf97409b527db11c6`, bytes `1901356`, under `/run` (volatile RAM). Xoom preflight verified UID0, exact `uname -r 7.0.0-next-20260422+`, internal root `/dev/mmcblk0p8 ext4`, and unused RAM target. The transfer code explicitly does **not** extract the archive, write `/lib/modules`, load drivers, change p7, or reboot. Previous status **COM9 busy / RAM upload pending** is superseded by this physical RAM transfer PASS.

After RAM success, an additional model-driven attempt to author a read-only remote-serial preinstall audit script was rejected by the remote interface's safety checks. No further device action was performed. Do not evade the safety controls. Resume with **user-operated local Xoom USB console**: inspect root UID, current kernel/root, free space, remote archive SHA, presence/absence of target new module directory and `depmod` before any permanent install. Preserve legacy `/lib/modules/7.0.0-next-20260422` (without `+`), back up as needed, then stage/install only exact `7.0.0-next-20260422+` if checks pass. Wi-Fi/radio/firmware testing is subsequent and still **NOT DONE**.

**Current actual state:** matching 114-module bundle IN XOOM RAM AND SHA VERIFIED; modules NOT installed or loaded; permanent Stage-D p7, Debian p8 unchanged by this task.

## Owner's real on-device preinstall checks and independently tested extraction layout

Owner showed Xoom USB root terminal: `id -u` returned `0`, `uname -r` returned `7.0.0-next-20260422+`, `findmnt -n -o SOURCE,FSTYPE /` returned `/dev/mmcblk0p8 ext4`; SHA256 of `/run/mz600-v064-stageD-matched-modules.tar.xz` returned exactly `50d821138f0fe04f79855d8996a61652fa7788e48457a9ebf97409b527db11c6`; `df -h /` showed `974M size, 464M used, 485M available, 49% used`; `ls -ld /lib/modules/*` showed ONLY preexisting root-owned `/lib/modules/7.0.0-next-20260422` (without plus); `command -v depmod` returned `/usr/sbin/depmod`. Serial pasted commands had visually interleaved echo but results were individually clear. These data satisfy prerequisites for installing a NEW separate versioned module directory, without touching the old one. No module has yet been extracted into p8 at this checkpoint.

Desktop WSL independently tested the *actual* SHA-pinned archive with GNU tar `--strip-components=3` into an otherwise-empty temporary directory. Result: exactly **114 `.ko` files**, the expected `modules.dep` at extraction root, and `kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko` at its intended relative path. Thus a guarded root-shell transaction may extract to a hidden, uniquely named staging folder beneath `/lib/modules`, count 114, check essential modules, atomically rename staging folder to `/lib/modules/7.0.0-next-20260422+`, run `depmod -a 7.0.0-next-20260422+`, and run only `modprobe -n -v brcmfmac` (dry run, not live radio startup). Retain `/lib/modules/7.0.0-next-20260422` and never touch p7 or GPT. Only call actual insertion after post-install verification and an explicit controlled plan.
