#!/usr/bin/env python3
"""Negative controls for Xoom forensic lab. Mutates temporary copies ONLY."""
import argparse, pathlib, subprocess, tempfile, sys
from audit import extract_boot, cpio_entries, nvram_transform, nvram_packed_token_valid, audit
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--image",required=True,type=pathlib.Path)
    ap.add_argument("--dtb",required=True,type=pathlib.Path)
    ap.add_argument("--arm",required=True,type=pathlib.Path)
    ap.add_argument("--linux-src",required=True,type=pathlib.Path)
    ap.add_argument("--init-src",required=True,type=pathlib.Path)
    a=ap.parse_args()
    count=0
    def mark(name,p):
        nonlocal count
        assert p,name
        count+=1
        print("FAULT_DETECTED",name)
    def arm(path):
        return subprocess.run(["qemu-arm","-cpu","cortex-a9",str(a.arm),str(path),
          "100","300","25000000"],capture_output=True,text=True)
    assert arm(a.dtb).returncode==0, "Valid real DTB rejected"
    print("CONTROL_PASS baseline-arm-good")
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td)/"wrong-value.dtb"
        p.write_bytes(a.dtb.read_bytes())
        subprocess.run(["fdtput","-t","x",str(p),"/mmc@c8000200",
                        "post-power-on-delay-ms","a"],check=True)
        mark("wrong-property-value",arm(p).returncode!=0)
        p=pathlib.Path(td)/"wrong-node.dtb"
        p.write_bytes(a.dtb.read_bytes())
        subprocess.run(["fdtput","-d",str(p),"/mmc@c8000200",
                        "post-power-on-delay-ms"],check=True)
        # Value also exists on the separate pwrseq node; MMC host consumer must reject this.
        mark("right-value-on-wrong-node",arm(p).returncode!=0)
        p=pathlib.Path(td)/"wrong-parent.dtb"
        p.write_bytes(a.dtb.read_bytes())
        subprocess.run(["fdtput","-t","x",str(p),"/wifi-pwrseq",
                       "post-power-on-delay-ms","64"],check=True)
        # This is an intentional negative: only pwrseq is 100; host remains 100;
        # QEMU must reject because pwrseq should be 300.
        mark("pwrseq-vs-host-property-confusion",arm(p).returncode!=0)
        b=bytearray(a.image.read_bytes())
        b[2048+400]^=1
        img=pathlib.Path(td)/"broken-boot.img"
        img.write_bytes(b)
        try:extract_boot(img)
        except AssertionError:mark("tampered-boot-payload",True)
        else:raise AssertionError("boot checksum mutation unnoticed")
        _,_,ram,_=extract_boot(a.image)
        files=cpio_entries(ram)
        nv=files["lib/firmware/brcm/brcmfmac4329-sdio.txt"]["content"]
        result,_=nvram_transform(nv)
        # Correctly excluded RAW1, and packed NVRAM includes 4-byte length token.
        assert len(result)==672 and nvram_packed_token_valid(result)
        corrupted=bytearray(result)
        corrupted[-1]^=0x80
        mark("nvram-binary-roundup-token",not nvram_packed_token_valid(corrupted))
        altered=nv.replace(b"RAW1=",b"RAWX=",1)
        mutated,_=nvram_transform(altered)
        mark("synthetic-nvram-content-corruption",mutated!=result)
        try:
            audit(a.image,p,a.linux_src,a.init_src)
        except AssertionError as exc:
            mark("compiled-dtb-vs-boot-integrity-reject",
                 "DTB" in str(exc) or "appended" in str(exc))
        else:
            raise AssertionError("unexpected artifact integrity pass")
    print("NEGATIVE_CONTROLS_PASS",count)
if __name__=="__main__":main()
