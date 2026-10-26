#!/usr/bin/env python3
"""Offline only: root=/dev/mmcblk0p8 diagnostic variant of verified SD Stage-B.

Do not confuse this TEMP fastboot boot candidate with a permanent installed ROM.
No device contact, no private PARTUUID, no recovery/eMMC writes. Prefer the
standard PARTUUID design after diagnosing why Stage-C does not reach USB login.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

STAGE_B_HASH = "b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba"
IMAGE_BYTES = 6645760
EXPECTED_NAME = "MZ600-V064-BIGPART-INTERNAL-P8-DEVNODE-TEMPBOOT-OFFLINE-UNTESTED.img"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.destination.exists() or args.destination.name != EXPECTED_NAME:
        raise RuntimeError("Refuse to overwrite or use an unexpected output name")
    source = args.source.read_bytes()
    if len(source) != IMAGE_BYTES or digest(source) != STAGE_B_HASH:
        raise RuntimeError("Stage-B source image SHA256 or size mismatch")
    if source[:8] != b"ANDROID!":
        raise RuntimeError("Expected Android boot v0 magic")
    fields = struct.unpack_from("<10I", source, 8)
    kernel_len, _, ramdisk_len, _, second_len, _, _, page, dt_len, _ = fields
    if page != 2048 or kernel_len < 5000000 or ramdisk_len < 1024 or second_len or dt_len:
        raise RuntimeError("Unexpected Android boot image header geometry")
    cmdline = source[64:576].split(b"\0", 1)[0]
    roots = re.findall(rb"(?<!\S)root=PARTUUID=([^\s\x00]+)", cmdline)
    if len(roots) != 1 or not re.fullmatch(rb"[a-fA-F0-9]{8}-[0-9]{2}", roots[0]):
        raise RuntimeError("Stage-B root selector no longer matches known SD geometry")
    if not (b"rootwait" in cmdline and b"rootfstype=ext4" in cmdline and b"init=/sbin/init" in cmdline):
        raise RuntimeError("Expected root safety/entry options missing")
    cmdline_alt = cmdline.replace(b"root=PARTUUID=" + roots[0], b"root=/dev/mmcblk0p8", 1)
    if len(cmdline_alt) >= 512:
        raise RuntimeError("Boot image command line capacity exceeded")
    image = bytearray(source)
    image[64:576] = cmdline_alt.ljust(512, b"\0")
    if image[:64] != source[:64] or image[576:] != source[576:]:
        raise RuntimeError("Non-command-line boot image bytes changed")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_bytes(image)
    metadata = {
        "stage_b_source_sha256": STAGE_B_HASH,
        "candidate_sha256": digest(image),
        "image_bytes": len(image),
        "root_selector": "/dev/mmcblk0p8",
        "difference_from_stage_b": "Android v0 cmdline field only",
        "status": "HOST_OFFLINE_UNTESTED_TEMPBOOT_ONLY_NO_FLASH",
        "purpose": "Distinguish p8 GPT PARTUUID lookup from p8 block-device mount problems",
    }
    manifest = args.destination.with_suffix(".manifest.json")
    if manifest.exists():
        raise RuntimeError("Manifest file already exists")
    manifest.write_text(json.dumps(metadata, indent=2) + "\n")
    print("MZ600_DIAGNOSTIC_STAGE_D_OFFLINE_CANDIDATE_CREATED")
    print("sha256", digest(image))
    print("bytes", len(image))
    print("NO_EMMC_WRITES_NO_FLASH_NO_DEVICE_BOOT")


if __name__ == "__main__":
    main()
