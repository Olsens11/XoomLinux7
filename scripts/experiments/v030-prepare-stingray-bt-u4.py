from pathlib import Path
import difflib, hashlib, re
repo=Path("/home/xoomdev/projects/XoomLinux7-bt-v030")
upstream=Path("/home/xoomdev/xoom-linux-rom/linux-src/drivers/bluetooth/hci_bcm.c")
old=upstream.read_text()
expected="3cdaf7e671babfc131f94909c009de0450e6da628786b2f9d9220c85d862bda2"
if hashlib.sha256(old.encode()).hexdigest()!=expected:
 raise RuntimeError("Refusing to patch an unqualified hci_bcm.c source revision")
s=old
def one(before,after,where):
 global s
 n=s.count(before)
 if n!=1: raise AssertionError(f"{where}: expected one anchor got {n}")
 s=s.replace(before,after,1)

one('''\tstruct clk\t\t*lpo_clk;
\tstruct regulator_bulk_data supplies[BCM_NUM_SUPPLIES];
\tbool\t\t\tres_enabled;''','''\tstruct clk\t\t*lpo_clk;
\tstruct regulator_bulk_data supplies[BCM_NUM_SUPPLIES];
\t/* Motorola Stingray: BT and WLAN vote on existing U4-backed regulator. */
\tstruct regulator\t*stingray_shared;
\tbool\t\t\tstingray_vote;
\tbool\t\t\tstingray_i7_passive;
\tbool\t\t\tres_enabled;''',"struct fields")
one('''\tdev->name = dev_name(dev->dev);

\tif (x86_apple_machine''','''\tdev->name = dev_name(dev->dev);
\t/* Board-specific opt-in only; generic Broadcom devices unchanged. */
\tif (dev->dev->of_node &&
\t    of_device_is_compatible(dev->dev->of_node,
\t				"motorola,stingray-bcm4329-bt") &&
\t    device_property_read_bool(dev->dev, "motorola,shared-u4-power")) {
\t\tdev->stingray_shared = devm_regulator_get(dev->dev, "shared");
\t\tif (IS_ERR(dev->stingray_shared))
\t\t\treturn PTR_ERR(dev->stingray_shared);
\t\tdev->stingray_i7_passive = true;
\t}
\tif (x86_apple_machine''',"resource opt in")
one('''\tgpiod_set_value_cansleep(dev->shutdown, powered);
\tif (dev->reset)''','''\t/* Stingray OEM held BT_SHUTDOWN/I7 low on either rfkill edge.
\t * U0 BT_RST_N, not I7, controls Bluetooth core reset here.
\t */
\tgpiod_set_value_cansleep(dev->shutdown,
\t\t\t\t  dev->stingray_i7_passive ? false : powered);
\tif (dev->reset)''',"i7 passive")
one('''\tif (powered && !dev->res_enabled) {
\t\t/* Intel Macs use''','''\tif (powered && !dev->res_enabled) {
\t\t/* Vote shared U4 *before* clock, reset or firmware operations.
\t\t * MMC's vmmc consumer already owns the same regulator, so
\t\t * the regulator core handles reference counting.
\t\t */
\t\tif (dev->stingray_shared && !dev->stingray_vote) {
\t\t\terr = regulator_enable(dev->stingray_shared);
\t\t\tif (err)
\t\t\t\treturn err;
\t\t\tdev->stingray_vote = true;
\t\t\tdev_info(dev->dev, "XOOM_V030 shared_U4_vote=on\\n");
\t\t}
\t\t/* Intel Macs use''',"poweron vote")
one('''\t\tif (err)
\t\t\t\treturn err;
\t\t}

\t\t/* LPO clock needs to be 32.768 kHz */''','''\t\tif (err)
\t\t\t\tgoto err_stingray_vote;
\t\t}

\t\t/* LPO clock needs to be 32.768 kHz */''',"bulk fail unwind")
one('''\tif (!powered && dev->res_enabled) {
\t\tclk_disable_unprepare(dev->txco_clk);''','''\tif (!powered && dev->res_enabled) {
\t\t/* Reset and device-wake were deasserted above. If dropping
\t\t * the vote fails, leave other resources enabled and report
\t\t * failure instead of claiming a completed power transition.
\t\t */
\t\tif (dev->stingray_vote) {
\t\t\terr = regulator_disable(dev->stingray_shared);
\t\t\tif (err)
\t\t\t\treturn err;
\t\t\tdev->stingray_vote = false;
\t\t\tdev_info(dev->dev, "XOOM_V030 shared_U4_vote=off\\n");
\t\t}
\t\tclk_disable_unprepare(dev->txco_clk);''',"poweroff vote")
one('''err_regulator_disable:
\tif (powered && !dev->res_enabled)
\t\tregulator_bulk_disable(BCM_NUM_SUPPLIES, dev->supplies);
\treturn err;''','''err_regulator_disable:
\tif (powered && !dev->res_enabled)
\t\tregulator_bulk_disable(BCM_NUM_SUPPLIES, dev->supplies);
err_stingray_vote:
\tif (dev->stingray_vote) {
\t\tint ret = regulator_disable(dev->stingray_shared);

\t\tif (ret)
\t\t\tdev_err(dev->dev, "XOOM_V030 failed to unwind U4 vote: %d\\n", ret);
\t\telse
\t\t\tdev->stingray_vote = false;
\t}
\treturn err;''',"unwind")
# In generic hci_bcm the active-low reset was acquired as GPIOD_OUT_LOW,
# which logically DEASSERTS U0 reset until the later initial power-off.
# Stingray must start passive: claim U0 already asserted, no startup pulse.
orig='GPIOD_OUT_LOW);\n\tif (IS_ERR(dev->reset))'
safe='dev->stingray_i7_passive ? GPIOD_OUT_HIGH : GPIOD_OUT_LOW);\n\tif (IS_ERR(dev->reset))'
assert s.count(orig)==1
s=s.replace(orig,safe)

