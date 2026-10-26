#!/usr/bin/env python3
"""v11 bounded legacy v108 BSS -> cfg80211 lab integration (no lifecycle changes).

Composes exact physical-v10 source, including 300ms passive NO_IR channel36,
its full-record and IE validator, and observation-only scancomplete event26.
Only NEW behavior: after full validation of all records, announce them using
the existing cfg80211_inform_bss_data() API; never log network identifiers.
Uses same 10s fallback and exactly-once scan_done as v10. No RF at build time.
Not upstream-ready, no persistent kernel change.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name(
    "build-v064-bcm4329-legacy-passive-dwell300-v10-20261026.py"
)
spec = importlib.util.spec_from_file_location("mz600_v10_build", P)
v10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v10)

builder = v10.builder
builder.WORK = builder.BASE / "v064-legacy-v108-cfg80211-inform-v11-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-v108-cfg80211-inform-v11.ko"
builder.PATCH_PATH = builder.WORK / "0011-bcm4329-lab-v108-cfg80211-bss-inform.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
previous = builder.make_patch


def patch(original):
    code = previous(original)
    # Already called in the scan-timeout worker, after all outer and IE
    # checks pass. All decoded offsets are fixed and compile-time asserted.
    helper = r'''
/* Only call after the full 108 envelope+IE validator has accepted EVERY
 * record. This does not alter the legacy ioctl-50 scan lifecycle or the
 * modern firmware escan path. No BSSID, SSID or IE logging. */
static int brcmf_legacy_inform_bss108(struct brcmf_cfg80211_info *cfg,
				      const u8 *raw, u32 total, u32 count)
{
	struct wiphy *wiphy = cfg_to_wiphy(cfg);
	struct ieee80211_channel *channel;
	struct cfg80211_inform_bss bss_data = {};
	struct cfg80211_bss *bss;
	u32 offset = 12, n, length, ies_start, ies_size;
	__le16 le16;
	__le32 le32;
	s16 rssi;
	u16 beacon, capability;
	int informed = 0;

	channel = ieee80211_get_channel(wiphy, 5180);
	if (!channel || channel->band != NL80211_BAND_5GHZ ||
	    channel->hw_value != 36 ||
	    (channel->flags & (IEEE80211_CHAN_DISABLED | IEEE80211_CHAN_RADAR)) ||
	    !(channel->flags & IEEE80211_CHAN_NO_IR))
		return -EINVAL;
	if (!cfg->scan_request || cfg->scan_request->n_channels != 1 ||
	    cfg->scan_request->channels[0] != channel)
		return -EINVAL;

	/* Preflight ALL metadata before publishing any BSS to cfg80211. */
	{
		u32 at = 12;

		for (n = 0; n < count; n++) {
			const u8 *record, *bssid;
			s16 signal;
			u32 size;

			if (at > total || total - at < 124)
				return -EINVAL;
			record = raw + at;
			memcpy(&le32, record, sizeof(le32));
			if (le32_to_cpu(le32) != 108)
				return -EINVAL;
			memcpy(&le32, record + 4, sizeof(le32));
			size = le32_to_cpu(le32);
			if (size < 124 || size > total - at)
				return -EINVAL;
			if (record[offsetof(struct brcmf_bss_info_le, ctl_ch)] != 36)
				return -EINVAL;
			memcpy(&le16, record +
			       offsetof(struct brcmf_bss_info_le, RSSI),
			       sizeof(le16));
			signal = (s16)le16_to_cpu(le16);
			if (signal > 0 || signal < -127)
				return -EINVAL;
			bssid = record + offsetof(struct brcmf_bss_info_le, BSSID);
			if (!is_valid_ether_addr(bssid))
				return -EINVAL;
			at += size;
		}
		if (at != total)
			return -EINVAL;
	}

	for (n = 0; n < count; n++) {
		const u8 *record, *bssid;
		u8 ctl_ch, ssid_len;

		if (offset > total || total - offset < 124)
			return -EINVAL;
		record = raw + offset;
		memcpy(&le32, record + 4, sizeof(le32));
		length = le32_to_cpu(le32);
		if (length < 124 || length > total - offset)
			return -EINVAL;
		ctl_ch = record[offsetof(struct brcmf_bss_info_le, ctl_ch)];
		ssid_len = record[offsetof(struct brcmf_bss_info_le, SSID_len)];
		if (ctl_ch != 36 || ssid_len > IEEE80211_MAX_SSID_LEN)
			return -EINVAL;
		memcpy(&le16, record +
		       offsetof(struct brcmf_bss_info_le, ie_offset),
		       sizeof(le16));
		ies_start = le16_to_cpu(le16);
		memcpy(&le32, record +
		       offsetof(struct brcmf_bss_info_le, ie_length),
		       sizeof(le32));
		ies_size = le32_to_cpu(le32);
		if (ies_start < 124 || ies_start > length ||
		    ies_size > length - ies_start)
			return -EINVAL;

		memcpy(&le16, record +
		       offsetof(struct brcmf_bss_info_le, beacon_period),
		       sizeof(le16));
		beacon = le16_to_cpu(le16);
		memcpy(&le16, record +
		       offsetof(struct brcmf_bss_info_le, capability),
		       sizeof(le16));
		capability = le16_to_cpu(le16);
		memcpy(&le16, record +
		       offsetof(struct brcmf_bss_info_le, RSSI), sizeof(le16));
		rssi = (s16)le16_to_cpu(le16);
		if (rssi > 0 || rssi < -127)
			return -EINVAL;
		bssid = record + offsetof(struct brcmf_bss_info_le, BSSID);
		if (!is_valid_ether_addr(bssid))
			return -EINVAL;

		bss_data.chan = channel;
		bss_data.boottime_ns = ktime_to_ns(ktime_get_boottime());
		bss_data.signal = (s32)rssi * 100;
		bss = cfg80211_inform_bss_data(
			wiphy, &bss_data, CFG80211_BSS_FTYPE_UNKNOWN,
			bssid, 0, capability, beacon, record + ies_start,
			ies_size, GFP_KERNEL);
		if (!bss)
			return -ENOMEM;
		cfg80211_put_bss(wiphy, bss);
		informed++;
		offset += length;
	}
	return offset == total ? informed : -EINVAL;
}

'''
    anchor = (
        "static s32\n"
        "brcmf_run_escan(struct brcmf_cfg80211_info *cfg, struct brcmf_if *ifp,\n"
    )
    code = builder.exactly_one(code, anchor, helper + anchor,
                               "LEGACY_VALIDATED_V108_CFG80211_BSS_HELPER")

    needle = (
        '\t\tbrcmf_info("MZ600_LEGACY_BSS108_VALIDATION records=%u ctl36=%u other=%u invalid_ie=%u safe=%u\\n",\n'
    )
    injection = (
        "\t\tif (valid && count && v108_checked == count &&\n"
        "\t\t    v108_other == 0) {\n"
        "\t\t\tint announced;\n\n"
        "\t\t\tannounced = brcmf_legacy_inform_bss108(cfg, raw, len,\n"
        "\t\t\t\t\t\t\t  count);\n"
        "\t\t\tbrcmf_info(\"MZ600_LEGACY_CFG80211_BSS_INFORM count=%d requested=%u\\n\",\n"
        "\t\t\t\t   announced, count);\n"
        "\t\t\tif (announced < 0 || announced != count)\n"
        "\t\t\t\tvalid = false;\n"
        "\t\t}\n"
    )
    code = builder.exactly_one(code, needle, injection + needle,
                               "V108_KNOWN_SAFE_SCAN_CFG80211_REPORT")
    return code


builder.make_patch = patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        raw = builder.TARGET.read_bytes()
        patch = builder.PATCH_PATH.read_text()
        checks = [
            "MZ600_LEGACY_CFG80211_BSS_INFORM",
            "cfg80211_inform_bss_data(",
            "cfg80211_put_bss(",
            "IEEE80211_CHAN_NO_IR",
            "v108_checked == count",
            "v108_other == 0",
            "cfg->scan_request",
            "is_valid_ether_addr(bssid)",
        ]
        for s in checks:
            if s not in patch:
                raise SystemExit("missing cfg80211 safe-reporting gate: " + s)
        if b"MZ600_LEGACY_CFG80211_BSS_INFORM" not in raw:
            raise SystemExit("v11 ELF lacks guarded cfg80211 reporting marker")
        report = json.loads(builder.REPORT.read_text())
        report["result"] = "V11_LAB_ONLY_BSS108_VERIFIED_TO_CFG80211_ABI_BUILT"
        report["physical_scan_performed"] = False
        report["scan_lifecycle_change"] = False
        report["no_identifiers_in_kernel_debug_logs"] = True
        report["user_visible_iw_results"] = "PRIVATE_HOST_OUTPUT_ONLY"
        report["upstream_ready"] = False
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("V11_BSS108_CFG80211_EXACT_ABI_OFFLINE_BUILD_PASS")
    raise SystemExit(rc)
