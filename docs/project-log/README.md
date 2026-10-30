# XoomLinux7 chronological project work log — mandatory agent process

> **OWNER REQUIREMENT (2026-10-30): EVERY substantive user/assistant conversation turn must leave a lightweight timestamped project-log entry. EVERY new agent must read ALL available project logs chronologically, from first to last, before acting.** Logs preserve what was known or believed **as of the entry timestamp**; they are NOT enduring truth and do not override later evidence.

## Format and burden

- Append a single short entry per substantive turn in a monthly file `docs/project-log/YYYY-MM.md` in ascending timestamp order; include local timezone offset (or UTC), focus, action actually taken (including NO ACTION), observed evidence, decision/uncertainty, next gate, and links to primary receipt/issue/commit when relevant.
- Routine turns: 4–8 concise lines, no duplicated full command output, credentials or raw private captures. Don't interrupt important engineering work with elaborate reports. This is **not** an alternate test database.
- Do not write speculative plans as completed tests. Explicitly label PROPOSED / OFFLINE / PHYSICAL PASS / FAIL / NOT RUN. Avoid words "current" or "latest" without as-of date. Never retroactively change an older entry to make its state fit later results; append correction, cross-link source.
- For an **important milestone**, also write a detailed immutable dated `docs/checkpoints/` record, comprehensive `docs/handoffs/` handoff, update W0–W6 gates/current-state/indexes and appropriate GitHub issue *in the same documented milestone work*. Logs link to these; they do not replace them.
- If a turn cannot update GitHub/working log because connection, permissions or safety checks fail, explicitly say so in the chat and prepare the exact entry for the next authorized session. Do not falsely claim persisted logging.
- New agents read every monthly log file, sequentially, **even when old entries seem superseded**; old entries explain why fixes were rejected or changed. The project may provide an index for navigation, never as a replacement for the log read. Combine this with [mandatory agent reading map](../rfc/bcm4329-upstream-first/AGENT_READING_MAP.md) and original physical evidence.

## Source-of-truth

1. Verified exact physical receipts + immutable checkpoints for what was measured then.
2. Source commits/build SHA and issue-amendment logs for exact code history.
3. Dated status/handoffs for navigation.
4. Conversation memory/work log for historical context only.

**Every item is as-of its date.** A later negative does not make a prior positive invented, but may supersede a prior hypothesis or "current state". Separate device variants, source branches, kernels and firmware always.
