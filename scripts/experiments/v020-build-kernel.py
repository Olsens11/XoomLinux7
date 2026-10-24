#!/usr/bin/env python3
from pathlib import Path
import hashlib,os,subprocess,sys
R=Path('/home/xoomdev/projects/XoomLinux7-mmc-on-demand')
B=Path('/home/xoomdev/xoom-linux-rom')
K=B/'linux-src'; O=B/'build-wingray-gcc14-initramfs'; V=B/'phase1-v20'
p=K/'drivers/mmc/core/sdio.c'
orig=p.read_bytes(); oldcfg=(O/'.config').read_bytes()
source_hash=hashlib.sha256(orig).hexdigest()
patch=R/'patches/experiments/v020-on-demand-mmc2-capability-parameter.patch'
cmd=['git','-C',str(K),'apply','--whitespace=nowarn',str(patch)]
env=os.environ.copy()
env['ARCH']='arm'
env['CROSS_COMPILE']=str(B/'toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-')
log=V/'build-v020.log'
try:
  print("SOURCE_BEFORE",source_hash,flush=True)
  print("CONFIG_MMC_BUILTIN",b'CONFIG_MMC=y' in oldcfg,flush=True)
  assert b'CONFIG_MMC=y' in oldcfg
  subprocess.run(cmd,check=True)
  assert b'XOOM_MMC2_V020' in p.read_bytes()
  subprocess.run([str(K/'scripts/config'),'--file',str(O/'.config'),
                  '--set-str','INITRAMFS_SOURCE',str(V/'phase1-initramfs.cpio.gz')],check=True,env=env)
  with log.open('wb') as out:
    x=subprocess.run(['make','O='+str(O),'olddefconfig'],cwd=K,env=env,stdout=out,stderr=subprocess.STDOUT)
    if x.returncode:raise RuntimeError('olddefconfig failed')
    x=subprocess.run(['make','-j2','O='+str(O),'zImage',
                      'nvidia/tegra20-motorola-stingray-usbdiag.dtb'],cwd=K,env=env,stdout=out,stderr=subprocess.STDOUT)
    if x.returncode:raise RuntimeError('kernel compilation failed')
  assert (O/'usr/initramfs_inc_data').read_bytes()==(V/'phase1-initramfs.cpio.gz').read_bytes()
  print("V020_KERNEL_COMPILED_AND_INITRAMFS_EMBEDDED",flush=True)
  subprocess.run(['bash',str(R/'scripts/experiments/v020-package-tempboot.sh')],check=True,env=env)
finally:
  p.write_bytes(orig)
  (O/'.config').write_bytes(oldcfg)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=source_hash:raise RuntimeError('CRITICAL: core source restore failed')
  if (O/'.config').read_bytes()!=oldcfg:raise RuntimeError('CRITICAL: build config restore failed')
  print('ORIGINAL_KERNEL_MMC_SOURCE_RESTORED',source_hash,flush=True)
  print('ORIGINAL_BUILD_CONFIG_RESTORED',flush=True)
path=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/Diagnostic-MZ600-v20-MMC2-ON-DEMAND/MZ600-stingray-diagnostic-v20-MMC2-ON-DEMAND-TEMPBOOT-ONLY.img')
print('CANDIDATE_SIZE',path.stat().st_size,flush=True)
print('CANDIDATE_SHA256',hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
