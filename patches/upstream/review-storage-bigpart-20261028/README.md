# STORAGE-01 — classic Motorola Xoom BigPart, unsigned RFC

**Not submitted, not human-signed and not yet physically tested in this exact source.** Independent one-logical-change block/partitions RFC on pinned `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Maintainer domain: `block/partitions`, generic EFI GPT parser / block maintainers; obtain the final maintainers from the actual target tree.

## Hardware fact versus upstream question

The physical replacement Stingray MZ600 has 62,521,344 512-byte internal eMMC sectors; two 2MiB boot partitions; a factory alternate GPT physically located at sector **62,513,151**; and ten original partitions. An earlier **different** v06.4 BigPart kernel was physically booted and exposed p8 at 1GiB, p9 at 512MiB and p10 at 28,929.5MiB, while preserving p1..p7 and the last usable userdata sector. See [physical Stage A](../../../docs/checkpoints/MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md), [GPT read-only proof](../../../docs/checkpoints/MZ600_BIGPART_TWRP_PHYSICAL_GPT_LLSEEK_PROOF_2026-10-25.md), and the [layout audit](../../../docs/checkpoints/MZ600_V064_ORIGINAL_BIGPART_LAYOUT_MATCH_OFFLINE_2026-10-25.md). That does not prove this RFC's kernel behavior.

**Major scope reduction:** Linux 7 already contains Tegra20's `NVQUIRK_HAS_ANDROID_GPT_SECTOR` and `MMC_CAP2_ALT_GPT_TEGRA`, with `mmc_card_alternative_gpt_sector()`, `block_device_operations.alternative_gpt_sector` and the existing `efi.c` fallback when `gpt` is passed. Calculated OEM sector = 62,521,344 − (2 × 4096) − 1 = **62,513,151**. Thus no new `gpt_sector=` parser, no hardcoded alternate-sector probe, no modification to native GPT CRC checks, and no DT policy property are in the new patch.

## Single RFC responsibility

Only **explicit opt-in virtual mapping** for an exact original factory GPT: Kconfig switch + boot parameter + `efi.c` validation/remap. It touches three files as one coherent feature. `CONFIG_MOTOROLA_XOOM_BIGPART=y` enables the code, **but does not enable the remap**. The boot image must also explicitly contain **`gpt xoom_bigpart=1`**. Without the bootarg, the standard factory GPT mapping remains active. **Never boot an existing BigPart-formatted Debian p8 under the stock 256MiB GPT view.** Verify the exact bootargs and partition listing before mounting or writing.

The guarded path requires Stingray root compatible, the exact disk capacity and 512-byte sectors, a non-removable Tegra20 SDHCI controller at `reg=0xc8000600`, and a CRC-validated GPT with the exact ten known starting sectors/lengths and no additional active partition entries. Unexpected/invalid GPT or inability to identify the eMMC controller results in a refused parse rather than exposing ordinary extents, for the matching opt-in disk. No GPT, boot, recovery or partition-table bytes are modified by the parser itself. **Ordinary userspace partitioning utilities can still write raw disk contents**, so writing is expressly forbidden during initial testing.

## Correct boundaries

- This patch is **not** a DT binding. The former `motorola,xoom-bigpart` DTS opt-in is **not** in the clean Stingray board review; hardware DT must not be used as an undocumented kernel policy switch.
- The separate [8-patch review-form baseline](../INTEGRATION_SOURCE_MANIFEST_20261028.json) comprises 3 DT + 1 ARM/ATAG + 4 Wi-Fi patches. This STORAGE-01 patch can apply independently to the pristine base, or **once** after those eight changes. Do not apply the historic `candidate/0003-block-partitions-motorola-xoom-bigpart.patch` alongside it.
- The standalone source patch passed exact clean source replay, `git diff --check` and strict `checkpatch.pl` (0/0/0). `block/partitions/efi.o` compiled with the Kconfig enabled. A separate clean **nine-patch ARM build** is under verification and must be recorded by its actual result.
- `tools/tests/test_xoom_bigpart_geometry.py` checks the literal factory extents, proposed arithmetic, disjoint ranges, protected p1..p7 and alternate GPT arithmetic. **It is not a C runtime/kernel or storage-fault-injection test.**

## Unresolved upstream acceptance and safety questions

Mainline review might reject any vendor-specific **virtual reinterpretation of valid GPT entries inside the generic parser**, even with all guards. This compatibility implementation may ultimately belong in a downstream/device integration track rather than being accepted upstream. Do not equate code style and successful build with an accepted Linux design. Verify need/alternatives and the actual block maintainers before proposing this externally.

Remaining: prove this exact nine-patch kernel on MZ600 with a reversible RAM-only boot and correct `gpt xoom_bigpart=1` cmdline; perform negative GPT/CRC/controller and partition-table overlap tests without risking the installed p8; verify normal `xoom_bigpart=0` behavior on a disposable image; check early parse, warning paths, device-model ancestry and other Xoom variants; review correct upstream licensing/author and human DCO. **No firmware, OS image, root partition, bootloader or device must be altered by routine source QA.**
