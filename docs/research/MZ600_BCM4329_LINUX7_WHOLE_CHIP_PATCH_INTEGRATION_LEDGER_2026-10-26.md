# MZ600 Linux 7 BCM4329 — whole-chip kernel patch integration ledger

**Updated:** 2026-10-26, following successful internal-p8 installation of all 114 ABI-exact Linux `7.0.0-next-20260422+` modules and read-only USB diagnostics. **Explicit user priority:** carry each material discovery from ordinary Debian bring-up into the longer-term **whole BCM4329 combination-chip** upstream-compatible kernel design. This file is the current integration tracker, **not** a claim that the whole-chip provider has been built, deployed or tested.

**Canonical upstream source:** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; repo active branch `wip/clean-wifi-bt-usb-20261025`. Track author-ready kernel commits separately from lab userspace, private firmware and Debian fixes.

## Physical subsystem contract — preserve each owner

The board has shared BCM4329 PMU/power and clock dependencies but separate WLAN SDIO (`mmc2`) and Bluetooth UART/HCI functions. Use a **single chip physical-resource owner / refcounted votes** rather than two independent GPIO owners or a monolithic replacement for generic `brcmfmac` and `hci_bcm`.

- **U4 shared rail/power vote:** Motorola OEM has a protected, two-consumer shared `change_power_brcm_4329()` count; Linux DTS currently models U4 as fixed `vdd_wifi` regulator. A future provider must **consume the existing regulator** (or migrate its GPIO ownership), never request U4 twice.
- **I7 / BT_REG_ON or shutdown:** Broadcom shared internal regulators are OR-enabled by WLAN/BT inputs. OEM sets BT_SHUTDOWN GPIO I7 low in both rfkill callback branches, but past read-only `get_direction=-EINVAL` does not prove physical pin voltage. Must inspect pinctrl and owner; cannot directly drive I7 if `hci_bcm` owns it.
- **U2 WLAN reset** belongs to MMC pwrseq; **U0 BT reset** to HCI; U1/U6 wake have separate states. Coordinated reset must not duplicate existing ownership. Internal POR/full regulator-off is **not proven** by a software driver unload or a U2 reset.
- **32.768 kHz LPO** is shared. Past BT `txco` label resolved to that same low-frequency clock; v032 compile-only preview uses proper `lpo` role. Do not assume it represents the 38.4 MHz normal crystal/reference.
- **Power sequence gates:** observe supply stable time, LPO enable and reset release on a shared monotonic trace, per BCM4329 datasheet. Bluetooth register states, WLAN reset and MMC2 host clocks are part of the same test contract. Never combine clock, regulator, and SDIO CCCR timing changes in one A/B.
- **F2 diagnostics:** earlier v025 F2 `-62` is a historically verified failure on *that candidate*, not the status of current upstream-based v06.x, which physically brought up `wlan0`. No assumption that earlier unqualified whole-chip theory caused or fixed later initialization.

## Kernel patch inventory and gate status

