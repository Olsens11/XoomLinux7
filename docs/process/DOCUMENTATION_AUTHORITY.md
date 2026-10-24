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
