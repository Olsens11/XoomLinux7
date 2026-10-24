#!/usr/bin/env python3
"""Read-only v031 GPIO / regulator / clock observer as brcmfmac.ko.
Compiles using known-good v021 instrumentation; no kernel boot or device writes.
Source tree is restored byte-for-byte even on failure.
"""
from pathlib import Path
import subprocess, hashlib, shutil, difflib, os
R=Path(__file__).resolve().parents[2]
K=Path('/home/xoomdev/xoom-linux-rom/linux-src')
O=Path('/home/xoomdev/xoom-linux-rom/build-wingray-gcc14-initramfs')
V=Path('/home/xoomdev/xoom-linux-rom/phase1-v031')
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
#include <linux/serdev.h>
#include <linux/of_clk.h>
#include <linux/of.h>
#include <linux/clk.h>
#include <linux/err.h>

#include <linux/err.h>
#include <dt-bindings/gpio/tegra-gpio.h>
'''
helpers=r'''
/* XOOM_V031_FORENSIC: read-only Tegra GPIO output latch and
 * regulator framework state. No requests, pinmux mutations,
 * regulator enable/disable, sleeps or peripheral register writes.
 * Tegra20 gpiochip base is statically 0 in this kernel, but stop
 * interpreting values if gpiochip provenance differs on device.
 */
