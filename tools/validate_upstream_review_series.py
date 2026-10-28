#!/usr/bin/env python3
"""Offline integrity check for canonical XoomLinux7 unsigned review patch sets."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKS = (
    ("review-stingray-dt-20261028", 3),
    ("review-wifi-four-logical-20261028", 4),
    ("review-arm-atag-20261028", 1),
)

def inspect_series(folder: Path, expected: int) -> list[Path]:
    raw = (folder / "series").read_bytes()
    if not raw.endswith(b"\n") or b"\\n" in raw or b"\r" in raw:
        raise ValueError(f"{folder}: series needs real LF separators and a final newline")
    names = raw.decode("utf-8").splitlines()
    if len(names) != expected or len(set(names)) != expected:
        raise ValueError(f"{folder}: expected {expected} distinct entries, got {len(names)}")
    patches = []
    for n, name in enumerate(names, 1):
        if not re.fullmatch(rf"{n:04d}-[A-Za-z0-9_.-]+\.patch", name):
            raise ValueError(f"{folder}: unexpected filename/order: {name!r}")
        p = folder / name
        if not p.is_file() or p.stat().st_size < 300:
            raise ValueError(f"{folder}: missing/incomplete {name}")
        data = p.read_bytes()
        if not data.startswith(b"From ") or b"diff --git " not in data:
            raise ValueError(f"{p}: not an email-formatted kernel patch")
        if b"Signed-off-by:" in data:
            raise ValueError(f"{p}: unexpected human DCO signoff in unsigned RFC")
        patches.append(p)
    print(f"SERIES_PASS {folder.name} members={len(patches)}")
    return patches

def main() -> None:
    source = ROOT / "patches" / "upstream"
    for folder_name, count in TRACKS:
        folder = source / folder_name
        patches = inspect_series(folder, count)
        if folder_name == "review-arm-atag-20261028":
            manifest = json.loads((folder / "manifest.json").read_text())
            if manifest["source_patch"] != patches[0].name or manifest["patch_sha256"] != hashlib.sha256(patches[0].read_bytes()).hexdigest():
                raise ValueError("ARM ATAG source patch/sha256 manifest mismatch")
            print("PATCH_HASH_PASS", patches[0].name, manifest["patch_sha256"])
            continue
        if folder_name != "review-wifi-four-logical-20261028":
            continue
        manifest = json.loads((folder / "manifest.json").read_text())
        entries = manifest["patches"]
        if [p.name for p in patches] != [x["file"] for x in entries]:
            raise ValueError("Wi-Fi series order != signed-off-free manifest order")
        for p, item in zip(patches, entries):
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            if actual != item["sha256"]:
                raise ValueError(f"{p.name}: sha256 mismatch")
            print(f"PATCH_HASH_PASS {p.name} {actual}")
    print("REVIEW_SERIES_INTEGRITY_PASS")

if __name__ == "__main__":
    main()
