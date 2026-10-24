#!/usr/bin/env python3
"""Independent v034 audit: all v033 bytes frozen except /init and Android header."""
from pathlib import Path
import gzip,hashlib,struct
R=Path(__file__).resolve().parents[2]
X=Path('/mnt/c/Users/olsen/XoomLinux/Phase1')
v33=(X/'Diagnostic-MZ600-v033-BT-USB-LAB/MZ600-v033-BLUETOOTH-USB-TEMPBOOT-ONLY.img').read_bytes()
v34=(X/'Diagnostic-MZ600-v034-HCI-IOCTL/MZ600-v034-HCI-IOCTL-TEMPBOOT-ONLY.img').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(v33)=='6806f2aa87abbfecf0b2f8a3625292de5366a4a52370d10e61cd53204069fb45'
assert sha(v34)=='9850361687f6d121119a0c3399cdc0abaa68d8e9714238aba5bb9b7207a0af39'
def parse(blob):
 assert blob[:8]==b'ANDROID!' and len(blob)<8*1024*1024
 h=struct.unpack_from('<10I',blob,8)
 kl,ka,rl,ra,ss,sa,ta,page,ds,unused=h
 assert page==2048
 align=lambda n:(n+page-1)//page*page
 k=blob[page:page+kl];r=blob[page+align(kl):page+align(kl)+rl]
 digest=hashlib.sha1()
 for p in (k,r,b'',b''):digest.update(p);digest.update(struct.pack('<I',len(p)))
 assert blob[576:596]==digest.digest()
 assert set(blob[page+kl:page+align(kl)])<={0}
 assert set(blob[page+align(kl)+rl:])<={0}
 return h,k,r
def entries(gz):
 b=gzip.decompress(gz)
 pos=0;results={}
 while True:
  assert b[pos:pos+6]==b'070701',pos
  f=[int(b[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
  start=pos+110
  name=b[start:start+f[11]-1].decode()
  assert b[start+f[11]-1]==0
  ds=(start+f[11]+3)//4*4
  data=b[ds:ds+f[6]]
  pos=(ds+f[6]+3)//4*4
  if name=='TRAILER!!!':
   assert set(b[pos:])<={0}
   break
  assert name not in results
  results[name]=(f[1],data)
 return results
h33,k33,r33=parse(v33);h34,k34,r34=parse(v34)
assert h33[0]==h34[0]
assert all(h33[i]==h34[i] for i in range(10) if i!=2)
assert v33[64:576]==v34[64:576] and k33==k34
e33=entries(r33);e34=entries(r34)
assert e33.keys()==e34.keys(),(e33.keys(),e34.keys())
changed=[n for n in e33 if e33[n]!=e34[n]]
assert changed==['init'],changed
orig_src=(R/'src/diag-init/phase1-v033/init.c').read_text()
fix_src=(R/'src/diag-init/phase1-v034/init.c').read_text()
assert orig_src.count('iof(fd,up?HCIDEVUP:HCIDEVDOWN,&dev)')==1
assert fix_src.count('iof(fd,up?HCIDEVUP:HCIDEVDOWN,(void *)(uintptr_t)dev)')==1
assert 'V034_HCI_IOCTL_BY_VALUE' in fix_src
assert b'V034_HCI_IOCTL_BY_VALUE' in e34['init'][1]
assert b'BT OFF HCI_DEV_DOWN COMPLETE' in e34['init'][1]
assert b'BT START PASS DRIVER REGISTERED; AUTO HARDWARE INIT MAY HAVE OCCURRED' in e34['init'][1]
assert e34['init'][0]==e33['init'][0]==0o100755
assert e34['init'][1]==Path('/home/xoomdev/xoom-linux-rom/phase1-v034/init').read_bytes()
print('V034_BOOT_HEADER_AND_RAMDISK_SHA1_PASS')
print('V034_KERNEL_DTB_CMDLINE_PRESERVED_SHA256',sha(k34))
print('V034_ONLY_INIT_CHANGED',changed)
print('V034_HCI_ABI_ARG_VALUE_SOURCE_TEST_PASS')
print('V034_V033_BLUETOOTH_MODULES_WLAN_FIRMWARE_IDENTITY_PASS')
print('V034_IMAGE_SHA256',sha(v34),'BYTES',len(v34))
print('V034_INDEPENDENT_AUDIT_PASS_NO_DEVICE_ACCESS')
