#!/usr/bin/env python3
from pathlib import Path
import re,subprocess
b=Path('/home/xoomdev/xoom-linux-rom')
src=(b/'linux-src/net/wireless/certs/wens.hex').read_text()
raw=bytes(int(x,16) for x in re.findall(r'0x([a-fA-F0-9]{2})',src))
assert raw.startswith(b'\x30\x82') and 500<len(raw)<2000
path=b/'firmware-reference-v07/regdb-kernel-wens.der'
path.write_bytes(raw)
pem=path.with_suffix('.pem')
subprocess.run(['openssl','x509','-inform','DER','-in',str(path),'-out',str(pem)],check=True)
subprocess.run(['openssl','x509','-in',str(pem),'-noout','-subject','-fingerprint','-sha256'],check=True)
reg=path.parent/'regulatory.db'
sig=path.parent/'regulatory.db.p7s'
result=subprocess.run(['openssl','cms','-verify','-binary','-inform','DER','-in',str(sig),'-content',str(reg),'-certfile',str(pem),'-nointern','-noverify','-out','/dev/null'],capture_output=True,text=True)
print('CMS_EXIT',result.returncode,'STDERR',result.stderr.strip())
if result.returncode:raise SystemExit('Signed regulatory database failed kernel-key signature verification')
print('REGULATORY.DB SIGNATURE VERIFIED WITH THE EXACT WENS CERTIFICATE BUILT INTO THE KERNEL')
