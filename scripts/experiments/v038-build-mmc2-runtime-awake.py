#!/usr/bin/env python3
"""v038: build ONLY a RAM-replaceable BCM4329 read-only PMU/CM3 lifecycle observer.

No Xoom contact. Test holds the verified Tegra MMC host awake during FW/F2, without flashes, firmware swaps, regulator or reset changes. Source/build only.
writes or changes to the shared regulator. Adds only bounded register reads,
single-shot printk events around pre-existing driver operations, timestamps,
and standard compiler instrumentation. Original local Linux source bytes are
restored byte-for-byte in finally even after a compiler failure.

The F2 failure should remain unchanged. Any change must be reviewed as a
potential observability effect, not taken as a valid fix.
"""
from pathlib import Path
from hashlib import sha256
import os
import shutil
import subprocess

BUILD = Path("/home/xoomdev/xoom-linux-rom")
KERNEL = BUILD / "linux-src"
OUTPUT = BUILD / "build-wingray-gcc14-initramfs"
STAGE = BUILD / "phase1-v038"
TOOLCHAIN = BUILD / "toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin"
SDIO = KERNEL / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c"
CHIP = KERNEL / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.c"
EXPECTED_SDIO = "74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab"
EXPECTED_CHIP = "932e25c75f9ea5247194dfdb78c6b41a457af68d7a558935a7b5489bf548aa9d"

SNAPSHOT = r"""
/* v038 bounded diagnostic: no chip writes, no customer calibration or MAC
 * logged. Only source-defined register locations and error codes.
 * Caller holds SDIO host lock in each instrumented location.
 */
static void xoom_v038_sdio_snapshot(struct brcmf_sdio *bus, const char *phase)
{
    struct brcmf_sdio_dev *sdiod = bus->sdiodev;
    struct brcmf_core *pmu = brcmf_chip_get_pmu(bus->ci);
    int ep = 0, ec = 0, ee = 0, er = 0;
    u32 ctl = 0;
    u8 clk = 0, ioex = 0, iorx = 0;

    if (pmu)
        ctl = brcmf_sdiod_readl(sdiod, CORE_CC_REG(pmu->base, pmucontrol), &ep);
    else
        ep = -ENODEV;
    clk = brcmf_sdiod_readb(sdiod, SBSDIO_FUNC1_CHIPCLKCSR, &ec);
    ioex = brcmf_sdiod_func0_rb(sdiod, SDIO_CCCR_IOEx, &ee);
    iorx = brcmf_sdiod_func0_rb(sdiod, SDIO_CCCR_IORx, &er);
    pr_info("XOOM_V038 t_ns=%llu phase=%s pmuctl=%08x/%d clkcsr=%02x/%d ioex=%02x/%d iorx=%02x/%d\n",
            (unsigned long long)ktime_get_ns(), phase, ctl, ep,
            clk, ec, ioex, ee, iorx, er);
    {
        struct brcmf_core *cc = brcmf_chip_get_core(bus->ci, BCMA_CORE_CHIPCOMMON);
        u32 stat = 0, res = 0, pend = 0, pu = 0, pd = 0;
        int a = -ENODEV, b = -ENODEV, c = -ENODEV;
        int u = -ENODEV, d = -ENODEV;
        if (pmu) {
            a = 0; b = 0; c = 0;
            stat = brcmf_sdiod_readl(sdiod, CORE_CC_REG(pmu->base, pmustatus), &a);
            res = brcmf_sdiod_readl(sdiod, CORE_CC_REG(pmu->base, res_state), &b);
            pend = brcmf_sdiod_readl(sdiod, CORE_CC_REG(pmu->base, res_pending), &c);
        }
        if (cc && cc->rev >= 20) {
            u = 0; d = 0;
            pu = brcmf_sdiod_readl(sdiod, CORE_CC_REG(cc->base, gpiopullup), &u);
            pd = brcmf_sdiod_readl(sdiod, CORE_CC_REG(cc->base, gpiopulldown), &d);
        }
        pr_info("XOOM_V038_RES t_ns=%llu phase=%s ccrev=%u pmurev=%u stat=%08x/%d res=%08x/%d pend=%08x/%d pu=%08x/%d pd=%08x/%d\n",
                (unsigned long long)ktime_get_ns(), phase, cc ? cc->rev : 0, bus->ci->pmurev,
                stat, a, res, b, pend, c, pu, u, pd, d);
    }
}
"""

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, got {n}")
    return s.replace(old, new, 1)

