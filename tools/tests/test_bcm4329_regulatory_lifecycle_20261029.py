#!/usr/bin/env python3
"""Offline source + illustrative regulatory lifecycle fixture for BCM4329.

NOT a kernel execution, firmware, radio, DFS, or legal acceptance test.
Read exact pinned Linux 7 source for call order and safety behavior; model
only the flag intersection to prevent replacing cfg80211 permissions with
firmware availability.
"""
import argparse
from pathlib import Path

DISABLED = 1 << 0
NO_IR = 1 << 1
RADAR = 1 << 3
NO_HT40 = (1 << 4) | (1 << 5)
NO_80 = 1 << 7
NO_160 = 1 << 8


def effective_flags(orig, country_flags, firmware_has_chan, metadata_supported):
    """Represent intended monotone constraints after cfg80211 recalculation.

    Unknown firmware metadata requires conservative NO_IR for 5GHz; firmware
    allowed list cannot remove driver or country restrictions. This model is
    illustrative and deliberately does not claim to execute kernel functions.
    """
    flags = orig | country_flags
    if not firmware_has_chan:
        flags |= DISABLED
    if firmware_has_chan and not (orig & DISABLED):
        flags |= NO_HT40 | NO_80 | NO_160
        if not metadata_supported:
            flags |= NO_IR
    return flags


def source_check(root: Path):
    cfg = (root / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c").read_text()
    reg = (root / "net/wireless/reg.c").read_text()
    core = (root / "net/wireless/core.c").read_text()
    assert "wiphy_register(wiphy);" in cfg
    assert "brcmf_setup_wiphybands(cfg);" in cfg
    assert cfg.index("wiphy_register(wiphy);") < cfg.index("brcmf_setup_wiphybands(cfg);", cfg.index("wiphy_register(wiphy);"))
    # The PHY-specific 99 domain applies to some initiators, while USER
    # and COUNTRY_IE can select the current cfg80211 global country rules.
    selector = reg.split("static const struct ieee80211_regdomain *reg_get_regdomain(", 1)[1].split("static unsigned int", 1)[0]
    assert "lr->initiator != NL80211_REGDOM_SET_BY_COUNTRY_IE" in selector
    assert "lr->initiator != NL80211_REGDOM_SET_BY_USER" in selector
    assert "return get_wiphy_regdom(wiphy);" in selector
    assert "return get_cfg80211_regdom();" in selector
    assert "sband->channels[i].orig_flags =" in core
    assert "sband->channels[i].flags;" in core
    assert "u32 flags = chan->orig_flags;" in reg
    update = reg.split("static void wiphy_update_regulatory(", 1)[1].split("static void update_all_wiphy_regulatory(", 1)[0]
    # Custom-REG CORE hints may notify without rebuilding channels.
    # For an accepted country/user update, normal channel recomputation
    # precedes the notifier at the END of the update function.
    assert update.count("reg_call_notifier(wiphy, lr);") == 2
    assert update.index("handle_band(wiphy") < update.rindex("reg_call_notifier(wiphy, lr);")
    legacy = cfg.split("static int brcmf_bcm4329_legacy_channels(", 1)[1].split("static int brcmf_construct_chaninfo(", 1)[0]
    assert "band->channels[j].orig_flags & IEEE80211_CHAN_DISABLED" in legacy
    assert "if (!supported) {" in legacy
    assert "band->channels[j].flags |= IEEE80211_CHAN_DISABLED;" in legacy
    assert "channel->flags |= IEEE80211_CHAN_NO_HT40" in legacy
    assert "channel->flags |= IEEE80211_CHAN_NO_IR" in legacy
    assert "return chan_err;" in legacy
    assert "fwerr ==\n" in legacy and "-BRCMF_BCM4329_FW_UNSUPPORTED" in legacy
    assert "channel->flags &= ~IEEE80211_CHAN_NO_IR" not in legacy
    assert "channel->orig_flags =" not in legacy
    assert "band->channels[j].orig_flags =" not in legacy
    custom = cfg.split("static const struct ieee80211_regdomain brcmf_regdom = {", 1)[1].split("};", 1)[0]
    assert '.alpha2 =  "99"' in custom
    assert "NL80211_RRF_DFS" not in custom and "NL80211_RRF_NO_IR" not in custom
    print("SOURCE_GATE_PASS: cfg80211 registration, notifier order, immutable orig_flags, no relax on legacy fallback")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    a = p.parse_args()
    source_check(a.source)
    # Start with one stable hardware channel and dynamic regulatory state.
    original = 0
    first = effective_flags(original, NO_IR, True, False)
    assert first & NO_IR
    second = effective_flags(original, DISABLED, False, False)
    assert second & DISABLED
    restored = effective_flags(original, 0, True, False)
    assert not restored & DISABLED
    assert restored & NO_IR  # still conservative due unknown metadata
    assert effective_flags(DISABLED, 0, True, True) & DISABLED
    assert effective_flags(0, RADAR, True, True) & RADAR
    assert effective_flags(0, DISABLED | NO_IR, True, True) & (DISABLED | NO_IR)
    print("MODEL_FIXTURES_PASS: country restrict / reallow, immutable hardware bans, DFS and NO_IR never relaxed")
    print("NOT REAL KERNEL, FIRMWARE, RF, OR LEGAL ACCEPTANCE")


if __name__ == "__main__":
    main()
