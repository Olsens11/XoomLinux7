# BCM4329 minimum-functional 2.4 GHz RFC — achievement milestones

**Scope:** Normal Motorola Xoom MZ600 BCM4329 2.4 GHz STA operation through upstream Linux 7 `brcmfmac`/`cfg80211`; no unverified 5 GHz TX, no speculative recovery system. **Branch:** `rfc/bcm4329-minimal-2ghz-20261029`. **Status labels:** `[x]` evidence-based COMPLETE, `[ ]` still OPEN. A source/build pass cannot close a physical-behavior milestone.

**Checkpoint rule:** Check an item off **only** when this branch's reproducible source, commit identity, source/build check and any required real hardware observation are linked. For an amendment, update the owning issue with exact old/new function/patch IDs, rationale, QA and rollback, then synchronize this file, `docs/ACTIVE_TEST_STATE.md`, `docs/status.md` and `runtime/PROJECT_STATE.env`. Preserve legacy r7 as READ-ONLY reference, not the parent of new implementation; no user identity/firmware or credentials committed.

## Source reuse and maintainability rule (applies to every milestone)

**Reusing verified prior code is allowed and often preferable**, but the clean RFC implementation must justify each reused portion against (a) the specific behavior required by the active milestone, (b) the smallest faithful upstream interface, (c) existing accepted kernel implementation patterns, (d) code readability/style/one-logical-issue patch scope, and (e) tests and rollback. Always compare a genuinely simpler alternative before selecting reuse. An old patch is **evidence and potentially a source of exact code**, not an automatic dependency or a reason to import neighboring work. Preserve source provenance, show meaningful diffs and explicitly log inherited upstream style if a large common file is moved.

## M0 — Clean-sheet foundation and project contract

- [x] Owner approves 2.4 GHz first, RFC before full dual-band features. [Scope decision](../../plans/MZ600_BCM4329_MINIMUM_FUNCTIONAL_2GHZ_UPSTREAM_RFC_SCOPE_2026-10-29.md).
- [x] Independent Linux source tree starts at **`2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`**, **zero new patches**, verified with [strict one-time baseline checker](../../../tools/rfc/check_bcm4329_clean_baseline.py).
- [x] Independent RFC project documentation and old r7 research preserved; original running Xoom not changed. [Clean architecture](README.md).
- [x] Initial repository check (884 entries, 0 errors). This checks project files, **not** kernel behavior.

**M0 COMPLETE.** The strict zero-patch checker is a bootstrap test and should intentionally stop passing after new implementation commits are made. Future tests must instead verify the pinned parent, documented applied series, and a clean working tree.

## M1 — Board identity and reproducible MZ600 device tree

- [ ] **M1a** Identify exact shared Wingray/Stingray hardware, common Xoom properties and *actual* variant differences from pinned upstream, OEM history and source evidence. Keep the original Wingray functional representation intact.
  - [x] **Source equivalence:** generated 1,707-line common Xoom body from original upstream 1,711-line Wingray DTS; exact match to independently preserved research reference. [Evidence](M1_BOARD_PROOF.md).
  - [x] **Upstream style precedent:** shared `.dtsi` plus short board wrappers matches other pinned Tegra20 boards.
  - [ ] Independently corroborate actual Stingray vs Wingray USB/power/radio differences with OEM/hardware evidence; old variant wrapper alone is not proof.
