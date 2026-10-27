#!/usr/bin/env python3
"""Assemble clean-base Xoom Linux 7 kernel patch CANDIDATES.

One patch per current logical function, NO chronological experimental overlays.
Never edits live Linux tree or invokes a physical device. Development-only
metadata lives outside patch files; no forged Signed-off-by/physical claims.
Require exact upstream base and explicit input hashes before each assembly.
"""
from __future__ import annotations
import difflib
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PROJECT=Path(__file__).resolve().parents[2]
TREE=Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/v064-bigpart-linux")
BASE="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
DEST=PROJECT/"patches"/"upstream"/"candidate"
FILES={
"board":"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray.dts",
"makefile":"arch/arm/boot/dts/nvidia/Makefile",
"mac":"arch/arm/boot/compressed/atags_to_fdt.c",
"kconfig":"block/partitions/Kconfig",
"efi":"block/partitions/efi.c",
"wifi":"drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c",
"event":"drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c",
"header":"drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.h",
}
DTS_SOURCE=TREE/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts"
NAMES=[
"0001-arm-dts-tegra20-motorola-stingray-board.patch",
"0002-arm-tegra-stingray-wlan-mac-atag.patch",
"0003-block-partitions-motorola-xoom-bigpart.patch",
"0004-wifi-brcmfmac-bcm4329-legacy-compatibility.patch",
]

def git(*args,cwd=TREE):
    return subprocess.check_output(["git",*args],cwd=cwd)

def sha(b):return hashlib.sha256(b).hexdigest()

def baseline(rel):
    return git("show",f"{BASE}:{rel}")

def component(rel,after):
    before=baseline(rel)
    assert after!=before,rel
    assert after.endswith(b"\n"),rel
    return before,after

def patch_hunk(rel,before,after):
    oldname="a/"+rel if before is not None else "/dev/null"
    newname="b/"+rel
    out=[f"diff --git a/{rel} b/{rel}\n"]
    if before is None:
        out.append("new file mode 100644\n")
    prior=[] if before is None else before.decode("utf-8").splitlines(keepends=True)
    future=after.decode("utf-8").splitlines(keepends=True)
    ud=list(difflib.unified_diff(prior,future,fromfile=oldname,tofile=newname,n=3))
    if not ud:
        raise AssertionError("Empty patch "+rel)
    return "".join(out+ud)

