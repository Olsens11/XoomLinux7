#!/usr/bin/env python3
"""Build only v020, preserving original Linux source/config on any outcome."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys
R=Path("/home/xoomdev/projects/XoomLinux7-mmc-on-demand")
B=Path("/home/xoomdev/xoom-linux-rom")
K=B/"linux-src"
O=B/"build-wingray-gcc14-initramfs"
V=B/"phase1-v20"
source=K/"drivers/mmc/core/sdio.c"
conf=O/".config"
patch=R/"patches/experiments/v020-on-demand-mmc2-capability-parameter.patch"
exe=R/"scripts/experiments/v020-package-tempboot.sh"
ram=V/"phase1-initramfs.cpio.gz"
base=source.read_bytes()
original_config=conf.read_bytes()
checksum=lambda b:hashlib.sha256(b).hexdigest()
assert checksum(base)=="cfc4635e4ae8c5690535b3933a4fd5387d3fbe6256f575c8794b074248fbf8f6"
assert ram.exists()
print("BASE_MMC_SOURCE",checksum(base),flush=True)
print("V020_INITRAMFS",checksum(ram.read_bytes()),flush=True)
print("V020_PATCH",checksum(patch.read_bytes()),flush=True)
env=os.environ.copy()
env["ARCH"]="arm"
env["CROSS_COMPILE"]=str(B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-")
log=V/"kernel-build.log"
built=False
try:
    subprocess.run(["git","apply","--check","--whitespace=nowarn",str(patch)],cwd=K,check=True)
    subprocess.run(["git","apply","--whitespace=nowarn",str(patch)],cwd=K,check=True)
    assert "XOOM_MMC2_V020" in source.read_text(encoding="utf8")
    subprocess.run([str(K/"scripts/config"),"--file",str(conf),"--set-str","INITRAMFS_SOURCE",str(ram)],check=True)
    with log.open("wb") as f:
        for args in (
            ["make","O="+str(O),"olddefconfig"],
            ["make","-j2","O="+str(O),"zImage","nvidia/tegra20-motorola-stingray-usbdiag.dtb"]
        ):
            p=subprocess.run(args,cwd=K,env=env,stdout=f,stderr=subprocess.STDOUT)
            if p.returncode:raise RuntimeError("Kernel build step failed "+repr(args))
    if (O/"usr/initramfs_inc_data").read_bytes()!=ram.read_bytes():
        raise RuntimeError("Embedded rootfs mismatch")
    print("V020_KERNEL_BUILD_PASS",flush=True)
    subprocess.run(["bash",str(exe)],env=env,check=True)
    built=True
finally:
    source.write_bytes(base)
    conf.write_bytes(original_config)
    assert source.read_bytes()==base, "CRITICAL SOURCE NOT RESTORED"
    assert conf.read_bytes()==original_config, "CRITICAL CONFIG NOT RESTORED"
    print("MMC_SOURCE_AND_CONFIG_RESTORED",checksum(base),flush=True)
if not built:
    raise RuntimeError("Kernel build did not complete")
img=Path("/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v20-MMC2-ON-DEMAND/MZ600-stingray-diagnostic-v20-MMC2-ON-DEMAND-TEMPBOOT-ONLY.img")
print("V020_IMAGE",img,flush=True)
print("V020_IMAGE_BYTES",img.stat().st_size,flush=True)
print("V020_IMAGE_SHA256",checksum(img.read_bytes()),flush=True)
