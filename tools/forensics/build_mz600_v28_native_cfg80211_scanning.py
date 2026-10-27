#!/usr/bin/env python3
"""V28 lab build: remove debug-only scan/RF restrictions, keep real completion fix.

Inherit exact-ABI source restoring V26b build, replacing only temporary
scan constraints and static passive-only channel marking. Preserve the
firmware-derived valid-channel bitmap, original hardware channel disables,
DFS/radar flagging, normal cfg80211 regulatory policy, live transaction ID
and real Event69 completion. Never write firmware, NVRAM, permanent modules.

The legacy firmware reports channels through WLC_GET_VALID_CHANNELS when
'chanspecs' is unavailable. That path cannot independently attest HT40/VHT
capability: keep *bandwidth capability* conservatively HT20 until separately
verified; this is NOT a NO_IR or passive-scan restriction.
"""
import importlib.util
import json
import re
from pathlib import Path

PREV = Path(__file__).with_name("build_mz600_v26_transitional_passive_scan.py")
spec = importlib.util.spec_from_file_location("mz600_v26b", PREV)
v26 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v26)
base = v26.base
base.RESULT = base.ROOT / "v064-2012-oem-escan-v28-20261027"
v26.v25.WCC_COPY = base.RESULT / "brcmfmac-wcc-matched-v25.ko"
old_scan = base.instrument
old_event = base.instrument_fweh

def replace_one_pattern(src, pattern, replacement, name):
    out, count = re.subn(pattern, replacement, src, count=0, flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise RuntimeError(f"STOP: expected 1 {name} block, got {count}")
    return out

def instrument_scan(original):
    c = old_scan(original)
    # Remove the *entire* diagnostic lab gate and the global passive mode
    # firmware command. No limits on channel count/frequency/SSIDs/IEs.
    c = replace_one_pattern(
        c,
        r"\t/\* V20 controlled single-channel NO_IR PASSIVE diagnostic\. \*/\n"
        r"(?:(?!\tif \(test_bit\(BRCMF_SCAN_STATUS_BUSY).)*"
        r"(?=\tif \(test_bit\(BRCMF_SCAN_STATUS_BUSY)",
        "",
        "V20 diagnostic scan gate/global passive override",
    )

    # Delete V20 500ms passive dwell override, leaving Linux's ordinary
    # request-dependent scan_type/active/passive dwell parameters.
    c = replace_one_pattern(
        c,
        r"\tif \(cfg->pub->bus_if->chip == BRCM_CC_4329_CHIP_ID &&\n"
        r"\t    n_channels == 1 && n_ssids == 0 &&\n"
        r"\t    request->channels\[0\]->center_freq == 5180\) \{\n"
        r"(?:(?!\t\}).)*\t\}\n"
        r"(?=\tparams_le->length = cpu_to_le16\(length\);)",
        "",
        "forced 500ms single-channel passive dwell",
    )

    # Do not advertise every legacy channel as NO_IR regardless of its
    # actual per-channel regulatory state. The native core and cfg80211
    # continue to own NO_IR, disabled and radar enforcement.
    old_flags = (
        "\t\t\t\tchannel->flags = channel->orig_flags |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_IR |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_HT40 |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_80MHZ |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_160MHZ;"
    )
    new_flags = (
        "\t\t\t\t/* Only bandwidth support is unknown in the legacy\n"
        "\t\t\t\t * valid-channel list. Do NOT force NO_IR.\n"
        "\t\t\t\t * cfg80211 retains country/regdb regulatory limits.\n"
        "\t\t\t\t */\n"
        "\t\t\t\tchannel->flags = channel->orig_flags |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_HT40 |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_80MHZ |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_160MHZ;"
    )
    c = base.replace_once(c, old_flags, new_flags)

    # Honest version label for fallback; do not claim passive-only.
    c = base.replace_once(
        c,
        'MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK chip=4329 fw2g=%u fw5g=%u no_ir=1 ht20_only=1',
        'MZ600_V28_LEGACY_VALID_CHANNEL_FALLBACK chip=4329 fw2g=%u fw5g=%u ht20_only=1',
    )

    # Remove stale "ch36" logging which would be incorrect for normal scans.
    # Channel-list inspection remains bounded and read-only when populated.
    c = c.replace("MZ600_V26_", "MZ600_V28_")
    return c

def instrument_event(original):
    return old_event(original).replace("MZ600_V26_", "MZ600_V28_")

base.instrument = instrument_scan
base.instrument_fweh = instrument_event

def main():
    v26.main()  # preserves all original sources/module and checks WCC pairing
    output = base.RESULT
    core_old = output / "brcmfmac-2012-escan-regstate-v26.ko"
    core_new = output / "brcmfmac-2012-escan-native-scan-v28.ko"
    wcc_old = output / "brcmfmac-wcc-matched-v26.ko"
    wcc_new = output / "brcmfmac-wcc-matched-v28.ko"
    if core_new.exists() or wcc_new.exists():
        raise RuntimeError("STOP: V28 artifacts already present")
    core_old.rename(core_new)
    wcc_old.rename(wcc_new)
    receipt = output / "offline-build-result.json"
    d = json.loads(receipt.read_text())
    d.update({
        "test": "V28_NATIVE_CFG80211_SCAN_POLICY_INSTEAD_OF_LAB_ONLY_GATES",
        "artifact_name": core_new.name,
        "module_name": core_new.name,
        "matched_wcc_name": wcc_new.name,
        "module_sha256":base.sha(core_new.read_bytes()),
        "module_bytes":len(core_new.read_bytes()),
        "matched_wcc_sha256":base.sha(wcc_new.read_bytes()),
        "matched_wcc_bytes":len(wcc_new.read_bytes()),
        "hardcoded_channel_36_gate":False,
        "hardcoded_no_ssid_or_ie_gate":False,
        "global_passive_scan_override":False,
        "forced_passive_dwell_500ms":False,
        "legacy_supported_channel_no_ir_override":False,
        "firmware_capability_ht20_conservative":True,
        "regulatory_or_firmware_writes":False,
        "on_device_test":"NOT_YET_RUN",
        "upstream_patch":False,
    })
    receipt.write_text(json.dumps(d,indent=2)+"\n")
    print("V28_OFFLINE_EXACT_ABI_PAIR_BUILD_PASS",d["module_sha256"],d["matched_wcc_sha256"])

if __name__ == "__main__":
    main()
