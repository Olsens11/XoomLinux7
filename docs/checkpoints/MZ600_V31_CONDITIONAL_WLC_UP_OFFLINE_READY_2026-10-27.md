> **User's first V31 setup attempt (2026-10-27 at ~17:49 Eastern): staging-only failure.** PowerShell launcher mistakenly revalidated `mz600-v31-normal-scan.sh` against **11386B** after already verifying the downloaded source against its correct **11426B** SHA-pinned size. All five files were actually copied and independently verified at their pinned byte sizes/SHA values. No V31 `runs` directory, consumed attempt marker or firmware test exists. [Fixed original launcher](../../tools/forensics/v31/run-v31-on-surface.ps1); for this already-staged folder use only [hash-pinned resume launcher](../../tools/forensics/v31/resume-v31-on-surface.ps1) without the Desktop HTTP server. Do NOT delete the staging directory or reuse an actual consumed trial. The physical readiness question remains OPEN.

# MZ600 V31 — conditional controller WLC_UP: offline build and owner-run test readiness

**2026-10-27 status: OFFLINE ARM BUILD PASS; V31 PHYSICAL TEST NOT YET RUN.** This is a reversible BCM4329 laboratory experiment, **not** a verified fix or upstream-quality patch. The owner explicitly approved the experiment. Follow [V31 owner-run instructions](../../tools/forensics/v31/README.md) and the established [Desktop→Surface→COM9 procedure](../process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md). Do not bypass previously encountered remote Surface write restrictions.

## Why we are testing this

[V30 physical evidence](MZ600_V30_FIRMWARE_UP_LOST_BETWEEN_ESCANS_PHYSICAL_PASS_2026-10-27.md): first normal multichannel scan 19 BSS in 3263ms; genuine Event69 terminal sync4661 and firmware UP1 immediately after its ordinary MPC1 restore, but firmware `WLC_GET_UP=0` about 4 seconds later before the second scan. Linux host READY1/netdev running1; setting MPC0 again does not immediately bring firmware UP, and second ESCAN sync4662 returned Linux -52. Prior V27 independently decoded `BCME_NOTUP=-4`. [External peer and Broadcom source research](../research/MZ600_BCM4329_MAINLINE_PEERS_AND_MPC_AUTO_DOWN_WLC_UP_2026-10-27.md) found a vendor `bcmdhd` channel-selection code path using MPC0 followed by explicit `WLC_UP` because MPC can automatically bring the interface down. That is a **source precedent**, not proof of an ordinary ESCAN solution or proof MPC1 caused the transition.

## Exact new behavior

[Source builder](../../tools/forensics/build_mz600_v31_conditional_fw_up.py) derives the V29 regulatory-safe normal scan plus physically measured V30 state instrumentation. On **BCM4329 primary station only** (`ifidx=0, bsscfgidx=0, NL80211_IFTYPE_STATION`), immediately after existing scan-entry MPC0:

1. Read firmware `WLC_GET_UP=162`. If an error or state other than 0 or 1 occurs, abort the scan and restore original MPC behavior.
2. Only if the controller explicitly says **DOWN0**, send a *single* existing official `BRCMF_C_UP=1` command.
3. Require a successful command and read-back of firmware UP1 before submitting otherwise unchanged ESCAN.
4. Preserve standard cfg80211/regulatory policy, real Event69 completion, per-scan transaction ID and normal MPC1 completion. No chip resets, added sleeps, forced passive/channel36/NO_IR, firmware/NVRAM/boot writes or fake terminal events.

## Offline verification

- Compiled module: `brcmfmac-2012-escan-conditional-up-v31.ko`, **354392 bytes**, SHA256 **`c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8`**.
- Matched WCC plugin: `brcmfmac-wcc-matched-v31.ko`, **5892 bytes**, SHA256 **`6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`**.
- Kernel ABI: `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`.
- Desktop WSL output: `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-2012-oem-escan-v31-conditional-up-20261027/`; `build.log` and `offline-build-result.json` retained.
- Original source SHA after builder restoration: `cfg80211.c=1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`, `fweh.c=4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c`.
- Bash `bash -n`, Python `py_compile` and Windows PowerShell parser passed. [Bash SHA](../../tools/forensics/v31/mz600-v31-normal-scan.sh): `5b168d624d23e68c828b6d169c4425de54b4f10e97c618d7a449cbe5f31033ea`, **11426 bytes**. [COM9 harness SHA](../../tools/forensics/v31/mz600-v31-owner-once.py): `9b54594f65c9b1ceb2e03f4ef793c201d0eaf16fd6a24217cdc37426ac3e9b29`, **19753 bytes**. [Surface launcher](../../tools/forensics/v31/run-v31-on-surface.ps1) validates these exact files and requests human `RUN` confirmation before COM9 use.
- Verified on Desktop Windows temporary staging only: `C:\Users\olsen\AppData\Local\Temp\mz600-v31-conditional-share-20261027\mz600-v31-escan-event69.ko`, 354392 bytes, exact module SHA. Temporary LAN server port **43157 not left running**.
- Surface preflight: COM9 present, no identified conflicting Python COM9 test process, fresh `MZ600-V31-CONDITIONAL-UP-20261027` folder absent, previous private V30 firmware/WCC available and hashes checked. These observations do not substitute for runner's live root/BT/overlay checks.

## Exact next action

Owner opens PowerShell on Desktop and runs the documented temporary port43157 single-module HTTP server; on Surface, runs the pinned [one-shot V31 launcher](../../tools/forensics/v31/run-v31-on-surface.ps1), which validates all SHA/bytes, asks to enter `RUN`, then uses **fresh** `up31a-01-mask000` trial. Do not rerun a consumed attempt. Close the server with Ctrl+C after transfer. Receipt/private trace will appear under Surface `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027\runs\`. Inspect state readbacks `MZ600_V31_UP_BEFORE_SCAN`, `MZ600_V31_WLC_UP`, `MZ600_V31_UP_AFTER_RECOVERY`, two genuine Event69 terminals/ids and independent SHA rollback. First scan success alone does **not** count as a full pass; if second fails preserve numeric trace. Never publish private SSIDs/BSSIDs, NVRAM, firmware or raw transcript.

**Success criteria:** two consecutive normal multi-channel scans in one module with two actual accepted ESCAN commands and **two real** terminal SUCCESS events matching distinct generation IDs; normal cfg80211 scan done, no timeout, independently restored installed firmware/NVRAM/core/WCC and no persistent changes. Later validate several idle cycles, power management, BT coexistence, connection/authentication and all [G01–G12 kernel standards](../../patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md) before proposing any source submission.