# Observability: every emitted timestamp is a kernel-side command, not
# proof of voltage at the BCM4329 pad or internal power rail.
inc='#include <linux/clk.h>\n'
assert s.count(inc)==1
s=s.replace(inc,inc+'#include <linux/ktime.h>\n',1)
for st in ('on','off'):
 oldlog=f'dev_info(dev->dev, "XOOM_V030 shared_U4_vote={st}\\n");'
 newlog=(f'dev_info(dev->dev, "XOOM_V030 t_ns=%llu event=BT_U4_VOTE_{st.upper()}\\n",\n'
         '\t\t\t (unsigned long long)ktime_get_ns());')
 assert s.count(oldlog)==1,(st,s.count(oldlog))
 s=s.replace(oldlog,newlog,1)
line='\t\tgpiod_set_value_cansleep(dev->reset, !powered);'
addition=('\n\tif (dev->stingray_i7_passive)\n'
          '\t\tdev_info(dev->dev, "XOOM_V030 t_ns=%llu event=BT_RESET_REQUEST release=%d i7_passive=1\\n",\n'
          '\t\t\t (unsigned long long)ktime_get_ns(), powered);')
assert s.count(line)==1
s=s.replace(line,line+addition,1)

assert "stingray_vote" in s and old!=s
out=repo/"patches/experiments/v030-stingray-hci-bcm-u4.patch"
out.parent.mkdir(parents=True,exist_ok=True)
diff="".join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile="a/drivers/bluetooth/hci_bcm.c",tofile="b/drivers/bluetooth/hci_bcm.c"))
out.write_text(diff)
# Keep modified source OUTSIDE the Linux kernel tree for the compile-only test.
stage=Path("/home/xoomdev/xoom-linux-rom/phase1-v030-bt-power")
stage.mkdir(parents=True,exist_ok=True)
(stage/"hci_bcm.c").write_text(s)
for name in ("hci_uart.h","btbcm.h"):
 p=upstream.parent/name
 (stage/name).write_bytes(p.read_bytes())
(stage/"Makefile").write_text("obj-m += hci_bcm.o\n")
print("PATCHED_C_SHA256",hashlib.sha256(s.encode()).hexdigest())
print("ORIGINAL_C_SHA256",hashlib.sha256(old.encode()).hexdigest())
print("PATCH",out,"LINES",len(diff.splitlines()))
print("ROOT_KERNEL_UNCHANGED")
