> **V20 SOURCE REVIEW 2026-10-27:** [Versioned event-header ABI audit and guarded V20 plan](../research/MZ600_V20_EVENT_HEADER_ABI_SOURCE_AUDIT_2026-10-27.md) now confirms current Linux7 `fweh.c` reads bsscfgidx and sets event data offset assuming the modern header without checking event version first; historical Broadcom v1 lacks those last two bytes. Crucially V19 never measured version, and potential 2-byte payload alignment must be audited before enabling any fallback. SOURCE-ONLY; no V20 build, module or Xoom scan has yet occurred.

# XoomLinux7 / Motorola Xoom MZ600 — complete V19 → V20 engineering handoff

**Canonical continuity snapshot: 2026-10-27, after actual V19 physical experiments. Active branch: `wip/clean-wifi-bt-usb-20261025` in `Olsens11/XoomLinux7`.**

> **READ THIS FIRST in the next chat.** It supersedes older document headlines suggesting V11/V12/V14–V18 are still pending. The newest PHYSICALLY CONFIRMED result is that the 2012 BCM4329 firmware **does send an on-time 5GHz scan-completion Event 69**; in failing scans, the Linux 7 firmware event worker **cannot resolve the interface indicated by the event header**, so it discards completion. We have not yet proven the precise reason for the header/index mismatch, and no production fix is installed.

## 1. Owner's goals, what we are building, and design philosophy

The owner is repurposing multiple Motorola Xoom tablets with a real native Linux 7 ARMv7 kernel and Debian armhf userspace. Primary developer/experiment target is **MZ600 Verizon CDMA / stingray**. Preserve the successful internally installed BigPart Linux baseline, original factory per-device data, and a route to stock Android or recovery where available. Other Xoom variants (MZ604 wingray Wi-Fi, MZ602, Xyboard) are secondary platforms and MUST be validated independently.

Near-term goal: **proper native Broadcom BCM4329 SDIO Wi-Fi on both 2.4 and 5 GHz** with normal cfg80211/iw scan results, real firmware-driven scan completion, valid association/DHCP later, coexistence with Bluetooth, and a clean small upstream-friendly patch set. The owner insists on a minimal causal fix: first prove the failure, change one logical thing, A/B the same module if possible, retain all diagnostic and experimental observations, then strip away temporary instrumentation. Do not add speculative power toggles, fake scan completion, unnecessary extra event subscriptions, regulatory workarounds, or arbitrary delays.

Other longer-term goals: proper shared-chip Wi-Fi/BT startup/clock/regulator sequencing, stable Bluetooth HID, audio, battery/charging/power management, native GUI, and eventually the optional Windows 95 under Linux idea. The separate TWRP Xoom Toolkit with Wi-Fi, Bluetooth, SSH and Desktop Commander is a separate project/reference implementation, NOT the new Linux7 Wi-Fi kernel patch.

## 2. MOST IMPORTANT V19 breakthrough: exactly where 5GHz completion is lost

V19 used the same private 2012 Broadcom BCM4329/3 firmware `4.218.248.44`, firmware SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, on the same MZ600 with Linux kernel `7.0.0-next-20260422+` and Debian 12.15. Two fully guarded 5180 MHz channel36 **NO_IR passive** scans, 500ms explicit dwell, load-time extra event mask **0**, were performed using a RAM-only diagnostic module. Both timed out at 10,454ms and 10,149ms, but driver instrumentation PROVED:

```text
MZ600_V19_FWEH_INGRESS code=69 status=0 reason=0 datalen=12 subscribed=1
MZ600_V19_FWEH_ADMIT code=69 status=0 datalen=12 pktlen=86
MZ600_V19_FWEH_WORKER code=69 status=0 bsscfg=1
MZ600_V19_FWEH_DISPATCH code=69 status=0 ifp=0 handler_rc=-22
```

The terminal-success packet passed event-code/subscription and length validation, allocation and queueing, was dequeued and entered worker dispatch. **The event is NOT missing from firmware, too late, or stopped by a hidden SSID.** Its reported `bsscfgidx=1` resolves to a NULL `ifp` on this single-WLAN MZ600, so `brcmf_fweh_call_event_handler()` returns `-EINVAL` before `brcmf_cfg80211_escan_handler()` sees SUCCESS. The worker also dropped several valid-looking Event69 PARTIALs early as `bsscfgidx=140`, exceeding `BRCMF_MAX_IFS=16`. V19 first scan: 5 bad-bsscfg drops, 16 admitted, 11 worker and 11 dispatch; second: 3 bad-bsscfg drops, 13 admitted, 10 worker and 10 dispatch. Seven partials reached cfg80211 each; terminal did not. NO durable system change occurred, and both posttest audits passed.

