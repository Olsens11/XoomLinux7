#!/usr/bin/env python3
"""MZ600 original Wi-Fi firmware/calibration provenance comparison (OFFLINE ONLY).

Never emits raw binary content, calibration values, MAC addresses, keys, or secrets.
Do not publish the private inputs. Does not connect to any device or alter files.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

MAGIC_VERSION = re.compile(rb'4329b1/[^\x00\r\n]{0,170}?Version:\s*(\d+(?:\.\d+){3})', re.I)

def fw_data(path):
    data = path.read_bytes()
    matches = MAGIC_VERSION.findall(data)
    return len(data), hashlib.sha256(data).hexdigest(), sorted({m.decode("ascii") for m in matches})

def private_params(path):
    # Intentionally do not print keys or any parameter values or line excerpts.
    params = []
    for line in path.read_bytes().splitlines():
        part = line.split(b"#", 1)[0].strip()
        if b"=" not in part:
            continue
        key, value = part.split(b"=", 1)
        params.append((key.strip(), value.strip()))
    return params

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--early", type=Path, required=True, help="Private early MZ600 normal firmware")
    p.add_argument("--later", type=Path, help="Private later Motorola firmware")
    p.add_argument("--early-cal", type=Path, help="Private early MZ600 reference calibration")
    p.add_argument("--later-cal", type=Path, help="Private later calibration")
    a = p.parse_args()
    for label, path in [("EARLY", a.early), ("LATER", a.later)]:
        if path is None:
            continue
        size, digest, versions = fw_data(path)
        print(f"{label} firmware bytes={size} sha256={digest} embedded_versions={','.join(versions) or 'NONE'}")
    if a.early_cal or a.later_cal:
        if not a.early_cal or not a.later_cal:
            p.error("Supply both calibration paths or neither.")
        early, later = private_params(a.early_cal), private_params(a.later_cal)
        one, two = dict(early), dict(later)
        shared = set(one) & set(two)
        different = [k for k in shared if one[k] != two[k]]
        # No device identifiers, proprietary setting names, or private values.
        identity = {b'macaddr', b'il0macaddr', b'ccode', b'regrev', b'et0macaddr'}
        print(f"CALIBRATION entry_counts={len(early)}/{len(later)} unique_key_counts={len(one)}/{len(two)} keysets_equal={set(one)==set(two)} ordering_equal={[k for k,v in early]==[k for k,v in later]}")
        print(f"CALIBRATION differing_value_fields={len(different)} identity_or_regulatory_field_changed={bool(set(different) & identity)}")
        print("CALIBRATION PROVENANCE: identical-looking reference files are not proof of per-unit suitability.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
