# MZ600 WIFI-01 native BCME/legacy chanspec diagnostic — source preparation and real baseline preflight (2026-10-29)

**Final status for this checkpoint: original hardware baseline read-only PREFLIGHT PASS; source-only generated diagnostic applies to pinned upstream+r3 PASS; kernel build and six-argument physical test NOT RUN.** This checkpoint does not alter the original nine-member review MZ600 kernel/modules or promote r3. No human DCO, no upstream submission.

## Authorization / guardrail

Owner responded “ok lets do it” to designing and conducting the bounded source-supported read-only legacy `per_chan_info` ABI/error diagnostic. The operation preserved a verified rollback requirement; the main ARM build Desktop was **offline**, while Surface and Pi were online, and neither available host had the established ARM Linux7 cross-compile environment. A physical module swap without a compiled/ABI-verified artifact would be unsafe, so **none was attempted**. Do not reinterpret this as a complete approval for future unbounded firmware experiments or destructive changes.

## Required historical reuse and source research

Read [r2 exact physical per-channel failure and full rollback](MZ600_WIFI01_R2_OEM_2012_PERCHAN_PHYSICAL_AND_HISTORY_2026-10-28.md), [r3 candidate](../../patches/upstream/review-wifi-four-logical-20261028-r3/README.md), [Oct28 legacy ABI contract](../research/MZ600_BCM4329_LEGACY_CHANNEL_REGULATORY_CONTRACT_2026-10-28.md), [new Oct29 firmware-error review audit](../research/MZ600_WIFI01_R3_FWERR_COLLAPSE_AND_IOCTL_ABI_SOURCE_AUDIT_2026-10-29.md), and [standing historical gate](../process/DEVELOPMENT_WORKFLOW.md). The May2012 OEM `4.218.248.44` recognized two bands/35 channels while full-D11n `per_chan_info` failed 35/35; no native BCME errno captured. The old v05/V13 lab-only NO_IR blanket safety and V28 deliberate retirement of normal-scan restrictions remain separate: avoid reviving an obsolete workaround as automatic production policy.

**Confirmed source-specific finding:** pinned `brcmfmac/fwil.c` collapses any negative firmware result to `-EBADE` unless original native errors are specifically exposed; r3 caches `-EBADE` as iovar unavailable. This may incorrectly conceal wrong query-argument format or other firmware errors. The historical Xoom `channel|BAND`, intermediate `+BW20`, and current D11n `+BW20+SB_NONE` formats are actual source precedents, not validated on the May2012 hardware yet.

## Actual physical read-only preflight, executed 2026-10-29

Remote Desktop Commander re-checked host availability: `SURFACE-BOOK-2` and `ps-to-vnc-dev` **online**, `DESKTOP-R16QJD4` **offline** (a snapshot, not a future guarantee). Surface COM9 enumerated physically; a fresh non-overwriting Python pyserial script `inspection/MZ600-WIFI01-BCME-ABI-Preflight-20261029A.py` used authenticated `root@xoom-mz600` and only read-side shell commands. Unredacted private receipt is **Surface-only** `captures/MZ600-WIFI01-BCME-ABI-20261029-A/preflight-original-baseline-private.txt`.

- **PASS**: `id -u=0`, kernel `7.0.0-next-20260422+`, `/dev/mmcblk0p10 ext4` mounted at `/`.
- **PASS**: NetworkManager and wpa_supplicant `active`, `wlan0` state `100 (connected)`, operational status `up`; bluetooth service inactive. Loaded original `brcmfmac_wcc`, `brcmfmac`, `brcmutil`; BT UART modules present but no HCI operation.
- **PASS**: actual core `brcmfmac.ko` SHA matched historical original exact-nine build `5e767d47017ff9028e6c364f8325420b0fc79efd1c1e07d36595fb4fd0540d26`; WCC `brcmfmac-wcc.ko` matched `eb9aa7efc8d9e356088aa9693cf1937c8c7e1a65dcd0193618915521b7a048b9`. Private actual OEM NVRAM/generic firmware SHA captured but **not printed publicly**.
- **PASS**: all four monitored original module/firmware/NVRAM paths reported `NO_OVERLAY`; COM9 shell closed cleanly with `READ_ONLY_PREFLIGHT_DONE_COM9_RELEASED_PRIVATE_RECEIPT`.
- **NOT DONE**: firmware replacement, driver reload, RF scan/probing, country or power changes, p7/p8/p9/p10 writes, flash, reboot, module build.

## Source-only lab probe prepared and checked

Pinned base `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` was **locally verified by git SHA on Surface**. Only `cfg80211.c` and `fwil.c` were extracted to a new isolated scratch folder; the existing public unsigned WIFI-01 r3 patch was applied solely to that staged two-file source. A new [lab-only generator](../../tools/diagnostics/mz600-wifi01-bcme-abi-overlay-20261029.py) produced a distinct [two-file diagnostic overlay](../../tools/diagnostics/mz600-wifi01-bcme-abi-six-query-lab-only-20261029.patch).

- **PASS**: Python generator `py_compile` and source anchoring; generator fails if r3 source markers are absent or its output path already exists, never mutates source in place.
- **PASS**: `git apply --check` for the pinned r3 WIFI-01 patch on staged pinned base, then `git apply --check` for the resulting diagnostic overlay on staged r3 source. Final corrected logging uses C `\n`, not literal escaped backslash+n.
- **Probe behavior, NOT run on the tablet**: `BRCMF_C_GET_VERSION` readback (numeric D11 family selector), then six `BRCMF_C_GET_VAR/per_chan_info` 4-byte queries: ch11 `0x200b,0x280b,0x2b0b`; ch36 `0x1024,0x1824,0x1b24`. Distinct `fwil.c` trace records transport status and negative native firmware BCME **before** `-EBADE` translation. The shared `ifp->fwil_fwerr` flag is **not toggled**. Log excludes SSIDs/MAC/BSSID/secret NVRAM data. Input/response words should only be treated as meaningful metadata on success and after validating flags; an echo must not be accepted.
- **OPEN**: checkpatch, affected-prefix ARM GCC14.3 compilation, full original-nine+r3+lab image/modules, CRC equivalence, firmware-specific numeric response, successful and adverse-path regulatory behavior. Build Desktop was offline and Surface WSL had **no Linux distro**, Pi had only its aarch64 compiler (no armhf Linux cross compiler). Do not install new system packages or alter the Pi's recovery environment to bypass these controls without an explicit new engineering decision.

## Next strictly bounded discriminator

Use the [test plan](../../tools/diagnostics/README-MZ600-WIFI01-BCME-ABI-20261029.md). On an available approved ARM build environment, assemble isolated exact nine+r3 with this **lab-only** trace, inspect and compile the entire affected scope, verify CRC and private artifact hashes. On the known replacement MZ600, only after rechecking live baseline and private rollback assets, perform fresh RAM-only May2012 OEM read-only query A/B. Report six **actual native BCME** status codes and trustworthy flag values, plus independent recovery of the original network. Then amend **existing WIFI-01 only** according to findings; do not assume r3's `-EBADE` unsupported-cache is correct, and do not add a fifth patch.

**Issue disposition:** [#4](https://github.com/Olsens11/XoomLinux7/issues/4) OPEN; WIFI-01 r3 source review risk confirmed, actual firmware support still UNKNOWN; original working p10 radio remains intact.
