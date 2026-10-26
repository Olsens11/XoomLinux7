#!/usr/bin/env python3
"""Build the existing BCM4329 bandlist diagnosis + one READ-ONLY country iovar query.

Imports original exact-ABI builder, adds country read diagnostics, reuses its
fail-closed compile and exact original source/ELF restoration. Does not deploy.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name("build-v064-bcm4329-5ghz-bandlist-diagnostic-20261026.py")
spec = importlib.util.spec_from_file_location("mz600_bandlist_exact_builder", P)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

base.WORK = base.BASE / "v064-5ghz-country-iovar-diagnostic-v3-20261026"
base.TARGET = base.WORK / "brcmfmac-5ghz-country-iovar-diagnostic.ko"
base.PATCH_PATH = base.WORK / "0003-brcmfmac-count-only-bandlist-and-read-only-country-iovar.patch"
base.REPORT = base.WORK / "offline-build-result.json"

original_patch = base.make_patch

def country_read_only_patch(original):
    c = original_patch(original)
    c = base.exactly_one(
        c,
        "\t__le32 bandlist[3];\n\tu32 n_bands;\n\tint err, i;\n",
        "\t__le32 bandlist[3];\n\tu32 n_bands;\n\tint err, i;\n"
        "\tstruct brcmf_fil_country_le diag_country = {};\n"
        "\tint diag_country_rc;\n",
        "LOCAL_READONLY_COUNTRY_STRUCT")
    anchor = (
        "\tbrcmf_info(\"MZ600_5G_DIAG_WIPHY has2g=%u has5g=%u\\n\",\n"
        "\t\t   !!wiphy->bands[NL80211_BAND_2GHZ],\n"
        "\t\t   !!wiphy->bands[NL80211_BAND_5GHZ]);\n\n"
        "\treturn 0;\n"
        "}\n\n"
        "static s32 brcmf_config_dongle"
    )
    replacement = (
        "\tbrcmf_info(\"MZ600_5G_DIAG_WIPHY has2g=%u has5g=%u\\n\",\n"
        "\t\t   !!wiphy->bands[NL80211_BAND_2GHZ],\n"
        "\t\t   !!wiphy->bands[NL80211_BAND_5GHZ]);\n"
        "\t/* Read-only DHD country iovar after successful bandlist fetch. */\n"
        "\t/* Never SET country, force a PHY channel, or modify NVRAM here. */\n"
        "\tdiag_country_rc = brcmf_fil_iovar_data_get(ifp, \"country\",\n"
        "\t\t\t\t\t\t&diag_country, sizeof(diag_country));\n"
        "\tif (diag_country_rc) {\n"
        "\t\tbrcmf_info(\"MZ600_5G_DIAG_COUNTRY_READ rc=%d\\n\", diag_country_rc);\n"
        "\t} else {\n"
        "\t\t/* print two code bytes as hex; no board MAC or credentials */\n"
        "\t\tbrcmf_info(\"MZ600_5G_DIAG_COUNTRY_READ rc=0 abbrev=%02x%02x ccode=%02x%02x rev=%u\\n\",\n"
        "\t\t\t   (u8)diag_country.country_abbrev[0],\n"
        "\t\t\t   (u8)diag_country.country_abbrev[1],\n"
        "\t\t\t   (u8)diag_country.ccode[0],\n"
        "\t\t\t   (u8)diag_country.ccode[1],\n"
        "\t\t\t   le32_to_cpu(diag_country.rev));\n"
        "\t}\n\n"
        "\treturn 0;\n"
        "}\n\n"
        "static s32 brcmf_config_dongle"
    )
    c = base.exactly_one(c, anchor, replacement, "READ_ONLY_COUNTRY_IOVAR")
    return c

base.make_patch = country_read_only_patch

if __name__ == "__main__":
    result = base.main()
    if result == 0:
        data = base.TARGET.read_bytes()
        if b"MZ600_5G_DIAG_COUNTRY_READ" not in data:
            raise SystemExit("OFFLINE_FAIL missing read-only firmware country log marker")
        report = json.loads(base.REPORT.read_text())
        report["result"] = "EXACT_ABI_BANDLIST_AND_READONLY_FIRMWARE_COUNTRY_IOVAR_BUILT_AND_RESTORED"
        report["country_read_does_not_call_iovar_set"] = True
        report["country_read_firmware_iovar_is_observational_only"] = True
        report["on_device_test_performed"] = False
        base.REPORT.write_text(json.dumps(report,indent=2)+"\n")
        print("OFFLINE_COUNTRY_READ_ONLY_DIAGNOSTIC_ELF_MARKERS_PASS",flush=True)
    raise SystemExit(result)
