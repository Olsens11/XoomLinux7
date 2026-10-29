# XoomLinux7 — Comprehensive handoff: minimum-functional BCM4329 2.4 GHz RFC

**Date:** October 29, 2026  
**Current phase:** M0 COMPLETE; M1 IN PROGRESS; M2–M7 OPEN.  
**Purpose:** Seamless continuation in the next ChatGPT conversation without losing source provenance, hardware safeguards, scope decisions, tests, issues, or the work we deliberately set aside.

> **Read this first:** The *new* clean-sheet RFC is the active project. The old WIFI-01 r7 and nine-patch implementation are preserved as *reference*, not the development line to continue. **No 3G/CDMA or 4G/LTE cellular functionality is required or desired.** Do not revive this work. The active objective is a simple, reviewable **2.4 GHz BCM4329 Wi-Fi implementation** through existing Linux interfaces, with a conservative and correct regulatory policy.

## 1. Authoritative project documents

Read the following on branch [`rfc/bcm4329-minimal-2ghz-20261029`](https://github.com/Olsens11/XoomLinux7/tree/rfc/bcm4329-minimal-2ghz-20261029) in this order:

1. [M0–M7 milestone checklist](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/rfc/bcm4329-minimal-2ghz/MILESTONES.md) — the **only authoritative completion checkboxes**.
2. [Clean-sheet RFC design and scope](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/rfc/bcm4329-minimal-2ghz/README.md) — user-facing goals, protected source trees, LTE/CDMA exclusions, regulatory gates.
3. [M1 board-source proof and draft commits](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/rfc/bcm4329-minimal-2ghz/M1_BOARD_PROOF.md).
4. [M1 dt-schema installation and validated output](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/rfc/bcm4329-minimal-2ghz/M1_DTSCHEMA_VALIDATION_2026-10-29.md).
5. [Owner-approved minimum functional scope](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/plans/MZ600_BCM4329_MINIMUM_FUNCTIONAL_2GHZ_UPSTREAM_RFC_SCOPE_2026-10-29.md), [AGENTS.md](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/AGENTS.md), and [development workflow](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/process/DEVELOPMENT_WORKFLOW.md).
6. [M1 GitHub issue #17](https://github.com/Olsens11/XoomLinux7/issues/17), especially its latest source/validation/safety and **no-CDMA/no-LTE** comments. Historical [DT issue #10](https://github.com/Olsens11/XoomLinux7/issues/10) and [Wi-Fi issue #4](https://github.com/Olsens11/XoomLinux7/issues/4) are prior research references.
7. [Active test state](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/ACTIVE_TEST_STATE.md), [status](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/docs/status.md), and [append-only runtime state](https://github.com/Olsens11/XoomLinux7/blob/rfc/bcm4329-minimal-2ghz-20261029/runtime/PROJECT_STATE.env). The **most recent RFC-specific blocks** supersede older chronological r7 content and stale earlier mentions of missing dtschema.

## 2. Product and technical goals

The first deliverable is the **smallest complete and technically sound** BCM4329 Wi-Fi integration on a Motorola Xoom MZ600 running pinned Linux 7. The chip should initialize automatically via the existing SDIO `brcmfmac` driver and register normal `wlan0`, with correct firmware, device-specific NVRAM/calibration and unique device MAC. Normal Linux `cfg80211`, NetworkManager and/or `wpa_supplicant` should support fresh and repeated 2.4 GHz scans, WPA2 connection, DHCP, traffic and reconnects without diagnostic user-space scripts or experimental module reloads.

**Initial RFC can explicitly leave 5 GHz unsolved**. Do not advertise or permit unverified 5 GHz transmissions. Effective Linux `cfg80211` restrictions, hardware/board capabilities and firmware restrictions must be intersected. The firmware valid-channel inventory alone is *not* proof of passive/DFS/radar permissions; `NO_IR` alone is *not* a complete prohibition on all STA transmissions. Do not invent regulatory metadata or force `US69`. Complete 5 GHz, Bluetooth/FM, firmware-generation caches, asynchronous regulatory retry engines and rare failure recovery are future work unless a real blocker is proven.

**Review-oriented simplicity:** Prefer familiar upstream APIs and historically accepted subsystem structures over bespoke recovery layers. This is a **clean design reconsideration, not a ban on reusing past code**: reuse exactly the portion of r7 or earlier source that satisfies one milestone if it proves the most elegant, maintainable and reviewer-recognizable solution. Independently compare alternatives; one logical issue per patch; descriptive commit body; separate test results and rollback per owning issue. An upstream RFC can be submitted for early feedback *before* merge acceptance, but do not send anything publicly without owner authorization.

### Explicit cellular exclusion and RF policy

The owner has settled this repeatedly: **No cellular support of any kind** in the minimum RFC — neither MZ600 legacy 3G/CDMA nor MZ602/other 4G LTE. No modem driver, cellular registration, SIM/carrier, baseband firmware, modem-only USB host routing, modem power sequencing or cellular tests. Some older OEM trees use `stingray_cdma` for MZ600 and `stingray` for LTE MZ602; **do not confuse variants**. The historical Verizon CDMA network was retired; this is only background, not a reason to explore LTE.

**Do not deliberately initialize or activate the legacy cellular radio** during development or hardware testing. Do not release modem-specific resets or enable a modem-specific host route. Automatic registration and uncontrolled RF transmissions should be avoided. This must **not** remove shared clocks, regulators/GPIO or the USB controller/PHY needed for **supported USB gadget COM9 serial console** or BCM4329 SDIO Wi-Fi. An MZ600 USB peripheral-mode DT override is currently justified by our Linux gadget/serial access, *not* by cellular functionality. See issue #17's most recent scope/safety comments, notably `#issuecomment-6504813198`, `#issuecomment-6504839683`, `#issuecomment-6504888403`.

## 3. Current source and worktree separation — extremely important

| Role | Path / identity | Intended use |
|---|---|---|
| **Active GitHub documentation** | Repository `Olsens11/XoomLinux7`, branch `rfc/bcm4329-minimal-2ghz-20261029` | Current RFC plan, milestones, issues, checkpoint documentation |
| Local RFC project docs | `/home/xoomdev/xoom-linux-rom/rfc-bcm4329-minimal-project-20261029` | **May lag GitHub**. Fetch and fast-forward before editing. Last observed local `c2e4df9f4020aa6c6587fe08c14b76950dfe4058` prior to later GitHub updates. |
| **Pristine active Linux source** | `/home/xoomdev/xoom-linux-rom/rfc-bcm4329-minimal-2ghz-20261029`, branch `rfc/bcm4329-minimal-2ghz-20261029`, commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` | **ZERO new patch commits**. Protected clean source until draft is justified and tested. |
| **Isolated M1 DT proof** | `/home/xoomdev/xoom-linux-rom/rfc-m1-dt-proof-20261029`, branch `rfc/m1-dt-study-20261029`, HEAD `0d4d7d3161b6ed9595f2cf28200535d59dcb3e0f` | Exactly three **unsigned, unaccepted** study commits, off the pinned upstream base. |
| **Historical r7 implementation** | `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-wifi01-r7-source-20261029`, nine-patch source tip `c0fe77938192a33f186998b335892e70793ea826` | Research/reference and rollback record, **not** the parent of the new RFC patches |
| Protected running Xoom | MZ600 Debian Linux 7 on internal p10, previously verified generic BCM4329 2.4 GHz connection | Last verified prior to new RFC; **not rechecked during M1**. No flashing, firmware swap, boot modification or live RF test during the clean RFC work. |

**Do not conflate project metadata Git ancestry with the pristine Linux source branch.** GitHub RFC project documentation inherited the older project history for access to records. The actual new Linux source worktree is at the exact upstream SHA with zero inherited patch commits.

### Local build/test directories and tools

- ARM out-of-tree reference DT build: `/home/xoomdev/xoom-linux-rom/rfc-m1-dtb-reference-build-20261029`.
- ARM out-of-tree proof DT build: `/home/xoomdev/xoom-linux-rom/rfc-m1-dtb-prototype-build-20261029`.
- Isolated `dtschema 2026.9` Python environment: `/home/xoomdev/xoom-linux-rom/.venvs/rfc-m1-dtschema-20261029`.
- Validation logs: `/home/xoomdev/xoom-linux-rom/inspection/rfc-m1-dtschema-20261029/`.
- Existing cross compiler prefix: `/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-`.
- Archived proof review patch files: [`patches/rfc/m1-board-proof-20261029/`](https://github.com/Olsens11/XoomLinux7/tree/rfc/bcm4329-minimal-2ghz-20261029/patches/rfc/m1-board-proof-20261029).
- Bootstrapping verifier: `tools/rfc/check_bcm4329_clean_baseline.py`; intentionally only passes before first actual new source patch; don't weaken later to force it to pass.

## 4. Evidence-gated milestones

| Milestone | State | Requirements to close |
|---|---|---|
| **M0 — Clean-sheet plan and source baseline** | **[x] Complete** | Approved 2.4 GHz-first scope; clean pinned upstream; protected old work; new docs. |
| **M1 — Board identity and Stingray/Wingray DT** | **[ ] IN PROGRESS** | Already passed source, build, targeted schema subgates; still needs corroborated relevant MZ600 differences, maintainer-ready source, physical MZ600 USB serial/SDIO/boot and MZ604 regression when possible. **No modem/LTE test.** |
| **M2 — Correct BCM4329 firmware/calibration/MAC and `wlan0`** | [ ] Not started | Normal initialization without debug overlays; verified boot/teardown and MAC. |
| **M3 — Truthful 2.4 GHz channels and regulatory safety** | [ ] Not started | Legacy compatibility, real native BCME errors, no illegal or unsupported 5 GHz TX, safe 2.4 GHz. |
| **M4 — Repeated fresh scans** | [ ] Not started | At least three fresh 2.4 GHz scans and cancellation/ownership correctness. |
| **M5 — WPA2 connectivity and traffic** | [ ] Not started | DHCP, DNS, data, disconnect/reconnect and ordinary network management. |
| **M6 — Reproducible integrated baseline** | [ ] Not started | Clean patches, full ARM zImage/DTBs/modules and ABI, physical test/rollback. BigPart/storage separate. |
| **M7 — Initial upstream RFC** | [ ] Not started | Single-issue patches, honest capability limitations, maintainer questions, owner-approved external submission. |

**Milestone rules:** One completed subcheck does not close its group. Previous r7 source/build/hardware achievements do not close clean RFC physical gates. All changes update MILESTONES.md, active state, status, runtime state and the relevant GitHub issue. Source-only tests are not on-device acceptance.

## 5. M1: device-tree source proof already obtained

Pinned upstream Linux 7 has `tegra20-motorola-wingray.dts` (1,711 lines) and **no new MZ600 Stingray DTS**. The new independent proof, constructed from upstream instead of cherry-picking r7, extracted a common **1,707-line Xoom `.dtsi`**, leaving minimal Wingray and Stingray `.dts` wrappers. The shared body exactly matches the old reference file byte-for-byte, confirming earlier work's value as a design reference. Similar common-DTSI patterns already exist in mainline Tegra boards.

The Stingray draft overrides board identity and the USB controller/PHY to peripheral/gadget mode. It shares Wi-Fi SDIO, common regulators, clocks and hardware descriptions. **No cellular driver, LTE support, modem activation or modem-specific USB host is introduced**. This is a **source-only** conclusion, not a fresh boot result.

### Three logical, unaccepted proof commits (separate local branch)

1. `0eae4a8c7e4bca3548a4d49e5ca293feb7e83a1a` — Tegra arm binding for Motorola Xoom Wingray/Stingray compatibles.
2. `2eaebe1df2bb36e2f08ce9e6ed19561e9f1aa0a8` — refactor shared Xoom hardware into `.dtsi`, keep tiny Wingray wrapper.
3. `0d4d7d3161b6ed9595f2cf28200535d59dcb3e0f` — Stingray wrapper and Makefile DTB entry.

No human Signed-off-by or upstream publication. Initial archived `checkpatch`: 0 errors, binding 1 warning; common 2 warnings; Stingray 2 warnings (missing meaningful commit body / MAINTAINERS ownership). `git diff -C --find-copies-harder --check` passes, treating the shared DTSI as 99% copied original source rather than ~1700 newly authored whitespace-linted lines. Add good commit descriptions, verify MAINTAINERS, avoid cosmetic 1700-line changes before promotion.

### Compiled board parity (offline evidence)

- Original upstream Wingray and independently refactored Wingray **DTBs both compile** using ARM GNU 14.3.1; prototype Stingray DTB also compiles.
- Wingray original/refactored raw bytes differ in serialization order, but sorted `dtc -I dtb -O dts -s` node/property representations are **semantically identical**.
- Prototype Stingray **61,076 bytes**, SHA256 **`c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa`**, **byte-identical** to the old r7 Stingray DTB. This is reproducibility, not on-device proof.

### `dtschema` installed and validation gates passed (do not redo installation)

WSL Ubuntu 22.04 installed OS prerequisites `python3-venv`, `swig`, `python3-dev`, `libyaml-dev`; dedicated venv has `dtschema 2026.9`, `yamllint 1.38.0`, `dt-doc-validate`, `dt-mk-schema`, `dt-validate`.

Actual results on unchanged three-commit study source:
- `dt-doc-validate` for `Documentation/devicetree/bindings/arm/tegra.yaml`: **PASS, exit 0, no diagnostics**.
- `make DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/tegra.yaml dt_binding_check`: **PASS, exit 0, no diagnostics**.
- `make ... DT_SCHEMA_FILES=... dtbs_check`: **exit 0** but **243 diagnostic lines about three unrelated Tegra boards**, not Xoom. Don't claim globally warning-free.
- `dt-validate -l arm/tegra.yaml` for **compiled Wingray and compiled Stingray**: **both PASS, exit 0, zero diagnostics**.
- Broad all-schema validation of untouched upstream Wingray versus new refactor: **66 diagnostic lines each**, identical multiset after normalizing paths. These are inherited issues (panel, regulator, keys, etc.), not introduced by the refactor.

M1 schema subchecks are **[x]**, but M1 overall remains **[ ]**.

## 6. Historical 2.4/5 GHz/r7 research (use selectively, do not resume automatically)

- Older MZ600 successfully ran Linux 7 Debian p10 and generic BCM4329 firmware 4.220.48 with connected 2.4 GHz Wi-Fi. This is *historical working evidence*, not a clean RFC test.
- Original Motorola May2012 BCM4329 firmware 4.218.248.44 exposed both 2.4 and 5 GHz and returned a real legacy `WLC_GET_VALID_CHANNELS` channel list; generic firmware under the same NVRAM exposed only 2.4. Both read `country=US/US/regrev0`; **don't assume US69** is a fix for 5 GHz.
- Six read-only OEM `per_chan_info` ABI variants returned native Broadcom **`BCME_UNSUPPORTED=-23`**; Linux mapped it to `-EBADE=-52`. Other native errors such as **`BCME_NOTUP=-4`** can map to the same Linux errno, so `-EBADE` alone is *not* proof of unsupported firmware API. Use raw native error provenance for a fallback if necessary.
- Historical r7 full nine-patch `zImage dtbs modules` ARM build passed, with **259/259 imported symbol CRC** matching the original and WCC module byte identity; two host test harnesses executed **19/19 exact source-extracted C cases** with ASAN/UBSAN. This validates parts of r7, but **neither the physical new RFC nor full 5 GHz regulatory safety**.
- Prior proposed last-known firmware restriction cache, generation checks and background retry were deliberately **deferred**, since a true initial 2.4 GHz failure requiring them has not been demonstrated. Old r7 is fully preserved for future comment-driven revision.
- Linux 3.2 originally supported BCM4329 within Broadcom `brcmfmac` FullMAC/SDIO architecture; use accepted patterns, not a brand-new driver.

## 7. Issue traceability and safety policy

**Owner requires every patch amendment be logged on its owning GitHub issue** with old/new SHA and patch identity, exact functions and behavior, evidence and reasons, alternatives, test status (static, build, real physical separated), limitations and reproducible rollback. Add a **separate follow-up after actual build/physical verification**. Do not claim a prior pass is a new result; do not fabricate DCO/author sign-off. Relevant issues: **M1 #17**, old **DT #10**, Wi-Fi **#4**. Create more precise issues as other logical problems emerge.

**Do not flash or alter running MZ600 without explicit scoped authorization and independent rollback.** Protect existing p10 Debian, kernel, wireless firmware/NVRAM, MAC identity, boot/recovery/USB and known-good connection. Do not power or initialize unsupported cellular modems. Existing USB gadget COM9 path on Surface Book 2 is an important recovery interface; don't disable it as a byproduct of retiring CDMA. Earlier physical tests were on an original working image; new RFC remains untested live.

## 8. Remote tools and standard processes

- Connected Desktop Commander machine **DESKTOP-R16QJD4** (Windows with WSL `Ubuntu-22.04`) is the source/build host. **SURFACE-BOOK-2** is historically the COM9 USB console host. Discover current tool and device IDs using `functions.exec`, `ALL_TOOLS` and `tools.mcp__Remote_Desktop_Commander__list_devices({})`; don't rely on cached device ID or suppose the device is currently running the prior state.
- Connected GitHub tools: `tools.mcp__GitHub__fetch_file`, `create_file`, `update_file` (current blob SHA required), `add_comment_to_issue` (issue number passed as `pr_number`), `fetch_issue`. Prefer them for native project docs. Repo is `Olsens11/XoomLinux7`.
- Remote WSL execution: write a standalone shell script on Desktop at `C:\Users\olsen\xoom-linux-rom\inspection\script.sh` with Desktop Commander `write_file`; invoke `start_process` with `wsl.exe -d Ubuntu-22.04 -- bash /mnt/c/Users/olsen/xoom-linux-rom/inspection/script.sh`, read via `read_process_output`. Avoid fragile nested `bash -lc` quoting with `$` and parentheses.
- Before writing, check Git status/HEAD for local **metadata**, **clean source**, **M1 study** and old r7 separately. Local project metadata was last observed at `c2e4df9f4020aa6c6587fe08c14b76950dfe4058`; it can lag GitHub. `git fetch` then `git merge --ff-only` for the docs branch, never force reset.
- Use isolated worktrees and O= build directories. Schema venv already installed. Keep source/config/output hashes. Respect process's tenets: upstream style, one logical issue per patch, no unrelated refactor, no private firmware or credentials in public GitHub, no new country SET or RF tests without necessity.

## 9. Exact next steps for the next conversation

1. **Read the milestone tracker and issue #17 latest comments**. Acknowledge **M0 complete / M1 active** and the **final no-CDMA/no-LTE** decision. Do not ask the owner to revisit this decision.
2. **Read-only OEM/primary-source comparison** of MZ600 vs MZ604 **only insofar as it impacts Wi-Fi/SDIO, USB gadget COM serial, shared regulators/GPIO, and board identity**. Distinguish historical `stingray_cdma` and LTE labels. Confirm which USB role/power/reset properties should be represented. Don't open a 3G/4G project.
3. **Review the existing minimal three study commits** for upstream elegance: common `.dtsi` versus alternatives, binding correctness, meaningful commit messages, MAINTAINERS warnings. The parity evidence suggests the existing approach is sound; do not rewrite just to make it look different. Amend an isolated study commit only if a genuine improvement is supported and log it immediately in issue #17 with rollback.
4. On any amendment rerun `git diff --check`, copy-aware patch/diff checks, ARM DT builds, original-versus-refactored Wingray semantic equivalence and targeted dtschema/`dtbs_check`; preserve exact errors versus inherited unrelated warnings. Keep milestone boxes synced to real evidence.
5. **Prepare a controlled, non-destructive MZ600 physical test plan** (USB gadget console, SDIO, safe power, boot) and optional MZ604 regression; protect old p10 boot and avoid modem initialization. Do not flash spontaneously. Obtain user approval for physical operations if needed.
6. **Promote the M1 proof into pristine RFC kernel source only when evidence supports that exact patch series**, then log resulting SHAs/rollback and eventually close M1 only after real required hardware testing. Start M2 afterwards.

**Resume prompt:** "Continue the XoomLinux7 clean-sheet minimum 2.4 GHz BCM4329 RFC from the 2026-10-29 comprehensive handoff. M0 is complete, M1 remains open. Audit only relevant MZ600/Wingray USB gadget, BCM4329 SDIO/power and board-identification differences, excluding all CDMA/3G/LTE support and modem initialization. Preserve the clean upstream source and the three unaccepted M1 study commits until a justified change is proven, then update issue #17 and the milestone tracker."

## 10. Immutable checkpoints and rollback

- Pristine RFC kernel: **`2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`**, zero new patches.
- M1 draft: **`0d4d7d3161b6ed9595f2cf28200535d59dcb3e0f`**, three logical unaccepted commits listed above.
- r7 historical nine-patch: **`c0fe77938192a33f186998b335892e70793ea826`**, separate read-only baseline.
- M1 Stingray DTB: **`c70d22c06efa3607f132027588c6c6cd34518a4c1e1dff83c125cfa25409f5aa`**, 61,076 bytes.
- **No new Xoom kernel/firmware/radio or boot changes occurred in M1**; no physical rollback is needed for source/schema work. For source-only rollback select pinned upstream clean worktree; archived draft patches and prior r7 remain preserved.

**Concluding directive:** Continue on the new, simple and reviewable 2.4 GHz Wi-Fi foundation. Treat M1 schema proof as done, but real MZ600 USB gadget/BCM4329 SDIO board correctness as still to be verified. **Avoid all cellular support and never confuse USB gadget serial with a modem USB host dependency.**