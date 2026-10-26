#!/usr/bin/env python3
"""Exact-ABI v8, lab-only validation of REAL HRI39 legacy BSS v108 records.

Keep v7's already physically proven single-channel passive ioctl 50/51
and firmware/channel regulatory constraints entirely unchanged. One
new diagnostic question: do individual original-firmware version-108
BSS structures satisfy full fixed-header and IE bounds, and how many
claim control-channel 36? Log COUNTS ONLY, never BSSID/SSID/IE content.
No cfg80211 BSS reporting and no new scan-start/completion behavior.

Separate eventual upstream changes, one logical change per commit.
This builder does not run the device or install a module.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name(
    "build-v064-bcm4329-legacy-singlepassive-5ghz-scan-probe-20261026.py"
)
spec = importlib.util.spec_from_file_location("mz600_legacy_v7_builder", P)
v7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v7)
builder = v7.builder
builder.WORK = builder.BASE / "v064-legacy-bss108-validator-v8-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-v108-record-validator-v8.ko"
builder.PATCH_PATH = builder.WORK / "0008-lab-only-bcm4329-legacy-bss108-sanitized-validator.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
previous = builder.make_patch


def patch(original):
    code = previous(original)
    # Add local counters in old scan-results timeout branch.
    needle = "\t\tbool valid = false;\n"
    code = builder.exactly_one(
        code, needle,
        needle + "\t\tu32 v108_checked = 0, v108_chan36 = 0, v108_other = 0;\n"
                 "\t\tu32 v108_invalid_ie = 0;\n",
        "V108_BSS_LOCAL_COUNTS",
    )
    # The older wl_bss_info_t is exactly the modern structure THROUGH
    # ie_length, without modern trailing SNR. Assert field offsets at
    # build time so a kernel rebase cannot silently invalidate parsing.
    anchor = (
        "\t\tbrcmf_info(\"MZ600_LEGACY_SCAN_LAB_RESULT51 rc=%d bytes=%u version=%u bss_count=%u envelope_ok=%u\\n\",\n"
    )
    checks = r'''
		/* Legacy Broadcom wl_bss_info version 108 ends before SNR.
		 * Validate lengths/IEs before inspecting any BSS data.
		 * This deliberately NEVER informs cfg80211 of the BSS. */
		BUILD_BUG_ON(offsetof(struct brcmf_bss_info_le, SNR) != 124);
		BUILD_BUG_ON(offsetof(struct brcmf_bss_info_le, ctl_ch) != 88);
		BUILD_BUG_ON(offsetof(struct brcmf_bss_info_le, ie_offset) != 116);
		BUILD_BUG_ON(offsetof(struct brcmf_bss_info_le, ie_length) != 120);
		if (!rc && valid) {
			u32 record_at = 12;

			for (i = 0; i < count; i++) {
				__le16 tmp16;
				__le32 tmp32;
				u32 rec_bytes, ie_at, ie_bytes, end, cursor;
				u8 ctl_ch, ssid_bytes;

				/* Envelope pass already validated each record
				 * version, length and overall consumption. */
				memcpy(&tmp32, raw + record_at + 4, sizeof(tmp32));
				rec_bytes = le32_to_cpu(tmp32);
				if (rec_bytes < 124) {
					valid = false;
					break;
				}
				ssid_bytes = raw[record_at +
					offsetof(struct brcmf_bss_info_le, SSID_len)];
				ctl_ch = raw[record_at +
					offsetof(struct brcmf_bss_info_le, ctl_ch)];
				memcpy(&tmp16, raw + record_at +
				       offsetof(struct brcmf_bss_info_le, ie_offset),
				       sizeof(tmp16));
				ie_at = le16_to_cpu(tmp16);
				memcpy(&tmp32, raw + record_at +
				       offsetof(struct brcmf_bss_info_le, ie_length),
				       sizeof(tmp32));
				ie_bytes = le32_to_cpu(tmp32);
				if (ssid_bytes > IEEE80211_MAX_SSID_LEN ||
				    ie_at < 124 || ie_at > rec_bytes ||
				    ie_bytes > rec_bytes - ie_at) {
					valid = false;
					break;
				}
				/* Walk each IE TLV with per-record bounds. */
				end = ie_at + ie_bytes;
				cursor = ie_at;
				while (cursor < end) {
					u8 element_bytes;

					if (end - cursor < 2) {
						v108_invalid_ie++;
						valid = false;
						break;
					}
					element_bytes = raw[record_at + cursor + 1];
					if (element_bytes > end - cursor - 2) {
						v108_invalid_ie++;
						valid = false;
						break;
					}
					cursor += 2 + element_bytes;
				}
				if (!valid)
					break;
				v108_checked++;
				if (ctl_ch == 36)
					v108_chan36++;
				else
					v108_other++;
				record_at += rec_bytes;
			}
			if (valid && v108_checked != count)
				valid = false;
		}
		brcmf_info("MZ600_LEGACY_BSS108_VALIDATION records=%u ctl36=%u other=%u invalid_ie=%u safe=%u\n",
			   v108_checked, v108_chan36, v108_other,
			   v108_invalid_ie, valid);
'''
    # Kernel source was already modified by the previous experiment.
    code = builder.exactly_one(
        code, anchor, checks + anchor, "V108_FIXED_FIELDS_IE_TLV_AND_CHANNEL_SUMMARY"
    )
    return code


builder.make_patch = patch

if __name__ == "__main__":
    status = builder.main()
    if status == 0:
        compiled = builder.TARGET.read_bytes()
        if b"MZ600_LEGACY_BSS108_VALIDATION" not in compiled:
            raise SystemExit("Missing BSS v108 validator marker in ELF")
        source_diff = builder.PATCH_PATH.read_text()
        for must in (
            "MZ600_LEGACY_BSS108_VALIDATION",
            "offsetof(struct brcmf_bss_info_le, SNR) != 124",
            "offsetof(struct brcmf_bss_info_le, ctl_ch) != 88",
            "offsetof(struct brcmf_bss_info_le, ie_offset) != 116",
            "offsetof(struct brcmf_bss_info_le, ie_length) != 120",
            "IEEE80211_MAX_SSID_LEN",
            "ie_bytes > rec_bytes - ie_at",
            "element_bytes > end - cursor - 2",
            "cfg->scan_request",
        ):
            if must not in source_diff:
                raise SystemExit("Missing fail-closed kernel guard: " + must)
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "LAB_ONLY_BSS108_FULL_BOUNDS_AND_TLV_VALIDATOR_BUILT"
        report["prints_ssid_bssid_ies"] = False
        report["reports_records_to_cfg80211"] = False
        report["changes_scan_start_or_completion"] = False
        report["physical_test_run"] = False
        report["upstream_ready"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("OFFLINE_V8_FULL_BSS108_VALIDATION_EXACT_ABI_PASS", flush=True)
    raise SystemExit(status)
