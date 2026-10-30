> **2026-10-30 ADDITION: ALL project-log entries are explicitly time-scoped, not durable facts.** [Mandatory lightweight per-turn log and future-agent all-log reading](../project-log/README.md) and [complete reading map](../rfc/bcm4329-upstream-first/AGENT_READING_MAP.md) are required. New agents must read every chronological log, compare subsequent amendments with primary receipts, and never project historical "current" state forward. Milestones still need full checkpoint/handoff and authoritative issue/status index updates. This is an addition to, not replacement of, the existing document authority hierarchy.

> **Time-scoped state and continuity rule (2026-10-28):** The phrases **current state**, **latest**, **now** and equivalent terms in each document mean *current as of that document's own production/verification timestamp*. They are not timeless claims. Do not relabel an older checkpoint as incorrect solely because later hardware state changed; keep each period's snapshot intact. Later records should append new verified facts, state the time and link their predecessors, and state which observation is most recent **as of the new document**. The [dated active test snapshot](../ACTIVE_TEST_STATE.md) is a navigation aid, not an automatically live telemetry source. For any later session, verify the actual present device state before operating. After every milestone, update the dated index, [docs/status.md](../status.md), both runtime state files, and the linked chronological checkpoint **in the same commit**. Label PASS/FAIL/NOT RUN, exact source and firmware, hypothesis vs proof, and rollback. Conversation memory is not evidence; public material excludes identifying hardware/network/credential secrets.

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
