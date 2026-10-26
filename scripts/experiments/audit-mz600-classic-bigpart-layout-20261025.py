#!/usr/bin/env python3
"""READ-ONLY Motorola Xoom classic BigPart layout auditor.

Compares a confirmed same-unit eMMC partition snapshot to Schischu's original
Xoom BigPart logical mapping (commit 6b3d70fff905b7395fd15992c3779b27d1b6c101).
No block devices are opened; no recovery package is flashed or generated.
The remap is a *kernel-visible, in-memory partition view*, NOT a GPT rewrite.

The default snapshot is the Oct 25 replacement MZ600 TWRP observation. For a
new device observation, supply --snapshot JSON with the same schema, obtained
through a verified READ-ONLY mechanism. Fail closed on any difference.
"""
import argparse
import hashlib
import json
from pathlib import Path

SECTOR_BYTES = 512
EMMC_SECTORS = 62_521_344
OLD = {
    "ebb":      [ 1,    51_200,      6_144],
    "pdsb":     [ 2,    57_344,      4_096],
    "misc":     [ 3,    61_440,      4_096],
    "logo.bin": [ 4,    65_536,      8_192],
    "kpanic":   [ 5,    73_728,      4_096],
    "recovery": [ 6,    77_824,     24_576],
    "boot":     [ 7,   102_400,     16_384],
    "system":   [ 8,   118_784,    524_288],
    "cache":    [ 9,   643_072,    346_112],
    "userdata": [10,   989_184, 61_522_944],
}
# Exactly the original Xoom kernel BigPart constants.
OLD_SYSTEM_SECTORS = 0x080000  # 256 MiB
OLD_CACHE_SECTORS = 0x054800   # 169 MiB
NEW_SYSTEM_SECTORS = 0x200000  # 1024 MiB
NEW_CACHE_SECTORS = 0x100000   # 512 MiB
OLD_STARTS = (0x1D000, 0x9D000, 0xF1800)
ORIGINAL_BIGPART_COMMIT = "6b3d70fff905b7395fd15992c3779b27d1b6c101"

def plan(snapshot):
    assert snapshot["sector_bytes"] == SECTOR_BYTES, "wrong sector size"
    assert snapshot["emmc_sectors"] == EMMC_SECTORS, "different eMMC geometry"
    current = snapshot["partitions"]
    assert set(current) == set(OLD), "unexpected partition names"
    for name, expected in OLD.items():
        assert current[name] == expected, f"snapshot mismatch: {name}"
    assert tuple(current[name][1] for name in ("system", "cache", "userdata")) == OLD_STARTS
    grow_system = NEW_SYSTEM_SECTORS - OLD_SYSTEM_SECTORS
    grow_cache = NEW_CACHE_SECTORS - OLD_CACHE_SECTORS
    effective = {k: list(v) for k, v in current.items()}
    effective["system"][2] = NEW_SYSTEM_SECTORS
    effective["cache"][1] += grow_system
    effective["cache"][2] = NEW_CACHE_SECTORS
    effective["userdata"][1] += grow_system + grow_cache
    effective["userdata"][2] -= grow_system + grow_cache
    before = sorted([(v[1], v[1] + v[2], k) for k, v in current.items()])
    after = sorted([(v[1], v[1] + v[2], k) for k, v in effective.items()])
    for layout in (before, after):
        assert all(start >= 51_200 and end <= EMMC_SECTORS and start < end
                   for start, end, _ in layout), "partition outside bounds"
        assert all(layout[i][1] <= layout[i + 1][0]
                   for i in range(len(layout) - 1)), "partition overlap"
    for name in ("ebb", "pdsb", "misc", "logo.bin", "kpanic", "recovery", "boot"):
        assert current[name] == effective[name], "protected partition moved"
    assert effective["system"][1] + effective["system"][2] == effective["cache"][1]
    assert effective["cache"][1] + effective["cache"][2] == effective["userdata"][1]
    assert current["userdata"][1] + current["userdata"][2] == (
        effective["userdata"][1] + effective["userdata"][2]), "p10 end changed"
    def render(d):
        return {name: {"index": v[0], "start_sector": v[1], "sectors": v[2],
                       "end_sector_inclusive": v[1] + v[2] - 1,
                       "size_mib": v[2] * SECTOR_BYTES / 1048576}
                for name, v in d.items()}
    return {
        "classification": "OFFLINE mathematical comparison only; NOT PHYSICAL",
        "device": "replacement MZ600, previous recovery measured baseline",
        "on_disk_partition_table_written": False,
        "provenance": "Schischu original Xoom BigPart kernel in-memory GPT remap",
        "source_commit": ORIGINAL_BIGPART_COMMIT,
        "old": render(current),
        "classic_bigpart_kernel_view": render(effective),
        "system_can_hold_existing_768mib_debian_image": effective["system"][2] * 512 >= 805306368,
        "recovery_and_boot_boundaries_unchanged": True,
        "next_gate": "Verify matching recovery/kernel partition view ON THIS MZ600 read-only before formatting or writing any sector",
        "no_device_access_no_writes": True,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=Path, help="read-only same-unit partition observation JSON")
    p.add_argument("--output", type=Path, help="save JSON result (refuse overwrite)")
    a = p.parse_args()
    snapshot = json.loads(a.snapshot.read_text()) if a.snapshot else {
        "sector_bytes": SECTOR_BYTES, "emmc_sectors": EMMC_SECTORS,
        "partitions": OLD,
    }
    result = plan(snapshot)
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if a.output:
        if a.output.exists():
            raise SystemExit(f"Refusing to overwrite existing report: {a.output}")
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(encoded)
    print("CLASSIC_BIGPART_OFFLINE_AUDIT_PASS")
    print("original_kernel_commit", ORIGINAL_BIGPART_COMMIT)
    for n in ("system", "cache", "userdata"):
        v = result["classic_bigpart_kernel_view"][n]
        print(n, f"start={v['start_sector']}", f"sectors={v['sectors']}",
              f"MiB={v['size_mib']}")
    print("NO PHYSICAL VALIDATION. NO GPT/DEVICE WRITES.")
    if a.output:
        print("report", a.output)

if __name__ == "__main__":
    main()
