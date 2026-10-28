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
