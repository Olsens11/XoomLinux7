#!/usr/bin/env python3
"""Diagnostic AB control: v06 clean upstream kernel + byte-exact proven v04 PID1.

Changes ONLY kernel payload relative to successful noSD-v04 control, and ONLY
userspace ramdisk relative to failed-on-USB v06 WiFi/BT first boot.
NO DEVICE ACCESS, NO FLASH.
"""
from pathlib import Path
import struct,hashlib,json
base=Path("/home/xoomdev/xoom-linux-rom/clean-upstream-usb-20261025/artifacts")
new=Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/artifacts")
z=(new/"zImage-with-stingray-wifi-bt.dtb").read_bytes()
r=(base/"phase1-v04-usb-readonly.cpio.gz").read_bytes()
old=(base/"MZ600-UPSTREAM-2404d273-USB-v04-RAM-ONLY-UNTESTED.img").read_bytes()
def sha(data):return hashlib.sha256(data).hexdigest()
assert sha(old)=="da6de4c2add6d2b13be993898db6ff9930440a8adf55adf2bd195f32fa45528b"
assert sha(z)=="c81765bb8c43c44bc232da932d5547c32516c3c8259bd3e796ab6bf1f9b9dbfe"
assert sha(r)=="e06a62070ef255fed1db39c7d22e6b1d2a6ab6955258eacd3c8dffa50f69d8ba"
pg=2048
head=bytearray(old[:pg])
assert head[:8]==b"ANDROID!"
struct.pack_into("<I",head,8,len(z))
struct.pack_into("<I",head,16,len(r))
sha1=hashlib.sha1()
for d in (z,r,b"",b""):
 sha1.update(d);sha1.update(struct.pack("<I",len(d)))
head[576:596]=sha1.digest()
out=bytes(head)+z+b"\0"*(-len(z)%pg)+r+b"\0"*(-len(r)%pg)
assert len(out)<8388608
dst=new/"MZ600-V06-KERNEL-V04-USB-AB-CONTROL-RAM-ONLY.img"
dst.write_bytes(out)
manifest={"status":"OFFLINE ONLY, NOT PHYSICALLY TESTED","image":dst.name,
          "bytes":len(out),"sha256":sha(out),
          "kernel_sha256":sha(z),"ramdisk_sha256":sha(r),
          "purpose":"Decide whether v06 host USB write-timeouts come from v06 kernel or v06 USB program/CPIO.",
          "unchanged":"firmware eMMC p7/p8 TWRP and user SD; no module/radio startup"}
(new/"v06-v04-ab-control.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("V06_V04_AB_CONTROL_OFFLINE_PASS",len(out),sha(out))
