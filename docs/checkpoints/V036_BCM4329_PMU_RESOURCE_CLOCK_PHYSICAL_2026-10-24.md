# v036 physical — BCM4329B1 PMU-revision-6 resource and clock-status observation

**Date:** 2026-10-24. **Result:** PASS for read-only observer compilation/verification, RAM-only transfer, two physical register traces, and clean unload. **Wi-Fi remains FAIL** (Function 2 IORx never ready, `-62`). **Scope:** protected Xoom untouched, replacement Xoom kept in preexisting temporary v034 kernel boot; no reboot/flash, firmware/NVRAM swap, reset, or regulator changes.

## Provenance and instrument
- Builder: [`scripts/experiments/v036-build-pmu-status-readonly.py`](../../scripts/experiments/v036-build-pmu-status-readonly.py), derived from source/hash guarded v035 observer. Pinned Linux 7 source `sdio.c` SHA256 `74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab` and `chip.c` `932e25c75f9ea5247194dfdb78c6b41a457af68d7a558935a7b5489bf548aa9d` restored and verified after build.
- Compiled ARMv7 module: `brcmfmac-v036-pmu-cm3-readonly.ko`, **462048 bytes**, SHA256 **`fc1ee41754769542c833f1c95c30f11fe211d5deaf8844e4fc31116bbbcfcc5b`**, vermagic `7.0.0-next-20260422 SMP mod_unload modversions ARMv7 p2v8`.
- Surface reconstruction independently matched size and SHA256. Existing guarded USB transfer on COM9 acknowledged **`UPLOAD DONE SIZE 462048 CRC32 0xB63E4E11`** into `/run/brcmfmac.ko`. The original runtime's normal `brcmutil` and modified diagnostic `brcmfmac` modules loaded rc=0 each.
- v036 only adds single-pass register reads `pmustatus` (0x608), `res_state` (0x60c), `res_pending` (0x610), and revision-guarded `gpiopullup`/`gpiopulldown`, extending v035 PMUControl/CHIPCLKCSR/CCCR snapshots. The driver still makes its original pre-existing writes. **Read-only is not timing-neutral**; no arbitrary polls/delays were added.

## Both physical trials

Both trials are warm driver-only starts on the already-running v034 temporary Linux session. Trial 2 was after successful WIFI_STOP of trial 1, without MMC detach, whole-chip power-cycle or reboot. All register read error codes were **0**.

| Signal | Trial 1 | Trial 2 | Meaning |
| --- | --- | --- | --- |
| ChipCommon revision | **29** | **29** | OEM revision-gate `ccrev >=20` satisfied |
| BCM4329 PMU revision | **6** | **6** | Critical for selecting actual silicon-specific PMU field interpretation |
| PMUControl T0-T5 | `0x012B03BC` | `0x012B03BC` | Warm retained value, as in latter two v035 trials |
| PMUStatus T0 through T3 | `0x000000AE` | `0x000000AE` | OEM `PST_SBCLKST=0x20`: ALP state |
| PMUStatus T4 through T5 | **`0x000000BE`** | **`0x000000BE`** | OEM `PST_SBCLKST=0x30`: HT state |
| Resource-state mask T0–T5 | **`0x003FE63E`** | **`0x003FE63E`** | Active mask invariant across sampled stages |
| Resource-pending T0–T5 | **`0x00000000`** | **`0x00000000`** | No resources pending at sampled instants |
| ChipCommon pull-up/down T0–T5 | both `0x00000000` | both `0x00000000` | Observed state is same as Motorola explicitly established |
| IOEx / IORx before F2 | `02 / 02` | `02 / 02` | Function 1 only |
| IOEx / IORx after F2 | `06 / 02` | `06 / 02` | Function 2 requested, never ready |
| F2 enable result | **`-62`** | **`-62`** | WLAN failure persists, `wlan0` not established |

Sanitized raw event snippets are preserved locally on Surface: `v036-trial1-sanitized.log` and `v036-trial2-sanitized.log`. The USB `LOGS` read returns only the newest 4KB of the kernel ring; first initial T0 standard entry is sometimes truncated but all six resource entries and the readiness boundary are captured. Do not infer missing data from that retrieval truncation.

## Critical recovery of Motorola's *actual* BCM4329 resource map

The OEM [Motorola `sbchipc.h` at kernel revision `2a65edc`](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/include/sbchipc.h) **lines 883–904** defines `RES4329_*` bit assignments specifically for this chip. Applying them to **resource-state mask `0x003FE63E`**, the following resources have active bits:

