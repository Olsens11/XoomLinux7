## 2026-10-26 upstream patch hygiene — one logical, bisectable change per commit

The owner explicitly confirmed the **Linux kernel norm: one logical change per patch**, not one file or one function per patch. A patch may modify several files when they together implement one independently understandable, testable change. Conversely, do not mix unrelated firmware compatibility, Motorola board regulators, BT power sequencing, Debian services, or logging into a single change. **Every intermediate commit must compile and remain operational (bisectable).**

For **`wifi: brcmfmac` legacy BCM4329 firmware compatibility**, use existing feature/quirk detection, not scattered hardcoded Xoom branches. Candidate independently coherent boundaries: (A) capability probing and error handling, without visible behavior change; (B) tightly bounded legacy firmware channel-list support with cfg80211/regulatory protections and modern-firmware regression tests; (C) a *complete* legacy scan request+results+completion+abort/timeout integration in a single bisectable commit or safely staged internal helper commits; (D) dedicated parser/lifecycle KUnit regression tests and documentation when these form meaningful reviewable units. Patch C must never expose a `.scan` path that can queue requests without eventual completion. Adjust split for maintainers' feedback rather than targeting an arbitrary number of commits.

Do not send the physical lab diagnostic / v05 fallback as if it were a clean upstream patch: remove hardware-test printk instrumentation and correct `checkpatch.pl` failures, prove bounded parsing/no memory-corruption risks, exactly-once cfg80211 completion, regulatory compliance and multi-model behavior. Keep **whole-chip U4/I7/U0/U2/LPO / device-tree / MMC quirk** as separate logically scoped subsystem series with its own test gates; connect dependencies through a cover letter and correct base tree. Upstream base and `MAINTAINERS` routing must be refreshed at the time of submission, and genuine DCO `Signed-off-by` requires the human author's approval. **No upstream submission currently authorized.**


### G4 dual-band lab PHY support succeeded, scan and release gates remain OPEN/PENDING

[Physical MZ600 5GHz wiphy and failed escan scan checkpoint](../checkpoints/MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md): Original matched Motorola HRI39 firmware returns actual WLC_GET_VALID_CHANNELS 20 entries including 9 for 5GHz. Board-scoped Linux7 v05 fallback ABI compiled/physically tested; `wlan0`+5GHz channels present and `NO_IR` for every enabled channel. **This fulfills a preliminary enum/wiphy acceptance subgate only.** 5GHz passive-only scan on ch36/40/44/48 failed at `brcmf_run_escan: -52`, no BSS; cannot claim whole Wi-Fi functional. Next code track must safely implement legacy scan state/result handling, preserve no-IR and world/regulatory restrictions, scan timeout/cancel, firmware/staging confidentiality, and retest original generic 2G plus Bluetooth. Multi-unit Xoom MZ600/MZ602/MZ604, cold/warm and WLAN+BT concurrent physical tests and owner explicit permission **still required before upstream review**. Lab binary not a production deliverable.



### 2026-10-26 owner-performed negative OEM US/69 bootstrap A/B

[Physical owner COM9 A/B](../checkpoints/MZ600_V064_OEM_US69_BOOTSTRAP_NVRAM_A_B_PHY5GHZ_UNCHANGED_OWNER_PHYSICAL_2026-10-26.md) verified Motorola original country/rev `US/69` in NVRAM prior to current firmware startup, but current generic firmware still reported only 2G (11 chanspecs). Reverted cleanly. Do **not** count this as G4 5GHz pass or evidence of country readback; firmware might ignore/translate override. Additional one-variable OEM firmware-vs-generic study is required; no forced channels or regulatory workaround. Preserve the working 2GHz scan and full-chip multi-device qualification gates.

# Linux 7 BCM4329 whole-chip patch series — multi-device engineering and review gates

**Decided with owner:** 2026-10-26. **Status:** development/test policy and roadmap, **not upstream-submitted and not a claim of compatibility**. The goal is a polished, reproducible and useful Linux patch series that first serves our own Xoom restoration effort and can *later* make a meaningful community contribution after rigorous **physical testing on multiple devices**.

**Source anchor:** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; project branch `wip/clean-wifi-bt-usb-20261025`. Full-chip integration: [ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md); [OEM shared-chip design](../research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md). **No patch submission, DCO signoff, external contact or assumption of upstream acceptance without owner's explicit direction.**

## Deliverables — useful to us before reviewers see them

