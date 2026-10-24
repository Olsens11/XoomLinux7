#!/usr/bin/env python3
"""Read-only v028 GPIO / regulator / clock observer as brcmfmac.ko.
Compiles using known-good v021 instrumentation; no kernel boot or device writes.
Source tree is restored byte-for-byte even on failure.
"""
from pathlib import Path
import subprocess, hashlib, shutil, difflib, os
R=Path(__file__).resolve().parents[2]
K=Path('/home/xoomdev/xoom-linux-rom/linux-src')
O=Path('/home/xoomdev/xoom-linux-rom/build-wingray-gcc14-initramfs')
V=Path('/home/xoomdev/xoom-linux-rom/phase1-v028')
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
#include <linux/of_address.h>
#include <linux/io.h>

#include <linux/err.h>
#include <dt-bindings/gpio/tegra-gpio.h>
'''
helpers=r'''
/* XOOM_V028_FORENSIC: read-only Tegra GPIO output latch and
 * regulator framework state. No requests, pinmux mutations,
 * regulator enable/disable, sleeps or peripheral register writes.
 * Tegra20 gpiochip base is statically 0 in this kernel, but stop
 * interpreting values if gpiochip provenance differs on device.
 */
static void xoom_v028_gpio(const char *name, int gpio)
{
    struct gpio_desc *d = gpio_to_desc(gpio);
    int direct, raw, logic, active_low;
    if (!d) {
        pr_info("XOOM_V028 GPIO %s pin=%d NO_DESC\n", name, gpio);
        return;
    }
    direct = gpiod_get_direction(d);
    raw = gpiod_get_raw_value_cansleep(d);
    logic = gpiod_get_value_cansleep(d);
    active_low = gpiod_is_active_low(d);
    pr_info("XOOM_V028 GPIO %s pin=%d direction=%d raw=%d logical=%d active_low=%d\n",
            name, gpio, direct, raw, logic, active_low);
}

/* Tegra20 GPIO driver verified: bank_stride=0x80,
 * each bank contains four ports spaced 4 bytes apart.
 * CNF/OE/OUT/IN offsets respectively 0, 0x10, 0x20, 0x30.
 * Separate OF iomap is strictly READ ONLY and is released afterwards.
 * CNF=0 specifically explains gpiod_get_direction()=-EINVAL.
 * IN is a controller input register, NOT proof of chip pin voltage when
 * CNF=0 or alternate pinmux function is selected.
 */
static void xoom_v028_tegra_raw_regs(void)
{
    const struct { const char *name; unsigned int gpio; } pins[] = {
      {"I7_BT_REG_ON", TEGRA_GPIO(I,7)},
      {"U0_BT_RST_N", TEGRA_GPIO(U,0)},
      {"U1_BT_WAKE", TEGRA_GPIO(U,1)},
      {"U6_BT_UART_WAKE", TEGRA_GPIO(U,6)},
      {"U2_WIFI_RESET", TEGRA_GPIO(U,2)},
      {"U4_WIFI_POWER", TEGRA_GPIO(U,4)}
    };
    struct device_node *np;
    void __iomem *base;
    int i;
    np=of_find_compatible_node(NULL,NULL,"nvidia,tegra20-gpio");
    if (!np) { pr_info("XOOM_V028 of_gpio_node_missing\n"); return; }
    base=of_iomap(np,0);
    of_node_put(np);
    if (!base) { pr_info("XOOM_V028 iomap_failed\n"); return; }
    for (i=0;i<ARRAY_SIZE(pins);i++) {
        unsigned int g=pins[i].gpio;
        unsigned int pos=(g>>5)*0x80+((g>>3)&3)*4;
        u32 bit=1U<<(g&7);
        u32 cnf=readl_relaxed(base+pos);
        u32 oe=readl_relaxed(base+pos+0x10);
        u32 out=readl_relaxed(base+pos+0x20);
        u32 in=readl_relaxed(base+pos+0x30);
        pr_info("XOOM_V028 pin=%s gpio=%u t_ns=%llu cnf=%u oe=%u out=%u in=%u (controller not pin voltage)\n",
            pins[i].name,g,(unsigned long long)ktime_get_ns(),
            !!(cnf&bit),!!(oe&bit),!!(out&bit),!!(in&bit));
    }
    iounmap(base);
}

'''
inventory=r'''
    /* Sample states immediately after device FW RAM download/CPU release,
     * BEFORE waiting on SDIO F2 ready. Note Tegra GPIO get for outputs
     * reflects the programmed output latch, not measured pin voltage.
     */
    pr_info("XOOM_V028 SNAPSHOT_BEGIN t_ns=%llu\n", (unsigned long long)ktime_get_ns());
    xoom_v028_gpio("U2_WIFI_RESET", TEGRA_GPIO(U, 2));
    xoom_v028_gpio("U4_WIFI_POWER", TEGRA_GPIO(U, 4));
    xoom_v028_gpio("U5_WIFI_HOST_WAKE", TEGRA_GPIO(U, 5));
    xoom_v028_gpio("I7_BT_REG_ON", TEGRA_GPIO(I, 7));
    xoom_v028_gpio("U0_BT_RST_N", TEGRA_GPIO(U, 0));
    xoom_v028_gpio("U1_BT_WAKE", TEGRA_GPIO(U, 1));
    xoom_v028_gpio("U6_BT_UART_WAKE", TEGRA_GPIO(U, 6));
    xoom_v028_tegra_raw_regs();

    pr_info("XOOM_V028 SNAPSHOT_END t_ns=%llu\n", (unsigned long long)ktime_get_ns());
    pr_info("XOOM_V028 MMC_HOST power_delay_ms=%u\n",
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
    (V/'v028-gpio-regulator-readonly.patch').write_text(diff)
    p.write_text(s)
    toolchain='/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-'
    env=dict(os.environ, ARCH='arm',CROSS_COMPILE=toolchain)
    with (V/'build-v028.log').open('wb') as f:
        q=subprocess.run(['make','-j2','O='+str(O),
                          'drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko',
                          'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko'],
                         cwd=K,env=env,stdout=f,stderr=subprocess.STDOUT)
    if q.returncode:
        print((V/'build-v028.log').read_text(errors='replace')[-11000:])
        raise RuntimeError('v028 compile failure')
finally:
    p.write_bytes(baseline)
    assert p.read_bytes()==baseline, 'CRITICAL SOURCE RESTORE FAIL'
    print('SOURCE_RESTORED',basehash,flush=True)
target=V/'brcmfmac-v028-forensic-readonly.ko'
shutil.copyfile(O/'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko',target)
assert target.read_bytes()[:4]==b'\x7fELF'
print('MODULE_BYTES',target.stat().st_size)
print('MODULE_SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
print('NO_DEVICE_OR_KERNEL_BOOT_WRITES')
