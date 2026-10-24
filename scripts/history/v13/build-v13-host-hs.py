#!/usr/bin/env python3
"""Temporarily instrument ONLY normal brcmfmac SDIO F2 enable, then restore source."""
from pathlib import Path
import hashlib,os,subprocess,difflib
B=Path('/home/xoomdev/xoom-linux-rom')
S=B/'linux-src'
P=S/'drivers/mmc/core/sdio_io.c'
OTHER=S/'drivers/mmc/core/sdio.c'
V=B/'phase1-v13'
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
HOST=S/'drivers/mmc/host/sdhci-tegra.c'
host_orig=HOST.read_bytes()
host_s=host_orig.decode()
assert host_s.count('static int sdhci_tegra_probe(struct platform_device *pdev)')==1
assert host_s.count('\trc = mmc_of_parse(host->mmc);')==1
assert 'static void sdhci_tegra_init_bcm4329_card(' not in host_s
# Based on previously proposed Linux upstream Tegra SDHCI init_card workaround,
# restricted to the Xoom root compatible and its brcm,bcm4329-fmac DT child.
callback=r'''static void sdhci_tegra_init_bcm4329_card(struct mmc_host *mmc,
                                            struct mmc_card *card)
{
    struct device_node *np;

    if (card->type != MMC_TYPE_SDIO ||
        !of_machine_is_compatible("motorola,stingray"))
        return;

    np = of_get_compatible_child(mmc_dev(mmc)->of_node,
                                 "brcm,bcm4329-fmac");
    if (!np)
        return;
    of_node_put(np);

    /* Xoom/Tegra20 BCM4329 explicit SDIO high-speed capability workaround.
     * Set before sdio_read_cccr() / bus timing selection, not after CIS.
     * No user address, persistent change, or generic MMC modification. */
    card->cccr.high_speed = 1;
    pr_info("%s: xoom-host-hs: forced card high_speed in Tegra init_card (early)\n",
            mmc_hostname(mmc));
}

'''
host_new=host_s.replace('static int sdhci_tegra_probe(struct platform_device *pdev)',callback+'static int sdhci_tegra_probe(struct platform_device *pdev)',1)
host_new=host_new.replace('\trc = mmc_of_parse(host->mmc);','\tif (of_machine_is_compatible("motorola,stingray"))\n\t\thost->mmc_host_ops.init_card = sdhci_tegra_init_bcm4329_card;\n\n\trc = mmc_of_parse(host->mmc);',1)
assert host_new.count('xoom-host-hs:')==1
(V/'sdhci-tegra-host-hs-original.sha256').write_text(hashlib.sha256(host_orig).hexdigest()+'\n')
(V/'sdhci-tegra-host-hs.patch').write_text(''.join(difflib.unified_diff(host_s.splitlines(True),host_new.splitlines(True),fromfile='a/drivers/mmc/host/sdhci-tegra.c',tofile='b/drivers/mmc/host/sdhci-tegra.c')))

print('V13 TRACE: only within SDIO enable of BCM4329 F2, no MAC or new writes.')
print('V13 source patch sha256:',hashlib.sha256(new.encode()).hexdigest())
env=os.environ.copy()
env['ARCH']='arm'
env['CROSS_COMPILE']=str(B/'toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-')
log=B/'build-stingray-v13.log'
try:
	P.write_text(new)
	HOST.write_text(host_new)
	# The previous v11 build used a temporary quirk; force core sdio.c rebuild
	# against unchanged upstream source to remove it from v13 object code.
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
	print('V13 zImage sha256',hashlib.sha256((OUT/'arch/arm/boot/zImage').read_bytes()).hexdigest())
	print('V13 built F2 trace from restored upstream MMC core; v11 highspeed quirk not used')
	subprocess.run(['bash','/mnt/c/Users/olsen/XoomLinux/Phase1/package-stingray-v13-host-hs.sh'],check=True)
finally:
	P.write_bytes(base)
	HOST.write_bytes(host_orig)
	assert hashlib.sha256(HOST.read_bytes()).digest()==hashlib.sha256(host_orig).digest()
	print("Original Tegra host source RESTORED VERIFIED")
	assert hashlib.sha256(P.read_bytes()).digest()==hashlib.sha256(base).digest()
	print('Original upstream SDIO I/O source RESTORED sha256:',hashlib.sha256(base).hexdigest())
