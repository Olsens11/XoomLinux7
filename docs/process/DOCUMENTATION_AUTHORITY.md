# Documentation authority and supersession contract

Adapted from successful patterns in xoom-recovery and PS-to-VNC.

| Question | Strongest evidence |
| --- | --- |
| What source/config produced an image? | Exact Git commit + build inputs/toolchain version + artifact SHA |
| Was a binary really built? | Build log, checksum and files on builder |
| Did a tablet actually boot it? | Physical console/screen observation with DUT and date |
| Did Wi-Fi work? | Real wlan0, RF/association results with properly scoped identity and country |
| What is current accepted state? | docs/status.md + runtime/PROJECT_STATE.env, reconciled against latest measured evidence |
| Why was a technique attempted? | Dated experiment/hypothesis and upstream reference code |

An immutable failed experiment stays failed even if a newer test succeeds. New evidence supersedes earlier conclusions **only for what it actually measures**. Preserve original evidence; update living state and the relevant checkpoint, source map, roadmap and ancestor documentation index together. A version label does not certify hardware state.

Documentation must be navigable from [docs/README.md](../README.md) and local indexes. Directory-local readmes carry ownership, what is current, links to children, and next gates; older studies remain marked historical.

Publish only curated public documents after identity/credential/firmware review. Raw physical logs and ROM dumps are not automatically safe or open source.

## Milestone record and patch-integration authority (2026-10-27)

Every verified milestone must be recorded at its **natural subsystem location** and linked to a stable upstream work item. The immutable checkpoint is authoritative for what physically happened; the focused patch and its source SHA are authoritative for the proposed code; the acceptance ledger records what remains unproven; the whole-chip ledger maps cross-subsystem dependencies. Neither a handoff nor a conversation may silently override an exact device log or source/build fingerprint.

A checkpoint must explicitly state: **(a)** maintainer routing track and work-item ID, **(b)** exact source/artifact tested, **(c)** status of upstream canonical patch integration (**revised, already represented, lab-only, blocked or not warranted**), **(d)** G01–G12 gate changes, and **(e)** next verification. Document negative findings and supersession without deleting prior checkpoints. Distinguish a working V31 laboratory module from the clean review-v2 source, which needs separate hardware testing.

Use the [development milestone gate](DEVELOPMENT_WORKFLOW.md#milestone-to-upstream-integration-gate-mandatory-2026-10-27) before declaring a development milestone finished. Do not use readme/handoff prose as the sole record of a kernel change or infer that chronological experiment numbering maps to upstream patch ordering.
