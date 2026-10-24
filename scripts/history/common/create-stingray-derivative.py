#!/usr/bin/env python3
"""Add conservative Stingray MZ600 bring-up DT target to pinned xoom-linux 7.0-dev.
Only root model/compatible and build target are modified; hardware nodes are
inherited UNCHANGED from Wingray and still need validation on actual MZ600.
No radio modem is activated or partitioned here.
"""
from pathlib import Path
import hashlib,difflib
base=Path("/home/xoomdev/xoom-linux-rom/linux-src/arch/arm/boot/dts/nvidia")
src=base/"tegra20-motorola-wingray.dts"
dst=base/"tegra20-motorola-stingray.dts"
orig=src.read_text()
old='model = "Motorola Xoom (Wingray)";\n\tcompatible = "motorola,wingray", "motorola,xoom", "nvidia,tegra20";'
new='model = "Motorola Xoom (Stingray MZ600 diagnostic)";\n\tcompatible = "motorola,stingray", "motorola,xoom", "nvidia,tegra20";'
assert orig.count(old)==1
adapted=orig.replace(old,new,1)
preamble='''// EXPERIMENTAL bring-up for Motorola Xoom MZ600 (Stingray)\n// Derived from xoom-linux's unmodified MZ604 Wingray DTS.\n// Same Tegra20 / 1GB / panel baseline; cellular hardware intentionally not\n// enabled. NOT proof of board compatibility. NO permanent data writes.\n'''
adapted=preamble+adapted
if dst.exists():
 assert dst.read_text()==adapted,'Stingray DT file exists with different content'
else:
 dst.write_text(adapted)
make=base/"Makefile"
txt=make.read_text()
needle='\ttegra20-motorola-wingray.dtb \\\n'
replacement='\ttegra20-motorola-wingray.dtb \\\n\ttegra20-motorola-stingray.dtb \\\n'
assert txt.count(needle)==1
if replacement not in txt:make.write_text(txt.replace(needle,replacement,1))
print('FILE',dst,len(adapted),'SHA256',hashlib.sha256(dst.read_bytes()).hexdigest())
print('DIFF:')
print(''.join(difflib.unified_diff(orig.splitlines(keepends=True),adapted.splitlines(keepends=True),fromfile='Wingray-original',tofile='Stingray-experimental'))[:2300])
print('MAKEFILE:',[line for line in make.read_text().splitlines() if 'tegra20-motorola-' in line])
