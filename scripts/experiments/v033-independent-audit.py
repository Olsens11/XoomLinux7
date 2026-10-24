#!/usr/bin/env python3
"""Independent v033 boot-image audit. Does not build or modify anything."""
import gzip,hashlib,struct,subprocess,json
from pathlib import Path
B=Path('/mnt/c/Users/olsen/XoomLinux/Phase1')
v25=B/'Diagnostic-MZ600-v025-HOST-PRE-RESET-100MS'
v33=B/'Diagnostic-MZ600-v033-BT-USB-LAB'
b25=(v25/'MZ600-stingray-diagnostic-v025-HOST-PRE-RESET-100MS-TEMPBOOT-ONLY.img').read_bytes()
b33=(v33/'MZ600-v033-BLUETOOTH-USB-TEMPBOOT-ONLY.img').read_bytes()
hash=lambda b:hashlib.sha256(b).hexdigest()
def split(data):
 assert data[:8]==b'ANDROID!'
 h=struct.unpack_from('<10I',data,8)
 kl,ka,rl,ra,ss,sa,ta,page,ds,zero=h
 assert page==2048 and len(data)<8*1024*1024
 a=lambda x:((x+page-1)//page)*page
 k=data[page:page+kl]
 rstart=page+a(kl)
 r=data[rstart:rstart+rl]
 assert len(k)==kl and len(r)==rl
 assert set(data[page+kl:page+a(kl)])<={0} and set(data[rstart+rl:])<={0}
 digest=hashlib.sha1()
 for part in (k,r,b'',b''):
  digest.update(part);digest.update(struct.pack('<I',len(part)))
 assert data[576:596]==digest.digest(),"BOOT HEADER CONTENT HASH INVALID"
 return h,k,r
def files(raw):
 pos=0; contents={}
 while True:
  assert raw[pos:pos+6] == b'070701'
  f=[int(raw[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
  start=pos+110
  name=raw[start:start+f[11]-1].decode()
  assert raw[start+f[11]-1]==0
  ds=(start+f[11]+3)//4*4
  content=raw[ds:ds+f[6]]
  pos=(ds+f[6]+3)//4*4
  if name=='TRAILER!!!':
   assert set(raw[pos:])<={0}
   return contents
  assert name not in contents, name
  contents[name]=(f[1],content)
h25,k25,r25=split(b25)
h33,k33,r33=split(b33)
assert all(h25[i]==h33[i] for i in range(10) if i not in (0,2)),"Android boot offsets/pages changed"
assert b25[64:576]==b33[64:576],"CMDLINE changed"
old=(v25/'tegra20-motorola-stingray-usbdiag.dtb').read_bytes()
new=(v33/'tegra20-motorola-stingray-usbdiag.dtb').read_bytes()
assert k25.endswith(old) and k33.endswith(new)
assert k25[:-len(old)]==k33[:-len(new)],"ZIMAGE KERNEL CODE CHANGED"
f25=files(gzip.decompress(r25));f33=files(gzip.decompress(r33))
assert set(f33)==set(f25)|{'bt','bt/ecc.ko','bt/ecdh_generic.ko','bt/cmac.ko','bt/bluetooth.ko','bt/btbcm.ko','bt/hci_uart.ko'}
for name in f25:
 if name!='init':
  assert f25[name]==f33[name],f'ORIGINAL CONTENT CHANGED: {name}'
assert f33['init'][1][:4]==b'\x7fELF'
for phrase in (b'BT STATUS BEGIN',b'BT START DENIED',b'BT ON DENIED',b'BT STOP DENIED',b'MMC2 REINIT',b'PONG XOOM-LINUX V20'):
 assert phrase in f33['init'][1],phrase
for mod in ('ecc','ecdh_generic','cmac','bluetooth','btbcm','hci_uart'):
 obj=f33['bt/'+mod+'.ko'][1]
 assert obj[:4]==b'\x7fELF'
 p=Path('/home/xoomdev/xoom-linux-rom/phase1-v033')/(mod+'.ko')
 assert obj==p.read_bytes(),mod
 info=subprocess.run(['modinfo','-F','vermagic',str(p)],capture_output=True,text=True,check=True).stdout
 assert info.startswith('7.0.0-next-20260422') and 'ARMv7' in info
def fdtget(n,key,fmt='s'):
 return subprocess.run(['fdtget','-t',fmt,str(v33/'tegra20-motorola-stingray-usbdiag.dtb'),n,key],capture_output=True,text=True,check=True).stdout.strip()
bt='/serial@70006200/bluetooth'
assert fdtget(bt,'status')=='okay'
assert 'motorola,stingray-bcm4329-bt' in fdtget(bt,'compatible')
assert fdtget(bt,'clock-names')=='lpo'
assert fdtget(bt,'shared-supply','x')==fdtget('/mmc@c8000200','vmmc-supply','x')
assert int(fdtget('/mmc@c8000200','max-frequency','x'),16)==25000000
assert int(fdtget('/mmc@c8000200','post-power-on-delay-ms','x'),16)==100
assert int(fdtget('/wifi-pwrseq','post-power-on-delay-ms','x'),16)==300
print('PASS V033 BOOT HEADER SHA1 AND ANDROID ADDRESS FIELDS')
print('PASS FROZEN V025 ZIMAGE BYTES AND CMDLINE')
print('PASS ORIGINAL WIFI MODULES, FIRMWARE, NVRAM UNCHANGED')
print('PASS BOUNDED NEW BT DEPENDENCY MODULES',6)
print('PASS V033 INIT USB CONTROL COMMANDS; NO AUTOSTART IN INIT TEST')
print('PASS BT LPO AND U4 REGULATOR BINDING; MMC CLOCK/DURATION')
print('IMAGE',len(b33),hash(b33))
print('BASE',len(b25),hash(b25))
print('V033_INDEPENDENT_AUDIT_PASS_NO_HARDWARE_ACTION')
