#!/usr/bin/env python3
"""V26 transitional lab ONLY: no stale NO_IR requirement after beacon hint.

V25 numeric scan-gate logging retained; the ONLY behavioral change is removing
the lab guard's requirement that ch36 still be tagged NO_IR. The scan must
still have one ch36 (5180 MHz), no SSIDs/IE, and never disabled/radar.
The existing lab passive-only setting stays for this final controlled
two-generation experiment; do not ship it as a production scan policy.
Uses source restoring exact-ABI core/WCC build; no on-device action.
"""
import importlib.util,json
from pathlib import Path
PREV=Path(__file__).with_name("build_mz600_v25_scan_gate_diagnostic.py")
spec=importlib.util.spec_from_file_location("v25_gate_diag",PREV)
v25=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v25)
base=v25.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v26-20261027"
previous_scan=base.instrument
previous_event=base.instrument_fweh

def instrument_scan(original):
    c=previous_scan(original).replace("MZ600_V25_","MZ600_V26_")
    # NO_IR may be legitimately cleared by cfg80211's beacon hint after the
    # first scan. Never require it in the *private* lab guard.
    needle="\t\t    !(ch->flags & IEEE80211_CHAN_NO_IR) ||\n"
    if c.count(needle)!=1:
        raise RuntimeError("expected a single legacy NO_IR check")
    c=c.replace(needle,"",1)
    return c

def instrument_event(original):
    return previous_event(original).replace("MZ600_V25_","MZ600_V26_")

base.instrument=instrument_scan
base.instrument_fweh=instrument_event

def main():
    v25.main()
    result=base.RESULT
    old=result/"brcmfmac-2012-escan-gate-v25.ko"
    new=result/"brcmfmac-2012-escan-regstate-v26.ko"
    oldw=result/"brcmfmac-wcc-matched-v25.ko"
    neww=result/"brcmfmac-wcc-matched-v26.ko"
    if new.exists() or neww.exists():
        raise RuntimeError("refuse V26 artifact overwrite")
    old.rename(new)
    oldw.rename(neww)
    report=result/"offline-build-result.json"
    d=json.loads(report.read_text())
    d.update({
        "test":"V26_TWO_GENERATION_TEST_NO_STALE_NO_IR_ASSUMPTION",
        "artifact_name":new.name,
        "matched_wcc_name":neww.name,
        "module_sha256":v25.digest(new.read_bytes()),
        "module_bytes":len(new.read_bytes()),
        "matched_wcc_sha256":v25.digest(neww.read_bytes()),
        "matched_wcc_bytes":len(neww.read_bytes()),
        "no_ir_flag_mutated":False,
        "no_ir_ever_required_at_scan_guard":False,
        "remaining_lab_scope":"ch36 frequency5180, one channel, no SSID/IE, non-disabled/non-radar, forced passive scan",
        "future_production_policy":"remove all hardcoded private lab gate and forced passive setting; use Linux cfg80211 regulatory and standard Wi-Fi connection",
        "physical_result":"NOT_TESTED",
        "production_patch":False,
    })
    report.write_text(json.dumps(d,indent=2)+"\n")
    print("V26_OFFLINE_EXACT_ABI_PAIR_PASS",d["module_sha256"],d["matched_wcc_sha256"])

if __name__=="__main__":main()
