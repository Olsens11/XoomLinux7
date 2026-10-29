#!/usr/bin/env python3
"""Source-only contract checks for the pinned Linux 7 BCM4329 boundary.

This verifies presence/order of upstream mechanisms, NOT their behavior on a
running tablet or legality of any RF transmission. No hardware I/O or writes.
Usage: python3 tools/forensics/check_bcm4329_country_boundary_20261029.py /path/to/linux
"""
import argparse
from pathlib import Path

def require(ok, label):
    print(f"{'PASS' if ok else 'FAIL'}: {label}")
    if not ok:
        raise AssertionError(label)

def between(source, start, stop):
    require(start in source and stop in source, f"source anchors: {start}")
    return source.split(start, 1)[1].split(stop, 1)[0]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kernel_source", type=Path)
    args = parser.parse_args()
    root = args.kernel_source
    fm = root / "drivers/net/wireless/broadcom/brcm80211/brcmfmac"
    cfg = (fm / "cfg80211.c").read_text()
    of = (fm / "of.c").read_text()
    fw = (fm / "fwil.c").read_text()
    reg = (root / "net/wireless/reg.c").read_text()
    core = (root / "net/wireless/core.c").read_text()

    translate = between(cfg, "static s32 brcmf_translate_country_code(",
                        "static int\nbrcmf_parse_dump_obss(")
    already = translate.find("return -EAGAIN")
    lookup = translate.find("country_codes = drvr->settings->country_codes")
    require(0 <= already < lookup, "country-abbrev early return precedes DT revision lookup")
    require("ccreq->rev = cpu_to_le32(country_codes->table[found_index].rev)" in translate,
            "country mapping sets firmware rev from board table")
    trivial = between(cfg, "static bool brmcf_use_iso3166_ccode_fallback(",
                      "static s32 brcmf_translate_country_code(")
    require("BRCM_CC_4329_CHIP_ID" not in trivial,
            "BCM4329 is not universally whitelisted for trivial rev0 mapping")
    require("brcm,ccode-map" in of and '"%2c-%2c-%d"' in of,
            "existing brcmfmac DT ISO-code/firmware-code/revision parser")
    notify = between(cfg, "static void brcmf_cfg80211_reg_notifier(",
                     "static void brcmf_free_wiphy(")
    order = ['"country", &ccreq, sizeof(ccreq)', 'brcmf_translate_country_code(',
             'brcmf_fil_iovar_data_set(', 'brcmf_setup_wiphybands(cfg)']
    positions = [notify.find(x) for x in order]
    require(all(p >= 0 for p in positions) and positions == sorted(positions),
            "country notifier: read, translate, set, update bands, in sequence")
    require("BRCMF_C_GET_VALID_CHANNELS" in cfg,
            "WIFI-01 legacy GET_VALID_CHANNELS fallback present in review source")
    require("if (err == -EBADE" in cfg and "BRCM_CC_4329_CHIP_ID" in cfg,
            "fallback gated by BCM4329 and normalized firmware error")
    require("channel->flags |= IEEE80211_CHAN_NO_IR" in cfg,
            "review candidate still applies conditional NO_IR for unknown 5GHz metadata")
    require("err = -EBADE" in fw and "if (ifp->fwil_fwerr)" in fw,
            "fwil normalizes multiple native firmware errors to -EBADE")
    require("chan->orig_flags" in reg and "flags = chan->orig_flags" in reg,
            "cfg80211 regulatory updates use registration-time original flags")
    require("sband->channels[i].orig_flags =" in core and
            "sband->channels[i].flags;" in core,
            "cfg80211 captures original channel flags at registration")
    print("SOURCE_CONTRACT_CHECKS_COMPLETE: no writes, no RF, no production acceptance")

if __name__ == "__main__":
    main()
