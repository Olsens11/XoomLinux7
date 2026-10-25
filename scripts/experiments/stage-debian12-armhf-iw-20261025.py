#!/usr/bin/env python3
"""Download and independently verify stock Debian bookworm armhf iw.

Only stages files in a private build workspace, not the live Xoom, rootfs,
or the public GitHub repo. Verify hash against Debian's official package page.
"""
from pathlib import Path
import hashlib, urllib.request, subprocess, os, json, shutil
ROOT=Path("/home/xoomdev/xoom-linux-rom")
WORK=ROOT/"clean-wifi-bt-usb-20261025"/"userspace-network"/"bookworm-armhf-iw"
ROOTFS=ROOT/"os-build"/"bookworm-armhf-root"
URL="https://deb.debian.org/debian/pool/main/i/iw/iw_5.19-1_armhf.deb"
SHA="fd1f6c926853505b0eb03a3afb4c6b68e4350f42b140fe6c5295012eeca872ee"
SIZE=93300
WORK.mkdir(parents=True,exist_ok=True)
deb=WORK/"iw_5.19-1_armhf.deb"
if not deb.exists():
 with urllib.request.urlopen(URL, timeout=40) as r:
  buf=r.read(SIZE+1)
 assert len(buf)==SIZE,(len(buf),"package truncated or unexpectedly large")
 assert hashlib.sha256(buf).hexdigest()==SHA
 deb.write_bytes(buf)
buf=deb.read_bytes()
assert len(buf)==SIZE and hashlib.sha256(buf).hexdigest()==SHA, "DEBIAN_PACKAGE_SHA256_VERIFICATION_FAILED"
def run(*args,**kw):
 print("RUN"," ".join(map(str,args)),flush=True)
 return subprocess.run(list(map(str,args)),check=True,**kw)
metadata=subprocess.check_output(["dpkg-deb","-f",str(deb),"Package","Version","Architecture","Depends"],text=True)
assert "iw\n" in metadata and "5.19-1\n" in metadata and "armhf\n" in metadata,metadata
assert "libnl-genl-3-200" in metadata
dest=WORK/"expanded"
dest.mkdir(exist_ok=True)
run("dpkg-deb","-x",deb,dest)
binaries=[x for x in dest.rglob("iw") if x.is_file()]
assert len(binaries)==1,binaries
binary=binaries[0]
magic=binary.read_bytes()[:20]
assert magic[:4]==b"\x7fELF" and magic[4]==1 and magic[5]==1, "not ELF32-LE"
import struct
assert struct.unpack_from("<H",magic,18)[0]==40,"not EM_ARM"
abi=subprocess.check_output(["readelf","-A",str(binary)],text=True)
assert "Tag_CPU_arch: v7" in abi or "Tag_CPU_arch: v6" in abi,abi
# ARMHF distro ABI should be VFP without mandatory NEON.
assert "NEON" not in abi and "Advanced SIMD" not in abi, "requires NEON (not on Tegra 2)"
shared=subprocess.check_output(["readelf","-d",str(binary)],text=True)
print("BIN",binary.relative_to(WORK),"BYTES",binary.stat().st_size)
for req in ["libnl-3.so.200","libnl-genl-3.so.200","libc.so.6"]:
 assert req in shared,("missing expected dependency",req)
libroot=ROOTFS/"lib/arm-linux-gnueabihf"
usrlib=ROOTFS/"usr/lib/arm-linux-gnueabihf"
assert (libroot/"ld-linux-armhf.so.3").exists()
assert (libroot/"libc.so.6").exists()
assert (usrlib/"libnl-3.so.200").exists()
assert (usrlib/"libnl-genl-3.so.200").exists()
# QEMU user emulator runs the real armhf executable with Debian armhf sysroot.
proc=run("qemu-arm","-L",ROOTFS,binary,"--version",capture_output=True,text=True,timeout=30)
print("QEMU_ARMHF_IW_VERSION",proc.stdout.strip(),proc.stderr.strip())
manifest={"package_url":URL,"debian_arch":"armhf","package":"iw","version":"5.19-1",
 "package_sha256":SHA,"package_bytes":SIZE,"binary_path":str(binary.relative_to(WORK)),
 "binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
 "binary_bytes":binary.stat().st_size,"emulation":"qemu-arm -L Debian12-armhf-root /path/to/iw --version",
 "notes":"Staged offline only. scan not yet available on running v06.2 and not physically tested on Xoom.",
 "requires":["libc6","libnl-3-200","libnl-genl-3-200"],
 "never_touched_device":True}
(WORK/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("DEBIAN_ARMHF_IW_STAGING_OFFLINE_PASS",flush=True)
