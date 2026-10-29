# BCM4329 WIFI-01 same-scope r2 patch revision: firmware channel restriction QA — 2026-10-28

## Context / actual state

This is an **offline source-only milestone**, not evidence of a new kernel boot. Owner directed that a single logical patch may be revised repeatedly to fully solve its own logical problem; tracking issue count need not match patch count. The **physically running** nine-review Linux 7 build on the MZ600 still uses the original WIFI-01, boots Debian from p10 and has known 2.4GHz Wi-Fi/COM9/LCD; do not relabel it r2. The original nine-source integrated commit `507eb069df819cb5cc801ad8be096f70d9ca7609` and the historical 4-way Wi-Fi RFC files were left unchanged.

## Specific source deficiency and response

Issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4): normal `brcmf_construct_chaninfo()` uses firmware `per_chan_info` for `WL_CHAN_RADAR` and `WL_CHAN_PASSIVE`, ORing flags into `IEEE80211_CHAN_RADAR`/`IEEE80211_CHAN_NO_IR`. The original WIFI-01 legacy fallback used only `GET_VALID_CHANNELS`, retaining initial cfg80211 flags but **not** requesting these additional firmware restrictions.

**R2 implementation (same WIFI-01 logical patch, no fifth patch):** for validated, firmware-supported 20MHz channels in existing 2.4/5GHz bands, encode the appropriate 20MHz Broadcom chanspec with the normal `cfg->d11inf.encchspec`, call `brcmf_fil_bsscfg_int_query(ifp, "per_chan_info", &chaninfo)`, then OR radar or passive restrictions as the normal branch does **if the optional IOCTL succeeds**. No channel flags are cleared. Bandlist/wiphy allocation logic, country, power, firmware version, scan event routing, WLAN state and global driver logic remain unchanged. If this IOCTL returns an error, no new firmware restrictions are imported; exact safe behavior remains to be tested before accepting regulatory parity. The normal upstream branch already has this error-ignoring pattern.

## Firmware capability evidence (non-executable)

Cross-reference to private original Motorola HRI39/HRI66 `fw_bcm4329.bin` (261,317 B): identical OEM binaries have embedded `per_chan_info\0` and lack `chanspecs\0` names. The **current Debian** 4.220.48 `brcmfmac4329-sdio.bin` (253,748 B) contains `chanspecs\0`, but no `per_chan_info\0`. These are simple binary-string tests; capability or per-channel return codes are **not proved**. Firmware binary bytes, NVRAM and private host identifiers stay off Git.

## Exact offline acceptance receipts

- Pinned original upstream source base `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`. New disposable four-commit isolated branch `review/wifi01-perchan-20261028`, final tip `2c464dd9b79c8ad2883282f9bb67e6dcc6c9f8b0`.
- **WIFI-01 amended first commit**, r2 commit `ec3e61a674cf92896a5239283e2ecc9a4ea50841`. Replayed other three unchanged logical changes. Exported as four patch files to [revision-2 directory](../../patches/upstream/review-wifi-four-logical-20261028-r2/README.md) with `series`. Original series preserved.
- Strict per-commit `checkpatch --no-tree --no-signoff --strict` **four PASS**, each **0 errors/0 warnings/0 checks**; clean `git diff --check`; no real human sign-off. Compare Git stable patch IDs: WIFI-01 changed, WIFI-02/03/04 exactly identical logical diffs to original four-way series (even though their commit SHAs and export bytes necessarily change).
- `ARCH=arm` GCC 14.3.1 cross-compile with isolated output, same `.config` copied from original nine-review build: `make olddefconfig`, `prepare`, modified `brcmfmac/cfg80211.o` compilation **PASS**. Broader `drivers/net/wireless/broadcom/brcm80211/brcmfmac/` prefix compiled and linked **PASS**. Not a full zImage/modules packaging build, DT schema check or in-kernel runtime test.
- Compiler output: `brcmfmac/cfg80211.o` 112,212 B, SHA256 `bb75af168804fe593b56f9d514c035724e4721d18ef0a151ff08c958bff20184`; assembled driver `brcmfmac.o` 319,744 B, SHA256 `eb39103e923ff575ce70932da5fd0736272645383fe8a967c461b79c885ef72f`. Private local build receipt under `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-wifi01-perchan-revision-build-20261028`.
- Source diff between **earlier exact nine-patch cfg80211.c** and **isolated four-member r2 cfg80211.c** is confined to declarations and `per_chan_info` query/flag OR within existing `brcmf_bcm4329_legacy_channels` fallback. No event handler, connection setup or unrelated source file changes.

## What remains unresolved / next discriminators

1. **Hardware query proof** of `per_chan_info` runtime return values and failure handling on OEM older firmware, including passive/radar channels, using approved read-only instrumentation in a reversible temp-boot kernel. This is **not yet a verified regulatory fix**; leave [issue #4](https://github.com/Olsens11/XoomLinux7/issues/4) open.
2. **5 GHz band creation:** unrelated earlier `GET_BANDLIST` stage. Current source firmware doesn't advertise 5GHz Band 2; read-only bandlist diagnostic and matched firmware/board config test remain pending under [issue #1](https://github.com/Olsens11/XoomLinux7/issues/1). Do not add channels or override country/DFS.
3. Fault/ABI tests: absent or invalid per-channel iovar, malformed legacy channel list, pre-existing disabled or NO_IR channels, DFS mapping, chip gating, 2.4GHz association, other Broadcom compatibility.
4. Separate **new nine-patch clean integration** and full build/hash QA, then exact-hardware temporary boot **only with owner-approved safeguards**. Original boot p7, fallback p8, TWRP p6, GPT, USB COM9 and live p10 unchanged.

**Classification:** SAME-LOGICAL-PATCH REVISION; SOURCE QA PASS; FULL REGULATORY PARITY AND HARDWARE VALIDATION OPEN. Never treat `checkpatch`'s stock wording “ready for submission” as an owner decision; patches intentionally remain unsigned/unsubmitted.