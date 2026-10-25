# MZ600 BCM4329 regulatory provenance audit and safe implementation plan

**Date:** October 25, 2026  
**State:** OEM and Linux 7 source reviewed, live Debian PHY queried read-only; official signed regulatory package downloaded and transferred to /tmp on tablet (SHA verified). **NO country/regrev settings changed, package not installed, radio not brought UP, no RF scans/association/transmissions initiated.** Existing Debian Bookworm on microSD and Android/TWRP on eMMC preserved.

## Evidence levels and hardware

Physical: replacement Verizon Motorola Xoom MZ600 / Stingray with BCM4329 rev3, clean upstream brcmfmac, Debian 12.15 and Linux 7.0.0-next-20260422. Already achieved real microSD Debian root, COM9 `ttyGS0` login, working factory MAC FDT-to-wlan0 match, separate `brcmfmac_wcc`, and `wlan0` DOWN.

### Original Motorola calibration: two independent production archives agree

Private Pi reference paths (do not publish files wholesale; original MAC/default identity information is sensitive):
- `/home/ps2/xoom-phase1/private/oem-reference-20261021/analysis/extracted-files/MZ600_HRI39/selected-oem-binaries/etc__wifi__bcm4329.cal`
- corresponding `MZ600_HRI66` path.

Extracted only the non-identity regulatory and board parameters:

| Parameter | HRI39 | HRI66 | Meaning/notes |
| --- | --- | --- | --- |
| `ccode` | `US` | `US` | Original US-market MZ600 firmware country |
| `regrev` | `69` | `69` | Broadcom firmware-specific regulatory revision, **not** a Linux wireless-regdb revision |
| `cctl` | `0x0` | `0x0` | Additional SROM field; don't invent meaning |
| `boardflags` | `0x200` | `0x200` | Board layout/calibration |
| `boardtype` | `0x4ff` | `0x4ff` | Board definition |
| `boardrev` | `0x10` | `0x10` | Board revision |
| `xtalfreq` | `38400` | `38400` | 38.4 MHz |
| `aa2g` / `aa5g` | `1 / 1` | `1 / 1` | Antenna/calibration fields, not runtime PHY proof |
| `pa0maxpwr` | `58` | `58` | Encoded 2.4 GHz calibration max power; **not 58 dBm** |
| `pa1maxpwr` | `42` | `42` | Encoded 5 GHz calibration max power; **not 42 dBm** |

Our published, identity-free calibration `configs/os/brcmfmac4329-sdio.stingray-calibration-no-identity.txt` preserves board PA/flags but deliberately **omits `ccode` and `regrev`** (and MAC) from early isolated bring-up experiments. Linux 7 firmware running today is BCM4329 r3 Broadcom 4.220.48 dated September 2011, not necessarily byte-identical to the oldest shipped Motorola WLAN firmware. Thus `US/69` is a **strong OEM candidate**, but should not be assumed confirmed under the newer 4.220.48 firmware until the embedded firmware country iovar accepts/readbacks that tuple.

### Current live Linux regulatory snapshot — PHYSICAL, read-only, no RF tests

- `/usr/sbin/iw reg get`: global **`country 00: DFS-UNSET`** (Linux world rules); `phy#0 country 99: DFS-UNSET` is Broadcom **custom driver regulatory domain**. **`99` is not an ISO country**, and does not certify a device for unrestricted transmission.
- `/usr/sbin/iw phy phy0 info`: **2.4 GHz channels 1–11 available**, each reported `20.0 dBm` maximum in the PHY table; channels **12, 13 and 14 disabled**. No 5 GHz frequencies were listed in this live PHY output. The reported 20 dBm is a software channel ceiling, not measured output nor proof that PA calibration allows that level.
- `wlan0` is present but **DOWN**. The driver reports no `clm_blob` and `txcap_blob` (err=-2), with a possible channels limitation. Source `brcmfmac/common.c` handles their absence as **nonfatal** (returns 0). This older firmware may have bundled its regulatory tables; **do not graft arbitrary modern CLM or TXCAP blobs** to silence messages.
- `/sys/module/cfg80211/parameters/ieee80211_regdom` contains `00`. `/lib/firmware/regulatory.db*` / `/usr/lib/firmware/regulatory.db*` absent in the running Debian root at audit time.
- With original firmware and US market provenance, a **conservative 2.4 GHz ch1–11, 20 MHz** operation policy is a good first test target. It is not a declaration that the channel table alone satisfies all US transmit power/antenna limits. No RF testing or setting changes were performed.

### Why `iw reg set US` alone does not solve BCM4329

Pinned Linux source `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`:
- Lines 219–234 build a static custom `brcmf_regdom` with `alpha2="99"`, registering rules including a Japan-only channel-14 entry and 5 GHz rules. The live PHY independently restricts channels further, so the static rule is **not** proof that those channels are operable or permitted.
- Lines 8374–8377 register a `reg_notifier`, set `REGULATORY_CUSTOM_REG`, apply the custom domain.
- Lines 8240–8280 show that a requested ISO country must be translated then sent through **firmware `country` iovar** (and country setting can be rejected).
- The fallback `brmcf_use_iso3166_ccode_fallback()` (lines 7945–7958) is **not enabled for BCM4329 by chip ID**. Without board country mappings or `brcm,ccode-map-trivial`, it returns `-EINVAL` and cannot reliably set firmware country from a generic userspace hint.
- `of.c` lines 17–66 parse `brcm,ccode-map` Device Tree strings formatted `ISO2-FIRMWARE2-REV`, for example `US-US-69`; child node must be compatible `brcm,bcm4329-fmac` (lines 124–127). **A minimal MZ600-specific DT mapping is viable and matches OEM evidence. Do not add a universally hardcoded US-only map to every Xoom variant.**

