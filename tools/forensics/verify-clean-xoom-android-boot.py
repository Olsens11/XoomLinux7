#!/usr/bin/env python3
"""Verify legacy Xoom Android boot.img structure without flashing or device access."""
import argparse
import gzip
import hashlib
import struct
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("image", type=Path)
p.add_argument("--expected-sha256", required=True)
args = p.parse_args()
raw = args.image.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == args.expected_sha256.lower(), "Unexpected image hash"
assert raw[:8] == b"ANDROID!"
kl, ka, rl, ra, sl, sa, ta, pg, dl, pad = struct.unpack_from("<10I", raw, 8)
assert (ka,ra,sl,sa,ta,pg,dl)==(0x10008000,0x11000000,0,0x10F00000,0x10000100,2048,0)
assert 0 < kl < 8388608 and 0 < rl < 1000000
off=pg
kernel=raw[off:off+kl]
off+= ((kl+pg-1)//pg)*pg
ram=raw[off:off+rl]
assert kernel.startswith(bytes.fromhex("000000ea")) or len(kernel)>100000, "Unrecognized kernel"
assert gzip.decompress(ram).startswith(b"070701"), "Missing newc archive"
assert len(raw) <= 8388608
sha1=hashlib.sha1()
for blob in (kernel,ram,b"",b""):
    sha1.update(blob)
    sha1.update(struct.pack("<I",len(blob)))
assert raw[576:596] == sha1.digest(), "Android boot SHA-1 mismatch"
print("ANDROID_BOOT_IMAGE_STRUCTURAL_PASS bytes=%d kernel=%d ramdisk=%d sha256=%s"%(len(raw),kl,rl,digest))
print("ANDROID_HEADER_SHA1_PASS; NO DEVICE ACCESS")
