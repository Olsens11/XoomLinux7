#!/usr/bin/env python3
"""Compile exactly one read-only BCM4329 5 GHz enumeration diagnostic .ko.

The running MZ600 uses kernel 7.0.0-next-20260422+ and MODVERSIONS.
Patch a temporary source file with four count-only kernel printk points,
build the matching module against the EXACT full v064 output directory, and
restore its original .ko and source even after build failure.

This script NEVER deploys, installs, copies to Xoom, flashes or reboots.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

BASE = Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025")
SOURCE = BASE / "v064-bigpart-linux"
OUTPUT = BASE / "v064-bigpart-debian-sdroot-build"
REL = Path("drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c")
CFILE = SOURCE / REL
MODULE_REL = Path("drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko")
ORIGINAL_MODULE = OUTPUT / MODULE_REL
# Kernel make M= builds .ko inside the source subdirectory even with O=.
BUILT_MODULE = SOURCE / MODULE_REL
WORK = BASE / "v064-5ghz-bandlist-diagnostic-v2-20261026"
COMPILER = "/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/"
READ_ELF = Path(COMPILER) / "arm-none-linux-gnueabihf-readelf"
ABI = "7.0.0-next-20260422+"
TARGET = WORK / "brcmfmac-5ghz-bandlist-diagnostic.ko"
PATCH_PATH = WORK / "0002-brcmfmac-log-firmware-bandlist-and-chanspec-band-counts.patch"
REPORT = WORK / "offline-build-result.json"


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def shell(args: list[str], **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def exactly_one(text: str, old: str, new: str, tag: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{tag}: expected one unique anchor; found {count}")
    return text.replace(old, new, 1)


def make_patch(original: str) -> str:
    c = original
    old = "\tu32 total;\n\tu32 chaninfo;\n"
    new = (
        "\tu32 total;\n\tu32 chaninfo;\n"
        "\tu32 diag_2g = 0;\n"
        "\tu32 diag_5g = 0;\n"
        "\tu32 diag_other = 0;\n"
    )
    c = exactly_one(c, old, new, "COUNTERS")
    old = (
        "\t\tch.chspec = (u16)le32_to_cpu(list->element[i]);\n"
        "\t\tcfg->d11inf.decchspec(&ch);\n\n"
        "\t\tif (ch.band == BRCMU_CHAN_BAND_2G) {\n"
    )
    new = (
        "\t\tch.chspec = (u16)le32_to_cpu(list->element[i]);\n"
        "\t\tcfg->d11inf.decchspec(&ch);\n"
        "\t\tif (ch.band == BRCMU_CHAN_BAND_2G)\n"
        "\t\t\tdiag_2g++;\n"
        "\t\telse if (ch.band == BRCMU_CHAN_BAND_5G)\n"
        "\t\t\tdiag_5g++;\n"
        "\t\telse\n"
        "\t\t\tdiag_other++;\n\n"
        "\t\tif (ch.band == BRCMU_CHAN_BAND_2G) {\n"
    )
    c = exactly_one(c, old, new, "CHANSPEC_CLASSIFIER")
    old = (
        "\t}\n\n"
        "fail_pbuf:\n"
        "\tkfree(pbuf);\n"
        "\treturn err;\n"
        "}\n\n"
        "static int brcmf_enable_bw40_2g"
    )
    new = (
        "\t}\n\n"
        "\t/* Only counts: no channels, calibration, identity or RF writes. */\n"
        "\tbrcmf_info(\"MZ600_5G_DIAG_CHANSPECS total=%u 2g=%u 5g=%u other=%u\\n\",\n"
        "\t\t   total, diag_2g, diag_5g, diag_other);\n\n"
        "fail_pbuf:\n"
        "\tkfree(pbuf);\n"
        "\treturn err;\n"
        "}\n\n"
        "static int brcmf_enable_bw40_2g"
    )
    c = exactly_one(c, old, new, "CHANSPEC_LOG")
    old = (
        "\t/* first entry in bandlist is number of bands */\n"
        "\tn_bands = le32_to_cpu(bandlist[0]);\n"
        "\tfor (i = 1; i <= n_bands && i < ARRAY_SIZE(bandlist); i++) {\n"
    )
    new = (
        "\t/* first entry in bandlist is number of bands */\n"
        "\tn_bands = le32_to_cpu(bandlist[0]);\n"
        "\t/* Firmware band enums only; no MAC, SSID, key or regulatory override. */\n"
        "\tbrcmf_info(\"MZ600_5G_DIAG_BANDLIST count=%u first=%u second=%u\\n\",\n"
        "\t\t   n_bands,\n"
        "\t\t   n_bands >= 1 ? le32_to_cpu(bandlist[1]) : 0,\n"
        "\t\t   n_bands >= 2 ? le32_to_cpu(bandlist[2]) : 0);\n"
        "\tfor (i = 1; i <= n_bands && i < ARRAY_SIZE(bandlist); i++) {\n"
    )
    c = exactly_one(c, old, new, "BANDLIST_LOG")
    old = (
        "\twiphy_read_of_freq_limits(wiphy);\n\n"
        "\treturn 0;\n"
        "}\n\n"
        "static s32 brcmf_config_dongle"
    )
    new = (
        "\twiphy_read_of_freq_limits(wiphy);\n"
        "\tbrcmf_info(\"MZ600_5G_DIAG_WIPHY has2g=%u has5g=%u\\n\",\n"
        "\t\t   !!wiphy->bands[NL80211_BAND_2GHZ],\n"
        "\t\t   !!wiphy->bands[NL80211_BAND_5GHZ]);\n\n"
        "\treturn 0;\n"
        "}\n\n"
        "static s32 brcmf_config_dongle"
    )
    c = exactly_one(c, old, new, "WIPHY_LOG")
    return c


def main() -> int:
    if not (CFILE.is_file() and ORIGINAL_MODULE.is_file()
            and (OUTPUT / "Module.symvers").is_file()
            and (OUTPUT / ".config").is_file()):
        raise RuntimeError("exact v064 source, output tree or matching ABI missing")
    if WORK.exists():
        raise RuntimeError("one-shot output directory already exists; inspect prior result")
    original_source = CFILE.read_bytes()
    orig_module = ORIGINAL_MODULE.read_bytes()
    preexisting_built = BUILT_MODULE.read_bytes() if BUILT_MODULE.exists() else None
    orig_text = original_source.decode("utf-8")
    revised = make_patch(orig_text)
    if "MZ600_5G_DIAG" in orig_text:
        raise RuntimeError("original source already contains diagnostic")
    modinfo = shell([str(READ_ELF), "-p", ".modinfo", str(ORIGINAL_MODULE)],
                    capture_output=True).stdout
    if f"vermagic={ABI} SMP mod_unload modversions ARMv7" not in modinfo:
        raise RuntimeError("existing module ABI/version not exact")
    if "CONFIG_MODVERSIONS=y" not in (OUTPUT / ".config").read_text():
        raise RuntimeError("module versions disabled")
    WORK.mkdir(mode=0o700, parents=False)
    # Store a small, publishable count-only source patch in the isolated
    # output directory; exact same bytes are used to compile the module.
    diff = "".join(difflib.unified_diff(
        orig_text.splitlines(keepends=True), revised.splitlines(keepends=True),
        fromfile="a/" + REL.as_posix(),
        tofile="b/" + REL.as_posix(), n=4))
    PATCH_PATH.write_text(diff)
    (WORK / "baseline-evidence.json").write_text(json.dumps({
        "original_source_sha256": sha(original_source),
        "original_module_sha256": sha(orig_module),
        "original_module_size": len(orig_module),
        "module_vermagic": ABI,
        "patch_sha256": sha(PATCH_PATH.read_bytes()),
        "patch_filename": PATCH_PATH.name,
        "running_device_modified_by_this_build": False,
    }, indent=2) + "\n")
    # Keep a safe local baseline module even if the original build output
    # becomes interrupted. Work path is private; never commit binary.
    (WORK / "brcmfmac-original-baseline.ko").write_bytes(orig_module)
    print("OFFLINE_INPUT_ABI_SHA_AND_PATCH_PREFLIGHT_PASS", flush=True)
    rc = -1
    try:
        CFILE.write_text(revised)
        command = [
            "make", "-C", str(SOURCE),
            "O=" + str(OUTPUT),
            "ARCH=arm",
            "CROSS_COMPILE=" + COMPILER + "arm-none-linux-gnueabihf-",
            "-j4",
            "M=drivers/net/wireless/broadcom/brcm80211/brcmfmac",
            "modules",
        ]
        with (WORK / "build.log").open("w") as out:
            res = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT,
                                 text=True, timeout=240)
        rc = res.returncode
        if rc != 0:
            raise RuntimeError(f"build command exit={rc}, see private build.log")
        if not BUILT_MODULE.is_file():
            raise RuntimeError("kernel M= build did not produce source-directory .ko")
        patched_module = BUILT_MODULE.read_bytes()
        if sha(patched_module) == sha(orig_module):
            raise RuntimeError("new module unchanged versus original")
        new_modinfo = shell([str(READ_ELF), "-p", ".modinfo", str(BUILT_MODULE)],
                            capture_output=True).stdout
        if f"vermagic={ABI} SMP mod_unload modversions ARMv7" not in new_modinfo:
            raise RuntimeError("new module wrong ABI")
        if not all(marker.encode() in patched_module for marker in (
                "MZ600_5G_DIAG_BANDLIST",
                "MZ600_5G_DIAG_CHANSPECS",
                "MZ600_5G_DIAG_WIPHY")):
            raise RuntimeError("instrumentation symbols missing in compiled ELF")
        TARGET.write_bytes(patched_module)
        report = {
            "result": "OFFLINE_BRCMFMAC_EXACT_ABI_COUNT_ONLY_DIAGNOSTIC_BUILD_PASS",
            "module_path": str(TARGET), "module_bytes": len(patched_module),
            "module_sha256": sha(patched_module),
            "kernel_release": ABI, "module_vermagic": new_modinfo.strip()[-260:],
            "original_module_sha256": sha(orig_module),
            "source_patch_sha256": sha(PATCH_PATH.read_bytes()),
            "reboot_or_flash": False,
            "on_xoom": False,
            "kernel_fullchip_provider_patch": False,
        }
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2), flush=True)
        return 0
    finally:
        # Restore canonical source and original build output in ALL cases.
        CFILE.write_bytes(original_source)
        ORIGINAL_MODULE.write_bytes(orig_module)
        if preexisting_built is not None:
            BUILT_MODULE.write_bytes(preexisting_built)
        elif BUILT_MODULE.exists():
            BUILT_MODULE.unlink()
        if CFILE.read_bytes() != original_source:
            raise RuntimeError("RESTORE_SOURCE_FAILED")
        if ORIGINAL_MODULE.read_bytes() != orig_module:
            raise RuntimeError("RESTORE_BASELINE_MODULE_FAILED")
        if preexisting_built is not None and BUILT_MODULE.read_bytes() != preexisting_built:
            raise RuntimeError("RESTORE_PREEXISTING_SOURCE_MODULE_FAILED")
        if preexisting_built is None and BUILT_MODULE.exists():
            raise RuntimeError("UNEXPECTED_STALE_BUILD_OUTPUT_MODULE")
        print("OFFLINE_SOURCE_AND_ORIGINAL_MODULE_RESTORED_VERIFIED", flush=True)
        print(f"BUILD_STATUS={rc}", flush=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"DIAG_OFFLINE_ABORT: {error}", file=sys.stderr, flush=True)
        sys.exit(2)
