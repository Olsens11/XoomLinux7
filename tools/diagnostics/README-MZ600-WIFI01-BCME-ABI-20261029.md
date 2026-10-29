# MZ600 WIFI-01 legacy per-channel ABI: bounded, read-only lab probe (2026-10-29)

**SOURCE-ONLY PREPARATION; NOT COMPILED OR EXECUTED ON A TABLET.** This is an optional lab overlay, **not an additional upstream review patch**. The current four-member WIFI-01/02/03/04 unsigned r3 draft and known-working original nine-member physical installation remain untouched. Run no firmware, module, country, power, scan, or flash steps without an exact hardware/rollback gate.

## Files

- [Overlay generator](mz600-wifi01-bcme-abi-overlay-20261029.py): given an **isolated nine-member + r3 kernel source tree**, emit one separate lab-only patch. Requires the r3 function/anchor exactly once, fails closed otherwise; writes **only the requested output patch**, never edits a kernel tree.
- [Generated overlay patch](mz600-wifi01-bcme-abi-six-query-lab-only-20261029.patch): two-file `cfg80211.c` and `fwil.c` instrumentation against the r3 WIFI-01 source. Explicitly tagged `MZ600_LAB_ONLY_20261029` and not submit-ready.
- [Dated physical preflight and source QA](../../docs/checkpoints/MZ600_WIFI01_BCME_ABI_DIAGNOSTIC_SOURCE_AND_PREFLIGHT_2026-10-29.md).
- [Underlying problem audit](../../docs/research/MZ600_WIFI01_R3_FWERR_COLLAPSE_AND_IOCTL_ABI_SOURCE_AUDIT_2026-10-29.md).

## Exact six read-only requests

The probe calls only the existing kernel `brcmf_fil_bsscfg_int_query(ifp, "per_chan_info", &value)` on primary bsscfg index zero while the legacy channel fallback initializes. Values are four-byte little-endian IOVAR query **inputs**, not channel changes:

| RF channel | Original Xoom band+channel | Intermediate +BW20 | Modern D11n HT20 |
|---|---|---|---|
| 2.4GHz ch11 | `0x200b` | `0x280b` | `0x2b0b` |
| 5GHz ch36 | `0x1024` | `0x1824` | `0x1b24` |

Before these requests the probe repeats the read-only `BRCMF_C_GET_VERSION`, reporting its numeric value. In the pinned brcmfmac source this is used to select the **D11 encoding family**, so do not assume it alone resolves every older DHD IOCTL-version conversion. The original archived Android source sometimes converts a pre-conversion value before transmission.

A separate narrowly gated `fwil.c` trace captures, before the normal `-EBADE` normalization, the **transport return**, original negative **firmware BCME status**, exact 32-bit input and response value on success, for the first six requests. It **does not** flip shared `ifp->fwil_fwerr`, change production error return behavior or dump sensitive buffers. A returned word is meaningful channel metadata only after checking actual `WL_CHAN_VALID_HW/SW`, `RADAR`, `PASSIVE`, `INACTIVE` and `RESTRICTED` semantics; echo/garbage must be rejected.

The lab code does not set country, power, channel, regulatory flags or initiate an RF scan. However **loading the instrumented module does disrupt live WLAN**, so it is a hardware experiment requiring an approved RAM-only procedure and a separate rollback postflight. No historical one-shot markers may be reused.

## Source-only reproduction on the supported build desktop

1. Begin from an **isolated, clean exact pinned upstream base** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` and apply the exact canonical nine-member patch series with the *r3 WIFI-01 replacing* the old WIFI-01 (do not layer r1+r2+r3).
2. Generate a new non-overwriting lab patch:
   ```sh
   python3 tools/diagnostics/mz600-wifi01-bcme-abi-overlay-20261029.py \
       --kernel-root /path/to/isolated-nine-plus-r3-source \
       --out /path/to/new-temp/mz600-wifi01-bcme-abi-lab.patch
   git -C /path/to/isolated-nine-plus-r3-source apply --check /path/to/new-temp/mz600-wifi01-bcme-abi-lab.patch
   ```
3. Apply **only in that scratch worktree**, inspect diff, run `git diff --check`, checkpatch, exact ARM build configuration, brcmfmac object-prefix compilation and full matching module/zImage/DTB dependency build. Verify all imported CRCs including WCC. Do not mix an arbitrary new module into the known-working p10 installation.
4. Before any physical run, confirm correct replacement device, root p10, COM9 exclusive, current Wi-Fi and module hashes, firmware/NVRAM identities, no overlays, inactive HCI, **previously validated private May2012 Motorola firmware**, exact signed-off owner approval for the bounded test and a fresh trial ID. Stage `brcmfmac.ko` and private OEM firmware in RAM only using the established vetted test/rollback SOP. No new regulatory assumptions; no physical step is automated by the overlay generator.
5. Collect a private log and sanitized public evidence for all six calls; independently restore the original installed generic firmware, original WCC/core/util modules, NM/WPA Wi-Fi and private NVRAM hashes; verify no overlays or extra processes. If any gate fails, do not attempt the radio swap.

## Executed versus open

- **PASS source-only**: Python generator syntax, pinned upstream source extraction, exact r3 WIFI-01 source patch `git apply --check`, generated two-file overlay and `git apply --check` on staged r3 source (Surface, 2026-10-29).
- **PASS hardware baseline only**: freshly verified COM9 root, p10 ext4, kernel `7.0.0-next-20260422+`, Wi-Fi state 100 connected, Bluetooth inactive, existing original brcmfmac/WCC SHA match historical exact nine-build, no firmware/module overlays, COM9 released. Fresh unredacted private receipt only on Surface under `captures/MZ600-WIFI01-BCME-ABI-20261029-A/`.
- **NOT RUN**: ARM compile/full nine+r3 build, new module CRC equivalence, May2012 6-query physical experiment, raw native BCME sample, regulatory acceptance, any reboot/flash or radio swap.

**Review finding:** Source r3's `-EBADE` `per_chan_available=false` cache cannot distinguish genuine unsupported iovar from bad argument or other firmware error. Keep issue [#4](https://github.com/Olsens11/XoomLinux7/issues/4) open. If successful legacy encoding is found, revise **existing WIFI-01**, not a fifth review member. The owner has withheld DCO signoff.
