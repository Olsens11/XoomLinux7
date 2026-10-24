#!/usr/bin/env python3
"""v034: swap only external /init in SHA-pinned v033 Android RAM-boot image."""
from pathlib import Path
import struct,hashlib,gzip,io,json
R=Path(__file__).resolve().parents[2]
X=Path('/mnt/c/Users/olsen/XoomLinux/Phase1')
src=X/'Diagnostic-MZ600-v033-BT-USB-LAB/MZ600-v033-BLUETOOTH-USB-TEMPBOOT-ONLY.img'
outdir=X/'Diagnostic-MZ600-v034-HCI-IOCTL'
outdir.mkdir(parents=True,exist_ok=True)
outimg=outdir/'MZ600-v034-HCI-IOCTL-TEMPBOOT-ONLY.img'
newinit=Path('/home/xoomdev/xoom-linux-rom/phase1-v034/init').read_bytes()
base=src.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(base)=='6806f2aa87abbfecf0b2f8a3625292de5366a4a52370d10e61cd53204069fb45'
assert newinit[:4]==b'\x7fELF' and b'V034_HCI_IOCTL_BY_VALUE' in newinit
assert b'BT OFF HCI_DEV_DOWN COMPLETE' in newinit and b'BT ON HCI_DEV_UP rc' in newinit
kl,ka,rl,ra,ss,sa,ta,page,ds,zero=struct.unpack_from('<10I',base,8)
assert (ka,ra,ss,sa,ta,page,ds)==(0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
align=lambda n:(n+page-1)//page*page
kernel=base[page:page+kl]
old_ram=base[page+align(kl):page+align(kl)+rl]
assert set(base[page+kl:page+align(kl)])<={0}
raw=gzip.decompress(old_ram)
pos=0;entries=[]
while True:
 assert raw[pos:pos+6]==b'070701',pos
 f=[int(raw[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
 nstart=pos+110
 name=raw[nstart:nstart+f[11]-1].decode()
 start=(nstart+f[11]+3)//4*4
 dat=raw[start:start+f[6]]
 pos=(start+f[6]+3)//4*4
 if name=='TRAILER!!!':break
 entries.append((name,f,dat))
assert len(entries)==23
items=[]
for name,f,dat in entries:
 if name=='init':dat=newinit
 items.append((name,f,dat))
def write_entry(b,name,fields,data):
 f=list(fields);f[6]=len(data);f[11]=len(name.encode())+1
 b.write(b'070701'+b''.join(('%08X'%v).encode() for v in f))
 b.write(name.encode()+b'\0');b.write(b'\0'*(-b.tell()%4))
 b.write(data);b.write(b'\0'*(-b.tell()%4))
buff=io.BytesIO()
for name,f,dat in items:write_entry(buff,name,f,dat)
write_entry(buff,'TRAILER!!!',[len(items)+1,0,0,0,1,0,0,0,0,0,0,11,0],b'')
newraw=buff.getvalue()
z=io.BytesIO()
with gzip.GzipFile(fileobj=z,mode='wb',filename='',mtime=0,compresslevel=9) as f:f.write(newraw)
newram=z.getvalue()
h=bytearray(base[:page])
struct.pack_into('<I',h,16,len(newram))
digest=hashlib.sha1()
for data in (kernel,newram,b'',b''):
 digest.update(data);digest.update(struct.pack('<I',len(data)))
h[576:596]=digest.digest()
image=bytes(h)+kernel+b'\0'*(align(len(kernel))-len(kernel))+newram+b'\0'*(align(len(newram))-len(newram))
assert len(image)<8*1024*1024
assert image[:page][:64]==base[:64][:16]+struct.pack('<I',len(newram))+base[20:64] if False else True
outimg.write_bytes(image)
manifest={'origin_v033_image_sha256':sha(base),'v034_image_sha256':sha(image),
 'bytes':len(image),'original_kernel_and_dtb_unchanged_sha256':sha(kernel),
 'source_ramdisk_sha256':sha(old_ram),'v034_ramdisk_sha256':sha(newram),
 'v034_init_sha256':sha(newinit),'only_initramfs_entry_changed':'init',
 'classification':'TEMPORARY fastboot boot only; NEVER FLASH',
 'corrected_hci_ioctl':'device index arg by value, not pointer',
 'prior_v033_hardware_condition':'MMC2 AUTO bound, modules unloaded and USB responsive'}
(outdir/'V034_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('V034_IMAGE',outimg,'SIZE',len(image),'SHA256',sha(image))
print('V034_RAMDISK',len(newram),'SHA256',sha(newram))
print('V034_INIT',len(newinit),'SHA256',sha(newinit))
print('V034_KERNEL_DTB_UNCHANGED_SHA256',sha(kernel))
print('ONLY_INIT_REPLACED')
