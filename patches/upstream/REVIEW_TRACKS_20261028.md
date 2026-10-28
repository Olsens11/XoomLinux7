# XoomLinux7 — Maintainer-routed source-review inventory

**Working snapshot:** 2026-10-28 UTC; branch `wip/clean-wifi-bt-usb-20261025`. **NOT SUBMITTED. NOT HUMAN SIGNED. NOT COMPLETE.**
**Kernel source base:** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. This is the reproducible development base, **not a promise that it is the final wireless/SoC receiving-tree base**.
**Owner's release policy:** All whole-chip components may be developed and validated in upstream-style independently reviewable source commits **now**. Actual posting/submission is held until the full BCM4329 implementation and integration are complete, and separately requires explicit human approval.

## Two independent products

1. **Maintainer review tracks** are logically scoped, independently versioned source commits and optional cover letters, with no experimental module parameters, binaries, private firmware, credentials, device identity or userspace deployment data. Never append a chronological Vxx fixup to a previously solved issue.
2. **Full-device integration manifest** names exact revisions of every selected review track, other kernel dependencies, Debian p8 environment, bootloader requirements and private deployment materials without putting these non-kernel artifacts into kernel patches. A clean wireless-only tree can compile yet cannot automatically boot the existing MZ600 p8 setup without platform compatibility. Record such prerequisites rather than hiding them.

## Current patch tracks and authority

| ID | Area / routing from pinned get_maintainer.pl or files | Current source and factual state | Release/validation gate |
| --- | --- | --- | --- |
| WIFI-01 | `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`; Broadcom wireless; Arend van Spriel; `linux-wireless`, `brcm80211` | Legacy bounded `WLC_GET_VALID_CHANNELS` fallback, `review-wifi-v2` 1/3; 4-way alternate 1/4. Related V31 lab behavior physically proven, cleaned source untested on Xoom. | Exact-form ARM build, fresh regulatory review, per-chip firmware, multi-model RF verification |
| WIFI-02 | Same driver; wireless | Per-scan ESCAN transaction ID, validation and rejection of stale success, alternate four-logical 2/4. Old combined v2 patch 2/3 included this. Four and three version **final source trees are equal** (local Git diff empty); prefix semantics must be independently evaluated. | Cancellation/timeout/duplicate, concurrency, wraparound, scan lifetime and per-prefix correctness |
| WIFI-03 | `brcmfmac/fweh.c`; wireless | Only genuine generation-matched malformed-index Event69 terminal route to sole live primary STA, alternate 3/4 dependent on WIFI-02. | Multiple vif/P2P, teardown, event version and endian validation, no unauthorized link-event rerouting |
| WIFI-04 | `brcmfmac/cfg80211.c`, `fwil.h`; wireless | Conditional `WLC_GET_UP` / `WLC_UP` readiness before ESCAN; alternate 4/4, original v2 3/3; V31 lab repeated scans proven. | Scope, power/PM regression, error handling, exact cleaned-source hardware test |
| WIFI-05 (unproven) | wireless | Slow ~399 s postboot association; uncertain vendor v1/v2 SET_SSID/LINK header/index handling; **no accepted fix** | Record proper raw format and causal evidence before new code |
| DT-01 | `Documentation/devicetree/bindings/arm/tegra.yaml`; Rob Herring, Krzysztof Kozlowski, Conor Dooley; Tegra Thierry Reding/Jonathan Hunter; `devicetree`, `linux-tegra` | `review-stingray-dt-20261028` 1/3: declare Wingray/Stingray compatible tuples | `dt_binding_check`, schema review, no new undocumented compatibles |
| DT-02 | `arch/arm/boot/dts/nvidia/`; Tegra SoC & DT | DT series 2/3: extract common Xoom electronics without intended semantic Wingray change | **Inherited source whitespace causes strict `git diff --check` failure**; maintainable whitespace fix and DTB semantic equivalence review |
| DT-03 | Tegra SoC & DT | DT series 3/3: Stingray wrapper and USB peripheral mode; independent earlier DTB build report | Exact clean-source board boot with proper compatible, physical MZ600/MZ604 regression; BigPart property deliberately excluded |
| BOOT-01 | `arch/arm/boot/compressed/atags_to_fdt.c`; ARM Russell King, `linux-arm-kernel` (Tegra review also relevant) | Existing separately formatted `rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch` and broad candidate snapshot. | Verify vendor ATAG parsing bounds, board scope, FDT write return and path portability; test exact source. Placeholder identity needs human DCO later |
| STORAGE-01 | `block/partitions/{efi.c,Kconfig}`; block Jens Axboe; GPT Davidlohr Bueso; `linux-block`, `linux-efi` | Legacy opt-in BigPart **integration snapshot only**; exact p8 storage boot physically proven with earlier source | **Not upstream-ready**: generic GPT effects, strict safety, command-line docs, code style and DT binding for `motorola,xoom-bigpart` remain open. Never slip into DT-03 |
| SDIO-01 | `drivers/mmc/**`, SDIO core; route with target `get_maintainer.pl` | Lab timing, F2, PM and OEM capability investigations; no fresh upstream-review member accepted | Isolate one necessary mechanism, avoid generic quirk unless justified |
| PWR-01 | GPIO/clock/regulator/pwrseq according to final modified paths | BCM4329 shared U4, WL_REG_ON, BT_REG_ON, 32 kHz clock; research/prototype only | Whole-chip ownership, suspend/resume, radio coexistence and binding ownership |
| BT-01 | `drivers/bluetooth/**`; Bluetooth maintainers via target tree | BCM4329B1 HCI lifecycle physically observed; private HCD remains outside public kernel source | Separate driver vs DT changes and prove Bluetooth coexistence, UART and patch-loading safety |
| INTEGRATION-01 | Internal, not mailed | Clean reviewer-style 3-DT plus 4-Wi-Fi replay complete: all four Wi-Fi driver prefixes compiled, both board DTBs built, unchanged-source full zImage/dtbs/modules build PASS after a recorded GCC ICE on first -j8 attempt. Broadcom module hashes match earlier three-Wi-Fi RFC build | Complete report with artifact SHAs and fail/open gates; test *exact same source* on target only with guarded, reversible owner-approved deployment |

