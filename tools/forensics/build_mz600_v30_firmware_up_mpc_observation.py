#!/usr/bin/env python3
"""V30 LAB ONLY: read-only firmware UP/MPC snapshots around normal ESCAN.

Derives exact-ABI, source-restoring V29 *regulatory-preserving* normal-scan
experiment. No chip-state changes beyond those ALREADY made by the driver.
The added commands are reads (WLC_GET_UP=162 and mpc get); log their errors
instead of assuming the 2012 firmware supports both. Matched WCC is retained.
The baseline brcmfmac scan completion/owner/generation logic is untouched.
"""
import importlib.util
import json
from pathlib import Path

PREV=Path(__file__).with_name("build_mz600_v29_regulatory_preserving_native_scan.py")
spec=importlib.util.spec_from_file_location("mz600_v29_regsafe",PREV)
v29=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v29)
base=v29.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v30-state-observe-20261027"
v29.v28.v26.v25.WCC_COPY=base.RESULT/"brcmfmac-wcc-matched-v25.ko"
previous_scan=base.instrument
previous_fweh=base.instrument_fweh

def instrument_scan(original):
    c=previous_scan(original)
    # This diagnostic reads only existing firmware state, no resets, new
    # writes, event subscriptions, RF policy or cfg80211 callbacks.
    insertion=r'''/* Lab-only BCM4329 controller/BSS readiness measurements.
 * WLC_GET_UP (162) is defined in older Broadcom wlioctl.h. An unsupported
 * command is recorded as such; host READY and firmware UP are distinct.
 */
static void mz600_v30_read_fw_state(struct brcmf_if *ifp, const char *where)
{
	struct brcmf_cfg80211_info *cfg;
	u32 fw_up = ~0U, mpc = ~0U;
	s32 fw_rc, mpc_rc;
	bool host_ready, netdev_running;

	if (!ifp || ifp->drvr->bus_if->chip != BRCM_CC_4329_CHIP_ID)
		return;

	cfg = ifp->drvr->config;
	host_ready = ifp->vif && check_vif_up(ifp->vif);
	netdev_running = ifp->ndev && netif_running(ifp->ndev);
	fw_rc = brcmf_fil_cmd_int_get(ifp, 162, &fw_up);
	mpc_rc = brcmf_fil_iovar_int_get(ifp, "mpc", &mpc);
	brcmf_info("MZ600_V30_FW_STATE site=%s get_up_rc=%d fw_up=%u get_mpc_rc=%d mpc=%u host_ready=%u netdev_running=%u scan_busy=%u\n",
		   where, fw_rc, fw_rc ? 0xffffffffU : fw_up,
		   mpc_rc, mpc_rc ? 0xffffffffU : mpc,
		   host_ready, netdev_running,
		   cfg && test_bit(BRCMF_SCAN_STATUS_BUSY, &cfg->scan_status));
}

'''
    anchor="static void brcmf_scan_config_mpc(struct brcmf_if *ifp, int mpc)"
    c=base.replace_once(c,anchor,insertion+anchor)
    # Only measure the actual existing MPC SET command outcome; do not
    # change its existing return/READY behavior.
    anchor='''\t\terr = brcmf_fil_iovar_int_set(ifp, "mpc", mpc);
\t\tif (err) {'''
    c=base.replace_once(c,anchor,'''\
		err = brcmf_fil_iovar_int_set(ifp, "mpc", mpc);
		if (ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID)
			brcmf_info("MZ600_V30_MPC_SET value=%d rc=%d\n", mpc, err);
		if (err) {''')
    # Caller traces: actual scan entry, MPC before/after, firmware request.
    anchor='''\tescan->escan_state = WL_ESCAN_STATE_SCANNING;'''
    c=base.replace_once(c,anchor,'''\
	escan->escan_state = WL_ESCAN_STATE_SCANNING;
	mz600_v30_read_fw_state(ifp, "before_scan");''')
    anchor='''\tbrcmf_scan_config_mpc(ifp, 0);
\tresults = (struct brcmf_scan_results *)cfg->escan_info.escan_buf;'''
    c=base.replace_once(c,anchor,'''\
	brcmf_scan_config_mpc(ifp, 0);
	mz600_v30_read_fw_state(ifp, "after_mpc0");
	results = (struct brcmf_scan_results *)cfg->escan_info.escan_buf;''')
    anchor='''\terr = escan->run(cfg, ifp, request);
\tif (err)
\t\tbrcmf_scan_config_mpc(ifp, 1);
\treturn err;'''
    c=base.replace_once(c,anchor,'''\
	err = escan->run(cfg, ifp, request);
	mz600_v30_read_fw_state(ifp, "after_escan_set");
	if (err) {
		brcmf_scan_config_mpc(ifp, 1);
		mz600_v30_read_fw_state(ifp, "after_error_mpc1");
	}
	return err;''')
    # Completion must remain real: report before/after normal existing MPC=1.
    anchor='''\tbrcmf_scan_config_mpc(ifp, 1);

\t/*
\t * e-scan can be initiated internally'''
    c=base.replace_once(c,anchor,'''\
	mz600_v30_read_fw_state(ifp, "completion_before_mpc1");
	brcmf_scan_config_mpc(ifp, 1);
	mz600_v30_read_fw_state(ifp, "completion_after_mpc1");

	/*
	 * e-scan can be initiated internally''')
    return c.replace("MZ600_V29_","MZ600_V30_")

def instrument_fweh(original):
    return previous_fweh(original).replace("MZ600_V29_","MZ600_V30_")

base.instrument=instrument_scan
base.instrument_fweh=instrument_fweh

def main():
    if base.RESULT.exists():
        raise RuntimeError("STOP: V30 output exists; do not overwrite")
    v29.main()
    out=base.RESULT
    oldcore=out/"brcmfmac-2012-escan-regsafe-v29.ko"
    newcore=out/"brcmfmac-2012-escan-state-v30.ko"
    oldwcc=out/"brcmfmac-wcc-matched-v29.ko"
    newwcc=out/"brcmfmac-wcc-matched-v30.ko"
    if newcore.exists() or newwcc.exists():
        raise RuntimeError("STOP: V30 artifact collision")
    oldcore.rename(newcore)
    oldwcc.rename(newwcc)
    report=out/"offline-build-result.json"
    d=json.loads(report.read_text())
    d.update({
        "test":"V30_REAL_WLC_GET_UP_AND_MPC_READS_AT_SCAN_BOUNDARIES",
        "artifact_name":newcore.name,
        "module_name":newcore.name,
        "module_bytes":newcore.stat().st_size,
        "module_sha256":base.sha(newcore.read_bytes()),
        "matched_wcc_name":newwcc.name,
        "matched_wcc_bytes":newwcc.stat().st_size,
        "matched_wcc_sha256":base.sha(newwcc.read_bytes()),
        "modifications":"read-only controller-UP/MPC probes and log original MPC SET result",
        "rf_scan_policy_changed":False,
        "regulatory_policy_changed":False,
        "mpc_or_up_writes_added":False,
        "event_routing_or_scan_completion_changed":False,
        "on_device_test":"NOT_RUN",
        "upstream_patch":False,
    })
    report.write_text(json.dumps(d,indent=2)+"\n")
    print("V30_READONLY_FW_UP_MPC_OFFLINE_ARM_BUILD_PASS")
    print(json.dumps(d,indent=2))

if __name__=="__main__":
    main()
