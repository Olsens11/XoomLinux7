#!/usr/bin/env python3
"""Offline-only ARM build of existing legacy scan integration plus WIFI-4.

The broad snapshot is a temporary source prerequisite for physical testing,
NOT a canonical upstream patch-series member. No device installation.
Preserve/restore all preexisting kernel source and module outputs bytewise.
"""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[2]
lab = Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025")
kernel = lab / "v064-bigpart-linux"
output = lab / "v064-bigpart-debian-sdroot-build"
drv = kernel / "drivers/net/wireless/broadcom/brcm80211/brcmfmac"
result = lab / "v064-bcm4329-wifi1234-integrated-offline-20261027"
snapshot = root / "patches/upstream/candidate/0004-wifi-brcmfmac-bcm4329-legacy-compatibility.patch"
wifi4 = root / "patches/upstream/review-drafts/WIFI-4-brcmfmac-bcm4329-resume-firmware-for-escan.patch"
compiler = lab.parent / "toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
def sha(b):
    return hashlib.sha256(b).hexdigest()
pins = {
    drv / "cfg80211.c": "1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8",
    drv / "cfg80211.h": "89031854e21941889ca07315f693c53ef0b61b94c022bce5743cc204e003735e",
    drv / "fweh.c": "4a4c090a81e7c2a954834e98db41633f1cc5dd0a6b739edc5dbfc9b0bcd9f51c",
    drv / "fwil.h": "770964dcbe004e1df7e7c5faecda90358e44cbd2fd56f25ceb73aaaf6a296f79",
    drv / "brcmfmac.ko": "9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb",
    drv / "wcc/brcmfmac-wcc.ko": "76e5becc888c6858b9e892a75e19db7eb27f248373b4e4377da1f66c63683e58",
}
if result.exists():
    raise SystemExit("STOP: integration build already exists")
if not all(p.exists() and sha(p.read_bytes()) == h for p,h in pins.items()):
    raise SystemExit("STOP: known kernel source or module hash is different")
if not all(p.exists() for p in (snapshot, wifi4, Path(str(compiler)+"gcc"))):
    raise SystemExit("STOP: source patch or compiler missing")
subprocess.run(["git", "-C", str(kernel), "apply", "--check", str(snapshot)], check=True)
originals = {p:p.read_bytes() for p in pins}
result.mkdir(mode=0o700)
status = {}
try:
    subprocess.run(["git", "-C", str(kernel), "apply", str(snapshot)], check=True)
    subprocess.run(["git", "-C", str(kernel), "apply", "--check", str(wifi4)], check=True)
    subprocess.run(["git", "-C", str(kernel), "apply", str(wifi4)], check=True)
    subprocess.run(["git", "-C", str(kernel), "diff", "--check"], check=True)
    cmd = ["make", "-C", str(kernel), "O="+str(output), "ARCH=arm",
           "CROSS_COMPILE="+str(compiler), "M="+str(drv), "modules", "-j2"]
    with (result / "build.log").open("w") as log:
        cp = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    if cp.returncode:
        raise RuntimeError("Combined ARM build returned %d; inspect build.log" % cp.returncode)
    core = drv / "brcmfmac.ko"
    wcc = drv / "wcc/brcmfmac-wcc.ko"
    expected_core = result / "brcmfmac-bcm4329-wifi1234-integrated.ko"
    expected_wcc = result / "brcmfmac-wcc-wifi1234-integrated.ko"
    expected_core.write_bytes(core.read_bytes())
    expected_wcc.write_bytes(wcc.read_bytes())
    if sha(expected_core.read_bytes()) == pins[core]:
        raise RuntimeError("core binary identical to baseline")
    status = {
        "result": "INTEGRATED_LAB_SOURCE_OFFLINE_BUILD_PASS",
        "base_commit": "2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3",
        "snapshot_sha256": sha(snapshot.read_bytes()),
        "wifi4_sha256": sha(wifi4.read_bytes()),
        "module_name": expected_core.name,
        "module_bytes": expected_core.stat().st_size,
        "module_sha256": sha(expected_core.read_bytes()),
        "wcc_name": expected_wcc.name,
        "wcc_bytes": expected_wcc.stat().st_size,
        "wcc_sha256": sha(expected_wcc.read_bytes()),
        "firmware_installed": False,
        "on_device_test": "NOT_RUN",
        "contains_lab_scaffold_from_snapshot": True,
        "submission_ready": False
    }
finally:
    for p,data in originals.items():
        p.write_bytes(data)
    for p,dgst in pins.items():
        if sha(p.read_bytes()) != dgst:
            raise RuntimeError("CRITICAL kernel-source restoration mismatch: %s" % p)
if status:
    (result / "manifest.json").write_text(json.dumps(status,indent=2)+"\n")
    print(json.dumps(status,indent=2))
