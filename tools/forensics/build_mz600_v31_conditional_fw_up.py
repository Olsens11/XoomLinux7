#!/usr/bin/env python3
"""Lab-only BCM4329 firmware-UP check immediately before ordinary ESCAN."""
import importlib.util
import json
from pathlib import Path

prev = Path(__file__).with_name("build_mz600_v30_firmware_up_mpc_observation.py")
spec = importlib.util.spec_from_file_location("v30_up_probe", prev)
v30 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v30)
base = v30.base
base.RESULT = base.ROOT / "v064-2012-oem-escan-v31-conditional-up-20261027"
v30.v29.v28.v26.v25.WCC_COPY = base.RESULT / "brcmfmac-wcc-matched-v25.ko"
prior = base.instrument
prior_fweh = base.instrument_fweh


def instrument_scan(original):
    c = prior(original)
    before = '''\tbrcmf_scan_config_mpc(ifp, 0);
\tmz600_v30_read_fw_state(ifp, "after_mpc0");
\tresults = (struct brcmf_scan_results *)cfg->escan_info.escan_buf;'''
    after = r'''\tbrcmf_scan_config_mpc(ifp, 0);
\tmz600_v30_read_fw_state(ifp, "after_mpc0");
\tif (ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID &&
\t    ifp->ifidx == 0 && ifp->bsscfgidx == 0 && ifp->vif &&
\t    ifp->vif->wdev.iftype == NL80211_IFTYPE_STATION) {
\t\tu32 up = ~0U;
\t\ts32 rc = brcmf_fil_cmd_int_get(ifp, 162, &up);

\t\tbrcmf_info("MZ600_V31_UP_BEFORE_SCAN rc=%d up=%u\n",
\t\t\t   rc, rc ? ~0U : up);
\t\tif (rc || up > 1) {
\t\t\terr = rc ? rc : -EIO;
\t\t\tgoto v31_fail;
\t\t}
\t\tif (!up) {
\t\t\trc = brcmf_fil_cmd_int_set(ifp, BRCMF_C_UP, 1);
\t\t\tbrcmf_info("MZ600_V31_WLC_UP sent=1 rc=%d\n", rc);
\t\t\tif (rc) {
\t\t\t\terr = rc;
\t\t\t\tgoto v31_fail;
\t\t\t}
\t\t\trc = brcmf_fil_cmd_int_get(ifp, 162, &up);
\t\t\tbrcmf_info("MZ600_V31_UP_AFTER_RECOVERY rc=%d up=%u\n",
\t\t\t\t   rc, rc ? ~0U : up);
\t\t\tif (rc || up != 1) {
\t\t\t\terr = rc ? rc : -EIO;
\t\t\t\tgoto v31_fail;
\t\t\t}
\t\t} else {
\t\t\tbrcmf_info("MZ600_V31_WLC_UP sent=0 rc=0\n");
\t\t}
\t}
\tresults = (struct brcmf_scan_results *)cfg->escan_info.escan_buf;'''
    after = after.replace(r'\t', '\t')
    if c.count(before) != 1:
        raise RuntimeError("V30 MPC site mismatch")
    c = c.replace(before, after, 1)
    exit_before = '''\tmz600_v30_read_fw_state(ifp, "after_escan_set");
\tif (err) {
\t\tbrcmf_scan_config_mpc(ifp, 1);
\t\tmz600_v30_read_fw_state(ifp, "after_error_mpc1");
\t}
\treturn err;'''
    exit_after = '''\tmz600_v30_read_fw_state(ifp, "after_escan_set");
\tif (err) {
\t\tbrcmf_scan_config_mpc(ifp, 1);
\t\tmz600_v30_read_fw_state(ifp, "after_error_mpc1");
\t}
\treturn err;

v31_fail:
\tbrcmf_scan_config_mpc(ifp, 1);
\tmz600_v30_read_fw_state(ifp, "after_wlc_up_failure");
\treturn err;'''
    if c.count(exit_before) != 1:
        raise RuntimeError("V30 exit site mismatch")
    c = c.replace(exit_before, exit_after, 1)
    return c.replace("MZ600_V30_", "MZ600_V31_")


def instrument_fweh(original):
    return prior_fweh(original).replace("MZ600_V30_", "MZ600_V31_")


base.instrument = instrument_scan
base.instrument_fweh = instrument_fweh


def main():
    if base.RESULT.exists():
        raise RuntimeError("V31 result exists: refuse overwrite")
    v30.main()
    out = base.RESULT
    core = out / "brcmfmac-2012-escan-conditional-up-v31.ko"
    wcc = out / "brcmfmac-wcc-matched-v31.ko"
    (out / "brcmfmac-2012-escan-state-v30.ko").rename(core)
    (out / "brcmfmac-wcc-matched-v30.ko").rename(wcc)
    report = out / "offline-build-result.json"
    meta = json.loads(report.read_text())
    meta.update(
        test="V31_BCM4329_CONDITIONAL_WLC_UP",
        module_name=core.name, artifact_name=core.name,
        module_bytes=core.stat().st_size,
        module_sha256=base.sha(core.read_bytes()),
        matched_wcc_name=wcc.name,
        matched_wcc_bytes=wcc.stat().st_size,
        matched_wcc_sha256=base.sha(wcc.read_bytes()),
        scan_policy_changed=False,
        firmware_write="BRCMF_C_UP only on confirmed DOWN primary BCM4329 station",
        physical_test="NOT_RUN", upstream_patch=False)
    report.write_text(json.dumps(meta, indent=2) + "\n")
    print("V31_LAB_OFFLINE_BUILD_PASS")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
