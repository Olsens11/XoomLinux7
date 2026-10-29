# M1 board-source proof: reuse after independent upstream and DTB verification

**2026-10-29 | Milestone M1 IN PROGRESS | Detached proof branch, NOT yet integrated/accepted.**

Owner design rule: The clean-sheet implementation may **reuse or adapt a precisely scoped portion of our earlier work** if that is truly the clearest and most conventional Linux solution. For each piece, compare (a) necessity for the current milestone, (b) source/behavior preservation, (c) better/smaller alternatives, (d) patterns in the pinned upstream tree, and (e) maintainer-friendly diff, style, tests and rollback. Do not cherry-pick the old series by default, and do not avoid useful code just because we've written it before.

## Source and variants verified

- Pinned untouched Linux 7 source worktree: `/home/xoomdev/xoom-linux-rom/rfc-bcm4329-minimal-2ghz-20261029`, `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, **zero new source patches**.
- Independent **disposable proof source worktree**: `/home/xoomdev/xoom-linux-rom/rfc-m1-dt-proof-20261029`, branch `rfc/m1-dt-study-20261029`, derived from *exact pinned upstream*, not from r7 or by cherry-picking its commits.
- Exactly three **unaccepted M1 study commits**, one logical change each:
  - `0eae4a8c7e4bca3548a4d49e5ca293feb7e83a1a` — arm/tegra compatible-binding schema for Xoom Stingray and Wingray;
  - `2eaebe1df2bb36e2f08ce9e6ed19561e9f1aa0a8` — separate common Xoom DTSI and short Wingray wrapper;
  - `0d4d7d3161b6ed9595f2cf28200535d59dcb3e0f` — Stingray-specific DTS wrapper and Makefile DTB entry.
- Source-equivalence: upstream Wingray DTS is **1711 lines**. Removing the DTS entry header and board-specific model/compatible declaration generates a **1707-line** shared body, **byte-for-byte identical** to the old experimental Xoom DTSI. This verifies a prior approach as a reference, but the new source was generated from upstream and independently reviewed.
- The minimal Stingray wrapper changes only `model`, `compatible`, and main USB controller/PHY from Wingray OTG/host description to peripheral/gadget mode. The SDIO Wi-Fi mapping `mmc2=&sdmmc2`, regulator/pin control and other common electronics are preserved.
- **Similar upstream convention:** NVIDIA Tegra already includes shared `tegra20-asus-transformer-common.dtsi` and `tegra20-motorola-mot.dtsi` for related variants. This is recognizable to DT maintainers, unlike a direct `.dts`-including-`.dts` shortcut which binds Stingray inheritance to Wingray's product identity.

## Cellular exclusion and narrowed M1 hardware acceptance (owner decision)

The owner explicitly excludes the **Verizon 3G CDMA modem** from the supported system: Verizon decommissioned CDMA January 3, 2023. This is a **service sunset**, not a claim that the radio frequencies became unused (licensed spectrum can be repurposed for LTE/5G). We therefore do **not** need modem driver initialization, modem-only USB host routing, modem network connectivity, or modem-specific power sequencing as M1 pass criteria. Maintain safe device hardware behavior and do not accidentally disable the shared BCM4329 SDIO path or the USB gadget/serial link.

Focus variant verification on **USB device/gadget role**, CDMA-independent SDIO/power and GPIOs that serve Wi-Fi, correct model identity and preservation of Wingray's currently supported hardware semantics. The draft Stingray peripheral-mode USB override remains a *candidate* to verify with a guarded boot, not proof that modem-specific EHCI must be added. See [Verizon's official CDMA shutdown](https://www.verizon.com/business/support/services-and-apps/cdma-network-retire/).

## Compiled proof (offline only)

- Build **untouched pinned-upstream Wingray** and the newly independently generated shared-DTSI prototype using the same ARM GNU toolchain, config and `make dtbs`: **both builds PASS**; prototype Stingray DTB also builds.
- Original Wingray DTB SHA256 **`c833f45e529dedaa70ff5f79e61f639236748c1be608020206039e1c834b6eef`**; new refactored Wingray DTB SHA256 **`4144940f352b437c340c5d37f5a4c9dcc711024ef9785746ff3bd2d1f8bab3ff`**. Different raw byte layout, but **`dtc -I dtb -O dts -s` normalized node/property content is identical**. This proves semantic preservation for Wingray at the DTS output level, not actual MZ604 hardware regression.
- Prototype Stingray DTB **61,076 bytes**, SHA256 **`c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa`**, **byte-identical** to the previous r7 experimental Stingray DTB. Old r7 is a research comparator, not a source of newly applied patches and not proof this new branch has booted on MZ600.
- Toolchain output includes existing warnings (e.g., USB controller/PHY duplicate addresses on DTS decompilation) in both old and new Wingray; no new semantic discrepancies were found.
- `git diff --check` succeeds on the small binding and Stingray changes. Copying the unchanged 1700-line upstream shared DTS body naïvely into a new file causes old whitespace to appear as newly added lint; **`git diff --cached -C --find-copies-harder --check`** passes and displays a **99%-identical copy** instead. Avoid cosmetic cleanup of 1700 unrelated lines in functional patch. Review exact extended copy-aware patch output before submission.
- **Schema checks now complete for targeted Xoom binding/compatible** (see the dated addendum below). **Still not done:** independent OEM-confirmed MZ600/MZ604 board differentiation, review of all relevant binding warnings, live USB/SDIO boot and MZ604 Wingray physical regression. M1 remains OPEN.

## Archived review patch and exact current style/schema gates

The three **unaccepted** copy-aware `git format-patch` artifacts are archived under [`patches/rfc/m1-board-proof-20261029/`](../../../patches/rfc/m1-board-proof-20261029/). They reproduce the three clean pinned-upstream-derived study commits, including extended `copy from` and `copy to` headers describing the **99% identical** common-board source. This is **a prototype**, not the canonical functional RFC series.

Initial `checkpatch.pl --no-tree --no-signoff` on those archived study patches:
- DT binding: **0 errors, 1 warning** (commit description missing).
- Shared DTSI/Wingray extraction: **0 errors, 2 warnings** (commit description missing; verify MAINTAINERS ownership for the moved common file).
- Stingray wrapper/Makefile: **0 errors, 2 warnings** (commit description missing; verify MAINTAINERS ownership for new DTS).
- Git's normal plain diff treats inherited 1700-line DTS body as new and raises old upstream whitespace; copy-aware `-C --find-copies-harder --check` **PASS**, leaving original board content unchanged. Reviewer-friendly copy detection and meaningful commit descriptions remain explicit pre-promotion work.

An actual `make DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/tegra.yaml dt_binding_check` was attempted against the study branch. It stopped **before any schema validation** with `Error: 'dt-doc-validate' not found!` because this build host lacks the Python `dtschema` tool. **At that historical attempt validation remained PENDING, not a detected schema defect; the required tools were subsequently installed and the focused tests PASSED (see addendum below).** The separate `make dtbs` DT compiles remain PASS.

## 2026-10-29 addendum — dtschema installed and targeted M1 schema tests PASS

[Full reproducible package/command/diagnostic record](M1_DTSCHEMA_VALIDATION_2026-10-29.md).

The desktop now has `python3-venv`, `swig`, `python3-dev`, `libyaml-dev`, and isolated Python `dtschema 2026.9` plus `yamllint`. `dt-doc-validate` and kernel `dt_binding_check` for `Documentation/devicetree/bindings/arm/tegra.yaml` **PASS exit 0, no diagnostics**. Filtered kernel `dtbs_check` **exits 0**, with **243 lines of root-compatible diagnostics for three unrelated Tegra boards**; this is **not** a warning-free whole-tree result. The focused `dt-validate -l arm/tegra.yaml` on both compiled Xoom Wingray and Stingray DTBs **PASS exit 0, zero output**.

As a control, broader all-schema validation of original untouched Wingray and our refactored Wingray each gives **the same 66 diagnostic lines** after normalizing build paths. No such broad-schema discrepancies are introduced by the M1 refactor; fixing inherited unrelated board bindings remains outside this patch.

**M1 schema subchecks are checked off; M1 overall remains IN PROGRESS** until the exact board-difference and physical testing gates close. This validation did not modify kernel source, the three study commit SHAs, the clean RFC checkout, old r7 or the actual Xoom.

## Design decision / what not to import

The correct minimal new board-support shape is a standard shared Xoom `.dtsi`, tiny Wingray and Stingray variant wrappers, a single Stingray DTB Makefile entry and a matching binding. The large shared body exists because the upstream Wingray description is large; it is **not** 1700 lines of new radio logic. A familiar upstream structure and compiled Wingray preservation justify the reuse conceptually.

**Do not copy/merge the old r7 Wi-Fi channel/scan/recovery patches, BigPart patch or ATAG parser into M1.** Each has its own distinct milestone/issue/evidence. Do not make a debug-only change to pin controls, clocks or country settings to satisfy a DT diff. Rely on standard DTS hierarchy and keep the current MZ600 p10 Linux system unchanged.

## Rollback / status

This study's candidate source commits are **local only**, on a separate proof source branch; the production clean RFC source worktree is still exactly pinned upstream with **zero added patches**, and the previous r7 research branch has not changed. Revert the proof by returning to pinned source at `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; no Xoom hardware change needs rollback. Track [M1 issue #17](https://github.com/Olsens11/XoomLinux7/issues/17), and only promote the three commits into the primary clean RFC source after schema, variant evidence and review gates are satisfied.

**Milestone progress:** M1a upstream/common source equivalence subcheck proven; M1b disposable three-commit draft prepared; M1c initial DTB compilation and Wingray semantic parity proven. **M1 as a whole remains unchecked** because schema, exact hardware differences, live boot and Wingray physical regression are still open.
