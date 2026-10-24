#!/usr/bin/env python3
"""v018: exact six-card-capability Motorola override, card/chip/board scoped.
Experimental temporary-boot kernel only. Restores source AND build config.
Uses v015 validated RAM-only diagnostic initramfs unchanged.
"""
from pathlib import Path
import hashlib, difflib, os, shutil, subprocess, sys
repo=Path(__file__).resolve().parents[2]
B=Path('/home/xoomdev/xoom-linux-rom')
K=B/'linux-src'
O=B/'build-wingray-gcc14-initramfs'
V=B/'phase1-v18'
V.mkdir(exist_ok=True)
src=K/'drivers/mmc/core/sdio.c'
orig=src.read_bytes()
orig_sha=hashlib.sha256(orig).hexdigest()
config=O/'.config'
config_original=config.read_bytes()
source=orig.decode('utf-8')
anchor='\tmmc_fixup_device(card, sdio_fixup_methods);\n'
assert source.count(anchor)==1,"mmc fixup phase mismatch"
assert '#include <linux/of.h>' not in source
assert 'XOOM_OEM_CAPS_V018' not in source
hook=r'''
    /*
     * XOOM_OEM_CAPS_V018: diagnostic-only reproduction of the six
     * capabilities supplied by Motorola's embedded_sdio_data.
     * Apply AFTER sdio_read_cccr() and common CIS parsing/fixups,
     * BEFORE high-speed negotiation and host timing selection.
     * Scoped to our Stingray BCM4329. Do NOT copy into unrelated boards.
     */
    if (of_machine_is_compatible("motorola,stingray") &&
        card->cis.vendor == SDIO_VENDOR_ID_BROADCOM &&
        card->cis.device == SDIO_DEVICE_ID_BROADCOM_4329) {
        pr_info("XOOM_OEM_CAPS_V018 before vsn=%u multi=%u low=%u wide=%u hp=%u hs=%u\n",
                card->cccr.sdio_vsn, card->cccr.multi_block,
                card->cccr.low_speed, card->cccr.wide_bus,
                card->cccr.high_power, card->cccr.high_speed);
        card->cccr.sdio_vsn = SDIO_SDIO_REV_1_20;
        card->cccr.multi_block = 1;
        card->cccr.low_speed = 0;
        card->cccr.wide_bus = 0;
        card->cccr.high_power = 1;
        card->cccr.high_speed = 1;
        pr_info("XOOM_OEM_CAPS_V018 after vsn=%u multi=%u low=%u wide=%u hp=%u hs=%u\n",
                card->cccr.sdio_vsn, card->cccr.multi_block,
                card->cccr.low_speed, card->cccr.wide_bus,
                card->cccr.high_power, card->cccr.high_speed);
    }
'''
patched=source.replace('#include <linux/err.h>\n',
                       '#include <linux/err.h>\n#include <linux/of.h>\n',1)
patched=patched.replace(anchor,anchor+hook,1)
assert patched.count('XOOM_OEM_CAPS_V018')==3
patch_path=repo/'patches/experiments/v018-motorola-six-field-sdio-capabilities.patch'
patch_path.parent.mkdir(parents=True,exist_ok=True)
patch_path.write_text(''.join(difflib.unified_diff(source.splitlines(True),patched.splitlines(True),
  fromfile='a/drivers/mmc/core/sdio.c',tofile='b/drivers/mmc/core/sdio.c')))
shutil.copyfile(B/'phase1-v15/phase1-initramfs.cpio.gz',V/'phase1-initramfs.cpio.gz')
shutil.copyfile(B/'phase1-v15/init',V/'init')
shutil.copyfile(B/'phase1-v15/init.c',V/'init.c')
assert (V/'phase1-initramfs.cpio.gz').read_bytes()==(B/'phase1-v15/phase1-initramfs.cpio.gz').read_bytes()
package=(repo/'scripts/build/v15-package.sh').read_text()
package=package.replace('phase1-v15','phase1-v18')
package=package.replace('Diagnostic-MZ600-v15-RAW-USB-LAB','Diagnostic-MZ600-v18-OEM-SDIO-CAPS')
package=package.replace('MZ600-stingray-diagnostic-v15-RAW-USB-LAB-TEMPBOOT-ONLY.img','MZ600-stingray-diagnostic-v18-OEM-SDIO-CAPS-TEMPBOOT-ONLY.img')
package=package.replace('kernel-v15.config','kernel-v18.config').replace('init-v15-source.c','init-v18-source.c')
package=package.replace('V15','V18').replace('v15','v18')
package_path=repo/'scripts/experiments/v018-package-tempboot.sh'
package_path.write_text(package)
package_path.chmod(0o755)
env=os.environ.copy()
env['ARCH']='arm'
env['CROSS_COMPILE']=str(B/'toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-')
log=V/'build-v018.log'
print('BASE_MMC_SDIO_SHA256',orig_sha,flush=True)
print('BASE_V15_INITRAMFS_SHA256',hashlib.sha256((V/'phase1-initramfs.cpio.gz').read_bytes()).hexdigest(),flush=True)
print('PATCH_SHA256',hashlib.sha256(patch_path.read_bytes()).hexdigest(),flush=True)
build_ok=False
try:
  src.write_text(patched,encoding='utf-8')
  cmd=[str(K/'scripts/config'),'--file',str(config),'--set-str','INITRAMFS_SOURCE',str(V/'phase1-initramfs.cpio.gz')]
  subprocess.run(cmd,check=True,env=env)
  with log.open('wb') as f:
    p=subprocess.run(['make','O='+str(O),'olddefconfig'],cwd=K,env=env,stdout=f,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('olddefconfig failed')
    p=subprocess.run(['make','-j2','O='+str(O),'zImage','nvidia/tegra20-motorola-stingray-usbdiag.dtb'],
                     cwd=K,env=env,stdout=f,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('kernel make failed')
  if (O/'usr/initramfs_inc_data').read_bytes() != (V/'phase1-initramfs.cpio.gz').read_bytes():
    raise RuntimeError('wrong embedded initramfs')
  if 'XOOM_OEM_CAPS_V018' not in src.read_text():
    raise RuntimeError('unexpected source state')
  print('KERNEL_BUILD_PASS',flush=True)
  subprocess.run(['bash',str(package_path)],check=True,env=env)
  build_ok=True
finally:
  src.write_bytes(orig)
  config.write_bytes(config_original)
  assert hashlib.sha256(src.read_bytes()).hexdigest()==orig_sha,'CRITICAL MMC source restoration failed'
  assert config.read_bytes()==config_original,'CRITICAL build config restoration failed'
  print('MMC_SOURCE_RESTORED_SHA256',orig_sha,flush=True)
  print('BUILD_CONFIG_RESTORED_BYTES',len(config_original),flush=True)
if not build_ok:
  print(log.read_text(errors='replace')[-9000:])
  raise RuntimeError('v018 not built')
image=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v18-OEM-SDIO-CAPS/MZ600-stingray-diagnostic-v18-OEM-SDIO-CAPS-TEMPBOOT-ONLY.img')
print('V018_IMAGE',image,flush=True)
print('V018_SIZE',image.stat().st_size,flush=True)
print('V018_SHA256',hashlib.sha256(image.read_bytes()).hexdigest(),flush=True)
