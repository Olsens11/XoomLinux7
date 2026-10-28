# STORAGE-01 — submission-form BigPart compatibility checkpoint (2026-10-28)

**Source-review milestone, not a physical test or an upstream submission.**
Device untouched; no reboot, COM9, live partition writes, flashing or kernel
installation. Existing v06.4 MZ600 Debian p8 and rollback artifacts remain as
previously verified.

## Source of truth and new code

- Developer base: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
- Maintainer track: block/partitions / generic GPT (STORAGE-01). Independent
  unsigned `git format-patch` member:
  [review-storage-bigpart-20261028](../../patches/upstream/review-storage-bigpart-20261028/README.md).
  SHA256: `4051ca979a8b61af13eb49a8e7351722dcdabd44eb85d9e9bc509911a69568eb`.
- Standalone exact source: `655385d37f3e382e836f90f9cd4230089e1e743a`;
  patch + `Kconfig` + kernel-parameters docs constitute ONE logical change.
- Integrated source: first eight upstream-shaped RFC commits plus one
  STORAGE-01 `git am` on clean current source, tip
  `507eb069df819cb5cc801ad8be096f70d9ca7609`.
- Strict `checkpatch.pl --no-tree --no-signoff --strict`: **0 errors,
  0 warnings, 0 checks**. Source `git diff --check` PASS.
- Standalone `block/partitions/efi.o` cross-compile **PASS**, with
  `CONFIG_MOTOROLA_XOOM_BIGPART=y`; object SHA256
  `0fd9e46240b9706010aadc40b8019073012819ca14a5b642900e7529e6614ac6`.
- Seven independent source-literal and arithmetic tests from
  `tools/tests/test_xoom_bigpart_geometry.py` **PASS**; these are
  **not actual kernel runtime fault-injection tests**.
- Complete nine-commit `zImage dtbs modules` build started in an isolated
  clean ARM output directory; record its exact result separately, not by
  inference from source replay or EFI object compile.

## Why the old parser is not the right submission code

The earlier integration snapshot added a custom `gpt_sector=` parser and
looked up a constant alternate GPT at LBA 62,513,151. Reviewing the pinned
Linux 7 source revealed this logic is ALREADY IMPLEMENTED upstream:
Tegra20's `NVQUIRK_HAS_ANDROID_GPT_SECTOR` enables the MMC
`alternative_gpt_sector` callback, and `find_valid_gpt()` calls it when
`gpt` is enabled. Two 4096-sector eMMC boot partitions place the GPT at
62,521,344 - 8192 - 1 = **62,513,151**, precisely matching the read-only
physical GPT proof.

The new source thus **does not modify GPT sector search, GPT CRC or DT
binding**. The old `motorola,xoom-bigpart` property is removed from this
clean submission-form plan; it is not hardware description and would need
separate DT justification. No proprietary firmware or OS installer included.

## On-device evidence (prior implementation only)

- [2026-10-25 physical OEM GPT proof](MZ600_BIGPART_TWRP_PHYSICAL_GPT_LLSEEK_PROOF_2026-10-25.md):
  62,521,344 512-byte sectors, GPT signature read from alternate header at
  LBA 62,513,151; old TWRP accepted ten valid entries.
- [2026-10-25 v06.4 RAM-only BigPart physical PASS](MZ600_V064_CLASSIC_BIGPART_RAM_BOOT_PHYSICAL_PASS_2026-10-25.md):
  factory p1–p7 preserved, virtual p8=1 GiB, p9=512 MiB, p10=28,929.5 MiB.
  The physical test used a **different downstream source**, not STORAGE-01.
- Persistent Debian root on p8 was independently verified afterward, but
  **the source in this RFC has not yet booted or mounted that installation**.

## New activation and risk boundaries

**Both** kernel config `CONFIG_MOTOROLA_XOOM_BIGPART=y` and kernel cmdline
`gpt xoom_bigpart=1` are mandatory. The source ignores this feature by default
and returns the ordinary factory mapping without explicit opt-in. On a matching
Stingray disk with an opt-in, an unknown eMMC controller, GPT validation
failure, unexpected first-ten partition geometry or any extra active entry
prevents partition enumeration (fail closed). The parser itself never writes
GPT or sector contents. Raw userspace tools remain capable of damaging the
disk.

