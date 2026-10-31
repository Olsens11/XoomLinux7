# MZ604 W1 — physical trace isolates legacy firmware channel-enumeration failure
**As-of 2026-10-31 04:41–04:55 EDT. PHYSICAL diagnostic PASS; Wi-Fi interface and upstream patch NOT PASS.** Read all chronological project logs, prior OEM firmware checkpoint and comprehensive handoffs as time-scoped evidence. Do not publish raw trace, board NVRAM, firmware, unique MAC or serial.

## Baseline / scope
- Dedicated MZ604 Wingray Linux 7.0.0-next-20260422+ Debian Bookworm, Surface COM10 xoom autologin, noninteractive sudo UID0 PHYSICAL PASS.
- OEM MZ604 station firmware v4.218.248.42 and original board NVRAM privately installed, original source commit 2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3. No scan, country SET, connection, active transmission or reboot in this test.
- p1/EBB/BCT/GPT/bootloader, p6 TWRP, p7 boot, p8 startup and p10 original root rollback untouched. TWRP software reboot-to-system previously powered off/red LED; physical boot works. I1 remains OPEN.

## One-option trace-only module, built and verified
- Separate configuration derived from exact kernel config, only change CONFIG_BRCM_TRACING=y; other flags unchanged. Modules_prepare, brcmfmac ARM compile and modpost PASS. Trace module 436344 bytes SHA256 9790298efc1f12617d42e90a0c5b71a9fc2175acf7f6830fc43a1c95c418d7a4; original core module 341676 bytes SHA256 9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb. Exact vermagic match: 7.0.0-next-20260422+ SMP mod_unload modversions ARMv7 p2v8. This is NOT an upstream patch.
- The kbuild M= command wrote ignored generated objects into the source subtree despite a separate O= directory; tracked Git status was clean, but ignored intermediate files remain intentionally. Do not use destructive git clean. Copies of final modules independently SHA verified on Desktop, Surface and guest COM10 private stage.
- First attempt to remove core directly stopped safely: WCC vendor module held brcmfmac in use, so nothing was traced/changed. Explicit unloading of brcmfmac-wcc succeeded and automatically unloaded the core, leaving brcmutil.
- Second controlled trial: trace events temporarily enabled; matching diagnostic core insmod RC0, private kernel trace and dmesg captured, trace events disabled, WCC/core diagnostic removed; unchanged original module loaded again. All host ACK steps RC0. Private evidence: Surface inspection/MZ604-W1-TRACED-MODULE-REPROBE-20261031T045234.txt.

## Exact causal failure chain in live dmesg
    brcmf_c_preinit_dcmds: Firmware: BCM4329/3 wl0: ... version 4.218.248.42
    brcmf_c_set_joinpref_default: Set join_pref error (-52) [nonfatal in this run]
    brcmf_construct_chaninfo: get chanspecs error (-52)
    brcmf_setup_wiphybands: brcmf_construct_chaninfo failed (-52)
    brcmf_cfg80211_attach: Setting wiphy bands failed (-52)
    brcmf_bus_started: failed: -12
    brcmf_attach: dongle is not responding: err=-12
    brcmf_sdio_firmware_callback: brcmf_attach failed

Pinned source cfg80211.c:7018–7023 issues chanspecs iovar and propagates error. cfg80211 attach returns NULL; core maps that NULL to generic -ENOMEM (-12). Thus this is NOT proof of RAM exhaustion. This is actual MZ604 hardware evidence that missing modern chanspecs inventory prevents wiphy-band construction and wlan0. Physical Linux -52 is normalized -EBADE; fwil.c maps more than one native vendor error to that status. The exact native BCME code on MZ604 remains UNKNOWN.

## Restoration and remaining evidence gates
- Read-only post-test live verification: COM10 still available; WCC/core restored and loaded; /sys/kernel/tracing/events/enable=0 and /sys/module/brcmfmac/parameters/debug=0; original on-disk SHA exactly 9fec47bc...; still no wlan0. No reboot or RF activity.
- MZ600 historical OEM 4.218.248.44 used WLC_GET_VALID_CHANNELS successfully (35 total, 11 2.4GHz); this is a DIFFERENT device/firmware, not MZ604 proof. MZ604 native chanspecs error and BRCMF_C_GET_VALID_CHANNELS ioctl 217 results are NOT YET measured.
- Read historical WIFI-01 #4 r7 source-only patch and caveats, OEM/legacy-channel and regulatory contracts: keep modern query unchanged when supported; only fallback when exact native firmware capability is verified, bounded count/channel list, preserving cfg80211/hardware/firmware/regulatory intersections. Do not copy permissive OEM regdomain, invent radar/passive flags, turn 5GHz TX on or freeze country-current channel list into immutable orig_flags.
- Next measurement: read-only native firmware status and bounded WLC_GET_VALID_CHANNELS on EXACT MZ604 4.218.248.42, via isolated lab module, no scan or channel/country SET. See next test plan and new full handoff.
