# Xoom Tegra20 board variants — unsigned RFC, not ready for submission

Three **logical** kernel source patches: (1) root compatible binding support for Wingray/Stingray; (2) no-intended-behavior-change extraction of shared Xoom hardware from the existing Wingray DTS; (3) small Stingray board identity and USB peripheral variant. No BigPart property, driver logic or personal firmware included.

Base: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
These are review artifacts, **not human-signed, not physically tested exact source**. See `manifest.json` and `docs/plans/MZ600_STINGRAY_DTS_LOGICAL_PATCH_DECOMPOSITION_2026-10-27.md`.

Offline check: both board DTBs compile in a new O= ARM build. Decompiling both compiled DTBs with `dtc -I dtb -O dts -s` and diffing to the known V31-era full-review-v2 build gives **zero device-tree content differences for Wingray**; for Stingray, **only the intentionally omitted `motorola,xoom-bigpart` boolean property differs**. Binary SHA hashes are not equal; do not claim byte-identical. Runtime and schema compliance remain open.

**Important style blocker:** the old `tegra20-motorola-wingray.dts` includes hundreds of pre-existing indent/whitespace defects. Moving it without unrelated reformatting preserves hardware semantics but surfaces the inherited defects as added lines in checkpatch. This RFC is **not style-clean**. Decide with the Tegra DT maintainer whether a strictly style-only preparatory fix of the existing Wingray file is warranted; never obscure a feature change inside mass whitespace edits. The BigPart property remains in the *separate storage review track*, which must define an acceptable binding and demonstrate bounds, fallback, safety and opt-in semantics.

Pinned Xoom-Linux documentation: `Documentation/process/coding-assistants.rst` (no AI Signed-off-by; human-only DCO), `Documentation/process/submitting-patches.rst`, `Documentation/process/5.Posting.rst`, `Documentation/devicetree/bindings/submitting-patches.rst`, `Documentation/process/maintainer-soc.rst`; local G01-G12 ledger applies. Do not mail or install anything without human review and explicit authorization.
