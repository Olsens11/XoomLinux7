#!/usr/bin/env python3
"""Source-only v12a regression: never build, contact Xoom or transmit RF.

Proves v12a only inserts numeric event_msgs GET diagnostics on top of
already verified v11 lab source. It does NOT prove firmware supports GET.
Usage: python3 tools/forensics/test_bcm4329_v12a_mask_probe_source.py
"""
import ast
from difflib import SequenceMatcher
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/experiments/build-v064-bcm4329-legacy-event26-mask-readback-v12a-20261026.py"
V11 = ROOT / "scripts/experiments/build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py"
SOURCE = Path(
    "/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/"
    "v064-bigpart-linux/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c"
)
if len(sys.argv) > 1:
    SOURCE = Path(sys.argv[1])
for path in (SCRIPT, V11):
    ast.parse(path.read_text(), filename=str(path))

spec = importlib.util.spec_from_file_location("mz600_v12a_test", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

original = SOURCE.read_text()
before = module.previous(original)
after = module.patch(original)
if before.count("MZ600_LEGACY_SCAN_LAB_START") != 1:
    raise SystemExit("expected v11 scan-start gate not found")
if after.count("MZ600_LEGACY_EVENT26_MASK_READBACK") != 1:
    raise SystemExit("v12a marker missing or repeated")

old_lines = before.splitlines(keepends=True)
new_lines = after.splitlines(keepends=True)
diff = SequenceMatcher(None, old_lines, new_lines, autojunk=False)
added = []
for kind, ia, ib, ja, jb in diff.get_opcodes():
    if kind == "insert":
        added.extend(new_lines[ja:jb])
    elif kind != "equal":
        raise SystemExit("v12a is not insertion-only: " + kind)
added_text = "".join(added)
required = (
    'brcmf_fil_iovar_data_get(',
    '"event_msgs"',
    "fweh->event_mask_len",
    "fweh->evt_handler[BRCMF_E_SCAN_COMPLETE]",
    "fw_mask[byte] & bit",
    "MZ600_LEGACY_EVENT26_MASK_READBACK",
    "kfree(fw_mask);",
)
for token in required:
    if token not in added_text:
        raise SystemExit("missing v12a-only readback gate: " + token)
for token in (
    "brcmf_fil_iovar_data_set(",
    "brcmf_fil_cmd_data_set(",
    "cfg80211_scan_done(",
    "brcmf_notify_escan_complete(",
    "mod_timer(",
    "schedule_work(",
):
    if token in added_text:
        raise SystemExit("v12a must not alter state or scan lifecycle: " + token)
if len(added) > 85 or len(added) < 30:
    raise SystemExit("unexpected v12a source delta size")
print("V12A_SOURCE_ONLY_INSERTION_AND_NO_LIFECYCLE_CHANGE_PASS")
print("inserted_lines=" + str(len(added)))
print("source_scan_started=FALSE; exact_abi_build=NOT_PERFORMED; physical_test=NOT_PERFORMED")
