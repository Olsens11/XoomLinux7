# [RFC PATCH 0/3] wifi: brcmfmac: support older BCM4329 channel and ESCAN behavior

**Unsuitable for mailing as-is: unsigned/unattributed, clean-source hardware test OPEN.**

The Linux 7 `brcmfmac` driver does not complete ordinary multichannel
scans reliably with a Motorola-era BCM4329 SDIO firmware. The older
firmware does not implement `chanspecs`, provides the older
`WLC_GET_VALID_CHANNELS` list, returns ESCAN Event 69 with an
unmapped bsscfg index for some genuine successful completions, and
allows firmware UP state to drop under the normal idle MPC policy.

The three logical changes below are limited to BCM4329 and preserve
normal paths for other chips. The channel fallback narrows support
without bypassing cfg80211 regulatory restrictions. The generation
and owner handling is a single scan-lifetime change: an ESCAN terminal
is delivered to the sole active primary STA only if its 16-bit
transaction ID is current. Firmware readiness is restored only on
demand before subsequent ESCAN, leaving ordinary idle MPC intact.

On a Motorola Xoom MZ600, a *different V31 lab source* using these
mechanisms completed repeated hardware ESCAN, WPA2 association,
DHCP, NTP, DNS and HTTPS. After one reboot automatic association
succeeded at ~399s: repeated authentication timeouts and dropped
legacy SET_SSID/LINK events still need investigation. This RFC source
is **not** claimed to reproduce the precise lab binary and has not
yet been run on the device.

Proposed patches:
1. wifi: brcmfmac: use legacy channel list on BCM4329
2. wifi: brcmfmac: match BCM4329 ESCAN completion to active scan
3. wifi: brcmfmac: restore BCM4329 firmware readiness for ESCAN

Please do not interpret this cover draft as a submitted or signed
patch series. Kernel-style series and validation manifest are beside
this document. Final recipients, base tree and DCO remain to be
confirmed by the human contributor.
