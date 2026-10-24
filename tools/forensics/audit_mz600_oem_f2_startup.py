#!/usr/bin/env python3
"""Read-only provenance and startup-order checks for MZ600 BCM4329 OEM vs Linux 7.

Private OEM binary/firmware/calibration must never be added to public Git.
This script reads local pinned *source* trees and optionally an OEM ELF.
It does not access any device, network, GPIO, PMU, firmware, or block device.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

OEM = "drivers/net/wireless/bcm4329/"
L7 = "drivers/net/wireless/broadcom/brcm80211/brcmfmac/"

EXPECTED = {
    "oem/dhd_linux.c": "d9eaaad014d25fbac09c46e92ff09c0c70aefa027f657d2979e088fc9d44ae92",
    "oem/dhd_sdio.c": "e8ad9ef7bac25f6ba82140e1b44387ce537bd484bfbfe38289b923eadba2d016",
    "oem/siutils.c": "1d30a5c249c6a05c3fef59cedf4705a278c04c86dea3e334c48a1f70b3eeb092",
    "oem/board-stingray-wifi.c": "e8b92a268bca6bc1c7798159d731117022223c45e8926b7307987e9b74ccb494",
    "linux/sdio.c": "74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab",
    "linux/chip.c": "932e25c75f9ea5247194dfdb78c6b41a457af68d7a558935a7b5489bf548aa9d",
}

def context(text, marker, size=7500, last=False):
    pos = text.rfind(marker) if last else text.find(marker)
    if pos < 0:
        raise ValueError("source marker absent: " + marker)
    return text[pos:pos + size]

def in_order(text, *markers):
    cursor = 0
    for marker in markers:
        pos = text.find(marker, cursor)
        if pos < 0:
            return False
        cursor = pos + len(marker)
    return True

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--oem-root", required=True, type=Path, help="Locally cached source root for Motorola kernel 2a65edc")
    ap.add_argument("--linux-root", required=True, type=Path, help="Locally cached source root for upstream Linux pinned 2404d273...")
    ap.add_argument("--module", type=Path, help="Optional PRIVATE HRI39/HRI66 bcm4329.ko; only symbols/hash are checked")
    args = ap.parse_args()
    sources = {
        "oem/dhd_linux.c": args.oem_root / OEM / "dhd_linux.c",
        "oem/dhd_sdio.c": args.oem_root / OEM / "dhd_sdio.c",
        "oem/siutils.c": args.oem_root / OEM / "siutils.c",
        "oem/board-stingray-wifi.c": args.oem_root / "arch/arm/mach-tegra/board-stingray-wifi.c",
        "linux/sdio.c": args.linux_root / L7 / "sdio.c",
        "linux/chip.c": args.linux_root / L7 / "chip.c",
    }
    passes, failures = [], []
    def check(name, ok):
        (passes if ok else failures).append(name)
        print(("PASS" if ok else "FAIL") + " " + name)

    code = {}
    for key, path in sources.items():
        try:
            raw = path.read_bytes()
            code[key] = raw.decode("utf-8", errors="replace")
            check("exact public-source SHA " + key, hashlib.sha256(raw).hexdigest() == EXPECTED[key])
        except (OSError, UnicodeError) as exc:
            check("source accessible " + key, False)
            print("  error:", type(exc).__name__)
    if len(code) != len(sources):
        return 1

    oemdhd = code["oem/dhd_linux.c"]
    oemsdio = code["oem/dhd_sdio.c"]
    si = code["oem/siutils.c"]
    board = code["oem/board-stingray-wifi.c"]
    l7sdio = code["linux/sdio.c"]
    chip = code["linux/chip.c"]

    cases = [
        ("OEM platform power before card detection", context(oemdhd, "static int wifi_probe(", 850),
         ("wifi_set_power(1, 0)", "wifi_set_carddetect(1)")),
        ("OEM staged shared U4 + WLAN U2 release", context(board, "stingray_wifi_power(int on)", 450),
         ("mdelay(100)", "change_power_brcm_4329(on)", "mdelay(100);\n\tgpio_set_value", "mdelay(200)")),
        ("OEM enter firmware download disables ARM and resets SOCRAM", context(oemsdio, "dhdsdio_download_state(dhd_bus_t *bus, bool enter)", 3000, True),
         ("si_core_disable(bus->sih, 0)", "si_core_reset(bus->sih, 0, 0)", "/* Clear the top bit of memory */")),
        ("OEM release writes vars, clears interrupts, resets ARM", context(oemsdio, "dhdsdio_download_state(dhd_bus_t *bus, bool enter)", 3600, True),
         ("dhdsdio_write_vars(bus)", "W_SDREG(0xFFFFFFFF", "si_core_reset(bus->sih, 0, 0)")),
        ("OEM firmware code then NVRAM then CPU release", context(oemsdio, "_dhdsdio_download_firmware(struct dhd_bus *bus)", 2750, True),
         ("dhdsdio_download_code_file", "dhdsdio_download_nvram(bus)", "dhdsdio_download_state(bus, FALSE)")),
        ("OEM HT-clock mailbox IOEx IORx ordering", context(oemsdio, "dhd_bus_init(dhd_pub_t *dhdp, bool enforce_mutex)", 2600, True),
         ("dhdsdio_clkctl(bus, CLK_AVAIL", "SBSDIO_FORCE_HT", "tosbmailboxdata", "SDIOD_CCCR_IOEN", "SDIOD_CCCR_IORDY")),
        ("OEM ALP clock preparation", context(si, "si_buscore_prep(si_info_t *sii", 1800, True),
         ("SBSDIO_ALP_AVAIL_REQ", "SBSDIO_FORCE_ALP", "SBSDIO_FUNC1_SDIOPULLUP")),
        ("Linux 7 ALP clock preparation", context(l7sdio, "brcmf_sdio_buscoreprep(void *ctx)", 2200),
         ("SBSDIO_ALP_AVAIL_REQ", "SBSDIO_FORCE_ALP", "SBSDIO_FUNC1_SDIOPULLUP")),
        ("Linux 7 firmware download then CPU activate", context(l7sdio, "brcmf_sdio_download_firmware(struct brcmf_sdio *bus", 1800),
         ("brcmf_sdio_download_code_file", "brcmf_sdio_download_nvram", "brcmf_chip_set_active")),
        ("Linux 7 F2 mailbox then ready request", context(l7sdio, "brcmf_sdio_firmware_callback(struct device *dev", 2150),
         ("SBSDIO_FORCE_HT", "tosbmailboxdata", "sdio_enable_func(sdiod->func2)")),
        ("Linux 7 CM3 clears interrupts before reset release", context(chip, "brcmf_chip_cm3_set_active(struct brcmf_chip_priv *chip)", 600),
         ("chip->ops->activate", "brcmf_chip_resetcore")),
    ]
    for name, section, markers in cases:
        check(name, in_order(section, *markers))

    check("OEM firmware owns PMU initialization policy", "Skip PMU initialization from the Dongle Host" in si)
    check("OEM clears ChipCommon GPIO pull registers", "W_REG(osh, &cc->gpiopullup, 0)" in si and "W_REG(osh, &cc->gpiopulldown, 0)" in si)
    check("Linux 7 programs PMU state-reload control", "BCMA_CC_PMU_CTL_RES_RELOAD" in l7sdio)
    check("Linux 7 configures SDIO reset to include backplane reset", "SDIO_CCCR_BRCM_CARDCTRL_WLANRESET" in l7sdio)

    if args.module:
        try:
            raw = args.module.read_bytes()
            expected = "4bf267fb432deb068a38849d87c744a2397ef4a7c7fc79476e265f3571d4ab0f"
            check("original MZ600 ELF SHA", hashlib.sha256(raw).hexdigest() == expected)
            result = subprocess.run(["nm", str(args.module)], check=True, capture_output=True, text=True).stdout
            for name in ["wifi_probe", "dhd_module_init", "dhd_bus_init", "dhdsdio_download_state", "si_doattach"]:
                check("original ELF contains " + name, any(line.split()[-1] == name for line in result.splitlines() if line.split()))
        except (OSError, subprocess.CalledProcessError) as exc:
            check("private OEM ELF available", False)
            print("  error:", type(exc).__name__)

    print("CHECKS:", len(passes), "passed,", len(failures), "failed")
    print("LIMIT: text/source/symbol checks only; not runtime, recompilation, GPIO voltage, PMU or firmware execution proof")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
