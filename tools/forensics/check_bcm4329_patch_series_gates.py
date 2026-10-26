#!/usr/bin/env python3
"""Fail-closed, read-only release gate checker for BCM4329 whole-chip patch series.

This is an engineering audit, NOT a substitute for physical verification, DCO,
regulatory approval, user authorization, or an upstream submission tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/patch-series/bcm4329-whole-chip-qualification-v1.json"


def path_inside_repo(raw: str) -> Path:
    p = (ROOT / raw).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError(f"path outside repository: {raw}")
    if not p.is_file():
        raise ValueError(f"missing regular file: {raw}")
    return p


def checked_series(config: dict) -> dict:
    series_file = path_inside_repo(config["exact_series_file"])
    parent = config["expected_upstream_rfc_prefix"].rstrip("/")
    lines = [line.strip() for line in series_file.read_text().splitlines()]
    entries = [s for s in lines if s and not s.startswith("#")]
    if not entries or len(set(entries)) != len(entries):
        raise ValueError("empty or duplicated upstream RFC series")
    patches = []
    for entry in entries:
        if Path(entry).is_absolute() or "/" in entry or "\\" in entry or entry.startswith("."):
            raise ValueError(f"invalid series entry: {entry!r}")
        p = path_inside_repo(parent + "/" + entry)
        blob = p.read_bytes()
        # RFC email-style patches may begin with "Subject:" and retain
        # the canonical diff after a cover explanation, without a From mbox.
        if (b"diff --git a/" not in blob or b"--- a/" not in blob or b"+++ b/" not in blob):
            raise ValueError(f"not a recognized unified Linux git patch: {entry}")
        patches.append({"name": entry, "bytes": len(blob),
                        "sha256": hashlib.sha256(blob).hexdigest()})
    return {"rfc_patch_count": len(patches), "rfc_patches": patches}


def qualified_units(config: dict) -> tuple[list[str], list[str]]:
    units: list[str] = []
    models: set[str] = set()
    for item in config["validated_device_entries"]:
        if item["whole_chip_patch_series_result"] != "pass":
            continue
        uid = item["physical_unit_id"]
        model = item["model"]
        if not uid or uid == "unassigned_private" or uid in units:
            raise ValueError("duplicate/unassigned anonymized physical unit ID")
        evidence = item.get("evidence") or []
        if not evidence:
            raise ValueError(f"no evidence for passing device {model}")
        for e in evidence:
            path_inside_repo(e)
        units.append(uid)
        models.add(model)
    return units, sorted(models)


def audit(config: dict) -> dict:
    if config.get("schema_version") != 1:
        raise ValueError("unknown config schema version")
    if config.get("baseline_commit") != "2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3":
        raise ValueError("unexpected Linux upstream base SHA")
    path_inside_repo(config["provider_candidate"])
    series = checked_series(config)
    units, models = qualified_units(config)
    checks = config["test_gates"]
    required = config["review_requires"]
    if len(required) != len(set(required)) or any(k not in checks for k in required):
        raise ValueError("required-gate list malformed")
    physical_matrix_pass = (
        len(units) >= 3
        and "MZ600" in models
        and "MZ602" in models
        and "MZ604" in models
    )
    missing = [key for key in required if not checks[key]]
    if checks.get("multiple_physical_devices_tested") and not physical_matrix_pass:
        missing.append("MULTIDEVICE_EVIDENCE_INVALID")
    # Human-verified flags are explicitly separate from automatic matrix checks.
    authorized = config.get("submission_authorized") is True
    ready = (not missing and physical_matrix_pass
             and config.get("physical_whole_chip_series_verified") is True
             and authorized
             and config.get("release_state") == "review_candidate")
    return {
        "project": config["project"],
        "upstream_base": config["baseline_commit"],
        "status": config["release_state"],
        "series": series,
        "qualifying_physical_units": len(units),
        "qualifying_models": models,
        "minimum_physical_matrix": "three distinct anonymized devices incl MZ600, MZ602, MZ604",
        "physical_matrix_pass": physical_matrix_pass,
        "missing_human_qualification_gates": sorted(set(missing)),
        "explicit_submission_authorization_recorded": authorized,
        "review_ready": ready,
        "does_not_submit_anything": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-review-ready", action="store_true",
                        help="return nonzero when any physical, source, or consent gate is unqualified")
    args = parser.parse_args()
    try:
        result = audit(json.loads(CONFIG.read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"valid_manifest": False, "error": str(error)}, indent=2))
        return 2
    result["valid_manifest"] = True
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_review_ready and not result["review_ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
