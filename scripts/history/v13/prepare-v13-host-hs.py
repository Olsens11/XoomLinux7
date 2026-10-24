from pathlib import Path
B=Path('/home/xoomdev/xoom-linux-rom')
v=B/'phase1-v13';v.mkdir(exist_ok=True)
s=(B/'phase1-v12/init.c').read_text()
assert 'PONG XOOM-LINUX V12' in s
s=s.replace('phase-1 v12 upstream SDIO F2 IOEx IORx timeout instrumentation','phase-1 v13 Tegra20 BCM4329 SDIO host init_card upstream workaround+F2 trace')
s=s.replace('V12 SDIO F2 CCCR TRACE','V13 TEGRA HOST INIT QUIRK').replace('PONG XOOM-LINUX V12','PONG XOOM-LINUX V13')
(v/'init.c').write_text(s)
host=Path('/mnt/c/Users/olsen/XoomLinux/Phase1')
a=(host/'build-v12-userland.sh').read_text()
(host/'build-v13-userland.sh').write_text(a.replace('phase1-v12','phase1-v13').replace('V12','V13'))
p=(host/'package-stingray-v12-f2-trace.sh').read_text()
p=p.replace('phase1-v12','phase1-v13').replace('Diagnostic-MZ600-v12-F2-TRACE','Diagnostic-MZ600-v13-HOST-HS').replace('MZ600-stingray-diagnostic-v12-F2-TRACE-TEMPBOOT-ONLY.img','MZ600-stingray-diagnostic-v13-HOST-HS-TEMPBOOT-ONLY.img').replace('init-v12-source.c','init-v13-source.c').replace('kernel-v12.config','kernel-v13.config').replace('V12','V13').replace('v12 upstream SDIO F2 IOEx and IORx timeout tracing (no new writes)','v13 Tegra20 host-specific BCM4329 init_card upstream proposed workaround plus F2 trace')
(host/'package-stingray-v13-host-hs.sh').write_text(p)
q=(host/'build-v12-f2-trace.py').read_text()
q=q.replace('phase1-v12','phase1-v13').replace('V12','V13').replace('v12','v13').replace('build-stingray-v12.log','build-stingray-v13.log').replace('package-stingray-v12-f2-trace.sh','package-stingray-v13-host-hs.sh')
needle="assert 'xoom-tegra20-bcm4329-highspeed-quirk' not in OTHER.read_text()"
assert q.count(needle)==1
insert="""assert 'xoom-tegra20-bcm4329-highspeed-quirk' not in OTHER.read_text()
HOST=S/'drivers/mmc/host/sdhci-tegra.c'
host_orig=HOST.read_bytes()
host_s=host_orig.decode()
assert host_s.count('static int sdhci_tegra_probe(struct platform_device *pdev)')==1
assert host_s.count('\\trc = mmc_of_parse(host->mmc);')==1
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
    pr_info("%s: xoom-host-hs: forced card high_speed in Tegra init_card (early)\\n",
            mmc_hostname(mmc));
}

'''
host_new=host_s.replace('static int sdhci_tegra_probe(struct platform_device *pdev)',callback+'static int sdhci_tegra_probe(struct platform_device *pdev)',1)
host_new=host_new.replace('\\trc = mmc_of_parse(host->mmc);','\\tif (of_machine_is_compatible("motorola,stingray"))\\n\\t\\thost->mmc_host_ops.init_card = sdhci_tegra_init_bcm4329_card;\\n\\n\\trc = mmc_of_parse(host->mmc);',1)
assert host_new.count('xoom-host-hs:')==1
(V/'sdhci-tegra-host-hs-original.sha256').write_text(hashlib.sha256(host_orig).hexdigest()+'\\n')
(V/'sdhci-tegra-host-hs.patch').write_text(''.join(difflib.unified_diff(host_s.splitlines(True),host_new.splitlines(True),fromfile='a/drivers/mmc/host/sdhci-tegra.c',tofile='b/drivers/mmc/host/sdhci-tegra.c')))
"""
q=q.replace(needle,insert)
needle='\tP.write_text(new)'
assert q.count(needle)==1
q=q.replace(needle,'\tP.write_text(new)\n\tHOST.write_text(host_new)')
needle='\tP.write_bytes(base)'
assert q.count(needle)==1
q=q.replace(needle,'\tP.write_bytes(base)\n\tHOST.write_bytes(host_orig)\n\tassert hashlib.sha256(HOST.read_bytes()).digest()==hashlib.sha256(host_orig).digest()\n\tprint("Original Tegra host source RESTORED VERIFIED")')
(host/'build-v13-host-hs.py').write_text(q)
print('v13 staged: early Tegra init_card high-speed board quirk + precise F2 trace + source restoration')
