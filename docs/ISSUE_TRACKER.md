> **ISSUE #4 NEW SOURCE-ONLY R3 REVIEW CANDIDATE — 2026-10-28:** [Four-member r3](../patches/upstream/review-wifi-four-logical-20261028-r3/README.md) handles optional firmware per_chan_info 35/35 failure by conservative 5GHz NO_IR and caching recognized unsupported errno, **within WIFI-01**, no fifth patch; [dated physical/source QA and historical lookback](checkpoints/MZ600_WIFI01_R2_OEM2012_PHYSICAL_PERCHAN_UNSUPPORTED_R3_CANDIDATE_2026-10-28.md). r3 strict checkpatch and isolated ARM prefix build PASS. Do not promote to accepted code until exact error, regulatory/country permission, original V28 normal-scanning rationale and hardware results are resolved. Current MZ600 reconnected to original Wi-Fi.

> **LATEST #4 PHYSICAL RESULT AND REQUIRED HISTORY REVIEW — 2026-10-28:** [May2012 OEM exact r2 RAM-only test + earlier v05 lab NO_IR versus V28 deliberate removal](checkpoints/MZ600_WIFI01_R2_OEM_2012_PERCHAN_PHYSICAL_AND_HISTORY_2026-10-28.md): firmware dual-band/35 legacy valid channels PASS, **per_chan_info 35/35 FAIL**, actual regulatory parity OPEN. The issue remains open; follow the [owner's standing historical-reuse gate](process/DEVELOPMENT_WORKFLOW.md#mandatory-historical-reuse-gate-2026-10-28) before editing existing WIFI-01 or authorizing another test.

> **REGULATORY/5GHZ HISTORICAL EVIDENCE — 2026-10-28:** [Reconstructed older controlled tests](checkpoints/MZ600_BCM4329_5GHZ_REGULATORY_FIRMWARE_CAUSAL_TIMELINE_RECHECK_2026-10-28.md). #1 generic missing-band limitation is **already physically diagnosed at the firmware bandlist**; May2012 OEM firmware reports both bands without an extra US69 calibration injection. #4 r2 firmware per-channel restriction behavior needs OEM runtime evidence; #7/#13 firmware readiness / second-scan `BCME_NOTUP` after obsolete NO_IR lab gate removal are separate. Preserve old checkpoints and don't repeat consumed experiments.

> **ISSUE #1 EVIDENCE RECONCILED, 2026-10-28:** [Oct26–27 dual-band OEM firmware and regulatory A/B physical chronology](checkpoints/MZ600_BCM4329_5GHZ_REGULATORY_FIRMWARE_CAUSAL_HISTORY_RECONCILIATION_2026-10-28.md). Previous generic `4.220.48` bandlist was *already captured* (2G only); OEM US69 alone did not fix; May2012 `4.218.248.44` with unchanged NVRAM showed 2G+5G. Progress now targets actual exact-nine/r2 + May2012 integration, regulatory restrictions, normal/repeated scans, not redundant bandlist discovery. Issue #1 updated with citations to historical checkpoints; issue #4 r2 still OPEN.