## Series policy and dependencies

- The `candidate/series` four-file integration snapshot is archival; its broad Wi-Fi patch must not become an upstream prerequisite.
- `review-wifi-v2-20261028` contains a prior **three-commit** wireless review; `review-wifi-four-logical-20261028` is a fine-grained candidate. These are **alternatives**, never applied together. Promote the four-way split only after per-prefix compile/review results, and preserve historical source.
- `review-stingray-dt-20261028` is independent of wireless. Binding before DTS. Its 2/3 changes existing Wingray source; it needs inherited whitespace remediation in a deliberately scoped change, not a hidden cleanup.
- BOOT/MAC and STORAGE/BigPart are **not** silently brought into the clean 3-DT+4-Wi-Fi source replay. They remain explicitly missing from complete MZ600 p8 boot reproduction until accepted as independently testable review-form sources.
- Side branches for SDIO, PWR and BT are not submission-grade proof; do not imply every whole-chip function is upstream-ready because WLAN works.
- Use the [milestone closure policy](../../docs/process/DEVELOPMENT_WORKFLOW.md#milestone-to-upstream-integration-gate-mandatory-2026-10-27) and per-item G01–G12 checklist in [submission requirements](candidate/SUBMISSION_REQUIREMENTS.md). Every major finding changes this registry and appropriate track immediately, not at project end.

## Accept/reject rule

A work item can be **CHECKPATCH CLEAN**, **SOURCE REPLAYED**, **PREFIX BUILT**, **FULL BUILT**, **PHYSICALLY PROVEN EXACT SOURCE**, **REVIEWED**, **HUMAN SIGNED**, or **SUBMITTED**. Those states are separate; never label one as another. Current draft authorship `rfc-draft@invalid.example` and AI `Assisted-by` attribution do **not** satisfy human DCO. No AI tool may add `Signed-off-by`. Nothing in this project is mailed automatically.

Next steps: complete clean 3-DT+4-Wi-Fi prefix/full build proof; repair DT whitespace in a behavior-preserving independent change; produce clean BOOT and STORAGE tracks; validate shared-chip completeness and protected, reproducible test image; then only when all hardware integration is ready discuss mailing.