**Critical:** The existing Debian p8 filesystem expects 1 GiB. Do not
attempt a persistent or RAM boot of this new source with stock 256MiB mapping;
nor let an ordinary TWRP kernel write/mount the expanded p8 read-write.
For any eventual hardware test, create a reversible, SHA-pinned RAM boot
image with the exact bootargs, verify /proc/cmdline and all ten
/proc/partitions sizes **before any write or mounting p8 read-write**. Leave
the working p7 boot and p8 filesystem alone.

## Revision, normal-GPT regression and build provenance

An initial nine-patch source tip `b7d6fadb45a68691bf87837dae0c2d68c2a18c25`
**passed a complete fresh ARM `zImage dtbs modules` build**, exit 0 at
2026-10-28 08:13:02 UTC; `zImage` SHA256
`a2b3ddf4294673dde82628be59d96647e470a36599c629df65ff9d5d61b9b5b0`.
DTB and Broadcom module hashes remained unchanged from the eight-patch build.
A code review then found a fail-open condition for a recognized internal eMMC
with unexpected total capacity. This was corrected **within STORAGE-01's
original single logical patch**, not as an extra trailing fixup commit.
The revised patch uses `bigpart != bigpart_emmc` to reject mismatched
controller/geometry opt-in cases before GPT parsing. Its new unsigned
source commit is `655385d37f3e382e836f90f9cd4230089e1e743a`,
strict checkpatch **0/0/0**, and enabled ARM `efi.o` build **PASS**.

As an independent negative-control compile, with
`CONFIG_MOTOROLA_XOOM_BIGPART` **disabled**, `efi.o` compiled successfully
and SHA256 `2da2beb2099715b76ddbe492cce70d4023758d6bbe8b5e3ae4620820b06f1261`
was **byte-for-byte identical** to the object from the already-built
eight-patch kernel. This supports no change to default-compiled GPT logic.

The **revised** canonical nine-patch source is
`507eb069df819cb5cc801ad8be096f70d9ca7609`, generated by applying
the amended STORAGE-01 patch after the exact original eight commits.
A **new fresh ARM build** started separately and must be reported by its
own outcome, not by the earlier initial-draft build. The initial full-build
log and artifacts remain preserved for provenance.

## G01–G12 and remaining engineering gates

- G01/G02: pinned exact source and focused logical scope **PASS**.
- G03: standalone and nine-source `git am` replay **PASS**; full-prefix
  runtime/bisectability pending.
- G04: strict checkpatch/diff **PASS**; sparse/other static tools **OPEN**.
- G05: ARM `efi.o` compile **PASS**; final composite build status recorded
  only after completion.
- G06/G07: not relevant to the storage implementation, but still **OPEN**
  elsewhere in full BCM4329 project.
- G08: new DT binding **not required by this RFC**; DTS schema review stays
  independently OPEN for board review series.
- G09: exact-source BigPart hardware, opt-in disabled, wrong geometry,
  invalid GPT/CRC, controller ancestry, alternate-sector discovery,
  overlap/bounds and MZ600/MZ604 regression remain **OPEN**.
- G10/G11: final receiving-tree maintainers, human DCO and review **OPEN**;
  no `Signed-off-by`, `Tested-by` or submission claimed.
- G12: an explicit new bootarg and Kconfig setting are non-optional and
  documented; no hidden custom GPT parser or experimental firmware included.

**Open design objection:** Generic EFI partition maintainers may decline
vendor-specific virtual reinterpretation of a valid on-disk GPT. The RFC
remains a demonstrably scoped device compatibility proposal, but could
ultimately be retained as a downstream integration-only member. Our
full-device integration must be reproducible either way, without asserting
upstream approval.

## Next

Complete exact nine-source ARM build, repeat disabled-code compilation,
inspect the new failure paths, and prepare a private, reversible read-only
MZ600 test plan rather than flashing or risking the persistent p8 system.
Continue to update the storage track and project state at each milestone,
per the [mandatory development workflow](../process/DEVELOPMENT_WORKFLOW.md).