**Working hypothesis, NOT YET FACT:** an older Broadcom firmware **version-1 event message** lacks the trailing `ifidx` and `bsscfgidx` bytes that modern `brcmfmac/fweh.h` always expects. A later version-2 header adds them. The original Broadcom `bcmevent.h` reference defines both formats. V19 did NOT log `event_msg.version`, and therefore v1 cannot yet be asserted. Other possibilities include garbage/alternate event indices or transient interface lifecycle mapping. Prove the actual packet version/bytes and valid payload/header framing before writing the production patch. Do not globally force `iflist[0]`.

**Very next engineering task:** source-audit and develop **V20**, a minimal diagnostic/experimental module that prints only numeric event header version, raw `ifidx`, raw `bsscfgidx`, packet and payload lengths, interface-map eligibility and event code/status. Retain V18's load-time configurable event-subscription mask and V19 ingress/queue/dispatch audit. Add a separately gated, default-OFF lab-only one-bit compatibility fallback for **BCM4329 + Event69 ESCAN_RESULT + demonstrably single primary WLAN + missing/invalid index only**, ideally conditioned on demonstrated legacy header version. Compare fallback off/on with the SAME exact module build, constant firmware/scan/BT/runtime. No remapping other events, other chips, P2P/multi-interface, or valid interface mappings. First validate event-version interpretation and physical no-TX constraints. Extract a tiny production fix ONLY after repeatable scan success and regressions.

## 3. Decisive V14–V19 physical chronology (earlier V0–V13 below)

| Test | Firmware/protocol/target | Actual observation | Interpretation/status |
|---|---|---|---|
| V14 | 2012 OEM BCM4329 ESCAN V1, 5180 MHz ch36, default passive dwell | 1 Event69 PARTIAL BSS109, no handler terminal, ~10.48s watchdog, 0 user BSS | At the time thought firmware omitted success; **superseded by V18/V19 ingress proof** |
| V15 | Same firmware, 2412 MHz ch1 passive | 2 partials, genuine Event69 SUCCESS, normal cfg80211 scan done and 2 user BSS at 179ms | First same-firmware proof of 2.4GHz normal ESCAN completion |
| V16 | Same 5GHz ch36, explicit 500ms passive dwell, unchanged chanspec 0x1B24, V1 escan accepted | 7 handler partial packets; 3 cached BSS109; no handler terminal; ~10.374s watchdog | Longer dwell NOT sufficient to fix outcome; firmware terminal might have been lost after ingress |
| V17 | Same ch36/500ms, broad Event26/45/13/14/35/40/63 subscriptions plus Event69; quiescent BT modules retained | **Real Event69 SUCCESS**, 6 partials, 2 user BSS, cfg80211 aborted=0 at **661ms** | Proven Linux7 5GHz can complete. Extra subscriptions and BT/runtime/logging changed simultaneously; cause unknown |
| V18 | ONE 347,380-byte module, module param `mz600_extra_events=0..127`, ten independent scans | **All 10 raw ingress logs show exactly 15 Event69 PARTIAL plus 1 Event69 SUCCESS; only 2 terminal SUCCESS reach handler.** Extra mask combinations confounded | Firmware completes ON TIME; host event delivery loses events |
| V19 | ONE 348,836-byte module, 2 scans mask0, logging validation→queue→worker→callback | Both raw SUCCESS terminal packets **admitted/queued/processed**, but callback dispatch failed `bsscfg=1 ifp=NULL rc=-22`; several partials invalid index140 | **Most specific verified cause to date**; seek header/version and narrow mapping |

### V18 all-ten individual trial matrix (already executed; NEVER rerun these IDs)

| Trial | Mask | Handler got terminal? | iw duration | iw BSS |
|---|---:|---|---:|---:|
| `ab1-01-mask000` | 0 | YES | 676ms | 1 |
| `ab1-02-mask127` | 127 | NO | 10,401ms | 0 |
| `ba1-01-mask127` | 127 | NO | 10,500ms | 0 |
| `ba1-02-mask000` | 0 | YES | 805ms | 2 |
| `split1-01-mask003` | 3 | NO | 10,362ms | 0 |
| `split1-02-mask124` | 124 | NO | 10,447ms | 0 |
| `bitcheck1-01-mask000` | 0 | NO | 10,515ms | 0 |
| `bitcheck1-02-mask001` | 1 | NO | 10,200ms | 0 |
| `bitcheck1-03-mask000` | 0 | NO | 10,242ms | 0 |
| `bitcheck1-04-mask002` | 2 | NO | 10,492ms | 0 |

