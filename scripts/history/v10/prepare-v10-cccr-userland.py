from pathlib import Path
b=Path('/home/xoomdev/xoom-linux-rom')
v=b/'phase1-v10'
v.mkdir(exist_ok=True)
s=(b/'phase1-v08/init.c').read_text()
s=s.replace('/* Xoom MZ600 phase-1 v08 read-only SDIO enumeration and boot-log diagnostics. No libc/NEON.',
 '/* Xoom MZ600 phase-1 v10 OEM BCM4329 CCCR revision quirk A/B test. No libc/NEON.')
s=s.replace('XOOM LINUX MZ600 V08 SDIO ENUMERATION AUDIT','XOOM LINUX MZ600 V10 OEM CCCR QUIRK')
s=s.replace('PONG XOOM-LINUX V08','PONG XOOM-LINUX V10')
assert 'PONG XOOM-LINUX V10' in s and 'usb_bootlog' in s
(v/'init.c').write_text(s)
print('V10 OEM CCCR QUIRK USERLAND SOURCE',v/'init.c',len(s))
