# Clean-sheet BCM4329 / Motorola Xoom Linux 7 — minimum functional 2.4 GHz RFC

**2026-10-29 | Independent RFC development line | DESIGN AND BASELINE ONLY**
**Source patches applied: 0. No hardware operations, new firmware, module loading, or regulatory changes.**

## Intent

Implement the *smallest complete, correct* BCM4329 Wi-Fi integration that makes ordinary **2.4 GHz client connectivity** usable through the **existing Linux 7 `brcmfmac` / `cfg80211` architecture** on the Motorola Xoom MZ600. We are rebuilding the solution **from the pinned upstream source**, not trying to slim down, cherry-pick or revert the previous r7 experimental implementation. The earlier research and patches are a **reference library**, not the source tree into which we continue committing.

The central upstream strategy is to get a **functional, verifiable foundation into RFC review**, so maintainers can shape the initial architecture *before* we add 5 GHz, Bluetooth/FM or unusual recovery mechanisms. RFC review is **not** merge acceptance.

## Source-of-truth boundaries

| Purpose | Location / identity |
| --- | --- |
| New independent project branch | `rfc/bcm4329-minimal-2ghz-20261029` |
| New desktop WSL Linux-source worktree | `/home/xoomdev/xoom-linux-rom/rfc-bcm4329-minimal-2ghz-20261029` |
| Exactly pinned upstream source HEAD, **zero RFC patches** | `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (`xoom-linux/linux` Linux 7 development) |
| Prior research and code (reference, **unchanged**) | `wip/clean-wifi-bt-usb-20261025`, `patches/upstream/review-wifi-four-logical-20261029-r7/`, nine-member source tip `c0fe77938192a33f186998b335892e70793ea826` |
| Prior WIFI-01 research issue and rollback ledger | [issue #4](https://github.com/Olsens11/XoomLinux7/issues/4) |
| Owner-approved initial RFC scope | [minimum functional scope decision](../../plans/MZ600_BCM4329_MINIMUM_FUNCTIONAL_2GHZ_UPSTREAM_RFC_SCOPE_2026-10-29.md) |

**Important nuance:** This *project-documentation* Git branch starts from the latest internal project history so the evidence and process rules remain accessible. The **Linux source worktree** is separate, freshly checked out at the upstream SHA and has **no inherited patch commits**. Never conflate those two branches or claim the project-documentation branch is an upstream-clean Linux kernel tree.

## Findings from actual pinned Linux 7 source (not assumptions)

1. **Chip protocol foundation already exists.** `drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c` already contains `BRCMF_FW_ENTRY(BRCM_CC_4329_CHIP_ID, ..., 4329)`. `chip.c` contains BCM4329 SoC details; there is no justification for a new BCM4329 SDIO driver.
2. **Standard STA plumbing already exists.** `cfg80211.c` implements `brcmf_cfg80211_scan()`, `brcmf_cfg80211_connect()`, `brcmf_setup_wiphybands()`, country notifier, ESCAN events and standard Linux WLAN operations.
3. **Legacy channel mismatch is a narrow compatibility seam.** `brcmf_construct_chaninfo()` requires firmware `chanspecs`; historical actual OEM 2012 radio supports `BRCMF_C_GET_VALID_CHANNELS` but rejects newer per-channel metadata. We should **not infer** that every normalized `-EBADE` is a native unsupported feature. Read the true firmware status or use an equivalently authoritative capability check.
4. **Base Linux source includes Wingray, not MZ600 Stingray DTS.** Pinned `arch/arm/boot/dts/nvidia` contains `tegra20-motorola-wingray.dts`. There is **no** `tegra20-motorola-stingray.dts` in the fresh base. An appropriately scoped *board variant* implementation is required before claiming this source boots MZ600.
5. **Regulatory ownership is already established.** `brcmf_cfg80211_attach()` applies `brcmf_regdom`, calls `wiphy_register()` and **then** `brcmf_setup_wiphybands()`. `cfg80211` records `orig_flags` at registration. Do **not** make mutable country-current `GET_VALID_CHANNELS` results permanent hardware limits or remove existing legal restrictions.
6. **The prior BigPart partition patch is not BCM4329.** Our test Linux installation may rely on a BigPart kernel configuration, but that is **not** automatically a Wi-Fi/BCM4329 upstream patch dependency. Keep build/deployment adaptations separate from the wireless RFC and disclose true test dependencies.
7. **Historical evidence is not new RFC acceptance.** A previous exact-nine implementation demonstrated connected 2.4GHz WPA/DHCP on the replacement MZ600 with generic firmware `4.220.48`. Repeated fresh scanning was *not* proved in the formal Oct 28 read-only audit. The OEM 2012 `4.218.248.44` exposes 5GHz but its safe active/regulatory operation remains unproved. These are useful prior measurements, **not** a fresh clean-RFC physical PASS.

## Initial user-facing functionality

The clean RFC must, on actual Xoom hardware, **automatically** bring up `wlan0` at normal boot; perform repeated **fresh** 2.4GHz scans; connect through NetworkManager or `wpa_supplicant` using a supported WPA2 AP; obtain DHCP and transfer data; disconnect, reconnect and survive an ordinary restart without diagnostic/manual interventions. No special user-space protocol or separate BCM4329 driver.

**Intentionally unresolved:** full 5GHz active/passive/DFS/client support, firmware-generation caches, worker-based retries, rare regulatory failure recovery, station telemetry extras, Bluetooth and FM. We may discuss them in the RFC as explicit questions and follow-up tasks, not claim they work.

### Regulatory safety is a release gate, not optional polish

- Intersect **current firmware allowed-channel information**, existing hardware/board limits and the effective `cfg80211`/regdb rules. Never invent region/revision, radar/passive metadata, channel support or transmit power.
- For the initial **2.4GHz-only** candidate, **do not allow any unverified 5GHz transmissions**. `NO_IR` alone does **not** prohibit all STA transmissions. Determine a minimal, testable implementation that does not **advertise or operate** an unqualified 5GHz band on the selected legacy firmware, *without breaking other Broadcom chips or modern BCM4329 firmware*. This is a **design/test gate**, not something already implemented by this document.
- Preserve legitimate country-dependent changes without freezing one country's channel inventory into `orig_flags`. Confirm that the per-PHY custom `99` domain and actual firmware country/tx power behavior are appropriately constrained; global `iw reg get` reporting US is **not** sufficient by itself.
- Until these checks pass on the *new* build, treat the clean RFC as a work-in-progress rather than a regulator-safe usable driver.

## Clean architecture: what new work must actually justify

**A. Board representation (its own logical issues).** Support the MZ600 Stingray variant using upstream Tegra/Motorola DTS/bindings, sharing hardware correctly with Wingray; maintain real chip power/reset/SDIO behavior. Respect per-device MAC identity if the vendor ATAG is the required unique source. Do not copy 1700 lines into a new variant without checking whether shared DTSI structure is appropriate. Track binding, common board refactor, variant support and ATAG as separate logical upstream changes **only if each is actually needed**.

**B. Legacy 2.4GHz channel compatibility (WIFI-01 issue #4).** Reuse existing `brcmfmac` firmware I/O; a **small, bounded, BCM4329/firmware-specific** adapter can translate currently valid **2.4GHz** channels from legacy `WLC_GET_VALID_CHANNELS` when `chanspecs` is genuinely unsupported. Do not replicate the modern channel parser or grow an independent regulatory engine. Keep established modern chips and firmware untouched. Ensure failure cannot unexpectedly grant permissions. Hold 5GHz outside initial supported operation.

**C. Scan lifecycle (separate owning issue(s)).** Prefer the simplest existing `cfg80211` scan operation and actual firmware's supported terminal protocol. Test 2–3 consecutive scans plus cancellations/disconnect/reconnect. **Only** introduce generation IDs, special Event69 handling, state-ready transitions or legacy iscan polling if direct evidence proves they are necessary for the chosen initial firmware and cannot be solved with existing kernel mechanisms. Prior WIFI-02/03/04 are **diagnostic references**, not default imports.

**D. Initial review/build packaging.** Full source/DT compile, original-upstream-relative patch boundaries, DCO only from actual human authors, no proprietary firmware/NVRAM or private MAC/SSID/serial/IP in public repository. Include precise physical test matrix and evidence for every claimed function. Use existing project [issue-linked amendment/rollback workflow](../../process/DEVELOPMENT_WORKFLOW.md).

**E. Do not couple Wi-Fi to unrelated kernel storage/boot artifacts.** Local Linux root or BigPart may be needed for a specific device trial; disclose it in the test harness, but do not fold it into the wireless series or imply reviewers must accept it to consider the radio code.

## First engineering sequence (NO PATCH YET)

1. Run a **clean-source interface audit** against pinned Linux 7 and historical physically tested firmware. Produce a table: upstream feature available? exact missing behavior? evidence? minimum code seam? isolated issue? test that proves the fix.
2. Choose a 2.4GHz reference firmware with **actual prior normal connected baseline** (generic `4.220.48`), and explicitly isolate original OEM `4.218.248.44` as later dual-band compatibility testing. Neither proprietary firmware binary is included in Git.
3. Build the **first small logical change** from scratch, review `git diff`, and append a precise issue comment recording the new behavior and baseline/rollback. Avoid cherry-picking prior r7 patch files; if any old technique is reused, independently explain why it is still the smallest correct interface adaptation.
4. Independently test the minimal source then build, before proposing a controlled **owner-authorized**, temporary and independently rolled-back physical trial. Existing working p10 Linux, recovery and original firmware are protected.
5. Only after this candidate demonstrates new real 2.4GHz boot/scan/connect behavior, prepare a reviewable RFC to the maintainers with explicit **unresolved 5GHz regulatory** and optional recovery questions. Do not claim maintainer approval or send externally without owner instruction.

**Decision rule:** *Does the proposed line make ordinary 2.4GHz Wi-Fi operate through existing interfaces, preserve legal restrictions, and solve a demonstrated problem?* If not, it stays in the research backlog.

## Stop/rollback contract

Previous r7, r6, earlier QA and the owner's installed Xoom are untouched. This new source worktree can be discarded at any time without reverting a kernel or affecting the protected baseline. For every new patch, record exact upstream parent SHA, new commit, changed behavior, source and physical tests (or clearly not run), a rollback command/selection, and limits **on the relevant issue** as soon as it exists. A second validation comment follows after actual tests. This README is scope/architecture only and is **not a patch submission**.
