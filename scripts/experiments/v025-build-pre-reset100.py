#!/usr/bin/env python3
"""Build exact v025 single-variable pre-reset-delay experiment from v022.
Do not compile a kernel or write to any Xoom storage; fail closed.
"""
from pathlib import Path
from hashlib import sha1,sha256
import subprocess,struct,json,difflib
R=Path("/home/xoomdev/projects/XoomLinux7-v025")
BASE=Path("/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v22-AUTO-LEGACY25-CONTROL")
OUT=Path("/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v025-HOST-PRE-RESET-100MS")
FILE=OUT/"MZ600-stingray-diagnostic-v025-HOST-PRE-RESET-100MS-TEMPBOOT-ONLY.img"
OUT.mkdir(parents=True,exist_ok=True)
hash=lambda b:sha256(b).hexdigest()
old=(BASE/"MZ600-stingray-diagnostic-v22-AUTO-LEGACY25-TEMPBOOT-ONLY.img").read_bytes()
assert hash(old)=="2be2f5094149f242a5a9e5d290f7505d9b312ae4bfba8dbc74e1f7362995c6b3",hash(old)
assert len(old)==6662144 and old[:8]==b"ANDROID!"
h=struct.unpack_from("<10I",old,8)
ks,kaddr,rs,raddr,ss,saddr,taddr,page,ds,zero=h
assert (kaddr,raddr,ss,saddr,taddr,page,ds)==(0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
align=lambda v: ((v+page-1)//page)*page
ram_offset=page+align(ks)
k=old[page:page+ks]
ram=old[ram_offset:ram_offset+rs]
assert set(old[page+ks:ram_offset])<={0}
assert set(old[ram_offset+rs:])<={0}
assert len(ram)==rs
old_dtb=(BASE/"tegra20-motorola-stingray-usbdiag.dtb").read_bytes()
assert k.endswith(old_dtb)
assert len(old_dtb)==61092
# Confirm original root-only target property absent, and pwrseq property remains 300ms.
def fdtget(dtb,node,property):
    return subprocess.run(["fdtget","-t","x",str(dtb),node,property],
       capture_output=True,text=True)
original_dtbf=BASE/"tegra20-motorola-stingray-usbdiag.dtb"
assert fdtget(original_dtbf,"/mmc@c8000200","post-power-on-delay-ms").returncode != 0
assert int(fdtget(original_dtbf,"/wifi-pwrseq","post-power-on-delay-ms").stdout.strip(),16)==300
assert int(fdtget(original_dtbf,"/mmc@c8000200","max-frequency").stdout.strip(),16)==25000000
candidate_dtb=OUT/"tegra20-motorola-stingray-usbdiag.dtb"
candidate_dtb.write_bytes(old_dtb)
subprocess.run(["fdtput","-t","x",str(candidate_dtb),
               "/mmc@c8000200","post-power-on-delay-ms","64"],check=True)
now_dtb=candidate_dtb.read_bytes()
assert int(fdtget(candidate_dtb,"/mmc@c8000200","post-power-on-delay-ms").stdout.strip(),16)==100
assert int(fdtget(candidate_dtb,"/wifi-pwrseq","post-power-on-delay-ms").stdout.strip(),16)==300
assert int(fdtget(candidate_dtb,"/mmc@c8000200","max-frequency").stdout.strip(),16)==25000000
def dts(data,where):
    path=OUT/where
    path.write_bytes(data)
    result=subprocess.run(["dtc","-I","dtb","-O","dts","-o","-",str(path)],
      capture_output=True,check=True,text=True)
    return result.stdout.splitlines(keepends=True)
before_text=dts(old_dtb,"original-only-for-audit.dtb")
after_text=dts(now_dtb,"new-only-for-audit.dtb")
diff=list(difflib.unified_diff(before_text,after_text,fromfile="v022",tofile="v025"))
# Compare semantic decompilation, not raw FDT offsets.
sm=difflib.SequenceMatcher(None,before_text,after_text,autojunk=False)
ops=[(kind,before_text[i:j],after_text[k:l]) for kind,i,j,k,l in sm.get_opcodes() if kind!='equal']
assert len(ops)==1,ops
kind,removed,added=ops[0]
assert kind=="insert" and not removed and len(added)==1 and "post-power-on-delay-ms = <0x64>;" in added[0],ops
assert now_dtb!=old_dtb
newkernel=k[:-len(old_dtb)]+now_dtb
buf=bytearray(old[:page])
struct.pack_into("<I",buf,8,len(newkernel))
digest=sha1()
for block in (newkernel,ram,b'',b''):
    digest.update(block);digest.update(struct.pack('<I',len(block)))
buf[576:596]=digest.digest()
buf.extend(newkernel)
buf.extend(b'\0'*(align(len(newkernel))-len(newkernel)))
buf.extend(ram)
buf.extend(b'\0'*(align(len(ram))-len(ram)))
new=bytes(buf)
assert new[:8]==b'ANDROID!'
assert new[page:page+len(newkernel)]==newkernel
assert new[page+align(len(newkernel)):page+align(len(newkernel))+rs]==ram
assert (newkernel[:-len(now_dtb)]==k[:-len(old_dtb)])
assert struct.unpack_from('<I',new,8)[0]==len(newkernel)
assert new[576:596]==digest.digest()
assert struct.unpack_from("<9I",new,8)[1:]==struct.unpack_from("<9I",old,8)[1:], "Other Android header fields changed"
assert old[64:576]==new[64:576], "Cmdline/board header changed"
FILE.write_bytes(new)
manifest={
 "candidate":str(FILE),"classification":"TEMPORARY fastboot boot only; NEVER FLASH",
 "parent_sha256":hash(old),"candidate_sha256":hash(new),
 "parent_bytes":len(old),"candidate_bytes":len(new),
 "rootfs_sha256":hash(ram),"old_dtb_sha256":hash(old_dtb),"new_dtb_sha256":hash(now_dtb),
 "semantic_dt_diff": ''.join(diff),
 "changed_semantics":"ONLY /mmc@c8000200/post-power-on-delay-ms = <100>",
 "unchanged_pwrseq_post_delay_ms":300,"unchanged_sdio_max_hz":25000000,
 "kernel_except_dtb_unchanged":True,"ramfs_unchanged":True,
 "test":"v020/v024 USB client should show effective MMC_HOST power_delay_ms=100; HOST clock 25MHz timing=0, 253748-byte firmware and 672-byte nvram; repeat F2 tests; original device and recovery untouched"
}
(OUT/"V025_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("V025_IMAGE",str(FILE),flush=True)
print("V025_BYTES",len(new),flush=True)
print("V025_SHA256",hash(new),flush=True)
print("OLD_DTB_BYTES",len(old_dtb),"NEW_DTB_BYTES",len(now_dtb),flush=True)
print("RAMFS_UNCHANGED_SHA256",hash(ram),flush=True)
print("PWRSEQ_POST_RESET_DELAY",300,"HOST_PRE_RESET_DELAY",100,flush=True)
print("DT_SEMANTIC_DELTA",str(ops),flush=True)
print("BOOT_HEADER_SHA1_VALID",digest.hexdigest(),flush=True)
print("NO_PARTITION_WRITE_OR_KERNEL_REBUILD",flush=True)
