#!/usr/bin/env python3
"""V25 LAB ONLY: exact numeric reason for consecutive-scan -EPERM.

Builds source-restoring V24 generation-checker with purely diagnostic,
bounded scan-gate logs; no radio policy/firmware/association changes.
Packages ABI-matched brcmfmac.ko AND automatically loaded WCC module.
Restores the host's original compiled WCC artifact even on failure.
"""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PREV=ROOT/"build_mz600_v24_generation_checked_terminal.py"
spec=importlib.util.spec_from_file_location("mz600_v24_builder",PREV)
v24=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v24)
base=v24.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v25-20261027"
old_scan=base.instrument
old_event=base.instrument_fweh
WCC=base.M/"wcc"/"brcmfmac-wcc.ko"
BASE_CORE=base.KO
WCC_COPY=base.RESULT/"brcmfmac-wcc-matched-v25.ko"

def instrument_scan(original):
    c=old_scan(original).replace("MZ600_V24_","MZ600_V25_")
    guard='''\
\t\tif (request->n_channels != 1 || request->n_ssids != 0 ||
\t\t    request->ie_len != 0)
\t\t\treturn -EPERM;'''
    replacement='''\
\t\tbrcmf_info("MZ600_V25_SCAN_REQUEST n_channels=%u n_ssids=%u ie_len=%zu busy=%u\\n",
\t\t\t   request->n_channels, request->n_ssids,
\t\t\t   request->ie_len,
\t\t\t   !!test_bit(BRCMF_SCAN_STATUS_BUSY, &cfg->scan_status));
\t\tif (request->n_channels != 1 || request->n_ssids != 0 ||
\t\t    request->ie_len != 0) {
\t\t\tbrcmf_info("MZ600_V25_GATE_REJECT reason=counts channels=%u ssids=%u ie_len=%zu\\n",
\t\t\t\t   request->n_channels, request->n_ssids,
\t\t\t\t   request->ie_len);
\t\t\treturn -EPERM;
\t\t}'''
    c=base.replace_once(c,guard,replacement)
    guard='''\
\t\tif (!ch || ch->center_freq != 5180 || ch->hw_value != 36 ||
\t\t    !(ch->flags & IEEE80211_CHAN_NO_IR) ||
\t\t    (ch->flags & (IEEE80211_CHAN_DISABLED |
\t\t\t\t IEEE80211_CHAN_RADAR)))
\t\t\treturn -EPERM;'''
    replacement='''\
\t\tif (!ch || ch->center_freq != 5180 || ch->hw_value != 36 ||
\t\t    !(ch->flags & IEEE80211_CHAN_NO_IR) ||
\t\t    (ch->flags & (IEEE80211_CHAN_DISABLED |
\t\t\t\t IEEE80211_CHAN_RADAR))) {
\t\t\tbrcmf_info("MZ600_V25_GATE_REJECT reason=channel present=%u freq=%u channel=%u flags=0x%x no_ir=%u disabled=%u radar=%u\\n",
\t\t\t\t   !!ch, ch ? ch->center_freq : 0,
\t\t\t\t   ch ? ch->hw_value : 0, ch ? ch->flags : 0,
\t\t\t\t   !!(ch && (ch->flags & IEEE80211_CHAN_NO_IR)),
\t\t\t\t   !!(ch && (ch->flags & IEEE80211_CHAN_DISABLED)),
\t\t\t\t   !!(ch && (ch->flags & IEEE80211_CHAN_RADAR)));
\t\t\treturn -EPERM;
\t\t}'''
    c=base.replace_once(c,guard,replacement)
    # V24's inherited V23 logger reported the obsolete module parameter, not
    # the generation override. Report the actual encoded request field.
    old='''\
\t\tbrcmf_info("MZ600_V25_SCAN_REQUEST_SYNC id=%u\\n",
\t\t\t   READ_ONCE(mz600_v23_request_sync_id));'''
    new='''\
\t\tbrcmf_info("MZ600_V25_SCAN_REQUEST_SYNC id=%u\\n",
\t\t\t   le16_to_cpu(params->sync_id));'''
    c=base.replace_once(c,old,new)
    return c

def instrument_event(original):
    return old_event(original).replace("MZ600_V24_","MZ600_V25_")

base.instrument=instrument_scan
base.instrument_fweh=instrument_event

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    if base.RESULT.exists():
        raise RuntimeError("V25 output exists; preserve previous trials")
    before_wcc=WCC.read_bytes()
    before_core=BASE_CORE.read_bytes()
    try:
        v24.main()
        built_wcc=WCC.read_bytes()
        if built_wcc==before_wcc and digest(built_wcc)=="31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80":
            raise RuntimeError("WCC appears to be old installed ABI")
        shutil.copyfile(WCC,WCC_COPY)
        origin=base.RESULT/"brcmfmac-2012-escan-generation-v24.ko"
        dest=base.RESULT/"brcmfmac-2012-escan-gate-v25.ko"
        if dest.exists():raise RuntimeError("V25 output collision")
        origin.rename(dest)
        report=base.RESULT/"offline-build-result.json"
        rec=json.loads(report.read_text())
        rec.update({
            "test":"V25_SCAN_REQUEST_REJECT_INSTRUMENTATION_ONLY",
            "artifact_name":dest.name,
            "module_sha256":digest(dest.read_bytes()),
            "module_bytes":len(dest.read_bytes()),
            "matched_wcc_name":WCC_COPY.name,
            "matched_wcc_sha256":digest(WCC_COPY.read_bytes()),
            "matched_wcc_bytes":len(WCC_COPY.read_bytes()),
            "policy_changes":False,
            "firmware_modified":False,
            "scan_result":"NO_PHYSICAL_TEST_YET",
            "production_patch":False,
        })
        report.write_text(json.dumps(rec,indent=2)+"\n")
        print("V25_ABI_MATCHED_OFFLINE_PASS")
        print(json.dumps(rec,indent=2))
    finally:
        WCC.write_bytes(before_wcc)
        if digest(WCC.read_bytes())!=digest(before_wcc):
            raise RuntimeError("CRITICAL WCC HOST ARTIFACT RESTORE FAILED")
        if BASE_CORE.read_bytes()!=before_core:
            raise RuntimeError("CRITICAL CORE HOST ARTIFACT RESTORE FAILED")

if __name__=="__main__":
    main()