def make_sdio(s):
    s = replace_once(s, "#include <linux/unaligned.h>\n",
                     "#include <linux/unaligned.h>\n#include <linux/ktime.h>\n#include <linux/pm_runtime.h>\n",
                     "SDIO ktime+runtime PM include")
    s = replace_once(s, "static int brcmf_sdio_download_firmware(struct brcmf_sdio *bus,",
                     SNAPSHOT + "\nstatic int brcmf_sdio_download_firmware(struct brcmf_sdio *bus,",
                     "snapshot insertion")
    s = replace_once(s,
                     "\t/* set PMUControl so a backplane reset does PMU state reload */",
                     '\txoom_v038_sdio_snapshot(bus, "T0_PRE_PMU_RELOAD");\n' +
                     "\t/* set PMUControl so a backplane reset does PMU state reload */",
                     "PMU before")
    s = replace_once(s,
                     "\tif (err)\n\t\tgoto fail;\n\n\tsdio_release_host(sdiodev->func1);\n\n\tbrcmu_pktq_init(",
                     '\tif (err)\n\t\tgoto fail;\n\txoom_v038_sdio_snapshot(bus, "T1_POST_PMU_RELOAD");\n\n\tsdio_release_host(sdiodev->func1);\n\n\tbrcmu_pktq_init(',
                     "PMU after")
    s = replace_once(s,
                     "\t/* Take arm out of reset */\n\tif (!brcmf_chip_set_active(bus->ci, rstvec)) {",
                     '\t/* Observe normal ARM release; do not alter reset. */\n\txoom_v038_sdio_snapshot(bus, "T2_BEFORE_CM3_RELEASE");\n\tif (!brcmf_chip_set_active(bus->ci, rstvec)) {',
                     "CPU before")
    s = replace_once(s,
                     "\t\tbcmerror = -EIO;\n\t\tgoto err;\n\t}\n\nerr:\n\tbrcmf_sdio_clkctl(",
                     '\t\tbcmerror = -EIO;\n\t\tgoto err;\n\t}\n\txoom_v038_sdio_snapshot(bus, "T3_AFTER_CM3_RELEASE");\n\nerr:\n\tbrcmf_sdio_clkctl(',
                     "CPU after")
    s = replace_once(s,
                     "\terr = sdio_enable_func(sdiod->func2);",
                     '\txoom_v038_sdio_snapshot(bus, "T4_PRE_F2_REQUEST");\n' +
                     "\terr = sdio_enable_func(sdiod->func2);\n" +
                     '\txoom_v038_sdio_snapshot(bus, "T5_POST_F2_RESULT");',
                     "F2 before and after")
    mailbox = ("\tbrcmf_sdiod_writel(sdiod, core->base + SD_REG(tosbmailboxdata),\n"
               "\t\t\t   SDPCM_PROT_VERSION << SMB_DATA_VERSION_SHIFT, NULL);")
    capture = ("\t/* v038: same existing SDPCM write, but record the ignored return code */\n"
               "\t{\n\t\tint xoom_v038_mb_err = 0;\n"
               "\t\tbrcmf_sdiod_writel(sdiod, core->base + SD_REG(tosbmailboxdata),\n"
               "\t\t\t   SDPCM_PROT_VERSION << SMB_DATA_VERSION_SHIFT, &xoom_v038_mb_err);\n"
               "\t\tpr_info(\"XOOM_V038_MAILBOX t_ns=%llu write_rc=%d sdpcm_protocol=%u\\n\",\n"
               "\t\t\t(unsigned long long)ktime_get_ns(), xoom_v038_mb_err,\n"
               "\t\t\t(unsigned int)SDPCM_PROT_VERSION);\n\t}\n")
    s = replace_once(s, mailbox, capture, "SDPCM mailbox return status")

    entry = '\tu8 devctl;\n\n\tbrcmf_dbg(TRACE, "Enter: dev=%s, err=%d\\n", dev_name(dev), err);'
    guarded = (
        '\tu8 devctl;\n'
        '\tstruct device *xoom_hostdev = sdiod->func1->card->host->parent;\n'
        '\tbool xoom_rpm_held;\n'
        '\tint xoom_rpm_rc;\n\n'
        '\txoom_rpm_rc = pm_runtime_resume_and_get(xoom_hostdev);\n'
        '\txoom_rpm_held = xoom_rpm_rc >= 0;\n'
        '\tpr_info("XOOM_V038_HOSTPM phase=ACQUIRE rpm_rc=%d enabled=%d active=%d held=%d\\n",\n'
        '\t        xoom_rpm_rc, pm_runtime_enabled(xoom_hostdev),\n'
        '\t        pm_runtime_active(xoom_hostdev), xoom_rpm_held);\n'
        '\tbrcmf_dbg(TRACE, "Enter: dev=%s, err=%d\\n", dev_name(dev), err);'
    )
    s = replace_once(s, entry, guarded, "hold actual MMC2 SDHCI parent active before download")
    s = replace_once(s,
        '\t/* ready */\n\treturn;\n\nfree:\n',
        '\t/* v038: balance host runtime-PM reference after F2 and attach. */\n'
        '\tif (xoom_rpm_held)\n\t\tpm_runtime_put_sync(xoom_hostdev);\n'
        '\tpr_info("XOOM_V038_HOSTPM phase=SUCCESS_RELEASE active=%d held=%d\\n",\n'
        '\t        pm_runtime_active(xoom_hostdev), xoom_rpm_held);\n'
        '\treturn;\n\nfree:\n',
        "successful callback host reference cleanup")
    s = replace_once(s,
        '\tbrcmf_dbg(TRACE, "failed: dev=%s, err=%d\\n", dev_name(dev), err);\n'
        '\tdevice_release_driver(&sdiod->func2->dev);',
        '\tbrcmf_dbg(TRACE, "failed: dev=%s, err=%d\\n", dev_name(dev), err);\n'
        '\tif (xoom_rpm_held)\n\t\tpm_runtime_put_sync(xoom_hostdev);\n'
        '\tpr_info("XOOM_V038_HOSTPM phase=FAIL_RELEASE error=%d active=%d held=%d\\n",\n'
        '\t        err, pm_runtime_active(xoom_hostdev), xoom_rpm_held);\n'
        '\tdevice_release_driver(&sdiod->func2->dev);',
        "failure callback host reference cleanup")
    return s

