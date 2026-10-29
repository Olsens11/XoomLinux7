# MZ604 Wingray — upstream-first BCM4329 2.4 GHz RFC milestones

**Active for branch `rfc/bcm4329-upstream-first-20261029`**; this replaces the MZ600-first M0–M7 checklist only for new work. The old checklist, M1 study commits, and nine-patch research stay unchanged as historical evidence. No MZ604 physical tests or new Linux source patches have been accepted.

## W0 — Select starting board and isolate source
- [x] Select Motorola Xoom **MZ604 (Wingray, Wi-Fi only)** to match the existing upstream DTS and avoid a first-series MZ600/Stingray variant refactor.
- [x] Create a new independent Linux source branch/worktree from pinned `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; preserve old MZ600 branches/worktrees and installed systems.
- [ ] Verify the new checkout is clean; record an exact baseline config, DTB and build manifest and checksums. No MZ604 boot claim.

## W1 — Prove baseline upstream support, before any patch
- [x] Source-level: upstream DTS and Makefile already contain Wingray; DTS contains BCM4329 SDIO, power, reset/clock, regulators and IRQ; `brcmfmac` already contains BCM4329 chip ID, standard STA/scan and firmware paths.
- [ ] Compare upstream DT declarations with actual OEM **MZ604** board and firmware provenance; identify true mismatches instead of assuming prior MZ600 differences apply.
- [ ] Verify OEM board and bootloader identity and which firmware/NVRAM/factory-MAC path MZ604 actually uses. Never publish private values.
- [ ] Separate approved guarded boot test on a selected healthy MZ604 with verified rollback, bootloader/recovery/stock preservation and no persistent changes without explicit approval.
- [ ] Establish minimal normal boot, SDIO, firmware and `wlan0` baseline; if boot fails, isolate the earliest causal deviation.

## W2 — Decide the minimum BCM4329 firmware ABI compatibility
- [ ] Measure on **MZ604** whether `chanspecs` fails, which native BCME is returned, and whether `BRCMF_C_GET_VALID_CHANNELS` is available; distinguish old MZ600 evidence from new physical proof.
- [ ] If needed, introduce a small chipset/firmware-specific legacy inventory fallback in existing `brcmfmac` with bounded counts, native error discrimination and no changes to normal modern driver behavior.
- [ ] Source/negative/regression QA and then separate authorized exact-kernel hardware test.

## W3 — Effective 2.4 GHz regulatory safety
- [ ] Establish actual MZ604 firmware, board/calibration and Linux regulatory intersection; no forced US/69 or synthetic DFS metadata.
- [ ] Ensure unverified 5 GHz transmit-capable operation cannot occur; `NO_IR` alone is not enough.
- [ ] Review existing device-specific country mapping before adding a new DT property or policy.

## W4 — Repeatable ordinary scanning
- [ ] Three fresh completed 2.4 GHz scans through standard `iw`/cfg80211; verify event ingress vs delivered completion, timeout, cancellation and request lifetime.
- [ ] Add only **necessary proven** sync ID, invalid-index Event69 ownership and conditional firmware-UP fixes from preserved r7/V31 research, not the whole collection by default.

## W5 — Ordinary STA connectivity and reproducible build
- [ ] WPA2 connection, DHCP/DNS/data and normal NetworkManager or wpa_supplicant operation; disconnect/reconnect and repeated boots.
- [ ] Full ARM zImage/DTB/modules and ABI, targeted DT schema, kernel style and static tests; exact source/build/firmware identities and physical receipts.
- [ ] No BigPart kernel GPT changes, proprietary firmware redistribution, CDMA/LTE work, Bluetooth/FM or unsupported 5 GHz claims.

## W6 — First upstream RFC review
- [ ] One logical issue per actual patch; original upstream code reused; meaningful commit body, no artificial patch count.
- [ ] Summarize demonstrated functions, exact tested **MZ604** hardware/firmware, known gaps, conservative radio behavior and precise maintainer questions.
- [ ] User reviews patch set and personally supplies applicable DCO; only then may it be submitted externally.
- [ ] Maintain MZ600 and other Xoom board variants as follow-on support, not blockers for this first RFC.

**Current completion:** W0 selection/source worktree created (clean verification still open); W1 source-level starting facts confirmed, all MZ604 hardware gates open. No changed radio, device firmware, partitions or physical flash. Future changes require exact issue-linked evidence and safe rollback.
