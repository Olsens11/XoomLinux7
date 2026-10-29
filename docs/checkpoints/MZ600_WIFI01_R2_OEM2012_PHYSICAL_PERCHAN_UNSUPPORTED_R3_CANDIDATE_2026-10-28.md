# WIFI-01 r2 — May 2012 OEM firmware physical test and r3 source correction (2026-10-28)

**Outcome:** OEM firmware dual-band PASS; optional per-channel restriction query FAIL 35/35; test stopped before scan; rollback and subsequent original Wi-Fi connectivity PASS. R3 is an **offline candidate, not physically tested**.

## Actual one-shot on MZ600

Fresh Surface trial MZ600-R2-OEM-DIAG-20261028B used the exact nine-patch Linux build plus r2 WIFI-01 and read-only driver diagnostics, 2012 Motorola OEM firmware 4.218.248.44 (264140 B, private SHA256 5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834), unchanged original 1550B NVRAM, temporary firmware RAM bind only. Instrumented full-build core module 344016 B SHA256 9f168c2e84ece2c51b2b3c5161704b86ff741558142372bd3307dcf7af1aacb5. Kernel 7.0.0-next-20260422+, Debian root p10. Exact core imported symbol CRCs match original and WCC binary was unchanged. Private serial logs and used attempt marker remain on the Surface, not Git.

Physical numeric results:
- Firmware GET_BANDLIST returned status0, count2, band1=1 (5GHz), band2=2 (2.4GHz).
- chanspecs returned -52; fallback used the firmware valid-channel list, count35.
- Firmware per_chan_info read was attempted on 35 allowed channels; **0 succeeded, 35 failed**. radar0/passive0 are NO VALID DATA, not evidence that no restrictions apply.
- The OEM binary contains a null-terminated per_chan_info string, but that does not prove functional ioctl compatibility.
- The lab-only capability display pipeline stopped with rc1 after wlan0 appeared, likely due to hardcoded phy0 on a reloaded device. The exact failing command was not independently logged. **No scan/association/transmission test occurred.**
- Cleanup succeeded: temporary firmware unmounted; original firmware/NVRAM/core/WCC hashes verified; original Broadcom modules, WPA and NetworkManager reloaded; a second read-only COM9 audit confirmed wlan0 UP, NetworkManager **100 connected**, bluetooth quiet, no overlays and p10 intact.

## Independent external precedent

Older Broadcom Android driver wl_cfg80211.c explicitly handles BCME_UNSUPPORTED on per_chan_info rather than inferring radar/passive metadata from an unsuccessful query:
https://android.googlesource.com/kernel/msm/+/68cdc8df1cb6622980b791ce03e99c255c9888af/drivers/net/wireless/bcmdhd/wl_cfg80211.c

We did **not** measure the exact per_chan_info failure errno in this run; do not claim BCME_UNSUPPORTED. It may be an ABI format problem, so a new diagnostic must capture the numeric error before declaring firmware support impossible.

## Historical reuse gate (mandatory)

The earlier [v05](MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md) and [V13](MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md) physical trials already demonstrated a **lab-only** passive/NO_IR-capability workaround with the OEM firmware. The later [V28](MZ600_V28_NATIVE_CFG80211_SCAN_AFTER_LAB_GATES_REMOVED_2026-10-27.md) intentionally **removed blanket NO_IR and one-channel passive test gates**, because their assumptions prevented normal cfg80211 operation and dynamic legal beacon-hint flag changes. Therefore r3's limited 5GHz NO_IR fallback is proposed **only when a genuine firmware metadata query fails**, not an adoption of v05's entire retired scan policy. It cannot be promoted as upstream-acceptable until its practical association/regulatory effects are tested and firmware iovar framing/errno are understood. This gate is formally documented in the project [development workflow](../process/DEVELOPMENT_WORKFLOW.md#mandatory-historical-reuse-gate-2026-10-28).

## WIFI-01 r3 (same logical patch, not a fifth patch)

The new draft r3 keeps firmware radar/passive metadata when available; on a per-channel restriction query error it ORs Linux NO_IR on **5GHz** channels, avoiding permission to initiate radiation on unknown channels. For known -EOPNOTSUPP or -EBADE it avoids repeating the unsupported request. Existing channel, bandwidth and cfg80211 restrictions remain. This **does not** force country, create channels or override DFS; kernel regulatory and real hardware tests remain mandatory. It may need further revision once the actual firmware error is measured.

Exported four-member series: [r3 README](../../patches/upstream/review-wifi-four-logical-20261028-r3/README.md). Exact isolated source four logical commits, strict checkpatch 0/0/0 per member, stable patch IDs unchanged for WIFI-02/03/04, whitespace PASS; ARM GCC14.3.1 olddefconfig, prepare and full brcmfmac-prefix compile PASS. Modified cfg80211.o SHA256 4d7bc9c6b35eb7d2c2ab25b7cb574c4a330b2b9469434bd857aa10a31020dc00. **No full r3 kernel image, deployed r3 module, accepted regulatory result, DCO or upstream submission.**

Next: fix test harness to discover current PHY, log exact legacy per_chan_info errno and effective channel flags in a fresh ABI-matched temporary run, and only consider passive legal scanning after the regulatory gate. No MAC/SSID/firmware blob public. See GitHub [#4](https://github.com/Olsens11/XoomLinux7/issues/4), [#1](https://github.com/Olsens11/XoomLinux7/issues/1), [#7](https://github.com/Olsens11/XoomLinux7/issues/7).
