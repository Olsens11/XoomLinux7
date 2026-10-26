# MZ600 BCM4329 — v9 actual empty scan and v10 one-variable 300 ms follow-up

**2026-10-26 15:16 EDT:** owner executed the original HRI39 firmware v9 lab test via manual Surface one-shot. Read actual private Surface COM9 transcript and JSON receipt, not a hypothetical result.

## v9 physical observations

- New v9 module **346440 B**, SHA256 `03c33805786caa6c22a6c51875d82e52861fa508808edf8cad8bdcba9f772146`, physically transferred into Xoom `/run`, uploader receipt says SHA verified, no persistent module/boot write.
- Motorola HRI39 firmware 4.218.248.20 and original US/69 NVRAM-minus-bootstrap-MAC booted via guarded temporary RAM bind mounts; native Linux 7 `7.0.0-next-20260422+`, `wlan0` phy15, channel36 5180MHz verified enabled NO_IR and non-DFS.
- Passive `iw dev wlan0 scan freq 5180 passive` **rc0**, firmware `WLC_SCAN` cmd50 **rc0**. Firmware `WLC_SCAN_RESULTS` cmd51 **rc0, buflen12, version108, count0, envelope_ok1**. `MZ600_LEGACY_BSS108_VALIDATION records=0 ctl36=0 other=0 invalid_ie=0 safe=1`. **This proves only correct parsing of an EMPTY results envelope**, not v108 populated BSS structures. Owner `MZ600_V9_BSS108_VALIDATION_RECORDS=1` counts diagnostic LOG ENTRIES, not BSS records. Prior v7R separate physical test had 1632B/version108/3 framed BSS, but not actual per-record IE/ctl_ch validation.
- Firmware event26 observer found **0 events**, after observed modern escan `timer expired` approximately 10s from scan start; legacy results still queried in timeout worker. This does NOT prove original firmware never emits completion nor that bounded polling cannot work.
- Ordered WCC→brcmfmac→brcmutil unload rc0, both OEM FW/cal temporary overlays unmounted rc0; guarded script exit0 and Surface wrapper JSON recorded `original_state_script_and_independently_verified=true`, `independent_audit_ok=true`, `run_completed=true`. Private transcript SHA256 `ea89583eb867b97890271205726e3b17c761076c8f025ca80ddf7969eaa27267`. An EXTRA assistant-initiated direct COM9 audit was safety-blocked, **not** accomplished; cite only the existing independent audit performed by owner's wrapper.
- No private SSIDs/BSSIDs or original proprietary firmware bytes published.

## Next: v10 only change one RF test parameter

80ms passive dwell is shorter than many beacon intervals near 100TU (~102.4ms); **hypothesis**, not verified explanation. Existing brcmfmac upstream scan parameters support a dedicated `passive_time` dwell field (see [Linux fwil_types.h](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil_types.h)). Do not mistake empty 80ms scan for a v108 parser failure.

[New exact-ABI v10 builder](../../scripts/experiments/build-v064-bcm4329-legacy-passive-dwell300-v10-20261026.py) composes identical v9 diagnostics and changes ONLY `params->passive_time = cpu_to_le32(80)` to **`cpu_to_le32(300)`**, in existing BCM4329-only, NO_IR channel36, passive-only scan. Existing `WLC_SCAN=50`, `WLC_SCAN_RESULTS=51` bounded response, 124B v108 record header/IE TLV validator, event26 observer and ~10s fallback remain identical. **Offline exact ARMv7 modversions ABI build PASS** with restored original source/.ko; v10 346440B module SHA256 **`d20da8542676df6aa226efe9868c8019b5ab840be6ef4787a9582a7a2e9cb911`**, generated source patch SHA **`a19f4be8c3081e4087f88ea20780139429f41de2ac4ca7fb1ca377ec58144db2`**. v10 not transferred or physically run at checkpoint creation. No kernel flash, installed module or generic firmware change.

A new owner one-shot must use a distinct attempt marker and privately recorded result/rollback; **do not repeat v9**. To claim physical version108 parser validated, require `records>0`, actual `safe=1`, per-record channel information and strict IE bounds. Event26 remains observation-only even if emitted; subsequent production integration needs correct cfg80211 ownership/timeout/cancel. Future proposed upstream series: one logical bisectable change per patch, KUnit and modern firmware regression, owner authorization; unrelated BT/pwrseq/SDIO fixes separate.

**State: v9 physical scan rc0 / BSS0 / event26 unseen / wrapper-restored baseline PASS; v10 offline built ONLY.**
