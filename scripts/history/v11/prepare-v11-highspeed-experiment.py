from pathlib import Path
B=Path('/home/xoomdev/xoom-linux-rom')
v=B/'phase1-v11'
v.mkdir(exist_ok=True)
s=(B/'phase1-v10/init.c').read_text()
assert 'PONG XOOM-LINUX V10' in s
s=s.replace('phase-1 v10 OEM BCM4329 CCCR revision quirk A/B test','phase-1 v11 Tegra20 BCM4329 high-speed quirk A/B test')
s=s.replace('V10 OEM CCCR QUIRK','V11 BCM4329 HIGH-SPEED QUIRK').replace('PONG XOOM-LINUX V10','PONG XOOM-LINUX V11')
(v/'init.c').write_text(s)
build=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/build-v10-userland.sh').read_text()
Path('/mnt/c/Users/olsen/XoomLinux/Phase1/build-v11-userland.sh').write_text(build.replace('phase1-v10','phase1-v11').replace('V10','V11'))
x=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/package-stingray-v10-cccr.sh').read_text()
x=x.replace('phase1-v10','phase1-v11').replace('Diagnostic-MZ600-v10-OEM-CCCR','Diagnostic-MZ600-v11-TEGRA-HS').replace('MZ600-stingray-diagnostic-v10-OEM-CCCR-TEMPBOOT-ONLY.img','MZ600-stingray-diagnostic-v11-TEGRA-HS-TEMPBOOT-ONLY.img').replace('init-v10-source.c','init-v11-source.c').replace('kernel-v10.config','kernel-v11.config').replace('V10','V11').replace('v10 OEM BCM4329 CCCR quirk experiment','v11 Tegra2 BCM4329 upstream high-speed capability quirk test')
Path('/mnt/c/Users/olsen/XoomLinux/Phase1/package-stingray-v11-highspeed.sh').write_text(x)
src=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/build-v10-experimental-cccr.py').read_text()
assert 'V10_QUIRK_KERNEL_SHA256' in src
assert 'SDIO_SDIO_REV_1_20' in src
src=src.replace('phase1-v10','phase1-v11').replace('V10','V11').replace('v10','v11').replace('xoom-oem-cccr-quirk','xoom-tegra20-bcm4329-highspeed-quirk').replace('sdio-quirk-experiment.patch','sdio-highspeed-experiment.patch').replace('package-stingray-v10-cccr.sh','package-stingray-v11-highspeed.sh')
src=src.replace('Motorola Stingray downstream\\n\\t * notes BCM4329 reports SDIO spec 1.1 and forces revision 1.2.','Tegra20/BCM4329 upstream patch\\n\\t * notes that WiFi requires forcing SDIO high-speed support.')
old='''\t\tpr_info("%s: Xoom BCM4329 OEM CCCR SDIO revision %u -> %u\\\\\\\\n",
\t\t\tmmc_hostname(card->host), card->cccr.sdio_vsn,
\t\t\tSDIO_SDIO_REV_1_20);
\t\tcard->cccr.sdio_vsn = SDIO_SDIO_REV_1_20;'''
# parse source text robustly using occurrence from expected exact source section
i=src.find('pr_info("%s: Xoom BCM4329 OEM CCCR SDIO revision')
assert i>=0
j=src.find("card->cccr.sdio_vsn = SDIO_SDIO_REV_1_20;",i)
assert j>=0
src=src[:i]+'''pr_info("%s: Xoom BCM4329 Tegra20 high-speed flag %u -> 1\\\\\\\\n",
\t\t\tmmc_hostname(card->host), card->cccr.high_speed);
\t\tcard->cccr.high_speed = 1;'''+src[j+len("card->cccr.sdio_vsn = SDIO_SDIO_REV_1_20;"):]
assert 'SDIO_SDIO_REV_1_20' not in src
assert 'card->cccr.high_speed = 1;' in src
assert 'Xoom BCM4329 Tegra20 high-speed' in src
Path('/mnt/c/Users/olsen/XoomLinux/Phase1/build-v11-highspeed-experiment.py').write_text(src)
print('STAGED V11 USERLAND, PACKAGER, TEMPORARY SOURCE PATCH BUILDER')