- [ ] **M1b** Build minimal, separately scoped binding/common-board/variant patches **from clean upstream**, not by cherry-picking old patch files; match upstream syntax/bindings and board-specific USB/SDIO/power behavior.
  - [x] **Disposable draft:** three separately committed **unaccepted** proof changes on local `rfc/m1-dt-study-20261029` branch: binding `0eae4a8c7`, common DTSI `2eaebe1df`, Stingray wrapper `0d4d7d316`. [Archived review patches](../../../patches/rfc/m1-board-proof-20261029/) and [issue ledger](https://github.com/Olsens11/XoomLinux7/issues/17#issuecomment-6503965844).
  - [ ] Check binding schema, exact variant hardware and reviewer-friendly patch structure before promoting any change into the untouched primary clean RFC Linux source.
- [ ] **M1c** ARM DTS/DTB compile and `dt_binding_check`/`dtbs_check` PASS. Assert **semantic Wingray DTB equivalence** for shared hardware (or explicitly justify each intentional delta), and validate Stingray compatible, Wi-Fi SDIO, regulators and USB routing.
  - [x] **DTB compilation:** pinned-original Wingray and independently built shared-DTSI Wingray/Stingray all compile in separate ARM out-of-tree builds.
  - [x] **Wingray preservation:** original vs draft `dtc -s` sorted DTB node/property representations exactly identical; raw bytes legitimately differ.
  - [x] **Stingray historical parity:** new compiled Stingray DTB (61,076 bytes, SHA256 `c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa`) byte-identical to earlier reference build. This is **not** a current physical boot PASS.
  - [ ] `dt_binding_check`, `dtbs_check`, explicit variant-difference audit and final signed-off review still required.
- [ ] **M1d** Controlled MZ600 boot with the new DTB, COM9/SDIO and normal system behavior, plus MZ604 Wingray regression gate when hardware is available; independent known-good recovery. **Never check complete on source-only evidence.**

**Status: IN PROGRESS — independent M1 source proof passed; board/schema/physical gates remain open.** New [M1 issue #17](https://github.com/Olsens11/XoomLinux7/issues/17), [compiled proof and review record](M1_BOARD_PROOF.md), with older related [DT issue #10](https://github.com/Olsens11/XoomLinux7/issues/10). Previous r7 DT refactor is research evidence, **not** the new branch's implementation. No M1 code or physical acceptance is claimed by this initial roadmap.

## M2 — Device identity, firmware load and normal WLAN registration

- [ ] Correct SDIO power/reset/clock initialization and calibrated BCM4329 firmware selection, with private blobs remaining external; standard `wlan0` appears on boot without manual overlays or scripts.
- [ ] Validate per-device MAC provenance (do not invent shared or random MAC unless upstream contract requires a safe fallback), boot/teardown and firmware logs.
- [ ] Physical warm/cold boot and ordinary driver load/unload gate. Issues for vendor MAC / boot behavior separate from DT as needed (existing [BOOT issue #8](https://github.com/Olsens11/XoomLinux7/issues/8)).

## M3 — Truthful 2.4 GHz channels and basic regulatory safety

- [ ] On firmware missing supported modern `chanspecs`, query only proven legacy information using *actual raw* `BCME_UNSUPPORTED` discriminator and bounded channel enumeration; preserve modern driver path.
- [ ] Show only firmware/hardware-supported, legally permitted 2.4 GHz STA channels; do not freeze country-current channel flags into immutable `orig_flags`, spoof region/revision, or invent DFS/power metadata.
- [ ] Ensure no unsupported 5 GHz TX/STA operation in the initial candidate (plain `NO_IR` alone is not a complete 5 GHz TX prohibition). Repeat after ordinary legal regulatory hints, and fail safely without speculative caches/retries.
- [ ] Host source/negative tests plus actual read-only/regulatory observed channel state and guarded physical radio tests PASS. Wi-Fi research [issue #4](https://github.com/Olsens11/XoomLinux7/issues/4).

## M4 — Repeated fresh 2.4 GHz scanning

- [ ] Standard `iw`/NetworkManager fresh scans show actual 2.4 GHz BSS records; at least three consecutive scans, including idle-after-scan and one cancellation.
- [ ] Exactly one correct completion/abort for each request, with no stale result, timeout wedge, spurious firmware-up dependency, or cross-request ownership problem.
- [ ] Use existing Linux driver scan lifecycle first; only add firmware-specific branches proven necessary with actual hardware traces. Document precise scan issue rather than reusing WIFI-02/03/04 by default.

## M5 — Ordinary WPA2 connection and network traffic

- [ ] NetworkManager / wpa_supplicant WPA2 association and authentication without userspace shims; DHCPv4, DNS and normal traffic.
- [ ] Disconnect/reconnect and AP restart behavior verified; no repeated module reload or manual recovery; record private logs safely.
- [ ] No false claims about unsupported legacy station telemetry or 5 GHz.

## M6 — Reproducible integrated functional baseline

- [ ] Clean patch application at pinned upstream, one logical issue per patch, no BigPart/firmware blob bundled into Wi-Fi RFC; full ARM `zImage dtbs modules` and DT schema/ABI tests.
- [ ] Functional boot + SDIO + Wi-Fi 2.4G scan/connection/regulatory tests repeated after ordinary restart; MZ600 and, where feasible, MZ604 coexistence tests.
- [ ] Known-good fallback, independent physical postflight and exact source/kernel/module/firmware hashes; original installed system not overwritten without explicit approval.

## M7 — First upstream RFC, not premature merge claims

- [ ] Each patch has a scoped commit, style/build/negative test report, linked issue amendment and rollback, no fabricated human DCO.
- [ ] Cover letter describes supported MZ600 firmware/device behavior, **demonstrated** normal 2.4 GHz Wi-Fi, 5 GHz deferred/regulatory boundaries, and specific maintainer questions.
- [ ] Owner reviews/authorizes any external mailing-list submission. Feedback may then revise design before further functionality.

### Deliberate post-RFC work (not milestones for this initial line)

Full dual-band 5 GHz regulatory/DFS and association, Bluetooth/FM, optional power management, advanced scan error recovery, firmware-generation cache, background recovery worker, wider country/SKU variants and unsupported telemetry. These have **not** been abandoned—r7 and earlier checkpoints remain accessible for later review.

### Live status

**Completed: M0 (1 of 8 milestone groups). Active: M1 with source/prototype subchecks above proved. Pending: M2–M7.** A milestone group remains unchecked until *every* child acceptance criterion is met, especially actual hardware gates. Update this summary when evidence changes.
