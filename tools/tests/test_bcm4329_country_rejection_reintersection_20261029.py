#!/usr/bin/env python3
"""Source contract and illustrative model for WIFI-01 r7 failure reintersection.

This is NOT compiled C-driver execution, firmware behavior or lawful RF
operation. It models why the already known firmware channel list must be
reapplied after country translation or firmware SET rejection, while
acknowledging that a query failure remains an unsolved fail-closed issue.
"""
import argparse
from pathlib import Path

DISABLED = 1
NO_IR = 2


def intersect_linux_firmware(linux_flags, available, read_ok, legacy):
    """Model monotone, atomic firmware restriction reapplication."""
    if not read_ok or not legacy:
        return linux_flags[:]  # Gap explicitly left open on read failure.
    return [f | (0 if yes else DISABLED) for f, yes in zip(linux_flags, available)]


def check_source(root):
    p = root / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c"
    s = p.read_text()
    n = s.split("static void brcmf_cfg80211_reg_notifier(", 1)[1].split(
        "static void brcmf_free_wiphy(", 1
    )[0]
    # Real code: two separate error pathways, before and after country SET.
    assert n.count("brcmf_bcm4329_refresh_legacy_channels(cfg)") == 2
    assert n.count("drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID") == 2
    tr = n.index("brcmf_translate_country_code(")
    setting = n.index('brcmf_fil_iovar_data_set(ifp, "country"')
    missing_map = n.index("BCM4329 legacy channel refresh failed")
    rejected = n.index("Firmware rejected country setting")
    reject_refresh = n.index("BCM4329 rejected-country refresh failed")
    assert tr < missing_map < setting < rejected < reject_refresh
    assert n.index("brcmf_setup_wiphybands(cfg);") > reject_refresh
    # The helper uses existing per-call native firmware error, not any -EBADE.
    helper = s.split("static int brcmf_bcm4329_refresh_legacy_channels(", 1)[1].split(
        "static int brcmf_construct_chaninfo(", 1
    )[0]
    assert '"chanspecs"' in helper
    assert "fwerr == -BRCMF_BCM4329_FW_UNSUPPORTED" in helper
    assert "brcmf_bcm4329_legacy_channels(cfg, pbuf)" in helper
    assert "ifp->fwil_fwerr =" not in n + helper
    # Flags remain additive and staged, even on the newly covered paths.
    legacy = s.split("static int brcmf_bcm4329_legacy_channels(", 1)[1].split(
        "static int brcmf_bcm4329_refresh_legacy_channels(", 1
    )[0]
    assert legacy.index("restrictions = kcalloc(") < legacy.index(
        "band->channels[j].flags |= restrictions[slot++]")
    assert "goto out_free;" in legacy and "kfree(restrictions);" in legacy
    assert "IEEE80211_CHAN_NO_IR" in legacy
    assert "channel->flags &=" not in legacy
    print("R7_SOURCE_PASS: translation-error and firmware-SET-error legacy-only reintersection")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    args = p.parse_args()
    check_source(args.source)
    # Each input is a cfg80211 state AFTER accepted rules were applied.
    for label, flags, channels, ok, legacy in [
        ("matching-country no-op", [0, NO_IR, 0], [True, False, True], True, True),
        ("country translation unmapped", [0, 0, NO_IR], [False, True, True], True, True),
        ("firmware country SET rejected", [0, 0, 0], [True, False, False], True, True),
        ("firmware query fails: open fail-closed gap", [0, 0, 0], [False]*3, False, True),
        ("modern firmware unchanged", [0, 0, 0], [False]*3, True, False),
    ]:
        new = intersect_linux_firmware(flags, channels, ok, legacy)
        assert all((n | old) == n for n, old in zip(new, flags))
        if not ok or not legacy:
            assert new == flags
        else:
            assert all((n & DISABLED) for n, allowed in zip(new, channels) if not allowed)
        print("PASS", label)
    print("R7_MODEL_5_CASES_PASS; unhandled firmware-query failure remains OPEN")


if __name__ == "__main__":
    main()
