# MZ600 WIFI-01 r2 May-2012 OEM actual firmware test + mandatory historical-solution comparison — 2026-10-28

**Status:** R2 channel enumeration PASS; **regulatory parity FAIL/OPEN** because optional `per_chan_info` accepted **0/35** queries. This is actual physical runtime evidence, not just successful source compilation. The original installed generic firmware/modules and live 2.4GHz association were independently restored. Do not repeat this consumed one-shot, nor conflate this with a legally qualified transmit capability.

## Exact device / source / firmware controls

- Replacement MZ600 Linux `7.0.0-next-20260422+`, root `/dev/mmcblk0p10 ext4`, physical Surface COM9 root; NetworkManager and wpa_supplicant both active prior to test.
- Isolated, complete build: pinned nine-review source integration (original 9 commits, original `HEAD 507eb069df819cb5cc801ad8be096f70d9ca7609`) **plus same-scope WIFI-01 r2 channel helper**, plus *LAB-ONLY read-only printk diagnostics*. The r2 is not an additional upstream patch and is not installed.
- ARM zImage, matched Stingray/Wingray DTBs and modules compiled independently. New RAM-only `brcmfmac.ko` size **344016**, SHA256 `9f168c2e84ece2c51b2b3c5161704b86ff741558142372bd3307dcf7af1aacb5`; **259/259 imported symbol CRCs match** validated original module. Matched `brcmfmac-wcc.ko` 5916B is **byte-for-byte identical** to original; no unexpected old module CRCs.
- Original Motorola **May25 2012** `4.218.248.44` firmware SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, 264140B, recovered from previously hash-verified Surface V13 archive. Original **1550-byte** NVRAM remained physically installed and unchanged; no country/regrev setting, RF transmit, power or scan change.
- Original module/core/WCC/firmware/NVRAM hashes checked, no existing overlays or active Bluetooth HCI, initial Wi-Fi NM state `100 (connected)`. Historical Desktop→Surface private port 43157 workflow with SHA checks was used and explicitly torn down. A fresh one-shot RAM trial (not historical V13/V17 marker) was executed, with script, private transcript and receipt preserved on Surface under `MZ600-R2-OEM-PERCHAN-20261028-A`. Public records exclude any MAC, BSSID, SSID, private NVRAM or proprietary firmware payloads.

## New actual firmware readback

```text
MZ600_R2_HASH_ABI_RUNTIME_PREFLIGHT_PASS
MZ600_R2_RAM_FIRMWARE_OVERLAY_VERIFIED
MZ600_R2_OEM_2012_DIAGNOSTIC_DRIVER_WLAN0_PRESENT_NO_SCAN
MZ600_IOREAD_BANDLIST status=0 count=2 band1=1 band2=2
MZ600_IOREAD_CHANSPECS status=-52
MZ600_IOREAD_PERCHAN status=legacy channels=35 success=0 fail=35 radar=0 passive=0
Firmware: BCM4329/3 wl0: May 25 2012 17:56:21 version 4.218.248.44
Band 1
Band 2
MZ600_R2_PERCHAN_COUNTRY_SCANLESS_REPORT_COMPLETE
MZ600_R2_ORIGINAL_FW_NV_MODULE_HASHES_PASS
MZ600_R2_ORIGINAL_WIFI_RECONNECTED=1
MZ600_R2_ROLLBACK_END rc=0
MZ600_R2_TEST_SHELL_RC=0
```

Both 2.4/5GHz bands and representative 5GHz channels 36/40/44/48/149/153/157/161/165 were exposed. **No NO_IR was shown in the sampled 5GHz channel lines**, and the r2 driver imported **zero** additional firmware-reported restrictions: the optional per-channel query failed on **every one of 35** firmware-supported channels. The exact per-query *firmware* error code was **not yet recorded**; modern brcmfmac maps many proprietary firmware errors into generic Linux `-EBADE`. Do not claim that `per_chan_info` must be unsupported without a decoded readback, nor claim legal/illegal RF transmissions based on a printed flag.

**Rollback:** WCC/core/brcmutil unload 0, OEM firmware RAM bind unmount 0, installed firmware/NVRAM/core/WCC SHA PASS, original core/WCC/util reload 0, NM and WPA restart 0, original Wi-Fi reconnection PASS, COM9 released. No bootloader, partition, GPT, p7/p8/p10, TWRP or permanent driver writes. This trial did not initiate any RF scan or 5GHz association.

## Mandatory historical lookup: what we previously knew and why it matters

