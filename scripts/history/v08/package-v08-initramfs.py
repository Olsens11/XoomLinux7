#!/usr/bin/env python3
"""Build deterministic RAM-only initramfs containing v08 userland and two upstream modules."""
from pathlib import Path
import gzip, io, hashlib, stat
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v08'
paths=[
 (v/'init','init'),
 (b/'build-wingray-gcc14-initramfs/drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko','wifi/brcmutil.ko'),
 (b/'build-wingray-gcc14-initramfs/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko','wifi/brcmfmac.ko')]
for source,name in paths:
 content=source.read_bytes()
 assert content[:4]==b'\x7fELF' and content[4]==1,(name,'not 32bit ELF')
 print(name,len(content),hashlib.sha256(content).hexdigest())
entries=[
 ("dev",0o040755,b"",0,0),
 ("proc",0o040555,b"",0,0),
 ("sys",0o040555,b"",0,0),
 ("run",0o040755,b"",0,0),
 ("tmp",0o040777,b"",0,0),
 ("wifi",0o040755,b"",0,0),
 ("dev/console",0o020600,b"",5,1),
 ("dev/null",0o020666,b"",1,3)]
for f,n in paths:entries.append((n,0o100755 if n=="init" else 0o100644,f.read_bytes(),0,0))
out=io.BytesIO()
def pad():out.write(b'\0'*((-out.tell())%4))
def writeentry(i,name,mode,data,rmajor,rminor):
 bname=name.encode()+b'\0'
 fields=[i,mode,0,0,2 if stat.S_ISDIR(mode) else 1,0,len(data),0,0,rmajor,rminor,len(bname),0]
 head=b'070701'+b''.join(('%08X'%q).encode() for q in fields)
 assert len(head)==110
 out.write(head);out.write(bname);pad();out.write(data);pad()
for i,e in enumerate(entries,1):writeentry(i,*e)
writeentry(len(entries)+1,"TRAILER!!!",0,b'',0,0)
uncompressed=out.getvalue()
target=v/'phase1-initramfs.cpio.gz'
with target.open('wb') as f:
 with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=9) as z:z.write(uncompressed)
print('V08 CPIO entries',len(entries),'UNCOMPRESSED',len(uncompressed),'GZIP',target.stat().st_size,'SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
