# [RFC PATCH 0/4] wifi: brcmfmac: handle older BCM4329 firmware scan behavior

**Unsent draft. Not approved for mailing, not signed off, and not physically tested in this cleaned form.**

Some BCM4329 SDIO firmware does not support the modern `chanspecs` query,
reports an ESCAN terminal with an unmapped bsscfg index, and may enter
firmware DOWN state after its normal idle MPC policy. These behaviors
prevent ordinary Linux cfg80211 scans or subsequent scans from finishing
reliably.

This series isolates four independent logical corrections:

1. Use a bounded legacy firmware channel list only when `chanspecs`
   fails with the diagnosed unsupported-operation return, preserving
   all existing kernel regulatory restrictions.
2. Generate a nonzero per-scan ESCAN transaction ID and reject stale
   successful terminals that fail to echo the current request ID.
3. Recover a genuine successful terminal only for the sole active
   primary station and matching transaction ID when its firmware index
   does not name a live interface. Preserve partial scans, P2P and
   unrelated firmware events.
4. Restore firmware UP state only when BCM4329 is confirmed DOWN before
   ESCAN, leaving the ordinary MPC idle policy in place.

Related mechanisms were proven on a Motorola Xoom MZ600 using a different
V31 laboratory kernel, with repeated scans, WPA2, DHCP and HTTPS. That
result **must not** be attributed to this refined review-source build.
The new clean review source still needs exact hardware reproduction,
failure-path, scan-lifetime, and multi-device verification. An unrelated
~399-second initial association and legacy connection-event ambiguity
remain unresolved and are outside these fixes.

These patches are separate from Tegra board bindings/DTS, bootloader
MAC/ATAG, MMC/SDIO and BigPart storage changes, which require different
maintainer trees. No private firmware or installation tooling is included.
The recipient tree, maintainers, human DCO and actual submission are
deliberately deferred until whole-chip integration is complete.