| Original dated evidence | What worked or was rejected | Does it apply to today's r2 failure? |
| --- | --- | --- |
| [Oct26 v05 HRI39 passive-only channel fallback](MZ600_V064_HRI39_5GHZ_WLAN0_PASSIVE_CHANNELS_PASS_ESCAN_UNSUPPORTED_2026-10-26.md); [exact earlier builder](../../scripts/experiments/build-v064-bcm4329-legacy-passive-only-wiphy-20261026.py) | When firmware lacks modern `chanspecs`, 20MHz-only, bounded firmware `WLC_GET_VALID_CHANNELS` channel list, **preserve original disabling**, set `NO_IR` on *all enabled fallback channels*; radar flags on DFS range. Actual OEM HRI39 dual-band wiphy/channel flags PASS without transmitting. | **YES as a conservative non-transmitting diagnostic fallback** when per-channel restrictions cannot be read. It does **not** establish correct permissions for ordinary association, active scanning, or all countries/firmware; cannot promote directly as final driver. |
| [Oct26 V13 newer OEM firmware-only A/B](MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md) | **24 firmware-supported 5GHz NO_IR channels**, five other 5GHz entries disabled, same 1550B NVRAM; clean physical rollback. | **YES**: direct same-firmware physical precedent. Today's 35 firmware valid channels equal V13; lost 5GHz `NO_IR` flags differ because current WIFI-01 r2 has neither blanket non-TX fallback nor valid `per_chan_info` response. |
| [Oct27 V25–V27 NO_IR and scan readiness](MZ600_V25_TO_V27_SECOND_SCAN_REGSTATE_AND_FIRMWARE_NOTUP_2026-10-27.md) | Kernel beacon hints can legitimately change `NO_IR` state. A *private lab gate* incorrectly insisted `NO_IR` must remain present and rejected scan 2; deleting only that extra gate exposed separate firmware `BCME_NOTUP`. | **Yes as a warning**: `NO_IR` is a dynamic regulatory flag and must not be treated as a permanent immutable indication in scan-policy lab scripts. Do not reproduce the obsolete private gate. |
| [Oct27 V28 native cfg80211](MZ600_V28_NATIVE_CFG80211_SCAN_AFTER_LAB_GATES_REMOVED_2026-10-27.md) | Deliberately **removed the blanket lab-only `NO_IR`** and arbitrary one-channel/500ms/passive scan admissions. First ordinary multichannel scan PASSED; second failed `-52`. Full *effective* regulatory compliance remained OPEN. | **YES, and this is why simply copying v05 into a production patch would be premature.** The viable direction must reconcile conservative behavior when firmware metadata is missing with actual cfg80211/regdb permissions, legitimate beacon hints, and normal Wi-Fi capabilities. |
| [May2012 exact firmware versus generic country A/B](MZ600_BCM4329_5GHZ_REGULATORY_FIRMWARE_CAUSAL_TIMELINE_RECHECK_2026-10-28.md) | 2012 OEM firmware already proves 5GHz bandlist; generic with US69 alone still 2GHz only. | **YES**: do not re-run consumed generic bandlist/country tests, force regrev69, or assume local custom phy country `99` itself establishes legally permitted emission. |

## Assessment and next smallest technical decision

- **WIFI-01 r2 is incomplete, not accepted.** Its new `per_chan_info` import path does not produce any firmware restrictions in this OEM ABI. A firmware iovar string present in a binary is not a working response.
- **Before a new WIFI-01 edit**, source-review the original BCM4329 firmware/legacy host API semantics and the exact `per_chan_info` invocation (including BSSCFG framing, chanspec format and error conversion); a narrow read-only numeric error trace can identify the cause if necessary. Compare the originally proven v05 passive-only flag policy and V28's consciously removed production scaffolding.
- A conservative fallback for unsupported/failed legacy metadata must not fabricate TX authorization. A truly upstream-ready normal-wifi solution needs defensible per-country and per-channel cfg80211/regdb interaction; do not use unconditional country forcing, false radar safety, regulatory bypass or blanket permanent RF capability assumptions.
- Keep issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4) OPEN for regulatory parity, [#1](https://github.com/Olsens11/XoomLinux7/issues/1) OPEN for OEM integration and 5GHz behavior, [#7](https://github.com/Olsens11/XoomLinux7/issues/7) open for firmware readiness. **No new kernel patch created simply because a new symptom was observed.**

**Owner's permanent engineering instruction:** Before treating any problem as new, first search the project for the previously attempted or validated fix, read the full context including why later work removed it, then record a reasoned reuse/revision decision. See [mandatory procedure](../process/DEVELOPMENT_WORKFLOW.md#mandatory-historical-reuse-gate-2026-10-28).