static void xoom_v031_gpio(const char *name, int gpio)
{
    struct gpio_desc *d = gpio_to_desc(gpio);
    int direct, raw, logic, active_low;
    if (!d) {
        pr_info("XOOM_V031 GPIO %s pin=%d NO_DESC\n", name, gpio);
        return;
    }
    direct = gpiod_get_direction(d);
    raw = gpiod_get_raw_value_cansleep(d);
    logic = gpiod_get_value_cansleep(d);
    active_low = gpiod_is_active_low(d);
    pr_info("XOOM_V031 GPIO %s pin=%d direction=%d raw=%d logical=%d active_low=%d\n",
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
static void xoom_v031_tegra_raw_regs(void)
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
    if (!np) { pr_info("XOOM_V031 of_gpio_node_missing\n"); return; }
    base=of_iomap(np,0);
    of_node_put(np);
    if (!base) { pr_info("XOOM_V031 iomap_failed\n"); return; }
    for (i=0;i<ARRAY_SIZE(pins);i++) {
        unsigned int g=pins[i].gpio;
        unsigned int pos=(g>>5)*0x80+((g>>3)&3)*4;
        u32 bit=1U<<(g&7);
        u32 cnf=readl_relaxed(base+pos);
        u32 oe=readl_relaxed(base+pos+0x10);
        u32 out=readl_relaxed(base+pos+0x20);
        u32 in=readl_relaxed(base+pos+0x30);
        pr_info("XOOM_V031 pin=%s gpio=%u t_ns=%llu cnf=%u oe=%u out=%u in=%u (controller not pin voltage)\n",
            pins[i].name,g,(unsigned long long)ktime_get_ns(),
            !!(cnf&bit),!!(oe&bit),!!(out&bit),!!(in&bit));
    }
    iounmap(base);
}

/*
 * v031 READ ONLY hardware-model introspection.
 * Does not request any GPIO, enable/disable any regulator/clock, or load BT.
 * A serdev *registered* controller is not evidence of bound hci_bcm.
 */
static void xoom_v031_read_uart_and_clocks(void)
{
    struct device_node *uart, *bt, *wifi;
    struct serdev_controller *ctrl;
    struct clk *bc, *wc;
    const char *compat = NULL;

    uart=of_find_node_by_path("/serial@70006200");
    if (!uart) {
        pr_info("XOOM_V031 UART_NODE_MISSING\n");
        return;
    }
    bt=of_get_child_by_name(uart, "bluetooth");
    pr_info("XOOM_V031 t_ns=%llu UART_OF_AVAILABLE=%u BT_CHILD=%u BT_OF_AVAILABLE=%u\n",
            (unsigned long long)ktime_get_ns(), of_device_is_available(uart),
            !!bt, bt ? of_device_is_available(bt) : 0);
    if (bt) {
        of_property_read_string(bt, "compatible", &compat);
        pr_info("XOOM_V031 BT_COMPAT=%s\n", compat ? compat : "NONE");
    }

    ctrl=of_find_serdev_controller_by_node(uart);
    if (!ctrl) {
        pr_info("XOOM_V031 UART_SERDEV_CTRL=ABSENT BT_BOUND=NO\n");
    } else {
        struct serdev_device *child=ctrl->serdev;
        if (!child) {
            pr_info("XOOM_V031 UART_SERDEV_CTRL=PRESENT CHILD=ABSENT BT_BOUND=NO\n");
        } else {
            const struct device_driver *drv=child->dev.driver;
            pr_info("XOOM_V031 UART_SERDEV_CTRL=PRESENT CHILD=PRESENT DRIVER=%s BT_BOUND=%u\n",
                    drv ? drv->name : "NONE", !!drv);
        }
        serdev_controller_put(ctrl);
    }

    wifi=of_find_node_by_path("/wifi-pwrseq");
    bc=bt ? of_clk_get_by_name(bt, "txco") : ERR_PTR(-ENOENT);
    wc=wifi ? of_clk_get_by_name(wifi, "ext_clock") : ERR_PTR(-ENOENT);
    pr_info("XOOM_V031 BT_TXCO_CLK_RC=%ld WIFI_LPO_CLK_RC=%ld\n",
            IS_ERR(bc)?PTR_ERR(bc):0L, IS_ERR(wc)?PTR_ERR(wc):0L);
    if (!IS_ERR(bc) && !IS_ERR(wc))
        pr_info("XOOM_V031 CLOCKS_SAME_HANDLE=%u BT_RATE_HZ=%lu WIFI_RATE_HZ=%lu\n",
                clk_is_match(bc,wc), clk_get_rate(bc), clk_get_rate(wc));
    if (!IS_ERR(bc))
        clk_put(bc);
    if (!IS_ERR(wc))
        clk_put(wc);
    of_node_put(wifi);
    of_node_put(bt);
    of_node_put(uart);
}

'''
inventory=r'''
    /* Sample states immediately after device FW RAM download/CPU release,
     * BEFORE waiting on SDIO F2 ready. Note Tegra GPIO get for outputs
     * reflects the programmed output latch, not measured pin voltage.
     */
    pr_info("XOOM_V031 SNAPSHOT_BEGIN t_ns=%llu\n", (unsigned long long)ktime_get_ns());
    xoom_v031_gpio("U2_WIFI_RESET", TEGRA_GPIO(U, 2));
    xoom_v031_gpio("U4_WIFI_POWER", TEGRA_GPIO(U, 4));
    xoom_v031_gpio("U5_WIFI_HOST_WAKE", TEGRA_GPIO(U, 5));
    xoom_v031_gpio("I7_BT_REG_ON", TEGRA_GPIO(I, 7));
    xoom_v031_gpio("U0_BT_RST_N", TEGRA_GPIO(U, 0));
    xoom_v031_gpio("U1_BT_WAKE", TEGRA_GPIO(U, 1));
    xoom_v031_gpio("U6_BT_UART_WAKE", TEGRA_GPIO(U, 6));
    xoom_v031_tegra_raw_regs();
    xoom_v031_read_uart_and_clocks();

    pr_info("XOOM_V031 SNAPSHOT_END t_ns=%llu\n", (unsigned long long)ktime_get_ns());
    pr_info("XOOM_V031 MMC_HOST power_delay_ms=%u\n",
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
    (V/'v031-gpio-regulator-readonly.patch').write_text(diff)
    p.write_text(s)
    toolchain='/home/xoomdev/xoom-linux-rom/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-'
    env=dict(os.environ, ARCH='arm',CROSS_COMPILE=toolchain)
    with (V/'build-v031.log').open('wb') as f:
        q=subprocess.run(['make','-j2','O='+str(O),
                          'drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko',
                          'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko'],
                         cwd=K,env=env,stdout=f,stderr=subprocess.STDOUT)
    if q.returncode:
        print((V/'build-v031.log').read_text(errors='replace')[-11000:])
        raise RuntimeError('v031 compile failure')
finally:
    p.write_bytes(baseline)
    assert p.read_bytes()==baseline, 'CRITICAL SOURCE RESTORE FAIL'
    print('SOURCE_RESTORED',basehash,flush=True)
target=V/'brcmfmac-v031-forensic-readonly.ko'
shutil.copyfile(O/'drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko',target)
assert target.read_bytes()[:4]==b'\x7fELF'
print('MODULE_BYTES',target.stat().st_size)
print('MODULE_SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
print('NO_DEVICE_OR_KERNEL_BOOT_WRITES')
