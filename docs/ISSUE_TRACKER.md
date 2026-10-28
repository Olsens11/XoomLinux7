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

## Update protocol for future experiments

1. On every relevant test, comment on the *existing* issue with dated input/source identity, exact methods, observed data, limitations, rollback, and next discriminator; don't open a duplicate just to report new evidence.
2. Link a new dated checkpoint and any logically isolated proposed fix or commit. Compare against original pinned `xoom-linux/linux` base before assigning `introduced-by-us` or `upstream-pre-existing`.
3. Keep **reported upstream ticket**, **source-recognized limitation without ticket**, **our observation of a pre-existing defect**, **new patch behavior**, and **unproven hypothesis** clearly distinct. If causality changes, append a dated explanation; never quietly overwrite historical as-of findings.
4. Close a bug only with a reproducible exact-source acceptance pass, regression check and preservation of working Wi-Fi/p10/COM9/fallbacks. Close an acceptance ticket when all specified checks actually pass, not because the feature usually works.
5. One logical issue per source patch. User signs personally **only when ready**; do not apply fictitious human signoffs or open a pull request/upstream bug report without explicit instruction.
6. Source, binary, hardware identity and proprietary firmware evidence remains in the private documented locations; never paste BSSID, MAC, password, serial or private HCD blobs into public GitHub.

**Foundational records:** [Detailed provenance matrix](checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md), [formal exact nine-patch backend audit](checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md), [development workflow](process/DEVELOPMENT_WORKFLOW.md), and [data/evidence privacy](process/EVIDENCE_AND_PRIVACY.md).