| Kernel topic | Canonical local asset | Evidence and integration status | Next gate |
| --- | --- | --- | --- |
| Unique WLAN MAC from Motorola boot ATAG | `patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch`; `patches/upstream/rfc/0001-ARM-tegra-stingray-wlan-mac-atag-to-fdt.patch` | Original source physically used for v06.x WLAN, factory DT MAC preserved. Reformatted upstream RFC separately applies/checkpatch but **not signed/submitted nor physically recompiled as exact RFC bytes** | Keep patch 0001 independent. Obtain actual author DCO before any submission; never hardcode/commit MAC bytes |
| Stingray board DTS and real shared-chip wiring | `src/chip/tegra20-stingray-bcm4329-owner-v029.dtsi`, board WIP DTS in separate Linux source worktree | Lab derivative; canonical upstream DTS/bindings not extracted as standalone qualified patch | Minimal SoC/board definition, regulator clock roles, GPIO ownership, DT bindings and build; physical one-variable verification |
| Whole-chip regulator/LPO pwrseq provider | `src/chip/stingray-bcm4329-pwrseq.c`, `src/chip/Kconfig`, `src/chip/Makefile` | **ARM 32-bit object compiled offline only**, not linked or deployed. `CONFIG_POWER_SEQUENCING` was disabled and MMC/HCI consumer integration absent in documented source | Bring provider+MMC+HCI consumers under API and DT binding; resolve ownership first; add isolated compile+dt-schema+hardware-trace gate |
| Bluetooth shared-U4 regulator vote | `src/chip/tegra20-stingray-bcm4329-bt-u4-v030.dtsi`; separate v030 historical compiled source recorded in checkpoints (do not claim a nonexistent patch file) | v030 Motorola-only hci_bcm vote compiled offline. v033/v034 follow-up physical BT UART/reset/U4 votes and v062 HCI controller bring-up prove *some* stages, not complete shared-owner wiring | Reconcile live p8 HCI binding, restore clock and reset ownership map; isolate provider interface from BT transport |
| Bluetooth LPO naming | `src/chip/tegra20-stingray-bcm4329-bt-lpo-v032.dtsi` | Compile-only disabled-DTB preview; not proven on current Debian running DTB | Compare actual `/proc/device-tree` and desired `lpo` binding against `hci_bcm` semantics; isolated compile/test |
| WLAN SDIO OEM capability/host quirk | `patches/experiments/v018-motorola-six-field-sdio-capabilities.patch`, v019/v020/v021 MMC prototypes | Experimental, not upstream RFC. v06.x can enumerate mmc2+BCM4329 and reach `wlan0` without a blanket SDIO quirk | No speculative high-speed flag/25MHz/host capability in main series unless matched physical regression evidence |
| Clean WLAN module teardown | `patches/lab/0001-v062-broadcom-wcc-unload-order.patch` | **Physical PASS v06.2**: WCC -> brcmfmac -> brcmutil unloaded; USB preserved. **Lab userspace patch only**, not an upstream kernel change | Adapt bounded unload commands for Debian and capture references/events; never interpret driver unload as internal regulator POR |
| Calibrated regulatory & country map | `docs/research/MZ600_BCM4329_REGULATORY_OEM_LINUX7_AUDIT_2026-10-25.md`; `configs/os/brcmfmac4329-sdio.mz600-us69-no-mac.txt` | OEM MZ600 factory US/69 calibration independently corroborated; signed regdb selected in earlier Debian checkpoint, yet no firmware country-iovar acceptance proven on installed p8. **No permanent DTS map patch yet** | Separate MZ600-only country map DT proposal, signed regdb verification, firmware country-iovar proof, legal RF-limit intersection; never embed factory identity |
| Bluetooth HCD firmware | PRIVATE `BCM4329B1.hcd` exact bytes never public | v06.2 HCI0/BCM4329B1 register and UP/DOWN physically passed; later v06.3 firmware HCD physically accepted per current WIP upstream patch README. **Firmware is not a kernel patch** | Revalidate actual p8 firmware + HCI after whole-chip state ownership; keep proprietary bytes/private keying separate |
| USB COM9, p7 boot, internal p8 Debian + 114 exact .ko | `docs/checkpoints/MZ600_V064_114_ABI_MODULES_INTERNAL_P8_ATOMIC_INSTALL_PHYSICAL_PASS_2026-10-26.md` | **Physical PASS**. Stable active root and USB console, 114 exact .ko and depmod, postinstall p7 physical readback unchanged | Use as safe standard-ABI testbed. No kernel recompilation/flashing for missing D-Bus or stale WLAN service failure |
| Debian system D-Bus and network services | `docs/checkpoints/MZ600_V064_POST_MODULE_INSTALL_READONLY_SDIO_WIFI_SYSTEMD_FORENSICS_2026-10-26.md` | **Now FIXED in running p8 Debian userspace**: six official Debian Bookworm APT metadata-matched packages installed, `messagebus` account/group present, system D-Bus socket/daemon active, actual `dbus-send ListNames` RPC PASS; see Oct26 physical checkpoint. WLAN and WPA still have historical failed status because they were NOT restarted. Userspace-only, no new kernel patch evidence | Verify bounded WLAN lifecycle under stable USB/recovery guard; only elevate actual kernel/device-tree discrepancy to whole-chip patch series |

**Artifact provenance correction:** The historical v030 source patch is NOT tracked under the former guessed `patches/experiments/` name in this repository. The tracked disabled DTS preview exists; review the actual v030 checkpoint/worktree before naming a source patch. All compile-only/proposed concepts retain their actual status, never promoted to deployed by implication.