1. **Small ordered patch series:** prerequisite Motorola factory ATAG→FDT MAC bridge, clean board DTS/bindings, shared BCM4329 regulator/clock target provider, separately wired MMC WLAN and UART Bluetooth consumers, fixups only if real matched A/B evidence requires them. A patch should have one clear rationale and be independently reviewable. Do not bury host scripts, firmware blobs, or Debian `dbus` packaging in kernel commits.
2. **Versioned own-use branch and artifact manifests:** pin upstream commit, complete source diff/series order, config, toolchain, output `zImage`/`dtb`/`.ko` SHA256, module `vermagic`/modversions, firmware provenance without publishing binaries, serial trace version, and per-target board-compatible IDs. Embed/ship only firmware with suitable permission; no OEM keys or personal identifiers.
3. **Self-service build/test tooling:** a documented one-command **offline** build + lint/DT schema/tests, followed by a separately guarded **operator-initiated** deploy of a *temporary* image. Tools must not guess COM ports, target identity, boot partition, or reset sequence. Script should support a `--dry-run`/inventory mode and stable private capture paths, with resume/checkpoint instead of repeated flashing.
4. **Own-use installation/upgrades/rollback:** keep known-good on-device kernel and TWRP, prefer RAM-only `fastboot boot` and USB console for uncertain chip-state patches, use atomic versioned module trees, avoid clobbering old ABI data. Normal permanent upgrade only after controlled repeated boot/shutdown/recovery tests.
5. **Release documentation and engineering story:** describe OEM rationale, datasheet constraints, pin ownership, Linux APIs, kernel commit scope, identity/privacy requirements, remaining gaps, license compatibility, verified results and honest limitations. Publish tests (redacted) with exact kernel/board/firmware state and dates.

## Physical device matrix — never infer results across machines

The owner's experimental replacement **MZ600** is currently the sole stable **internal Debian p8 + COM9 + 114 ABI-exact modules** verified baseline. Separate hardware owned or being assembled includes **MZ604 Wi-Fi (three units)**, **MZ602 Verizon 3G (two units)**, and **MZ617 Xyboard 4G (two units)**. These counts are a planning inventory, not a claim any other unit was booted or has the same power schematic, BCM chip revision, bootloader, touch/display controller, or pin assignments. MZ617 is **out-of-scope unless independent board/SoC/BCM4329 compatibility is demonstrated**; do not include it as an automatic Xoom/Stingray test target.

| Device | Known-use role | Required inventory before selecting DTS or radio patch | Evidence as of 2026-10-26 |
| --- | --- | --- | --- |
| Experimental **MZ600** | Reference engineering and instrumented baseline | Product/bootloader, `compatible`/machine DT, Wi-Fi SDIO tuple/revision, BT UART, supply/reset pinmux, OEM regulatory calibration, boot/USB console, pstore and safe recovery | **Linux 7 Debian internal p8, modules 114 PASS**; current release's live Wi-Fi still to be tested; previous temporary v06.x `wlan0` PASS |
| Additional **MZ602** | Cellular-model cross-variant test | Independently capture board DTS, CPU/PMIC/pins, combo chip identity and firmware; confirm eMMC layouts and cellular/regulatory coexistence | **Not tested on this patch series** |
| Additional **MZ604** | Wi-Fi-only model cross-variant test | Independently capture Wi-Fi/BT chip revision, rails, pin mux and clocks, original MAC and regional calibration, panel/touch variant | **Not tested on this patch series** |
| **MZ617 Xyboard** | Potentially useful future comparator, **NOT assumed compatible** | First identify SoC, board, radio chip, boot scheme, recovery and datasheets. Only include if evidence supports compatible drivers | **Not in validated target matrix** |

An owner-protected original Xoom running the TWRP Toolkit is a **reference only** and may not be used as a destructive test target. Record **each physical unit under a privacy-safe local ID**, NOT IMEI/serial/full MAC in public GitHub. Do not assume all Stingray variants require MZ600-only country `US-US-69`; use own factory region/calibration for each.

## Mandatory stage gates

