#!/usr/bin/env python3
"""Lab-only: inspect old BCM4329 SCAN_RESULTS header WITHOUT starting a scan.

Layer the source-validated v05 5GHz NO_IR channel fallback and exactly one
BRCMF_C_SCAN_RESULTS(51) read-only query on HRI39 firmware initialization.
Print return code and length/version/count ONLY; never SSIDs/BSSIDs or payload,
never WLC_SCAN / escan, never change flags, regulatory country or transmit.
Restores original kernel source/module files as in the pinned prior builder.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name("build-v064-bcm4329-legacy-passive-only-wiphy-20261026.py")
spec = importlib.util.spec_from_file_location("mz600_passive_v05", P)
v05 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v05)

builder = v05.builder
builder.WORK = builder.BASE / "v064-readonly-legacy-results-header-v6-20261026"
builder.TARGET = builder.WORK / "brcmfmac-readonly-legacy-results-header.ko"
builder.PATCH_PATH = builder.WORK / "0006-brcmfmac-readonly-legacy-results-header-in-noir-lab.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
old_patch = builder.make_patch


def patch(original):
    data = old_patch(original)
    anchor = (
        "\t\t\tbrcmf_info(\"MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK chip=4329 fw2g=%u fw5g=%u no_ir=1 ht20_only=1\\n\",\n"
        "\t\t\t\t   count_2g, count_5g);\n"
        "\t\t\terr = 0;\n"
    )
    replacement = (
        "\t\t\tbrcmf_info(\"MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK chip=4329 fw2g=%u fw5g=%u no_ir=1 ht20_only=1\\n\",\n"
        "\t\t\t\t   count_2g, count_5g);\n"
        "\t\t\t/* Diagnostic GET only: old scan-results header size and\n"
        "\t\t\t * format version, with no scan started. Reuse pbuf;\n"
        "\t\t\t * no BSS payload parsing or user-identity output. */\n"
        "\t\t\tmemset(pbuf, 0, BRCMF_DCMD_MEDLEN);\n"
        "\t\t\t((struct brcmf_scan_results *)pbuf)->buflen =\n"
        "\t\t\t\tcpu_to_le32(BRCMF_DCMD_MEDLEN);\n"
        "\t\t\tlegacy_rc = brcmf_fil_cmd_data_get(ifp,\n"
        "\t\t\t\t\t      BRCMF_C_SCAN_RESULTS,\n"
        "\t\t\t\t\t      pbuf, BRCMF_DCMD_MEDLEN);\n"
        "\t\t\tif (legacy_rc) {\n"
        "\t\t\t\tbrcmf_info(\"MZ600_5G_DIAG_SCAN_RESULTS_HEADER rc=%d\\n\",\n"
        "\t\t\t\t\t   legacy_rc);\n"
        "\t\t\t} else {\n"
        "\t\t\t\tstruct brcmf_scan_results *res = (void *)pbuf;\n"
        "\t\t\t\tbrcmf_info(\"MZ600_5G_DIAG_SCAN_RESULTS_HEADER rc=0 buflen=%u version=%u count=%u\\n\",\n"
        "\t\t\t\t\t   res->buflen, res->version, res->count);\n"
        "\t\t\t}\n"
        "\t\t\terr = 0;\n"
    )
    return builder.exactly_one(data, anchor, replacement, "SCAN_RESULTS_HEADER_READ_ONLY")


builder.make_patch = patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        raw = builder.TARGET.read_bytes()
        if b"MZ600_5G_DIAG_SCAN_RESULTS_HEADER" not in raw:
            raise SystemExit("missing header marker")
        patch_text = builder.PATCH_PATH.read_text()
        assert "BRCMF_C_SCAN_RESULTS" in patch_text
        assert "BRCMF_C_SCAN," not in patch_text
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "EXACT_ABI_NO_SCAN_READ_ONLY_LEGACY_RESULTS_HEADER_BUILT"
        report["scan_request_started"] = False
        report["scan_results_bss_data_read_or_logged"] = False
        report["kernel_or_firmware_installed"] = False
        report["physical_test_performed"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("READONLY_NO_SCAN_HEADER_DIAGNOSTIC_ELF_AND_BASELINE_PASS",flush=True)
    raise SystemExit(rc)
