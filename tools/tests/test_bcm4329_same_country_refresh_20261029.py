#!/usr/bin/env python3
"""Offline contract/model for BCM4329 same-country legacy channel reapply.

Checks pinned Linux source *structure* and a small explicitly illustrative
staged-flag model. Does NOT execute the kernel C helper, firmware or RF policy.
Run:
  python3 tools/tests/test_bcm4329_same_country_refresh_20261029.py \
     /path/to/qa-wifi01-r6-source-20261029
"""
import argparse
from pathlib import Path

DISABLED = 1 << 0
NO_IR = 1 << 1
RADAR = 1 << 3
NO_HT40 = (1 << 4) | (1 << 5)
BCME_UNSUPPORTED = -23
BCME_NOTUP = -4


def apply_restrictions(original, wanted, errors, is_legacy):
    """Model additive-only, commit-after-all-queries behavior."""
    state = original[:]
    if not is_legacy:
        return state
    pending = []
    for available, metadata, error in zip(wanted, [None] * len(wanted), errors):
        if error not in (0, BCME_UNSUPPORTED):
            # Entire transaction aborted; never touch the live state.
            return state
        flags = NO_HT40 if available else DISABLED
        if available and error == BCME_UNSUPPORTED:
            flags |= NO_IR
        pending.append(flags)
    return [old | restriction for old, restriction in zip(state, pending)]


def check_source(root):
    file = root / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c"
    source = file.read_text()
    legacy = source.split("static int brcmf_bcm4329_legacy_channels(", 1)[1].split(
        "static int brcmf_bcm4329_refresh_legacy_channels(", 1
    )[0]
    helper = source.split("static int brcmf_bcm4329_refresh_legacy_channels(", 1)[1].split(
        "static int brcmf_construct_chaninfo(", 1
    )[0]
    notifier = source.split("static void brcmf_cfg80211_reg_notifier(", 1)[1].split(
        "static void brcmf_free_wiphy(", 1
    )[0]
    assert "restrictions = kcalloc(" in legacy
    assert "goto out_free;" in legacy
    assert "kfree(restrictions);" in legacy
    assert "restrictions[slot++] = IEEE80211_CHAN_DISABLED;" in legacy
    assert "band->channels[j].flags |= restrictions[slot++];" in legacy
    assert legacy.index("brcmf_fil_bsscfg_data_get_fwerr") < legacy.index(
        "band->channels[j].flags |= restrictions[slot++];"
    )
    assert legacy.index("goto out_free;") < legacy.index(
        "band->channels[j].flags |= restrictions[slot++];"
    )
    assert "orig_flags & IEEE80211_CHAN_DISABLED" in legacy
    assert "IEEE80211_CHAN_NO_IR" in legacy
    assert "channel->flags &=" not in legacy
    assert "orig_flags =" not in legacy
    assert 'brcmf_fil_iovar_data_get_fwerr(ifp, "chanspecs"' in helper
    assert "fwerr == -BRCMF_BCM4329_FW_UNSUPPORTED" in helper
    assert "brcmf_bcm4329_legacy_channels(cfg, pbuf)" in helper
    assert "if (err == -EAGAIN" in notifier
    assert "drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID" in notifier
    assert "brcmf_bcm4329_refresh_legacy_channels(cfg)" in notifier
    assert notifier.index("if (err == -EAGAIN") < notifier.index(
        'brcmf_fil_iovar_data_set(ifp, "country"'
    )
    assert "brcmf_setup_wiphybands(cfg);" in notifier
    print("R6_SOURCE_CONTRACT_PASS: legacy-only matching-country refresh, atomic flag commit, no restriction clearing")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("source", type=Path)
    args = a.parse_args()
    check_source(args.source)
    starting = [DISABLED, NO_IR, RADAR, 0]
    cases = [
        ([True] * 4, [0] * 4, True, "normal metadata success"),
        ([True] * 4, [BCME_UNSUPPORTED] * 4, True, "raw BCME unsupported is conservatively NO_IR"),
        ([True] * 4, [0, BCME_NOTUP, 0, 0], True, "raw NOTUP aborts whole transaction"),
        ([True] * 4, [0, -5, 0, 0], True, "transport failure aborts whole transaction"),
        ([True] * 4, [0] * 4, False, "modern firmware bypasses legacy"),
        ([True, False, True, False], [0] * 4, True, "missing firmware channels are disabled"),
    ]
    for available, errors, legacy, name in cases:
        result = apply_restrictions(starting, available, errors, legacy)
        assert all((new | old) == new for new, old in zip(result, starting))
        if not legacy or any(error not in (0, BCME_UNSUPPORTED) for error in errors):
            assert result == starting
        if legacy and all(error == BCME_UNSUPPORTED for error in errors):
            assert result[3] & NO_IR
        print("PASS", name)
    print("R6_MODELED_ERROR_CASES_PASS 6/6; NOT a live C-driver, regulatory or RF validation")


if __name__ == "__main__":
    main()
