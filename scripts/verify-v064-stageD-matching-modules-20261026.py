#!/usr/bin/env python3
"""Read-only acceptance checks for replacement MZ600 native Stage-D module bundle."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

RELEASE = "7.0.0-next-20260422+"
BUNDLE = "MZ600-v064-Linux7-7.0.0-next-20260422plus-matching-modules-OFFLINE-UNDEPLOYED.tar.xz"
BUNDLE_SHA = "50d821138f0fe04f79855d8996a61652fa7788e48457a9ebf97409b527db11c6"
KERNEL_ZIMAGE_SHA = "d0ada47734cd7686f780cb37f9abb95e354a80d333840c7979b756053fe6a9d1"
KERNEL_VMLINUX_SHA = "02fe5350955156bdfa0020f6eefa4628c73cf7cacff50ba9058420ad22745dae"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact-dir", type=Path, required=True)
    p.add_argument("--build-dir", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    bundle = args.artifact_dir / BUNDLE
    root = args.artifact_dir / "staging/lib/modules" / RELEASE
    assert bundle.is_file() and bundle.stat().st_size == 1901356
    assert sha256(bundle) == BUNDLE_SHA
    assert (args.build_dir / "include/config/kernel.release").read_text().strip() == RELEASE
    assert sha256(args.build_dir / "arch/arm/boot/zImage") == KERNEL_ZIMAGE_SHA
    assert sha256(args.build_dir / "vmlinux") == KERNEL_VMLINUX_SHA
    assert (args.build_dir / "Module.symvers").is_file()
    expected = ["brcmfmac.ko", "brcmfmac-wcc.ko", "brcmutil.ko",
                "btbcm.ko", "hci_uart.ko", "bluetooth.ko"]
    modules = sorted(root.rglob("*.ko"))
    assert len(modules) == 114, f"Unexpected module count: {len(modules)}"
    names = {m.name for m in modules}
    assert set(expected).issubset(names), sorted(set(expected) - names)
    hashes = {}
    for module in modules:
        release = subprocess.check_output(
            ["modinfo", "-F", "vermagic", str(module)], text=True
        ).strip()
        assert release.startswith(RELEASE + " SMP mod_unload modversions ARMv7"), (
            module.name, release
        )
        hashes[str(module.relative_to(root))] = sha256(module)
    for name in ["modules.dep", "modules.dep.bin", "modules.alias", "modules.order"]:
        assert (root / name).is_file(), name
    brcm_dependencies = subprocess.check_output([
        "modprobe", "-d", str(args.artifact_dir / "staging"),
        "-S", RELEASE, "--show-depends", "brcmfmac"
    ], text=True)
    assert "brcmutil.ko" in brcm_dependencies and "brcmfmac.ko" in brcm_dependencies
    with tarfile.open(bundle, "r:xz") as t:
        members = t.getmembers()
    archive_kos = [m for m in members if m.name.endswith(".ko") and m.isfile()]
    assert len(archive_kos) == 114
    assert all(m.name.startswith("lib/modules/" + RELEASE + "/") or
               (m.isdir() and m.name == "lib/modules/" + RELEASE) for m in members)
    assert all(not m.issym() and not m.islnk() for m in members)
    assert all(".." not in Path(m.name).parts for m in members)
    manifest = {
        "classification": "OFFLINE_STAGED_ONLY_NOT_INSTALLED_ON_XOOM",
        "device": "replacement Motorola Xoom MZ600; protected original excluded",
        "runtime_kernel_release": RELEASE,
        "kernel_zimage_sha256_unmodified": KERNEL_ZIMAGE_SHA,
        "kernel_vmlinux_sha256_unmodified": KERNEL_VMLINUX_SHA,
        "archive_filename": BUNDLE,
        "archive_sha256": BUNDLE_SHA,
        "archive_bytes": bundle.stat().st_size,
        "module_count": len(modules),
        "vermagic_and_modversions_all_match": True,
        "modprobe_brcmfmac_requires_brcmutil": True,
        "contains_separate_wcc_vendor_module": True,
        "module_sha256_by_relative_path": hashes,
        "installed_on_live_device": False,
        "radio_activated": False,
        "boot_partition_modified": False
    }
    print(json.dumps({k: v for k, v in manifest.items() if k != "module_sha256_by_relative_path"}, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            raise SystemExit("Manifest already exists; refusing overwrite")
        args.output.write_text(json.dumps(manifest, indent=2) + "\n")
        print("Manifest saved:", args.output)

if __name__ == "__main__":
    main()
