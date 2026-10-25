#!/usr/bin/env python3
"""Offline-only build of clean upstream Xoom Linux 7 + proven WLAN MAC bridge.

Uses isolated worktree/config; leaves currently booted v04 kernel, SD and eMMC
untouched. Userland CPIO and RAM-boot image are prepared in a second step.
"""
from pathlib import Path
import hashlib,os,subprocess,shutil,json
B=Path("/home/xoomdev/xoom-linux-rom")
PROJECT=B/"clean-upstream-usb-20261025/project"
UPSTREAM=B/"linux"
ROOT=B/"clean-wifi-bt-usb-20261025"
SRC=ROOT/"linux"
OBJ=ROOT/"build"
ART=ROOT/"artifacts"
PIN="2404d27378503b4df74ab2cb0a8b7cd6cf9d5fc3"
CC=str(B/"toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-")
assert os.geteuid()!=0
def run(args,**kw):
 print("RUN"," ".join(map(str,args)),flush=True)
 subprocess.run(list(map(str,args)),check=True,**kw)
def sha(b):return hashlib.sha256(b).hexdigest()
assert subprocess.check_output(["git","-C",str(UPSTREAM),"rev-parse","HEAD"],text=True).strip()==PIN
assert not subprocess.check_output(["git","-C",str(UPSTREAM),"status","--porcelain"])
ROOT.mkdir(parents=True,exist_ok=True);ART.mkdir(exist_ok=True)
if not (SRC/".git").exists():
 run(["git","-C",UPSTREAM,"worktree","add","--detach",SRC,PIN])
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip()==PIN
# Pin exactly to the proven Stingray board/USB DTS, now changing only Linux
# kernel source ATAG WLAN identity bridge (never a static/shared MAC).
orig=B/"clean-upstream-usb-20261025/linux/arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts"
dest=SRC/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dts"
assert orig.is_file()
if dest.exists():assert dest.read_bytes()==orig.read_bytes()
else:shutil.copyfile(orig,dest)
mk=SRC/"arch/arm/boot/dts/nvidia/Makefile"
m=mk.read_text()
needle="\ttegra20-motorola-wingray.dtb \\\n"
new=needle+"\ttegra20-motorola-stingray-clean-usb.dtb \\\n"
if new not in m:
 assert m.count(needle)==1
 mk.write_text(m.replace(needle,new,1))
patch=PROJECT/"patches/os/0001-arm-stingray-convert-wlan-mac-atag-to-fdt.patch"
assert patch.is_file()
if subprocess.run(["git","-C",str(SRC),"apply","--reverse","--check",str(patch)],capture_output=True).returncode!=0:
 run(["git","-C",SRC,"apply","--check",patch])
 run(["git","-C",SRC,"apply",patch])
# Proven normal Debian setup config is much smaller than tegra_next_defconfig
# and already used cfg80211 built-in + upstream brcmfmac module + USB gadget.
# It is a reference *config* only, not an old experimental source tree.
OBJ.mkdir(parents=True,exist_ok=True)
proven_cfg=B/"os-build/kernel/.config"
assert proven_cfg.is_file()
if not (OBJ/".config").exists():shutil.copyfile(proven_cfg,OBJ/".config")
config=SRC/"scripts/config"
run([config,"--file",OBJ/".config",
    "--enable","ARM_APPENDED_DTB","--enable","ARM_ATAG_DTB_COMPAT",
    "--enable","USB_GADGET","--enable","USB_CHIPIDEA_UDC",
    "--enable","USB_CHIPIDEA_TEGRA","--enable","USB_G_SERIAL",
    "--enable","USB_F_ACM","--enable","USB_U_SERIAL",
    "--enable","DEVTMPFS","--enable","DEVTMPFS_MOUNT",
    "--enable","PSTORE","--enable","PSTORE_RAM","--enable","PSTORE_CONSOLE",
    "--enable","CFG80211","--enable","MODULES","--enable","FW_LOADER",
    "--enable","BRCMFMAC_SDIO","--enable","BRCMFMAC_PROTO_BCDC",
    "--module","BRCMFMAC","--module","BRCMUTIL",
    "--module","BT_HCIUART","--disable","IIO_ST_HUB_DRIVERS",
    "--disable","NEON","--set-str","INITRAMFS_SOURCE",""])
env={**os.environ,"ARCH":"arm","CROSS_COMPILE":CC}
run(["make","-s","-C",SRC,f"O={OBJ}","olddefconfig"],env=env)
cfg=(OBJ/".config").read_text()
for line in ("CONFIG_CFG80211=y","CONFIG_BRCMFMAC=m","CONFIG_BRCMUTIL=m",
             "CONFIG_ARM_APPENDED_DTB=y","CONFIG_ARM_ATAG_DTB_COMPAT=y",
             "CONFIG_USB_G_SERIAL=y","CONFIG_BT_HCIUART=m"):
 assert line in cfg,line
assert "# CONFIG_NEON is not set" in cfg
# No presumption that Wi-Fi firmware is ready or 2.4 GHz permitted.
log=ROOT/"kernel-and-modules-build.log"
with log.open("w") as out:
 try:
  run(["make","-C",SRC,f"O={OBJ}","-j6",
       "zImage","nvidia/tegra20-motorola-stingray-clean-usb.dtb"],env=env,stdout=out,stderr=subprocess.STDOUT)
  run(["make","-C",SRC,f"O={OBJ}","-j6","modules"],env=env,stdout=out,stderr=subprocess.STDOUT)
 except subprocess.CalledProcessError:
  print("BUILD FAILED: tail",flush=True)
  print("\n".join(log.read_text().splitlines()[-65:]),flush=True)
  raise
z=(OBJ/"arch/arm/boot/zImage").read_bytes()
dt=(OBJ/"arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-clean-usb.dtb").read_bytes()
(ART/"zImage-with-stingray-wifi-bt.dtb").write_bytes(z+dt)
shutil.copyfile(OBJ/".config",ART/"kernel.config")
module_rel=[
 "drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko",
 "drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/brcmfmac-wcc.ko",
 "drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko",
 "net/bluetooth/bluetooth.ko","net/bluetooth/rfcomm/rfcomm.ko",
 "drivers/bluetooth/btbcm.ko","drivers/bluetooth/hci_uart.ko",
 "crypto/ecdh_generic.ko","crypto/echainiv.ko","crypto/cmac.ko",
 "lib/crypto/curve25519-generic.ko",
]
record={}
for rel in module_rel:
 p=OBJ/rel
 if not p.is_file():continue
 record[str(Path(rel).name)]={"size":p.stat().st_size,"sha256":sha(p.read_bytes()),"source":rel}
# cfg80211 built-in; check symbols and module dependency issues before hardware
(ART/"modules-manifest.json").write_text(json.dumps(record,indent=2)+"\n")
print("CLEAN_WIFI_BT_KERNEL_MODULES_BUILD_PASS",flush=True)
print("KERNEL_ZIMAGE_BYTES",len(z),"DTB_BYTES",len(dt),"COMBINED_SHA256",sha(z+dt),flush=True)
print("MODULES"," ".join(sorted(record)),flush=True)
print("NO_DEVICE_ACCESS_NO_STORAGE_WRITES",flush=True)
