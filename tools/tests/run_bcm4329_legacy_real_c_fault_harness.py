#!/usr/bin/env python3
"""Compile/test the exact WIFI-01 C legacy channel function with fake firmware.

Unlike Python behavior models, this extracts and executes the C function
unchanged from the specified Linux source tree. All surrounding kernel
types, firmware calls, cfg80211 channels and memory allocation are STUBS;
there is no kernel or device/radio I/O. This is NOT acceptance for the
regulatory notifier, concurrency, live firmware or lawful operation.

Usage:
 python3 tools/tests/run_bcm4329_legacy_real_c_fault_harness.py \
    /absolute/path/to/linux-source
"""
from pathlib import Path
import argparse
import hashlib
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    root = args.source
    driver = root / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c"
    source = driver.read_text()
    first = "static int brcmf_bcm4329_legacy_channels("
    last = "static int brcmf_bcm4329_refresh_legacy_channels("
    assert source.count(first) == 1 and source.count(last) == 1
    func = source[source.index(first):source.index(last)]
    assert "restrictions = kcalloc(" in func
    assert "band->channels[j].flags |= restrictions[slot++]" in func
    assert "goto out_free;" in func

    harness = (Path(__file__).with_name(
        "mz600_bcm4329_legacy_real_c_fault_harness.c")).read_text()
    sentinel = ("/* BEGIN_EXACT_R7_LEGACY_FUNCTION */\n"
                "/* END_EXACT_R7_LEGACY_FUNCTION */")
    assert harness.count(sentinel) == 1
    harness = harness.replace(sentinel, func)
    print("EXACT_FUNCTION_SHA256", hashlib.sha256(func.encode()).hexdigest(), flush=True)
    print("EXACT_FUNCTION_BYTES", len(func), flush=True)
    with tempfile.TemporaryDirectory(prefix="mz600-wifi01-real-c-") as td:
        p = Path(td)
        test_c = p / "test.c"
        binary = p / "test"
        test_c.write_text(harness)
        subprocess.run([
            "gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
            "-O1", "-g", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", str(test_c), "-o", str(binary)
        ], check=True)
        subprocess.run([str(binary)], check=True)
    print("R7_EXACT_C_SOURCE_FAULT_CHECK_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
