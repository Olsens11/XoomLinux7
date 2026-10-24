#!/usr/bin/env python3
"""Read-only v024 GPIO / regulator / clock observer as brcmfmac.ko.
Compiles using known-good v021 instrumentation; no kernel boot or device writes.
Source tree is restored byte-for-byte even on failure.
"""
from pathlib import Path
import subprocess, hashlib, shutil, difflib, os
R=Path(__file__).resolve().parents[2]
K=Path('/home/xoomdev/xoom-linux-rom/linux-src')
O=Path('/home/xoomdev/xoom-linux-rom/build-wingray-gcc14-initramfs')
V=Path('/home/xoomdev/xoom-linux-rom/phase1-v024')
V.mkdir(exist_ok=True)
p=K/'drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c'
baseline=p.read_bytes()
basehash=hashlib.sha256(baseline).hexdigest()
assert basehash=='74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab'
patch=R/'patches/experiments/v021-brcmfmac-f2-cccr-readback.patch'
assert patch.exists()
included=r'''
#include <linux/gpio/consumer.h>
#include <linux/regulator/consumer.h>
#include <linux/err.h>
#include <dt-bindings/gpio/tegra-gpio.h>
'''
helpers=r'''
/* XOOM_V024_FORENSIC: read-only Tegra GPIO output latch and
 * regulator framework state. No requests, pinmux mutations,
 * regulator enable/disable, sleeps or peripheral register writes.
 * Tegra20 gpiochip base is statically 0 in this kernel, but stop
 * interpreting values if gpiochip provenance differs on device.
 */
static void xoom_v024_gpio(const char *name, int gpio)
{
    struct gpio_desc *d = gpio_to_desc(gpio);
    int direct, raw, logic, active_low;
    if (!d) {
        pr_info("XOOM_V024 GPIO %s pin=%d NO_DESC\n", name, gpio);
        return;
    }
    direct = gpiod_get_direction(d);
    raw = gpiod_get_raw_value_cansleep(d);
    logic = gpiod_get_value_cansleep(d);
    active_low = gpiod_is_active_low(d);
    pr_info("XOOM_V024 GPIO %s pin=%d direction=%d raw=%d logical=%d active_low=%d\n",
            name, gpio, direct, raw, logic, active_low);
}
static void xoom_v024_regulator(struct mmc_host *host, const char *name)
{
    struct regulator *reg;
    int enabled, voltage;
    /* Optional avoids selecting a dummy if a supply is absent. */
    reg = regulator_get_optional(mmc_dev(host), name);
    if (IS_ERR(reg)) {
        pr_info("XOOM_V024 REG %s lookup_errno=%ld\n",
                name, PTR_ERR(reg));
        return;
    }
    enabled = regulator_is_enabled(reg);
    voltage = regulator_get_voltage(reg);
    pr_info("XOOM_V024 REG %s enabled=%d reported_uV=%d\n",
            name, enabled, voltage);
    regulator_put(reg);
}
'''
inventory=r'''
    /* Sample states immediately after device FW RAM download/CPU release,
     * BEFORE waiting on SDIO F2 ready. Note Tegra GPIO get for outputs
     * reflects the programmed output latch, not measured pin voltage.
     */
    xoom_v024_gpio("U2_WIFI_RESET", TEGRA_GPIO(U, 2));
    xoom_v024_gpio("U4_WIFI_POWER", TEGRA_GPIO(U, 4));
    xoom_v024_gpio("U5_WIFI_HOST_WAKE", TEGRA_GPIO(U, 5));
    xoom_v024_regulator(sdiod->func1->card->host, "vmmc");
    xoom_v024_regulator(sdiod->func1->card->host, "vqmmc");
    pr_info("XOOM_V024 MMC_HOST power_delay_ms=%u\n",
            sdiod->func1->card->host->ios.power_delay_ms);

'''
try:
    subprocess.run(['git','apply','--check','--whitespace=nowarn',str(patch)],cwd=K,check=True)
    subprocess.run(['git','apply','--whitespace=nowarn',str(patch)],cwd=K,check=True)
    s=p.read_text()
    assert s.count('XOOM_LPOV021') >=1
    anchor='#include <linux/clk-provider.h>\n'
    assert s.count(anchor)==1
    s=s.replace(anchor,anchor+included,1)
    anchor='static void brcmf_sdio_firmware_callback(struct device *dev, int err,'
    assert s.count(anchor)==1
    s=s.replace(anchor,helpers+anchor,1)
    anchor='\t/* Make sure backplane clock is on, needed to generate F2 interrupt */'
    assert s.count(anchor)==1
    s=s.replace(anchor,inventory+anchor,1)
    diff=''.join(difflib.unified_diff(baseline.decode().splitlines(True),s.splitlines(True),fromfile='a/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c',tofile='b/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c'))
    (R/'patches/experiments/v024-gpio-regulator-readonly.patch').write_text(diff)
    p.write_text(s)
    toolchain='/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-'
    env=dict(os.environ, ARCH='arm',CROSS_COMPILE=toolchain)
    with (V/'build-v024.log').open('wb') as f:
        q=subprocess.run(['make','-j2','O='+str(O),
                          'drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko',
                          'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko'],
                         cwd=K,env=env,stdout=f,stderr=subprocess.STDOUT)
    if q.returncode:
        print((V/'build-v024.log').read_text(errors='replace')[-11000:])
        raise RuntimeError('v024 compile failure')
finally:
    p.write_bytes(baseline)
    assert p.read_bytes()==baseline, 'CRITICAL SOURCE RESTORE FAIL'
    print('SOURCE_RESTORED',basehash,flush=True)
target=V/'brcmfmac-v024-forensic-readonly.ko'
shutil.copyfile(O/'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko',target)
assert target.read_bytes()[:4]==b'\x7fELF'
print('MODULE_BYTES',target.stat().st_size)
print('MODULE_SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
print('NO_DEVICE_OR_KERNEL_BOOT_WRITES')
