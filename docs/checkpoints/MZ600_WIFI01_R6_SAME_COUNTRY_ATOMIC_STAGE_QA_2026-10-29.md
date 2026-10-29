# BCM4329 WIFI-01 r6: same-country notifier refresh and staged legacy channel restrictions (2026-10-29)

**Status: engineering RFC, source-only; no physical/radio regulatory acceptance.** [Corresponding issue #4 exact r5→r6 amendment/rollback ledger](https://github.com/Olsens11/XoomLinux7/issues/4#issuecomment-6501180482). This issue record and [the r6 four-member review directory](../../patches/upstream/review-wifi-four-logical-20261029-r6/README.md) are intentionally linked so each amendment has immutable source ids and a clear rollback procedure, as the owner requires. R5 was preserved unchanged.

## Reproducible inputs

- Base upstream `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.
- Exact original nine-member review series: DT-01/02/03, ARM BOOT-01, **WIFI-01**, WIFI-02/03/04, STORAGE-01 (BigPart).
- Prior r5 WIFI-01 commit `c2cd9da91`; r5 nine-member source tip `3d672f96b`; prior known-good offline r5 module SHA256 `838c718a8a5e607c33344dbb1366100553640040f12c08eabb53673ae4635722`.
- Current r6 WIFI-01 source commit `db76db5766942799dbc96190210c6d345613a7cb`; integrated nine-member source tip `5c7d32863fa31134cd7db1372f0cbca1ddee72ad`.
- Working WSL source `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-wifi01-r6-source-20261029`; independent build directory `qa-wifi01-r6-build-20261029`; ARM GCC 14.3.1; original BigPart-enabled kernel config reused. Test patch export on desktop `C:\Users\olsen\xoom-linux-rom\inspection\wifi01-r6-four-review-export-20261029\` before GitHub publication. All four review patches now reside in `patches/upstream/review-wifi-four-logical-20261029-r6/`.
- **No private firmware, USB serial, MAC, SSID, raw UART logs, or credentials published**.

## Exact change vs r5

In `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c`, r6 addresses two sides of the **same legacy BCM4329 channel-compatibility issue**.

1. The pinned notifier receives a regulatory request after Linux may have reconstructed channel flags from immutable registration-time `orig_flags`; Broadcom's `brcmf_translate_country_code()` returns `-EAGAIN` for an ISO country already matching firmware and the original notifier skipped `brcmf_setup_wiphybands()`. For **BCM4329 only**, a matching-country no-op now invokes a private *legacy-only* refresh. That first asks `chanspecs` using r4's per-call native firmware error. Only raw `BCME_UNSUPPORTED=-23` triggers `WLC_GET_VALID_CHANNELS`; modern firmware/query success bypasses the fallback, and other errors do not imply unsupported. It does **not** invoke a country SET or change the generic driver behavior.
2. `brcmf_bcm4329_legacy_channels()` used to write into live `channel->flags` before querying every channel's optional metadata. A late firmware/transport error could leave a **partial live channel table**. r6 fetches and validates bounded firmware list values and allocates `kcalloc` staging for the wiphy 2.4/5GHz channel entries, accumulating **additive-only** flag restrictions. Only after every query returns success or proven native unsupported does it apply `flags |= staged` to channels; on error it frees staging without changing flags in that function. A firmware-missing channel gets `DISABLED`, offered channels are 20 MHz only, optional actual radar/passive metadata is translated if available, unknown 5GHz metadata remains conservative `NO_IR`; no `orig_flags` writes, invented metadata or clearing of regulatory flags.

The other three Wi-Fi patch members have **unchanged stable Git patch IDs** to r5: WIFI-02 `f3640d66bb029408fd9bbd66d24b52873696b8e4`, WIFI-03 `8c968d701aa204f86d0c62655a2e134092aeea10`, WIFI-04 `a265bc9566a6f8fba96af95434d377c7863d0efc`. Separate BigPart unchanged. The source still retains r4's distinction between normalized Linux `-EBADE=-52` and actual Broadcom `BCME_UNSUPPORTED=-23` versus `BCME_NOTUP=-4`. **No new chronological fifth Wi-Fi patch.**

## QA actually completed

- `git diff --check` and amended WIFI-01 source commit `git show --format= --check`: **PASS**.
- Original exact-nine ARM GCC 14.3.1 `olddefconfig`, `prepare` and `brcmfmac/` driver-directory compilation: **PASS**.
- [Firmware error provenance](../../tools/tests/test_bcm4329_fwerr_boundary_20261029.py): **7/7** source/model cases PASS.
- [Regulatory lifecycle](../../tools/tests/test_bcm4329_regulatory_lifecycle_20261029.py): source-path and illustrative country restrict/reenable model PASS, including the custom-core notifier exception. The test was extended to accept source that stages restrictions rather than mutating channel flags directly.
- [New matching-country and atomic-staging](../../tools/tests/test_bcm4329_same_country_refresh_20261029.py): source contract and **6/6** illustrative failure/scenario cases PASS. **These tests do not execute C, device firmware, or enforce actual DFS/regulatory law.**
- Exported WIFI-01 `checkpatch.pl --no-tree --no-signoff` **0 errors / 0 warnings / 10 alignment CHECKs** (review formatting remains). WIFI-02/03/04 each 0/0/0.
- **Full `zImage dtbs modules` cross-build:** launched in the same fresh out-of-tree source/config as before, had not yet finished when this initial checkpoint was authored. **Record actual later exit/ABI results on issue #4 separately** before making a completed build claim.
- Original Linux Xoom is on known-good kernel `7.0.0-next-20260422+`, Debian p10, generic 4.220.48 firmware, unchanged calibration, with connected Wi-Fi last independently postflight-verified. **This work did not contact COM9, load r6, change RF, modify p7/p10 or reboot.**

## Current safety and remaining gaps

- The Broadcom custom regulatory PHY domain `99` lacks trustworthy per-channel radar/passive metadata. Original Motorola OEM 2012 `per_chan_info` six-format test returned native unsupported for those tested ABI calls; the actual radio country `US/US/rev0` on OEM 2012 and generic firmware did not independently prove 5GHz transmission legality. Thus **do not remove unknown-metadata 5 GHz `NO_IR`**, claim ordinary active 5GHz operation, or force factory US/69.
- New matching-country refresh applies **additive restrictions** without relaxation, but other notifier initiators, error branches after a genuine firmware country SET, concurrency/locking with cfg80211 and modern-driver behavior still need review and eventual physical validation. The staged helper avoids its own partial mutation on query errors; that is not a proof of system-wide atomicity or regulatory compliance.
- Review formatting has ten alignment checks. DCO/signoff absent; no upstream submission or release.
- Issue remains OPEN.

## Explicit rollback (OFFLINE; no tablet action)

Use the preserved [r5 four-member review set](../../patches/upstream/review-wifi-four-logical-20261029-r5/README.md) on a fresh checkout at pinned upstream commit, after original DT-01/02/03 + ARM BOOT-01, followed by unchanged WIFI-02/03/04 + STORAGE-01; verify resulting source against r5 nine-tip `3d672f96b` and previous [r5 full QA](MZ600_WIFI01_R5_REGULATORY_LIFECYCLE_NINE_BUILD_QA_2026-10-29.md). The r6 review directory, source commits, and both QA checkpoints remain available for A/B. **Because r6 was never installed on the Xoom, no physical device rollback is needed.**