| Gate | Offline or physical proof | When to advance |
| --- | --- | --- |
| G0 — Source and semantics | Clean rebase on pinned Linux 7, enumerate Kconfig/protocol consumers; compare Motorola OEM+BCM4329 datasheet; pin U4/I7/U0/U2 ownership, LPO and reset gating, independent regulator references | No unexplained double claim, no heuristic hardcoded MAC/regulatory or generic behavior regressions |
| G1 — Deterministic offline CI | `git diff --check`, `git apply --check` on clean tree, `checkpatch.pl` and bindings checks, build `ARCH=arm` no-NEON, module ABI/ELF version audit, software fault model, offline artifacts hashed | Every staged change has clean build and diff provenance; checkpatch/DCO issues listed honestly |
| G2 — MZ600 non-radio baseline | RAM-only exact-hash image, correct hardware target, serial responsiveness, console watchdog, read-only GPIO/regulator/pinctrl ownership, stable MMC2 SDIO/USB/power | Boot+shutdown+recovery repeatable; unchanged p7/eMMC verified; no automatic RF scan |
| G3 — MZ600 whole-chip lifecycle | Individual WLAN and HCI start/stop, shared LPO/U4 vote traces, U2/U0 resets and I7 state, no firmware F2 error, factory identity matches protected per-unit reference, recoverable teardown | Repeatable normal/cold/warm sequences with **no COM9/red-LED regressions**; genuine internal-regulator-off status only if independently measured |
| G4 — Concurrency/regulatory/long-run | Wi-Fi and Bluetooth simultaneously, bounded roam/BT reconnection, suspend/wake, device-family regulatory intersection and signed db/country acceptance, measured battery/power where possible | No power leak, unsafe RF changes, Bluetooth regression, driver unload hang or USB disconnect; errors captured |
| G5 — Other Xoom variant A/B | Reproduce same G0–G4 per independently inventoried **MZ602 and MZ604** with a matched stock/OEM or previously known-good baseline and one variable per trial | Actual physical pass evidence from **multiple individual devices and at least two distinct validated variant models**; a single cross-variant run is insufficient to call it broadly stable |
| G6 — Own-use candidate/release | Versioned installer and rollback, private secrets separate, documentation updated, exact supported-device list, unsupported-model guard and repeatability checklist | Workable for ongoing self-maintained installations and tests, not merely a lab proof |
| G7 — Upstream review candidate | Split minimal kernel commits, bindings and maintainer scope, standards/legal/license review, actual author DCO, reproducible testing evidence/cover letter | **Only after owner explicitly requests submission**; no rushed RFC merely because one MZ600 boots |

Record hard failures too: missing COM9, red LED, driver/module busy, F2 `-62`, missing D-Bus userspace, Wi-Fi firmware country rejection, BT HCI patch mismatch and failed safe unload. The diagnostic failure matrix should distinguish kernel patch defects, incomplete board DTS, userspace packaging, external firmware, and hardware-specific faults.

## Daily test record format

For every physical test log: timestamp/time zone; private anonymized unit ID; model and independent identity check; exact boot/kernel/dtb/module/firmware hashes; serial tool version and commands; baseline state and prior WLAN/BT wake history; read-only pin/regulator/LPO/F2/SDIO/host controller observations; load and unload reference counts; radio legal constraints; result and negative evidence; postcondition and rollback; explicit `kernel patch?`, `board variant DTS?`, `lab tool?`, `Debian package?`, `proprietary firmware?` disposition; link to patch/issue without publishing identifiers.

Add a new checkpoint, update [whole-chip integration ledger](../research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md), current handoff, runtime env and status after each milestone. **Physical testing on other devices has not begun.**


### Current installed Debian WLAN lifecycle caveat

The actual MZ600 factory-MAC guarded `mz600-wlan.service` contains `ExecStart` with WCC then brcmfmac load, `RemainAfterExit=yes`, **no `ExecStop`**. A one-shot unit stop is **not** proof of modules unloaded or shared chip reset. Before G3 field tests, build an independently supervised **reversible WLAN start/stop diagnostic**, explicitly unload WCC→brcmfmac→brcmutil, preserve serial and the ability to recover from power-state hangs; test only with operator near device or a separately qualified recovery method. Continue to isolate changes to Debian service scripts from upstream kernel patches.


### 5GHz must pass before self-use multi-variant release

Owner confirms original Android associated to a 5GHz AP on this same board. Linux7 current generic BCM4329 firmware/NVRAM advertises **zero 5GHz channels**, though `aa5g=1` and 5GHz PA keys exist in the NVRAM and 2.4GHz scanning works. [Physical negative checkpoint](../checkpoints/MZ600_V064_5GHZ_BAND_NOT_ADVERTISED_PASSIVE_SCAN_BLOCKED_PHYSICAL_2026-10-26.md) records clean safe unload and no 5GHz RF scan. **Added future G4 acceptance:** proof of actual per-unit firmware `BRCMF_C_GET_BANDLIST` 5GHz presence, valid supported low channels/regulatory constraints, successful passive scan and reversible teardown. Follow OEM firmware/NVRAM compatibility and kernel bandlist/chanspecs logic, not a DT or regdb hack. Repeat once MZ602/MZ604 capabilities independently inventoried; do not assume 5GHz on every hardware variant or use MZ600 calibration on others.

## Immediate development priority

### Original 2a65edc Bluetooth first/last initialization order must be qualified

The matching original Motorola BT rfkill source is now recovered; [51/51 pinned source/ELF audit](../checkpoints/MZ600_OEM_2A65EDC_BLUETOOTH_WLAN_SHARED_U4_51CHECK_SOURCE_AUDIT_2026-10-26.md) shows BT probe calls BLOCK before rfkill allocation, releasing an *untyped* shared-U4 count that could already contain a WLAN vote if BT driver binds late. Linux7 owner model must reject BT release without actual BT-acquired reference (host-only regression added). Future own-use and multi-device acceptance must deliberately exercise **WLAN-first BT-late, BT-first WLAN-late, BT blocked/unblocked with WLAN active, failed BT bind/unwind, WLAN unload with BT awake, and warm/cold recovery**, including U4/I7/U0/U2/LPO event traces and no duplicate GPIO owner. Do not assert this race happened in OEM; do not submit until measured and owner authorizes.



