#!/usr/bin/env python3
"""Xoom Wi-Fi forensic lab v1: audit REAL Android image, FDT, initramfs,
firmware/NVRAM and Linux consumers. Host-only; no Xoom device access.
Source file evidence is not automatically proof of physical execution.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, pathlib, re, struct, subprocess, sys

def sha(b):return hashlib.sha256(b).hexdigest()
def must(condition,why):
    if not condition:raise AssertionError(why)
def extract_boot(image):
    data=image.read_bytes()
    must(data[:8]==b"ANDROID!","Not Android legacy boot image")
    ks,ka,rs,ra,ss,sa,tags,page,dt,zero=struct.unpack_from("<10I",data,8)
    must(page>=512 and (page & (page-1))==0 and dt==0,"Unsupported boot layout")
    aligned=lambda n:(n+page-1)//page*page
    ramstart=page+aligned(ks)
    kernel=data[page:page+ks]
    ram=data[ramstart:ramstart+rs]
    must(len(kernel)==ks and len(ram)==rs,"Truncated Android boot image")
    d=hashlib.sha1()
    for blob in (kernel,ram,b"",b""):
        d.update(blob);d.update(struct.pack("<I",len(blob)))
    must(data[576:596]==d.digest(),"Android boot id mismatch")
    return data,kernel,ram,{"kernel_size":ks,"initramfs_size":rs,"page_size":page,"boot_image_sha256":sha(data),"kernel_sha256":sha(kernel),"ram_sha256":sha(ram)}

def cpio_entries(archive):
    raw=gzip.decompress(archive)
    entries={}
    pos=0
    for idx in range(200000):
        must(raw[pos:pos+6]==b"070701",f"bad newc at {pos}")
        h=raw[pos:pos+110]
        fields=[int(h[6+i*8:14+i*8],16) for i in range(13)]
        size,namesize=fields[6],fields[11]
        pos+=110
        name=raw[pos:pos+namesize-1].decode("utf8")
        must(raw[pos+namesize-1:pos+namesize]==b"\0","bad cpio filename")
        pos=(pos+namesize+3)&~3
        content=raw[pos:pos+size]
        must(len(content)==size,"truncated cpio member")
        pos=(pos+size+3)&~3
        if name=="TRAILER!!!":break
        must(name not in entries,"duplicate cpio entry: "+name)
        entries[name]={"content":content,"mode":fields[1],"size":size,"sha256":sha(content)}
    else:raise AssertionError("cpio trailer missing")
    return entries

def fdt_prop(fdt,node,property):
    path=pathlib.Path(fdt)
    proc=subprocess.run(["fdtget","-t","x",str(path),node,property],capture_output=True,text=True)
    return {"exists":proc.returncode==0,"value":proc.stdout.strip() if proc.returncode==0 else None}

def source_match(path,regex):
    txt=path.read_text(encoding="utf8")
    m=re.search(regex,txt,re.M|re.S)
    return {"file":str(path),"line":txt.count("\n",0,m.start())+1 if m else None,"found":m is not None}

def nvram_transform(data,platform_mac=None):
    """Model firmware.c's simple ASCII nvram_parser path, not executed kernel C.
    Reject complex multi-device formats; platform MAC override is optional.
    Keep private MAC out of reports. End token format matches firmware.c.
    """
    if len(data)>64000:raise ValueError("oversized NV text")
    text=data.decode("ascii")
    lines=[]
    for line in text.splitlines():
        val=line.lstrip(" \r\t")
        if not val or val.startswith("#"):continue
        if val.startswith("RAW1="):continue
        val=val.split("#",1)[0].strip()
        if "=" not in val:continue
        key,v=val.split("=",1)
        if not key or any(ch.isspace() for ch in key):continue
        if not all(0x20<=ord(ch)<0x7f for ch in val):continue
        if key.startswith("devpath") or key.startswith("pcie/"):
            raise ValueError("multi-device format needs firmware.c branch-specific model")
        if key=="macaddr" and platform_mac is not None:continue
        lines.append(val)
    if not lines:raise ValueError("No NVRAM records")
    if not any(line.startswith("boardrev=") for line in lines):
        lines.append("boardrev=0xff")
    if platform_mac is not None:
        must(re.fullmatch("[0-9a-fA-F]{12}",platform_mac) is not None,"Invalid test MAC")
        mac=":".join(platform_mac[i:i+2] for i in range(0,12,2))
        lines.append("macaddr="+mac)
    body=b"\0".join(x.encode("ascii") for x in lines)+b"\0"
    aligned=(len(body)+1+3)&~3
    body+=b"\0"*(aligned-len(body))
    wordlen=len(body)//4
    token=((~wordlen&0xffff)<<16)|wordlen
    return body+struct.pack("<I",token),lines

def nvram_packed_token_valid(buf):
    """Broadcom packed NVRAM 4-byte pad + complement/length token."""
    if len(buf)<8 or len(buf)%4:
        return False
    count=(len(buf)-4)//4
    if count>0xffff:
        return False
    token=struct.unpack("<I",buf[-4:])[0]
    return (token & 0xffff)==count and (token >> 16)==(~count & 0xffff) and buf[-5]==0

def audit(image,dtb,kernel_root,init_source):
    boot,k,ram,info=extract_boot(image)
    compiled=dtb.read_bytes()
    must(k.endswith(compiled),"The declared DTB is NOT the appended boot kernel DTB")
    must(int.from_bytes(compiled[:4],"big")==0xd00dfeed,"DTB magic wrong")
    must(int.from_bytes(compiled[4:8],"big")<=len(compiled),"DTB totalsize invalid")
    must(sha(compiled)==sha(k[-len(compiled):]),"DTB changed")
    root=cpio_entries(ram)
    inittext=init_source.read_text()
    results={"schema":1,"status":"AUDIT_COMPLETED_NOT_HARDWARE_QUALIFICATION","image":info,
             "dtb_sha256":sha(compiled),"dt":{},"initramfs":{},"nvram":{},
             "consumers":[],"findings":[],"limits":[]}
    expected={
        ("/mmc@c8000200","post-power-on-delay-ms"):100,
        ("/mmc@c8000200","max-frequency"):25000000,
        ("/wifi-pwrseq","post-power-on-delay-ms"):300,
        ("/wifi-pwrseq","power-off-delay-us"):200,
        ("/regulator-wifi","regulator-min-microvolt"):3300000,
        ("/regulator-wifi","regulator-max-microvolt"):3300000,
    }
    for (node,prop),expected_val in expected.items():
        observed=fdt_prop(dtb,node,prop)
        value=int(observed["value"].split()[0],16) if observed["exists"] else None
        results["dt"][node+"/"+prop]={"value":value,"expected":expected_val,"match":value==expected_val}
        must(value==expected_val,f"DT mismatch {node}/{prop}: {value} expected {expected_val}")
    for node,properties in {
        "/mmc@c8000200":["mmc-pwrseq","vmmc-supply","vqmmc-supply","non-removable","status"],
        "/wifi-pwrseq":["reset-gpios","clocks","clock-names"],
        "/regulator-wifi":["gpio","enable-active-high","regulator-boot-on","phandle"]
    }.items():
        for prop in properties:
            x=fdt_prop(dtb,node,prop)
            results["dt"][node+"/"+prop]=x
            must(x["exists"],"Missing key required by this v025 wiring: "+node+"/"+prop)
    files=[
      ("lib/firmware/brcm/brcmfmac4329-sdio.bin","firmware"),
      ("lib/firmware/brcm/brcmfmac4329-sdio.txt","nvram_source"),
      ("wifi/brcmfmac.ko","driver_module"),
      ("wifi/brcmutil.ko","support_module"),
      ("init","diagnostic_pid1"),
    ]
    for filename,key in files:
        must(filename in root,"Missing firmware/rootfs entry: "+filename)
        f=root[filename]
        results["initramfs"][key]={"path":"/"+filename,"size":f["size"],"sha256":f["sha256"],"mode":oct(f["mode"]&0o777)}
    must(root["lib/firmware/brcm/brcmfmac4329-sdio.bin"]["size"]==253748,"Unexpected candidate firmware")
    text=root["lib/firmware/brcm/brcmfmac4329-sdio.txt"]["content"]
    b,lines=nvram_transform(text)
    results["nvram"]={"source_bytes":len(text),"modeled_packed_bytes":len(b),"modeled_packed_sha256":sha(b),
     "entry_count":len(lines),"contains_macaddr":any(x.startswith("macaddr=") for x in lines),
     "token_word_length":struct.unpack("<I",b[-4:])[0]&0xffff,
     "model_not_kernel_execution":True}
    results["nvram"]["matches_live_672byte_trace"]=len(b)==672
    results["nvram"]["packed_token_valid"]=nvram_packed_token_valid(b)
    must(results["nvram"]["packed_token_valid"],"Malformed modeled Broadcom NVRAM token")
    must(not results["nvram"]["contains_macaddr"],"Unexpected MAC in generic NVRAM")
    if len(b)!=672:results["findings"].append({"severity":"investigate","subject":"NVRAM packed length differs from observed v025 672-byte transfer","observed":len(b)})
    fwbase=kernel_root/"drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.h"
    fwm=kernel_root/"drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c"
    sdio=kernel_root/"drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c"
    core=kernel_root/"drivers/mmc/core/core.c"
    host=kernel_root/"drivers/mmc/core/host.c"
    pwr=kernel_root/"drivers/mmc/core/pwrseq_simple.c"
    for file,expr,tag in [
       (fwbase,r'#define\s+BRCMF_FW_DEFAULT_PATH\s+"brcm/"',"firmware-name-prefix"),
       (fwm,r'static void \*brcmf_fw_nvram_strip',"nvram-strip-entry"),
       (fwm,r'eth_platform_get_mac_address\(dev, mac\)',"platform-MAC-override"),
       (fwm,r'brcmf_fw_request_firmware\(const',"firmware-request"),
       (sdio,r'brcmf_fw_alloc_request\(', "sdio-firmware-map"),
       (core,r'void mmc_power_up\(struct mmc_host \*host',"mmc-power-up"),
       (core,r'mmc_delay\(host->ios.power_delay_ms\)',"host-power-delay"),
       (host,r'device_property_read_u32\(dev,\s*"post-power-on-delay-ms"', "host-property-parser"),
       (pwr,r'device_property_read_u32\(dev,\s*"post-power-on-delay-ms"', "pwrseq-property-parser"),
       (pwr,r'static void mmc_pwrseq_simple_pre_power_on', "pwrseq-pre"),
       (pwr,r'static void mmc_pwrseq_simple_post_power_on',"pwrseq-post"),
       (pwr,r'\.name\s*=\s*"pwrseq_simple"',"sysfs-driver-registration"),
    ]:
       m=source_match(file,expr)
       results["consumers"].append({"step":tag,"source":str(file.relative_to(kernel_root)),"line":m["line"],"found":m["found"]})
       must(m["found"],"Kernel source pattern changed: "+tag)
    wrong_path='/sys/bus/platform/drivers/mmc-pwrseq-simple'
    registered='/sys/bus/platform/drivers/pwrseq_simple'
    results["findings"].append({"severity":"confirmed-tool-error","subject":"Old diagnostic referenced incorrect driver sysfs path",
      "incorrect":wrong_path,"correct":registered,"source_in_init":wrong_path in inittext})
    results["findings"].append({"severity":"open-runtime-question","subject":"vmmc regulator-boot-on may prevent a full power-cycle during MMC2 rebind",
      "software_configured":True,"physical_power_cycle_proven":False})
    results["findings"].append({"severity":"runtime-provenance-unverified",
      "subject":"Firmware loader supports board-specific candidates and module firmware_path override",
      "path_exist_in_image":True,"actual_request_path_recorded":False,
      "source":"brcmfmac/firmware.c and sdio.c"})
    results["findings"].append({"severity":"runtime-provenance-unverified",
      "subject":"Generic NVRAM intentionally omits per-device MAC; verify Linux fallback identity and optional platform MAC override",
      "has_embedded_mac":False,"actual_chip_mac_source_verified":False})
    results["limits"]=[
      "qemu-arm userspace ARM consumer checks DEVICE TREE bytes but does not boot original Tegra20 kernel or emulate BCM4329, SDMMC2, GPIO rails or electrical timing.",
      "Modeled NVRAM packer mirrors simple firmware.c path, but is not actual kernel C execution or a byte-for-byte confirmation of what the chip consumed.",
      "Cold boot firmware lookup can prefer board-specific paths; RAM USB uploads can replace files. Image contents alone do not prove each runtime firmware request.",
      "No private OEM firmware, MAC address or board calibration values copied into public project, reports or tests.",
      "Source callback order does not independently prove hardware event delivery or arrival order at BCM4329.",
    ]
    return results

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--image",type=pathlib.Path,required=True)
    ap.add_argument("--dtb",type=pathlib.Path,required=True)
    ap.add_argument("--linux-src",type=pathlib.Path,required=True)
    ap.add_argument("--init-src",type=pathlib.Path,required=True)
    ap.add_argument("--report",type=pathlib.Path,required=True)
    ap.add_argument("--private-nvram-source",type=pathlib.Path)
    ap.add_argument("--private-nvram-model",type=pathlib.Path)
    args=ap.parse_args()
    facts=audit(args.image,args.dtb,args.linux_src,args.init_src)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(facts,indent=2)+"\n")
    if bool(args.private_nvram_source) != bool(args.private_nvram_model):
        raise ValueError("Both private NVRAM output paths required together")
    if args.private_nvram_source:
        _,_,ram,_=extract_boot(args.image)
        files=cpio_entries(ram)
        raw=files["lib/firmware/brcm/brcmfmac4329-sdio.txt"]["content"]
        model,items=nvram_transform(raw)
        for dest,content in ((args.private_nvram_source,raw),(args.private_nvram_model,model)):
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(content)
        print("PRIVATE_NVRAM_EXTRACTION_DONE",len(raw),len(model))
    print("FORENSIC_AUDIT_PASS")
    print("IMAGE_SHA256",facts["image"]["boot_image_sha256"])
    print("DTB_SHA256",facts["dtb_sha256"])
    print("NVRAM_MODELED_BYTES",facts["nvram"]["modeled_packed_bytes"])
    print("NVRAM_MATCHES_LIVE_SIZE",facts["nvram"]["matches_live_672byte_trace"])
    print("SOURCE_CONSUMERS",len(facts["consumers"]))
    print("REPORT",args.report)
if __name__=="__main__":main()
