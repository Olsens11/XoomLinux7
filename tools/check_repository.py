#!/usr/bin/env python3
"""Lightweight public-source/documentation continuity and secret-pattern guard."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "AGENTS.md", "START_HERE.md", "docs/README.md",
    "docs/status.md", "runtime/PROJECT_STATE.env",
    "docs/checkpoints/README.md", "docs/hardware/WIFI_BCM4329.md",
    "docs/process/WORKTREES_AND_KEYS.md", "docs/architecture/UPSTREAM_POLICY.md",
]
def main():
    errors=[]
    for rel in REQUIRED:
        if not (ROOT/rel).is_file():
            errors.append("Missing "+rel)
    secret_re = re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----")
    files = list(ROOT.rglob("*"))
    for p in files:
        if not p.is_file() or ".git" in p.parts or any(z in p.parts for z in ("upstream","linux-src","build","out","private")):
            continue
        if p.suffix.lower() in (".img",".ko",".bin",".p12",".pfx"):
            errors.append("Forbidden binary: "+str(p.relative_to(ROOT)))
        if p.stat().st_size > 1_000_000 or p.suffix.lower() not in (".md",".txt",".py",".sh",".ps1",".dts",".config",".env",".yml",".yaml",".json",".c",".h",""):
            continue
        try:
            data=p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if secret_re.search(data):
            errors.append("Private key material: "+str(p.relative_to(ROOT)))
    status=(ROOT/"docs/status.md").read_text(encoding="utf-8") if (ROOT/"docs/status.md").exists() else ""
    state=(ROOT/"runtime/PROJECT_STATE.env").read_text(encoding="utf-8") if (ROOT/"runtime/PROJECT_STATE.env").exists() else ""
    if "v013" not in status or "CURRENT_HARDWARE_VERIFIED=v013" not in state:
        errors.append("Expected imported v013 verified baseline absent; review promotion procedure")
    for err in errors: print("ERROR",err)
    print(f"Checked {len(files)} filesystem entries; errors={len(errors)}")
    return int(bool(errors))
if __name__ == "__main__":
    sys.exit(main())
