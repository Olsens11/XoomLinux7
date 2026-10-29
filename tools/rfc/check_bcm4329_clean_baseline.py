#!/usr/bin/env python3
"""One-time, read-only proof that the new BCM4329 RFC starts at Linux upstream.

This is a BOOTSTRAP check. It is expected to FAIL after the first new RFC
patch is committed; do not weaken it to make later amended trees pass.
It never modifies a Git checkout, firmware, kernel, or physical device.
"""
from pathlib import Path
import argparse
import subprocess


PINNED = "2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"


def git(source: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(source), *args], text=True
    ).strip()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("linux_source", type=Path)
    a = p.parse_args()
    source = a.linux_source.resolve()
    assert git(source, "rev-parse", "HEAD") == PINNED, (
        "This is not the clean upstream baseline"
    )
    assert not git(source, "status", "--porcelain"), (
        "This checkout already has uncommitted edits"
    )
    assert git(source, "rev-list", "--count", f"{PINNED}..HEAD") == "0"
    br = git(source, "branch", "--show-current")
    assert br == "rfc/bcm4329-minimal-2ghz-20261029", br

    d = source / "drivers/net/wireless/broadcom/brcm80211/brcmfmac"
    sdio = (d / "sdio.c").read_text()
    cfg = (d / "cfg80211.c").read_text()
    chip = (d / "chip.c").read_text()
    assert "BRCMF_FW_ENTRY(BRCM_CC_4329_CHIP_ID" in sdio
    assert "bcm4329" in chip.lower()
    assert "brcmf_cfg80211_scan(" in cfg
    assert "brcmf_cfg80211_connect(" in cfg
    assert "brcmf_construct_chaninfo(" in cfg
    assert 'brcmf_fil_iovar_data_get(ifp, "chanspecs"' in cfg
    assert "brcmf_cfg80211_reg_notifier(" in cfg
    assert 'BRCMF_C_GET_VALID_CHANNELS' in (d / "fwil.h").read_text()
    board = source / "arch/arm/boot/dts/nvidia"
    assert (board / "tegra20-motorola-wingray.dts").exists()
    assert not (board / "tegra20-motorola-stingray.dts").exists()

    print("PASS: exact upstream commit", PINNED)
    print("PASS: independently named RFC source branch and zero applied patches")
    print("PASS: BCM4329 SDIO/firmware mapping exists in upstream")
    print("PASS: upstream cfg80211 scan, connection and country hooks exist")
    print("PASS: modern chanspecs required, legacy command already defined")
    print("PASS: Wingray present, Stingray MZ600 DTS not yet implemented")
    print("NOT TESTED: 2.4GHz scanning, association, regulatory behavior or boot")
    print("NOT AN RFC IMPLEMENTATION OR HARDWARE ACCEPTANCE")


if __name__ == "__main__":
    main()
