#!/usr/bin/env python3
"""v022 datasheet Section 11 control, AUTO/legacy SDIO @ max 25 MHz.
Rebuild nothing. Patch ONLY the compiled SDMMC2 max-frequency property of the
physically qualified v020 temporary-boot image, then recompute Android header
hash. Fail closed on ANY unexpected byte or source artifact.
"""
from pathlib import Path
import hashlib,struct,json,shutil
R=Path('/home/xoomdev/projects/XoomLinux7-legacy25')
BASE=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v20-MMC2-ON-DEMAND')
V19=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v19-OEM-SDIO-CAPS-25MHZ')
DEST=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v22-AUTO-LEGACY25-CONTROL')
OLD=BASE/'MZ600-stingray-diagnostic-v20-MMC2-ON-DEMAND-TEMPBOOT-ONLY.img'
OUTPUT=DEST/'MZ600-stingray-diagnostic-v22-AUTO-LEGACY25-TEMPBOOT-ONLY.img'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert R.exists()
before=OLD.read_bytes()
expected='96f01d72782cd3ab6574b806a0d84b1874ec0f98bbe865c74365623ba7148067'
assert sha(before)==expected,('unexpected baseline image',sha(before))
assert len(before)==6662144
assert before[:8]==b'ANDROID!'
header=struct.unpack_from('<10I',before,8)
kl,ka,rl,ra,sec,sa,ta,page,dt,zero=header
assert (ka,ra,sec,sa,ta,page,dt)==(0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
assert before[64:576].split(b'\0')[0].find(b'rdinit=/init')>=0
assert before[64:576].split(b'\0')[0].find(b'brcmfmac.debug=6')>=0
kernel=before[page:page+kl]
ramoffset=page+((kl+page-1)//page)*page
ram=before[ramoffset:ramoffset+rl]
old_dtb=(BASE/'tegra20-motorola-stingray-usbdiag.dtb').read_bytes()
new_dtb=(V19/'tegra20-motorola-stingray-usbdiag.dtb').read_bytes()
assert len(old_dtb)==len(new_dtb) and len(old_dtb)>50000
assert kernel.endswith(old_dtb)
assert ram==(BASE/'phase1-initramfs.cpio.gz').read_bytes()
assert sha(ram)=='060664a25adf9fa90136e0e10fd186f41fb397b920698c04d8e89b100a8fcb67'
old_bytes=struct.pack('>I',46153846)
new_bytes=struct.pack('>I',25000000)
positions=[i for i,(x,y) in enumerate(zip(old_dtb,new_dtb)) if x!=y]
offset=positions[0]
assert positions==list(range(offset,offset+4))
assert old_dtb[offset:offset+4]==old_bytes
assert new_dtb[offset:offset+4]==new_bytes
assert positions==[offset+i for i in range(4)],('DTB modified beyond max-frequency',positions[:30])
assert old_dtb[:offset]==new_dtb[:offset]
assert old_dtb[offset+4:]==new_dtb[offset+4:]
dest=bytearray(before)
dtb_location=page+kl-len(old_dtb)
dest[dtb_location:dtb_location+len(old_dtb)]=new_dtb
newkernel=bytes(dest[page:page+kl])
m=hashlib.sha1()
for blob in (newkernel,ram,b'',b''):
    m.update(blob)
    m.update(struct.pack('<I',len(blob)))
dest[576:596]=m.digest()
candidate=bytes(dest)
assert len(candidate)==len(before)
changed=[i for i,(a,b) in enumerate(zip(before,candidate)) if a!=b]
assert changed==sorted(set(range(576,596))&set(changed) | set(range(dtb_location+offset,dtb_location+offset+4)))
assert all(576<=i<596 or dtb_location+offset<=i<dtb_location+offset+4 for i in changed)
assert candidate[page:page+kl]==newkernel
assert candidate[ramoffset:ramoffset+rl]==ram
assert candidate[dtb_location:dtb_location+len(new_dtb)]==new_dtb
assert candidate[:8]==b'ANDROID!'
assert candidate[576:596]==m.digest()
assert b'MMC2_PROFILE' not in kernel # compressed image, no literal expected
DEST.mkdir(parents=True,exist_ok=True)
OUTPUT.write_bytes(candidate)
(DEST/'tegra20-motorola-stingray-usbdiag.dtb').write_bytes(new_dtb)
(DEST/'v020-kernel-zImage.sha256').write_text(sha((BASE/'zImage').read_bytes())+'\n')
manifest={
    'classification':'RAM-ONLY fastboot boot; DO NOT FLASH',
    'description':'v020 exact baseline boot image with ONLY compiled SDMMC2 DTB max-frequency 46153846->25000000 and Android header digest adjusted. Initial runtime profile AUTO.',
    'baseline_image_sha256':sha(before),'baseline_image_bytes':len(before),
    'variant_image_sha256':sha(candidate),'variant_image_bytes':len(candidate),
    'baseline_dtb_sha256':sha(old_dtb),'variant_dtb_sha256':sha(new_dtb),
    'old_max_frequency':46153846,'new_max_frequency':25000000,
    'kernel_zImage_sha256':sha((BASE/'zImage').read_bytes()),
    'ramfs_sha256':sha(ram),
    'image_changed_byte_count':len(changed),
    'image_changed_byte_locations':changed,
    'test_instructions':'Verify physical MMC2 profile AUTO=0, instrumented host clock <=25MHz and legacy timing=0, unchanged firmware/NVRAM, IOEx/IORx and F2 outcome. No report of physical PASS before test.'
}
(DEST/'V022_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('V022_IMAGE',OUTPUT)
print('V022_BYTES',len(candidate))
print('V022_SHA256',sha(candidate))
print('BASELINE_IMAGE_SHA256',sha(before))
print('DTB_CHANGES_ONLY_AT_PROPERTY_OFFSET',offset)
print('IMAGE_CHANGED_BYTES',len(changed))
print('KERNEL_SHA256',manifest['kernel_zImage_sha256'])
print('INITRAMFS_SHA256',sha(ram))
print('ANDROID_SHA1_RECOMPUTED',m.digest().hex())
print('NO_KERNEL_REBUILD_OR_DEVICE_WRITE')
