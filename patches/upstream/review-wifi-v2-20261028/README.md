# BCM4329 clean Wi-Fi review series (unsigned RFC draft)

**Base:** `xoom-linux/linux@2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`.  
**Status:** isolated, logical upstream-style source commits; clean 3-patch replay PASS; strict `checkpatch.pl --no-signoff` **0 errors / 0 warnings / 0 checks** per patch. **Not submitted, not human-signed, not the exact physically tested V31 lab source.** See `manifest.json` for individual SHA256s and the independent replay/checkpatch report.

## Commit order

1. `wifi: brcmfmac: use legacy channel list on BCM4329` — only when `chanspecs` fails with `-EBADE` on BCM4329, read bounded `WLC_GET_VALID_CHANNELS`, intersect with currently permitted wiphy channels and constrain unverified bandwidth. Never clear cfg80211 regulatory restrictions.
2. `wifi: brcmfmac: match BCM4329 ESCAN completion to active scan` — distinct 16-bit scan transaction ID; accept a genuine terminal only for the active normal primary-STA scan; route unmapped *successful terminal only* to sole active station. Generation checking and terminal owner fallback are one indivisible completion-lifetime change: a standalone owner patch without transaction correlation would be unsafe.
3. `wifi: brcmfmac: restore BCM4329 firmware readiness for ESCAN` — after ordinary MPC0, read `WLC_GET_UP`, conditionally issue `WLC_UP` only when precisely DOWN, verify readiness; preserve MPC1 idle behavior.

Experimental `MZ600_Vxx` diagnostics, extra subscriptions, test module parameters, hardcoded channel assumptions, and firmware/credentials are absent from these three diffs.

## Tested

- Source: isolated pristine detached worktree with exactly this kernel base. Git-format-patch series generated from three commits; no lab Vxx dependency.
- `git am`: three patches applied sequentially to a *separate* pristine kernel worktree with frozen platform integration snapshots, each prefix checked with `git diff --check`. Exact replay documented in `validation-initial.json` (first draft) and `clean-arm-build-result.json` when complete.
- Strict `checkpatch.pl --no-tree --no-signoff --strict`: **zero findings on all three revised patch files**. No actual human `Signed-off-by` has been added; omission deliberate.
- Hardware: the prior private-firmware V31 lab source scanned repeatedly, connected to WPA2, got DHCP, resolved DNS, synchronized NTP and verified HTTPS 200/TLS 0; **this cleaned source has not been flashed/loaded, and hardware tests cannot be inherited**.
- Other gates still OPEN: compile each series prefix, full clean kernel/modules/DTB build and exact binary readback, sparse/static/race review, P2P multi-interface and cancellation/stale events, broad Kconfig/architectures, regulatory review, real-world fast association, multiple device models.

## Replay

From an exact pristine checkout of the pinned base (not the current dirty development source tree):

```sh
git am /path/to/review-wifi-v2-20261028/0001-*.patch
git am /path/to/review-wifi-v2-20261028/0002-*.patch
git am /path/to/review-wifi-v2-20261028/0003-*.patch
git diff HEAD~3 HEAD --check
```

The board DTS, Motorola bootloader MAC ATAG and opt-in BigPart files are **different maintainer domains**: their existing `candidate/0001..0003` patches were independently staged before the Wi-Fi patches only for full-device clean-build reproduction. They remain *review snapshots*, not cleanly accepted upstream DT/ARM/block submissions. Booting the complete device requires compatible platform source, matching config, correct DTB and private non-kernel firmware/NVRAM/system services; this directory is **source code, not a ROM**.

## Submission and DCO requirements

These are **RFC drafts** with unattributed placeholder commit identities (`rfc-draft@invalid.example`) and transparent `Assisted-by: ChatGPT:GPT-6 [Desktop Commander]` trailers. The AI did not add `Signed-off-by` and cannot certify human DCO. Before mailing, a human must examine, revise, consciously accept authorship/licensing and add their own genuine sign-off; verify the *receiving* wireless maintainer tree / `MAINTAINERS` / `scripts/get_maintainer.pl`, run final tests and obtain explicit submission authorization. **Nothing has been emailed or sent upstream.**

Open separate issue: slow ~399s first automatic association, invalid-index firmware `SET_SSID`/`LINK` events and legacy v1/v2 header-format hypothesis. Do not invent an upstream connection-event fix until a clean diagnostic validates the raw event version and intended owner.

See also `candidate/SUBMISSION_REQUIREMENTS.md` (G01–G12) and `docs/checkpoints/MZ600_V31_FIRST_REBOOT_AUTOCONNECT_FULL_STACK_PASS_2026-10-28.md`.
