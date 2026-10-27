> **LATEST post-handoff continuation (2026-10-27):** V30 read-only firmware controller-UP / MPC query diagnostic has **compiled offline** against the target kernel; matched WCC and original source hashes verified. [New V30 checkpoint](../research/MZ600_V30_FIRMWARE_UP_MPC_DIAGNOSTIC_OFFLINE_CHECKPOINT_2026-10-27.md) records exact SHA, event-handler audit, measurement design, and the **Surface harness-write safety block**. **No V30 Xoom test was run.** Existing V28 normal first scan and V27 BCME_NOTUP are still the latest physical evidence. Do not treat this handoff's earlier next-step wording as physical test completion.

# XoomLinux7 — comprehensive engineering handoff: native MZ600, BCM4329, and canonical upstream patch series

**Prepared:** 2026-10-27  
**Project:** [Olsens11/XoomLinux7](https://github.com/Olsens11/XoomLinux7), development branch `wip/clean-wifi-bt-usb-20261025`  
**Kernel upstream:** [xoom-linux/linux](https://github.com/xoom-linux/linux) at pinned commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`, Linux `7.0.0-next-20260422+` on device  
**Purpose:** enable the next conversation/agent to resume actual engineering immediately without redoing investigations, corrupting a working installation, confusing tests with upstream patches, or inventing a different operating procedure.  
**Status of this document:** handoff and evidence index; **not** a Linux source patch, final reviewed kernel, or authorization to submit/flash.

> **Immediate state, read before touching anything.** A **replacement/test Motorola Xoom MZ600** runs **persistent Debian 12.15 on internal eMMC BigPart p8** with a previously SHA-verified Linux boot image on p7 and a usable USB COM9 root console. BCM4329 native brcmfmac/BT support has made major physical progress. V28 ran a **normal, unrestricted multi-channel `iw dev wlan0 scan`**, returning **12 BSS in 2,834 ms**; its **second scan in the same loaded driver failed with generic Linux `-52` after ~50 ms**. A targeted V27 source/physical diagnostic of an equivalent second ESCAN path decoded underlying Broadcom `BCME_NOTUP=-4`; the exact cause of firmware readiness loss is **not determined**. Versioned V21–V29 artifacts are LAB instruments, not patch prerequisites. A broad four-patch **integration snapshot** exists, but upstream-quality review requires **smaller logical, independently bisectable canonical patches**. The project's actual patch standards and 12 acceptance gates now live directly beside the snapshot in `patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md`. **Next steps:** address firmware repeat-scan readiness from evidence and extract a properly scoped Wi-Fi review series; test the exact new source rather than inheriting claims from earlier modules. No production source patch is submission-ready.

## 1. Essential reading order — DO THIS FIRST in the next conversation

All following paths are relative to [the current project branch](https://github.com/Olsens11/XoomLinux7/tree/wip/clean-wifi-bt-usb-20261025). Always check their **current content** and current Git HEAD before proceeding; this document reflects the 2026-10-27 handoff point.

1. **`patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md`** — binding working standard: pinned upstream links, AI-agent/DCO rules, logical scope, exact G01–G12 acceptance gates, regulatory/DT/maintainer and source-evidence requirements. This takes priority over advice in an older conversation.
2. **`docs/plans/MZ600_UPSTREAM_CANONICAL_PATCH_DECOMPOSITION_2026-10-27.md`** — owner-approved intended *fine-grained* upstream patch subjects, dependencies, and exclusions.
3. **`patches/upstream/candidate/README.md`**, **`series`**, and **`candidate-manifest.json`** — broad four-member *source integration snapshot*, clean-apply/hash evidence, and outstanding gaps. **DO NOT send this broad snapshot as the final upstream series.**
4. **`docs/process/DEVELOPMENT_WORKFLOW.md`**, **`docs/process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md`**, **`docs/process/EVIDENCE_AND_PRIVACY.md`** — proven use of desktop/Surface/COM9, hash/rollback, one-time IDs, and public vs private data.
5. **`docs/checkpoints/MZ600_V28_NATIVE_CFG80211_SCAN_AFTER_LAB_GATES_REMOVED_2026-10-27.md`** — physically tested native scan, 12 BSS; second ESCAN fails even without artificial restrictions.
6. **`docs/checkpoints/MZ600_V25_TO_V27_SECOND_SCAN_REGSTATE_AND_FIRMWARE_NOTUP_2026-10-27.md`** and **`docs/checkpoints/MZ600_V26B_NO_IR_GATE_REMOVED_SECOND_ESCAN_FW_ERROR_2026-10-27.md`** — precise chronology from obsolete NO_IR admission check to firmware-reported `BCME_NOTUP`.
7. **`docs/checkpoints/MZ600_V21_TERMINAL_OWNER_LAB_SWITCH_AB_PHYSICAL_PASS_2026-10-27.md`**, **V22b echo**, **V23 alternate IDs**, and **V24 generation/matched-WCC** checkpoints — proof of what Event69 handling actually achieves and does *not* yet guarantee.
8. **`docs/research/MZ600_V21_TO_UPSTREAM_EVENT69_COMPLETION_MODEL_2026-10-27.md`** and **`docs/research/MZ600_BCM4329_LINUX7_WHOLE_CHIP_PATCH_INTEGRATION_LEDGER_2026-10-26.md`** — concrete brcmfmac paths, candidate design, verified boundaries, and older chip/power research.
9. **`docs/checkpoints/MZ600_V064_STAGE_D_PERSISTENT_P7_FULL_PHYSICAL_SHA_VERIFIED_2026-10-26.md`**, the v064 persistent-p8 BCM4329 scan checkpoint, and v11 HRI39 BSS108 milestone — installed/bootable baseline and why the current problem is distinct from the earliest failures.
10. **`docs/plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md`**, **`docs/status.md`**, **`runtime/PROJECT_STATE.env`** — evolving cross-subsystem release gates and state overrides. These append historical sections; **newest heading supersedes older future-task paragraphs**.
11. For deep background only when pertinent: `docs/research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md`, `BCM4329_DATASHEET_PAGE_INDEX.md`, `BCM4329_SHARED_CHIP_OWNERSHIP_DESIGN.md`, `MZ600_BCM4329_MOTOROLA_OEM_WORKAROUND_CROSS_LAYER_SYSTEM_AUDIT_2026-10-26.md`, `MOTOROLA_BCM4329_F2_SOURCE_AUDIT.md`, and the HRI39 ISCAN wire-protocol research.

**Authoritative external project source:** `xoom-linux/linux` at the exact commit above, particularly `README`, `Documentation/process/coding-assistants.rst`, `submitting-patches.rst`, `5.Posting.rst`, `coding-style.rst`, `submit-checklist.rst`, `license-rules.rst`, `Documentation/devicetree/bindings/submitting-patches.rst`, `Documentation/process/maintainer-soc.rst`, `maintainer-netdev.rst`, `Documentation/networking/regulatory.rst`, and `MAINTAINERS`. The receiving branch may differ; re-audit at submission time.

## 2. Project objectives, hierarchy, and non-negotiable owner decisions

### Long-term product

- Native, **standard Debian/Linux 7 as the principal OS** on Motorola Xoom Tegra2 hardware—not an ephemeral emulator or a RAM-only demonstration. Preserve a normal root filesystem and OS integration; the experimental replacement MZ600 now boots from internal p7/p8.
- Correct, portable upstream-style Linux support for the Broadcom **BCM4329 combo chip**: SDIO Wi-Fi, UART Bluetooth and coexistence/shared power/reset/clock resource behavior; later FM where supported. Address real incompatibilities without proprietary firmware patching or permanent chip-specific hacks.
- Full normal Wi-Fi behavior: channel inventory, cfg80211/regulatory compliance, repeated scans, association, authentication, IP networking and coexistence. **Single-channel passive scans are not the target**.
- Submit clear, maintainable, bisectable Linux kernel patches consistent with **xoom-linux's actual documented standards**, and ultimately upstream maintainers' expectations.

### Critical patch-series instructions from owner

1. **One logical issue = one properly scoped review patch**, but one whole-chip integration can require many such patches. Do not compress all BCM4329 work into one huge patch just because it concerns one chip.
2. **No sequential "fix V21," "fix V24," etc. patch stack.** A logical patch should appear as the clean change written correctly the first time. Revisions replace that member, with necessary dependencies only on earlier *logical* changes in the series.
3. Every intermediate **review-series prefix must be coherent, compile and ideally operate** so that bisect is meaningful. Do not create unused scaffolding that is only repaired by later patches. Whether scan-ID checking and exceptional owner route are separate patches should be decided by true bisectability: combine only if functionally indivisible.
4. **Preserve ALL tested progress and exact source**, but keep development history/checkpoints/lab toggles OUT of final submitted patch diffs and commit messages.
5. Follow documented standards *inside the patch tree*, not hand-wavy generic Linux guidance; update the G01–G12 ledger and provenance with each revision.
6. **Do not add unnecessary regulatory restrictions.** Use kernel cfg80211/regdb authorization; never override it to permit an impermissible transmission. Specifically retire old forced channel36, one SSID/IE shape, forced passive, 500-ms dwell and blanket `NO_IR` policies. The owner emphasized that extra restrictions interfered with diagnosis.
7. Preserve actual per-device identity: bootloader factory WLAN MAC (ATAG→FDT), not a fixed/dummy MAC; avoid broadcasting or committing identifying/calibration values.
8. **Do not flash or overwrite** the proven boot, p8 root, recovery, installed Wi-Fi driver, factory firmware or NVRAM during routine driver lab tests. Authorized rare flash uses specific consent, independent SHA, target identity and backups. Don't confuse test replacement Xoom with protected original.
9. **Prefer actual execution and tangible checked artifacts**, not repeated philosophical discussions or promising future work. Check existing one-time attempts and other live sessions before opening COM9 or launching a new test.
10. Use the **existing documented Desktop→Surface transfer SOP exactly**. Do not randomly change LAN port, nest PowerShell, invent new transfer mechanisms or attribute malformed commands to a general transfer failure.
11. **No fabricated "PASS"**. Distinguish source build, RAM staging, first scan, second scan, successful suite, cleanup, independent original-state preflight and finally upstream submission readiness.

## 3. Actual machines, architecture, code location, and deployment

| Item | Verified/project location or role |
| --- | --- |
| Source host | Windows desktop `DESKTOP-R16QJD4`, discover current Remote Desktop Commander device ID from `list_devices` before use (do not hard-code/publish credentials or device identifiers). |
| Cross-build environment | Desktop WSL `Ubuntu-22.04`, user `xoomdev`, ARM GNU Toolchain 14.3.Rel1, ARMv7/Cortex-A9 and exact Linux module ABI. |
| Development project Git checkout | `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project`. Public GitHub `Olsens11/XoomLinux7`, branch `wip/clean-wifi-bt-usb-20261025`. |
| Actual kernel source tree | `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux`. Upstream source commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; read current Git status BEFORE modifying. |
| brcmfmac sources | `drivers/net/wireless/broadcom/brcm80211/brcmfmac/{cfg80211.c,cfg80211.h,fweh.c,fwil.c,fwil_types.h,feature.c,sdio.c,firmware.c}`. Matched separate `wcc/brcmfmac-wcc.ko` when interface/export CRC changes. |
| Device control / host | Microsoft Surface Book 2 `SURFACE-BOOK-2`, discover current Remote Desktop Commander device ID from `list_devices` before use (do not hard-code/publish credentials or device identifiers). Runs Windows native Python/PowerShell and connects USB serial COM9 to the Xoom. |
| Target DUT | **Replacement/test** Motorola Xoom MZ600, Tegra2, BCM4329 rev/B1 combo, Linux `7.0.0-next-20260422+`, Debian 12.15 armhf. In testing root access over COM9 (not an always-on guarantee; preflight). |
| Test artefacts on Surface | `C:\Users\olsen\xoom-linux-rom\captures\MZ600-<VERSION>-...\\`; each test owns its own guarded runner, private transcript, receipt JSON and consumed `.attempted` marker. |
| Desktop temporary LAN transfer | Desktop WSL→`C:\Users\olsen\AppData\Local\Temp\mz600-<fresh-ID>`→temporary Python HTTP on **port 43157**→Surface PowerShell `Invoke-WebRequest`. Historical desktop IPv4 `192.168.0.125`; verify before use. |
| Terminal | **COM9 @ 115200**, Python `pyserial`, exclusive ownership. No multiple readers/writers or concurrently running test harness. |
| Device root/boot | Default Linux boot: eMMC **p7**, Debian root ext4 **`/dev/mmcblk0p8`** using BigPart virtual view; p6 TWRP recovery. Preserve eMMC GPT and backups. |
| Kernel patch snapshot | `patches/upstream/candidate/{series,candidate-manifest.json,0001..0004,README.md,SUBMISSION_REQUIREMENTS.md}`. Snapshot is **not** final fine-grained upstream series. |
| Source-only generation utilities | `tools/forensics/build_mz600_vXX_...py` (experiment history); `tools/forensics/assemble_mz600_canonical_kernel_series.py` (broad snapshot generator). Review their exact source and SHA before any work. |

**Tool usage:** Discover available `mcp__Remote_Desktop_Commander__start_process`, `read_process_output`, `read_file`, `write_file`, `get_recent_tool_calls` and `mcp__GitHub__fetch_file/create_file/update_file` in the connected tools. Use Remote Desktop Commander only for explicitly authorized computers. Invoke **simple native PowerShell commands on Windows hosts**; WSL via `wsl.exe -d Ubuntu-22.04 -u xoomdev -- ...`. Long operations return a PID; read its output instead of launching an identical command again. Never treat a process-launch acknowledgment as test PASS.

## 4. Verified native Linux boot, whole-chip hardware and early milestone history

### Early kernel / hardware research, 2026-10-24 to 2026-10-25

- The project intentionally followed existing `xoom-linux/linux` upstream architecture, comparing Motorola original downstream Tegra/BCM4329 reference implementations and the Broadcom CYW4329 documentation. The combo chip's WL_REG_ON/BT_REG_ON, LPO, power sequencing and SDIO runtime PM were investigated *holistically*. Avoid a partial Wi-Fi-only hardware model that overlooks shared resource ownership.
- Early BCM4329 SDIO F2 `-ETIME` failures were investigated: normal Broadcom PMU/HT clocking, chip core and original NVRAM RAM token/CM3 startup, MMC2 runtime-PM hold, sequencing delay (datasheet ≥110ms where applicable), host clock, GPIO/regulator ownership. Do not resurrect an ancient F2 "fix" when a later baseline already brings up `wlan0`; diagnose actual current failure.
- Original Motorola firmware/NVRAM was audited, including an OEM country/regrev difference. Proven factory identity must be obtained **for this device** from bootloader/FDT, and original calibration/NVRAM kept private. Country changes must follow regulatory data and legal rules; don't apply a blanket US/69 override to every Xoom.
- USB/COM9 boot diagnostics, fastboot RAM boot, and staged full recovery/safety audits preceded the persistent install. A red LED/non-boot event sometimes occurred after restarts; previous owner button/power actions could recover. **Do not infer chip failures from the LED alone; avoid unnecessary reboot/flashing**.
- BCM4329 Bluetooth HCI UART software stack `hci0` was physically registered, HCI UP and DOWN accepted, and modules cleanly unloaded. Separate v06.3 evidence includes private HCD/patchram load and HCI lifecycle. This does **not** establish full pairing, Wi-Fi/BT concurrent coexistence, FM or pwrseq-provider acceptance. Proprietary HCD is not a kernel patch.
- Early v06.2/v06.3 RAM-only test environments verified USB control, onboard SDIO identity, firmware handoff, and module load/unload. All are preserved milestones, **not** the final persistent OS deployment.

### Persistent Debian installation, 2026-10-26

- The **replacement MZ600** was deliberately converted to a standard internal-p8 Debian 12.15 ext4 installation, after approved backups and temporary boot tests. BigPart mapping provides p8 (1GiB ext4) as root. Runtime command line `root=/dev/mmcblk0p8 rootfstype=ext4 rootwait rw init=/sbin/init`; prefer stable ext4 UUID in `/etc/fstab`, not a dynamic BigPart PARTUUID assumed stable across boots.
- Stage-D Linux boot image was the **only authorized persistent p7 flash**. It was SHA-pinned, owner-executed via local `.cmd`, verified normal persistent reboot and Debian login. Physical p7 raw readback over boot image length **matched** image SHA `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8` (image length 6,645,760B). Full raw 8MiB p7 SHA `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`. **Do not reflash this to prove it again.**
- Kernel runtime reported `uname -r=7.0.0-next-20260422+`, `/dev/mmcblk0p8 ext4 /`, Debian 12.15. Full modules eventually installed matched to kernel ABI. The separate `+ ` suffix / modversions mismatch and WCC auto-plugin import CRCs must always be handled honestly, not bypassed.
- Physical native installed Debian Wi-Fi bring-up with then-existing generic firmware `4.220.48`: interface `wlan0`, real passive 2.4GHz scan of three requested frequencies, **19 observed BSS**, clean WCC→brcmfmac→brcmutil teardown and independent postflight. This was a particular v064 installed-state milestone **not** equivalent to current OEM2012 ESCAN repeat-scan test.
- Original p7/p6, factory Android backup, recovery/rescue images and eMMC GPT were protected. Linux installed on replacement DUT; **do not conflate with the owner's other Xoom devices**.

## 5. Evolution of the BCM4329 scan investigation (do not redo settled experiments)

### Legacy HRI39 firmware / V11: proof the scan engine and BSS can work

- Motorola legacy `HRI39` firmware `4.218.248.20` did not support modern `escan` in earlier tests. Original legacy `WLC_SCAN` (IOCTL 50), `WLC_SCAN_RESULTS` (IOCTL 51), Event26 and `iscan`/polling alternatives were studied. Not receiving event26 did **not** mean firmware never scanned: valid results existed.
- V11 physically decoded bounded version-108 BSS records on 5180MHz/channel36, published **four BSS** to cfg80211/`iw`, and restored the original system. This was a **legacy compatibility experiment with a watchdog**, not proof of proper legacy completion or a patch to keep timeouts.
- `iscan` start/continue/abort ABI and lifecycle analyses are documented in `docs/research/MZ600_HRI39_...md` files. Preserve for older-firmware compatibility, but do not graft ISCAN onto the newer firmware if ESCAN already works. The older v108 parser may justify a separate logical patch only if actually needed.

### OEM2012 firmware / V13–V20: real Event69 exists

- An original 2012 Motorola BCM4329 firmware candidate `4.218.248.44` supported 2.4 and 5GHz ESCAN and was selected for later controlled RAM-only tests. Private firmware **264,140B SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`**. **Do not publish bytes or assume this firmware is licensing-cleared for distribution.**
- V15 saw a genuine Event69 `BRCMF_E_ESCAN_RESULT` SUCCESS promptly on 2.4GHz. V17–V20 traced ingress, worker dispatch and event framing, ruling out the fiction that firmware never signals scan end.
- V19 established that `brcmf_fweh_event_worker` sometimes discarded a true terminal SUCCESS because decoded `emsg.bsscfgidx` did not resolve a live `drvr->iflist[]` (or exceeded bounds). Hence the normal `brcmf_cfg80211_escan_handler` was never called and the scan watchdog fired.
- V20 demonstrated that with **ordinary valid interface index0**, the unmodified normal cfg80211 completion handler can finish promptly. All 17 inspected Event69 headers reported **event message version2**. Do **not** claim the older "version1 header missing two bytes" theory was proved, or that firmware actually corrupts index bytes. Some partials have ambiguous indices; exact root cause still unproven. Beware of dmesg ring rollover in old scripts.

### V21: controlled *causal* lab proof of existing Event69 owner route

Six separate full SHA/rollback tests, same exact ARM module and private 2012 firmware:

| Trial | Owner fallback | Terminal decoded `bsscfgidx` | Actual outcome / meaning |
| --- | --- | ---: | --- |
| `term1-01-mask000` | OFF | 16 | Lost normal route, **10,476ms** watchdog, 0 BSS |
| `term1-02-mask001` | ON | 0 | **1,388ms** / 3 BSS, normal route, fallback not used |
| `ba21-01-mask001` | ON | 1 | Fallback **logged eligible+DELIVER**, **1,642ms** / 3 BSS / `aborted=0` |
| `ba21-02-mask000` | OFF | 0 | **1,613ms** / 3 BSS, normal route |
| `ba21-03-mask001` | ON | 16 | Fallback **actually delivered**, **1,232ms** / 3 BSS, same invalid index as OFF negative |
| `ba21-04-mask000` | OFF | 0 | **1,654ms** / 3 BSS, normal route |

The data prove **two genuine corrective deliveries**, not that all successes were due to the fix. The fix **does not fabricate an Event69**, universally rewrite firmware indices, or guarantee all future scans. Original clean restoration passed all six trials. V21 exact module SHA `aa222e2bebe47b76649dacabeddfd3d6fe823813a74c267b73c82813fcd13741`; lab toggle `mz600_terminal_owner` default OFF. **Not upstream-ready:** scan generation, races, cancellation, teardown/multiif.

### V22b–V23: firmware transaction identity actually exists

- The 12-byte fixed `struct brcmf_escan_result_le` envelope provides `buflen`, result-version, `sync_id` and `bss_count`; true Event69 terminal is `status=SUCCESS`. Linux previously sent fixed `0x1234`, which alone cannot distinguish stale generations.
- V22b measured requested `0x1234` (4660), returned **4660** in real terminal `bytes=12 buflen=12 escan_version=109 bss_count=0`, normal scan complete in **750ms / 3 BSS** (normal index0; fallback NOT used).
- V23 explicitly requested non-default **`0x1235` (4661)** and **`0x1236` (4662)** in *separate module-load trials*. Firmware returned the exact respective sync ID, both problematic `bsscfgidx=1` terminals exercised the V21 owner route, and scans completed **1,847ms / 3 BSS** and **1,742ms / 3 BSS**. This proves firmware honors host-selected IDs, not that scans are race-safe or a second scan in one module has completed.
- Key evidence: [V23 physical checkpoint](../checkpoints/MZ600_V23_ALTERNATE_ESCAN_SYNC_IDS_FIRMWARE_ECHO_PHYSICAL_PASS_2026-10-27.md). Proprietary network identity stays private.

### V24: in-session generation, module-ABI lesson, second request initially host-blocked

- Per-device generation state was added experimentally to `cfg80211.h`, source-restoring builder V24, default-OFF lab switch. Generated first in-session **4661**, true terminal returned 4661, checked before owner fallback and in ordinary ESCAN completion; **first scan passed** (three BSS, around 1.2s).
- Adding shared structure members changed `CONFIG_MODVERSIONS` CRCs exposed to the separate firmware-vendor WCC plugin. Old installed `brcmfmac-wcc.ko` failed with `disagrees about version of symbol brcmf_set_wsec` and `brcmf_fwvid_register_vendor`. Do not override CRC or pretend the module compiled for another ABI works.
- A matched WCC module **5892B SHA256 `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`** compiled from the same V24 tree. Automatic `request_module("brcmfmac-wcc")` can race a *later manual insmod*. Resolved in **guarded lab only** by a SHA-verified temporary RAM bind onto the exact installed WCC path *before* standard driver load. After test, unload and unmount both WCC and firmware, verify original installed WCC SHA `31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80`. Production distro solution is to ship mutually matching modules, **not** use bind mounts.
- First scan passed, but old constrained second `iw ... scan freq 5180 passive` immediately returned `Operation not permitted (-1)` in ~23 ms; no second scan generation was generated on that V24 test. Preserved private trial attempts `gen24a`, `paired24b`, `spacing24c`, `autowcc24d`, each unique/consumed; failures did not authorize repeating IDs.

### V25–V27: disentangle artificial regulatory gate from true firmware error

- V25 instrumented *request fields at rejection*: first and second requested the same **one channel36/5180MHz, zero SSIDs, IE length0, BUSY=0**. After a successful passive scan, cfg80211 beacon-hint handling had **removed `NO_IR`** (without disabling the channel or setting RADAR). The *lab-only* guard demanded it stay present, causing the host's `-EPERM`; this was not a legal/regulatory requirement.
- V26b removed **only that obsolete conditional** (did **not** clear flags). In one continuous module session, first scan generated 4661 and completed with real Event69. Second scan **passed** host admission, generated the next ID **4662**, and submitted ESCAN, but `brcmf_fil_iovar_data_set("escan", ...)` returned generic Linux **`-52`** in ~66ms. No second firmware terminal was emitted because the request was not accepted.
- V27 narrow `fwil.c` error instrument decoded native firmware **`BCME_NOTUP=-4`**, translated by Linux to `-EBADE/-52`, on the second ESCAN. The first controlled scan completed, the second returned the error. **This is a firmware-reported state error, not proof of Linux netdev IFF_UP loss, radio power rail failure, or sync-ID incompatibility.**
- Existing brcmfmac source has `BRCMF_FEAT_QUIRK_NEED_MPC` specifically for BCM4329: `brcmf_scan_config_mpc(ifp, 0)` before scan, `brcmf_scan_config_mpc(ifp, 1)` after completion, firmware `mpc` iovar, plus normal `BRCMF_C_UP/DOWN` elsewhere. **Whether MPC or scan/BSS ready-state causes NOTUP is UNPROVEN**. Do not arbitrarily issue UP, reset or force MPC off forever.
- **Do not restore old NO_IR/passive/ch36 guards.** Regulatory enforcement belongs to cfg80211, including actual channel legality/DFS/power. More restrictions are not safer if they artificially reject permitted operations.

### V28: decisive *normal* multi-channel proof; V29 offline follow-up

- Owner instructed us to remove all lingering superficial restrictions, because the next goal is real network joining. V28 removed lab-imposed channel36/5180MHz, no-SSID/IE gate, global forced passive, fixed 500-ms dwell and blanket `NO_IR` on firmware-supported channels. No manual regulatory flag clearing.
- Physically tested V28 with normal **`iw dev wlan0 scan`**: **first scan rc0, 2,834ms, 12 BSS** across native discovery, a major improvement from the ch36-only test. **Second scan same module rc204, firmware/general error `-52` after 50ms**. First scan success does not make a two-scan suite PASS. Exact module SHA `f58391f2eb7753ea7effe4fa83fcf9364523cf90e4aaeaadf663a5d91cfd0d8b`, 352004B; matched WCC SHA as above. Trial `native28a-01-mask000` consumed. Both temporary overlays were unmounted and original runtime independently checked.
- Firmware capabilities under V28 fallback: **35 valid channels (11 2.4GHz, 24 5GHz)**. A reported **zero 5GHz channels with NO_IR** is *not* license to transmit anywhere: inspect the **effective** cfg80211 regulatory domain, custom wiphy restrictions, DFS/radar and power ceilings before directed active probes or association.
- The V29 builder `tools/forensics/build_mz600_v29_regulatory_preserving_native_scan.py` was a *source-only/offline* regulatory-preserving revision. It aims to retain effective `orig_flags` / cfg80211 decisions while advertising valid firmware-supported channels and known 20MHz limitations. V29 source compiles offline in exact ABI; **do not claim V28's 12 BSS hardware PASS belongs to V29 or its extracted canonical diff**.
- Any other later local V27/V28 experimental files/folders must be checked in current Git/Surface; **version labels can collide across independent diagnostic branches**. Prioritize exact source path, module SHA, receipt and checkpoint over a bare version number.

## 6. Current kernel patch artifacts — WHAT IS canonical now and what is not

### Broad four-member *integration snapshot* (preserved, clean-applying, not review-submittable)

Current snapshot folder `patches/upstream/candidate/`:
1. `0001-arm-dts-tegra20-motorola-stingray-board.patch`: 1713-line lab-derived Stingray DTS plus Makefile integration; canonical renamed board file **not independently rebuilt/booted**.
2. `0002-arm-tegra-stingray-wlan-mac-atag.patch`: per-device bootloader WLAN MAC vendor ATAG→FDT bridge; older analogous hardware evidence exists but exact normalized patch not separately booted.
3. `0003-block-partitions-motorola-xoom-bigpart.patch`: opt-in BigPart GPT logical view, physically validated via installed p8 Debian but clean-source final review of generic safety outstanding.
4. `0004-wifi-brcmfmac-bcm4329-legacy-compatibility.patch`: ~680 lines merging channel fallback, per-scan ID and Event69 owner attribution, **lab log/toggles**. Reflects V29-source-oriented snapshot, **not** a clean review-worthy logical unit.

Source snapshot creation commit `cf009ca`, SHA-pinned `candidate-manifest.json`; all four **passed ordered `git apply --check` and exact byte-for-byte source replay against pinned clean base**. No full final-series compile/boot/association was conducted. README was explicitly corrected later to prevent treating this as upstream patch boundary. **Do not apply the four snapshot patches and then apply future split review patches over them.** They are an *alternative reference integration representation*, not a review-series dependency.

### Intended fine-grained *review* patches

See `docs/plans/MZ600_UPSTREAM_CANONICAL_PATCH_DECOMPOSITION_2026-10-27.md` for the authoritative subject matrix. Numbering below is conceptual, not final `[PATCH N/M]` ordering:

| Area | Logical patch and conditions | Present state |
| --- | --- | --- |
| **BOARD** | Base Stingray board DTS and binding-compliant hardware description; optional distinct BCM4329 SDIO power resources, Bluetooth UART, bindings as needed | Existing large DTS source snapshot; normalized board file, DT schema and exact series build not fully tested |
| **BOOT** | Preserve individual Xoom WLAN MAC from bootloader ATAG in FDT, with input/bounds/country/identity separation | Prior RFC and lab evidence; separate ARM subsystem subject |
| **STORAGE** | Generic-safe, opt-in Motorola BigPart GPT mapping; never write physical GPT | Physically p8 Debian works; generic patch review outstanding |
| **WIFI-1** | Firmware `WLC_GET_VALID_CHANNELS` fallback when `chanspecs` unavailable; bounded channel list, exact firmware capabilities, preserve effective regdom and bandwidth | Physically capability enumeration partly proven; V29 regulatory-preserving source offline-only |
| **WIFI-2** | Generate and validate ESCAN sync transaction identity; protect against stale/late/canceled/duplicate terminal; 16-bit wrap, correct owner/synchronization | Firmware echo physically proven; full race/lifetime proof open |
| **WIFI-3** | Exceptional genuine Event69 **terminal-only** delivery to active, matching scan owner when ordinary interface lookup fails; no fake completion, no rewriting all events, preserve partial/P2P | V21 physically proved lab mechanism twice; secure generic routing API/lifetime checks not yet proven |
| **WIFI-4** | **Not yet implemented**: correct actual repeat-ESCAN firmware readiness issue `BCME_NOTUP` after first completion | Exact root cause unknown, no patch file justified yet |
| **WIFI-5 conditional** | Legacy HRI39 version108 BSS parser/ISCAN only if final support for that older firmware requires it | V11 lab proof; do not mix into modern firmware ESCAN without reason |
| **HW/BT follow-ons** | Genuine independent MMC/SDIO power/clock and combo-resource fixes, Bluetooth/serdev, FM later | Physical partial hardware evidence; true new source changes require separate need/proof |

**Patch splitting caution:** WIFI-2 vs WIFI-3 might be one *indivisible* logical scan-completion lifecycle patch if separation yields a broken intermediate state. Do not mechanically split by file or insist on maximum patch count. Each patch must have a real standalone purpose and bisectable states. Also an upstream DTS normally follows documented bindings/SoC workflow; the earlier snapshot board-first sequence is not automatically appropriate for a public cross-subsystem series.

**Critical NEXT PATCH WORK:** reconstruct source-only clean review patches from the pinned base, with **no test-only `MZ600_Vxx` printk flood/module knobs, fake controller state, artificial passive scans, broad event masks or temporal iteration history**. Keep canonical source patches updated in place and evidence archived separately. Do NOT claim this fine-grained review series is already extracted.

## 7. Project-specific submission rules — the mandatory standards ledger

**The newly created file** `patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md` is the normative local record. It links the exact pinned `xoom-linux/linux` process docs and is linked from `patches/upstream/README.md`, `candidate/README.md` and the decomposition plan. It must stay **beside canonical patch artifacts** and be reviewed before each revision.

- **G01** provenance/base/legal source and receiving branch; **G02** minimal logical scope.
- **G03** apply/build/bisect each prefix; **G04** kernel style, checkpatch, sparse/checkstack and warnings.
- **G05** exact ARM and matched modules/DTB/Kconfig builds; **G06** locking, stale/late/cancel/timeout/duplicate/teardown and multiif.
- **G07** actual regulatory and normal network use; **G08** DTS binding compliance: YAML and `dt_binding_check` / `dtbs_check`.
- **G09** precise built-series hardware regression and additional devices; **G10** correct subsystem maintainers/tree and `get_maintainer.pl`.
- **G11** provenance, licenses/SPDX and human developer certification; **G12** no hidden firmware/rootfs/private data dependencies.

**AI-assisted contributions:** pinned `Documentation/process/coding-assistants.rst` specifically says AI agent **MUST NOT insert `Signed-off-by`**; after real human review the human contributor certifies DCO, and an appropriate `Assisted-by: AGENT_NAME:MODEL_VERSION [SPECIALIZED_TOOLS]` should be used. Never fabricate human identity, signoff, `Tested-by`, physical testing, licenses or maintainer acceptance. This is an *official upstream source requirement*, not optional friendly wording.

**Code and evidence standards:** GPL-2.0-compatible provenance; SPDX; preserve original copyright/licensing; Linux CodingStyle; self-contained technical commit description; every series prefix reasonably buildable/operable; patchcheck `git diff --check`, `scripts/checkpatch.pl`, `sparse`, `checkstack`; dt binding docs and YAML separate/prior when genuinely new; `MAINTAINERS` and recipient routing; normal cfg80211/regulatory rules; actual evidence for any PASS.

**Known status:** 12 gates are mostly **OPEN/PARTIAL**, *not PASS*, for the new fine-grained review series. A source integration snapshot applying cleanly is only a source-application fact.

## 8. Exact engineering problem now: repeat ESCAN returns firmware NOTUP

### Confirmed data

1. Normal hardware can initialize BCM4329 SDIO, firmware and `wlan0` on the replacement Linux7 DUT.
2. The 2012 firmware supports ESCAN and emits genuine status-SUCCESS Event69; when callback receives proper owner, normal `cfg80211_scan_done` can complete.
3. In-session generated ID4661 was accepted/echoed on first scan; ID4662 was generated and offered on second V26b scan. Its firmware ESCAN iovar returned Linux `-52`; separate V27 firmware numeric mapping **`BCME_NOTUP=-4`**.
4. After **all old forced-passive/ch36/NO_IR/dwell gates were removed** in V28, **first normal multi-channel scan 12 BSS** succeeded and second `-52` persisted. Those extra restrictions are therefore **not the causal underlying second failure**.
5. Normal scan completion in `cfg80211.c` may restore firmware `mpc=1` after requesting `mpc=0` at scan start; BCM4329 has `BRCMF_FEAT_QUIRK_NEED_MPC`. This is a **hypothesis**, not proof of a particular power-state bug.

### High-information investigation — do next, without broad random testing

A. **Source-only audit before further RF test.** On exact `v064-bigpart-linux` source inspect `brcmf_cfg80211_scan`, `brcmf_do_escan`, `brcmf_run_escan`, `brcmf_cfg80211_escan_handler`, `brcmf_notify_escan_complete`, `brcmf_abort_scanning`, `brcmf_scan_config_mpc`, `brcmf_set_mpc`, `brcmf_fil_iovar_*("escan"/"mpc")`, `BRCMF_C_UP/DOWN`, `feature.c` BCM4329 NEED_MPC, `fwil.c` Broadcom error conversion and SDIO/runtime PM. Identify exact branch responsible for turning interface/BSS/power "not UP" after successful scan. Compare original Motorola firmware and modern brcmfmac behavior, but do not port arbitrary OEM workaround wholesale.

B. **Minimal reversible numeric state measurements** if source review leaves alternatives: at startup, before first request, immediately after genuine Event69 and before/after second `escan`, inspect supported firmware `mpc`, UP/BSS status, scan busy/owner, interface `IFF_UP`, state of power votes/SDIO clocks; do not print identities. Probe via read-only IOCTL/iovar where defined, and record return codes when unsupported. Preserve normal cfg80211 scan requests; **do not reintroduce forced channel36 or NO_IR**.

C. **Small controlled causal A/B** based on actual evidence, not speculative UP/DOWN reset: e.g. firmware MPC readback variation or already-available official resume path with a single changed variable and independent rollback. A same-ID second-scan control may distinguish transaction-ID hypothesis if appropriate, but must be *correctly interpreted* and not accidentally bypass new generation safety.

D. When actual cause is demonstrated, implement the minimal generic-compatible **WIFI-4 logical fix** and re-test: two or more normal scans in one loaded instance; terminal statuses and sync IDs; no watchdog; then user-authorized **normal association/authentication/IP** on an allowed network. No credentials in public files. Independently check effective regulatory domain and DFS/power before transmit. Owner may elect to supply network secrets through secure local handling; **do not read unrelated password notebooks or clipboard speculatively**.

E. Concurrently or subsequently, **extract the fine-grained review series** (WIFI-1, WIFI-2/WIFI-3 as properly scoped, real WIFI-4 only after fix) from the clean base. Review the entire-source net effect, complete required tests per standards checklist, and maintain one canonical file per logical issue. Do not submit or sign off automatically.

### What NOT to do again

- Do not "prove" Event69 exists again, tweak subscription masks forever, or mistake header version2 for a confirmed version1 padding bug.
- Do not claim scan completion from a watchdog or fake `cfg80211_scan_done`.
- Do not set `drvr->iflist[0]` for every firmware event; only prove a narrowly validated active scan owner as needed.
- Do not treat a 12-byte terminal fixed `sync_id=0x1234` as sufficient stale-event protection if every request uses that same ID.
- Do not add or preserve the old NO_IR/ch36/forced-passive restrictions solely for developer convenience; do not clear *legitimate* regulatory restrictions to make association work.
- Do not globally disable MPC, force firmware UP/DOWN, hard-reset shared WLAN/BT rails, or hack on-chip firmware on an untested hypothesis.
- Do not conflate a single completed scan, two separate module-load scans, two **host-submitted** scan IDs, and two successfully **firmware-completed** scans.
- Do not use V29 physical claims inherited from V28; V29 was an offline source revision.
- Do not apply experimental V21–V29 patches in sequence or create "fixup" series members.

## 9. Tested host-to-host transfer, COM9 one-shot and rollback procedure — MUST FOLLOW

The definitive SOP is `docs/process/DESKTOP_SURFACE_XOOM_ARTIFACT_TRANSFER.md`. User explicitly objected when malformed commands and ad hoc transfer methods repeatedly interrupted routine work. **It works consistently when followed correctly.**

**Stage 0 — command/ID checks:** confirm which host runs each command, that the destined file/trial ID is unused, no concurrent COM9 console or tool session is live, previous .attempted not reused, and the expected exact module SHA/size/source restoration is recorded. Verify present desktop IPv4; historical value `192.168.0.125`. No unprompted alternative network port.

**Stage 1 — compile on desktop WSL.** Source `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux`, toolchain `arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf`, target ABI `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`. Before/after source checksums and `make` logs. If shared `cfg80211.h` ABI/CRC changes, **also build matched WCC** and compare symbol versions. Do not erase prior build directories or reuse SHA.

**Stage 2 — desktop WSL artifact to desktop Windows staging.** Use simple WSL `cp` into *new* `/mnt/c/Users/olsen/AppData/Local/Temp/mz600-<unique-id>/`, compute `sha256sum` there. Note **this is not yet cross-host transfer**.

**Stage 3 — existing desktop HTTP transfer.** Confirm 43157 free. Start native Windows PowerShell command on desktop:
```powershell
py -3 -m http.server 43157 --bind 192.168.0.125 --directory 'C:\Users\olsen\AppData\Local\Temp\mz600-UNIQUE'
```
This is short-lived LAN-only with only the intended hashed files. Inspect listener and exact process CommandLine; do not serve arbitrary private directories.

**Stage 4 — Surface direct native PowerShell** (avoid nested `powershell -Command` quoting/malformed variables):
```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://192.168.0.125:43157/FILE.ko' -OutFile 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-UNIQUE\FILE.ko'
Get-Item -LiteralPath 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-UNIQUE\FILE.ko' | Select-Object Name,Length
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-UNIQUE\FILE.ko'
```
Refuse if bytes/size differ. The known standard uses **43157**, not speculative 43158.

**Stage 5 — close server and staging:** stop *only* verified server PID, confirm 43157 no listener, remove *only* that run's desktop temporary directory. Surface private captures persist.

**Stage 6 — COM9 guarded one-shot:** sole client pyserial COM9 115200; UID0, correct `uname`, `findmnt / = p8 ext4`, input SHA and `bash -n`, original firmware/NVRAM/module/WCC SHA, wlan down, WPA/BT states, no unknown bind overlays, correct regulatory context; stage RAM files under `/run` and verify SHA. In WCC ABI mismatch case a *conditional, guarded* temporary bind of matched module into standard autoload path is documented; no persistent module overwrite and no disabling modversions. Use precise unique `.attempted` marker, stable `/dev/kmsg` sequence markers (not ring-count heuristics), time-bounded commands, fail-closed `trap` restoration and private logs.

**Stage 7 — independent original-state check:** after unload WCC→brcmfmac→brcmutil and unmount of temporary WCC/firmware, confirm **installed** firmware/NVRAM/core/WCC hashes, no overlays, wlan state, Bluetooth quiet, COM9 still usable. Record independent preflight/receipt; it is possible for **cleanup integrity to PASS even when test suite rc is nonzero**. Never claim a successful scan test because cleanup passed.

**Incident lessons:** malformed quoted Windows PowerShell and a needless port change caused repeated apparent file-transfer issues; user correctly identified this as procedure drift, not a fundamental transfer blocker. Do not reinvent transports. A remote tool refusal is not license to bypass safety; note the refusal honestly. The same temporary-server method later transferred V21–V28 builds successfully.

**Confidentiality:** raw scan outputs contain nearby SSIDs/BSSIDs, device MACs/serials and proprietary NVRAM/firmware. Keep private Surface transcripts and proprietary binary outside public Git; public reports include sanitized event codes, numeric status, elapsed ms, sizes, checksums and explicitly cited local paths only.

## 10. Preserved hashes / named experiments / source trust boundaries

| Item | Immutable identifier | Why it matters |
| --- | --- | --- |
| Source base | `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3` | xoom-linux pinned kernel baseline; verify actual current receiving branch before submission. |
| Persistent p7 boot | SHA256 image `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`; full p7 `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c` | Physically verified normal Linux7 boot; preserve unchanged. |
| Installed original firmware | `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93` | Do not overwrite with 2012 candidate permanently. |
| Original NVRAM | `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb` | Calibration/identity private; avoid global US/69. |
| Original installed WCC | `31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80` | Source-ABI checks and rollback. |
| OEM2012 test firmware | `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834` | Verified lab `4.218.248.44` test candidate; private, RAM only. |
| V21 tested core | `aa222e2bebe47b76649dacabeddfd3d6fe823813a74c267b73c82813fcd13741` | Six-trial causal Event69 owner fallback evidence. |
| V23 tested core | `dc338742e4e8c36fca4b325ee6a885bb888949281129f6898c420a4e39f45bcf` | Physically proven alternate request ID echo. |
| V24 first-generation core | `784a564baa66446aff0ea0d9d4984736c34cb133fa61a43d526295eba0c9e6e3` | Matched WCC needed; single-generation result. |
| Matched WCC used in V24+ | `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d` | Core/plugin exported CRC compatibility; tested RAM pairing. |
| V28 native scan core | `f58391f2eb7753ea7effe4fa83fcf9364523cf90e4aaeaadf663a5d91cfd0d8b` | Exact 12-BSS physical normal scan + failed second. |
| Broad source snapshot | Git project commit `cf009ca`, 4 patch SHA256 values in `candidate-manifest.json` | Clean-source integration recovery reference only. |
| Standards file | `patches/upstream/candidate/SUBMISSION_REQUIREMENTS.md`; head at start of this handoff was `3ca9a85c4f980d9d75ae291d2921a5b6c4fe44fa` | Current G01–G12 and pinned source links; this handoff commit will advance HEAD. |

**Consumed one-shot IDs:** V21 `term1-01-mask000`, `term1-02-mask001`, `ba21-01` through `ba21-04`; V22b `sync22b-01-mask001`; V23 `sid23a-01-mask000`, `sid23a-02-mask001`; V24 `gen24a-01`, `paired24b-01`, `spacing24c-01`, `autowcc24d-01`; V25 `gate25a-01`; V26b `reg26b-01`; V27 `fwerr27a-01`; V28 `native28a-01`. The complete identifiers and private SHA receipts are in each checkpoint. **NEVER rerun an existing ID or overwrite existing trial files**.

## 11. Clean continuation checklist for the next agent/conversation

**On first response to "continue":**

1. Read the mandatory standards file, decomposition plan, latest status/ledger and this handoff. State that `candidate/series` is a **broad snapshot** and that fine-grained review patch files have **NOT** yet been extracted. Do not confuse a logical decomposition plan with actual built patches.
2. Using GitHub/desktop connector, check Git branch + `git status --short --branch` and exact HEAD **at that time**. Do not assume old latest commit or that a working tree has no concurrent changes. Inspect relevant source files and existing scripts/binaries before replacing anything.
3. If the next task is **fix repeat scan**: perform targeted source audit of `BCME_NOTUP` vs MPC/readiness. Quote exact current source line/functions and formulate a falsifiable read-only numeric test. Only then compile a minimal source-restoring candidate with both core and matched WCC and run a unique RAM-only test through the canonical SOP. Preserve V28 full normal scan policy and regulatory correctness.
4. If next task is **canonical patches**: begin the fine-grained review-series extraction from clean xoom-linux base. Prioritize WIFI-1 channel enumeration, then WIFI-2/3 ESCAN lifetime and true owner handling, and only add WIFI-4 after demonstrated root cause. Treat board/ATAG/BigPart as separate proper subsystem patches/series; DT bindings before DTS where needed. Run G01–G12 checks as possible, mark gates OPEN if not.
5. For either: maintain a private hash/receipt per physical run; keep original boot p7/p8 untouched, do not expose credentials/private binaries, do not promise work without actually executing it, do not fake human DCO/assisted-by tests.
6. Every advance: **update the existing canonical logical source patch** (or issue file for still-unsolved issues), plus status/ledger/requirements evidence. Avoid accumulating unrelated workaround code or per-version patch fixups.
7. Stop and report an actual blocker if a tool or safety gate prevents required action; do not describe it as general incompetence of ordinary cross-host file transfers. Use the known-good procedure.

**Precise immediate engineering question:**

> On the OEM 2012 BCM4329 firmware, after a real ESCAN SUCCESS Event69 and Linux cfg80211 completion, why does the next ordinary `escan` iovar return firmware `BCME_NOTUP=-4` despite the host submitting a valid next-generation request? Is there a required firmware MPC/BSS/UP transition or an existing brcmfmac lifecycle bug? What smallest generic-correct, race-safe driver change preserves normal cfg80211/regulatory behavior and yields two actual firmware-completed scans plus standard network join?

**Precise immediate patch-series question:**

> How do we express channel enumeration, transaction/generation lifetime and exceptional terminal-owner routing as the smallest individual reviewable, self-contained, per-subsystem patches, each safe at every series prefix, obeying the pinned `xoom-linux/linux` process/AI DCO/Devicetree rules—while preserving all verified behavior and excluding laboratory debug scaffolding?

### Final handoff truth table

| Claim | Status |
| --- | --- |
| Replacement MZ600 boots persistent Debian from internal p7/p8 | **PHYSICAL PASS; p7 raw SHA verified** |
| BCM4329 SDIO firmware `wlan0` init and Bluetooth HCI software lifecycle | **PHYSICAL PASS in specified configurations**; coexistence/full BT use not proven |
| OEM firmware scan engine returns real Event69 SUCCESS | **PHYSICAL PASS** |
| Missing-interface terminal can be delivered to actual Linux scan owner | **PHYSICAL LAB PASS in two controlled V21 trials** |
| OEM2012 firmware echoes 0x1234, 0x1235, 0x1236 ESCAN IDs | **PHYSICAL PASS** across identified tests |
| V28 normal multi-channel Linux scan | **PHYSICAL PASS, 12 BSS** |
| Two successful native ESCAN completions in same loaded driver | **FAIL/OPEN**; second firmware command `-52`; V27 specific `BCME_NOTUP=-4` |
| Normal Wi-Fi association, authentication, DHCP | **NOT TESTED with V28/V29 candidate** |
| V29 regulatory-preserving source equivalent to V28 physical proof | **NO**; V29 offline-only |
| Broad four-patch snapshot applies from clean pinned upstream | **SOURCE APPLICATION PASS only**, not combined compile/boot |
| Fine-grained review-quality upstream series exists | **NOT YET**; decomposition plan and standards ledger ready |
| Owner authorized an upstream Linux submission or human DCO signature | **NO** |
| Original installed firmware/module/p7/p8 changed by V21–V28 lab trials | **NO**, independent restorations verified at the documented trials |

**End-of-handoff instruction:** Continue engineering from facts, current source, the standard operating procedures and G01–G12—not from repeated assumptions or past assistant assurances. Read this document plus the linked primary evidence first. Maintain a source-constrained, no-shortcuts, reviewable kernel patch series and preserve the working Xoom installation.
