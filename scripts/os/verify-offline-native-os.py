#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
"""Read-only, offline validation of the UNINSTALLED MZ600 native OS images."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

B = Path(os.environ.get("XOOM_BUILD_ROOT", "/home/xoomdev/xoom-linux-rom"))
out = Path(os.environ.get("XOOM_OS_ARTIFACTS", str(B / "os-build/artifacts")))
root = B / "os-build/bookworm-armhf-root"
kernel_out = B / "os-build/kernel"
boot = (out / "xoom-linux-boot.img").read_bytes()
system_image = out / "xoom-linux-root.ext4"
dtb = kernel_out / "arch/arm/boot/dts/nvidia/tegra20-motorola-stingray-usbdiag.dtb"
zimage = kernel_out / "arch/arm/boot/zImage"
krel = (kernel_out / "include/config/kernel.release").read_text().strip()

def check(cond: bool, label: str) -> None:
    if not cond:
        raise SystemExit("FAIL: " + label)
    print("PASS:", label)

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout

check(boot[:8] == b"ANDROID!", "normal Android-format boot image signature")
kernel_bytes = zimage.read_bytes() + dtb.read_bytes()
kernel_size, kernel_addr, ramdisk_size = struct.unpack_from("<3I", boot, 8)
page_size = struct.unpack_from("<I", boot, 8 + 7 * 4)[0]
check(page_size == 2048 and kernel_addr == 0x10008000, "bootloader pagesize and kernel address")
check(kernel_size == len(kernel_bytes), "boot image kernel + appended DTB exact length")
check(boot[page_size:page_size + kernel_size] == kernel_bytes, "boot image payload byte-for-byte zImage+USB-DTB")
check(ramdisk_size == 0, "no embedded diagnostic initramfs")
cmdline = boot[64:576].split(b"\0", 1)[0].decode()
card_partuuid = os.environ.get("XOOM_LINUX_ROOT_PARTUUID", "").lower()
if card_partuuid:
    check(bool(re.fullmatch(r"[0-9a-f]{8}-0[1-4]", card_partuuid)),
          "MBR card PARTUUID selector syntax")
    root_selector = "PARTUUID=" + card_partuuid
else:
    root_selector = "PARTLABEL=xoom-linux"
for keyword in ("root=" + root_selector, "rootfstype=ext4", "rootwait", "init=/sbin/init"):
    check(keyword in cmdline, "normal OS cmdline includes " + keyword)
check("root=PARTLABEL=system" not in cmdline and "root=PARTLABEL=userdata" not in cmdline,
      "Android system/userdata are NOT Linux root")
check("rdinit=/init" not in cmdline and "brcmfmac.debug=" not in cmdline,
      "temporary diagnostic init flags absent")
check(system_image.stat().st_size == 768 * 1048576, "768 MiB ext4 staged system image")
check("xoom-root" in run("dumpe2fs", "-h", str(system_image)), "ext4 filesystem label")

dts_compat = run("fdtget", "-t", "s", str(dtb), "/usb@c5000000", "compatible")
check("nvidia,tegra20-udc" in dts_compat, "USB0 is Tegra USB device controller")
check("peripheral" == run("fdtget", "-t", "s", str(dtb), "/usb@c5000000", "dr_mode").strip(),
      "USB0 remains peripheral in normal OS")
check("brcm,bcm4329-fmac" in run("fdtget", "-t", "s", str(dtb),
                                "/mmc@c8000200/wifi@1", "compatible"), "BCM4329 SDIO FDT child present")
mac_property = subprocess.run(["fdtget", str(dtb), "/mmc@c8000200/wifi@1", "local-mac-address"],
                              capture_output=True)
check(mac_property.returncode != 0, "no static or copied MAC in public DTB")
startup_patched = kernel_out / "arch/arm/boot/compressed/atags_to_fdt.o"
check(startup_patched.exists() and b"local-mac-address" in startup_patched.read_bytes(),
      "ARM decompressor includes Motorola MAC→FDT startup translator")

fw = root / "lib/firmware/brcm/brcmfmac4329-sdio.bin"
nv = root / "lib/firmware/brcm/brcmfmac4329-sdio.txt"
check(sha(fw) == "d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93",
      "firmware hash matches physical success baseline")
check(sha(nv) == "a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb",
      "NVRAM hash matches 1550-byte calibration baseline")
check(not re.search(rb"(?mi)^\s*(macaddr|ccode|regrev)\s*=", nv.read_bytes()),
      "public NVRAM has no identity or regulatory overrides")

modules = list((root / "lib/modules" / krel).rglob("*.ko*"))
for name in ("brcmfmac.ko", "brcmfmac-wcc.ko", "brcmutil.ko"):
    check(any(p.name.startswith(name) for p in modules),
          "separate upstream module installed: " + name)
check((root / "lib/modules" / krel / "modules.dep").is_file(), "depmod index present")
brcmfmac = next(p for p in modules if p.name == "brcmfmac.ko")
check(b"XOOM_V0" not in brcmfmac.read_bytes(), "no XOOM_Vxx instrumentation in native brcmfmac")
check((root / "etc/systemd/system/getty.target.wants/serial-getty@ttyGS0.service").is_symlink(),
      "normal USB gadget serial login is enabled")
check((root / "etc/systemd/system/multi-user.target.wants/mz600-wlan.service").is_symlink(),
      "identity-gated WLAN startup enabled")
check(root_selector + " / ext4" in (root / "etc/fstab").read_text(),
      "native root fstab matches selected Linux root partition")
check("xoom:$6$" in (root / "etc/shadow").read_text(),
      "owner account has non-default generated hash (secret not printed)")
check(not (root / "usr/bin/qemu-arm-static").exists(), "host QEMU build helper excluded from OS image")

# fsck exit code 0 = clean; -n does not write to the image.
fsck = subprocess.run(["e2fsck", "-fn", str(system_image)], text=True, capture_output=True)
check(fsck.returncode == 0, "offline ext4 integrity check clean (no write)")
# Confirm *packaged ext4 contents*, not just the staging directory.
# debugfs performs read-only filesystem metadata lookups without mounting it.
from pathlib import PurePosixPath
for artifact in (
    root / "etc/hostname",
    root / "etc/shadow",
    root / "lib/firmware/brcm/brcmfmac4329-sdio.bin",
    root / "lib/firmware/brcm/brcmfmac4329-sdio.txt",
    next(p for p in modules if p.name == "brcmfmac-wcc.ko"),
):
    on_disk = "/" + artifact.resolve().relative_to(root.resolve()).as_posix()
    proc = subprocess.run(["debugfs", "-R", "stat " + on_disk,
                           str(system_image)], text=True, capture_output=True)
    check("Inode:" in proc.stdout and "Type:" in proc.stdout,
          "ext4 packaged inode exists: " + on_disk)

check((out / "NOT_INSTALLED.txt").exists(), "persistent-install hold marker")
print("NATIVE_OS_OFFLINE_ACCEPTANCE_PASS", "kernel=" + krel,
      "boot_bytes=" + str(len(boot)), "system_sha256=" + sha(system_image),
      "boot_sha256=" + sha(out / "xoom-linux-boot.img"))
print("DEVICE_FLASHED=NO BOOT_TESTED=NO FACTORY_MAC_RUNTIME_UNVERIFIED")
