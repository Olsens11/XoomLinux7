#!/usr/bin/env python3
"""Offline-only v06.4 ARMHF dependency / image-capacity audit.

Does not touch the tablet, download packages, stage private binaries, flash,
or alter the existing v06.3 artifact. All output is local and sanitized.
This is a PREFLIGHT, not the v06.4 image builder or acceptance test.
"""
import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
from collections import deque
from pathlib import Path

BASE = Path("/home/xoomdev/xoom-linux-rom")
WORK = BASE / "clean-wifi-bt-usb-20261025"
ROOT = BASE / "os-build/bookworm-armhf-root"
IMAGE = WORK / "artifacts-embedded-v063/MZ600-CLEAN-WIFI-BT-USB-v063-HCD-RAM-ONLY-UNTESTED.img"
CPIO = WORK / "artifacts-embedded-v063/v063-private-bcm4329b1-firmware.cpio.gz"
CONFIG = WORK / "build/.config"
EXPECTED_V063 = "07950963496de68cf53b7d0218ed71450252450846768f065b0f36a37cb6743e"
LIMIT = 8 * 1024 * 1024
CANDIDATES = {
    "dash": ["/bin/dash"],
    "iproute2_ip": ["/bin/ip", "/usr/sbin/ip"],
    "iw": ["/usr/sbin/iw"],
    "busybox": ["/bin/busybox", "/usr/bin/busybox"],
    "bluetoothd": ["/usr/lib/bluetooth/bluetoothd", "/usr/libexec/bluetooth/bluetoothd"],
    "bluetoothctl": ["/usr/bin/bluetoothctl"],
    "dbus-daemon": ["/usr/bin/dbus-daemon"],
    "getty": ["/sbin/getty", "/usr/sbin/agetty"],
}
LIBDIRS = [
    "lib/arm-linux-gnueabihf", "usr/lib/arm-linux-gnueabihf",
    "lib", "usr/lib", "lib/arm-linux-gnueabihf/blas",
]

def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cmd(*args):
    return subprocess.run(args, text=True, capture_output=True, check=False)

def find_file(root, name):
    for d in LIBDIRS:
        p = root / d / name
        if p.exists():
            return p
    return None

def deps_for(p):
    r = cmd("readelf", "-d", str(p))
    if r.returncode:
        return [], "readelf_failed: " + r.stderr.strip()[:120]
    return re.findall(r"\(NEEDED\)\s+Shared library: \[([^]]+)\]", r.stdout), None

def interp_for(p):
    r = cmd("readelf", "-l", str(p))
    matches = re.findall(r"Requesting program interpreter:\\s*([^]]+)", r.stdout)
    return matches[0] if matches else None

def closure(root, start):
    q = deque([start])
    seen, missing = {}, set()
    while q:
        p = q.popleft()
        if not p.exists():
            missing.add(p.name)
            continue
        key = str(p.resolve())
        if key in seen:
            continue
        needed, error = deps_for(p)
        if error:
            missing.add(p.name + ": " + error)
            continue
        seen[key] = p
        interpreter = interp_for(p)
        if interpreter:
            target = root / interpreter.lstrip("/")
            if target.exists():
                q.append(target)
            else:
                missing.add(interpreter)
        for lib in needed:
            libpath = find_file(root, lib)
            if libpath:
                q.append(libpath)
            else:
                missing.add(lib)
    raw_bytes = sum(Path(k).stat().st_size for k in seen)
    # Only a diagnostic gzip proxy: actual kernel zImage difference may differ.
    z = gzip.compress(b"".join(Path(k).read_bytes() for k in sorted(seen)), compresslevel=9, mtime=0)
    return {
        "files": [str(p.relative_to(root)) for p in sorted(seen.values())],
        "raw_bytes": raw_bytes,
        "gzip_content_proxy_bytes": len(z),
        "unresolved_dependencies": sorted(missing),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, default=WORK / "artifacts-embedded-v064-preflight/PREFLIGHT.json")
    a = ap.parse_args()
    if not a.root.is_dir():
        raise SystemExit("Missing ARMHF sysroot")
    if not IMAGE.exists() or sha_file(IMAGE) != EXPECTED_V063:
        raise SystemExit("v06.3 immutable input absent or SHA mismatch")
    if not CPIO.exists() or not CONFIG.exists():
        raise SystemExit("Missing v06.3 CPIO or kernel config")
    cfg = CONFIG.read_text()
    examined = {}
    for name, choices in CANDIDATES.items():
        p = next((a.root / n.lstrip("/") for n in choices if (a.root / n.lstrip("/")).exists()), None)
        if p is None:
            examined[name] = {"available": False}
            continue
        record = {"available": True, "path": "/" + str(p.relative_to(a.root)), **closure(a.root, p)}
        record["elf_machine"] = (cmd("readelf", "-h", str(p)).stdout.split("Machine:")[-1].splitlines()[0].strip())
        record["arm_attributes_neon_mentions"] = "NEON" in cmd("readelf", "-A", str(p)).stdout
        examined[name] = record
    image_size = IMAGE.stat().st_size
    regdb = [(s, (a.root / s.lstrip("/")).exists()) for s in
             ("/lib/firmware/regulatory.db", "/lib/firmware/regulatory.db.p7s",
              "/usr/lib/firmware/regulatory.db", "/usr/lib/firmware/regulatory.db.p7s")]
    report = {
        "classification": "OFFLINE PREFLIGHT ONLY; no image built; no device access",
        "starting_image_sha256": EXPECTED_V063,
        "starting_image_bytes": image_size,
        "legacy_ram_image_limit_bytes": LIMIT,
        "available_compressed_image_headroom_bytes": LIMIT - image_size,
        "embedded_cpio_compressed_bytes": CPIO.stat().st_size,
        "vt_enabled": "CONFIG_VT=y" in cfg,
        "vt_console_enabled": "CONFIG_VT_CONSOLE=y" in cfg,
        "fbcon_enabled": "CONFIG_FRAMEBUFFER_CONSOLE=y" in cfg,
        "signed_regdb_required": "CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y" in cfg,
        "signed_regdb_sysroot_files": dict(regdb),
        "hidp_kernel_module_present": (WORK / "build/net/bluetooth/hidp/hidp.ko").exists(),
        "candidates": examined,
        "packaging_decision": "DEFERRED: missing BlueZ and signed regulatory database; exact incremental zImage must be measured",
        "no_flash_no_device_access": True,
    }
    if a.out.is_file():
        raise SystemExit("Refusing to overwrite existing preflight report: " + str(a.out))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n")
    print("V064_PREFLIGHT_SAVED", a.out)
    print("v063_image_bytes", image_size, "headroom_bytes", LIMIT-image_size)
    for name, item in examined.items():
        if item["available"]:
            print(name, "raw", item["raw_bytes"],
                  "gzip_proxy", item["gzip_content_proxy_bytes"],
                  "missing", item["unresolved_dependencies"],
                  "neon_mentioned", item["arm_attributes_neon_mentions"])
        else:
            print(name, "MISSING")
    print("NOT A BUILD OR A PHYSICAL PASS")

if __name__ == "__main__":
    main()