All 10 scans used 500ms passive single channel36, exact same module, original NVRAM; all ten had Event69 status0 at FWEH ingress ~9.5–9.8 seconds BEFORE a watchdog in the failures. The apparent early mask0 vs mask127 difference is **NOT causal proof**: later mask0 itself timed out twice. The event-mask feature is a useful research tool, not a production requirement. Handler raw and ingress counts differ because event-worker rejects/misroutes entries; V19 localized dispatch of terminal. V19 two consumed IDs: `drop1-01-mask000`, `drop1-02-mask000` (both independent rollback PASS).

### Hidden SSIDs/channel hypothesis decisively checked

V17 reported six per-BSS metadata observations, of which FOUR had `SSID_len=0`; nevertheless Event69 terminal SUCCESS arrived and Linux returned 2 BSS. All six reported raw chanspec `0x1b24`, `ctl_ch=36`, and valid IE bounds. V18 repeats showed zero-length SSID partials in both successes and failures. Hidden SSID or an AP-count quota is NOT a completion prerequisite. 5GHz passive scans should end even with 0 BSS; never use discovered-BSS count to fake `scan_done(aborted=false)`.

## 4. Hardware, installed Linux, backups and power caveats

- Experimental device: Motorola Xoom **MZ600 stingray CDMA**, NVIDIA Tegra 2 ARMv7 (no NEON), on-board BCM4329 Wi-Fi/BT SDIO/UART shared-chip design; the ORIGINAL owner's MZ600 is a protected, separate reference. Some newly acquired Xoom units have odd volume/power/charging behavior; don't infer all units are identical.
- Upstream kernel source ancestor `xoom-linux/linux` commit `2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3`; running kernel exact ABI `7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8`. Debian 12.15 armhf installed on internal BigPart **p8 ext4**, normal boot from **p7**. Stable ext4 UUID `c2fb0167-7143-4186-b284-c86d6c09ea64`.
- Persistent BigPart p7 actual boot image 6,645,760 bytes SHA256 `fa28f9a9edfd4fd07031faf62de1216abda413e569ff933075ce0aa6ec4c70f8`; complete 8MiB p7 readback SHA256 `901c79cfbeb646dad7f41d6de9d8605029d3fe082231ab7032cdba8cc7c0ff5c`. Working boot uses `root=/dev/mmcblk0p8`; **GPT PARTUUID was observed inconsistent across boots**, so do not casually switch root selector.
- **Do not format p8, flash p7, modify GPT, restore stock Android from memory, or use old small-partition recovery against BigPart without verified geometry/backups.** Android/recovery/p7/p8 original byte-level backups exist in private project storage. Owners encountered red status LED and unusual power button/dock charging behavior; unrequested reboot is a material risk.
- Installed normal generic BCM4329 firmware **4.220.48.0**, 253,748 bytes SHA256 `d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93`. Current Linux NVRAM/calibration 1,550 bytes SHA256 `a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb`; installed `brcmfmac.ko` SHA256 `9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb`. These are critical baseline sentinels.
- Original kernel sources after reversible experimental build: `cfg80211.c` SHA256 `1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8`; `fweh.c` SHA256 `4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c`.
- Original 2012 dual-band lab firmware SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, 264,140 bytes. Kept PRIVATE; staged RAM-only at `/run` per one-shot. Factory MAC read from device must never be hardcoded, modified or placed in public Git. OEM HRI39 earlier FW `4.218.248.20`, 261,317 bytes SHA `7afdc1b85313bcc6054e01bd22aa4540a47cf6f42903b4f9728a1236b955251a` is a separate legacy V108 track.
- Normal generic installed firmware has physically scanned 2.4 GHz (19 BSS in prior tests); regression must be retained. 2012 lab FW physically showed 2.4GHz/5GHz channel lists (11 valid 2G, 24 valid 5G, with 24 5G NO_IR and five 5G disabled in patched wiphy). Official Debian regulatory package source respected; no active transmissions, directed probes, associations, forced country or radar bypass in current lab tests.

## 5. Shared BCM4329 Wi-Fi/BT hardware: do not 'fix' Wi-Fi by breaking Bluetooth

