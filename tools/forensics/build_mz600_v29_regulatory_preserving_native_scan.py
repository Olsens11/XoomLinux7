#!/usr/bin/env python3
"""V29 lab: native cfg80211 scans, preserve existing regulatory channel flags.

Correct the V28 channel-list fallback which could replace flags already
applied by cfg80211 after wiphy_register(). Only add DISABLED to channels
absent from firmware's WLC_GET_VALID_CHANNELS; for supported channels do
not remove any existing regulatory restriction. Still capability-limit
legacy bandwidth to 20MHz until firmware capability is established.
No firmware/NVRAM writes, source-restoring exact ABI core+WCC build.
"""
import importlib.util,json
from pathlib import Path

PREV=Path(__file__).with_name("build_mz600_v28_native_cfg80211_scanning.py")
spec=importlib.util.spec_from_file_location("mz600_v28_native",PREV)
v28=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v28)
base=v28.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v29-regsafe-20261027"
v28.v26.v25.WCC_COPY=base.RESULT/"brcmfmac-wcc-matched-v25.ko"
prior_scan=base.instrument
prior_fweh=base.instrument_fweh

def instrument_scan(original):
    c=prior_scan(original)
    # This exact block is in the private legacy valid-channel fallback
    # of patch 0005 only. No changes to the upstream chanspec normal path.
    old='''\
			band = wiphy->bands[NL80211_BAND_2GHZ];
			if (band)
				for (j = 0; j < band->n_channels; j++)
					band->channels[j].flags = IEEE80211_CHAN_DISABLED;
			band = wiphy->bands[NL80211_BAND_5GHZ];
			if (band)
				for (j = 0; j < band->n_channels; j++)
					band->channels[j].flags = IEEE80211_CHAN_DISABLED;
'''
    new='''\
			/*
			 * wiphy_register() has already run: NEVER replace
			 * supported channel flags with orig_flags. Preserve
			 * the current cfg80211/regdb restrictions and only
			 * disable frequencies absent from the firmware list.
			 */
			band = wiphy->bands[NL80211_BAND_2GHZ];
			if (band) {
				for (j = 0; j < band->n_channels; j++) {
					bool supported = false;
					for (index = 0; index < count; index++) {
						if (band->channels[j].hw_value ==
						    le32_to_cpu(list->element[index])) {
							supported = true;
							break;
						}
					}
					if (!supported)
						band->channels[j].flags |= IEEE80211_CHAN_DISABLED;
				}
			}
			band = wiphy->bands[NL80211_BAND_5GHZ];
			if (band) {
				for (j = 0; j < band->n_channels; j++) {
					bool supported = false;
					for (index = 0; index < count; index++) {
						if (band->channels[j].hw_value ==
						    le32_to_cpu(list->element[index])) {
							supported = true;
							break;
						}
					}
					if (!supported)
						band->channels[j].flags |= IEEE80211_CHAN_DISABLED;
				}
			}
'''
    c=base.replace_once(c,old,new)
    before='''\
				channel->flags = channel->orig_flags |
					IEEE80211_CHAN_NO_HT40 |
					IEEE80211_CHAN_NO_80MHZ |
					IEEE80211_CHAN_NO_160MHZ;'''
    after='''\
				/* Keep regulatory bits (NO_IR, RADAR,
				 * DISABLED, etc.) already applied by cfg80211.
				 * Only narrow unproven legacy bandwidth.
				 */
				channel->flags |= IEEE80211_CHAN_NO_HT40 |
					IEEE80211_CHAN_NO_80MHZ |
					IEEE80211_CHAN_NO_160MHZ;'''
    c=base.replace_once(c,before,after)
    return c.replace("MZ600_V28_","MZ600_V29_")

def instrument_fweh(original):
    return prior_fweh(original).replace("MZ600_V28_","MZ600_V29_")

base.instrument=instrument_scan
base.instrument_fweh=instrument_fweh

def main():
    v28.main()
    out=base.RESULT
    old=out/"brcmfmac-2012-escan-native-scan-v28.ko"
    new=out/"brcmfmac-2012-escan-regsafe-v29.ko"
    oldw=out/"brcmfmac-wcc-matched-v28.ko"
    neww=out/"brcmfmac-wcc-matched-v29.ko"
    if new.exists() or neww.exists():
        raise RuntimeError("STOP: refusing V29 overwrite")
    old.rename(new)
    oldw.rename(neww)
    report=out/"offline-build-result.json"
    obj=json.loads(report.read_text())
    obj.update({
        "test":"V29_NATIVE_SCANNING_KEEP_CFG80211_REG_FLAGS",
        "module_name":new.name,"artifact_name":new.name,
        "matched_wcc_name":neww.name,
        "module_sha256":base.sha(new.read_bytes()),
        "module_bytes":len(new.read_bytes()),
        "matched_wcc_sha256":base.sha(neww.read_bytes()),
        "matched_wcc_bytes":len(neww.read_bytes()),
        "only_disable_firmware_unsupported_channels":True,
        "preserves_existing_regulatory_flags":True,
        "forces_no_ir":False,
        "clears_no_ir":False,
        "limits_scans_to_channel36":False,
        "forces_passive_scan":False,
        "on_device_test":"NOT_YET_RUN",
        "upstream_patch":False,
    })
    report.write_text(json.dumps(obj,indent=2)+"\n")
    print("V29_REGULATORY_PRESERVING_ARM_PAIR_BUILD_PASS",obj["module_sha256"],obj["matched_wcc_sha256"])

if __name__=="__main__":
    main()
