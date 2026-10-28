> **Provenance update, 2026-10-28:** No issue reported against [xoom-linux/linux](https://github.com/xoom-linux/linux/issues), and no proof that the observed values are caused by our nine patches. The original regulator/firmware-to-cfg80211 logic largely persists, but active firmware/NVRAM behavior is still unmeasured. This is an **unexplained runtime discrepancy**, *not* a demonstrated upstream regulatory violation or newly introduced bug. Separately investigate [our WIFI-01 legacy-channel review concern](WIFI-REVIEW-04-LEGACY-CHANNEL-REGULATORY-PARITY_2026-10-28.md). See [provenance audit](../checkpoints/MZ600_NINE_PATCH_UPSTREAM_PROVENANCE_AND_LATENT_ISSUES_AUDIT_2026-10-28.md).

# WIFI-BUG-03 — BCM4329 per-PHY country and TX power values require reconciliation

**State (2026-10-28):** REPORTING DISCREPANCY CONFIRMED; actual regulatory misconfiguration, wrong conducted output power, illegal emission or a patch regression **NOT PROVEN**. **Priority: high for investigation before expanded 5 GHz testing or upstream acceptance.**

**Observed:** `iw reg get`: **global country US DFS-FCC** and **phy0 country 99 DFS-UNSET**. `iw phy phy0 info`: usable 2.4GHz channels advertise **20 dBm**. `iw dev wlan0 info`: **txpower 31.00 dBm**. Firmware log: no CLM blob (`err=-2`, limited channels possible) and no txcap blob (`err=-2`). Exact firmware BCM4329/3 `4.220.48`. `99` can denote a driver-managed / unknown specific regulatory identifier; it is not automatically a kernel bug. Kernel cfg80211 channel limits and firmware reported nominal TX power can differ; **no real RF emission measurement was taken**.

**Read-only reproduction:**
```sh
iw reg get
iw phy phy0 info | grep -E '240[0-9]|2462 MHz|dBm'
iw dev wlan0 info | grep txpower
dmesg | grep -E 'clm_blob|txcap_blob|Firmware: BCM4329'
```

**Investigation:** Compare actual NVRAM ccode/regrev calibration against OEM regional evidence in private lab, inspect firmware `country` and `qtxpower`/valid-channels using approved **read-only** driver IOCTLs, and trace cfg80211 country translation. Distinguish reported nominal TX output from cfg80211/effective regulatory and physical transmit behavior. Check global↔per-wiphy restrictions under `iw reg get`, DFS/NO_IR and antenna/power constraints. **Do not set US69, force regulatory domains, or enable channels** without validated mapping, firmware and per-device authorization.

**Acceptance:** Consistent, explained reporting and demonstrably enforced band/channel/EIRP limits within tested regulatory domain. No route should increase allowed transmission because of driver test. Check against firmware/NVRAM provenance before any upstream submission.

**Evidence:** [Formal exact-source audit](../checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md); proprietary firmware/NVRAM remain private.
