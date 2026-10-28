# MZ600 V31 — first boot-persistent full network stack verified

**Date:** 2026-10-28 UTC (2026-10-27 evening US/Eastern). **Status:** PHYSICAL PASS for eventually automatic full connectivity on a single controlled reboot; significant slow-association issue remains OPEN. Private router identities, password, BSSIDs and MAC addresses are not included here.

## Test provenance and non-invasive remote access

The owner first rebooted the Motorola Xoom MZ600 from a USB COM9 root console after installing persistent per-interface WPA, networkd DHCP and timesyncd services. The same boot was later inspected remotely through **SURFACE-BOOK-2 Desktop Commander → USB Serial COM9** using a dedicated read-only pyserial tool on the Surface at `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V31-PostBoot-COM9-ReadOnly-20261028.py` (115200 baud, explicit start/end marker, no reboot, module reload, network restart or password reads). The read-only COM9 tool reports sanitized/aliased MAC and SSID fields. The final successful connection occurred without any owner or agent Wi-Fi restart during this boot.

## End-to-end LIVE PASS (approximately 20 minutes of uptime)

| Gate | Physical observation |
| --- | --- |
| Internal boot/kernel | `uname -r` = `7.0.0-next-20260422+` |
| Rootfs | `/dev/mmcblk0p8 ext4` |
| Installed V31 module options | `/sys/module/brcmfmac/parameters/mz600_generation` = `Y`; `mz600_terminal_owner` = `Y` |
| Persistent services | `wpa_supplicant@wlan0`, `systemd-networkd`, `systemd-timesyncd` all **active** after boot |
| WPA2 | `wpa_state=COMPLETED`; `key_mgmt=WPA2-PSK`; `pairwise_cipher=CCMP` |
| DHCP4 | `wlan0 UP 192.168.0.9/24`; `default via 192.168.0.1 dev wlan0 proto dhcp` |
| DNS | `getent ahostsv4 example.com` resolved to a public IPv4 address |
| Time | `timedatectl show -p NTPSynchronized` = **yes** |
| Real TLS/HTTPS | `curl -fsS ... https://example.com/` → **HTTP 200; `ssl_verify_result=0`** |

These observations **prove boot-persistent automatic networking eventually succeeds**, not that it connects promptly or has been repeatedly reboot-tested. Previous same-installation HTTPS success was pre-reboot; this is a *new* independent post-reboot end-to-end check.

## Exact WPA & networkd timeline: severe delay

Using `journalctl -b -u wpa_supplicant@wlan0 -o short-monotonic` and networkd's monotonic logs avoids timestamp skew from NTP corrections:

- **7.054s:** interface-specific wpa_supplicant service started.
- **10.491s:** first association attempt.
- **20.547s, 33.797s, 46.974s, 60.203s, 83.554s, 127.947s, 190.373s, 301.072s:** eight ~10-second **`Authentication with ... timed out`** outcomes; retries become widely spaced due WPA BSSID/SSID temporary ignore and exponential backoff.
- **398.707s:** ninth association attempt.
- **399.082s:** `WPA: Key negotiation completed ... [PTK=CCMP GTK=TKIP]`; **399.083s** `CTRL-EVENT-CONNECTED`.
- **399.084s:** networkd gained carrier.
- **399.204s:** DHCPv4 address and default gateway acquired.

Thus Wi-Fi connectivity took **6 minutes 39 seconds** from boot, and the DHCP lease followed association in **~0.12 seconds**. Both observed BSSID candidates had timeout attempts; the eventual successful candidate was **the same anonymized AP_1** that previously timed out repeatedly. Avoid claiming a single permanently bad AP or DHCP/NTP slowness.

## Firmware driver event correlation

V31's repeated ESCAN completion remains physically proven, with `SCAN_COMPLETION aborted=0 fw_abort=0 owned=1`. After idle MPC1, firmware was observed `fw_up=0`; V31's conditional `WLC_UP sent=1 rc=0` restored it before scans; no always-on radio workaround was required.

