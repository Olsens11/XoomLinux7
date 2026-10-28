# ARM Stingray WLAN MAC bootloader ATAG — unsigned RFC review

**Status:** source replayed as an independently scoped Linux kernel change; **not submitted, not human-signed, not physically tested in this exact source form**. Base: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.

## Problem and scope

The Stingray Android bootloader exposes the device's factory WLAN MAC using Motorola vendor ATAG `0x57464d41`; the kernel needs to provide that identity to the BCM4329 SDIO node through the FDT `local-mac-address` property. This draft updates `arch/arm/boot/compressed/atags_to_fdt.c` only. It deliberately does not generate or hardcode a user MAC and does not contain firmware/NVRAM or anything from the Debian p8 installation.

The independent patch has been reconstructed from the older local [vendor ATAG RFC](../rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch), and re-exported using `git format-patch` from a pristine pinned upstream checkout. The draft code retains the originally researched logic; indentation and commit text were revised to pass `checkpatch.pl --no-tree --no-signoff --strict` with **zero errors/warnings/checks**. An older related source implementation has physical evidence, but **not this exact exported commit**.

## Upstream-review blockers (not waived by checkpatch)

1. Confirm the Motorola vendor ATAG data layout, length guards, and valid bounds when payloads are malformed or truncated.
2. Confirm precise board identification: code currently relies on the FDT Wi-Fi path, and must not touch a non-Stingray device with a coincidentally matching path.
3. Validate the return value and writable FDT capacity for `fdt_setprop`; prove bootloader/ATAG handling remains safe for normal ARM users.
4. Confirm whether code belongs in common ARM ATAG conversion, Tegra-specific boot plumbing, or another interface; consult ARM and Tegra maintainers on the receiving tree.
5. Verify exact source compile, full composite boot image, physical Stingray factory MAC correctness and Wingray/MZ602/MZ604 regressions before qualifying it for complete-device integration.
6. Human licensing review, actual author identity and DCO `Signed-off-by` are pending; the AI must never add sign-off.

Maintainer routing per pinned `get_maintainer.pl`: Russell King / `linux-arm-kernel`; Tegra maintainers should be included for board semantics. Recheck on the actual recipient branch.

The patch is an independent review track, **not a blanket prerequisite of the wireless patch series**, and should be introduced into the complete-device integration manifest only with exact hashes and verified tests. No upstream mail, no tablet change or flash.
