#!/usr/bin/env python3
"""v032 validate proposed Bluetooth low-power-oscillator binding (offline only)."""
from pathlib import Path
import subprocess,hashlib,sys,re
repo=Path(__file__).resolve().parents[2]
k=Path('/home/xoomdev/xoom-linux-rom/linux-src')
private=Path('/home/xoomdev/xoom-linux-rom/phase1-v032-bt-lpo')
private.mkdir(parents=True,exist_ok=True)
dts=repo/'src/board/tegra20-motorola-stingray-usbdiag.dts'
overlay=repo/'src/chip/tegra20-stingray-bcm4329-bt-lpo-v032.dtsi'
source=private/'proposed-lpo.dts'
source.write_text(dts.read_text()+"\n#include \""+overlay.name+"\"\n")
pre=private/'proposed-lpo.pre.dts'
dtb=private/'proposed-lpo.dtb'
subprocess.run(['gcc','-E','-P','-x','assembler-with-cpp','-nostdinc','-undef',
                '-D__DTS__','-I',str(k/'include'),'-I',str(k/'arch/arm/boot/dts'),
                '-I',str(k/'arch/arm/boot/dts/nvidia'),'-I',str(overlay.parent),
                str(source),'-o',str(pre)],check=True)
subprocess.run(['dtc','-q','-I','dts','-O','dtb','-o',str(dtb),str(pre)],check=True)
def get(node,property,fmt='s'):
 r=subprocess.run(['fdtget','-t',fmt,str(dtb),node,property],capture_output=True,text=True)
 assert r.returncode==0,(node,property,r.stderr)
 return r.stdout.strip()
def passes(label,condition):
 print('PASS' if condition else 'FAIL',label)
 if not condition:raise AssertionError(label)
bt='/serial@70006200/bluetooth'
wifi='/wifi-pwrseq'
mmc='/mmc@c8000200'
passes('BT_DISABLED',get(bt,'status')=='disabled')
passes('CLOCK_IS_LPO_NOT_TXCO',get(bt,'clock-names')=='lpo')
passes('CLOCK_REFERENCE_SHARED_WITH_WLAN',
       get(bt,'clocks','x')==get(wifi,'clocks','x'))
passes('SAME_SHARED_U4_AS_MMC',
       get(bt,'shared-supply','x')==get(mmc,'vmmc-supply','x'))
passes('BT_EXTRA_REGULATOR_OPT_IN',
       'motorola,shared-u4-power' in subprocess.run(
          ['fdtget','-p',str(dtb),bt],capture_output=True,text=True,check=True).stdout.splitlines())
passes('BT_SUPPLY_VBAT_UNCHANGED',
       'vbat-supply' not in overlay.read_text() and
       bool(re.search(r'vbat-supply\s*=\s*<&vdd_3v3_sys>',dts.read_text())))
passes('BT_SUPPLY_VDDIO_UNCHANGED',
       'vddio-supply' not in overlay.read_text() and
       bool(re.search(r'vddio-supply\s*=\s*<&vwlan1>',dts.read_text())))
passes('BT_GPIO_I7_PRESENT',bool(get(bt,'shutdown-gpios','x')))
passes('BT_RESET_U0_PRESENT',bool(get(bt,'reset-gpios','x')))
passes('MMC_UNQUALIFIED_SOURCE_UNTOUCHED',get(mmc,'max-frequency','x')==format(46153846,'x'))
hci=(k/'drivers/bluetooth/hci_bcm.c').read_text()
passes('HCI_BCM_SUPPORTS_LPO', 'devm_clk_get_optional(dev->dev, "lpo")' in hci)
passes('HCI_BCM_SEPARATES_TXCO', 'bcm_get_txco(dev->dev)' in hci)
print('V032_DISABLED_LPO_DTB_SHA256',hashlib.sha256(dtb.read_bytes()).hexdigest())
print('V032_SOURCE_ONLY_NOT_BOOTED')
