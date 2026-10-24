#!/usr/bin/env python3
from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v09';v.mkdir(exist_ok=True)
s=(b/'phase1-v08/init.c').read_text()
assert s.count('PONG XOOM-LINUX V08')==1
s=s.replace('PONG XOOM-LINUX V08','PONG XOOM-LINUX V09')
s=s.replace('XOOM LINUX MZ600 V08 BOOT WIFI LOGS','XOOM LINUX MZ600 V09 SIGNED REGDB DIAGNOSTIC')
s=s.replace('phase-1 v08 early SDIO/wifi kernel ring diagnostics','phase-1 v09 official signed regulatory database')
(v/'init.c').write_text(s)
print('V09 SOURCE',len(s),'bytes')
