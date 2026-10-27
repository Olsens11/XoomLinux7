#!/usr/bin/env python3
"""Offline-only isolated WIFI-4 draft compile; retain module and restore sources.

Do not install on Xoom. This patch is intentionally independent of the
unfinished WIFI-1/2/3 review extraction, not a validated connectivity image.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

repo = Path(__file__).resolve().parents[2]
lab = Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025")
kernel = lab / "v064-bigpart-linux"
out = lab / "v064-bigpart-debian-sdroot-build"
m = kernel / "drivers/net/wireless/broadcom/brcm80211/brcmfmac"
patch = repo / "patches/upstream/review-drafts/WIFI-4-brcmfmac-bcm4329-resume-firmware-for-escan.patch"
result = lab / "v064-wifi4-draft-smokebuild-20261027"
cfg, fwil, ko = m/"cfg80211.c", m/"fwil.h", m/"brcmfmac.ko"
pins = {
    cfg: "1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8",
    fwil: "770964dcbe004e1df7e7c5faecda90358e44cbd2fd56f25ceb73aaaf6a296f79",
    ko: "9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb",
}
compiler = lab.parent / "toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
def digest(blob): return hashlib.sha256(blob).hexdigest()
if result.exists():
    raise SystemExit("STOP: review smoke output exists; do not overwrite")
if not all(p.exists() and digest(p.read_bytes()) == h for p,h in pins.items()):
    raise SystemExit("STOP: pre-build source or module hash differs from known original")
if not patch.is_file() or not Path(str(compiler)+"gcc").is_file():
    raise SystemExit("STOP: patch or compiler absent")
subprocess.run(["git","-C",str(kernel),"apply","--check",str(patch)],check=True)
original = {p:p.read_bytes() for p in pins}
result.mkdir(mode=0o700)
status = {}
try:
    subprocess.run(["git","-C",str(kernel),"apply",str(patch)],check=True)
    subprocess.run(["git","-C",str(kernel),"diff","--check"],check=True)
    cmd = ["make","-C",str(kernel),"O="+str(out),"ARCH=arm","CROSS_COMPILE="+str(compiler),"M="+str(m),"modules","-j2"]
    with (result/"build.log").open("w") as log:
        p = subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    if p.returncode:
        raise RuntimeError("WIFI-4 exact ARM compile failed, see build.log")
    built = ko.read_bytes()
    if digest(built) == pins[ko]:
        raise RuntimeError("module unchanged after patch compile")
    artifact = result/"brcmfmac-wifi4-standalone-draft.ko"
    artifact.write_bytes(built)
    status = dict(
        outcome="WIFI4_STANDALONE_ARM_COMPILE_PASS",
        module_name=artifact.name,module_sha256=digest(built),
        module_bytes=len(built),patch_sha256=digest(patch.read_bytes()),
        kernel="7.0.0-next-20260422+",firmware_or_hardware_touched=False,
        after_wifi123_integration=False,ready_for_association=False,
    )
finally:
    for path,data in original.items():
        path.write_bytes(data)
    for path,dgst in pins.items():
        if digest(path.read_bytes()) != dgst:
            raise RuntimeError("CRITICAL: failed to restore "+str(path))
if status:
    (result/"offline-build-result.json").write_text(json.dumps(status,indent=2)+"\n")
    print(json.dumps(status,indent=2))