## Required evidence feed from every upcoming Debian Wi-Fi test

Capture a small, private **timestamped physical test transcript**, then update this ledger and the public checkpoint (without MACs/credentials/firmware payloads):

1. **Pre-driver state:** kernel exact ABI; SDIO 1/2/3; `/sys/class/net`; `/proc/modules`; Bluetooth serdev binding/power vote/clock owner; factory DT MAC field length and derived identity *comparison result only*, not actual MAC.
2. **One controlled change at a time:** module `brcmutil/brcmfmac/brcmfmac-wcc` start, firmware and NVRAM selected, F2 readback, `wlan0` actual appearance, signed regulatory-domain / firmware country readback. No auto-scan or power overrides by test script.
3. **Share-chip ownership observation:** regulator U4 vote, I7/U0/U2 pinctrl states, shared LPO timing and state; label `observed kernel readback` vs true physical voltage. Distinguish independent WLAN and BT tests from simultaneous operation. Never conflate an RF scan with chip POR proof.
4. **Symmetric cleanup and preservation:** ordered WCC-first unloading, no active Wi-Fi network sessions, no BTCOMP restart, USB console and power responsiveness after each operation. Record failure before doing anything that could lose COM9.
5. **Patch disposition:** For every meaningful difference, designate either **kernel/DT**, **lab userspace**, **official Debian package**, or **private firmware/calibration**. Kernel/DT observations require a minimal patch, unaffected baseline, `git apply --check` on pinned source, `checkpatch` and build, then controlled hardware A/B before any upstream readiness claim.

## Current operating constraints

- Preserve permanent p7 SHA256 `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`, p8 stable filesystem UUID and p6 TWRP/GPT. No flash/reboot to test D-Bus.
- Keep live WLAN radio quiet until a bounded lifecycle and regulatory plan is ready; owner may be away and prior red-LED power-state episodes make unattended reboot/forced reset unsafe.
- Do not change the experimental original Xoom TWRP Toolkit or its Bluetooth implementation; this is the replacement MZ600 Linux project.
- Do **not** submit kernel patches upstream without user instruction and authentic DCO.
- Every meaningful patch experiment must update this ledger, exact handoff, runtime env, status and a dated evidence checkpoint in the same development branch; run repository validator afterward.

## Primary references

- `docs/research/BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md`
- `docs/research/BCM4329_CROSS_SUBSYSTEM_FAULT_TREE.md`
- `docs/research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md`, `docs/research/BCM4329_DATASHEET_PAGE_INDEX.md`
- `src/chip/README.md`, `patches/upstream/README.md`
- `docs/checkpoints/MZ600_V062_WIFI_WCC_ORDERED_UNLOAD_PHYSICAL_PASS_2026-10-25.md`
- `docs/checkpoints/MZ600_V062_BCM4329B1_BLUETOOTH_HCI_LIFECYCLE_PHYSICAL_PASS_2026-10-25.md`
- `docs/research/MZ600_BCM4329_REGULATORY_OEM_LINUX7_AUDIT_2026-10-25.md`
- `docs/checkpoints/MZ600_V064_POST_MODULE_INSTALL_READONLY_SDIO_WIFI_SYSTEMD_FORENSICS_2026-10-26.md`


## Oct 26 follow-up — actual installed WLAN service audit: missing reverse lifecycle

Read-only physical COM9 audit of `/usr/local/libexec/xoom-check-factory-wlan-mac` and `mz600-wlan.service` confirms robust per-device FDT identity guard followed by `modprobe brcmfmac-wcc` and `modprobe brcmfmac`. Exact ABI `modprobe -n -v brcmfmac-wcc` resolves `brcmutil`→`brcmfmac`→`WCC`. **WLAN service has no `ExecStop` and is one-shot `RemainAfterExit=yes`**: stopping that unit alone cannot serve as proven driver/resource teardown. This is a **Debian integration/lab lifecycle gap**, not automatically a kernel source defect; implement a reversible bounded diagnostic with explicit WCC→brcmfmac→brcmutil unload, preserve USB root console and test postcondition. Record U4/I7/U0/U2/pwrseq ownership independently; unloading does not prove chip POR. Wi-Fi was **not loaded** during inspection.

