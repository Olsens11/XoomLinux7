#!/usr/bin/env python3
"""Offline source contract for review-only BCM4329 native firmware errors.

Tests the *decision rule* and required source constructs, not runtime RF
behavior, transport concurrency, cfg80211 country transitions, or legal
regulatory acceptance.

Run: python3 tools/tests/test_bcm4329_fwerr_boundary_20261029.py /path/to/linux
"""
import argparse
from pathlib import Path


BRCM_CC_4329_CHIP_ID = 4329
BCME_UNSUPPORTED = -23


def legacy_fallback(chip_id: int, normal_err: int, native_fwerr: int) -> bool:
    return (
        chip_id == BRCM_CC_4329_CHIP_ID
        and normal_err != 0
        and native_fwerr == BCME_UNSUPPORTED
    )


def check_source(root: Path) -> None:
    driver = root / "drivers/net/wireless/broadcom/brcm80211/brcmfmac"
    cfg = (driver / "cfg80211.c").read_text()
    fwil = (driver / "fwil.c").read_text()
    head = (driver / "fwil.h").read_text()
    assert "brcmf_fil_iovar_data_get_fwerr(ifp, \"chanspecs\"" in cfg
    assert "fwerr == -BRCMF_BCM4329_FW_UNSUPPORTED" in cfg
    assert "brcmf_fil_bsscfg_data_get_fwerr(" in cfg
    assert "per_chan_available = false;" in cfg
    assert "if (!err && fwerr_out)" in fwil
    assert "*fwerr_out = 0;" in fwil
    assert "brcmf_fil_iovar_data_get_common" in fwil
    assert "brcmf_fil_bsscfg_data_get_common" in fwil
    assert "brcmf_fil_iovar_data_get_fwerr(" in head
    assert "brcmf_fil_bsscfg_data_get_fwerr(" in head
    assert "if (ifp->fwil_fwerr)" in fwil  # existing callers unchanged
    assert "ifp->fwil_fwerr =" not in cfg  # no unsafe shared flag toggle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kernel_source", type=Path)
    args = parser.parse_args()

    cases = [
        # normal Linux errno may be -EBADE (-52) for distinct native results.
        (4329, -52, -23, True, "actual native unsupported"),
        (4329, -52, -4, False, "native NOTUP must not mean unsupported"),
        (4329, -52, -2, False, "native BADARG must not mean unsupported"),
        (4329, -52, -1, False, "unknown native failure must not trigger"),
        (4329, -5, 0, False, "transport failure must not trigger"),
        (4329, 0, 0, False, "supported chanspecs stays normal"),
        (4359, -52, -23, False, "other Broadcom chips unchanged"),
    ]
    for chip, err, fwerr, expected, label in cases:
        assert legacy_fallback(chip, err, fwerr) == expected, label
        print("PASS:", label)

    check_source(args.kernel_source)
    print("SOURCE_API_AND_DECISION_CONTRACT_PASS")
    print("NOT a driver runtime, firmware, regulatory, or RF acceptance test")


if __name__ == "__main__":
    main()