During an unsuccessful ninth-minute-ish attempt around **291s** monotonic, Broadcom `BRCMF_E_SET_SSID` **event code 0, status=0**, arrived, and event worker discarded it due `raw_bsscfg=42` at 291.343s; WPA still timed out around 301.072s. During the **successful** final attempt, `BRCMF_E_LINK` **event code 16, status=0**, arrived at 398.925s and was **also discarded** due `raw_bsscfg=29`; nonetheless `networkd` reported the AP connected and WPA2 handshake completed by 399.083s. So invalid legacy event indices are genuine but **not sufficient alone** to explain success/failure. Do not broadly reroute event codes 0 and 16 to the primary interface without additional validation.

Note: V31's `MZ600_V31_HEADER` diagnostic logs were intentionally scoped to **Event 69**, so an empty grep for `MZ600_V31_HEADER code=(0|16)` does not indicate that 0/16 events lacked headers. If future instrumentation is needed, inspect raw version, flags, ifidx, bsscfg, packet length and primary-STA ownership using narrowly gated logs.

## Current status / next experiment

1. **Do not rebuild or flash because of the delay**; p7 boot and Debian p8 are working.
2. Preserve the live connected condition and capture baseline WPA/driver status before any experiment.
3. Perform source-level analysis of the core Broadcom event parser and legacy firmware message format, and distinguish missing notification of *successful auth* from true air-interface authentication failure; capture event-header variants only with an isolated, reviewable diagnostic build or safe trace method.
4. For any subsequent controlled reconnect tests, record monotonic attempt time, AP alias, firmware `UP`/MPC state, event status/flags/index and transition to netcarrier. Keep one logical change per patch and do not disguise lab diagnostics as upstream-ready code.
5. After root cause is identified, verify stable quick reconnection across multiple boots/devices; full auto-connect **persistence PASS** is distinct from **connection latency/reliability OPEN**.

## Source-level follow-up: historical event format and firmware readiness

The pinned Linux7 `drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h` defines `struct brcmf_event_msg_be` with **unconditional trailing `ifidx` and `bsscfgidx` bytes**. The local `fweh.c` worker rejects any event with `bsscfgidx >= BRCMF_MAX_IFS` before `brcmf_notify_connect_status` can process it. The local `cfg80211.c` registers **Event0 `BRCMF_E_SET_SSID` and Event16 `BRCMF_E_LINK`** to `brcmf_notify_connect_status`; `brcmf_is_linkup` may treat `SET_SSID+SUCCESS` as a successful connection, while LINK flags can represent down or other changes. This makes the lost 291.334s SET_SSID event a strong, specific explanation for at least one timeout, but the ~398.925s LINK drop during successful connection prevents a blanket inference for Event16.

A dated Broadcom bcmdhd interface header has an explicitly distinct **`wl_event_msg_v1_t` (without ifidx or bsscfgidx)** alongside the extended `wl_event_msg_t` (with both fields), and defines `WLC_EVENT_MSG_UNKBSS`/`UNKIF` flags: https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/proto/bcmevent.h . The current brcmfmac header convention includes both trailing indices: https://github.com/torvalds/linux/blob/master/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h . **Hypothesis only:** the legacy Motorola BCM4329 may occasionally send a v1-format/otherwise nonconforming connection event that our v2-assuming parser interprets as arbitrary `bsscfgidx`. The version and actual packet length of Event0/Event16 **have not been measured**; Event69 logged version2, and V31 does not log HEADER for code0/16. Do not claim a v1 event occurred without inspecting it.

The local `brcmf_cfg80211_connect()` checks `check_vif_up()` (host-side interface status) then submits an extended `join` request; it **does not explicitly read WLC_GET_UP and restore firmware UP** in this path. V31 restores firmware UP for **ESCAN**, not necessarily `connect`. Firmware `fw_up=0` after idle MPC1 is an independently measured state, so connect-path firmware readiness remains a distinct plausible hypothesis; however, during a failed attempt at 291s the preceding scan completed with `fw_up=1`, so MPC alone is **not** an adequate explanation for all timeouts.

**Upstream-quality next diagnostic** (not yet implemented): narrow, read-only kernel diagnostic for Event0/Event16 raw `version`, `flags`, `ifidx`, `bsscfgidx`, `pktlen`, `datalen`, active-primary-STA state and connection ownership, with no SSIDs, MACs, PSKs or payload dumps. Compare failing vs passing connections and only then decide whether an independently scoped compatibility patch (possible WIFI-5) is justified. Avoid forwarding all invalid-index events, fabricating kernel notifications or disabling MPC globally.
