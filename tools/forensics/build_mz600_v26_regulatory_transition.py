#!/usr/bin/env python3
"""V26 LAB: accept cfg80211's ordinary NO_IR beacon-hint transition.

Derives exact-ABI, source-restoring V25 diagnostic, with matched WCC.
Only eliminates the historical lab-only requirement that channel 36
*retain* IEEE80211_CHAN_NO_IR between scans. Does not clear flags, touch
regulatory policy, permit active probing, or modify firmware/flash.
"""
import importlib.util
import json
from pathlib import Path

PREV = Path(__file__).with_name("build_mz600_v25_scan_gate_diagnostic.py")
spec = importlib.util.spec_from_file_location("mz600_v25_builder", PREV)
v25 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v25)

base = v25.base
base.RESULT = base.ROOT / "v064-2012-oem-escan-v26-20261027"
prior_scan = base.instrument
prior_fweh = base.instrument_fweh

def instrument_scan(original):
    c = prior_scan(original)
    lines = c.splitlines(keepends=True)
    check = [i for i, line in enumerate(lines)
             if "!(ch->flags & IEEE80211_CHAN_NO_IR) ||" in line]
    if len(check) != 1:
        raise RuntimeError("STOP: expected exactly one historical NO_IR check")
    del lines[check[0]]
    c = "".join(lines)

    # Do not print the obsolete claim NO_IR=1 after a beacon hint.
    log_lines = [line for line in c.splitlines(keepends=True)
                 if "SCAN_GATE_PASS channel=36 freq=5180 no_ir=1 nssid=0" in line]
    if len(log_lines) != 1:
        raise RuntimeError("STOP: changed success log anchor")
    log = log_lines[0]
    new_log = log.replace("no_ir=1 nssid=0", "no_ir=%u nssid=0")
    new_log = new_log.replace('\\\\n");',
                              '\\\\n", !!(ch->flags & IEEE80211_CHAN_NO_IR));')
    if new_log == log or new_log.count("!!(ch->flags") != 1:
        raise RuntimeError("STOP: unexpected C logging format")
    c = c.replace(log, new_log, 1)

    # Other validations are TEMPORARY TEST RESTRICTIONS, not regulatory law:
    # single channel 36, no SSID/probe IEs, disabled/radar still rejected.
    # The true ESCAN request is still passive with finite 500ms dwell.
    c = c.replace("MZ600_V25_", "MZ600_V26_")
    return c

def instrument_fweh(original):
    return prior_fweh(original).replace("MZ600_V25_", "MZ600_V26_")

base.instrument = instrument_scan
base.instrument_fweh = instrument_fweh

def main():
    v25.main()   # Source restoration, exact ABI, WCC save/restore checks
    out = base.RESULT
    old_core = out / "brcmfmac-2012-escan-gate-v25.ko"
    new_core = out / "brcmfmac-2012-escan-regtransition-v26.ko"
    old_wcc = out / "brcmfmac-wcc-matched-v25.ko"
    new_wcc = out / "brcmfmac-wcc-matched-v26.ko"
    if new_core.exists() or new_wcc.exists():
        raise RuntimeError("STOP: V26 output collision")
    old_core.rename(new_core)
    old_wcc.rename(new_wcc)
    report = out / "offline-build-result.json"
    data = json.loads(report.read_text())
    data.update({
        "test": "V26_TWO_SCANS_ACCEPT_NORMAL_NO_IR_TRANSITION",
        "artifact_name": new_core.name,
        "module_name": new_core.name,
        "matched_wcc_name": new_wcc.name,
        "no_ir_requirement_removed": True,
        "regulatory_flags_modified": False,
        "active_scan_enabled": False,
        "normal_network_join_test": "FUTURE_STEP",
        "physical_test": "NOT_RUN",
        "upstream_patch": False,
    })
    report.write_text(json.dumps(data, indent=2) + "\n")
    print("V26_OFFLINE_EXACT_ABI_PASS", new_core, new_wcc)

if __name__ == "__main__":
    main()
