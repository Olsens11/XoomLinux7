#!/usr/bin/env python3
"""V24 LAB prototype: distinct request IDs per scan, guarded Event69 delivery.

Extends V23's tested source-restoring builder. Adds two tiny per-device
fields to cfg80211.h for experimental generation state. A finally block
restores the exact pre-build header bytes even if compilation fails.
Experimental module parameter defaults OFF. No firmware, flash, or RF here.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

PREV = Path(__file__).with_name("build_mz600_v23_variable_scan_sync_id.py")
spec = importlib.util.spec_from_file_location("mz600_v23_builder", PREV)
v23 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v23)
base = v23.base
base.RESULT = base.ROOT / "v064-2012-oem-escan-v24-20261027"
HEADER = base.M / "cfg80211.h"
HEADER_SHA = "89031854e21941889ca07315f693c53ef0b61b94c022bce5743cc204e003735e"
old_scan = base.instrument
old_event = base.instrument_fweh

def instrument_header(original):
    anchor = "\tu32 escan_state;\n\tu8 *escan_buf;"
    return base.replace_once(original, anchor,
        "\tu32 escan_state;\n"
        "\t/* V24 lab-only: active request generation, per adapter. */\n"
        "\tu16 mz600_sync_next;\n"
        "\tu16 mz600_sync_active;\n"
        "\tbool mz600_generation_enabled;\n"
        "\tu8 *escan_buf;")

def instrument_scan(original):
    c = old_scan(original).replace("MZ600_V23_", "MZ600_V24_")
    anchor = "#define BRCMF_SCAN_IE_LEN_MAX"
    c = base.replace_once(c, anchor, r'''/* V24 LAB: generation check default OFF, no generic-chip changes. */
static bool mz600_v24_generation;
module_param_named(mz600_generation, mz600_v24_generation, bool, 0444);
MODULE_PARM_DESC(mz600_generation, "LAB ONLY: rotate BCM4329 ESCAN sync id per scan");

#define BRCMF_SCAN_IE_LEN_MAX''')
    # New generation is assigned immediately before the firmware request.
    anchor = "\tescan->ifp = ifp;\n\tescan->wiphy = cfg->wiphy;"
    c = base.replace_once(c, anchor, r'''\
	if (mz600_v24_generation &&
	    ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID) {
		u16 id = READ_ONCE(escan->mz600_sync_next);
		id = id ? id + 1 : 0x1235;
		if (!id)
			id = 1;
		WRITE_ONCE(escan->mz600_sync_next, id);
		WRITE_ONCE(escan->mz600_sync_active, id);
		WRITE_ONCE(escan->mz600_generation_enabled, true);
		brcmf_info("MZ600_V24_NEW_SCAN_GENERATION id=%u\n", id);
	} else {
		WRITE_ONCE(escan->mz600_generation_enabled, false);
	}
	escan->ifp = ifp;
	escan->wiphy = cfg->wiphy;'''.lstrip("\\"))
    # V23's lab request field continues to work when generation mode is off.
    anchor = "params->sync_id = cpu_to_le16(READ_ONCE(mz600_v23_request_sync_id));"
    c = base.replace_once(c, anchor,
        "params->sync_id = cpu_to_le16("
        "mz600_v24_generation ? "
        "READ_ONCE(cfg->escan_info.mz600_sync_active) : "
        "READ_ONCE(mz600_v23_request_sync_id));")
    # Check the genuine terminal against the in-flight generation, even if
    # the firmware index happens to be valid. No separate scan_done path.
    anchor = "\tstatus = e->status;\n"
    insert = r'''\
	status = e->status;
	if (mz600_v24_generation &&
	    drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID &&
	    status == BRCMF_E_STATUS_SUCCESS) {
		u16 expected = READ_ONCE(cfg->escan_info.mz600_sync_active);
		u16 actual = 0;
		bool valid = e->datalen == 12 && data &&
			     READ_ONCE(cfg->escan_info.mz600_generation_enabled);
		if (valid)
			actual = get_unaligned_le16((u8 *)data + 8);
		if (!valid || !expected || actual != expected) {
			brcmf_info("MZ600_V24_STALE_TERMINAL_REJECT expected=%u actual=%u valid=%u\n",
				   expected, actual, valid);
			return 0;
		}
		brcmf_info("MZ600_V24_TERMINAL_GENERATION_ACCEPT id=%u\n", actual);
	}
'''.lstrip("\\")
    c = base.replace_once(c, anchor, insert)
    return c

def instrument_event(original):
    c = old_event(original).replace("MZ600_V23_", "MZ600_V24_")
    anchor = "cfg->escan_info.ifp == drvr->iflist[0] &&"
    c = base.replace_once(c, anchor, r'''\
cfg->escan_info.ifp == drvr->iflist[0] &&
			    /*
			     * Check wire transaction before bypassing the
			     * missing bsscfg interface; never change bytes.
			     */
			    (!READ_ONCE(cfg->escan_info.mz600_generation_enabled) ||
			     (event->datalen == 12 &&
			      READ_ONCE(cfg->escan_info.mz600_sync_active) &&
			      get_unaligned_le16(event->data + 8) ==
			      READ_ONCE(cfg->escan_info.mz600_sync_active))) &&'''.lstrip("\\"))
    return c

base.instrument = instrument_scan
base.instrument_fweh = instrument_event

def main():
    raw = HEADER.read_bytes()
    if hashlib.sha256(raw).hexdigest() != HEADER_SHA:
        raise RuntimeError("STOP: cfg80211.h baseline mismatch")
    if base.RESULT.exists():
        raise RuntimeError("STOP: V24 output already exists")
    patched = instrument_header(raw.decode("utf-8")).encode("utf-8")
    try:
        HEADER.write_bytes(patched)
        v23.main()
    finally:
        HEADER.write_bytes(raw)
        if HEADER.read_bytes() != raw:
            raise RuntimeError("STOP: cfg80211.h restoration failed")
    source = base.RESULT / "brcmfmac-2012-escan-variable-sync-v23.ko"
    destination = base.RESULT / "brcmfmac-2012-escan-generation-v24.ko"
    if destination.exists():
        raise RuntimeError("STOP: refusing V24 artifact overwrite")
    source.rename(destination)
    result = base.RESULT / "offline-build-result.json"
    receipt = json.loads(result.read_text())
    receipt.update({
        "test": "V24_PER_SCAN_GENERATION_AND_GENUINE_EVENT69_CHECK_LAB",
        "module_name": destination.name,
        "experiment_switch": "mz600_generation=0(default)|1",
        "default_behavior": "unchanged V23 lab",
        "firmware_modified": False,
        "physical_verification": "NOT_YET_TESTED",
        "race_safe_upstream_patch": False,
        "header_source_restored_sha256": HEADER_SHA,
    })
    result.write_text(json.dumps(receipt, indent=2) + "\n")
    print("V24_OFFLINE_BUILD_PASS",destination)

if __name__ == "__main__":
    main()
