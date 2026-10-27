# MZ600 V14 direction: favor newer compatible dual-band OEM firmware, reuse normal brcmfmac ESCAN (source audit)

**2026-10-26. Source/repository audit only. No Xoom RF operation or new firmware trial.**

## Strategic choice

Favor the most recent *compatible and operationally qualified* Motorola/BCM4329 firmware rather than assuming the largest version number or default Linux distribution image is best. V13 owner physical PASS validated the **May 25 2012 `4.218.248.44`** firmware, SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`: real `wlan0`, firmware BANDLIST two bands, old ioctl217 35 valid channels / 11 2G + 24 5G with NO_IR-only wiphy fallback, original NVRAM unchanged and independently verified rollback. `escan` literal exists in 2012 binary, unlike original HRI39; physical ESCAN/event69 success **not yet tested**.

Do not confuse "newer" with a guarantee of full compatibility. Generic image `4.220.48.0` (build Sept 2011) supports native brcmfmac 2.4 GHz enhanced scanning but physically reported no 5GHz band even with US69 calibration A/B; its numerically larger `4.220` branch prefix does not override the more recent May 2012 timestamp and dual-band evidence of `4.218.248.44`.

## Exact Linux7 ESCAN path source checks

Read the active kernel at Desktop WSL: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`.

- `brcmf_run_escan` builds `"escan"` iovar and uses legacy ESCAN V1 request when `BRCMF_FEAT_SCAN_V2` is unavailable, otherwise ESCAN V2. The feature is probed separately in `feature.c` via `scan_ver`. Firmware `escan` ASCII presence alone does not establish V1 acceptance.
- `brcmf_escan_prep` starts with active defaults but **when `request->n_ssids==0` sets `params->scan_type = BRCMF_SCANTYPE_PASSIVE`**. The host must restrict to `iw dev wlan0 scan freq 5180 passive` and verify a single allowed NO_IR, non-DFS 20MHz channel36 on real wiphy; no SSID, probes, active scan, association or country override. A strict lab module/host guard can independently reject unsafe request shapes.
- `brcmf_init_escan` registers `BRCMF_E_ESCAN_RESULT=69` handler. `brcmf_cfg80211_escan_handler` gathers PARTIAL records then on terminal SUCCESS informs results and calls `brcmf_notify_escan_complete(cfg,ifp,false,false)`; unsuccessful statuses mark aborted. Existing `escan_timeout` is backup, not evidence of successful Event69.
- **Compatibility check:** `fwil_types.h` declares `BRCMF_BSS_INFO_VERSION=109` and `brcmf_inform_bss` refuses nonempty result lists with another version. Original HRI39 legacy IOCTL51 returned BSS **108**, while 2012 firmware BSS version is **NOT YET MEASURED**. V14 should capture sanitized version/count before assuming normal Linux BSS parser works. A later 108-to-109 support change, if justified, must be guarded and parser-reviewed rather than simply changing a constant. Event69 completion may work independently of BSS parse support.
- Candidate lacks modern `chanspecs` iovar (`-52` confirmed V13). **Do not remove the known-good legacy VALID_CHANNELS 217 enumeration fallback**. The verified v05 lab module (343200 bytes SHA `ff19d91726f406468d6cc9516d43a851f6a7a22d403259094ae376041671db29`) is a narrow passive-only NO_IR/HT20 4329 workaround and already loaded normally with 2012 candidate in V13, not installed permanently.

## Recommended next gate

Before any permanent software design decision, use a new SHA-pinned, reversible owner-operated v14 RAM-only 2012 firmware + same NVRAM + old channel fallback. Run just one **5180 MHz channel36, NO_IR, non-DFS passive 20MHz `iw scan`**, with complete original-state preflight, no probes/association, a bounded timeout, independent post-audit, and fresh event69/scan response/safe BSS version-count markers. Check error=0 vs -52, successful Event69 terminal vs timeout, and elapsed duration. If firmware advertises dual band but ESCAN fails, return to HRI39 ISCAN plan without affecting the known-good legacy scan. Test 2.4 GHz too *later* only after 5GHz scan is qualified. Do not modify installed firmware yet.

**Desktop Git checkout recovered:** fast-forward pulled committed V13 physical checkpoint and handoff update (`ff0ca35`). No physical test conducted in this decision review.

References: [V13 physical PASS](../checkpoints/MZ600_V13_2012_OEM_FIRMWARE_2G_5G_BANDLIST_PHYSICAL_PASS_CLEAN_2026-10-26.md), [2012 candidate plan](MZ600_BCM4329_2012_DUALBAND_ESCAN_FIRMWARE_CANDIDATE_PRIORITY_2026-10-26.md).
