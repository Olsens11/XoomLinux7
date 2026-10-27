# MZ600 BCM4329: Evaluate 2012 OEM escan-capable candidate before implementing HRI39 iscan

Date: 2026-10-26. **Read-only existing checkpoint review and offline private firmware ASCII-name comparison ONLY**. No RF scan, Xoom/USB COM9 access, module load, firmware swap, installation, calibration alteration or test of the candidate was performed.

## Why this changes the next priority

The actual goal is standard dual-band wlan0 scan completion under Linux7, not implementing Event26 for its own sake. Generic firmware has already proven ordinary 2.4GHz escan scanning; the original Motorola firmware has proved 5GHz legacy WLC_SCAN scanning, but without observed Event26 and with 10-second fallback. If a later compatible OEM image provides 5GHz and the modern ESCAN protocol together, it may avoid any new iscan lifecycle implementation.

| Reference | Firmware binary / identity | Physical results on experimental MZ600 |
| --- | --- | --- |
| Standard installed Linux7 4.220.48 (Sep 2 2011) | 253748B, SHA256 `d61983946b1e733e4c75dbe6841ac0f1250eb2e3ee9058cdfdbbba3ba37c93` | Normal cfg80211 2.4G passive scan returned 19 BSS; firmware `GET_BANDLIST` count1 = 2G, `chanspecs` total11=11 2G, 0 5G, even after restoring 1569B OEM-matched US69 country/regrev at bootstrap. Cannot currently use it for 5G. |
| Original Motorola HRI39 4.218.248.20 (Jan12 2011) | 261317B SHA256 `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a` | Firmware bandlist 2G+5G; WLC_GET_VALID_CHANNELS reports 11 2G + 9 5G. Legacy passive 5180MHz WLC_SCAN50 / results51 returns 3-4 validated BSS; modern escan returned -52 and full event26 mask enabled without observed event; timer ~10 sec. |
| Later OEM reference 4.218.248.44 (May25 2012) | 264140B SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`; private Desktop `firmware-reference-v08-OEM-MZ600-private/brcm/brcmfmac4329-sdio.bin`; provenance later OEM `fw_bcmdhd.bin` also indexed in v5 firmware evidence plan | **NEVER physically tried on current Linux7 experimental MZ600**: no verified bandlist, effective regulatory status, `wlan0`, `escan` acceptance, Event69, completion or coexistence results. |

## New 2026-10-26 read-only binary comparison

On Desktop WSL, simple case-sensitive ASCII-name search (`grep -aob -e escan -e iscan -e chanspecs -e bandlist -e event_msgs`) of the distinct existing private candidate images yielded:

- Generic 4.220.48: `escan` at offset 170870, `chanspecs` at 170905. It already physically performs modern 2.4G scans but reports NO 5G.
- Later OEM 4.218.248.44: `event_msgs` at 187417, `iscan` at 187538/187544, `escan` at 187805. **No literal `chanspecs` match**. The old `WLC_GET_VALID_CHANNELS` fallback may therefore still be needed even if newer `escan` is supported. ASCII iovar-name presence suggests a code path, **not proven successful support** or a terminal Event69.
- Original HRI39 4.218.248.20 was separately hashed and inspected in the earlier exact-binary report and has `iscan`, `iscanresults`, `event_msgs` but lacks `escan`. Original HRI39 5G working legacy-only scan is the current reference.

Important: 2012 firmware version numbers belong to a different minor version lineage (4.218.248.44 versus generic 4.220.48) and a later OEM source. Firmware build date or the common BCM4329-B1 label alone is NOT proof of compatible RF front-end, calibration, region or Bluetooth power sharing. Historical later OEM calibration differs from HRI39/HRI66 reference; do not transplant OEM MAC/OTP and do not blindly use another unit's calibration.

## Safer next validation sequence, if owner chooses

1. **Offline first**: verify file provenance and exact hashes, OEM firmware intended chip/rev and version, available command strings, later OEM calibration differences (private values never printed), whether current `brcmfmac` works with old `chanspecs` absence and whether modern ESCAN request variant is compatible. Build a host-only decision/compatibility matrix.
2. **Owner-controlled no-scan candidate test** only if offline checks permit: RAM-only bind-overlaid 2012 firmware plus strictly matched board calibration and factory per-device FDT MAC, load ABI-matched reversible diagnostic module. Do not install. Query `GET_BANDLIST`, effective country/rev, legacy valid channels, and enumerate wiphy. Do **not** force 5 GHz capabilities, switch country, enable TX, or run a scan if the firmware doesn't present permissible 5GHz channels.
3. **Conditionally after 5G bands/protocol prove real**: one NO_IR non-DFS passive scan limited to permitted 5180 MHz channel36, no probe or association, verify `escan` command acceptance, partial Event69 records and actual success terminal Event69 or other grounded completion, radio duration and full cleanup. Reuse the proven v11 5GHz channel and BSS constraints, and independent original-state post-audit.
4. **Compare standard generic 2.4G baseline**, original HRI39 5G legacy fallback, and later OEM candidate. If candidate fails dual-band/ESCAN/completion, preserve HRI39 plus source-verified ISCAN work without assuming the candidate's failure disproves our previous milestones.

## Specific answers to user's question

Yes, newer firmware plus existing completion signal is the simplest potential outcome and should now be **prioritized ahead of writing a brand-new HRI39 iscan polling/worker patch**. We did not ignore this deliberately: 4.220.48 already experimentally lacked 5G and the May 2012 alternate candidate was not yet tested. The firmware-binary `escan` string discovery now provides a concrete hypothesis and narrow next measurement. Do not claim 5G capability/Event69 for 2012 until measured.

## Existing project evidence

- [Generic firmware reported only 2G and 11 channel specs](../checkpoints/MZ600_V064_BRCMFMAC_FIRMWARE_5GHZ_BANDLIST_CHANSPEC_PHYSICAL_PROOF_2026-10-26.md)
- [Generic fw still 2G after OEM US69 calibration A/B](../checkpoints/MZ600_V064_OEM_US69_BOOTSTRAP_NVRAM_A_B_PHY5GHZ_UNCHANGED_OWNER_PHYSICAL_2026-10-26.md)
- [Original HRI39 has real 2G+5G firmware-supported channels](../checkpoints/MZ600_V064_HRI39_OEM_FIRMWARE_TWO_BANDS_LEGACY_VALID_CHANNELS_20_PASS_2026-10-26.md)
- [2012 firmware private provenance and calibration caveats](MZ600_BCM4329_V5_FIRMWARE_PMU_CM3_EVIDENCE_PLAN.md)
- [HRI39 v12 event26 readback and iscan-only alternative](MZ600_HRI39_EXACT_BINARY_ISCAN_RESULTS_COMPLETION_STATUS_SOURCE_AUDIT_2026-10-26.md)
- [Standard generic Linux7 2G scan 19 BSS](../checkpoints/MZ600_V064_PERSISTENT_DEBIAN_BCM4329_WLAN0_PASSIVE_SCAN_AND_ORDERED_TEARDOWN_PHYSICAL_PASS_2026-10-26.md)