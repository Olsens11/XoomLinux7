#!/usr/bin/env python3
"""V27 lab: remove *all* temporary scan-policy constraints, preserve cfg80211.

Retain source-restoring exact-ABI V26b Event69/scan-generation experiment.
Replace only the BCM4329 legacy valid-channel fallback with a normal
hw-supported channel list (no blanket NO_IR). Retain DFS/RADAR+NO_IR
and narrow 20MHz hardware limitations; cfg80211/regdb remains authoritative.
No firmware, NVRAM, regulatory flag *runtime override*, or device action.
"""
import difflib
import hashlib
import json
import importlib.util
import subprocess
import tempfile
from pathlib import Path

PREV=Path(__file__).with_name("build_mz600_v26_transitional_passive_scan.py")
spec=importlib.util.spec_from_file_location("v26b_builder",PREV)
v26=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v26)
base=v26.base
base.RESULT=base.ROOT/"v064-2012-oem-escan-v27-normal-20261027"
v26.v25.WCC_COPY=base.RESULT/"brcmfmac-wcc-matched-v25.ko"
earlier_scan=base.instrument
earlier_event=base.instrument_fweh

def instrument_scan(original):
    c=earlier_scan(original)
    # Eliminate extra local channel36, zero-SSID/IE, hardcoded passive gate,
    # and BRCMF_C_SET_PASSIVE_SCAN=1 command. Allow normal cfg80211 requests.
    begin="\t/* V20 controlled single-channel NO_IR PASSIVE diagnostic. */\n"
    end="\tif (test_bit(BRCMF_SCAN_STATUS_BUSY, &cfg->scan_status))"
    if c.count(begin)!=1:
        raise RuntimeError("STOP: old V20 lab-only scan gate anchor changed")
    start=c.index(begin)
    stop=c.index(end,start)
    if "BRCMF_C_SET_PASSIVE_SCAN" not in c[start:stop] or "5180" not in c[start:stop]:
        raise RuntimeError("STOP: gate content differs, manual audit required")
    c=c[:start]+c[stop:]

    # Drop V20 lab dwell override. Let normal driver populate scan parameters
    # from userspace requests/firmware defaults. Avoid arbitrary 500ms policy.
    begin="\tif (cfg->pub->bus_if->chip == BRCM_CC_4329_CHIP_ID &&\n"
    end="\tparams_le->length = cpu_to_le16(length);\n\t/* Adding mask to channel numbers */"
    if c.count(begin)!=1:
        raise RuntimeError("STOP: V20 dwell anchor changed")
    start=c.index(begin)
    stop=c.index(end,start)
    if "passive_time = cpu_to_le32(500)" not in c[start:stop]:
        raise RuntimeError("STOP: different dwell control")
    c=c[:start]+c[stop:]

    # V25 diagnostic was inserted inside the removed V20 gate, so remove
    # stale label claims too; preserve remaining Event69/firmware diagnostics.
    if "MZ600_V26_SCAN_GATE_PASS" in c or "MZ600_V26_GLOBAL_PASSIVE_RC" in c:
        raise RuntimeError("STOP: partial old passive code still present")
    c=c.replace("MZ600_V26_","MZ600_V27_")

    # The old lab log assumed an explicit first channel on every scan.
    # Read only channel count and scan_type, valid for a full-band request.
    anchor='''\t\tif (ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID)
\t\t\tbrcmf_info("MZ600_V27_V1_CH36_WIRE chanspec=0x%04x passive_ms=%d scan_type=%u nprobes=%d nchans=%u\\n",
\t\t\t    le16_to_cpu(params_v1->params_le.channel_list[0]),
\t\t\t    le32_to_cpu(params_v1->params_le.passive_time),
\t\t\t    params_v1->params_le.scan_type,
\t\t\t    le32_to_cpu(params_v1->params_le.nprobes),
\t\t\t    le32_to_cpu(params_v1->params_le.channel_num));'''
    repl='''\t\tif (ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID)
\t\t\tbrcmf_info("MZ600_V27_NORMAL_SCAN_WIRE passive_ms=%d scan_type=%u nprobes=%d channel_num=0x%x\\n",
\t\t\t    le32_to_cpu(params_v1->params_le.passive_time),
\t\t\t    params_v1->params_le.scan_type,
\t\t\t    le32_to_cpu(params_v1->params_le.nprobes),
\t\t\t    le32_to_cpu(params_v1->params_le.channel_num));'''
    if c.count(anchor)!=1:
        raise RuntimeError("STOP: V1 logger anchor mismatch")
    c=c.replace(anchor,repl,1)
    return c

def instrument_event(original):
    return earlier_event(original).replace("MZ600_V26_","MZ600_V27_")

base.instrument=instrument_scan
base.instrument_fweh=instrument_event

