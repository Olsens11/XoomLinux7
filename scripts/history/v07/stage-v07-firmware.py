#!/usr/bin/env python3
"""Stage MAC-free/regulatory-neutral reference firmware in private build tree."""
from pathlib import Path
import hashlib
b=Path('/home/xoomdev/xoom-linux-rom')
source=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/brcmfmac4329-sdio.xoom-board-no-mac.txt')
firmware=b/'firmware-reference-v07/brcmfmac4329-sdio.bin'
out=b/'firmware-reference-v07/brcm'
out.mkdir(parents=True,exist_ok=True)
raw=source.read_bytes()
assert len(raw)==1568 and hashlib.sha256(raw).hexdigest()=='c51cf2733ddaeab4c83f0cd11661c76c4709c79bc920b0459e90e5e47aac7305'
txt=raw.decode('ascii')
lines=txt.splitlines(keepends=True)
# Previous recovery file carries ccode=XY regrev=4; not a portable radio policy.
drop=('macaddr=','ccode=','regrev=')
filtered=''.join(l for l in lines if not l.lstrip().startswith(drop))
assert 'macaddr=' not in filtered and 'ccode=' not in filtered and 'regrev=' not in filtered
assert 'boardtype=' in filtered and 'boardrev=' in filtered and 'vendid=' in filtered
assert len(filtered)>1400
nv=out/'brcmfmac4329-sdio.txt'
nv.write_text(filtered)
assert firmware.stat().st_size==253748 and hashlib.sha256(firmware.read_bytes()).hexdigest()=='d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93'
fw=out/'brcmfmac4329-sdio.bin'
fw.write_bytes(firmware.read_bytes())
print('STAGED GENERIC BCM4329 FIRMWARE',fw.stat().st_size,hashlib.sha256(fw.read_bytes()).hexdigest())
print('STAGED MAC/COUNTRY-OVERRIDE FREE BOARD REFERENCE',nv.stat().st_size,hashlib.sha256(nv.read_bytes()).hexdigest())
print('NO MACADDR/CCODE/REGREV IN STAGED NVRAM, NO DEVICE CHANGES')