Original Motorola kernel and board audit identified shared U4 rail/power votes, WLAN first power before SDIO card detect, original six-field fabricated SDIO CCCR workaround, SDMMC2 tap delay 6, Bluetooth control GPIOs/shutdown/reset/wake and possibly first rfkill callback ordering effects. Their **exact Linux7 correctness remains to be validated**; do not apply speculative GPIO toggles mid-test. The owner wants a whole-chip design (Wi-Fi + Bluetooth pins/power/clock) that is coherent, but each fix must be separately tested and upstream-friendly.

At V17–V19 Linux runtime baseline, `bluetooth`, `btbcm`, `hci_uart` can be loaded while `bluetooth.service` is INACTIVE and `hci0` is DOWN. That quiescent state is allowed and preserved; do not unload the UART BT module casually or restart HCI merely to satisfy an older overly broad Wi-Fi-only guard. Original Wi-Fi modules (`brcmfmac_wcc`, `brcmfmac`, `brcmutil`) may be loaded with `wlan0` DOWN, while `wpa_supplicant.service` is ACTIVE. The approved wrapper temporarily stops WPA/unloads only Wi-Fi modules, runs the RAM experiment, then restores original modules, `wlan0` DOWN, and WPA ACTIVE. No BT service/controller changes. Validate these states afresh before each new test.

## 6. Host machines, agent tools, connections and exact code locations

