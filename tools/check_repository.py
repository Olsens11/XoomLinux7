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
    # Canonical current state supersedes dated/duplicated legacy keys. Both
    # v063 (artifact tag) and v06.3 (human-facing version) are valid spellings.
    current_path = ROOT / "runtime/CURRENT_LINUX7_STATE.env"
    canonical = current_path.read_text(encoding="utf-8") if current_path.exists() else ""
    # A reboot into TWRP replaces the *live* Linux environment but does not
    # invalidate the most recently proven temporary-boot Linux image.
    m = (re.search(r"(?m)^LAST_VERIFIED_LINUX_IMAGE=(V[0-9]+)$", canonical)
         or re.search(r"(?m)^LAST_VERIFIED_RUNNING_IMAGE=(V[0-9]+)$", canonical))
    if m:
        compact = m.group(1).lower()
        pretty = compact[:-1] + "." + compact[-1] if len(compact) >= 4 else compact
        if compact not in status and pretty not in status:
            errors.append("Canonical last verified Linux image missing from status")
    else:
        legacy = re.search(r"(?m)^CURRENT_HARDWARE_VERIFIED=(v[0-9]+)(?:_partial)?$", state)
        if not legacy or legacy.group(1) not in status:
            errors.append("Physical baseline version missing or inconsistent")
    current = re.search(r"(?m)^CURRENT_DUT_MODE=([^\\n]+)$", canonical)
    if current and current.group(1).startswith("TWRP") and "TWRP" not in status:
        errors.append("Current TWRP device state not documented in status")
    for err in errors: print("ERROR",err)
    print(f"Checked {len(files)} filesystem entries; errors={len(errors)}")
    return int(bool(errors))
if __name__ == "__main__":
    sys.exit(main())
