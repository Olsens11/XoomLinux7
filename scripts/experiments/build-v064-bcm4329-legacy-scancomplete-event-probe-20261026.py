#!/usr/bin/env python3
"""Exact ABI v9 diagnostic: observe legacy BCM4329 SCAN_COMPLETE event #26.

Layer v8 full BSS108 field/IE-safe count-only decoder atop physical v7
single-channel passive scan. Add ONE scoped firmware event observer:
only log numeric status/length when an owned legacy scan is in progress.
Do not call cfg80211_scan_done, cancel timers or change data path here.
Modern ESCAN_RESULT handler remains unchanged. No device execution.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name(
    "build-v064-bcm4329-legacy-bss108-validated-probe-20261026.py"
)
spec = importlib.util.spec_from_file_location("mz600_legacy_v8_builder", P)
v8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v8)
builder = v8.builder
builder.WORK = builder.BASE / "v064-legacy-scancomplete-event-v9-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-v108-event26-observer-v9.ko"
builder.PATCH_PATH = builder.WORK / "0009-lab-only-bcm4329-observe-legacy-scancomplete-event26.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
previous = builder.make_patch


def patch(original):
    code = previous(original)
    anchor = (
        "static void brcmf_init_escan(struct brcmf_cfg80211_info *cfg)\n"
        "{\n"
        "\tbrcmf_fweh_register(cfg->pub, BRCMF_E_ESCAN_RESULT,\n"
    )
    insertion = (
        "/* Legacy scan firmware event 26 observer only. The current\n"
        " * v7/v8 lab path continues to use existing timeout completion.\n"
        " * Neither modern escan behavior nor cfg80211 state is changed. */\n"
        "static s32\n"
        "brcmf_legacy_scan_complete_probe(struct brcmf_if *ifp,\n"
        "\t\t\t const struct brcmf_event_msg *event, void *data)\n"
        "{\n"
        "\tstruct brcmf_cfg80211_info *cfg = ifp->drvr->config;\n"
        "\n"
        "\tif (!cfg || !cfg->scan_request ||\n"
        "\t    cfg->escan_info.run != brcmf_run_legacy_passive_probe)\n"
        "\t\treturn 0;\n"
        "\tbrcmf_info(\"MZ600_LEGACY_SCAN_EVENT26 observed=1 status=%u data_bytes=%u owner=1\\n\",\n"
        "\t\t   event->status, event->datalen);\n"
        "\treturn 0;\n"
        "}\n"
        "\n"
        "static void brcmf_init_escan(struct brcmf_cfg80211_info *cfg)\n"
        "{\n"
        "\tbrcmf_fweh_register(cfg->pub, BRCMF_E_SCAN_COMPLETE,\n"
        "\t\t\t    brcmf_legacy_scan_complete_probe);\n"
        "\tbrcmf_fweh_register(cfg->pub, BRCMF_E_ESCAN_RESULT,\n"
    )
    code = builder.exactly_one(
        code, anchor, insertion, "LEGACY_SCAN_EVENT26_OBSERVER_ONLY"
    )
    return code


builder.make_patch = patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        raw = builder.TARGET.read_bytes()
        assert b"MZ600_LEGACY_SCAN_EVENT26" in raw
        p = builder.PATCH_PATH.read_text()
        for must in (
            "BRCMF_E_SCAN_COMPLETE",
            "brcmf_legacy_scan_complete_probe",
            "MZ600_LEGACY_SCAN_EVENT26",
            "cfg->escan_info.run != brcmf_run_legacy_passive_probe",
            "MZ600_LEGACY_BSS108_VALIDATION",
        ):
            if must not in p:
                raise SystemExit("Missing event observer guard: " + must)
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "LAB_BSS108_VALIDATOR_PLUS_EVENT26_OBSERVER_ABI_BUILT"
        report["event26_modifies_scan_completion"] = False
        report["event26_logs_identities"] = False
        report["modern_escan_changed"] = False
        report["physical_test_run"] = False
        report["upstream_ready"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2)+"\n")
        print("OFFLINE_V9_EVENT26_OBSERVATION_ONLY_ABI_PASS", flush=True)
    raise SystemExit(rc)
