# WIFI-BUG-02 — Associated-station statistics unavailable through nl80211 / brcmfmac

**State (2026-10-28):** RUNTIME TELEMETRY GAP CONFIRMED; whether legacy firmware inability or host driver defect **OPEN**. **Priority: medium-low.** Potential area `brcmfmac/cfg80211.c` get/dump station; independent of Wi-Fi patches 01–04 until a causal test.

**Observed:** `wlan0` managed STA associated with AP at 2462MHz; `iw dev wlan0 link` includes association/frequency but **no signal or TX bitrate**; `iw dev wlan0 station dump` produces **no station entries**. Earlier kernel log states `brcmf_cfg80211_dump_station: BRCMF_C_GET_ASSOCLIST unsupported`. `iw dev wlan0 scan dump` shows a cached BSS -63 dBm **from approximately 48 minutes earlier**; cache signal is not current link signal. NetworkManager does reconnect and DHCP works, so this is not proof of broken data transport.

**Repeat safely:**
```sh
iw dev wlan0 link
iw dev wlan0 station dump
dmesg | grep 'GET_ASSOCLIST unsupported'
```

**Investigation:** Examine get_station/dump_station separate code paths in exact Linux 7 source and supported legacy firmware IOCTLs. Determine if `BRCMF_C_GET_ASSOCLIST` is appropriate for client STA vs AP, and whether simpler per-peer `WLC_GET_RSSI` and rate information can be reported through nl80211 without guessing data. Avoid fallback whose output is fabricated or which breaks AP/P2P. Preserve Linux cfg80211 station API semantics; test all supported interface modes and error propagation.

**Acceptance:** Per-station statistics displayed correctly where firmware can supply them; otherwise gracefully report unsupported without misleading values or unrelated kernel log spam. Repeat with known RF changes to verify freshness.

**Evidence:** [Exact-source audit](../checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md); actual MAC and nearby device IDs in private Surface receipts, not Git.