> **Subsequent source QA update, 2026-10-28:** [Issue #4](https://github.com/Olsens11/XoomLinux7/issues/4) now has a [versioned r2 revision of WIFI-01](../patches/upstream/review-wifi-four-logical-20261028-r2/README.md), with [source-only checkpoint](checkpoints/MZ600_WIFI01_R2_PER_CHAN_RESTRICTION_SOURCE_QA_2026-10-28.md). Strict lint and ARM brcmfmac object-prefix compile PASS; no physical proof, original nine-source installed, issue remains OPEN. Issue count and patch count remain independent. [Issue #1](https://github.com/Olsens11/XoomLinux7/issues/1) missing Band 2 remains a separate diagnostic pipeline.

# XoomLinux7 GitHub issue tracker — first population, 2026-10-28

**[Open the live GitHub Issues board](https://github.com/Olsens11/XoomLinux7/issues)** · This file is an **as-of 2026-10-28 issue inventory**, not live telemetry. The repository's GitHub issue state is authoritative for subsequently opened/closed tickets. The user authorized populating the **personal development repository's** issue tracker, **not** submitting issues or signed patches to upstream Linux.

## Working classifications

- **Observed:** directly reproduced missing behavior, failure, or discrepancy on the exact development system. It does **not** automatically mean caused by our patches.
- **Inherited limitation:** source existed in original [xoom-linux/linux](https://github.com/xoom-linux/linux) baseline before our changes; can be *newly discovered by us* or known to source authors even if no GitHub ticket exists.
- **Patch-specific review risk:** concrete new source behavior or validation gap introduced by our patch; **not necessarily a confirmed user-visible defect**.
- **Validation/integration:** necessary acceptance testing or subsystem work; do not convert “not tested” into “broken.”
- **Release gate:** criteria for readiness, review, and owner approval. **Human DCO sign-off remains intentionally withheld** until owner says patches are ready.

At initial audit time, upstream `xoom-linux/linux` had GitHub Issues enabled but **zero filed issues (open or closed)**. This is not evidence that the baseline is bug-free.

## Issue register

| # | Area | Classification as filed | First priority | Primary source |
| --- | --- | --- | --- | --- |
| [#1](https://github.com/Olsens11/XoomLinux7/issues/1) | BCM4329 5GHz Band 2 missing | Observed feature gap; root cause open | High | [WIFI-BUG-01](bugs/WIFI-BUG-01-MISSING-5GHZ-PHY-BAND_2026-10-28.md) |
| [#2](https://github.com/Olsens11/XoomLinux7/issues/2) | Station telemetry / ASSOCLIST unsupported | **Pre-existing** in base source; reproduced | Medium | [WIFI-BUG-02](bugs/WIFI-BUG-02-STATION-TELEMETRY_2026-10-28.md) |
| [#3](https://github.com/Olsens11/XoomLinux7/issues/3) | Regulatory country / TX-power reports | Observed discrepancy; unsafe RF **not** proved | High investigate | [WIFI-BUG-03](bugs/WIFI-BUG-03-REGULATORY-TXPOWER-REPORTING_2026-10-28.md) |
| [#4](https://github.com/Olsens11/XoomLinux7/issues/4) | WIFI-01 firmware passive/radar parity | **Introduced source-path review risk**; impact open | **High / blocking review** | [WIFI-REVIEW-04](bugs/WIFI-REVIEW-04-LEGACY-CHANNEL-REGULATORY-PARITY_2026-10-28.md) |
| [#5](https://github.com/Olsens11/XoomLinux7/issues/5) | WIFI-02 ESCAN request generation / abort | New patch edge cases unvalidated | High | [Nine-patch audit](checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md) |
| [#6](https://github.com/Olsens11/XoomLinux7/issues/6) | WIFI-03 Event69 owner/malformed index | New patch edge cases unvalidated | High | [Review tracks](../patches/upstream/REVIEW_TRACKS_20261028.md) |
| [#7](https://github.com/Olsens11/XoomLinux7/issues/7) | WIFI-04 conditional WLC_UP / MPC | New patch edge cases unvalidated | High | [Review tracks](../patches/upstream/REVIEW_TRACKS_20261028.md) |
| [#8](https://github.com/Olsens11/XoomLinux7/issues/8) | BOOT-01 OEM ATAG → per-device MAC | New patch error/provenance paths unvalidated | High | [Provenance audit](checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md) |
| [#9](https://github.com/Olsens11/XoomLinux7/issues/9) | STORAGE-01 BigPart negative-path safety | New storage feature; fail-closed not fully tested | **High / blocking review** | [Provenance audit](checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md) |
| [#10](https://github.com/Olsens11/XoomLinux7/issues/10) | DT-01/02/03, schema and MZ604 parity | Our board refactor; variant regression untested | High | [Review tracks](../patches/upstream/REVIEW_TRACKS_20261028.md) |
| [#11](https://github.com/Olsens11/XoomLinux7/issues/11) | Bluetooth OEM HCD clock/reset and discovery | Observed failure; UART DTS value **inherited** | High | [OEM HCD A/B](checkpoints/MZ600_REVIEW9_P10_RECOVERY_SURFACE_OEM_BLUETOOTH_FIRMWARE_AB_2026-10-28.md) |
| [#12](https://github.com/Olsens11/XoomLinux7/issues/12) | SDIO, shared-chip rails and PM/coexistence | Cross-subsystem validation open | High | [Provenance audit](checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md) |
| [#13](https://github.com/Olsens11/XoomLinux7/issues/13) | Wi-Fi scan/stability/stress/power-save | Reliability testing open; no repeated failure proved | Medium | [Wi-Fi backend audit](checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md) |
| [#14](https://github.com/Olsens11/XoomLinux7/issues/14) | Local touchscreen/keyboard/console input | Partial hw success; actual local input untested | Medium | [As-of status](ACTIVE_TEST_STATE.md) |
| [#15](https://github.com/Olsens11/XoomLinux7/issues/15) | Battery, charging, audio, suspend, peripherals | Device acceptance coverage open | Medium | [Provenance audit](checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md) |
| [#16](https://github.com/Olsens11/XoomLinux7/issues/16) | G01–G12 upstream-quality release gate | **Not submission-ready; no human DCO** | Blocking release | [Review tracks](../patches/upstream/REVIEW_TRACKS_20261028.md) |

## Mandatory historical lookup before work on every issue (standing rule, 2026-10-28)

Before proposing a new fix, compare the symptom and exact kernel/firmware/board combination against historical physical checkpoints, experiments, older patch versions, prior issue comments and OEM/upstream driver examples. For each finding, add to the corresponding GitHub issue: **prior related result**, **how it was solved or why that approach was retired**, **which assumptions still hold**, and **smallest new discriminating test**. If none found, record searched locations. Do not mistake a lab-only passive/NO_IR restriction for an upstream-ready production regulatory implementation. **One logical change per patch does not imply one new patch per issue**; revise the existing patch whenever the correction belongs within its scope. Full procedure: [historical reuse gate](process/DEVELOPMENT_WORKFLOW.md#mandatory-historical-reuse-gate-2026-10-28).

## Update protocol for future experiments## Update protocol for future experiments

1. On every relevant test, comment on the *existing* issue with dated input/source identity, exact methods, observed data, limitations, rollback, and next discriminator; don't open a duplicate just to report new evidence.
2. Link a new dated checkpoint and any logically isolated proposed fix or commit. Compare against original pinned `xoom-linux/linux` base before assigning `introduced-by-us` or `upstream-pre-existing`.
3. Keep **reported upstream ticket**, **source-recognized limitation without ticket**, **our observation of a pre-existing defect**, **new patch behavior**, and **unproven hypothesis** clearly distinct. If causality changes, append a dated explanation; never quietly overwrite historical as-of findings.
4. Close a bug only with a reproducible exact-source acceptance pass, regression check and preservation of working Wi-Fi/p10/COM9/fallbacks. Close an acceptance ticket when all specified checks actually pass, not because the feature usually works.
5. **One coherent logical change per patch, but multiple issues/findings can refine one existing patch.** Do not create a patch merely because an issue was filed. User signs personally **only when ready**; do not apply fictitious human signoffs or open a pull request/upstream bug report without explicit instruction.
6. Source, binary, hardware identity and proprietary firmware evidence remains in the private documented locations; never paste BSSID, MAC, password, serial or private HCD blobs into public GitHub.

**Foundational records:** [Detailed provenance matrix](checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md), [formal exact nine-patch backend audit](checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md), [development workflow](process/DEVELOPMENT_WORKFLOW.md), and [data/evidence privacy](process/EVIDENCE_AND_PRIVACY.md).