def make_patch(path):
    original=base.SOURCE.read_text()
    if base.sha(original.encode())!=base.SOURCE_SHA:
        raise RuntimeError("STOP: original source checksum changed")
    with tempfile.TemporaryDirectory(prefix="mz600-v27-src-") as tmp:
        tree=Path(tmp)
        rel=base.SOURCE.relative_to(base.LINUX)
        dest=tree/rel
        dest.parent.mkdir(parents=True)
        dest.write_text(original)
        subprocess.run(["patch","--batch","--forward","-p1",
                        "-i",str(base.PATCH)],cwd=tree,check=True,
                       stdout=subprocess.DEVNULL)
        patched=dest.read_text()
    # The original fallback restricted every supported channel to NO_IR.
    # Restore normal channel capability while preserving hw 20MHz limit.
    old='''\t\t\t\tchannel->flags = channel->orig_flags |
\t\t\t\t\tIEEE80211_CHAN_NO_IR |
\t\t\t\t\tIEEE80211_CHAN_NO_HT40 |'''
    new='''\t\t\t\tchannel->flags = channel->orig_flags |
\t\t\t\t\tIEEE80211_CHAN_NO_HT40 |'''
    if patched.count(old)!=1:
        raise RuntimeError("STOP: existing legacy-channel fallback differs")
    patched=patched.replace(old,new,1)
    # Existing DFS/radar handling is retained and conservatively denies
    # IR where CAC/offload has not yet been proven.
    old='''\t\t\t\t\tchannel->flags |= IEEE80211_CHAN_RADAR;'''
    new='''\t\t\t\t\tchannel->flags |= IEEE80211_CHAN_RADAR |
\t\t\t\t\t\tIEEE80211_CHAN_NO_IR;'''
    if patched.count(old)!=1:
        raise RuntimeError("STOP: missing legacy DFS flag anchor")
    patched=patched.replace(old,new,1)
    # Replace misleading diagnostic claim, without changing firmware/regdb.
    patched=base.replace_once(
        patched,
        'no_ir=1 ht20_only=1',
        'regdb_enforced=1 ht20_only=1')
    if "MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK" in patched:
        patched=patched.replace("MZ600_5G_LEGACY_PASSIVE_ONLY_FALLBACK",
                                "MZ600_5G_LEGACY_VALID_CHANNEL_FALLBACK",1)
    diff="".join(difflib.unified_diff(
        original.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile="a/"+str(rel),tofile="b/"+str(rel)))
    if not diff:
        raise RuntimeError("STOP: empty compatibility patch")
    path.write_text(diff)
    return base.sha(diff.encode())

def main():
    if base.RESULT.exists():
        raise RuntimeError("STOP: V27 output folder already exists")
    with tempfile.TemporaryDirectory(prefix="mz600-v27-patch-") as folder:
        patch=Path(folder)/"0005-brcmfmac-bcm4329-legacy-valid-channels-normal.patch"
        digest=make_patch(patch)
        base.PATCH=patch
        base.PATCH_SHA=digest
        v26.main()
    out=base.RESULT
    original_core=out/"brcmfmac-2012-escan-regstate-v26.ko"
    final_core=out/"brcmfmac-2012-escan-normal-v27.ko"
    original_wcc=out/"brcmfmac-wcc-matched-v26.ko"
    final_wcc=out/"brcmfmac-wcc-matched-v27.ko"
    if final_core.exists() or final_wcc.exists():
        raise RuntimeError("STOP: V27 target files exist")
    original_core.rename(final_core)
    original_wcc.rename(final_wcc)
    report=out/"offline-build-result.json"
    data=json.loads(report.read_text())
    data.update({
        "test":"V27_REMOVE_ALL_TEMPORARY_SCAN_POLICY_PRESERVE_REGDB",
        "artifact_name":final_core.name,
        "module_sha256":base.sha(final_core.read_bytes()),
        "module_bytes":final_core.stat().st_size,
        "matched_wcc_name":final_wcc.name,
        "matched_wcc_sha256":base.sha(final_wcc.read_bytes()),
        "matched_wcc_bytes":final_wcc.stat().st_size,
        "compatibility_patch_sha256":digest,
        "normal_cfg80211_scan_request":True,
        "force_passive_scan":False,
        "force_ch36":False,
        "force_500ms_dwell":False,
        "blanket_no_ir":False,
        "dfs_radar_protection_retained":True,
        "regulatory_policy_modified":False,
        "firmware_modified":False,
        "physical_test":"NOT_DONE",
        "production_patch":False,
        "note":"Legacy-channel valid-list fallback still lab review; upstream lifecycle gates open"
    })
    report.write_text(json.dumps(data,indent=2)+"\n")
    print("V27_OFFLINE_BUILD_PASS",json.dumps(data,indent=2))

if __name__=="__main__":
    main()
