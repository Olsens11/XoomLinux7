# BCM4329 Wi-Fi four-member review r4 — native firmware-error provenance

**2026-10-29 | SOURCE-ONLY, UNSIGNED, UNACCEPTED, UNSUBMITTED.** Four logically distinct Wi-Fi fixes, one logical issue per patch. r4 **replaces** r3 for future evaluation and is **not** stacked on r3. Pinned upstream Linux7 `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. Exact working original nine-review Linux7 on MZ600 is untouched; no kernel flashed, no radio module loaded from r4, no firmware or country changed.

## Physical evidence driving this amendment

The controlled [October 29 generic/OEM firmware-country A/B](../../../docs/checkpoints/MZ600_OEM2012_FIRMWARE_COUNTRY_US_REV0_DUAL_BAND_RAM_TEST_ROLLBACK_PASS_2026-10-29.md) proved that generic Broadcom 4.220.48 and genuine Motorola May2012 4.218.248.44 **both** returned `country abbrev=US, ccode=US, regrev=0` with *identical active NVRAM*, yet only OEM 2012 advertised both 2.4 and 5 GHz. Therefore forcing factory US/69 is **not** the answer to the generic firmware's absent band; preserve legitimate Linux regulatory controls and the original dynamic country interface.

The earlier [six-format native Broadcom query trial](../../../docs/checkpoints/MZ600_WIFI01_BCME_SIXFORMAT_NATIVE_UNSUPPORTED_PHYSICAL_PASS_2026-10-29.md) on OEM2012 returned `per_chan_info` **native `BCME_UNSUPPORTED=-23`** for all three documented inputs on ch11 and ch36, while the Linux-facing error was `-EBADE=-52`. The same normalized `-EBADE` has also concealed **native `BCME_NOTUP=-4`** in separate second-scan readiness failures. The r3 review improperly treated any `-EBADE` as proof of an unsupported optional firmware API.

## Exactly what r4 changes

- **WIFI-01 (updated in place, still one logical issue):** Query `chanspecs` through a per-call native-error result on BCM4329. Take the historical `WLC_GET_VALID_CHANNELS` fallback **only** when the actual firmware code is `-23`, not for all Linux `-EBADE` results. Likewise query optional `per_chan_info` with native-error capture and cache missing metadata only for actual `BCME_UNSUPPORTED`. On success preserve the existing little-endian 20MHz encoded input/return flags. On other failures, do not declare the API missing.
- **FWIL implementation:** Small internal extension threads optional firmware-error output through the existing `brcmf_fil_cmd_data` transport under the **existing proto mutex**. Normal callers pass `NULL` and still use their previous normalized return semantics. The special BCM4329 readers use two non-exported per-call wrappers, **without toggling shared `ifp->fwil_fwerr`**. If transport fails, native-error output stays 0 and no unsupported fallback is taken.
- **WIFI-02/03/04:** The same three files/commits as r3; scan-generation, genuine Event69 owner routing and bounded firmware readiness are separate scopes. They must not be collapsed into WIFI-01 or any new chronological fixup.

**Not yet fixed (release blockers):** This r4 intentionally **retains** r3's conservative 5 GHz `NO_IR` when optional firmware metadata is absent. That is a diagnostic safety measure, not a proven production-equivalent regulatory implementation; it might interfere with normal channels. `WLC_GET_VALID_CHANNELS` is a **current-country valid-channel list**, not permanent silicon capability; r4 must still be reviewed for dynamic regulatory updates and stale `DISABLED` flags after a country transition. Motorola legacy per-channel DFS/passive information remains unavailable under the six measured requests. Signed `cfg80211`/regdb enforcement, true RF permissions and repeat-scan success are **not demonstrated by an offline compile**. The original driver-custom alpha2 `99` is not a substitute for legal/current national rules.

## Review source and QA

The source-only nine-member sequence: DT-01/02/03; ARM MAC ATAG BOOT-01; **WIFI-01 r4**; WIFI-02/03/04 unchanged; STORAGE-01 BigPart unchanged. Isolated detached WSL Linux source worktree:

`/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-wifi01-r4-source-20261029`

WIFI-01 source commit `3252fe6c8974f31091f599757e7db59fe85bdaa0`; integrated nine-member source tip `61d8fe397`. Arm GNU Toolchain `arm-none-linux-gnueabihf-gcc 14.3.1`. Original exact-nine build configuration reused with BigPart enabled for full integrated build.

**Completed as of this README:** r4 driver source changes confined to `cfg80211.c`, `fwil.c`, `fwil.h`; strict `git show --check` WIFI-01 patch PASS; `git am` remaining unrelated members PASS; driver-directory ARM prefix build PASS, before and after complete nine-member source replay. Exported WIFI-01 r4 checkpatch **0 errors, 0 warnings, 9 style checks (continuation alignment)**, which remains a cleanup gate before upstream submission. [Offline decision/source fixture](../../../tools/tests/test_bcm4329_fwerr_boundary_20261029.py) **7/7 logical cases PASS** and source-API assertion PASS. Project repository checker **0 errors**. The original nine-member DT source already has independent whitespace debt: do **not** conflate that inherited upstream-review issue with a WIFI-01 diff failure.

**Integrated full zImage/DTBs/modules:** pending verification in fresh isolated out-of-tree build `qa-wifi01-r4-build-20261029`; do not claim full build or modversion CRC PASS from the driver-only compile.

## Hardware acceptance required before promotion

On a future separately approved one-use RAM-only OEM firmware trial, independently verify native `chanspecs` and `per_chan_info` codes; genuine dual-band bandlist/allowed-channel set; effective signed-regdb/country restrictions (including DFS/NO_IR); ordinary 2.4 and 5 GHz passive/normal scans as permitted; scan1/scan2 ownership and genuine terminal events; and exact rollback of original generic firmware, calibration, WCC, brcmfmac and connected Wi-Fi. No speculative country set, universal rev0 map, fabricated firmware restrictions, boot flash or silent permanent installation.

**Human signoff/DCO not supplied.** GitHub issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4) remains OPEN; r4 is an engineering review candidate, not accepted release functionality.
