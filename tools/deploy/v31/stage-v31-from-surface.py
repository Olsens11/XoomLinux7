#!/usr/bin/env python3
"""Owner-run serial staging of V31 private assets; no install or RF activity.

Uses the EXACT serial gzip/base64/ACK transport from the successful V31 test.
Requires exclusive COM9, the existing V31 Surface capture and the accompanying
install-v31-provisional.sh. Do not run if COM9 terminal is open.
"""
from pathlib import Path
import hashlib
import importlib.util

HOME = Path(r"C:\Users\olsen\xoom-linux-rom\captures\MZ600-V31-CONDITIONAL-UP-20261027")
owner_path = HOME / "mz600-v31-owner-once.py"
installer = Path(__file__).with_name("install-v31-provisional.sh")
STAGE = "/run/xoom-v31-install"
items = [
    (HOME / "mz600-v31-escan-event69.ko", 354392,
     "c82bd4e25ba1d96a01136407b200fe8c5431c7c89856e420dac4a81580183dc8",
     STAGE+"/brcmfmac.ko", "CORE"),
    (HOME / "brcmfmac-wcc-matched-v31.ko", 5892,
     "6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d",
     STAGE+"/brcmfmac-wcc.ko", "WCC"),
    (HOME / "mz600-v31-oem2012.bin", 264140,
     "5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834",
     STAGE+"/brcmfmac4329-sdio.bin", "FIRMWARE"),
]
if not owner_path.is_file() or not installer.is_file():
    raise SystemExit("STOP: verified original transport or installer script missing")
spec = importlib.util.spec_from_file_location("v31_owner_transport", owner_path)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
payloads = []
for path, size, digest, dest, tag in items:
    raw = owner.checked(path, size, digest)
    payloads.append((path, raw, dest, tag))
source = installer.read_bytes()
if len(source)>24000 or not source.startswith(b"#!/bin/bash\n"):
    raise SystemExit("STOP: unexpected installer source")
response = owner.command(
    "id -u; uname -r; "
    "if test ! -e "+STAGE+"; then echo STAGE_UNUSED; fi; "
    "test ! -e /var/lib/xoomlinux7/backup-v31-before-install && echo BACKUP_UNUSED",
    "__V31_STAGE_AUDIT_END__", 20)
for required in ("STAGE_UNUSED", "BACKUP_UNUSED", "7.0.0-next-20260422+"):
    if required not in response:
        raise SystemExit("STOP: Xoom stage or backup not virgin: "+required)
response=owner.command("install -d -m 0700 "+STAGE,"__V31_STAGE_DIR_END__",20)
for path,raw,dest,tag in payloads:
    owner.upload(path,raw,dest,"INSTALL_"+tag)
owner.upload(installer,source,STAGE+"/install-v31-provisional.sh","INSTALL_SCRIPT")
cmd = ("chmod 0700 "+STAGE+"/install-v31-provisional.sh; "
       "bash "+STAGE+"/install-v31-provisional.sh --check; "
       "printf 'V31_DRY_RUN_RC=%s__\\n' \"$?\"")
result = owner.command(cmd, "__V31_STAGE_DRY_RUN_END__", 40)
if "V31_INSTALL_PREFLIGHT_PASS" not in result or "V31_DRY_RUN_RC=0__" not in result:
    raise SystemExit("STOP: staged file checks passed; installer dry-run did NOT pass. Preserve stage and inspect on COM9")
print("V31_PRIVATE_FILES_STAGED_SHA_PASS")
print("V31_INSTALL_DRY_RUN_PASS")
print("NO_DEVICE_FILES_INSTALLED_AND_NO_WIFI_SCAN_PERFORMED")
print("Reopen COM9 terminal and review the install script before using --apply.")
