> **HISTORICAL EXPERIMENT RECOVERED, 2026-10-28:** [Full experimental proof timeline](../checkpoints/MZ600_BCM4329_5GHZ_REGULATORY_FIRMWARE_CAUSAL_HISTORY_RECONCILIATION_2026-10-28.md). Oct26 baseline diagnostic physically established generic 4.220.48 `BANDLIST count=1 first=2`, not merely inferred from `iw`. Same firmware plus RAM-only OEM `US69` NVRAM bootstrap STILL one 2G band. **May2012 OEM firmware 4.218.248.44** used with UNCHANGED 1550B NVRAM produced `BANDLIST count=2 first=1 second=2`, 11 2G +24 5G valid channels, and later real native 5GHz ESCAN SUCCESS V17. V28 normal 12-BSS scan first request PASS; second-scan readiness/BCME_NOTUP remained open. Therefore #1 is specifically the **currently installed firmware choice / exact-nine integration**, not inability of BCM4329 hardware or original driver to expose 5G. Do not repeat old one-shots; r2 + known 2012 firmware remains untested physically.

> **Baseline provenance update, 2026-10-28:** `WLC_GET_BANDLIST` decides whether 5GHz Band 2 is allocated in the original `brcmfmac` source; it is unmodified by our nine patches. Earlier HRI39 4.218 firmware proved valid 5GHz channels on Linux, while this boot uses 4.220 firmware. **No public xoom-linux/linux issue filed** as of tracker check. Thus current 5GHz absence is a newly reproduced *integration symptom* with firmware/board/driver causality still open; it is **not yet an introduced patch regression**. See [upstream provenance audit](../checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md).

> **Historic causality evidence clarified (2026-10-28):** [Four-condition physical firmware+regulatory review](../checkpoints/MZ600_BCM4329_5GHZ_REGULATORY_FIRMWARE_CAUSAL_TIMELINE_RECHECK_2026-10-28.md). This **generic firmware's missing 5GHz band is not an unmeasured hypothesis**: count1 band2 = 2.4GHz, and effective USrev69 did not change it. HRI39 first dual-band trial combined OEM firmware and OEM US69; separate May2012 4.218.248.44 OEM **firmware-only** A/B with unchanged installed calibration showed count2 IDs1(5GHz)+2(2.4GHz). Regulatory does affect legal channels and subsequent NO_IR lab test state, but is **not sufficient as a generic firmware 5GHz unlock**. Reprioritize validated OEM dual-band and ESCAN state instead of redundant generic bandlist boot.

# WIFI-BUG-01 — No 5 GHz band advertised by BCM4329 PHY in exact nine-review Linux 7

**State (2026-10-28):** PHYSICAL CAPABILITY GAP CONFIRMED; **source patch regression NOT demonstrated**. **Priority: medium** to complete dual-band acceptance. **Track:** WIFI-01/WIFI-05 + firmware/BCM4329 bandlist, PHY capabilities; cross-check DT/REG. **No live fix attempted.**

**Expected:** A supported/calibrated BCM4329 dual-band device should advertise firmware-supported and legally permitted 5 GHz channels through cfg80211; a 5 GHz connection should use a 5 GHz frequency. Do not promise all bands unless this firmware/board calibration supports them.

**Observed:** `iw dev wlan0 info` and `iw dev wlan0 link` show channel 11, **2462 MHz**, 20 MHz, while the network's name happens to contain “5G”. `iw phy phy0 info` lists **Band 1** with 2.4 GHz channels but **no Band 2**. Global US rules include 5 GHz but cannot invent a firmware/hardware band. The device is connected and DHCP/HTTPS works; that does not prove 5 GHz. Actual firmware reports BCM4329/3 revision **4.220.48 (2011)**. Older historical experiments used other firmware revisions; compare exact versions before inferring a regression.

**Repeat (read-only):**
```sh
iw dev wlan0 info | grep -E 'channel|freq'
iw dev wlan0 link | grep freq
iw phy phy0 info | grep -E 'Band [12]:|5180 MHz|2462 MHz'
dmesg | grep -F 'Firmware: BCM4329'
```

**Potential mechanism (not yet proven):** Original firmware `WLC_GET_BANDLIST` advertises only 2.4GHz, regulatory/chip board selection or calibration insufficient, or a driver branch fails to construct Band 2. WIFI-01's bounded legacy `WLC_GET_VALID_CHANNELS` fallback **only disables unsupported channels in already-present wiphy bands** and cannot create a missing Band 2; do not blame that fallback solely on this evidence. Verify firmware bandlist through safe, read-only IOCTL, correct firmware/NVRAM provenance, and cfg80211 setup path; compare known previous 5GHz valid-BSS proof. **Do not add channels artificially or bypass regulatory controls.**

**Independent AP evidence — Surface Windows WLAN fresh scan 2026-10-28:** The same nearby SSID appears on **5 GHz channel 153 / 5765 MHz** and **2.4 GHz channel 11 / 2462 MHz**. A second similarly named SSID without the suffix appears on **2.4 GHz channel 11 / 2462 MHz**. User confirms naming is historical convenience and *not* intended as band truth. The Surface directly demonstrates that a real in-range 5 GHz AP exists; the Xoom itself only advertises 2.4 GHz in this exact image. The AP discovery is not evidence of Xoom 5GHz support and does not identify the exact reason Band 2 is absent. Host private scan prints SSIDs; public issue records only the channel/frequency and generic aliases.

**Acceptance:** On exact source and licensed firmware, legitimately advertise tested 5 GHz channels, complete approved passive scan and 5 GHz association, correct restricted-channel flags. Test both 2.4 and 5 GHz and resume old 2.4 baseline. No Wi-Fi disconnect/reload without owner hardware access and rollback gate.

**Evidence:** [Formal source/hardware audit](../checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md). Full identifying logs private on Surface.
