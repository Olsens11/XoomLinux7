# MZ600 Linux7: v7R `iw` scan positional-argument correction — owner one-shot prepared

**2026-10-26. State:** Prepared for owner-operated test; **not yet executed**, no new module build or radio action. Existing v7 test was physically performed using owner one-shot: exact ABI brcmfmac 345380B, original HRI39 firmware and calibration loaded RAM-only, wlan0/phy13 present, 9 firmware-supported 5GHz channels, permitted channel36 `NO_IR`; however `iw dev wlan0 scan passive freq 5180` returned 1, driver `MZ600_LEGACY_SCAN_LAB_START`, command50 and result51 markers absent. Rollback independently verified.

## Root cause now grounded in `iw` source

On physical Debian Xoom, `iw --version` is **5.19** and `iw help scan` explicitly formats positional options `[freq <freq>*] ... [ssid <ssid>*|passive]`. Historical/modern `iw scan.c` command parser (e.g. [Linux iw scan.c source](https://android.googlesource.com/platform/external/iw/+/999e129ee24a3c15e633b8489382faba831e87fe/scan.c) and [maintained iw source](https://fossies.org/linux/iw/scan.c)) switches to `DONE` once it reads `passive`; an additional `freq` keyword in DONE is invalid and causes rc1 **before any netlink scan message is constructed**. Thus the prior usage `scan passive freq 5180` explains missing driver prints with high confidence. Testing both orders against a deliberately nonexistent interface returned `No such device (-19)` for both because interface resolution precedes parser; this does not refute the source-based conclusion.

**One controlled correction:**
- Previous erroneous: `iw dev wlan0 scan passive freq 5180`
- New: `iw dev wlan0 scan freq 5180 passive`

No legacy driver code / firmware / NVRAM / region / channel changes. Retain same v7 lab module SHA **ca2dbbf1131a44515b724b38f3ce3a7e7a6b8a7712ecceea404c833aa0f3ffec**, exact running ABI `7.0.0-next-20260422+`, same original Motorola HRI39 firmware SHA `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a`, identity-preserving OEM-calibration-minus-bootstrap-MAC variant, same single 5180MHz channel36 NO_IR non-radar restriction and bounded passive scan, no SSIDs/BSSIDs in public log.

## Prepared artifacts

- [v7R guarded one-shot source](../../scripts/host/xoom/test-v064-hri39-singlepassive-5ghz-legacy-scan-proof-v7r-20261026.sh) **177 lines, 7557 bytes, SHA256 d3c5e261479cf71ef3adf6cacca3452e52c9344fb77a14538afbc699951d1d13**, Bash `-n` PASS. New, unique v7R RAM calibration and once-only attempted marker rather than reusing prior consumed v7 one-shot. Same full module unload (WCC first), firmware and calibration overlay unmount and original file hash verification. Enhanced private stderr handling: retain only bounded **category/negative errno** in COM9 transcript; output still stored in private `/run` files and deleted on cleanup, never print neighboring SSIDs/BSSIDs.
- Physical host copy: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V7R-USER-ONESHOT-SCAN-20261026.sh`, exact LF bytes and SHA verified against GitHub.
- Surface manual launcher: `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V7R-USER-ONE-SHOT-20261026.py`, SHA256 **832bcfbcb56f128e1e8c0dd08dc312450b4dbb05dcc737a8f16b128391f457f8**, `python -m py_compile` PASS. This invokes **no uploader**: original v7 module **remains SHA-verified in Xoom RAM**, as confirmed by COM9 `sha256sum /run/mz600-v064-legacy-singlepassive5g-v7.ko`. The manual launcher preflights installed baseline, verifies RAM module and OEM FW, submits only new guarded v7R Bash script to COM9, captures all status markers and independent postcleanup read-only COM9 audit, then saves a unique **v7R** Surface private transcript and JSON receipt. Prior v7 receipts are preserved and are not re-used or overwritten. No GitHub firmware/MAC output, no boot changes.
- Explicit owner command in **Surface PowerShell** (close any other COM9 console first): `python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V7R-USER-ONE-SHOT-20261026.py"`. **Not executed by assistant**. If failure/cleanup incomplete, DO NOT retry or reboot until inspection.

## Acceptance / interpretation

Successful firmware probing needs `MZ600_LEGACY_SCAN_LAB_START` and `MZ600_LEGACY_SCAN_LAB_COMMAND50_RC=0`, plus a delayed `MZ600_LEGACY_SCAN_LAB_RESULT51` sanitized version108 count/valid envelope; physical still needs results record and IE validation before exposing actual cfg80211 BSS. Even if `iw` rc1 after driver was called, collected new stderr category, kernel return and independent cleanup will establish next logical fix. **No physical legacy 5GHz scan success is claimed yet.** Upstream patch series remains one logical change per commit with proper cfg80211 lifetime and regulations; no lab v7 patch submission.