### Original OEM compiled-branch and full-lifecycle acceptance

Reproducible [Motorola early 2.6.36 source+ELF lifecycle auditor](../../tools/forensics/audit_mz600_oem_system_lifecycle.py) is now **42/42 PASS** with exact original HRI39 binary. [Evidence](../checkpoints/MZ600_OEM_2A65EDC_CROSSLAYER_SOURCE_BINARY_CONDITIONAL_AUDIT_42_PASS_2026-10-26.md). New mandatory comparisons: platform control (CUSTOMER_HW2 and CONFIG_WIFI_CONTROL_FUNC compiled), **no artificial second generic U4 vote**, staged Wi-Fi power/carddetect and reverse order on remove, early suspend firmware settings vs no-op platform PM, runtime dongle reset, OEM SDMMC2 tap=6 already in Linux7 DTS, per-unit regulatory calibration, and Bluetooth/source-generation uncertainty. A source check is not physical acceptance. Any final 5GHz fix and full-chip pwrseq implementation require independent multi-unit WLAN/BT plus suspend/recovery tests; preserve later 2011 vs original 2a65edc vendor provenance boundaries.



### OEM SDIO quirk cannot be evaluated in isolation

The [cross-layer Motorola OEM workaround audit](../research/MZ600_BCM4329_MOTOROLA_OEM_WORKAROUND_CROSS_LAYER_SYSTEM_AUDIT_2026-10-26.md) identifies the 6-field embedded SDIO override as a real workaround, but physical v018 proves it alone altered host high-speed timing while still failing F2. Earlier v044 and v045 proved additional firmware bootstrap identity and WCC packaging dependencies. **Own-use/preview gate:** record matching OEM 2.6.36 firmware+calibration+platform compile conditions, board U4/U2/I7/LPO state, carddetect, PMU and pulls, SDIO six fields, F2, actual country and 5GHz bandlist. Test scoped CCCR changes versus current reference in an A/B with one independently measurable variable, then BT/SDIO coexistence and multiple device types before a candidate quirk may join the upstream series. Full-chip provider, MMC quirk and firmware-userland assets remain separate changes.



### New firmware-bandlist gate grounded by physical 5GHz diagnosis

On reference MZ600 Debian Linux7 p8, the RAM-only diagnostic physically measured **firmware `GET_BANDLIST count=1, band=2G`; `chanspecs total=11, 2G=11, 5G=0`** while Android previously connected to 5GHz with this same hardware. See [actual Xoom checkpoint](../checkpoints/MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md). **Do not credit this as 5GHz working or as a whole-chip kernel patch pass.** A device-appropriate 5GHz restoration must show a genuine firmware-provided band/channel list, legal regulatory and verified per-unit calibration, PHY advertisement, passive scan, and correct unload, first on MZ600 and independently per eligible MZ602/MZ604 unit. Preserve known-good 2G baseline and do not inject synthetic channels, wrong factory calibration or arbitrary country codes. Diagnostic source kept separate from upstream candidate power sequencing patches.


### 2026-10-26 newly proved own-use installed WLAN reference

Current reference MZ600 Debian p8 Linux 7 has now physically completed a one-shot standard-driver WCC→`wlan0`→passive 2.4GHz scan with **19 BSS**→reverse-order full driver unload, **no reboot or lost COM9**. Unexpected 2442 MHz BSS metadata despite channels 1/6/11 filter is a future diagnostics gate (must test cache/reporting versus actual scan; don't assume prohibited scan). [Physical baseline](../checkpoints/MZ600_V064_PERSISTENT_DEBIAN_BCM4329_WLAN0_PASSIVE_SCAN_AND_ORDERED_TEARDOWN_PHYSICAL_PASS_2026-10-26.md). **Keep this separate from G3/G5 whole-chip provider series qualification**, which remains pending independent ARM build, binding, hardware trace and multi-device tests. Reuse the guarded start/scan/unload protocol for future *validated* patch A/B; avoid unnecessary repeat of this same no-patch success.



Continue current **MZ600** without touching verified p7/GPT: validate D-Bus daemon package deficiency and eventually restore signed Debian packages; conduct guarded module lifecycle test only after stable USB/recovery gate, then use **actual** Xoom live results to refine shared-chip kernel source. Start an independent hardware inventory worksheet for MZ602/MZ604 **before** proposing a universal DTS or regulator/pin configuration. Keep a comprehensible `patches/upstream/rfc/series` and change log of tested versus merely compiled patches.
