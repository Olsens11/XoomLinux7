#!/usr/bin/env python3
"""V23 LAB ONLY: change *host ESCAN request* sync_id, then read real terminal echo.

Uses exact source-restoring V22b diagnostic + physically tested V21 owner
dispatch. Does not modify chip firmware, firmware files or permanent kernel.
Read-only module parameter limits value selection to load time. Target scope:
BCM4329 only; other chips retain original constant 0x1234.
"""
import importlib.util
import json
from pathlib import Path

PREV=Path(__file__).with_name("build_mz600_v22_terminal_sync_id_readback.py")
spec=importlib.util.spec_from_file_location("v22b_builder",PREV)
v22=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v22)

base=v22.v21.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v23-20261027"
prior_scan=base.instrument
prior_event=base.instrument_fweh

def instrument_scan(original):
    c=prior_scan(original).replace("MZ600_V22_","MZ600_V23_")
    anchor="#define BRCMF_SCAN_IE_LEN_MAX\t\t2048"
    c=base.replace_once(c,anchor,r'''\
/* V23 lab parameter: vary the existing request's 16-bit sync_id only. */
static ushort mz600_v23_request_sync_id = 0x1234;
module_param_named(mz600_request_sync_id, mz600_v23_request_sync_id, ushort, 0444);
MODULE_PARM_DESC(mz600_request_sync_id, "LAB ONLY: BCM4329 ESCAN request sync ID");

#define BRCMF_SCAN_IE_LEN_MAX		2048'''.lstrip("\\"))
    anchor="\tparams->sync_id = cpu_to_le16(0x1234);"
    c=base.replace_once(c,anchor,r'''\
	/*
	 * Probe only: no change on generic chips and no new scan semantics.
	 * The returned ID is read separately from the true firmware terminal.
	 */
	if (ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID) {
		params->sync_id = cpu_to_le16(READ_ONCE(mz600_v23_request_sync_id));
		brcmf_info("MZ600_V23_SCAN_REQUEST_SYNC id=%u\n",
			   READ_ONCE(mz600_v23_request_sync_id));
	} else {
		params->sync_id = cpu_to_le16(0x1234);
	}'''.lstrip("\\"))
    return c

def instrument_event(original):
    c=prior_event(original).replace("MZ600_V22_","MZ600_V23_")
    # With variable request sync_id, do not claim the old 0x1234 is expected.
    anchor=" expected_request_sync_id=4660"
    if c.count(anchor)!=1:
        raise RuntimeError("Unexpected V22 numeric logger anchor")
    c=c.replace(anchor,"",1)
    return c

base.instrument=instrument_scan
base.instrument_fweh=instrument_event

def main():
    v22.main()
    directory=base.RESULT
    existing=directory/"brcmfmac-2012-escan-terminal-sync-v22.ko"
    output=directory/"brcmfmac-2012-escan-variable-sync-v23.ko"
    if output.exists():
        raise RuntimeError("Refuse overwrite existing V23")
    existing.rename(output)
    receipt=directory/"offline-build-result.json"
    state=json.loads(receipt.read_text())
    state.update({
        "test":"V23_FIRMWARE_ECHO_NONDEFAULT_HOST_ESCAN_SYNC_IDS",
        "artifact_name":output.name,
        "lab_parameter":"mz600_request_sync_id=4661|4662",
        "terminal_owner_switch":"mz600_terminal_owner=1",
        "firmware_modified":False,
        "scan_request_modified":"only existing sync_id field on BCM4329",
        "physical_result":"NOT_TESTED",
        "production_patch":False,
    })
    receipt.write_text(json.dumps(state,indent=2)+"\n")
    print("V23_OFFLINE_EXACT_ABI_COMPILED_NO_DEVICE_TEST",output)

if __name__=="__main__":
    main()