def load_v29():
    root=PROJECT/"tools"/"forensics"
    p=root/"build_mz600_v29_regulatory_preserving_native_scan.py"
    spec=importlib.util.spec_from_file_location("mz600_canonical_source",p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def wifi_sources():
    mod=load_v29()
    # For extraction only: prepare a temporary clean cfg80211.c plus the
    # original historical channel fallback input. The OUTPUT is ONE delta
    # from upstream, not a patch atop that historical fallback.
    rel=FILES["wifi"]
    original=baseline(rel)
    with tempfile.TemporaryDirectory(prefix="mz600-canonical-input-") as tmp:
        root=Path(tmp);f=root/rel;f.parent.mkdir(parents=True)
        f.write_bytes(original)
        historical_patch=mod.base.PATCH
        subprocess.run(["patch","--batch","--forward","-p1","-i",str(historical_patch)],
                       cwd=root,check=True,stdout=subprocess.DEVNULL)
        staged=f.read_text()
    cfg=mod.base.instrument(staged).encode()
    fweh=mod.base.instrument_fweh(baseline(FILES["event"]).decode()).encode()
    hdr=mod.v28.v26.v25.v24.instrument_header(
        baseline(FILES["header"]).decode()).encode()
    # Current candidate reflects fully normal cfg80211 scanning. Strictly
    # disallow resurrected lab-only scan policy in final generated source.
    assert b"controlled single-channel NO_IR PASSIVE" not in cfg
    assert b"BRCMF_C_SET_PASSIVE_SCAN, 1" not in cfg
    assert b"passive_time = cpu_to_le32(500)" not in cfg
    assert b"MZ600_V29_LEGACY_VALID_CHANNEL_FALLBACK" in cfg
    assert b"channel->flags |= IEEE80211_CHAN_NO_HT40" in cfg
    assert b"mz600_generation" in cfg
    assert b"BRCMF_E_ESCAN_RESULT" in fweh
    return {FILES["wifi"]:(original,cfg),
            FILES["event"]:(baseline(FILES["event"]),fweh),
            FILES["header"]:(baseline(FILES["header"]),hdr)}

def main():
    if git("rev-parse","HEAD").decode().strip()!=BASE:
        raise SystemExit("STOP: kernel base tree changed")
    refresh=sys.argv[1:]==["--refresh"]
    if len(sys.argv)>1 and not refresh:
        raise SystemExit("STOP: only explicit --refresh option is supported")
    if DEST.exists():
        if not refresh:
            raise SystemExit("STOP: candidate exists; use explicit --refresh after review")
        old_manifest=json.loads((DEST/"candidate-manifest.json").read_text())
        if old_manifest["base"]!=BASE or [x["patch"] for x in old_manifest["series"]]!=NAMES:
            raise SystemExit("STOP: candidate manifest differs")
        for item in old_manifest["series"]:
            if sha((DEST/item["patch"]).read_bytes())!=item["sha256"]:
                raise SystemExit("STOP: manually edited candidate patch must be reconciled first")
    elif refresh:
        raise SystemExit("STOP: no existing candidate for refresh")
    # Prevent silent changes in the authoritative source artifacts.
    if sha((TREE/FILES["wifi"]).read_bytes()) != \
       "1cb2c600fe401245cd218589d4bc3325f9ac0c0a15bd26ed1576c55eb3d85eb8":
        raise SystemExit("STOP: baseline brcmfmac source changed")
    if sha(DTS_SOURCE.read_bytes())=="0"*64:
        raise SystemExit("STOP: no DTS source")
    dt=DTS_SOURCE.read_text()
    if not all(x in dt for x in ('"motorola,stingray"','motorola,xoom-bigpart','wifi@1')):
        raise SystemExit("STOP: board identity / storage / WLAN nodes missing")
    # Canonical board filename; do NOT falsely claim this DT has been rebuilt
    # or hardware booted under its normalized name.
    dt=dt.replace(
        "// XoomLinux7 isolated clean-upstream USB-only test. NOT an upstream source patch.\n",
        "")
    dt=dt.replace("Motorola Xoom (Stingray MZ600 minimal USB diagnostic)",
                  "Motorola Xoom (Stingray)")
    # Formatting only: remove whitespace that Linux git apply/checkpatch rejects.
    dt=re.sub(r"^ +\t", "\t", dt, flags=re.MULTILINE)
    dt="\n".join(line.rstrip() for line in dt.splitlines())+"\n"
    makefile=(TREE/FILES["makefile"]).read_text()
    old="tegra20-motorola-stingray-clean-usb.dtb"
    assert makefile.count(old)==1
    makefile=makefile.replace(old,"tegra20-motorola-stingray.dtb")
    steps=[
        {FILES["makefile"]:component(FILES["makefile"],makefile.encode()),
         FILES["board"]:(None,dt.encode())},
        {FILES["mac"]:component(FILES["mac"],(TREE/FILES["mac"]).read_bytes())},
        {FILES["kconfig"]:component(FILES["kconfig"],(TREE/FILES["kconfig"]).read_bytes()),
         FILES["efi"]:component(FILES["efi"],(TREE/FILES["efi"]).read_bytes())},
        wifi_sources(),
    ]

    # Whitespace normalization only; do not change runtime code semantics.
    final_wifi=steps[3]
    for rel,(before,after) in list(final_wifi.items()):
        after=(("\n".join(line.rstrip() for line in after.decode().splitlines())+"\n").encode())
        final_wifi[rel]=(before,after)
    rendered=[]
    for files in steps:
        rendered.append("".join(patch_hunk(rel,*value) for rel,value in files.items()))
    # Test every patch as a single clean-base series in a scratch filesystem.
    with tempfile.TemporaryDirectory(prefix="mz600-canonical-verify-") as tmp:
        target=Path(tmp)
        for files in steps:
            for rel,(before,_) in files.items():
                p=target/rel
                if before is not None and not p.exists():
                    p.parent.mkdir(parents=True,exist_ok=True)
                    p.write_bytes(before)
        for n,body in zip(NAMES,rendered):
            patch=target/n
            patch.write_text(body)
            subprocess.run(["git","apply","--check",str(patch)],cwd=target,check=True)
            subprocess.run(["git","apply",str(patch)],cwd=target,check=True)
        for group in steps:
            for rel,(_,after) in group.items():
                assert (target/rel).read_bytes()==after,rel
    # Only once checks pass: create the standalone canonical candidates.
    DEST.mkdir(parents=True,exist_ok=refresh)
    for name,body in zip(NAMES,rendered):
        (DEST/name).write_text(body)
    (DEST/"series").write_text("\n".join(NAMES)+"\n")
    manifest={
      "base":BASE,"kernel_tree":str(TREE),
      "series":[{"index":i+1,"patch":name,"sha256":sha(body.encode()),
                 "files":list(step),"status":
                  "source-only board candidate (renamed; not separately booted)" if i==0 else
                  "earlier MAC logic hardware-tested; canonical file not separately booted" if i==1 else
                  "BigPart p8 physically booted; source diff needs submission review" if i==2 else
                  "V29 regulator-preserving source OFFLINE build; physical WiFi evidence belongs to earlier V28"} for i,(name,body,step) in enumerate(zip(NAMES,rendered,steps))],
      "validation":"all four patches pass sequential clean-base git apply --check and byte-for-byte replay; no fresh compile/run claimed",
      "unresolved":[
        "WiFi: after first working normal multichannel scan, repeated ESCAN returned firmware BCME_NOTUP (-4); exact firmware ready/power lifecycle unresolved",
        "WiFi: race-safe cancel/timeout/duplicate/lifetime and matching event generation; multi-interface and P2P unresolved",
        "WiFi: V29 regulatory-safe fallback compiled offline; normal V28 12-BSS scan was physically verified but regulatory-safe canonical candidate not independently tested",
        "WiFi: ordinary association/authentication/DHCP and multidevice validation not yet established",
        "Board: normal filename and bindings, power supplies, Bluetooth, SDIO and DT validation require separate review/testing",
        "BigPart: in-memory exact geometry, boot command-line and board selector must be audited for generic kernel maintainability",
        "Kernel patches do not represent Debian rootfs, firmware, private NVRAM, initramfs, or userspace services",
        "Candidate still contains diagnostic scaffolding inherited from tests; remove before submission and verify again",
      ],
    }
    (DEST/"candidate-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("CANONICAL_CANDIDATE_SERIES_REFRESHED" if refresh else "CANONICAL_CANDIDATE_SERIES_CREATED")
    for item in manifest["series"]:
        print(item["index"],item["patch"],item["sha256"][:16],item["status"])
    print("CLEAN_UPSTREAM_APPLICATION_PASS")
    print("NO_XOOM_ACCESS_NO_FIRMWARE_CHANGES_NO_UPSTREAM_SUBMISSION")
if __name__=="__main__":main()
