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