**Surface Book 2 / `SURFACE-BOOK-2`:** authorized Remote Desktop Commander device ID `bf441b48-041b-4940-b629-8b441339e80a`, Windows. Experimental Linux MZ600 connected via exclusive **COM9 USB serial gadget, 115200 baud**, providing root interactive console when owner logged in. Python + pyserial serial launcher transfers gzip/base64 in 16-line ACK chunks and verifies every RAM payload SHA256 before test. Surface captures/staging under `C:\Users\olsen\xoom-linux-rom\captures\`; numerous private per-test logs, receipt JSON, attempt-marker files live there. Closing any other COM9 Python session normally is prerequisite; never kill unrelated Bluetooth checker or steal serial access. Owner has previously used Ctrl+] to release console. If it doesn't enumerate, inspect physical state rather than guessing.

**Desktop / `DESKTOP-R16QJD4`:** authorized Remote Desktop Commander device ID `2fc5f6ea-20da-436f-8ad8-c5cd59f44870`. WSL distro `Ubuntu-22.04`, user `xoomdev`; canonical Git checkout `/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/project`, checkout's active branch `wip/clean-wifi-bt-usb-20261025`. Kernel build source `/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux`, separate O=output build directory `v064-bigpart-debian-sdroot-build`, cross compiler ARM GNU 14.3. Lab modules under `v064-2012-oem-escan-vNN-20261026` per version. Do not directly edit checkout's source files without source-restoring builder. Validate `git status --short --branch`, `git pull --ff-only` and `python3 tools/check_repository.py` after docs updates.

**Raspberry Pi:** private reference original Motorola source/ELFs/backups and earlier recovery forensics; a noted private OEM path `/home/ps2/xoom-phase1/private/oem-reference-20261021/`. Not required for most new 2012 Event69 interface fixes; prefer repository source and Desktop.

**GitHub connector:** use `functions.exec`, discover exact `mcp__GitHub__fetch_file`, `mcp__GitHub__create_file`, `mcp__GitHub__update_file` signatures in `ALL_TOOLS`. GitHub branch is WIP, NOT default. Fetch an existing file's current blob SHA before updating; never parallel-update the same file. Cite relevant GitHub docs links in next chat, and after update sync Desktop WSL checkout with fast-forward and run repository checker. Tool `start_process` returning a PID only means started, not completed—poll `read_process_output` and inspect receipts.

**Stock spare Xoom Android reference:** owner's MZ604 Wi-Fi `wingray`, Android 4.1.2 JZO54K, kernel 2.6.39.4, connected to Surface with USB debugging. Windows formerly bound old Motorola `motoandroid.sys` ADB MI_01 and `adb devices -l` showed nothing; with owner's approval ONLY that ADB interface was switched to signed Microsoft `winusb.inf`. Original driver exported at `C:\Users\olsen\xoom-linux-rom\captures\OEM-XOOM-ADB-DRIVER-ROLLBACK-20261027`. Keep MTP and composite parent intact. Stock read-only OEM scan comparison: user deliberately toggled Wi-Fi OFF/ON during test (therefore supplicant termination/restart is EXPECTED, not spontaneous failure), system scan request counter 3→14, cached BSS31→34 (5GHz15→18), one 5180MHz AP, but NO low-level scan terminal measured. See OEM checkpoint. MZ604 firmware is not automatically equivalent to MZ600.

## 7. Exact active engineering files / hashes

| Version | Repository tool / evidence | Status |
|---|---|---|
| V17 | `tools/forensics/build_mz600_v17_2012_5g_all_scan_completion_paths.py`; checkpoint `docs/checkpoints/MZ600_V17_2012_5G_CH36_WIDE_EVENT_MONITOR_REAL_ESCAN_TERMINAL_SUCCESS_661MS_PHYSICAL_PASS_2026-10-27.md` | 346,508B module SHA `d8ccb6f7077d54db0fa95e90debcd0e06494c9acd8e539eabebb7abde68233c7`, genuine 661ms Event69 SUCCESS |
| V18 | `tools/forensics/build_mz600_v18_2012_5g_runtime_event_mask.py`, `scripts/host/xoom/test-mz600-v18-parametric-event-mask-owner-20261027.sh`, `scripts/host/surface/mz600-v18-parametric-event-mask-ab-suite-20261027.py` | 347,380B module SHA `65b805f5fe6ca1d28a14b5af6f1cf7251b490fbed9488a3a69d5f70eed02c229`, 10 trials consumed |
| V19 | `tools/forensics/build_mz600_v19_2012_5g_event_delivery_drop_audit.py`, `scripts/host/xoom/test-mz600-v19-event-drop-audit-mask-owner-20261027.sh`, `scripts/host/surface/mz600-v19-event-drop-audit-suite-20261027.py` | 348,836B module SHA `c6580ff0f2e354e2f8a885bdc76168417e16779b9f93d41db0614375ae67efbd`, two trials consumed, NULL ifp cause localized |

V19 shell SHA256 `9c581f5cdb2da79338eaf26483f124777ac317abc9a09e5c4a20311d6f401beb`; V19 Surface suite SHA `06faaabeea0792e65a39456c4cc534377f801c1ab4c7f94bfd32eacccf8557e0`. V18 shell SHA256 `48c917557330ef6fc75cd9040f2786095291786ef3eb670d29a7ef6c730507ca`. V18 Surface suite SHA `ad98e6713f65e5cfc596a08fb193f3aeb1c75394e7977a53922b1e7887437d20`. One-source variant `build_mz600_v18_2012_5g_ab_event_mask_off.py` had an OFFLINE builder anchor failure and was superseded; DO NOT use it.

Private Surface V17 directory `MZ600-V17-2012-WIDE-EVENTS-20261027`; V18 directory `MZ600-V18-2012-MASK-SWEEP-20261027\runs` (10 JSON/private/attempted sets); V19 directory `MZ600-V19-2012-EVENT-DROP-AUDIT-20261027\runs` (two sets). Private logs are authoritative for timestamps and numeric fields but may contain network identifiers; never upload full private COM9 transcript or fixed device identifiers to public GitHub. Research checkpoint docs contain sanitized aggregates.

## 8. Test harness and fail-closed safety contract

1. Protect installed kernel/boot/OS: no flash, boot.img edit, GPT/p7/p8 format, firmware install, persistent driver replacement or hidden reboot unless owner explicitly authorizes a separate operation with backups. Linux is currently logged-in/root on COM9 after user reconnect but confirm actual port/runtime when next session starts.
2. Reversible OFFLINE ARM build only; pin exact source and baseline .ko hashes; restore source even after compilation failure. Verify kernel vermagic matches `7.0.0-next-20260422+`. Keep private OEM 2012 firmware out of GitHub.
3. Preflight per-unit kernel, root, installed generic firmware SHA, installed NVRAM SHA, installed brcmfmac module SHA, `wlan0` state, original Wi-Fi modules, Bluetooth service and HCI state, and absence of bind overlays. A radio already connected to AP or active BT is a STOP, not permission to force disconnect.
4. Preserve original runtime precisely: if `wlan0` DOWN and WPA active, stop WPA and unload Wi-Fi modules to prepare clean state, but do not unload or alter quiescent `hci_uart`/BT. Always restore original installed modules, `wlan0` DOWN and WPA service original state in `finally` regardless of scan result.
5. RAM-only bind the known SHA-verified 2012 firmware, load SHA-pinned diagnostic `.ko`, retain original NVRAM and factory MAC. Restrict to one **5180MHz channel36 NO_IR, nonradar, HT20 passive** scan with `iw dev wlan0 scan freq 5180 passive`; no directed SSID, active probes, association or regulatory override. Existing V18/19 drivers log actual legacy 0x1B24 V1 scan param and 500ms passive dwell.
6. Event and BSS debug outputs numeric only: never log network SSIDs, BSSIDs/MACs, raw IEs or credentials in public artifacts. `iw` RC0 alone is **NOT** scan SUCCESS: the clean test script can exit 0 after a watchdog abort. Require actual Event69 status0 at **cfg80211 handler**, `scan_done aborted=0 fw_abort=0`, userspace result count, or other explicit normal outcome.
7. Each trial requires a brand-new unique one-shot marker (both on-device under `/run` and Surface persistent private receipts), explicit chosen experiment and scope; spent V14–V19 attempts never replayed. Per-trial independent firmware/NVRAM/driver SHA + no overlay/no candidate module cleanup; stop whole series on any failure. Save private console/receipt and privacy-safe checkpoint, update master handoff, and sync WSL checkout.
8. If one-shot fails preflight, verify whether marker was set BEFORE assuming it has been consumed. Never retry an unknown partially executed trial blindly. Do NOT convert safety-blocked remote tool calls into alternate bypasses; choose user-approved manual one-shot when required.

## 9. V20 source-audit and proof plan, precise conditional engineering

**Read before coding:** current Linux7 `drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c` / `fweh.h`, `core.h`, `cfg80211.c`. In current `struct brcmf_event_msg_be`, fields are packed `version, flags, event_type, status, reason, auth_type, datalen, addr, ifname, ifidx, bsscfgidx`. `brcmf_fweh_process_event` validates subscription/length and queues event. `brcmf_fweh_event_worker` maps raw `event->emsg.bsscfgidx` into `drvr->iflist[...]`, checks `BRCMF_MAX_IFS=16`, calls `brcmf_fweh_call_event_handler`; if `ifp=NULL` the handler returns -EINVAL without invoking cfg80211. We HAVE proof this occurred for terminal status0 in V19.

**Suggested V20 stages:**

1. **Source review only:** locate original Broadcom firmware-era `wl_event_msg_v1_t` vs `wl_event_msg_t` version2 struct, packet lengths and attached buffers; compare with modern packed `brcmf_event_msg_be`. Reference historical `https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/proto/bcmevent.h`. Assess whether V1 truly lacks both trailing indices and how 12-byte terminal payload and `pktlen=86` map to framing. Do not infer event header version from garbage `140` alone.
2. **Instrument packet version** numeric, ifidx and bsscfgidx at ingress/worker, overall `packet_len`, `datalen`, accepted bytes, plus preexisting interface existence; no device IDs. Ensure logger does not read an optional field beyond `packet_len` for an older header. Check `event->emsg.version` before reading optional indices. Keep log privacy and no new scan parameters.
3. Add **default-OFF `mz600_legacy_escan_if_fallback` module parameter**, validated 0/1, separate from `mz600_extra_events` (still accepts 0..127; use mask0). Implement fallback ONLY for Broadcom BCM4329 firmware ESCAN event69, when the event cannot resolve valid interface, and when exactly ONE primary WLAN0 interface is present and no secondary interfaces/P2P. Prefer matching event version1 if physically proven; never override a valid resolved bsscfg; no fallback on other firmware events or generic devices; do not invent event status0.
4. **One compiled module**, repeat controlled off/on in alternating order with unique markers and realistic repeat counts; inspect both actual normal cfg80211 completion and bad bsscfg drops, and whether fallback also recovers all valid partial BSS metadata. If evidence remains mixed, continue event-header inspection; do not prematurely turn fallback on by default.
5. Once proven, write **clean upstream candidate**: minimum version-specific event-header interface resolution plus safe bounds; remove temporary printks, extra mask machinery, forced passive dwell and project-only test scaffolding from production changes. Keep mainline generic firmware, MZ600 and additional Xoom variants unaffected. Do not silently hide genuinely malformed or multi-interface events.
6. Regression and quality gates: 2.4GHz same 2012 firmware, 5GHz multi-channel where legally allowed, installed generic 4.220 FW, different MZ600, MZ604 and MZ602 (board-specific), BT coexistence and cold/warm boot, suspend/resume/timeout/cancellation, KUnit or equivalent parser/event compatibility tests, no log spam, correct upstream coding/patch split.

**Why not change 10-second watchdog?** In V18, firmware terminal SUCCESS arrived at ingress roughly 9.5–9.8 seconds BEFORE watchdog, so a longer watchdog cannot fix a misrouted interface callback. **Why not subscribe Event26?** All measured 2012 terminal reports are Event69, and additional masks sometimes timed out; Event26/45 is not the missing completion mechanism in these test runs. **Why not assume hidden networks?** V17 completed with hidden BSS reports.

## 10. Older V0–V13 Linux7 work — still important; not the current blocker

- Early V0–V06: booted upstream Linux7 on Xoom with framebuffer and touchscreen grid/crosshair (fast motion lag noncritical), Android fallback. BCM4329 SDIO/card-detect/power firmware recovery pursued, OEM kernel board-init references gathered. Android firmware on primary devices and recovery toolkit retained as references.
- V063: native USB gadget root console, HCI BT load/up/down, ordered BCM Wi-Fi module activation and unload, Linux ramboot tests. No full Wi-Fi BT coex yet. Wi-Fi firmware and NVRAM private.
- V064: classic BigPart p7 boot/p8 root and permanent Debian 12.15; installed 114 matched kernel modules; repaired D-Bus/systemd; USB console COM9 operational. Corrected internal root device selector after GPT PARTUUID variability. Generic Linux firmware 2.4GHz `iw` scan displayed 19 BSS.
- Legacy HRI39 FW `4.218.248.20`: `WLC_SCAN` ioctl50 + `WLC_GET_SCAN_RESULTS` ioctl51; older **BSS format version108** (vs new 2012 ESCAN BSS109). Original OEM per-country/regrev calibration and controller cap showed 5GHz support, but modern ESCAN behavior diverged. One approach is generic dual-band 2012 ESCAN V1; another older-fw legacy WLC_SCAN/v108 parser. Preserve both lines until compatibility gates close.
- v7 command failure was host **iw option ordering** only: wrong `scan passive freq 5180` fixed to `scan freq 5180 passive`. V7R got 3 framed old-fw BSS. v8 parser work, v9 Event26 observer and result extraction, v10 passive dwell300 and 3 validated channel36 IE-safe v108 BSS, v11 physically reported 4 v108 BSS via proper cfg80211 and user iw; but lifecycle still used timeout.
- v12a Event26 firmware event mask readback proved bit26 enabled but no normal callback. v12b–v13 packet path and alternative-fw research continued (read their dated checkpoint for exact status; do not invent unverified passes). At V14 focus shifted to **private 2012 May25 4.218.248.44** whose ESCAN V1 provides native BSS109 in both bands, avoiding a permanent v108 translation just to get scan data. V15 proved real 2G completion; V17 proved real 5G completion; V19 now localized lost event.

## 11. Stock Android OEM reference Wi-Fi scan experiment and its correction

The spare stock Wi-Fi Xoom `wingray/MZ604` was connected to Surface by USB; Windows originally saw its MTP but not ADB because the old 2013 Motorola ADB interface driver was active. With owner permission, changed **only** MI_01 to Microsoft signed WinUSB, kept driver rollback. Android 4.1.2 logcat captured 2,936 lines; caches changed 31→34 BSS, 5GHz 15→18, one ch36 at 5180MHz; Android system scan counter 3→14. The owner deliberately toggled Wi-Fi OFF/ON mid-observation, which explains the supplicant stop/restart; it is NOT evidence of spontaneous OEM instability. No raw low-level OEM scan terminal timing was captured, and list security details can fill across multiple UI/network refreshes. This does not justify lengthening the Linux watchdog.

## 12. Read order / documents: which are authoritative?

1. **THIS new canonical handoff** (V19→V20) for the exact next action, model-specific issue and guarded workflow.
2. **V19 proven physical checkpoint:** `docs/checkpoints/MZ600_V19_EVENT69_WORKER_PRIMARY_IF_LOOKUP_FAIL_PHYSICAL_2026-10-27.md`. Most specific failure evidence; confirmed valid packet queued and misrouted; legacy v1 hypothesis unproven.
3. **V18 ten-mask checkpoint:** `docs/checkpoints/MZ600_V18_PARAMETRIC_MASK_TEN_SCANS_FIRMWARE_TERMINAL_AT_INGRESS_NOT_HANDLER_2026-10-27.md`. Numeric ingress/handler matrix and privacy-safe receipts; prevents misreading the early A/B mask correlation.
4. **V17 first real 5G success:** `docs/checkpoints/MZ600_V17_2012_5G_CH36_WIDE_EVENT_MONITOR_REAL_ESCAN_TERMINAL_SUCCESS_661MS_PHYSICAL_PASS_2026-10-27.md`.
5. V14–V16 separate checkpoints for control-plane firmware 2012 switch, explicit dwell, 2.4 vs 5GHz channel tests; then `docs/research/MZ600_V17_HIDDEN_SSID_BSS_METADATA_VS_5GHZ_ESCAN_TERMINAL_COMPLETION_2026-10-27.md` and OEM MZ604 corrected observation checkpoint.
6. **Previous v11 stopping handoff** `docs/handoffs/MZ600_XOOMLINUX7_V11_CURRENT_STOPPING_POINT_2026-10-26.md` (~51KB) contains many chronological appended updates and exact hashes; its **newest top prefixes supersede stale v11-only bottom**. Current V19 is newer.
7. **Full historical BigPart/physical transition** `docs/handoffs/MZ600_LINUX7_FULL_TRANSITION_HANDOFF_2026-10-26.md` (~85KB) — thorough hardware, partitions, exact rescue and module-history. Its opening historical `NOT_RUN` flags are explicitly superseded by later physical checkpoints.
8. `docs/plans/MZ600_BCM4329_LINUX7_MULTIDEVICE_PATCH_SERIES_RELEASE_GATES_2026-10-26.md` for engineering/upstream QA and second device gates; `docs/checkpoints/MZ600_OEM_2A65EDC_BLUETOOTH_WLAN_SHARED_U4_51CHECK_SOURCE_AUDIT_2026-10-26.md` for whole-chip shared power/BT/SDIO quirks; `runtime/CURRENT_LINUX7_STATE.env` for historical raw state journal but check dates: file contains many superseded `LATEST_` entries.
9. GitHub repo README, exact current kernel source, build scripts and `tools/check_repository.py` are source of truth for code. Never infer from an old handoff that something is currently staged or needs user to rerun.

**Potential documentation pitfall:** older V11/v12 HRI39 firmware had v108 and a timeout-driven scan result; newer V14–V19 2012 firmware uses ESCAN V1 Event69 and v109. These are separate tracks and not interchangeable. Likewise an earlier kernel scan after V17 'success' cannot be assumed reliable—V18 reproduced both outcomes and V19 explained a host event-routing failure.

## 13. Next-chat opening execution checklist (no questions owner already answered)

- Confirm user continues at this V19 physical milestone and wants V20 source-led fix; **do not repeat** V19, old A/B masks or previous OEM Android capture.
- Read GitHub V19/V18/V17 checkpoints and this handoff before editing. Confirm fresh GitHub branch SHA, WSL checkout clean, module/source baseline intact; physically test only if user continues authorization and the device is reachable/idle.
- Inspect original Broadcom v1/v2 event message struct sizes, exact `fweh.c` version dispatch, and `core.h` primary/secondary interface conditions. Design data-driven version-conditional path, preserving multi-if correctness.
- Write V20 isolated source-restoring builder+read-only telemetry and **parameterized narrow fallback default OFF**. Compile exact ABI once, verify SHA/vermagic, source restored. Build a new guarded Xoom one-shot and Surface suite with fresh markers, no old script reuse.
- Preflight COM9 root/kernel/fw/NVRAM/modules, HCI/WPA status, overlays and safe passive NO_IR. Stage in `/run` SHA only. Test fallback 0 and 1 with isolated numeric reports and independent poststate per trial; do not invent results before execution.
- Evaluate: is event version1 actually emitted? Is it the source of bsscfg=1/140? Does fallback pass **only** when one primary IF and deliver Event69 status0 to cfg80211 and real user BSS? Do original generic firmware/other devices remain unaffected? If no, revert hypothesis and inspect broader interface-map/firmware frame field alignment.
- Only after physical proof: create minimal production patch, codify tests, update dated checkpoint, this canonical handoff, runtime state and GitHub commit(s); sync Desktop and report exactly what ran.

## 14. Verbatim high-priority instruction for the receiving assistant

> The firmware is not failing to finish the 5GHz scan. We physically observed timely Event69 SUCCESS arriving on all ten V18 tests. V19 proved it passed validation/queue and reached the worker, but on failures `bsscfgidx=1` maps to a missing interface (`ifp=NULL`, `-EINVAL`) and several partial events carry raw index140. The leading hypothesis is legacy Broadcom event header version/ifidx/bsscfg parsing incompatibility; **version unmeasured**. Work from this point, not stale V11 status. Preserve firmware, NVRAM, factory MAC, Linux BigPart p7/p8, working BT and generic 2G. Next perform version-aware, BCM4329-only event-header analysis and default-off one-primary-IF Event69 mapping experiment with identical module A/B; never globally redirect every event or merely extend timeout. One logical minimal patch, fully reversible tests, dated checkpoints and ongoing master handoff updates.

---
End of handoff. All physical result claims above are grounded in existing per-version committed checkpoints, independent private Surface receipts, and checked Desktop builds. No V20 hardware test has been performed as of this document.
