#!/usr/bin/env python3
"""Temporarily instrument ONLY normal brcmfmac SDIO F2 enable, then restore source."""
from pathlib import Path
import hashlib,os,subprocess,difflib
B=Path('/home/xoomdev/xoom-linux-rom')
S=B/'linux-src'
P=S/'drivers/mmc/core/sdio_io.c'
OTHER=S/'drivers/mmc/core/sdio.c'
V=B/'phase1-v12'
OUT=B/'build-wingray-gcc14-initramfs'
base=P.read_bytes()
orig=base.decode()
assert hashlib.sha256(base).hexdigest()=='95eeac8c70fd825aff913a316077acbb3514b9a35603ca693c0c5f510bd18198'
assert 'xoom-f2:' not in orig
assert orig.count('#include <linux/kernel.h>')==1
new=orig.replace('#include <linux/kernel.h>','#include <linux/kernel.h>\n#include <linux/of.h>',1)
first=new.index('int sdio_enable_func(struct sdio_func *func)\n{')
after=new.index('EXPORT_SYMBOL_GPL(sdio_enable_func);',first)
body=r"""int sdio_enable_func(struct sdio_func *func)
{
	int ret;
	unsigned char reg;
	unsigned char orig_ioex = 0, requested_ioex = 0, last_iorx = 0;
	unsigned char final_ioex = 0;
	unsigned long start, timeout;
	unsigned int polls = 0;
	int ioex_ret = 0;
	bool trace;

	if (!func)
		return -EINVAL;

	trace = func->num == 2 &&
		func->vendor == 0x02d0 && func->device == 0x4329 &&
		of_machine_is_compatible("motorola,stingray");
	start = jiffies;

	if (trace)
		pr_info("xoom-f2: start timeout_ms=%u hostclk=%u sdio_vsn=%u hs=%u\n",
			func->enable_timeout, func->card->host->ios.clock,
			func->card->cccr.sdio_vsn, func->card->cccr.high_speed);

	ret = mmc_io_rw_direct(func->card, 0, 0, SDIO_CCCR_IOEx, 0, &reg);
	if (ret)
		goto err;
	orig_ioex = reg;
	reg |= 1 << func->num;
	requested_ioex = reg;

	ret = mmc_io_rw_direct(func->card, 1, 0, SDIO_CCCR_IOEx, reg, NULL);
	if (ret)
		goto err;
	if (trace)
		pr_info("xoom-f2: IOEx before=0x%02x requested=0x%02x, write succeeded\n",
			orig_ioex, requested_ioex);

	timeout = jiffies + msecs_to_jiffies(func->enable_timeout);
	while (1) {
		ret = mmc_io_rw_direct(func->card, 0, 0, SDIO_CCCR_IORx, 0, &reg);
		if (ret)
			goto err;
		polls++;
		last_iorx = reg;
		if (reg & (1 << func->num))
			break;
		ret = -ETIME;
		if (time_after(jiffies, timeout))
			goto err;
	}
	if (trace)
		pr_info("xoom-f2: READY polls=%u iorx=0x%02x elapsed_ms=%u\n",
			polls, last_iorx, jiffies_to_msecs(jiffies - start));
	return 0;

err:
	if (trace) {
		/* ONE extra READ ONLY CCCR query, only after normal driver error. */
		ioex_ret = mmc_io_rw_direct(func->card, 0, 0, SDIO_CCCR_IOEx, 0,
					    &final_ioex);
		pr_warn("xoom-f2: FAILED ret=%d polls=%u last_iorx=0x%02x ioex_before=0x%02x requested=0x%02x ioex_after=0x%02x ioex_read_rc=%d elapsed_ms=%u\n",
			ret, polls, last_iorx, orig_ioex, requested_ioex,
			final_ioex, ioex_ret, jiffies_to_msecs(jiffies - start));
	}
	return ret;
}
"""
new=new[:first]+body+'\n'+new[after:]
assert new.count('xoom-f2:')==4
assert body.count('mmc_io_rw_direct(func->card, 1, 0, SDIO_CCCR_IOEx, reg, NULL)')==1
V.mkdir(exist_ok=True)
(V/'sdio_io-original.sha256').write_text(hashlib.sha256(base).hexdigest()+'\n')
(V/'sdio_io-f2-trace.patch').write_text(''.join(difflib.unified_diff(orig.splitlines(True),new.splitlines(True),fromfile='a/drivers/mmc/core/sdio_io.c',tofile='b/drivers/mmc/core/sdio_io.c')))
assert 'xoom-tegra20-bcm4329-highspeed-quirk' not in OTHER.read_text()
print('V12 TRACE: only within SDIO enable of BCM4329 F2, no MAC or new writes.')
print('V12 source patch sha256:',hashlib.sha256(new.encode()).hexdigest())
env=os.environ.copy()
env['ARCH']='arm'
env['CROSS_COMPILE']=str(B/'toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-')
log=B/'build-stingray-v12.log'
try:
	P.write_text(new)
	# The previous v11 build used a temporary quirk; force core sdio.c rebuild
	# against unchanged upstream source to remove it from v12 object code.
	os.utime(OTHER,None)
	config=OUT/'.config'
	subprocess.run([str(S/'scripts/config'),'--file',str(config),
			'--set-str','INITRAMFS_SOURCE',str(V/'phase1-initramfs.cpio.gz'),
			'--enable','RESET_GPIO','--enable','BRCMDBG'],check=True,env=env)
	subprocess.run(['make',f'O={OUT}','olddefconfig'],check=True,cwd=S,env=env,stdout=subprocess.DEVNULL)
	cfg=config.read_text()
	for needed in ['CONFIG_RESET_GPIO=y','CONFIG_BRCMDBG=y','CONFIG_BRCMFMAC=y','CONFIG_BRCMFMAC_SDIO=y',
			   'CONFIG_USB_G_SERIAL=y','# CONFIG_NEON is not set','regulatory.db.p7s']:
		assert needed in cfg,needed
	with log.open('w') as f:
		p=subprocess.run(['make','-j2',f'O={OUT}','nvidia/tegra20-motorola-stingray-usbdiag.dtb','zImage'],cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT)
	if p.returncode:
		print('\n'.join(log.read_text().splitlines()[-80:]))
		raise RuntimeError('kernel build failed '+str(p.returncode))
	assert (OUT/'usr/initramfs_inc_data').read_bytes()==(V/'phase1-initramfs.cpio.gz').read_bytes()
	print('V12 zImage sha256',hashlib.sha256((OUT/'arch/arm/boot/zImage').read_bytes()).hexdigest())
	print('V12 built F2 trace from restored upstream MMC core; v11 highspeed quirk not used')
	subprocess.run(['bash','/mnt/c/Users/olsen/XoomLinux/Phase1/package-stingray-v12-f2-trace.sh'],check=True)
finally:
	P.write_bytes(base)
	assert hashlib.sha256(P.read_bytes()).digest()==hashlib.sha256(base).digest()
	print('Original upstream SDIO I/O source RESTORED sha256:',hashlib.sha256(base).hexdigest())
