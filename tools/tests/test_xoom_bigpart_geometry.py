#!/usr/bin/env python3
"""Read-only source-literal/geometry checks; not an executed C kernel test."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "patches/upstream/review-storage-bigpart-20261028/0001-block-partitions-add-opt-in-Xoom-BigPart-view.patch"
OLD_STARTS = (51200, 57344, 61440, 65536, 73728, 77824, 102400, 118784, 643072, 989184)
OLD_SIZES = (6144, 4096, 4096, 8192, 4096, 24576, 16384, 524288, 346112, 61522944)
NEW_STARTS = OLD_STARTS[:7] + (118784, 2215936, 3264512)
NEW_SIZES = OLD_SIZES[:7] + (2097152, 1048576, 59247616)
SECTORS = 62521344
ALT_GPT = 62513151

def literal_array(name):
    source = re.sub(r"(?m)^\+", "", PATCH.read_text())
    match = re.search(r"static const u64 " + name + r"\[\] = \{([^}]*)\}", source, re.S)
    assert match, "missing source array " + name
    return tuple(int(v) for v in re.findall(r"\d+", match.group(1)))

def extents_valid(starts, sizes):
    end = 0
    for start, size in zip(starts, sizes):
        if start < end or size <= 0 or start + size > SECTORS:
            return False
        end = start + size
    return len(starts) == len(sizes)

class Geometry(unittest.TestCase):
    def test_source_literals_match_physically_observed_factory(self):
        self.assertEqual(literal_array("starts"), OLD_STARTS)
        self.assertEqual(literal_array("sizes"), OLD_SIZES)

    def test_both_maps_have_nonoverlapping_extents(self):
        self.assertTrue(extents_valid(OLD_STARTS, OLD_SIZES))
        self.assertTrue(extents_valid(NEW_STARTS, NEW_SIZES))

    def test_protected_first_seven_and_end_of_userdata(self):
        self.assertEqual((NEW_STARTS[:7], NEW_SIZES[:7]),
                         (OLD_STARTS[:7], OLD_SIZES[:7]))
        self.assertEqual(OLD_STARTS[9] + OLD_SIZES[9],
                         NEW_STARTS[9] + NEW_SIZES[9])
        self.assertLess(NEW_STARTS[9] + NEW_SIZES[9], ALT_GPT)

    def test_bigpart_sizes(self):
        self.assertEqual(NEW_SIZES[7] // 2048, 1024)
        self.assertEqual(NEW_SIZES[8] // 2048, 512)
        self.assertEqual(NEW_SIZES[9] // 1024, 57859)

    def test_native_tegra_alternate_gpt_address(self):
        self.assertEqual(SECTORS - 2 * 4096 - 1, ALT_GPT)

    def test_negative_overlap_and_overrun(self):
        self.assertFalse(extents_valid(NEW_STARTS[:8] + (118784,) + NEW_STARTS[9:], NEW_SIZES))
        self.assertFalse(extents_valid(NEW_STARTS, NEW_SIZES[:9] + (SECTORS,)))

    def test_source_does_not_add_another_gpt_sector_parser(self):
        source = PATCH.read_text()
        self.assertIn("xoom_bigpart=1", source)
        self.assertIn('of_machine_is_compatible("motorola,stingray")', source)
        self.assertNotIn('__setup("gpt_sector=', source)
        self.assertNotIn('motorola,xoom-bigpart', source)

if __name__ == "__main__":
    unittest.main(verbosity=2)
