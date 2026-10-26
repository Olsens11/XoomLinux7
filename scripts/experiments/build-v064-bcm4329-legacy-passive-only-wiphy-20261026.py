#!/usr/bin/env python3
"""Lab-only BCM4329 legacy channel compatibility: firmware-validated PASSIVE ONLY.

Based on physically successful WLC_GET_VALID_CHANNELS(217) read-only probe.
If modern 'chanspecs' is rejected, and ONLY on BCM4329, map legacy firmware
channel numbers to existing Linux wiphy 2G/5G channels. Never fabricate any,
always NO_IR + NO_HT40/80/160, preserve disabled and radar restrictions.

This is NOT an upstream patch and must receive physical and multiple-unit
regulatory tests before any ordinary use. Exact ABI one-shot build; no deploy.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name("build-v064-bcm4329-legacy-valid-channels-probe-20261026.py")
spec = importlib.util.spec_from_file_location("mz600_legacy_ioctl217_builder_v4", P)
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)

builder = v4.builder
builder.WORK = builder.BASE / "v064-legacy-passive-only-wiphy-v5-20261026"
builder.TARGET = builder.WORK / "brcmfmac-4329-legacy-passive-only-lab.ko"
builder.PATCH_PATH = builder.WORK / "0005-brcmfmac-bcm4329-legacy-valid-channel-passive-only-fallback.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"

prior_patch = builder.make_patch

def passive_only_patch(original):
    c = prior_patch(original)
    old = (
        "\t\terr = saved_err; /* NEVER mask existing firmware failure */\n"
        "\t\tgoto fail_pbuf;\n"
    )
    new = (
        "\t\t/* Narrow, non-transmitting fallback for BCM4329 firmware\n"
        "\t\t * which has no 'chanspecs' iovar but reports valid channels.\n"
        "\t\t * No broad device override, no regulatory bypass, no TX. */\n"
        "\t\tif (saved_err == -EBADE && !legacy_rc && count > 0 &&\n"
        "\t\t    count_5g > 0 && !count_other &&\n"
        "\t\t    drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID) {\n"
        "\t\t\tband = wiphy->bands[NL80211_BAND_2GHZ];\n"
        "\t\t\tif (band)\n"
        "\t\t\t\tfor (j = 0; j < band->n_channels; j++)\n"
        "\t\t\t\t\tband->channels[j].flags = IEEE80211_CHAN_DISABLED;\n"
        "\t\t\tband = wiphy->bands[NL80211_BAND_5GHZ];\n"
        "\t\t\tif (band)\n"
        "\t\t\t\tfor (j = 0; j < band->n_channels; j++)\n"
        "\t\t\t\t\tband->channels[j].flags = IEEE80211_CHAN_DISABLED;\n"
        "\t\t\tfor (index = 0; index < count; index++) {\n"
        "\t\t\t\tlegacy_channel = le32_to_cpu(list->element[index]);\n"
        "\t\t\t\tband = legacy_channel <= 14 ?\n"
        "\t\t\t\t\twiphy->bands[NL80211_BAND_2GHZ] :\n"
        "\t\t\t\t\twiphy->bands[NL80211_BAND_5GHZ];\n"
        "\t\t\t\tif (!band)\n"
        "\t\t\t\t\tcontinue;\n"
        "\t\t\t\tfor (j = 0; j < band->n_channels; j++)\n"
        "\t\t\t\t\tif (band->channels[j].hw_value == legacy_channel)\n"
        "\t\t\t\t\t\tbreak;\n"
        "\t\t\t\tif (j == band->n_channels)\n"
        "\t\t\t\t\tcontinue;\n"
        "\t\t\t\tchannel = &band->channels[j];\n"
        "\t\t\t\tif (channel->orig_flags & IEEE80211_CHAN_DISABLED)\n"
        "\t\t\t\t\tcontinue;\n"
        "\t\t\t\t/* No active TX or initiating radiation on ANY\n"
        "\t\t\t\t * legacy channel; cfg80211 regdb may only narrow. */\n"
        "\t\t\t\tchannel->flags = channel->orig_flags |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_IR |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_HT40 |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_80MHZ |\n"
        "\t\t\t\t\tIEEE80211_CHAN_NO_160MHZ;\n"
        "\t\t\t\tif (band->band == NL80211_BAND_5GHZ &&\n"
        "\t\t\t\t    channel->center_freq >= 5260 &&\n"
        "\t\t\t\t    channel->center_freq <= 5720)\n"
        "\t\t\t\t\tchannel->flags |= IEEE80211_CHAN_RADAR;\n"
        "\t\t\t}\n"
        "\t\t\tbrcmf_info(\"MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK chip=4329 fw2g=%u fw5g=%u no_ir=1 ht20_only=1\\n\",\n"
        "\t\t\t\t   count_2g, count_5g);\n"
        "\t\t\terr = 0;\n"
        "\t\t\tgoto fail_pbuf; /* shared free buffer */\n"
        "\t\t}\n"
        "\t\terr = saved_err;\n"
        "\t\tgoto fail_pbuf;\n"
    )
    return builder.exactly_one(c, old, new, "SAFE_PASSIVE_ONLY_FW_LIST_FALLBACK")

builder.make_patch = passive_only_patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        raw = builder.TARGET.read_bytes()
        if b"MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK" not in raw:
            raise SystemExit("Missing passive-only channel fallback marker in ELF")
        patch = builder.PATCH_PATH.read_text()
        for required in [
            "BRCMF_C_GET_VALID_CHANNELS", "BRCM_CC_4329_CHIP_ID",
            "IEEE80211_CHAN_NO_IR", "IEEE80211_CHAN_NO_HT40",
            "IEEE80211_CHAN_NO_80MHZ", "IEEE80211_CHAN_NO_160MHZ",
            "IEEE80211_CHAN_RADAR", "saved_err == -EBADE",
        ]:
            if required not in patch:
                raise SystemExit("Missing required fail-closed constraint "+required)
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "LAB_ONLY_LEGACY_BCM4329_NO_IR_WIPHY_BUILT_RESTORED"
        report["firmware_query"] = "WLC_GET_VALID_CHANNELS(217)"
        report["no_ir_every_fallback_channel"] = True
        report["disables_ht40_80_160_on_fallback_channels"] = True
        report["5ghz_dfs_range_radar_flagged"] = True
        report["no_country_override_or_scan"] = True
        report["upstream_or_multiunit_qualified"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2)+"\n")
        print("OFFLINE_LEGACY_BCM4329_PASSIVE_ONLY_FALLBACK_ABI_AND_GATES_PASS",flush=True)
    raise SystemExit(rc)
