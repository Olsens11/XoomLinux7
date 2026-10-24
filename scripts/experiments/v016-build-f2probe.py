#!/usr/bin/env python3
"""Build a trace-only BCM4329 Function-2 probe as a hot-uploadable module.
Restore the actual kernel source exactly, including on failed builds.
No bootloader commands and no device writes.
"""
from pathlib import Path
from hashlib import sha256
import difflib, subprocess, shutil, sys
repo=Path(__file__).resolve().parents[2]
B=Path('/home/xoomdev/xoom-linux-rom')
kernel=B/'linux-src'
out=B/'build-wingray-gcc14-initramfs'
relative='drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c'
source=kernel/relative
stage=B/'phase1-v16'
stage.mkdir(exist_ok=True)
baseline=source.read_bytes()
assert b'\0' not in baseline
original=baseline.decode('utf8')
needle='\terr = sdio_enable_func(sdiod->func2);\n\n\tbrcmf_dbg(INFO, "enable F2: err=%d\\n", err);'
assert original.count(needle)==1,'Expected one F2 enable handoff'
pre='''\t/* XOOM V016: read-only SDIO CCCR/clock snapshot before the F2-ready wait. */
\t{
\t\tint exerr = 0, rdyerr = 0, clkerr = 0;
\t\tu8 ex = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IOEx, &exerr);
\t\tu8 ready = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IORx, &rdyerr);
\t\tu8 clk = brcmf_sdiod_readb(sdiod, SBSDIO_FUNC1_CHIPCLKCSR,
\t\t\t\t\t   &clkerr);
\t\tpr_info("XOOM_F2V016 before ioex=%02x/%d iorx=%02x/%d clkcsr=%02x/%d clkstate=%d\\n",
\t\t\tex, exerr, ready, rdyerr, clk, clkerr, bus->clkstate);
\t}
'''
post='''\t/* XOOM V016: same registers immediately after sdio_enable_func returns. */
\t{
\t\tint exerr = 0, rdyerr = 0, clkerr = 0;
\t\tu8 ex = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IOEx, &exerr);
\t\tu8 ready = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IORx, &rdyerr);
\t\tu8 clk = brcmf_sdiod_readb(sdiod, SBSDIO_FUNC1_CHIPCLKCSR,
\t\t\t\t\t   &clkerr);
\t\tpr_info("XOOM_F2V016 after ioex=%02x/%d iorx=%02x/%d clkcsr=%02x/%d result=%d\\n",
\t\t\tex, exerr, ready, rdyerr, clk, clkerr, err);
\t}
'''
new=original.replace(needle,pre+'\terr = sdio_enable_func(sdiod->func2);\n'+post+'\n\tbrcmf_dbg(INFO, "enable F2: err=%d\\n", err);')
bpath=stage/'sdio-original.c'
bpath.write_bytes(baseline)
cpath=stage/'sdio-with-readback.c'
cpath.write_text(new,encoding='utf8')
patch_lines=difflib.unified_diff(original.splitlines(keepends=True),
                                 new.splitlines(keepends=True),
                                 fromfile='a/'+relative,tofile='b/'+relative)
patch=repo/'patches/experiments/v016-brcmfmac-f2-cccr-readback.patch'
patch.parent.mkdir(parents=True,exist_ok=True)
patch.write_text(''.join(patch_lines),encoding='utf8')
print('ORIGINAL_SDIO_SHA256',sha256(baseline).hexdigest())
print('PATCH_BYTES',patch.stat().st_size)
toolchain=B/'toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin'
env=dict(__import__('os').environ,ARCH='arm',
         CROSS_COMPILE=str(toolchain/'arm-none-linux-gnueabihf-'))
module_relative='drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko'
result=1
try:
 source.write_text(new,encoding='utf8')
 with (stage/'build.log').open('wb') as log:
  proc=subprocess.run(['make','-j2','O='+str(out),'drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko',module_relative],cwd=kernel,env=env,
                      stdout=log,stderr=subprocess.STDOUT)
 result=proc.returncode
finally:
 source.write_bytes(baseline)
 assert source.read_bytes()==baseline,'SOURCE RESTORE FAILURE'
 print('ORIGINAL_SOURCE_RESTORED_SHA256',sha256(source.read_bytes()).hexdigest())
if result:
 print((stage/'build.log').read_text(errors='replace')[-9000:])
 raise RuntimeError('v016 module build failed: '+str(result))
built=out/module_relative
target=stage/'brcmfmac-v016-f2probe.ko'
shutil.copy2(built,target)
assert target.read_bytes()[:4]==b'\x7fELF'
print('BUILT_MODULE_BYTES',target.stat().st_size)
print('BUILT_MODULE_SHA256',sha256(target.read_bytes()).hexdigest())
print('COMPLETE_WITHOUT_PARTITION_WRITE')
