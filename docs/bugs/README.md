# BCM4329 / Linux 7 evidence-backed issue ledger

**Snapshot as of 2026-10-28.** These are **internal project bug/investigation reports**, not Linux upstream submissions or claims of causal attribution to the existing nine patches. Each issue names reproducible physical symptoms, competing explanations, an evidence source and an acceptance gate. Public logs exclude SSIDs, MAC addresses, IPs, serials, credentials and proprietary firmware. Preserve each report when later tests revise its conclusion; add dated findings, do not silently delete negative evidence.

| ID | Topic | Classification as of report | Severity |
| --- | --- | --- | --- |
| [WIFI-BUG-01](WIFI-BUG-01-MISSING-5GHZ-PHY-BAND_2026-10-28.md) | Missing advertised 5GHz PHY band despite dual-band target | Confirmed limitation, patch attribution open | Medium |
| [WIFI-BUG-02](WIFI-BUG-02-STATION-TELEMETRY_2026-10-28.md) | nl80211 station metrics absent/legacy ASSOCLIST unsupported | Confirmed reporting gap, ABI cause open | Medium-low |
| [WIFI-BUG-03](WIFI-BUG-03-REGULATORY-TXPOWER-REPORTING_2026-10-28.md) | country 99 vs global US and 20/31 dBm display | Reporting discrepancy, RF effect unproven | High-investigate |

**Later corroboration:** An independent fresh Surface scan observed a genuine nearby 5 GHz BSS on channel 153 (5765 MHz) as well as related 2.4 GHz networks on channel 11. The Xoom advertises only 2.4 GHz. The user confirms SSID naming does not indicate actual radio band. See WIFI-BUG-01 for independent host evidence.

**Additional observations not yet bug tickets:** One ~1s reassociation recorded during Bluetooth lab; the older WPA AP has mixed WPA/TKIP capabilities but no proof current connection is using TKIP; stale `scan dump` cache does not prove an ESCAN failure; power-save ON without idle-battery or suspend measurement. Promote only after isolated reproduction. Main test evidence: [formal nine-review audit](../checkpoints/MZ600_REVIEW9_EXACT_PATCH_WIFI_BACKEND_FORMAL_AUDIT_2026-10-28.md), plus [active dated project snapshot](../ACTIVE_TEST_STATE.md). Next hardware test must be owner-approved and reversible.
