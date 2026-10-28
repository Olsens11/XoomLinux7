# Stingray / Wingray DTS canonical patch review — actual source comparison

**Status:** planned logical decomposition only; source patches not yet reconstructed or hardware-validated. **Authority:** pinned `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` and `patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md` G01–G12. Do **not** mail, sign, flash or change the live Xoom based on this note.

## Discovery: original 1,712-line Stingray patch largely duplicates 1,711-line Wingray DTS already in the pinned kernel

Compared `arch/arm/boot/dts/nvidia/tegra20-motorola-wingray.dts` with clean-review `tegra20-motorola-stingray.dts`, line-by-line using `diff -u`. Except for whitespace-only normalization (which itself is **not** a reason for an upstream patch), the material differences are:

1. Root `model` / `compatible`: Wingray -> Stingray.
2. `usb@c5000000` `compatible` EHCI -> UDC, and `dr_mode` OTG -> peripheral for both controller and `usb-phy@c5000000`. This distinction is device-function policy and must be checked against USB binding and physical MZ600.
3. `sdmmc4` internal eMMC gains `motorola,xoom-bigpart`, a vendor-specific opt-in coupled to **separate experimental BigPart GPT parser**. This is **not** ordinary board-enablement content and the DT vendor property currently lacks accepted binding documentation. Treat as a separate storage/controller integration track, with a documented opt-in and rigorous generic parser bounds checks. Avoid silently putting this property in the shared hardware description or retrofitting Wingray.

**Do not add a second wholesale copy** of common Xoom hardware. Linux DT convention prefers shared `.dtsi` for genuinely shared hardware, with small board `.dts` variants. New DTS should preserve all proven existing Wingray nodes as a starting point, not replicate ~1,700 lines and carry along existing formatting issues.

## Binding gap discovered in pinned tree

`Documentation/devicetree/bindings/arm/tegra.yaml` does not enumerate `motorola,wingray`, `motorola,stingray` or `motorola,xoom` (checked at exact pinned tree). The pinned `Documentation/devicetree/bindings/submitting-patches.rst` explicitly requires new compatible strings documented **in an earlier separate binding patch**. BCM4329 SDIO `brcm,bcm4329-fmac` is already described under `Documentation/devicetree/bindings/net/wireless/brcm,bcm4329-fmac.yaml`; do not invent a redundant Wi-Fi node/binding solely to split a patch. Review separate unrelated pre-existing compatibles before claiming `dtbs_check` clean.

## Proposed logical and review order (not necessarily one email submission)

1. **DT-BINDING-1** — `dt-bindings: arm: tegra: document Motorola Xoom variants`: amend root-board `tegra.yaml` compat entries to cover actual Wingray and Stingray compatible tuples. Preserve existing boards and binding inheritance. Requires `dt_binding_check`. Any storage-specific vendor property requires its **own binding issue**, not forced into this root-board patch.
2. **DT-COMMON-1** — `ARM: dts: tegra20: share Motorola Xoom board hardware`: factor genuinely identical hardware from existing Wingray into `tegra20-motorola-xoom.dtsi`; keep `tegra20-motorola-wingray.dts` as a minimal identity wrapper. **No behavior change for Wingray.** An independent, useful refactor justified by the immediately following additional board. Do not mix mechanical source moves with unrelated whitespace or hardware changes. Verify its compiled Wingray DTB property tree is identical to the pinned baseline, modulo irrelevant phandle numbering or build metadata if unavoidable; show comparison.
3. **DT-STINGRAY-1** — `ARM: dts: tegra20: add Motorola Xoom Stingray variant`: small Stingray `.dts` with its own identity, shared include, explicitly validated USB/peripheral delta, Makefile build entry and only physically grounded variant properties. Verify compiled Stingray DTB against the original V31-era 1,712-line candidate after accounting for *separately staged* BigPart opt-in; check boot function and USB serial safely before declaring equal behavior.
4. **STORAGE-BINDING-1 / STORAGE-INTEGRATION** — If the opt-in `motorola,xoom-bigpart` survives generic partition maintainer review, separately document the binding and stage the vendor property with a proven, reviewed partition parser, never in a generic unconditional board hardware refactor. Do not claim this storage approach is upstream-approved yet.
5. Further **BT / Wi-Fi SDIO / display / audio / USB** DTS patches only when a *distinct proven defect or new hardware capability* exists; avoid splitting the same already-functional board configuration by arbitrary node/function/file. In particular the shared DTS includes a Bluetooth UART node, Wi-Fi pwrseq and SDMMC2, many panel/audio nodes inherited from existing Wingray. Do not fabricate feature changes to inflate patch count. Audio is marked TODO in existing DT; do not claim fully operational sound.

## Upstream rules, verification and blockers

- Pinned `Documentation/process/submitting-patches.rst`, `5.Posting.rst`, `maintainer-soc.rst`, `Documentation/devicetree/bindings/submitting-patches.rst` and `arm/tegra.yaml` govern the work, together with `coding-assistants.rst`: no AI `Signed-off-by`; human-only DCO; accurate optional AI `Assisted-by`; no copied vendor firmware/license ambiguity.
- Verify every source series prefix applies, builds and (where possible) yields intended DT output. Run `dt_binding_check`, `dtbs_check`, `checkpatch.pl` and independent DTB content comparison; all are **OPEN** for reconstructed variant code.
- Existing broad Stingray DTS candidate has **353 checkpatch errors / 360 warnings**; most are inherited whitespace from Wingray, not proof of new functional defects. Do not “solve” this by duplicating 1,712 lines and formatting them; preserve provenance and avoid unrelated reformatting in feature commits.
- Existing MZ600 boot, internal p8 root, serial USB, Wi-Fi, DHCP, DNS, NTP and HTTPS were physically proved with **different existing integration snapshots**. The new clean DTS and platform series have not been deployed. Preserve p7/p8 and the working V31 module, and keep a reversible test route.
- Proposed source tracks are **different maintainer domains**: DT bindings, Tegra/ARM DTS, block/GPT storage and Broadcom wireless. Do not merge all into one nominal “BCM4329 integration” upstream patch. Before mailing, consult updated MAINTAINERS and receiving branches.

The target is the *smallest well-scoped actual behavior change*, **not the greatest number of patches**. Review the compiled DTB equivalence before choosing final commit boundaries.
