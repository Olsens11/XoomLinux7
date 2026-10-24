from pathlib import Path
B=Path('/home/xoomdev/xoom-linux-rom')
v=B/'phase1-v12'
v.mkdir(exist_ok=True)
s=(B/'phase1-v11/init.c').read_text()
assert 'PONG XOOM-LINUX V11' in s
s=s.replace('phase-1 v11 Tegra20 BCM4329 high-speed quirk A/B test','phase-1 v12 upstream SDIO F2 IOEx IORx timeout instrumentation')
s=s.replace('V11 BCM4329 HIGH-SPEED QUIRK','V12 SDIO F2 CCCR TRACE').replace('PONG XOOM-LINUX V11','PONG XOOM-LINUX V12')
(v/'init.c').write_text(s)
host=Path('/mnt/c/Users/olsen/XoomLinux/Phase1')
a=(host/'build-v11-userland.sh').read_text()
(host/'build-v12-userland.sh').write_text(a.replace('phase1-v11','phase1-v12').replace('V11','V12'))
p=(host/'package-stingray-v11-highspeed.sh').read_text()
p=p.replace('phase1-v11','phase1-v12').replace('Diagnostic-MZ600-v11-TEGRA-HS','Diagnostic-MZ600-v12-F2-TRACE').replace('MZ600-stingray-diagnostic-v11-TEGRA-HS-TEMPBOOT-ONLY.img','MZ600-stingray-diagnostic-v12-F2-TRACE-TEMPBOOT-ONLY.img').replace('init-v11-source.c','init-v12-source.c').replace('kernel-v11.config','kernel-v12.config').replace('V11','V12').replace('v11 Tegra2 BCM4329 upstream high-speed capability quirk test','v12 upstream SDIO F2 IOEx and IORx timeout tracing (no new writes)')
(host/'package-stingray-v12-f2-trace.sh').write_text(p)
print('V12 freestanding userland & Android boot packager staged; previous v11 high-speed test NOT carried into live patch')
