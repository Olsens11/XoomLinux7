#!/usr/bin/env python3
"""V27 LAB ONLY: log negative Broadcom ESCAN firmware RC, source-restoring."""
import hashlib,importlib.util,json
from pathlib import Path

PREV=Path(__file__).with_name("build_mz600_v26_transitional_passive_scan.py")
spec=importlib.util.spec_from_file_location("mz600_v26",PREV)
v26=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v26)
base=v26.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v27-20261027"
v26.v25.WCC_COPY=base.RESULT/"brcmfmac-wcc-matched-v25.ko"
FWIL=base.M/"fwil.c"
FWIL_SHA="1ba05bb9a089f6da2e7cdc863473c6168e2443e5c97d9e4906a94bde8bb202a9"
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    raw=FWIL.read_bytes()
    if sha(raw)!=FWIL_SHA or base.RESULT.exists():
        raise RuntimeError("STOP: fwil.c source mismatch or V27 output exists")
    c=raw.decode()
    anchor='''\t} else if (fwerr < 0) {
\t\tbrcmf_dbg(FIL, "Firmware error: %s (%d)\\n",
\t\t\t  brcmf_fil_get_errstr((u32)(-fwerr)), fwerr);
\t\terr = -EBADE;'''
    replacement='''\t} else if (fwerr < 0) {
\t\t/* V27 numerical-only diagnostic, specific to ESCAN iovar. */
\t\tif (set && cmd == BRCMF_C_SET_VAR && data &&
\t\t    len >= 6 && !memcmp(data, "escan", 6))
\t\t\tbrcmf_info("MZ600_V27_ESCAN_FWERR fwerr=%d generic_errno=%d\\n",
\t\t\t\t   fwerr, -EBADE);
\t\tbrcmf_dbg(FIL, "Firmware error: %s (%d)\\n",
\t\t\t  brcmf_fil_get_errstr((u32)(-fwerr)), fwerr);
\t\terr = -EBADE;'''
    if c.count(anchor)!=1:raise RuntimeError("STOP: firmware-error anchor differs")
    try:
        FWIL.write_text(c.replace(anchor,replacement,1))
        v26.main()
    finally:
        FWIL.write_bytes(raw)
        if FWIL.read_bytes()!=raw:
            raise RuntimeError("CRITICAL fwil.c restoration failed")
    out=base.RESULT
    oldcore=out/"brcmfmac-2012-escan-regstate-v26.ko"
    oldwcc=out/"brcmfmac-wcc-matched-v26.ko"
    core=out/"brcmfmac-2012-escan-fwerr-v27.ko"
    wcc=out/"brcmfmac-wcc-matched-v27.ko"
    if core.exists() or wcc.exists():raise RuntimeError("Refuse V27 overwrite")
    oldcore.rename(core);oldwcc.rename(wcc)
    r=out/"offline-build-result.json";d=json.loads(r.read_text())
    d.update(test="V27_NUMERIC_ESCAN_FIRMWARE_ERROR_ONLY",
        artifact_name=core.name,module_sha256=sha(core.read_bytes()),
        module_bytes=core.stat().st_size,matched_wcc_name=wcc.name,
        matched_wcc_sha256=sha(wcc.read_bytes()),matched_wcc_bytes=wcc.stat().st_size,
        fwil_original_sha256=FWIL_SHA,firmware_modified=False,
        radio_policy_changed=False,physical_result="NOT_TESTED",upstream_patch=False)
    r.write_text(json.dumps(d,indent=2)+"\n")
    print("V27_OFFLINE_BUILD_PASS",d["module_sha256"],d["matched_wcc_sha256"])
if __name__=="__main__": main()