## Oct 26, 2026 — owner's multi-device qualification decision and physical D-Bus progress
## Oct 26 physical baseline upgrade — persistent Debian wlan0 and passive scan proved

After D-Bus repair and 114 ABI-correct `.ko` installation, the owner authorized actual live testing (no reboot). An exact-hash, bounded, auto-cleanup [Wi-Fi test script](../../scripts/host/xoom/test-v064-wlan0-passive-scan-bounded-20261026.sh) executed on actual MZ600 Debian p8 Linux 7. Driver stack `brcmutil` + `brcmfmac` + `brcmfmac-wcc` loaded, `wlan0` appeared with `addr_assign_type=0`, PHY ch1/6/11 verified, WLAN link UP, **passive 2412/2437/2462 scan rc0 with 19 BSS**. It then brought interface down and unloaded WCC→brcmfmac→brcmutil each rc0; an independent USB audit proved wlan0/brcm modules absent again, D-Bus alive, and full p7 SHA+root UUID unchanged. Firmware was BCM4329/3 September 2011 `4.220.48`; missing optional CLM/TXCAP not fatal. See [full physical checkpoint](../checkpoints/MZ600_V064_PERSISTENT_DEBIAN_BCM4329_WLAN0_PASSIVE_SCAN_AND_ORDERED_TEARDOWN_PHYSICAL_PASS_2026-10-26.md).

**Important new anomaly for patch-series triage:** scan requested 2412,2437,2462 passive, but the **19 BSS metadata** included **2 entries reported 2442 MHz** (8/4/2/5 split). Possible firmware cache or driver-reported extra results; without MMC/WLAN scan-trace it is **not proof of RF tuning** to channel 7. Do not modify kernel filtering, regional country map, or radio power based on this alone. Preserve as test observation for later deterministic cache/scan trace and per-unit regulatory tests.

**Classification:** upstream generic driver / existing board DTS = PHYSICALLY PASS on installed MZ600. The candidate whole-chip pwrseq provider/consumer wiring remains **compile-only and unqualified**; do NOT mark G3 or multi-device G5 complete. Successful WLAN-only driver cleanup still does not measure internal PMU POR, U4/I7 votes, U0/U2 resets or simultaneous Bluetooth. A polished own-use patch series must *preserve* this working baseline and prove one-variable improvements across MZ600/MZ602/MZ604.



Owner requires **rigorous physical testing of the whole-chip patch series on multiple additional Xooms before any community review**. We are optimizing own-use reproducibility, safe deploy/rollback, and a useful understandable patch set first. [Multi-device source/build/physical validation gates](../plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md), [machine-readable stage manifest](../../configs/patch-series/bcm4329-whole-chip-qualification-v1.json), and [offline fail-closed checker](../../tools/forensics/check_bcm4329_patch_series_gates.py) are now tracked. Initially `review_ready=false`: no other unit yet validated with the whole-chip provider; MZ617 compatibility must be separately proven. Formal source gate currently contains a single unsent MAC-ATAG RFC, not a completed shared-chip series.

**Offline QA actually executed on Desktop WSL:** `python3 tools/forensics/test_bcm4329_shared_chip_model.py` **20/20 PASS**; `python3 tools/forensics/check_bcm4329_index.py` **149/149-page index + 36/36 requirement rows PASS**; repository validator PASS. These tests cover logical contracts/doc integrity, not GPIO waveforms, phys PMU reset or a field-tested integrated provider.

**New on-device userspace result:** [D-Bus 6/6 offline install and live method-call PASS](../checkpoints/MZ600_V064_DEBIAN_DBUS_OFFLINE_SIX_PACKAGE_INSTALL_SYSTEM_BUS_PHYSICAL_PASS_2026-10-26.md). This removes missing system bus as a blocker for subsequent BlueZ/WPA userland bring-up, but **does not** validate `hci_bcm` binding, `WL_REG_ON`/`BT_REG_ON` regulator votes, WCC teardown, radio concurrency or Bluetooth pairing. Physical WLAN/WPA services remain in their previous failed state until separately started; no radio test happened during D-Bus repair. Record only as Debian packaging milestone; no kernel source modifications in this step.
