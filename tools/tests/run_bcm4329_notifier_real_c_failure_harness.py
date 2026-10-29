#!/usr/bin/env python3
"""Run the exact pinned brcmfmac regulatory notifier with controlled fake I/O.

C function text is extracted byte-for-byte from the supplied Linux tree;
the wiphy, firmware and country functions are host-only test doubles.
This does not prove live RF behavior, concurrency or actual regulatory
compliance. It demonstrates precisely which callback branches return
without any successful firmware re-intersection.

Usage: python3 tools/tests/run_bcm4329_notifier_real_c_failure_harness.py /path/to/linux
"""
import argparse
from pathlib import Path
import hashlib
import subprocess
import tempfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    args = p.parse_args()
    path = args.source / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c"
    s = path.read_text()
    start = "static void brcmf_cfg80211_reg_notifier("
    end = "static void brcmf_free_wiphy("
    assert s.count(start) == s.count(end) == 1
    real = s[s.index(start):s.index(end)]
    assert "brcmf_bcm4329_refresh_legacy_channels(cfg)" in real

    template = (Path(__file__).with_name(
        "mz600_bcm4329_notifier_real_c_failure_harness.c")).read_text()
    tag = ("/* BEGIN_EXACT_R7_NOTIFIER_FUNCTION */\n"
           "/* END_EXACT_R7_NOTIFIER_FUNCTION */")
    assert template.count(tag) == 1
    combined = template.replace(tag, real)
    print("NOTIFIER_EXACT_SHA256", hashlib.sha256(real.encode()).hexdigest(), flush=True)
    print("NOTIFIER_EXACT_BYTES", len(real), flush=True)
    with tempfile.TemporaryDirectory(prefix="mz600-notifier-exact-c-") as td:
        c_file = Path(td) / "test.c"
        executable = Path(td) / "test"
        c_file.write_text(combined)
        subprocess.run([
            "gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
            "-O1", "-g", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", str(c_file), "-o", str(executable)
        ], check=True)
        subprocess.run([str(executable)], check=True)
    print("NOTIFIER_EXACT_C_SOURCE_FAULT_CHECK_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