### Signed Debian wireless regulatory database — OFFLINE validated

Debian Bookworm (armhf/all) `wireless-regdb` **2026.05.30-1~deb12u1**. Origin: the user's Debian armhf staging tree with signed apt repository indexes (the same Bookworm release as installed Debian). Downloaded by `apt-get download wireless-regdb` inside the rootfs environment; `.deb` SHA256:

`3ff60d4ebc84fa4e202ce6359da3816a48ec1ea06b0820fdffda0396f33002c9`, size **12,556 bytes**.

The Debian archive provides **`/lib/firmware/regulatory.db-upstream`** (6380 bytes) and **`regulatory.db.p7s-upstream`** (1085 bytes) plus Debian-signed alternates. An OpenSSL detached CMS content-signature verification of the upstream DB/PKCS#7 pair passed offline. **Cryptographic content-signature validation without trust-chain anchoring does not itself prove the running custom kernel has accepted that signer yet.**

The compiled custom Linux kernel has `CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y` and `CONFIG_CFG80211_USE_KERNEL_REGDB_KEYS=y`; source cert entries include `sforshee.hex` and `wens.hex`. Official Debian documentation says custom upstream-built kernels should select upstream-signed regulatory.db through `update-alternatives`. Do **not** disable signature enforcement.

**Safe transfer proof:** package securely copied via user's pre-authorized LAN from WSL to Surface and then byte transferred over working Linux USB COM9 into `/tmp/xoom-wireless-regdb-20261025.deb`. Physical tablet SHA256 **matched** `3ff60d4e...`. No root action was required for staging. **Installation via privileged remote console was blocked by the access safety controls and therefore NOT performed; never claim installed.** The staged package is ephemeral `/tmp` data and may disappear upon reboot.

## Proposed qualified implementation (NOT YET APPLIED)

1. **Debian userspace:** install the verified official Debian `wireless-regdb` package using an authorized privileged terminal. Select `/lib/firmware/regulatory.db-upstream` through Debian `update-alternatives --set regulatory.db /lib/firmware/regulatory.db-upstream`. Confirm both `regulatory.db` and `regulatory.db.p7s` symlinks resolve to upstream-signed files; verify boot-time kernel signature acceptance, not just desktop OpenSSL.
2. **Board-specific regulatory mapping:** on the **MZ600 Stingray variant only**, propose `brcm,ccode-map = "US-US-69";` for `wifi@1` (or a stricter variant policy source). Must keep generic code/DT independent of universal U.S. assumptions for other Xoom variants. The mapping affects the country hint-to-firmware translation; does **not** grant license by itself.
3. **Motorola calibration:** prepare an *identity-safe, MZ600-only* candidate retaining all the exact PA/antenna fields, adding only OEM-established `ccode=US` and `regrev=69`. **Keep dynamic factory MAC injection**, no copied `macaddr` or guessed `boardflags`/power values.
4. **Controlled qualification:** after known-good backup and rebootable test image, observe firmware's `country` iovar and whether it accepts and preserves the US/69 tuple. Verify Linux global US limits from the signed DB, the BCM PHY's effective 1–11 channel restrictions, no unverified 5GHz expansion, power limitations and driver logs. Remember Broadcom's `phy#0 country 99` custom regulatory domain may legitimately remain as a separate driver-specific report; country=99 is not necessarily evidence of failure.
5. **Safety gate before RF:** insist on the **intersection** of actual local legal rules, signed Linux regulatory DB, shipped-board antenna/PA calibration, firmware restrictions and supported PHY capabilities. Avoid raising TX power, unlocking disabled channels, guessing calibration parameters or spoofing identity. Only after readbacks pass consider one permitted 2.4 GHz test scan, then authorized association and DHCP, cold/warm reboot repeatability.
6. **FM/Bluetooth coexistence:** retain whole-BCM4329 power/reset constraints; do not load unqualified combo firmware files or alter hardware to fix regulatory software.

### Helpful source documentation

- https://wireless.docs.kernel.org/en/latest/en/developers/regulatory/processing_rules.html
- https://www.kernel.org/doc/html/latest/driver-api/80211/cfg80211.html
- https://packages.debian.org/bookworm/wireless-regdb
- https://packages.debian.org/bookworm/all/wireless-regdb/filelist
- https://lists.debian.org/debian-release/2026/05/msg01172.html (custom kernel should select upstream-signed database)
- Internal: `docs/checkpoints/NATIVE_DEBIAN_SD_BOOT_USB_WIFI_IDENTITY_PHYSICAL_PASS_2026-10-25.md`, `docs/research/MOTOROLA_BCM4329_OEM_CALLGRAPH_TRACE_V3.md`.

## Do not misstate status

**CONFIRMED:** Motorola OEM `US/69` in TWO archived builds; live PHY channels 1–11; firmware interface up and down-state; source of Broadcom pseudo-country 99; BCM4329 requires country-code map unless a DT trivial override; upstream regulatory database cryptographic detached signature verified offline; exact package moved to /tmp via serial with correct hash.

**PENDING:** Debian package installation, regulatory database acceptance by running kernel, MZ600 board-specific DT/regrev deployment, direct firmware-country iovar verification, correct effective Linux US country state, RF/regulatory qualification, any association/connectivity. **No RF activity initiated; no persistent eMMC writes.**
