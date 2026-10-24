#!/usr/bin/env python3
"""v033 Android boot candidate: v025 zImage frozen; BT DT edits + ramdisk only.
Build-only; never flashes, resets, or talks to an actual Xoom.
"""
from pathlib import Path
import hashlib,struct,gzip,io,subprocess,json
B=Path('/home/xoomdev/xoom-linux-rom')
V=B/'phase1-v033'
BASE=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v025-HOST-PRE-RESET-100MS')
P=BASE/'MZ600-stingray-diagnostic-v025-HOST-PRE-RESET-100MS-TEMPBOOT-ONLY.img'
DEST=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v033-BT-USB-LAB')
DEST.mkdir(parents=True,exist_ok=True)
HASH=lambda b:hashlib.sha256(b).hexdigest()
old=P.read_bytes()
assert HASH(old)=='142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb'
assert old[:8]==b'ANDROID!'
orig_header=struct.unpack_from('<10I',old,8)
kl,ka,rl,ra,ss,sa,ta,page,ds,unused=orig_header
assert (ka,ra,ss,sa,ta,page,ds)==(0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
align=lambda n:(n+page-1)//page*page
orig_k=old[page:page+kl]
orig_ram=old[page+align(kl):page+align(kl)+rl]
assert len(orig_k)==kl and len(orig_ram)==rl
assert set(old[page+kl:page+align(kl)]) <= {0}
assert set(old[page+align(kl)+rl:]) <= {0}
orig_dtb=(BASE/'tegra20-motorola-stingray-usbdiag.dtb').read_bytes()
assert orig_k.endswith(orig_dtb)
kernelfrozen=orig_k[:-len(orig_dtb)]
outdtb=DEST/'tegra20-motorola-stingray-usbdiag.dtb'
outdtb.write_bytes(orig_dtb)
node='/serial@70006200/bluetooth'
mmc='/mmc@c8000200'
def get(node,key,fmt='x',dtb=outdtb):
 r=subprocess.run(['fdtget','-t',fmt,str(dtb),node,key],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(f'missing {key} from {node}: {r.stderr}')
 return r.stdout.strip()
assert int(get(mmc,'max-frequency'),16)==25000000
assert int(get(mmc,'post-power-on-delay-ms'),16)==100
assert int(get('/wifi-pwrseq','post-power-on-delay-ms'),16)==300
assert get(node,'clock-names','s')=='txco'
assert get(node,'compatible','s')=='brcm,bcm4329-bt'
def put(key,values,fmt='s'):
 subprocess.run(['fdtput','-t',fmt,str(outdtb),node,key,*values],check=True)
put('compatible',['motorola,stingray-bcm4329-bt','brcm,bcm4329-bt'])
put('clock-names',['lpo'])
put('shared-supply',[get(mmc,'vmmc-supply')],'x')
put('motorola,shared-u4-power',[],'x')
put('status',['okay'])
assert get(node,'status','s')=='okay'
assert get(node,'compatible','s').split()==['motorola,stingray-bcm4329-bt','brcm,bcm4329-bt']
assert get(node,'clock-names','s')=='lpo'
assert get(node,'shared-supply')==get(mmc,'vmmc-supply')
assert get(node,'clocks')==get('/wifi-pwrseq','clocks')
assert get(mmc,'max-frequency')==format(25000000,'x')
assert get(mmc,'post-power-on-delay-ms')=='64'
# Assert ONLY listed DT semantic properties changed, normalized by dtc decompile.
def decomp(blob,name):
 p=V/name;p.write_bytes(blob)
 r=subprocess.run(['dtc','-I','dtb','-O','dts','-o','-',str(p)],capture_output=True,text=True,check=True)
 return r.stdout
old_dec=decomp(orig_dtb,'old-dt.dtb'); newdtb=outdtb.read_bytes()
new_dec=decomp(newdtb,'new-dt.dtb')
# Keep full semantic diff for human review, no broad string substring approval.
import difflib
diff=''.join(difflib.unified_diff(old_dec.splitlines(True),new_dec.splitlines(True),fromfile='v025',tofile='v033'))
(DEST/'V033_DTB_SEMANTIC_DIFF.txt').write_text(diff)
assert 'max-frequency' not in diff and 'post-power-on-delay-ms' not in diff
assert 'regulator-wifi' not in diff and 'mmc@c8000200' not in diff
assert len(diff)<2600,diff
assert 'motorola,shared-u4-power' in diff and 'clock-names = "lpo"' in diff
print('DT_SEMANTIC_DIFF\n'+diff)

# Extract original newc into item tuples (name, fields, content).
raw=gzip.decompress(orig_ram)
pos=0;original=[]
while True:
 assert raw[pos:pos+6]==b'070701'
 f=[int(raw[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
 ns=pos+110
 nam=raw[ns:ns+f[11]]
 assert len(nam)==f[11] and nam.endswith(b'\0')
 name=nam[:-1].decode()
 start=(ns+f[11]+3)//4*4
 content=raw[start:start+f[6]]
 pos=(start+f[6]+3)//4*4
 if name=='TRAILER!!!':break
 original.append((name,f,content))
oldnames=[n for n,_,_ in original]
assert set(oldnames)==set(['dev','proc','sys','run','tmp','wifi','lib','lib/firmware','lib/firmware/brcm','dev/console','dev/null','init','wifi/brcmutil.ko','wifi/brcmfmac.ko','lib/firmware/brcm/brcmfmac4329-sdio.bin','lib/firmware/brcm/brcmfmac4329-sdio.txt'])
newinit=(V/'init').read_bytes()
assert newinit[:4]==b'\x7fELF' and b'BT START PASS' in newinit
updated=[]
for name,fields,content in original:
 if name=='init':
  fields=fields.copy(); fields[6]=len(newinit);content=newinit
 updated.append((name,fields,content))
# rootfs six dependency modules: no automatic module loads before USB BT_START.
for name in ('ecc','ecdh_generic','cmac','bluetooth','btbcm','hci_uart'):
 content=(V/(name+'.ko')).read_bytes()
 assert content[:4]==b'\x7fELF'
 newfields=[len(updated)+1,0o100644,0,0,1,0,len(content),0,0,0,0,len('bt/'+name+'.ko')+1,0]
 updated.append(('bt/'+name+'.ko',newfields,content))
# Insert directory ahead of its files to satisfy unpack ordering.
dfields=[50,0o040755,0,0,2,0,0,0,0,0,0,len('bt')+1,0]
updated.insert(len(original),('bt',dfields,b''))
def pad(out):
 out.write(b'\0'*(-out.tell()%4))
def entry(out,name,fields,content):
 fields=list(fields)
 fields[6]=len(content)
 fields[11]=len(name.encode())+1
 out.write(b'070701'+b''.join(f'{x:08X}'.encode() for x in fields))
 out.write(name.encode()+b'\0')
 pad(out)
 out.write(content)
 pad(out)
out=io.BytesIO()
for name,fields,content in updated:entry(out,name,fields,content)
entry(out,'TRAILER!!!',[len(updated)+1,0,0,0,1,0,0,0,0,0,0,11,0],b'')
with (V/'phase1-v033-initramfs.cpio.gz').open('wb') as f:
 with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=9) as z:z.write(out.getvalue())
ram=(V/'phase1-v033-initramfs.cpio.gz').read_bytes()
assert gzip.decompress(ram)==out.getvalue()
assert HASH(gzip.decompress(orig_ram))!=HASH(out.getvalue())
assert len(ram)<1700000
new_kernel=kernelfrozen+newdtb
h=bytearray(old[:page])
struct.pack_into('<I',h,8,len(new_kernel))
struct.pack_into('<I',h,16,len(ram))
import hashlib
digest=hashlib.sha1()
for data in (new_kernel,ram,b'',b''):
 digest.update(data);digest.update(struct.pack('<I',len(data)))
h[576:596]=digest.digest()
boot=bytes(h)+new_kernel+b'\0'*(align(len(new_kernel))-len(new_kernel))+ram+b'\0'*(align(len(ram))-len(ram))
assert len(boot)<8*1024*1024,len(boot)
assert boot[:8]==b'ANDROID!'
assert boot[64:576]==old[64:576]
assert boot[page:page+len(new_kernel)]==new_kernel
assert boot[page+align(len(new_kernel)):page+align(len(new_kernel))+len(ram)]==ram
assert kernelfrozen==orig_k[:-len(orig_dtb)]
assert hashlib.sha1(b''.join([b''])).digest()!=digest.digest() # sanity
outimg=DEST/'MZ600-v033-BLUETOOTH-USB-TEMPBOOT-ONLY.img'
outimg.write_bytes(boot)
manifest={
 'classification':'TEMPORARY fastboot boot only, NEVER FLASH',
 'v025_baseline_sha256':HASH(old),'v033_image_sha256':HASH(boot),
 'v033_image_bytes':len(boot),'kernel_binary_except_dtb_unchanged':True,
 'old_dtb_sha256':HASH(orig_dtb),'new_dtb_sha256':HASH(newdtb),
 'rootfs_unchanged_existing_files_except_init':True,'wifi_module_and_firmware_bytes_unchanged':True,
 'new_modules':{n:HASH((V/(n+'.ko')).read_bytes()) for n in ('ecc','ecdh_generic','cmac','bluetooth','btbcm','hci_uart')},
 'v033_init_sha256':HASH(newinit),'ramdisk_sha256':HASH(ram),
 'usb_bt_controls':['BT_STATUS','BT_START','BT_ON','BT_OFF','BT_STOP'],
 'boot_default':'BT modules present in RAM only; not loaded automatically',
 'mmc2_max_frequency_hz':25000000,
 'mmc2_host_pre_reset_delay_ms':100,
 'pwrseq_post_reset_delay_ms':300,
 'dt_delta':'Bluetooth child compatible, clock-names, shared-supply, opt-in, status only',
 }
(DEST/'V033_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('V033_IMAGE',outimg,'SIZE',len(boot),'SHA256',HASH(boot))
print('V033_RAMDISK',len(ram),'SHA256',HASH(ram))
print('V033_KERNEL_BINARY_UNCHANGED',len(kernelfrozen))
print('V033_ROOTFS_KEEP_ORIGINAL',len(original),'NEW_BT',6)
print('V033_OFFLINE_BUILD_PASS_NO_DEVICE_WRITES')
