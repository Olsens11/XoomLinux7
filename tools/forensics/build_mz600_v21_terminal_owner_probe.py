#!/usr/bin/env python3
"""V21 LAB ONLY: exact-ABI, source-restoring single-module Event69 terminal owner A/B.

Reuses the SHA-pinned V20 2012 firmware passive-only diagnostic, with one
parameter-controlled, off-by-default handler-routing experiment. Does not
alter on-chip firmware, device, calibration, production driver or repository
kernel sources at rest. Firmware/kernel physical testing is separate.
"""
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).with_name("build_mz600_v20_2012_5g_event_header_probe.py")
spec = importlib.util.spec_from_file_location("mz600_v20_source_builder", BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

old_scan = base.instrument
old_event = base.instrument_fweh
base.RESULT = base.ROOT / "v064-2012-oem-escan-v21-20261027"

def instrument_scan(original):
    return old_scan(original).replace("MZ600_V20_", "MZ600_V21_")

def instrument_event(original):
    c = old_event(original).replace("MZ600_V20_", "MZ600_V21_")
    c = base.replace_once(
        c, '#include <brcm_hw_ids.h>',
        '#include <linux/module.h>\n#include <brcm_hw_ids.h>')

    # Off by default, read-only after load. V20's mz600_extra_events=0 retained.
    anchor = 'struct brcmf_fweh_queue_item {'
    insertion = r'''/* TEMPORARY experiment; never promote without scan-generation review. */
static bool mz600_v21_terminal_owner;
module_param_named(mz600_terminal_owner, mz600_v21_terminal_owner, bool, 0444);
MODULE_PARM_DESC(mz600_terminal_owner,
    "LAB ONLY: route unmatched BCM4329 ESCAN SUCCESS to active single scan owner");

'''
    c = base.replace_once(c, anchor, insertion + anchor)
    anchor = '''\twhile ((event = brcmf_fweh_dequeue_event(fweh))) {
\t\tenum brcmf_fweh_event_code code;'''
    c = base.replace_once(c, anchor, '''\
\twhile ((event = brcmf_fweh_dequeue_event(fweh))) {
\t\tenum brcmf_fweh_event_code code;
\t\tstruct brcmf_if *mz600_scan_owner = NULL;''')

    anchor = '''\t\tif (event->emsg.bsscfgidx >= BRCMF_MAX_IFS) {'''
    c = base.replace_once(c, anchor, r'''\
\t\t/*
\t\t * LAB ONLY: the firmware's real ESCAN SUCCESS is already
\t\t * received and queued; normal interface routing sometimes fails.
\t\t * Never fabricate completion or reassign partial/other events.
\t\t * Reject P2P/multi-interface use; do not mutate event fields.
\t\t */
\t\tif (mz600_v21_terminal_owner &&
\t\t    drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID &&
\t\t    event->code == BRCMF_E_ESCAN_RESULT &&
\t\t    get_unaligned_be16(&event->emsg.version) == 2 &&
\t\t    get_unaligned_be32(&event->emsg.status) ==
\t\t\tBRCMF_E_STATUS_SUCCESS &&
\t\t    (event->emsg.bsscfgidx >= BRCMF_MAX_IFS ||
\t\t     !drvr->iflist[event->emsg.bsscfgidx])) {
\t\t\tstruct brcmf_cfg80211_info *cfg = drvr->config;
\t\t\tbool only_primary = true;
\t\t\tint n;

\t\t\tfor (n = 1; n < BRCMF_MAX_IFS; n++) {
\t\t\t\tif (drvr->iflist[n]) {
\t\t\t\t\tonly_primary = false;
\t\t\t\t\tbreak;
\t\t\t\t}
\t\t\t}
\t\t\tif (cfg && only_primary && list_is_singular(&cfg->vif_list) &&
\t\t\t    READ_ONCE(cfg->scan_request) &&
\t\t\t    !READ_ONCE(cfg->int_escan_map) &&
\t\t\t    test_bit(BRCMF_SCAN_STATUS_BUSY, &cfg->scan_status) &&
\t\t\t    cfg->escan_info.escan_state == WL_ESCAN_STATE_SCANNING &&
\t\t\t    cfg->escan_info.ifp == drvr->iflist[0] &&
\t\t\t    drvr->iflist[0] && drvr->iflist[0]->vif &&
\t\t\t    drvr->iflist[0]->ndev)
\t\t\t\tmz600_scan_owner = drvr->iflist[0];

\t\t\tbrcmf_info("MZ600_V21_TERMINAL_OWNER_CHECK raw_bsscfg=%u eligible=%u owner_mode=%u\n",
\t\t\t\t   event->emsg.bsscfgidx, !!mz600_scan_owner,
\t\t\t\t   mz600_v21_terminal_owner);
\t\t}
\t\tif (event->emsg.bsscfgidx >= BRCMF_MAX_IFS &&
\t\t    !mz600_scan_owner) {'''.replace(r'\t','\t').lstrip('\\'))

    anchor = '''\t\tif (event->code == BRCMF_E_TDLS_PEER_EVENT)
\t\t\tifp = drvr->iflist[0];
\t\telse
\t\t\tifp = drvr->iflist[emsg.bsscfgidx];'''
    c = base.replace_once(c, anchor, '''\
\t\tif (mz600_scan_owner)
\t\t\tifp = mz600_scan_owner;
\t\telse if (event->code == BRCMF_E_TDLS_PEER_EVENT)
\t\t\tifp = drvr->iflist[0];
\t\telse
\t\t\tifp = drvr->iflist[emsg.bsscfgidx];
\t\tif (mz600_scan_owner)
\t\t\tbrcmf_info("MZ600_V21_TERMINAL_OWNER_DELIVER status=%u raw_bsscfg=%u\\n",
\t\t\t\t   emsg.status, emsg.bsscfgidx);''')
    return c

base.instrument = instrument_scan
base.instrument_fweh = instrument_event

def main():
    base.main()
    former = base.RESULT / "brcmfmac-2012-escan-event69-v20.ko"
    final = base.RESULT / "brcmfmac-2012-escan-terminal-owner-v21.ko"
    if final.exists():
        raise RuntimeError("V21 artifact already present, refuse overwrite")
    former.rename(final)
    report = base.RESULT / "offline-build-result.json"
    data = json.loads(report.read_text())
    data.update({
        "test": "V21_BCM4329_TERMINAL_OWNER_DEFAULT_OFF_AB_MODULE",
        "artifact_name": final.name,
        "switch": "mz600_terminal_owner=0|1",
        "physical_evidence": "NOT_YET_TESTED",
        "production_patch": False,
    })
    report.write_text(json.dumps(data, indent=2) + "\n")
    print("V21_EXACT_ABI_OFFLINE_ARTIFACT_PASS", final)

if __name__ == "__main__":
    main()