| Bit | OEM name | Active? |
| ---: | --- | :---: |
| 1 | `CBUCK_LPOM` | Yes |
| 2 | `CBUCK_BURST` | Yes |
| 3 | `CBUCK_PWM` | Yes |
| 4 | `CLDO_PU` | Yes |
| 5 | `PALDO_PU` | Yes |
| 9 | `LNLDO1_PU` | Yes |
| 10 | `OTP_PU` | Yes |
| 13 | `XTAL_PU` | Yes |
| 14 | `ALP_AVAIL` | Yes |
| 15 | `RX_PWRSW_PU` | Yes |
| 16 | `TX_PWRSW_PU` | Yes |
| 17 | `RFPLL_PWRSW_PU` | Yes |
| 18 | `LOGEN_PWRSW_PU` | Yes |
| 19 | `AFE_PWRSW_PU` | Yes |
| 20 | `BBPLL_PWRSW_PU` | Yes |
| 21 | `HT_AVAIL` | Yes |

Non-active/reserved bits are 0, 6 (`ILP_REQUEST`), 7, 8, 11, and 12 (`LNLDO2_PU`). **A zero ILP_REQUEST resource bit does not prove loss of an external 32.768kHz signal**; the active/pending mask is interpreted using OEM definitions but status-bit semantics and policy may vary across runtime states.

This demonstrates multiple PMU-reported regulators, crystal, baseband/RF PLL and internal power-switch resources already active at F2 failure; this is **not** a direct external rail-voltage measurement or a proof that digital WLAN firmware is functioning. Do not force radio resources merely because they are marked active.

## PMUStatus bit semantics from same-generation OEM source

[`sbchipc.h` lines 705–713](https://android.googlesource.com/kernel/tegra/+/2a65edc/drivers/net/wireless/bcm4329/include/sbchipc.h) specifies:
- `PST_SBCLKST` `0x30`; `PST_SBCLKST_ALP=0x20`; `PST_SBCLKST_HT=0x30`.
- `PST_ALPAVAIL=0x08`, `PST_HTAVAIL=0x04`, both asserted throughout traces.
- `PST_RESINIT=0x03` and `PST_INTPEND=0x40` are defined, but interpretation of unassigned bits is deliberately withheld.

The original `sbchipc.h` **does not assign generic `EXT_LPO_AVAIL=0x100` or `WDRESET=0x80` definitions** at that location. Later generic Broadcom headers provide these bit names, but their applicability to PMU revision 6 on BCM4329B1 is **not established**. Do **not** assert either an absent external LPO or a watchdog reset based solely on those bits.

## What is stronger / weaker after v036

**Stronger:** host-requested ALP and HT transitions manifest in chip PMUStatus and the OEM-mapped `HT_AVAIL` resource bit. Specific internal PMU power resource transitions are not pending at the sampled boundaries. The ChipCommon pull-register state already agrees with Motorola's reset-time programming. This removes several straightforward missing-setup explanations.

**Unresolved:** what precisely executes on CM3 after reset, why the firmware never asserts F2 ready, whether the v035 first-run PMUControl transition is firmware-driven or autonomous, actual POR/pin voltages, and the revision-6 XTAL frequency-code table. `pmurev=6` alone does not authorize applying PLL code assignments from newer PMU generations.

## Stop/rollback state

After two trials, `WIFI_STOP brcmfmac_rc 0 brcmutil_rc 0`. Final `MMC2_STATUS`: COM9 responsive; target valid; MMC2 bound; BCM4329 verified; both driver modules unloaded; `AUTO` profile 0. Still running original temporary-boot v034 kernel, original generic firmware/NVRAM unchanged. **No persistent device writes.**

## Next discriminating evidence gates

1. Compare OEM `dhd_bus_init` / F2 polling exactly to Linux 7 `brcmf_sdio_firmware_callback`; inspect indirect writes and configuration around mailbox, CM3 reset and firmware placement.
2. Recover the PMU rev6 / BCM4329-specific `PCTL_XTALFREQ` encoding from a reliable same-chip source (other PMU family tables disagree on the meaning of raw `15`).
3. If necessary, add read-only CM3 core wrapper and SDIO mailbox **status** probes with exact read semantics and error handling, not arbitrary extra register writes.
4. Treat actual whole-chip POR, coordinated WLAN/BT/FM reset, and early original Motorola 2011 firmware 4.218.248.20 as **distinct one-variable tests**, only with explicit device-identity/regulatory protection and reversible USB RAM test plan.

**Acceptance:** v036 compilation pass; SHA256 transfer pass; USB CRC pass; physical PMU-resource observations pass and repeated; WLAN F2 remains FAIL; clean driver unload and MMC2 bound pass.
