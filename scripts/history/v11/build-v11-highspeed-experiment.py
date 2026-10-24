#!/usr/bin/env python3
"""Build experimental Stingray/BCM4329 CCCR v1.2 quirk, then restore shared source exactly."""
from pathlib import Path
import hashlib,os,subprocess,difflib
B=Path('/home/xoomdev/xoom-linux-rom')
P=B/'linux-src/drivers/mmc/core/sdio.c'
V=B/'phase1-v11'
S=B/'linux-src'
OUT=B/'build-wingray-gcc14-initramfs'
FIRM=B/'firmware-reference-v07'
ORIG=P.read_bytes()
src=ORIG.decode('utf-8')
assert src.count('#include <linux/sysfs.h>')==1
assert src.count('err = sdio_read_common_cis(card);\n\tif (err)\n\t\tgoto remove;')==1
assert 'xoom-tegra20-bcm4329-highspeed-quirk' not in src
patch=src.replace('#include <linux/sysfs.h>', '#include <linux/sysfs.h>\n#include <linux/of.h>',1)
find='err = sdio_read_common_cis(card);\n\tif (err)\n\t\tgoto remove;'
insert='''err = sdio_read_common_cis(card);
\tif (err)
\t\tgoto remove;

\t/*
\t * EXPERIMENTAL xoom-tegra20-bcm4329-highspeed-quirk: Motorola Stingray downstream
\t * notes BCM4329 reports SDIO spec 1.1 and forces revision 1.2.
\t * Restrict to this exact DT board and actual Broadcom 4329 ID.
\t * No identity or address is injected; upstream driver unchanged.
\t */
\tif (of_machine_is_compatible("motorola,stingray") &&
\t    card->cis.vendor == SDIO_VENDOR_ID_BROADCOM &&
\t    card->cis.device == SDIO_DEVICE_ID_BROADCOM_4329) {
\t\tpr_info("%s: Xoom BCM4329 Tegra20 high-speed flag %u -> 1\\\\n",
			mmc_hostname(card->host), card->cccr.high_speed);
		card->cccr.high_speed = 1;
\t}'''
# Correct C escaped newline: both Python backslash and C literal must be right.
insert=insert.replace('\\\\n"', '\\n"') if False else insert
patch=patch.replace(find,insert,1)
assert patch!=src and patch.count('xoom-tegra20-bcm4329-highspeed-quirk')==1
V.mkdir(exist_ok=True)
(V/'sdio-original.sha256').write_text(hashlib.sha256(ORIG).hexdigest()+'\n')
(V/'sdio-highspeed-experiment.patch').write_text(''.join(difflib.unified_diff(src.splitlines(True),patch.splitlines(True),fromfile='a/drivers/mmc/core/sdio.c',tofile='b/drivers/mmc/core/sdio.c')))
print('SOURCE ORIGINAL_SHA256',hashlib.sha256(ORIG).hexdigest())
print('V11 PATCH_SHA256',hashlib.sha256(patch.encode()).hexdigest())
conf=OUT/'.config'
print('SOURCE_EDIT_TEMPORARY=YES, MUST_RESTORE_IN_FINALLY')
env=os.environ.copy()
env['ARCH']='arm'
env['CROSS_COMPILE']=str(B/'toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-')
log=B/'build-stingray-v11.log'
try:
 P.write_text(patch)
 subprocess.run([str(S/'scripts/config'),'--file',str(conf),'--set-str','INITRAMFS_SOURCE',str(V/'phase1-initramfs.cpio.gz'),'--enable','RESET_GPIO','--enable','BRCMDBG'],check=True,env=env)
 subprocess.run(['make',f'O={OUT}','olddefconfig'],check=True,cwd=S,env=env,stdout=subprocess.DEVNULL)
 cfg=conf.read_text()
 for check in ('CONFIG_RESET_GPIO=y','CONFIG_BRCMDBG=y','CONFIG_BRCMFMAC=y','CONFIG_BRCMFMAC_SDIO=y','CONFIG_USB_G_SERIAL=y','# CONFIG_NEON is not set', 'regulatory.db.p7s'):
  assert check in cfg,check
 with log.open('w') as f:
  proc=subprocess.run(['make','-j2',f'O={OUT}','nvidia/tegra20-motorola-stingray-usbdiag.dtb','zImage'],cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT)
 if proc.returncode:
  print('BUILD FAILED LAST 50 LINES:\n'+'\n'.join(log.read_text().splitlines()[-50:]))
  raise RuntimeError(f'MAKE FAILED {proc.returncode}')
 assert (OUT/'usr/initramfs_inc_data').read_bytes()==(V/'phase1-initramfs.cpio.gz').read_bytes()
 print('V11_QUIRK_KERNEL_SHA256',hashlib.sha256((OUT/'arch/arm/boot/zImage').read_bytes()).hexdigest())
 print('V11_SOURCE_HAS_QUIRK',P.read_text().count('xoom-tegra20-bcm4329-highspeed-quirk')==1)
 print('V11_BUILD_PASSED_NOW_PACKAGING')
 subprocess.run(['bash','/mnt/c/Users/olsen/XoomLinux/Phase1/package-stingray-v11-highspeed.sh'],check=True)
finally:
 P.write_bytes(ORIG)
 assert hashlib.sha256(P.read_bytes()).digest()==hashlib.sha256(ORIG).digest()
 print('ORIGINAL_SHARED_KERNEL_SOURCE_RESTORED_VERIFIED',hashlib.sha256(P.read_bytes()).hexdigest())
