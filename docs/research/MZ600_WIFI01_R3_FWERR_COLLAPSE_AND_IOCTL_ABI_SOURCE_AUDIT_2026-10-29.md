# WIFI-01 r3: firmware-error normalization and legacy IOCTL ABI — source audit, 2026-10-29

**Status: NEW SOURCE-LEVEL FINDING; NO PHYSICAL TEST, NO NEW KERNEL PATCH, NO BUILD, NO SIGNOFF.** Working MZ600 p10 Debian, installed original nine-patch Wi-Fi and earlier r2/r3 candidates were not touched. Issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4) remains OPEN.

## Provenance and mandatory historical gate

Read the [Oct28 35/35 r2 OEM failure](../checkpoints/MZ600_WIFI01_R2_OEM_2012_PERCHAN_PHYSICAL_AND_HISTORY_2026-10-28.md), the [BCM4329 regulatory contract archaeology](MZ600_BCM4329_LEGACY_CHANNEL_REGULATORY_CONTRACT_2026-10-28.md), the [r3 draft](../../patches/upstream/review-wifi-four-logical-20261028-r3/README.md), and issue #4's earlier comments before interpreting this result. Earlier Oct26 v05 and V13 blanket passive-only flags were **lab safeguards**; V28 deliberately removed obsolete blanket NO_IR/scan gates. The May2012 Motorola firmware 4.218.248.44, with the unchanged calibrated 1,550B NVRAM, returned dual-band (count2), 35 valid channels, and **0/35 success** on full D11n chanspec per_chan_info in r2. That physical trial logged **no raw BCME status**, executed no scan and rolled back fully. This finding does **not** retroactively change that trial's measured results.

Source identities:
- Pinned upstream: `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
- Project branch: `Olsens11/XoomLinux7:wip/clean-wifi-bt-usb-20261025`.
- Current r3 WIFI-01 export: `patches/upstream/review-wifi-four-logical-20261028-r3/0001-wifi-brcmfmac-use-legacy-channel-list-on-BCM4329.patch`, fetched blob SHA `340520d4e2dd842db2b9ea8878988a196e8d3e50`. The source remains **unsigned/unaccepted**.

## Newly verified causal distinction — `-EBADE` is not `BCME_UNSUPPORTED`

In pinned [`brcmfmac/fwil.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.c#L95-L128), `brcmf_fil_cmd_data()` calls `brcmf_proto_query_dcmd(..., &fwerr)`; **when transport succeeded but `fwerr < 0`**, it collapses arbitrary firmware failure codes to Linux **`-EBADE`**. The native negative BCME value is only returned to callers when `ifp->fwil_fwerr` is enabled. Thus `-EBADE` alone cannot distinguish `BCME_BADARG`, `BCME_UNSUPPORTED`, `BCME_NOTUP`, or any other firmware failure. This is not a newly introduced upstream transport defect.

The r3 WIFI-01 hunk explicitly tests:
```c
} else if (chan_err == -EOPNOTSUPP ||
           chan_err == -EBADE) {
        /* Early firmware lacks per-channel metadata. */
        per_chan_available = false;
}
```
The comment / caching inference is **not established**. A malformed modern chanspec returning BCME_BADARG could be misclassified as globally unsupported and suppress queries for subsequent channels. The r3 5GHz conservative NO_IR behavior is a **separate candidate policy** and is not proof of a correct normal-radio regulatory solution. This is a **confirmed source-specific review risk**, not proof of which BCME error occurred on the physical May2012 firmware.

## Existing, upstream-native way to preserve firmware error identity

The pinned [`core.h`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.h#L180-L207) declares `ifp->fwil_fwerr`. Pinned [`feature.c`](https://github.com/xoom-linux/linux/blob/2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.c#L179-L207) already temporarily sets that field to `true` around a feature iovar and checks the original `-BRCMF_FW_UNSUPPORTED`, then resets it to `false`. This is a validated **source precedent for retrieving raw firmware errno**; it has NOT yet been used in our particular `per_chan_info` experiment.

Critical caution: `fwil_fwerr` is *per-interface shared state*, not a per-query argument. A lab diagnostic must isolate concurrent callers or prefer a strictly targeted, bounded trace in `fwil.c` that records both transport return and `fwerr` **before** normalization only for `per_chan_info`; don't leave the flag enabled, don't change ordinary production error behavior, and don't treat raw firmware error as valid if the underlying transport itself failed. The existing fil query wrapper uses a 4-byte little-endian in/out argument; for primary bsscfg index zero, `brcmf_create_bsscfg()` falls back to the ordinary iovar name+NUL+argument framing (see pinned `fwil.c` and `fwil.h`). No BSSCFG-prefix error has been proven.

## Additional external upstream/OEM precedent: IOCTL protocol version

Older Broadcom [Android `wl_cfg80211.c`](https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/wl_cfg80211.c) queries read-only `WLC_GET_VERSION`, validates `ioctl_version`, and when version 1 is returned, `wl_chspec_host_to_driver()` calls `wl_chspec_to_legacy()` before sending the argument. Later `wl_construct_reginfo` source paths use `per_chan_info` with `channel|BAND|BW20`; the archived Xoom source used `channel|BAND`; modern `brcmfmac` uses encoded D11n 20MHz. **The 0x1824 pre-conversion source constant is not necessarily the exact wire value in every legacy driver.** Preserve actual post-conversion, little-endian bytes in the comparison.

External `bcmdhd` also explicitly handles native `BCME_UNSUPPORTED` in its channel metadata logic (for example [Android msm](https://android.googlesource.com/kernel/msm/+/68cdc8df1cb6622980b791ce03e99c255c9888af/drivers/net/wireless/bcmdhd/wl_cfg80211.c)); this proves a vendor precedent, **not** that this May2012 firmware returned unsupported. [Linux channel flags definitions](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/broadcom/brcm80211/include/brcmu_wifi.h) distinguish `WL_CHAN_RADAR`, `PASSIVE`, `RESTRICTED`, etc.; no metadata was actually obtained on the device.

## Minimum next discriminator — not an authorized hardware procedure

1. Source-only: design an isolated diagnostic that preserves **transport errno + native BCME errno**, the `BRCMF_C_GET_VERSION` (historical `WLC_GET_VERSION`) read-only result if supported, and exact wire-framed little-endian input/response. Avoid a global state change in ordinary operating paths.
2. Compare 2.4GHz ch11 `0x200b/0x280b/0x2b0b` and 5GHz ch36 `0x1024/0x1824/0x1b24`; log response validity and distinguish an echo from recognized `WL_CHAN_VALID_HW/VALID_SW` and restricted bit patterns. Actual legacy conversion may require interpreting the IOCTL version rather than assuming three raw numbers cover all cases.
3. Only after an explicit new hardware gate: same replacement MZ600, known May2012 OEM private firmware + unchanged NVRAM, matched RAM-only modules and full hash/COM9/WLAN preflight and independent rollback. **No scan, country/power modification, association, flash, or re-use of consumed r2 trial IDs.**
4. If a format succeeds, amend the **same WIFI-01** and classify firmware-only restrictions correctly. If all fail, preserve Linux cfg80211/regdb and conservative no-TX fallback without pretending the iovar works. **Do not promote r3's cache as correct merely on a `-EBADE` return.**

**Acceptance:** Source finding VERIFIED; new diagnostic NOT BUILT; exact IOCTL version and native per-channel errno on the DUT NOT MEASURED; r3 full nine-patch integration/hardware/regulatory qualification NOT RUN; issue #4 remains OPEN. No public private identifiers, firmware binaries, or credentials were accessed or published.
