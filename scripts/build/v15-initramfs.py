#!/usr/bin/env python3
"""Deterministic v15 RAM-only rootfs: stable PID1, replaceable SDIO modules and firmware."""
from pathlib import Path
import gzip,io,hashlib,stat
B=Path('/home/xoomdev/xoom-linux-rom')
V=B/'phase1-v15'
O=B/'build-wingray-gcc14-initramfs'
F=B/'firmware-reference-v07/brcm'
mods=[
(V/'init','init'),
(O/'drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko','wifi/brcmutil.ko'),
(O/'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko','wifi/brcmfmac.ko'),
(F/'brcmfmac4329-sdio.bin','lib/firmware/brcm/brcmfmac4329-sdio.bin'),
(F/'brcmfmac4329-sdio.txt','lib/firmware/brcm/brcmfmac4329-sdio.txt')
]
for source,name in mods:
 dat=source.read_bytes()
 if name.startswith('wifi/') or name=='init':
  assert dat[:4]==b'\x7fELF',name
 if name.endswith('.txt'):
  assert not any(line.lstrip().startswith(k) for line in dat.splitlines() for k in (b'macaddr=',b'ccode=',b'regrev=')),name
 print(name,len(dat),hashlib.sha256(dat).hexdigest())
entries=[
('dev',0o040755,b'',0,0),
('proc',0o040555,b'',0,0),
('sys',0o040555,b'',0,0),
('run',0o040755,b'',0,0),
('tmp',0o040777,b'',0,0),
('wifi',0o040755,b'',0,0),
('lib',0o040755,b'',0,0),
('lib/firmware',0o040755,b'',0,0),
('lib/firmware/brcm',0o040755,b'',0,0),
('dev/console',0o020600,b'',5,1),
('dev/null',0o020666,b'',1,3)]
for src,name in mods:
 entries.append((name,0o100755 if name=='init' else 0o100644,src.read_bytes(),0,0))
out=io.BytesIO()
def pad():out.write(b'\0'*(-out.tell()%4))
def item(i,name,mode,dat,rmajor,rminor):
 n=name.encode()+b'\0'
 fields=[i,mode,0,0,2 if stat.S_ISDIR(mode) else 1,0,len(dat),0,0,rmajor,rminor,len(n),0]
 out.write(b'070701'+b''.join(('%08X'%x).encode() for x in fields));out.write(n);pad();out.write(dat);pad()
for i,x in enumerate(entries,1):item(i,*x)
item(len(entries)+1,'TRAILER!!!',0,b'',0,0)
blob=out.getvalue()
target=V/'phase1-initramfs.cpio.gz'
with target.open('wb') as fp:
 with gzip.GzipFile(fileobj=fp,mode='wb',filename='',mtime=0,compresslevel=9) as f:f.write(blob)
print('V15 BUNDLED RAM ROOTFS',len(blob),'UNCOMPRESSED',target.stat().st_size,'GZIP',hashlib.sha256(target.read_bytes()).hexdigest())
