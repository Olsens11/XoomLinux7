#!/usr/bin/env python3
"""Build a TEMPORARY BCM4329 2012 ESCAN diagnostic, with guaranteed source restoration.

Offline host only. Fails closed unless source, old lab patch and original module
match recorded checksums. No Xoom connection, firmware transfer, or RF operation.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025")
LINUX = ROOT / "v064-bigpart-linux"
OUT = ROOT / "v064-bigpart-debian-sdroot-build"
M = LINUX / "drivers/net/wireless/broadcom/brcm80211/brcmfmac"
SOURCE = M / "cfg80211.c"
KO = M / "brcmfmac.ko"
PATCH = ROOT / "v064-legacy-passive-only-wiphy-v5-20261026/0005-brcmfmac-bcm4329-legacy-valid-channel-passive-only-fallback.patch"
RESULT = ROOT / "v064-2012-oem-escan-v16-20261026"
COMPILER = Path("/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-")
SOURCE_SHA = "1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8"
PATCH_SHA = "9ef957fc8c8a8d4843e35666db8d71092d06c92a456d5d17d1521d2125b7575a"
ORIG_KO = "9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb"

def sha(buf):
    return hashlib.sha256(buf).hexdigest()

def run(*args, **kw):
    subprocess.run(args, check=True, **kw)

def replace_once(text, anchor, new):
    count=text.count(anchor)
    if count!=1:
        raise RuntimeError(f"expected unique source anchor (found {count}): {anchor[:90]!r}")
    return text.replace(anchor, new, 1)

def instrument(original):
    c=original
    # Actual brcmfmac scan() entry: fail closed before it takes ownership.
    anchor='''\tif (!check_vif_up(vif))
\t\treturn -EIO;

\tif (test_bit(BRCMF_SCAN_STATUS_BUSY, &cfg->scan_status))'''
    replacement='''\tif (!check_vif_up(vif))
\t\treturn -EIO;

\t/* V16 controlled single-channel NO_IR PASSIVE diagnostic. */
\tif (drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID) {
\t\tstruct ieee80211_channel *ch;

\t\tif (request->n_channels != 1 || request->n_ssids != 0 ||
\t\t    request->ie_len != 0)
\t\t\treturn -EPERM;
\t\tch = request->channels[0];
\t\tif (!ch || ch->center_freq != 5180 || ch->hw_value != 36 ||
\t\t    !(ch->flags & IEEE80211_CHAN_NO_IR) ||
\t\t    (ch->flags & (IEEE80211_CHAN_DISABLED |
\t\t\t\t IEEE80211_CHAN_RADAR)))
\t\t\treturn -EPERM;
\t\terr = brcmf_fil_cmd_int_set(vif->ifp,
\t\t\t\t\tBRCMF_C_SET_PASSIVE_SCAN, 1);
\t\tif (err) {
\t\t\tbrcmf_info("MZ600_V16_GLOBAL_PASSIVE_RC=%d\\n", err);
\t\t\treturn err;
\t\t}
\t\tbrcmf_info("MZ600_V16_SCAN_GATE_PASS channel=36 freq=5180 no_ir=1 nssid=0\\n");
\t}

\tif (test_bit(BRCMF_SCAN_STATUS_BUSY, &cfg->scan_status))'''
    c=replace_once(c,anchor,replacement)

    # Narrow, source-verified change: instead of the firmware-default -1,
    # use finite 500ms passive dwell for exactly the gated 5GHz ch36 case.
    # All other scan behavior is left unchanged.
    anchor='''\tparams_le->length = cpu_to_le16(length);
\t/* Adding mask to channel numbers */'''
    c=replace_once(c,anchor,'''\
\tif (cfg->pub->bus_if->chip == BRCM_CC_4329_CHIP_ID &&
\t    n_channels == 1 && n_ssids == 0 &&
\t    request->channels[0]->center_freq == 5180) {
\t\t/* V16: one passive 20MHz channel, 500ms dwell, no TX. */
\t\tparams_le->passive_time = cpu_to_le32(500);
\t\tbrcmf_info("MZ600_V16_V2_PASSIVE_DWELL_MS=500 encoded_chanspec=0x%04x d11io=%u\n",
\t\t\t   le16_to_cpu(params_le->channel_list[0]),
\t\t\t   cfg->d11inf.io_type);
\t}
\tparams_le->length = cpu_to_le16(length);
\t/* Adding mask to channel numbers */''')

    # Verify the actual V1 command bytes after the old-D11 conversion.
    anchor='''\t\tbrcmf_scan_params_v2_to_v1(&params->params_v2_le, &params_v1->params_le);
\t\tkfree(params);'''
    c=replace_once(c,anchor,'''\
\t\tbrcmf_scan_params_v2_to_v1(&params->params_v2_le, &params_v1->params_le);
\t\tif (ifp->drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID)
\t\t\tbrcmf_info("MZ600_V16_V1_CH36_WIRE chanspec=0x%04x passive_ms=%d scan_type=%u nprobes=%d nchans=%u\n",
\t\t\t    le16_to_cpu(params_v1->params_le.channel_list[0]),
\t\t\t    le32_to_cpu(params_v1->params_le.passive_time),
\t\t\t    params_v1->params_le.scan_type,
\t\t\t    le32_to_cpu(params_v1->params_le.nprobes),
\t\t\t    le32_to_cpu(params_v1->params_le.channel_num));
\t\tkfree(params);''')

    anchor='''\terr = brcmf_fil_iovar_data_set(ifp, "escan", params, params_size);
\tif (err) {'''
    c=replace_once(c,anchor,'''\
\terr = brcmf_fil_iovar_data_set(ifp, "escan", params, params_size);
\tbrcmf_info("MZ600_V16_ESCAN_SET_RC=%d v2=%u\\n",
\t\t    err, brcmf_feat_is_enabled(ifp, BRCMF_FEAT_SCAN_V2));
\tif (err) {''')

    anchor='''\tstatus = e->status;

\tif (status == BRCMF_E_STATUS_ABORT)'''
    c=replace_once(c,anchor,'''\
\tstatus = e->status;
\tbrcmf_info("MZ600_V16_EVENT69 status=%d datalen=%u\\n",
\t\t    status, e->datalen);

\tif (status == BRCMF_E_STATUS_ABORT)''')

    anchor='''\t\tbss_info_le = &escan_result_le->bss_info_le;

\t\tif (brcmf_p2p_scan_finding_common_channel'''
    c=replace_once(c,anchor,'''\
\t\tbss_info_le = &escan_result_le->bss_info_le;
\t\tbrcmf_info("MZ600_V16_EVENT69_PARTIAL bss_ver=%u bss_len=%u count=%u\\n",
\t\t\t   le32_to_cpu(bss_info_le->version),
\t\t\t   le32_to_cpu(bss_info_le->length),
\t\t\t   le16_to_cpu(escan_result_le->bss_count));

\t\tif (brcmf_p2p_scan_finding_common_channel''')

    anchor='''\tbss_list = (struct brcmf_scan_results *)cfg->escan_info.escan_buf;
\tif (bss_list->count != 0 &&'''
    c=replace_once(c,anchor,'''\
\tbss_list = (struct brcmf_scan_results *)cfg->escan_info.escan_buf;
\tbrcmf_info("MZ600_V16_FINAL_BSS count=%u version=%u\\n",
\t\t    bss_list->count, bss_list->version);
\tif (bss_list->count != 0 &&''')

    anchor='''\tscan_request = cfg->scan_request;
\tcfg->scan_request = NULL;

\ttimer_delete_sync(&cfg->escan_timeout);'''
    c=replace_once(c,anchor,'''\
\tbrcmf_info("MZ600_V16_SCAN_COMPLETION aborted=%u fw_abort=%u owned=%u\\n",
\t\t    aborted, fw_abort, !!cfg->scan_request);
\tscan_request = cfg->scan_request;
\tcfg->scan_request = NULL;

\ttimer_delete_sync(&cfg->escan_timeout);''')

    anchor='''\tif (cfg->int_escan_map || cfg->scan_request) {
\t\tbphy_err(drvr, "timer expired\\n");'''
    c=replace_once(c,anchor,'''\
\tif (cfg->int_escan_map || cfg->scan_request) {
\t\tbrcmf_info("MZ600_V16_ESCAN_WATCHDOG_FIRED\\n");
\t\tbphy_err(drvr, "timer expired\\n");''')
    return c

def main():
    if not (LINUX.is_dir() and OUT.is_dir() and M.is_dir()):
        raise RuntimeError("No matching kernel source/build tree")
    if not (Path(str(COMPILER)+"gcc").is_file() and PATCH.is_file()):
        raise RuntimeError("Missing exact compiler or base fallback patch")
    source=SOURCE.read_bytes()
    original_ko=KO.read_bytes()
    if sha(source)!=SOURCE_SHA or sha(PATCH.read_bytes())!=PATCH_SHA or sha(original_ko)!=ORIG_KO:
        raise RuntimeError("Source/patch/compiled module SHA changed: refuse")
    RESULT.mkdir(mode=0o700,exist_ok=True)
    artifact=RESULT/"brcmfmac-2012-escan-event69-v16.ko"
    report=RESULT/"offline-build-result.json"
    if artifact.exists() or report.exists():
        raise RuntimeError("V16 artifact already exists: refuse overwrite")
    result={}
    try:
        run("patch","--batch","--forward","-p1","-i",str(PATCH),cwd=LINUX)
        patched=SOURCE.read_text()
        SOURCE.write_text(instrument(patched))
        cmd=["make","-C",str(LINUX),"O="+str(OUT),"ARCH=arm",
             "CROSS_COMPILE="+str(COMPILER),"M="+str(M),"modules","-j2"]
        with (RESULT/"build.log").open("w") as log:
            run(*cmd,stdout=log,stderr=subprocess.STDOUT)
        current=KO.read_bytes()
        if sha(current)==ORIG_KO:
            raise RuntimeError("V16 compiled module is identical to baseline!")
        shutil.copyfile(KO,artifact)
        result={
            "outcome":"OFFLINE_V16_ARM_MODULE_BUILT",
            "module_sha256":sha(current),"module_bytes":len(current),
            "source_sha256_at_rest":SOURCE_SHA,
            "base_patch_sha256":PATCH_SHA,
            "no_device_access":True,"no_scan":True,"firmware_stays_private":True
        }
    finally:
        SOURCE.write_bytes(source)
        KO.write_bytes(original_ko)
        if sha(SOURCE.read_bytes())!=SOURCE_SHA or sha(KO.read_bytes())!=ORIG_KO:
            raise RuntimeError("CRITICAL HOST SOURCE/MODULE RESTORE FAILED")
    if not result:
        raise RuntimeError("No successful artifact")
    report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
