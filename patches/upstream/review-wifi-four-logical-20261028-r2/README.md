# BCM4329 Wi-Fi four-logical-member RFC — revision 2 (source QA, 2026-10-28)

**NOT SUBMITTED · NOT HUMAN SIGNED · NOT PHYSICALLY TESTED AS R2.**

This folder is a **versioned revision of the existing four logical Wi-Fi patches**, not a fifth patch and not an additional series to apply on top of the historical [review-wifi-four-logical-20261028](../review-wifi-four-logical-20261028/README.md). Select **either** four-member series from the same pinned source base, never stack both. Historical exact **nine-review** kernel currently installed on the MZ600 remains built with the **earlier** version; its source manifest and verified hashes remain authoritative for that live installation.

**Pinned upstream base:** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` (2026-10-28 check). **Isolated source-only r2 tip:** `2c464dd9b79c8ad2883282f9bb67e6dcc6c9f8b0`, worktree `qa-wifi01-perchan-revision-20261028` on the Desktop. Exact candidate changes only source `drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c` inside WIFI-01.

## Logical members

1. **WIFI-01 — existing legacy BCM4329 channel-list fallback, *amended*:** when older firmware rejects `chanspecs` and presents bounded `WLC_GET_VALID_CHANNELS`, keep the band's available 20MHz channels and existing cfg80211 restrictions. R2 additionally uses the original normal driver's `per_chan_info` read-only IOCTL for each allowed 20MHz channel, encodes its band/chanspec and **ORs firmware `WL_CHAN_RADAR`/ `WL_CHAN_PASSIVE` into Linux `RADAR`/`NO_IR` flags**. It never clears those flags; unsupported optional query leaves original fallback restrictions intact. No firmware power, country, TX-power or scan behavior changed. This is a correction **inside WIFI-01's existing one-logical-issue scope**, tracked by [issue #4](https://github.com/Olsens11/XoomLinux7/issues/4).
2. **WIFI-02** — per-scan ESCAN synchronization/late terminal rejection. **Unchanged logical diff / identical stable Git patch-ID** from earlier four-member series.
3. **WIFI-03** — narrowly scoped Event69 malformed-index terminal recovery for sole active owner. **Identical stable patch-ID**.
4. **WIFI-04** — conditional firmware-up readiness for later ESCAN. **Identical stable patch-ID**.

The latest source patch hashes are in the `0001`–`0004` files themselves; IDs on disposable replay are not permanent patch identities. R2 uses placeholder draft author and pre-existing `Assisted-by`, **never a fictitious human Signed-off-by**. The user will review and sign only once the entire implementation is ready.

## Verified source-only QA (2026-10-28)

- Fresh `git worktree` on clean pinned base, `git am` all 4, amend WIFI-01, replay WIFI-02..04: **PASS**.
- Four standalone `git format-patch` exports in `series` order; **exactly four logical commits**.
- `scripts/checkpatch.pl --no-tree --no-signoff --strict` on **each exported commit**: **0 errors / 0 warnings / 0 checks**.
- `git diff --check` and clean isolated source state: **PASS**.
- Stable patch-id comparison against historical four-way series: WIFI-01 **changed** as intended; WIFI-02/03/04 **identical** to earlier patch IDs. Direct file comparison with physically proven old nine-source build isolates only declarations and optional per-channel restriction query in existing legacy fallback.
- ARM GNU Toolchain `14.3.Rel1`, `ARCH=arm`, same config as pinned nine-source build: `make olddefconfig` **PASS**; `make prepare` **PASS**; `make drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.o` **PASS**; full `brcmfmac/` driver object-prefix build **PASS**. Build output is **isolated** and not installed or made available to MZ600.
- Exact source and output receipts (local only): `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/qa-wifi01-perchan-revision-build-20261028/` and corresponding isolated source worktree. No firmware binaries or identifying host/device logs in this Git revision.

## Firmware evidence and uncertainty

- Private HRI39/HRI66 OEM firmware from MZ600 (261,317 bytes each, matching binary): `per_chan_info` embedded null-terminated string present; `chanspecs` string absent. **Binary string presence is not proof of a successful runtime IOCTL.**
- Current Debian-tested 4.220.48 firmware (253,748 bytes): `chanspecs` string present; `per_chan_info` string absent. **String absence is not proof of unsupported IOCTL**.
- R2 mirrors the ordinary path's optional firmware query **only for the fallback**. On unsupported firmware query it currently leaves the same original cfg80211 flags in place as R1; this does **not** establish regulatory correctness on every firmware/country or justify adding 5GHz channels.
- [Missing 5GHz Band 2](https://github.com/Olsens11/XoomLinux7/issues/1) is **a separate initialization stage**: original, untouched `WLC_GET_BANDLIST` determines which bands are created *before* WIFI-01 filters channels. R2 does not pretend to create/restore Band 2 or claim dual-band PASS.

## Mandatory gates before replacing the integrated nine-patch reference

1. Instrument/capture read-only `per_chan_info` response/return code on target HRI39 and compare with current firmware; trace exact path and intact regulatory constraints under approved temporary boot, no forced country/power/channel settings.
2. Independently model/fault-test firmware restrictions: 2.4/5GHz allowed, passive/NO_IR, DFS/radar, unsupported query, invalid list entries, DISABLED channels, bandwidth and regulatory flags. Review whether failure mode needs stricter conservative behavior.
3. Determine `GET_BANDLIST` responses and missing 5GHz band cause separately; preserve actual regulatory restrictions and hardware calibration.
4. Build a **new clean nine-patch integration** using this **revised WIFI-01 in place of the historical one**, plus the unchanged eight other members; rehash modules/DTB/image, run required code/style/source QA, compare against historical exact reference.
5. Only with user-approved safeguarded procedure: **temporary boot**, matched modules/firmware, verify 2.4GHz association, legally supported 5GHz passive scans, exact scan lifecycle, Bluetooth coexistence, p10/COM9 fallback and storage geometry. **Do not flash p7** during this source-only phase.

See [dated source QA checkpoint](../../docs/checkpoints/MZ600_WIFI01_R2_PER_CHAN_RESTRICTION_SOURCE_QA_2026-10-28.md), [original four-patch review](../review-wifi-four-logical-20261028/README.md), [issues #4](https://github.com/Olsens11/XoomLinux7/issues/4) and [#1](https://github.com/Olsens11/XoomLinux7/issues/1).