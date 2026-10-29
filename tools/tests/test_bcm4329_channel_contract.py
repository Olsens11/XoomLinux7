#!/usr/bin/env python3
"""Contract fixtures for BCM4329 legacy channel metadata: NOT driver execution.
A pure Python safety sketch to ensure intended behavior is unambiguous before a kernel patch.
"""
import unittest

# Broadcom legacy D11n on-wire band/width/sideband fields; static source values.
BAND_5G = 0x1000
BAND_2G = 0x2000
BW_20 = 0x0800
SB_NONE = 0x0300
WL_CHAN_RADAR = 1 << 3
WL_CHAN_PASSIVE = 1 << 5

# Model only. Do not map these integers to Linux kernel ABI automatically.
DISABLED = 1 << 0
NO_IR = 1 << 1
RADAR = 1 << 2
NO_HT40 = 1 << 3
NO_80 = 1 << 4
NO_160 = 1 << 5
HT20_ONLY = NO_HT40 | NO_80 | NO_160


def argument(band, channel, profile):
    assert band in (2, 5) and (1 <= channel <= 196)
    prefix = BAND_5G if band == 5 else BAND_2G
    if profile == "xoom-legacy":
        return prefix | channel
    if profile == "intermediate-bw20":
        return prefix | BW_20 | channel
    if profile == "modern-d11n":
        return prefix | BW_20 | SB_NONE | channel
    raise ValueError("unknown firmware argument profile")


def allowed_channel_flags(band, channel, supported, existing_flags,
                          metadata_ok=False, metadata_flags=0):
    """Conservative candidate contract, NOT verified firmware-specific behavior.

    Firmware inventory is an input, not a license to clear regulatory bits.
    A missing 5GHz metadata response adds NO_IR; never sets allowed-TX.
    """
    if channel not in supported:
        return existing_flags | DISABLED
    flags = existing_flags | HT20_ONLY
    if metadata_ok:
        if metadata_flags & WL_CHAN_RADAR:
            flags |= RADAR | NO_IR
        if metadata_flags & WL_CHAN_PASSIVE:
            flags |= NO_IR
    elif band == 5:
        flags |= NO_IR
    return flags


class ContractTests(unittest.TestCase):
    def test_argument_profiles(self):
        self.assertEqual([argument(5, 36, kind) for kind in
                          ("xoom-legacy", "intermediate-bw20", "modern-d11n")],
                         [0x1024, 0x1824, 0x1B24])
        self.assertEqual([argument(2, 11, kind) for kind in
                          ("xoom-legacy", "intermediate-bw20", "modern-d11n")],
                         [0x200B, 0x280B, 0x2B0B])

    def test_missing_hardware_channel_remains_disabled(self):
        self.assertTrue(allowed_channel_flags(5, 165, {36, 40}, 0) & DISABLED)

    def test_original_regulatory_restrictions_never_cleared(self):
        before = DISABLED | NO_IR | RADAR
        after = allowed_channel_flags(5, 36, {36}, before,
                                      metadata_ok=True, metadata_flags=0)
        self.assertEqual(after & before, before)

    def test_radar_and_passive_add_no_ir(self):
        flags = allowed_channel_flags(5, 52, {52}, 0, True,
                                      WL_CHAN_RADAR | WL_CHAN_PASSIVE)
        self.assertEqual(flags & (RADAR | NO_IR), RADAR | NO_IR)

    def test_passive_adds_no_ir_not_radar(self):
        flags = allowed_channel_flags(5, 36, {36}, 0, True, WL_CHAN_PASSIVE)
        self.assertTrue(flags & NO_IR)
        self.assertFalse(flags & RADAR)

    def test_missing_metadata_never_implies_5ghz_tx(self):
        for number in (36, 52, 149, 153):
            flags = allowed_channel_flags(5, number, {number}, 0, False)
            self.assertTrue(flags & NO_IR)

    def test_ht20_only_on_supported_channels(self):
        self.assertEqual(allowed_channel_flags(2, 11, {11}, 0) & HT20_ONLY,
                         HT20_ONLY)

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            argument(5, 36, "guess")

    def test_metadata_success_not_assumed_from_nonzero_input(self):
        # An echoed wire-format input is NOT a validated status/flag response.
        flags = allowed_channel_flags(5, 36, {36}, 0, metadata_ok=False,
                                      metadata_flags=0x1B24)
        self.assertTrue(flags & NO_IR)


if __name__ == "__main__":
    unittest.main(verbosity=2)
