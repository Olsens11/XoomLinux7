#!/usr/bin/env python3
"""Create PRIVATE UNTESTED p8-root boot candidate from a known-good SD-root kernel.

Host-only operation. No eMMC write, no mount/format/flash. Exact SHA-gated.
Use a privately recorded real internal GPT p8 PARTUUID (not a filesystem UUID).
No PII, GPT GUID, root selector, or private firmware is published.
"""
import argparse, hashlib, json, re, struct
from pathlib import Path

PREV_SHA = "b9667187ffe0ff74a6d0f801f300a78012d8242c2e45e34bd35e39c59fc657ba"
PREV_SIZE = 6645760
DEFAULT_NAME = "MZ600-V064-BIGPART-INTERNAL-SYSTEM-ROOT-TEMPBOOT-PREINSTALL-UNTESTED.img"
def sha(b):
    return hashlib.sha256(b).hexdigest()
def go():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--p8-partuuid-file",type=Path,required=True)
    p.add_argument("--destination",type=Path,required=True)
    a=p.parse_args()
    if a.destination.exists():raise RuntimeError("Refuse to overwrite destination")
    if a.destination.name != DEFAULT_NAME:raise RuntimeError("Unexpected destination filename")
    old=a.source.read_bytes()
    if len(old)!=PREV_SIZE or sha(old)!=PREV_SHA or old[:8]!=b"ANDROID!":
        raise RuntimeError("Proven Stage-B image size/SHA/header mismatch")
    new_uuid=a.p8_partuuid_file.read_text().strip().lower()
    if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}",new_uuid):
        raise RuntimeError("Target p8 GUID must be a full 36-character GPT GUID")
    fields=struct.unpack_from("<10I",old,8)
    klen,kaddr,rlen,raddr,sslen,ssaddr,tags,page,dtlen,reserved=fields
    if page!=2048 or sslen!=0 or rlen<1024 or dtlen!=0 or klen<5000000:
        raise RuntimeError("Legacy image fields not valid")
    cmd=old[64:576].split(b"\0",1)[0]
    candidates=re.findall(rb"(?<!\S)root=PARTUUID=([^\s\x00]+)",cmd)
    if len(candidates)!=1 or len(candidates[0])!=11 or not re.fullmatch(rb"[a-fA-F0-9]{8}-[0-9]{2}",candidates[0]):
        raise RuntimeError("Proven removable SD root selector format unexpected")
    if b"rootwait" not in cmd or b"init=/sbin/init" not in cmd:
        raise RuntimeError("Proven systemd boot selector missing")
    if new_uuid.encode("ascii")==candidates[0].lower():
        raise RuntimeError("Target p8 root accidentally equals SD root")
    updated=cmd.replace(b"root=PARTUUID="+candidates[0],b"root=PARTUUID="+new_uuid.encode("ascii"),1)
    if len(updated)>511:raise RuntimeError("Legacy cmdline field too long")
    new=bytearray(old)
    new[64:576]=updated.ljust(512,b"\0")
    if bytes(new)[576:]!=old[576:] or bytes(new)[:64]!=old[:64]:
        raise RuntimeError("Kernel, ramdisk or bootloader load addresses changed")
    # Legacy Android v0 image ID hashes kernel and external ramdisk, NOT cmdline.
    # It stays byte-for-byte identical, as intended.
    a.destination.parent.mkdir(parents=True,exist_ok=True)
    a.destination.write_bytes(new)
    manifest={
        "classification":"OFFLINE_STAGED_UNTESTED_NO_DEVICE_WRITE",
        "stage_b_source_sha256":PREV_SHA,
        "image_bytes":len(new),
        "new_image_sha256":sha(new),
        "changed_bytes_are_only_legacy_cmdline":True,
        "target_is_privately_supplied_p8_gpt_partuuid":True,
        "target_partuuid_disclosed_in_manifest":False,
        "root_system_not_yet_formatted":True,
        "hardware_stage_c_boot_test_not_performed":True,
        "persistent_boot_flash_not_performed":True,
    }
    mf=a.destination.with_suffix(".manifest.json")
    if mf.exists():raise RuntimeError("Manifest already exists")
    mf.write_text(json.dumps(manifest,indent=2)+"\n")
    print("STAGE_C_INTERNAL_ROOT_BOOT_OFFLINE_PASS")
    print("bytes",len(new),"sha256",sha(new))
    print("NO_PARTITION_WRITES_NO_FLASH_NO_BOOT")
if __name__=="__main__":
    go()
