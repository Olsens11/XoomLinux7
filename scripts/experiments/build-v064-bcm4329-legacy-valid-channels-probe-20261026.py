#!/usr/bin/env python3
"""Build brcmfmac read-only OEM legacy valid-channels probe, ABI 7.0.

A temporary lab module for BCM4329 firmware 4.218.x. On 'chanspecs'
firmware-get failure ONLY, query historical WLC_GET_VALID_CHANNELS (217)
with declared buffer capacity and count 2G/5G entries. Original driver
failure is preserved; NO channels enabled, no tx, no country override.
Builds via existing reversible exact-kernel ABI builder; no deployment.
"""
import importlib.util
import json
from pathlib import Path

COUNTRY_BUILDER = Path(__file__).with_name(
    "build-v064-bcm4329-country-iovar-and-bandlist-diagnostic-20261026.py")
spec = importlib.util.spec_from_file_location("mz600_country_builder_v3", COUNTRY_BUILDER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
builder = mod.base

builder.WORK = builder.BASE / "v064-legacy-valid-channels-diag-v4-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-valid-channels-ram-diagnostic.ko"
builder.PATCH_PATH = builder.WORK / "0004-brcmfmac-diagnose-legacy-valid-channels-without-enabling.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"

original_patch = builder.make_patch

def legacy_probe_patch(original):
    c = original_patch(original)
    old = (
        "\terr = brcmf_fil_iovar_data_get(ifp, \"chanspecs\", pbuf,\n"
        "\t\t\t\t       BRCMF_DCMD_MEDLEN);\n"
        "\tif (err) {\n"
        "\t\tbphy_err(drvr, \"get chanspecs error (%d)\\n\", err);\n"
        "\t\tgoto fail_pbuf;\n"
        "\t}\n"
    )
    new = (
        "\terr = brcmf_fil_iovar_data_get(ifp, \"chanspecs\", pbuf,\n"
        "\t\t\t\t       BRCMF_DCMD_MEDLEN);\n"
        "\tif (err) {\n"
        "\t\tint saved_err = err;\n"
        "\t\tint legacy_rc;\n"
        "\t\tu32 max_channels = (BRCMF_DCMD_MEDLEN - sizeof(list->count)) /\n"
        "\t\t\t\t   sizeof(list->element[0]);\n"
        "\t\tu32 count = 0, count_2g = 0, count_5g = 0, count_other = 0;\n"
        "\t\tu32 index, legacy_channel;\n"
        "\t\tbphy_err(drvr, \"get chanspecs error (%d)\\n\", err);\n"
        "\t\t/* Diagnostic ONLY. Legacy Motorola DHD uses ioctl 217 and\n"
        "\t\t * sets list->count to output capacity before querying. */\n"
        "\t\tmemset(pbuf, 0, BRCMF_DCMD_MEDLEN);\n"
        "\t\tlist->count = cpu_to_le32(max_channels);\n"
        "\t\tlegacy_rc = brcmf_fil_cmd_data_get(ifp,\n"
        "\t\t\t\t\t      BRCMF_C_GET_VALID_CHANNELS,\n"
        "\t\t\t\t\t      pbuf, BRCMF_DCMD_MEDLEN);\n"
        "\t\tif (!legacy_rc) {\n"
        "\t\t\tcount = le32_to_cpu(list->count);\n"
        "\t\t\tif (count <= max_channels) {\n"
        "\t\t\t\tfor (index = 0; index < count; index++) {\n"
        "\t\t\t\t\tlegacy_channel = le32_to_cpu(list->element[index]);\n"
        "\t\t\t\t\tif (legacy_channel >= 1 && legacy_channel <= 14)\n"
        "\t\t\t\t\t\tcount_2g++;\n"
        "\t\t\t\t\telse if (legacy_channel >= 30 && legacy_channel <= 196)\n"
        "\t\t\t\t\t\tcount_5g++;\n"
        "\t\t\t\t\telse\n"
        "\t\t\t\t\t\tcount_other++;\n"
        "\t\t\t\t}\n"
        "\t\t\t} else {\n"
        "\t\t\t\tlegacy_rc = -EINVAL;\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t\tbrcmf_info(\"MZ600_5G_DIAG_LEGACY_VALID_CHANNELS original_chanspec_rc=%d legacy_rc=%d total=%u 2g=%u 5g=%u other=%u max=%u\\n\",\n"
        "\t\t\t   saved_err, legacy_rc, count, count_2g, count_5g,\n"
        "\t\t\t   count_other, max_channels);\n"
        "\t\terr = saved_err; /* NEVER mask existing firmware failure */\n"
        "\t\tgoto fail_pbuf;\n"
        "\t}\n"
    )
    c = builder.exactly_one(c, old, new, "READONLY_LEGACY_VALID_CHANNELS_FALLBACK_PROBE")
    return c

builder.make_patch = legacy_probe_patch

if __name__ == "__main__":
    outcome = builder.main()
    if outcome == 0:
        raw = builder.TARGET.read_bytes()
        if b"MZ600_5G_DIAG_LEGACY_VALID_CHANNELS" not in raw:
            raise SystemExit("Missing legacy ioctl 217 read-only diagnostic in ELF")
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "EXACT_ABI_READONLY_LEGACY_VALID_CHANNELS_PROBE_BUILT_AND_RESTORED"
        report["legacy_ioctl"] = "WLC_GET_VALID_CHANNELS:217"
        report["masks_original_error"] = False
        report["enables_or_changes_channels"] = False
        report["firmware_country_set_operations"] = 0
        report["test_on_device_performed"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2)+"\n")
        print("OFFLINE_LEGACY_FW_CHANNEL_PROBE_ELF_VERIFIED_NO_RADIO_WRITE",flush=True)
    raise SystemExit(outcome)
