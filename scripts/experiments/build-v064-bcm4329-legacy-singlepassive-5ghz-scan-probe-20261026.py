#!/usr/bin/env python3
"""Experimental non-upstream single-channel BCM4329 legacy passive scan probe.

Exact-ABI source-restore builder. Based on v6b physically tested dual-band
wiphy and read-only scan-results header. For old BCM4329 FW that lacks
'chanspecs', add a ONE CHANNEL (5180 MHz), passive-only WLC_SCAN ioctl 50
and read bounded WLC_SCAN_RESULTS ioctl 51 after existing ten-second scan
timer. Validate record envelope v108 and log COUNT ONLY (no BSS payload,
SSIDs, BSSIDs, credentials, identities). Always complete cfg80211 request.
No generic firmware changes, persistent installation or scan at build time.

This is a lab-only diagnostic; not review-ready or physical-scan-proven.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name("build-v064-bcm4329-read-only-legacy-results-header-20261026.py")
spec = importlib.util.spec_from_file_location("mz600_legacy_results_header_v6b", P)
v6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v6)
builder = v6.builder

builder.WORK = builder.BASE / "v064-legacy-passive-single5g-v7-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-single-passive-5g-probe.ko"
builder.PATCH_PATH = builder.WORK / "0007-brcmfmac-lab-only-legacy-singlechannel-passive-scan.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
prior_patch = builder.make_patch


def patch(original):
    c = prior_patch(original)
    anchor = (
        "static s32\n"
        "brcmf_run_escan(struct brcmf_cfg80211_info *cfg, struct brcmf_if *ifp,\n"
    )
    legacy_fn = (
        "/* Lab-only: only firmware-declared US/69 channel 36, passive only. */\n"
        "static s32\n"
        "brcmf_run_legacy_passive_probe(struct brcmf_cfg80211_info *cfg,\n"
        "\t\t\t       struct brcmf_if *ifp,\n"
        "\t\t\t       struct cfg80211_scan_request *request)\n"
        "{\n"
        "\tstruct brcmf_scan_params_le *params;\n"
        "\tstruct ieee80211_channel *chan;\n"
        "\ts32 err;\n"
        "\n"
        "\tif (!request || request->n_channels != 1 || request->n_ssids ||\n"
        "\t    request->ie_len || request->flags)\n"
        "\t\treturn -EOPNOTSUPP;\n"
        "\tchan = request->channels[0];\n"
        "\tif (!chan || chan->band != NL80211_BAND_5GHZ ||\n"
        "\t    chan->center_freq != 5180 || chan->hw_value != 36 ||\n"
        "\t    (chan->flags & IEEE80211_CHAN_DISABLED) ||\n"
        "\t    !(chan->flags & IEEE80211_CHAN_NO_IR) ||\n"
        "\t    (chan->flags & IEEE80211_CHAN_RADAR))\n"
        "\t\treturn -EOPNOTSUPP;\n"
        "\tparams = kzalloc(BRCMF_SCAN_PARAMS_FIXED_SIZE + sizeof(__le16),\n"
        "\t\t\t GFP_KERNEL);\n"
        "\tif (!params)\n"
        "\t\treturn -ENOMEM;\n"
        "\teth_broadcast_addr(params->bssid);\n"
        "\tparams->bss_type = DOT11_BSSTYPE_ANY;\n"
        "\tparams->scan_type = BRCMF_SCANTYPE_PASSIVE;\n"
        "\tparams->nprobes = cpu_to_le32(0);\n"
        "\tparams->active_time = cpu_to_le32(0);\n"
        "\tparams->passive_time = cpu_to_le32(80);\n"
        "\tparams->home_time = cpu_to_le32(-1);\n"
        "\tparams->channel_num = cpu_to_le32(1);\n"
        "\tparams->channel_list[0] =\n"
        "\t\tcpu_to_le16(channel_to_chanspec(&cfg->d11inf, chan));\n"
        "\tbrcmf_info(\"MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0\\n\");\n"
        "\terr = brcmf_fil_cmd_data_set(ifp, BRCMF_C_SCAN,\n"
        "\t\t\t\t      params,\n"
        "\t\t\t\t      BRCMF_SCAN_PARAMS_FIXED_SIZE + sizeof(__le16));\n"
        "\tbrcmf_info(\"MZ600_LEGACY_SCAN_LAB_COMMAND50_RC=%d\\n\", err);\n"
        "\tkfree(params);\n"
        "\treturn err;\n"
        "}\n"
        "\n"
    )
    c = builder.exactly_one(c, anchor, legacy_fn + anchor, "LEGACY_SCAN_DRIVER_PRIVATE_START")

    anchor = "\tcfg->escan_info.run = brcmf_run_escan;\n\terr = brcmf_p2p_scan_prep(wiphy, request, vif);\n"
    replacement = (
        "\tcfg->escan_info.run = brcmf_run_escan;\n"
        "\t/* Lab-only capability check: old BCM4329 rejects 'chanspecs'.\n"
        "\t * Modern or other chips keep their unmodified escan path. */\n"
        "\tif (drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID &&\n"
        "\t    wiphy->bands[NL80211_BAND_5GHZ]) {\n"
        "\t\tu8 *lab_buf = kzalloc(BRCMF_DCMD_MEDLEN, GFP_KERNEL);\n"
        "\t\tint lab_rc;\n"
        "\n"
        "\t\tif (!lab_buf) {\n"
        "\t\t\terr = -ENOMEM;\n"
        "\t\t\tgoto scan_out;\n"
        "\t\t}\n"
        "\t\tlab_rc = brcmf_fil_iovar_data_get(vif->ifp, \"chanspecs\",\n"
        "\t\t\t\t\t\t lab_buf, BRCMF_DCMD_MEDLEN);\n"
        "\t\tkfree(lab_buf);\n"
        "\t\tif (lab_rc == -EBADE)\n"
        "\t\t\tcfg->escan_info.run = brcmf_run_legacy_passive_probe;\n"
        "\t}\n"
        "\terr = brcmf_p2p_scan_prep(wiphy, request, vif);\n"
    )
    c = builder.exactly_one(c, anchor, replacement, "LEGACY_SCAN_PRECISE_FW_GATE")

    anchor = (
        "static void brcmf_cfg80211_escan_timeout_worker(struct work_struct *work)\n"
        "{\n"
        "\tstruct brcmf_cfg80211_info *cfg =\n"
        "\t\t\tcontainer_of(work, struct brcmf_cfg80211_info,\n"
        "\t\t\t\t     escan_timeout_work);\n"
        "\n"
        "\tbrcmf_inform_bss(cfg);\n"
        "\tbrcmf_notify_escan_complete(cfg, cfg->escan_info.ifp, true, true);\n"
        "}\n"
    )
    worker = (
        "static void brcmf_cfg80211_escan_timeout_worker(struct work_struct *work)\n"
        "{\n"
        "\tstruct brcmf_cfg80211_info *cfg =\n"
        "\t\t\tcontainer_of(work, struct brcmf_cfg80211_info,\n"
        "\t\t\t\t     escan_timeout_work);\n"
        "\n"
        "\tif (cfg->escan_info.run == brcmf_run_legacy_passive_probe) {\n"
        "\t\tstruct brcmf_if *ifp = cfg->escan_info.ifp;\n"
        "\t\tu8 *raw = NULL;\n"
        "\t\t__le32 le_field;\n"
        "\t\tu32 len = 0, version = 0, count = 0, offset = 12;\n"
        "\t\tu32 i, rec_ver, rec_len;\n"
        "\t\tint rc = -ENOMEM;\n"
        "\t\tbool valid = false;\n"
        "\n"
        "\t\tif (!cfg->scan_request || !ifp)\n"
        "\t\t\treturn;\n"
        "\t\traw = kzalloc(BRCMF_DCMD_MAXLEN, GFP_KERNEL);\n"
        "\t\tif (raw) {\n"
        "\t\t\tle_field = cpu_to_le32(BRCMF_DCMD_MAXLEN);\n"
        "\t\t\tmemcpy(raw, &le_field, sizeof(le_field));\n"
        "\t\t\trc = brcmf_fil_cmd_data_get(ifp, BRCMF_C_SCAN_RESULTS,\n"
        "\t\t\t\t\t\t raw, BRCMF_DCMD_MAXLEN);\n"
        "\t\t\tif (!rc) {\n"
        "\t\t\t\tmemcpy(&le_field, raw, 4);\n"
        "\t\t\t\tlen = le32_to_cpu(le_field);\n"
        "\t\t\t\tmemcpy(&le_field, raw + 4, 4);\n"
        "\t\t\t\tversion = le32_to_cpu(le_field);\n"
        "\t\t\t\tmemcpy(&le_field, raw + 8, 4);\n"
        "\t\t\t\tcount = le32_to_cpu(le_field);\n"
        "\t\t\t\tvalid = len >= 12 && len <= BRCMF_DCMD_MAXLEN &&\n"
        "\t\t\t\t\tversion == 108 && count <= 64;\n"
        "\t\t\t\tfor (i = 0; valid && i < count; i++) {\n"
        "\t\t\t\t\tif (offset > len || len - offset < 8) {\n"
        "\t\t\t\t\t\tvalid = false;\n"
        "\t\t\t\t\t\tbreak;\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\t\tmemcpy(&le_field, raw + offset, 4);\n"
        "\t\t\t\t\trec_ver = le32_to_cpu(le_field);\n"
        "\t\t\t\t\tmemcpy(&le_field, raw + offset + 4, 4);\n"
        "\t\t\t\t\trec_len = le32_to_cpu(le_field);\n"
        "\t\t\t\t\tif (rec_ver != 108 || rec_len < 8 ||\n"
        "\t\t\t\t\t    rec_len > len - offset) {\n"
        "\t\t\t\t\t\tvalid = false;\n"
        "\t\t\t\t\t\tbreak;\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\t\toffset += rec_len;\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif (valid && offset != len)\n"
        "\t\t\t\t\tvalid = false;\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t\tbrcmf_info(\"MZ600_LEGACY_SCAN_LAB_RESULT51 rc=%d bytes=%u version=%u bss_count=%u envelope_ok=%u\\n\",\n"
        "\t\t\t   rc, len, version, count, valid);\n"
        "\t\tkfree(raw);\n"
        "\t\t/* Never present unvalidated v108 network identities to cfg80211.\n"
        "\t\t * Finish the owned scan exactly once with existing logic. */\n"
        "\t\tif (cfg->scan_request)\n"
        "\t\t\tbrcmf_notify_escan_complete(cfg, ifp, !valid, false);\n"
        "\t\treturn;\n"
        "\t}\n"
        "\tbrcmf_inform_bss(cfg);\n"
        "\tbrcmf_notify_escan_complete(cfg, cfg->escan_info.ifp, true, true);\n"
        "}\n"
    )
    c = builder.exactly_one(c, anchor, worker, "LEGACY_SCAN_BOUNDED_IOCTL51_TIMEOUT_WORKER")
    return c


builder.make_patch = patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        data = builder.TARGET.read_bytes()
        required = [
            b"MZ600_LEGACY_SCAN_LAB_START",
            b"MZ600_LEGACY_SCAN_LAB_COMMAND50_RC",
            b"MZ600_LEGACY_SCAN_LAB_RESULT51",
        ]
        if not all(token in data for token in required):
            raise SystemExit("Missing one of the protected lab scan markers")
        patch_text = builder.PATCH_PATH.read_text()
        for must in (
            "BRCMF_C_SCAN_RESULTS", "BRCMF_C_SCAN", "BRCMF_SCANTYPE_PASSIVE",
            "IEEE80211_CHAN_NO_IR", "nprobes = cpu_to_le32(0)",
            "chan->center_freq != 5180", "rec_ver != 108",
            "brcmf_notify_escan_complete", "cfg->scan_request",
        ):
            if must not in patch_text:
                raise SystemExit("Fail closed missing: " + must)
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "LAB_ONLY_BCM4329_SINGLE_PASSIVE_5GHZ_SCAN_BINARY_BUILT"
        report["does_not_scan_until_explicit_iw_scan_request"] = True
        report["firmware_version_onevariable_hri39"] = "4.218.248.20"
        report["test_channel_frequency_mhz"] = 5180
        report["no_ir_and_no_probe_requests"] = True
        report["scan_result_disclosure"] = "count/version/length/envelope_ok_only"
        report["kernel_cfg80211_bss_reporting"] = "none_until_version_108_parser_qualified"
        report["upstream_ready"] = False
        report["physical_test_run"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("OFFLINE_BOUNDED_SINGLE_5GHZ_PASSIVE_SCAN_MODULE_BUILT_ONLY", flush=True)
    raise SystemExit(rc)