def make_chip(s):
    s = replace_once(s, "#include <linux/kernel.h>\n",
                     "#include <linux/kernel.h>\n#include <linux/ktime.h>\n",
                     "chip ktime include")
    s = replace_once(s,
                     "\tchip->ops->activate(chip->ctx, &chip->pub, 0);\n\n\tcore = brcmf_chip_get_core(&chip->pub, BCMA_CORE_ARM_CM3);",
                     '\tpr_info("XOOM_V038 t_ns=%llu phase=CM3_ACTIVATE_BEGIN\\n",\n' +
                     '\t        (unsigned long long)ktime_get_ns());\n' +
                     "\tchip->ops->activate(chip->ctx, &chip->pub, 0);\n\n" +
                     "\tcore = brcmf_chip_get_core(&chip->pub, BCMA_CORE_ARM_CM3);",
                     "CM3 after SOCRAM up")
    s = replace_once(s,
                     "\tbrcmf_chip_resetcore(core, 0, 0, 0);\n\n\treturn true;\n}\n\nstatic inline void",
                     '\tbrcmf_chip_resetcore(core, 0, 0, 0);\n' +
                     '\tpr_info("XOOM_V038 t_ns=%llu phase=CM3_ACTIVATE_DONE\\n",\n' +
                     '\t        (unsigned long long)ktime_get_ns());\n\n\treturn true;\n}\n\nstatic inline void',
                     "CM3 reset release")
    return s

def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    originals = {SDIO: SDIO.read_bytes(), CHIP: CHIP.read_bytes()}
    assert sha256(originals[SDIO]).hexdigest() == EXPECTED_SDIO, "sdio.c pinned source changed; abort"
    assert sha256(originals[CHIP]).hexdigest() == EXPECTED_CHIP, "chip.c pinned source changed; abort"
    assert (TOOLCHAIN / "arm-none-linux-gnueabihf-gcc").exists(), "ARM toolchain missing"
    assert (OUTPUT / ".config").exists(), "prepared kernel output missing"
    sdio = make_sdio(originals[SDIO].decode("utf-8"))
    chip = make_chip(originals[CHIP].decode("utf-8"))
    for src in (sdio, chip):
        assert "XOOM_V038" in src
    env = dict(os.environ, ARCH="arm", CROSS_COMPILE=str(TOOLCHAIN / "arm-none-linux-gnueabihf-"))
    try:
        SDIO.write_text(sdio, encoding="utf-8")
        CHIP.write_text(chip, encoding="utf-8")
        with (STAGE / "compile.log").open("wb") as log:
            proc = subprocess.run(["make", "-j2", "O=" + str(OUTPUT),
                 "drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko",
                 "drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"],
                cwd=KERNEL, env=env, stdout=log, stderr=subprocess.STDOUT)
        if proc.returncode:
            raise RuntimeError("ARM compile failed:\n" +
                               (STAGE / "compile.log").read_text(errors="replace")[-7000:])
    finally:
        for path, source in originals.items():
            path.write_bytes(source)
            if path.read_bytes() != source:
                raise RuntimeError("CRITICAL source restore failed: " + str(path))
    obj = OUTPUT / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
    dest = STAGE / "brcmfmac-v038-pmu-cm3-readonly.ko"
    shutil.copyfile(obj, dest)
    if dest.read_bytes()[:4] != b"\x7fELF":
        raise RuntimeError("not ELF")
    print("BUILT_RAM_ONLY_MODULE", dest.name)
    print("BYTES", dest.stat().st_size)
    print("SHA256", sha256(dest.read_bytes()).hexdigest())
    print("SOURCE_RESTORED", all(sha256(p.read_bytes()).hexdigest()==exp
        for p, exp in ((SDIO, EXPECTED_SDIO), (CHIP, EXPECTED_CHIP))))
    print("NO_HARDWARE_OR_FIRMWARE_ACTION")
if __name__ == "__main__":
    main()
