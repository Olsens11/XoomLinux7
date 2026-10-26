#!/usr/bin/env python3
"""Lab v10: change only passive single-channel dwell 80ms -> 300ms.

Preserve prior v9 BCM4329/3 HRI39 validated v108 scan-result parser and
event26 observation-only callback. No other driver logic or ABI changes.
One-variable physical comparison, NOT upstream-ready, no radio at build time.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name(
    "build-v064-bcm4329-legacy-scancomplete-event-probe-20261026.py"
)
spec = importlib.util.spec_from_file_location("mz600_v9_base", P)
v9 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v9)

builder = v9.builder
builder.WORK = builder.BASE / "v064-legacy-passive-dwell300-v10-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-bss108-event26-dwell300-v10.ko"
builder.PATCH_PATH = builder.WORK / "0010-lab-only-bcm4329-passive-dwell80-to-300.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
previous = builder.make_patch


def patch(original):
    c = previous(original)
    return builder.exactly_one(
        c,
        "\tparams->passive_time = cpu_to_le32(80);\n",
        "\tparams->passive_time = cpu_to_le32(300);\n",
        "ONLY_PASSIVE_DWELL_80_TO_300",
    )


builder.make_patch = patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        raw = builder.TARGET.read_bytes()
        if not all(tag in raw for tag in (
            b"MZ600_LEGACY_SCAN_LAB_COMMAND50_RC",
            b"MZ600_LEGACY_BSS108_VALIDATION",
            b"MZ600_LEGACY_SCAN_EVENT26",
        )):
            raise SystemExit("Missing proven v9 diagnostic markers")
        diff = builder.PATCH_PATH.read_text()
        if diff.count("params->passive_time = cpu_to_le32(300);") != 1:
            raise SystemExit("Exactly one dwell time expected")
        if "params->passive_time = cpu_to_le32(80);" in diff:
            raise SystemExit("Unexpected old dwell in final lab patch")
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "EXACT_ABI_V10_PASSIVE_DWELL_300_BUILT_RESTORED"
        report["single_variable_changed_vs_v9"] = "passive_time_ms: 80 -> 300"
        report["scan_frequency_mhz"] = 5180
        report["radio_started_during_build"] = False
        report["physical_scan_performed"] = False
        report["actual_v108_bss_records_decoded"] = False
        report["firmware_event26_physical_evidence"] = False
        report["upstream_ready"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("OFFLINE_V10_SINGLE_VARIABLE_DWELL300_EXACT_ABI_PASS", flush=True)
    raise SystemExit(rc)
