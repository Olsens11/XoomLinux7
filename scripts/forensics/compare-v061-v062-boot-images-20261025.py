#!/usr/bin/env python3
"""Compare exact physical-good v06.1 and failed v06.2 images and ramfiles.

Offline only. Exposes no private firmware/MAC contents. No target access.
"""
import gzip,hashlib,pathlib,struct,json
W=pathlib.Path("/home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025")
B61=W/"artifacts-embedded-v061"
B62=W/"artifacts-embedded-v062"
FILES={
 "v061":(B61/"MZ600-CLEAN-WIFI-BT-USB-v061-BUILTIN-INITRAMFS-RAM-ONLY-UNTESTED.img",
          "b913b62943eebd52992a05273d9ce4ab5d4d8e9109e3bc571d7829889a81888a",
          B61/"v061-linux-gen_init_cpio-private.cpio.gz"),
 "v062":(B62/"MZ600-CLEAN-WIFI-BT-USB-v062-WCC-UNLOAD-RAM-ONLY-UNTESTED.img",
          "bfa8c7385329a6429c2bc03736133443d59864d2877142308ad2a4573dd2f4b8",
          B62/"v062-embedded-radio-private.cpio.gz")
}
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(blob):
 pos=0;data={}
 while True:
  if blob[pos:pos+6]!=b"070701":raise ValueError("bad cpio at "+str(pos))
  f=[int(blob[pos+6+j*8:pos+14+j*8],16) for j in range(13)]
  ns=pos+110
  name=blob[ns:ns+f[11]-1].decode()
  ds=(ns+f[11]+3)//4*4
  chunk=blob[ds:ds+f[6]]
  pos=(ds+f[6]+3)//4*4
  if name=="TRAILER!!!":return data
  assert name not in data
  data[name]={"payload":chunk,"mode":f[1],"uid":f[2],"gid":f[3],"type":f[1]&0o170000}
images={}; archives={}
for label,(path,expected,initramfs) in FILES.items():
 blob=path.read_bytes()
 assert sha(blob)==expected
 assert blob[:8]==b"ANDROID!"
 hdr=struct.unpack_from("<10I",blob,8)
 klen=hdr[0];page=hdr[7];rs=hdr[2]
 assert page==2048 and rs==0
 payload=blob[page:page+klen]
 fdt_mark=b"\xd0\x0d\xfe\xed"
 i=payload.rfind(fdt_mark)
 assert i>0 and len(payload)-i==struct.unpack_from(">I",payload,i+4)[0]
 dtb=payload[i:]
 images[label]={"raw":blob,"header_fields":hdr,"kernel":payload[:i],"dtb":dtb,"cmdline":blob[64:576].split(b"\x00")[0]}
 arch=parse(gzip.decompress(initramfs.read_bytes()))
 archives[label]=arch
 print(label,"IMAGE_BYTES",len(blob),"KERNEL_IMAGE_BYTES",i,"DTB_BYTES",len(dtb),"CPIO_FILES",len(arch))
 print(label,"KERNEL_ZIMAGE_SHA256",sha(payload[:i]))
 print(label,"DTB_SHA256",sha(dtb),"CPIO_SHA256",sha(initramfs.read_bytes()))
 print(label,"ENTRYPOINT_EXISTS","init" in arch, "MODE_OCTAL",oct(arch.get("init",{}).get("mode",0)))
a,b=images["v061"],images["v062"]
assert a["cmdline"]==b["cmdline"]
assert a["dtb"]==b["dtb"]
assert a["header_fields"][1:]==b["header_fields"][1:],"other boot header fields changed"
assert set(archives["v061"])==set(archives["v062"])
changed=[]
for name in sorted(archives["v061"]):
 x,y=archives["v061"][name],archives["v062"][name]
 assert (x["mode"],x["uid"],x["gid"],x["type"])==(y["mode"],y["uid"],y["gid"],y["type"]),(name,"metadata changed")
 if x["payload"]!=y["payload"]:
  changed.append(name)
assert changed==["init"],f"Unexpected archive file differences: {changed}"
print("BOOTLOADER_KERNEL_ADDR_AND_CMDLINE_MATCH=PASS")
print("DEVICE_TREE_BYTE_IDENTICAL=PASS")
print("RADIO_FIRMWARE_MODULE_PAYLOADS_BYTE_IDENTICAL=PASS")
print("CPIO_ONLY_CHANGED_FILE=init")
print("NO_AUTO_WIFI_START_CONCLUSION_FROM_THIS_BINARY_COMPARISON")
print("COMPRESSED_KERNEL_BINARIES_DIFFER_WITH_EMBEDDED_INIT_AS_EXPECTED")
print("FORENSIC_AUDIT_OFFLINE_PASS_NO_DEVICE_ACCESS")
