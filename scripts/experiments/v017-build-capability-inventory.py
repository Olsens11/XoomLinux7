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
stage=B/'phase1-v17'
stage.mkdir(exist_ok=True)
baseline=source.read_bytes()
assert b'\0' not in baseline
original=baseline.decode('utf8')
needle='\terr = sdio_enable_func(sdiod->func2);\n\n\tbrcmf_dbg(INFO, "enable F2: err=%d\\n", err);'
assert original.count(needle)==1,'Expected one F2 enable handoff'
pre='''\t/* XOOM V017: read-only SDIO CCCR/clock snapshot before the F2-ready wait. */
\t{
\t\tint exerr = 0, rdyerr = 0, clkerr = 0;
\t\tu8 ex = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IOEx, &exerr);
\t\tu8 ready = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IORx, &rdyerr);
\t\tu8 clk = brcmf_sdiod_readb(sdiod, SBSDIO_FUNC1_CHIPCLKCSR,
\t\t\t\t\t   &clkerr);
\t\tpr_info("XOOM_F2V017 before ioex=%02x/%d iorx=%02x/%d clkcsr=%02x/%d clkstate=%d\\n",
\t\t\tex, exerr, ready, rdyerr, clk, clkerr, bus->clkstate);
\t}
'''
post='''\t/* XOOM V017: same registers immediately after sdio_enable_func returns. */
\t{
\t\tint exerr = 0, rdyerr = 0, clkerr = 0;
\t\tu8 ex = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IOEx, &exerr);
\t\tu8 ready = sdio_f0_readb(sdiod->func1, SDIO_CCCR_IORx, &rdyerr);
\t\tu8 clk = brcmf_sdiod_readb(sdiod, SBSDIO_FUNC1_CHIPCLKCSR,
\t\t\t\t\t   &clkerr);
\t\tpr_info("XOOM_F2V017 after ioex=%02x/%d iorx=%02x/%d clkcsr=%02x/%d result=%d\\n",
\t\t\tex, exerr, ready, rdyerr, clk, clkerr, err);
\t}
'''
new=original.replace(needle,pre+'\terr = sdio_enable_func(sdiod->func2);\n'+post+'\n\tbrcmf_dbg(INFO, "enable F2: err=%d\\n", err);')

    # Additional read-only inventory before Function 2 enable.
    # CARD fields can differ from raw register bytes due to capability parsing.
caps=r"""
    {
        struct mmc_card *xc = sdiod->func1->card;
        struct mmc_host *xh = xc->host;
        int errev=0, ercaps=0, erpow=0, erspeed=0;
        u8 rawrev=sdio_f0_readb(sdiod->func1,SDIO_CCCR_CCCR,&errev);
        u8 rawcaps=sdio_f0_readb(sdiod->func1,SDIO_CCCR_CAPS,&ercaps);
        u8 rawpow=sdio_f0_readb(sdiod->func1,SDIO_CCCR_POWER,&erpow);
        u8 rawspeed=sdio_f0_readb(sdiod->func1,SDIO_CCCR_SPEED,&erspeed);
        pr_info("XOOM_F2V017 RAW cccr=%02x/%d caps=%02x/%d power=%02x/%d speed=%02x/%d\n",
                rawrev,errev,rawcaps,ercaps,rawpow,erpow,rawspeed,erspeed);
        pr_info("XOOM_F2V017 CARD sdio_vsn=%u multi=%u low=%u wide=%u highpower=%u highspeed=%u\n",
                xc->cccr.sdio_vsn,xc->cccr.multi_block,xc->cccr.low_speed,
                xc->cccr.wide_bus,xc->cccr.high_power,xc->cccr.high_speed);
        pr_info("XOOM_F2V017 HOST clock=%u timing=%u buswidth=%u signalvoltage=%u vdd=%u\n",
                xh->ios.clock,xh->ios.timing,xh->ios.bus_width,
                xh->ios.signal_voltage,xh->ios.vdd);
    }
    """
new=new.replace('/* XOOM V017: read-only SDIO CCCR/clock snapshot',
                    caps+'/* XOOM V017: read-only SDIO CCCR/clock snapshot',1)
new=new.replace('#include <linux/mmc/core.h>',
                    '#include <linux/mmc/host.h>\n#include <linux/mmc/core.h>',1)

bpath=stage/'sdio-original.c'
bpath.write_bytes(baseline)
cpath=stage/'sdio-with-readback.c'
cpath.write_text(new,encoding='utf8')
patch_lines=difflib.unified_diff(original.splitlines(keepends=True),
                                 new.splitlines(keepends=True),
                                 fromfile='a/'+relative,tofile='b/'+relative)
patch=repo/'patches/experiments/v017-brcmfmac-f2-cccr-readback.patch'
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
 raise RuntimeError('v017 module build failed: '+str(result))
built=out/module_relative
target=stage/'brcmfmac-v017-f2probe.ko'
shutil.copy2(built,target)
assert target.read_bytes()[:4]==b'\x7fELF'
print('BUILT_MODULE_BYTES',target.stat().st_size)
print('BUILT_MODULE_SHA256',sha256(target.read_bytes()).hexdigest())
print('COMPLETE_WITHOUT_PARTITION_WRITE')
