# BCM4329 legacy channel discovery/regulatory contract — reconstructed 2026-10-28

**Status: SOURCE MODEL + OFFLINE CONTRACT TEST ONLY.** This is not a demonstrated fix. Do not mark issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4) resolved, imply a human DCO, substitute old custom regulatory tables for the signed Linux regulatory database, or boot an unapproved test. The original exact nine-review running MZ600 and historical r1/r2/r3 candidate patch files remain unchanged. New evidence discovered after the previous physical r2 trial is included.

## Principle: reconstruct function before adapting transport

The *meaning* we must preserve is the **intersection** of (a) what the BCM4329 and exact firmware support, (b) what the firmware/board/country calibration allows, (c) what the Linux cfg80211 regulatory authority allows right now, and (d) what the driver can implement (currently conservative HT20). **Radio support != authorization to initiate radiation.** The channel restriction state must remain dynamic: Linux regulatory updates/beacon hints may legitimately change NO_IR; a private test gate requiring it to remain static caused a false failure in V25.

## Source archaeology: three successive query input formats

1. **Xoom archived Lineage Motorola Broadcom bcmdhd**, local source `recovery-bigpart-research-20261028/lineage-xoom-kernel/drivers/net/wireless/bcmdhd/wl_cfg80211.c`, `wl_construct_reginfo`, around lines 7228–7243. This version builds `u32 channel = channel_number | WL_CHANSPEC_BAND_5G` (or `BAND_2G`), calls `wldev_iovar_getint(dev, "per_chan_info", &channel)`, then interprets `WL_CHAN_RADAR` and `WL_CHAN_PASSIVE`. It **does not add BW=20 or sideband bits in this call**. Example on 5GHz channel 36: `0x1024`.
2. **Other Broadcom downstream bcmdhd implementations** (e.g. [Android BCM version](https://android.googlesource.com/kernel/msm.git/+/426a5d3eaedd6bf2459a1280984a58a358b9f776/drivers/net/wireless/bcmdhd/wl_cfg80211.c)) build `channel | BAND_5G | WL_CHANSPEC_BW_20`, sometimes convert via `wl_chspec_host_to_driver`, then use the same read-only `per_chan_info` iovar. Example ch36 before conversion: `0x1824`. A different 5GHz P2P selection path sends the raw channel number. These examples prove **multiple historical argument ABIs**, not that every BCM4329 supports all variants.
3. **Modern `brcmfmac`/Linux7**, pinned xoom-linux/linux source `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`, encodes `ch.chnum=36, band=5G, bw=20, sb=NONE` via `cfg->d11inf.encchspec`. Input to `brcmf_fil_bsscfg_int_query(..., "per_chan_info", ...)` is `0x1b24` for D11n encoding. This is the unchanged normal-path upstream convention adopted in our WIFI-01 r2/r3 fallback. The BSSCFG-index-zero host helper uses the plain iovar form; no evidence yet that a BSSCFG prefix is the rejection cause.
4. Historical firmware is the **May25 2012 Motorola OEM `4.218.248.44`**. The [actual r2 hardware test](../checkpoints/MZ600_WIFI01_R2_OEM_2012_PERCHAN_PHYSICAL_AND_HISTORY_2026-10-28.md) returned `chanspecs=-52`, `GET_VALID_CHANNELS=35` (11×2.4, 24×5), and **zero of 35 `per_chan_info` query calls succeeded** with the modern full-chanspec argument; the raw vendor error code and alternative argument-format acceptance have not yet been recorded. The firmware string table alone is not proof of a supported ABI.

### Comparative read-only candidate arguments (NOT yet physically tested)

| Channel | Historical Xoom band+channel | Intermediate band+BW20+channel | Modern D11n full HT20 chanspec |
| --- | --- | --- | --- |
| 2.4GHz ch11 | `0x200b` | `0x280b` | `0x2b0b` |
| 5GHz ch36 | `0x1024` | `0x1824` | `0x1b24` |

All are **query payload hypotheses**, not commands to set a channel, change the country, scan, or initiate TX. The old 2012 Motorola firmware may reject all of them. Each result must include decoded firmware error/status and response flags (no SSID/BSSID/MAC).

## Original regulatory design is NOT necessarily an acceptable modern policy

- Old `bcmdhd` `wl_construct_reginfo` consumed `chanspecs`; when available it translated radar to `IEEE80211_CHAN_RADAR|NO_IBSS` and passive to `PASSIVE_SCAN|NO_IBSS`, i.e. *older kernel-era forms of constraints expressed by `RADAR` and `NO_IR` today*.
- On `chanspecs` unsupported, that old routine returned an error; old `wl_update_wiphybands` **ignored `BCME_UNSUPPORTED`** and continued using its pre-existing static band structures. Separately old `wl_get_valid_channels` used `WLC_GET_VALID_CHANNELS` for scan channels. This means the old source **is not proof that `per_chan_info` ever succeeded on the May2012 firmware**.
- Old Xoom `bcmdhd` also calls `wiphy_apply_custom_regulatory(wiphy, &brcm_regdom)` with alpha2 `99`. Its historical regdomain intentionally relaxed world 5GHz passive/P2P restrictions across broad ranges (source comment). **Do not copy that table or permit scan/TX on the basis that OEM once did so**. Linux cfg80211, a trustworthy regulatory database, firmware country/OTP/NVRAM and valid DFS support must govern actual operations. Source at local archived `wl_cfg80211.c` lines 80–112, 7280–7340.
- `WL_CHAN_VALID_HW`, `VALID_SW`, `RADAR`, `INACTIVE`, `PASSIVE`, and `RESTRICTED` bits exist in matching OEM `wlioctl.h` and current Linux `brcmu_wifi.h`. **Do not reinterpret `VALID_SW`, `INACTIVE`, or `RESTRICTED` as a new transmit permission without actual ABI response samples and documented semantics.** A channel returned by `GET_VALID_CHANNELS` is an enumeration input, not a complete channel-specific DFS/power permission oracle.

## Proposed Linux7 compatibility boundary

```text
WLC_GET_BANDLIST ---------------> physically advertised bands only
          |
Modern chanspecs? ---yes--------> existing normal brcmfmac channel path unchanged
          |
          no (-EBADE) and BCM4329 only
          v
WLC_GET_VALID_CHANNELS ---------> bounded channel-number inventory
          |
          +-- unknown/not reported -> DISABLED
          +-- reported -> preserve existing flags, support HT20 only
                             |
                             +--> choose verified, generation-specific
                                  read-only per_chan_info encoding
                                        |
                                        +--> successful, semantically valid
                                        |    firmware flags: OR RADAR/NO_IR,
                                        |    preserve other restrictions
                                        |
                                        +--> no trustworthy info: do NOT
                                             infer active-TX permission.
                                             Defer to regdb and conservative
                                             NO_IR/non-TX diagnostic mode
                                             until model verified.
Final authorization = intersection of hardware, firmware board/country,
                     regulatory state, and driver capability.
```

- Unsupported query **does not** justify clearing NO_IR or making a blanket unsupported 5GHz band available. Existing WIFI-01 r3 applies NO_IR to 5GHz when per-channel firmware metadata is missing; this is an **unsigned source-only defensive candidate** and not necessarily final production policy, particularly for beacon hints and normal association.
- Validate that a *success* response contains meaningful flags rather than mistaking the query input echoed back for metadata. Examine the raw vendor status, length, endian semantics and whether the driver query path is using bsscfg index zero. Never change country codes or disable cfg80211 rules to make an IOCTL succeed.
- This research **belongs within an amended WIFI-01** if the verified fix is legacy channel metadata interpretation. Distinct scan Event69 routing and firmware-up/MPC readiness remain WIFI-02/03/04, not part of this change.

## Explicit acceptance gates before an r4 kernel proposal

1. **Pure offline fixture tests**: 3 argument formats, bit-flag combinations, unknown channels, unavailable metadata, valid/disabled original flags, passive/DFS/inactive and broad vs narrow bandwidth restrictions. The fixture is a **contract sketch**, not a production kernel test. See [Python model tests](../../tools/tests/test_bcm4329_channel_contract.py).
2. **Source-only diagnostic**: introduce a separate lab-only read-only `per_chan_info` format A/B. Use actual OEM firmware `4.218.248.44`, its original board-specific 1550B NVRAM and matched module; capture `BRCMF_C_GET_VAR` raw firmware status and bounded numeric result for 2.4GHz ch11 and 5GHz ch36 using each documented format, without any scanning or AP association. Capture input and response endian and whether returned metadata carries known `VALID_HW/SW` bits.
3. If one documented format works, refine existing WIFI-01 and **remove any fallback scaffolding made unnecessary**. If all three are unsupported, document firmware's actual API limitation and use only independently justified regulatory restrictions: ordinary cfg80211 rules with a conservative no-TX default for unknown firmware-specific permissions. Do not invent a fake `per_chan_info` response, copy the old custom alpha2 `99` regdomain, or force US/69.
4. **Kernel-level** source, fault-path, real wiphy flags/DFS/passive/reassociation/regulatory update, repeat scan and MZ604 regression acceptance. Fresh nonreplayed owner-approved one-shot with SHA-pinned temporary modules and full radio/network rollback. No automatic boot/flash before test authorization and preflight.
5. Document result in [GitHub #4](https://github.com/Olsens11/XoomLinux7/issues/4) and [#1](https://github.com/Olsens11/XoomLinux7/issues/1); source-only versus tested-on-device must be explicit.

## Primary external references (read-only, not patches to copy)

- [Android Broadcom legacy `wl_iw.c`: WLC_GET_VALID_CHANNELS](https://android.googlesource.com/platform/hardware/broadcom/wlan/+/b4ace791eb574f589c53be582ea0d14e1a85ff09/bcm4329/src/wl/sys/wl_iw.c)
- [Downstream Broadcom `per_chan_info` with BW20](https://android.googlesource.com/kernel/msm.git/+/426a5d3eaedd6bf2459a1280984a58a358b9f776/drivers/net/wireless/bcmdhd/wl_cfg80211.c)
- [Current Linux cfg80211 channel flag and `orig_flags` semantics](https://docs.kernel.org/next/driver-api/80211/cfg80211.html)
- [Linux brcmfmac driver history](https://kernel.googlesource.com/pub/scm/linux/kernel/git/soc/soc/+/a1467faa10414ab3d91be7ef6d2b11272ec00e95/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c)

**Source-based conclusion:** A change in **query encoding** is a documented plausible explanation for the observed 0/35 r2 failures. It is not yet a tested fix. The second necessary property is correct **regulatory behavior when firmware metadata cannot be read**, not an ability to make the firmware accept every command.
