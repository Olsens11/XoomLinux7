#!/usr/bin/env python3
"""v045: build RAM-replaceable BCM4329 with original upstream WCC vops linked inline.

No Xoom contact. No boot image changes, flash, firmware swaps, power/reset
writes or changes to the shared regulator. Links only upstream vendor ops plus bounded register reads,
single-shot printk events around pre-existing driver operations, timestamps,
and standard compiler instrumentation. Original local Linux source bytes are
restored byte-for-byte in finally even after a compiler failure.

The F2 failure is expected to be tested with a separate identical-stock-MAC NVRAM trial. Any change must be reviewed as a
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
STAGE = BUILD / "phase1-v045"
TOOLCHAIN = BUILD / "toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin"
SDIO = KERNEL / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c"
CHIP = KERNEL / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.c"
EXPECTED_SDIO = "74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab"
EXPECTED_CHIP = "932e25c75f9ea5247194dfdb78c6b41a457af68d7a558935a7b5489bf548aa9d"
FWVID = KERNEL / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.c"
BRCM_MAKEFILE = KERNEL / "drivers/net/wireless/broadcom/brcm80211/brcmfmac/Makefile"
EXPECTED_FWVID = "0b495cc8e5287c1f24b1ae411f0d74c6c0bbe491a866c1982f6a0d0eb616a7c1"
EXPECTED_MAKEFILE = "fba4e66e491186c5fdd295d81602a83abc5f8b827a104f9910fe6aa9214f815f"

SNAPSHOT = r"""
/* v045 bounded diagnostic: no chip writes, no customer calibration or MAC
 * logged. Only source-defined register locations and error codes.
 * Caller holds SDIO host lock in each instrumented location.
 */
static void xoom_v045_sdio_snapshot(struct brcmf_sdio *bus, const char *phase)
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
    pr_info("XOOM_V045 t_ns=%llu phase=%s pmuctl=%08x/%d clkcsr=%02x/%d ioex=%02x/%d iorx=%02x/%d\n",
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
        pr_info("XOOM_V045_RES t_ns=%llu phase=%s ccrev=%u pmurev=%u stat=%08x/%d res=%08x/%d pend=%08x/%d pu=%08x/%d pd=%08x/%d\n",
                (unsigned long long)ktime_get_ns(), phase, cc ? cc->rev : 0, bus->ci->pmurev,
                stat, a, res, b, pend, c, pu, u, pd, d);
    }
}


/* v045: read-only CPU core state and NVRAM-token versus shared pointer candidate.
 * Never log NVRAM values, firmware bytes or device identifiers.
 */
static void xoom_v045_handoff(struct brcmf_sdio *bus, const char *phase,
                             u32 nvlen, bool read_tail)
{
    struct brcmf_core *arm = brcmf_chip_get_core(bus->ci, BCMA_CORE_ARM_CM3);
    bool up = arm ? brcmf_chip_iscoreup(arm) : false;
    u8 tail[4] = {0};
    u32 ram_end = bus->ci->rambase + bus->ci->ramsize;
    u32 expected = 0, observed = 0;
    int rc = -EOPNOTSUPP;
    bool matches = false;

    bool tail_is_length = false;
    bool tail_is_ptr = false;
    if (nvlen >= 4 && !(nvlen & 3)) {
        u32 words = (nvlen - 4) / 4;
        expected = (~words << 16) | (words & 0xffff);
    }
    if (read_tail && bus->ci->ramsize >= 4) {
        rc = brcmf_sdiod_ramrw(bus->sdiodev, false, ram_end - 4,
                              tail, sizeof(tail));
        if (!rc) {
            observed = get_unaligned_le32(tail);
            matches = observed == expected && nvlen >= 4;
            tail_is_length = ((observed >> 16) ^ (observed & 0xffff)) == 0xffff;
            tail_is_ptr = !(observed & 3) &&
                  observed >= bus->ci->rambase &&
                  observed < ram_end - 32 && !tail_is_length;
        }
    }
    /*
     * OEM dhdsdio_readshared() parses a 7-word SDPCM shared header.
     * Read ONLY the 28-byte header, ONLY once after the failed F2 request,
     * ONLY when the firmware has replaced the length token with an aligned
     * in-bounds address. Never publish raw memory, console text or NVRAM.
     */
    if (tail_is_ptr && !nvlen) {
        u8 header[28] = {0};
        int shared_rc;
        u32 flags = 0, trap = 0, con = 0, msg = 0, assert_exp = 0;
        bool console_in_ram = false;
        bool message_in_ram = false;
        shared_rc = brcmf_sdiod_ramrw(bus->sdiodev, false,
                                      observed, header, sizeof(header));
        if (!shared_rc) {
            flags = get_unaligned_le32(&header[0]);
            trap = get_unaligned_le32(&header[4]);
            assert_exp = get_unaligned_le32(&header[8]);
            con = get_unaligned_le32(&header[20]);
            msg = get_unaligned_le32(&header[24]);
            console_in_ram = con >= bus->ci->rambase &&
                             con < ram_end - 64 && !(con & 3);
            message_in_ram = msg >= bus->ci->rambase &&
                             msg < ram_end - 64 && !(msg & 3);
        }
        pr_info("XOOM_V045_SHARED t_ns=%llu read_rc=%d shared_addr=0x%08x shared_below_128k=%u first4_le=0x%08x version=%u assert_flag=%u trap_flag=%u trap_ptr_nonzero=%u assert_ptr_nonzero=%u console_ptr=0x%08x console_ptr_in_ram=%u msgtrace_ptr=0x%08x msgtrace_ptr_in_ram=%u\n",
                (unsigned long long)ktime_get_ns(), shared_rc,
                observed, observed < bus->ci->rambase + 131072,
                flags, flags & 0xff, !!(flags & 0x200), !!(flags & 0x400),
                trap != 0, assert_exp != 0,
                con, console_in_ram, msg, message_in_ram);
        if (!shared_rc && console_in_ram) {
            u8 loghead[12] = {0};
            u32 ring_addr = 0, ring_len = 0, ring_idx = 0;
            int log_rc = brcmf_sdiod_ramrw(bus->sdiodev, false,
                                            con + 8, loghead, sizeof(loghead));
            bool bounded = false;
            if (!log_rc) {
                ring_addr = get_unaligned_le32(&loghead[0]);
                ring_len = get_unaligned_le32(&loghead[4]);
                ring_idx = get_unaligned_le32(&loghead[8]);
                bounded = ring_len > 0 && ring_len <= 2048 &&
                    ring_idx <= ring_len &&
                    ring_addr >= bus->ci->rambase &&
                    (u64)ring_addr + ring_len <= ram_end;
            }
            pr_info("XOOM_V045_CONSOLE_META t_ns=%llu read_rc=%d log_buf_addr=0x%08x log_buf_below_128k=%u log_buf_size=%u log_idx=%u metadata_bounded=%u\n",
                    (unsigned long long)ktime_get_ns(), log_rc,
                    ring_addr, ring_addr < bus->ci->rambase + 131072,
                    ring_len, ring_idx, bounded ? 1 : 0);
            /*
             * No raw console bytes or user strings in kernel log: the ring
             * could contain MAC, SSID, or other device-specific material.
             * Read only a bounded sample and report counters and fixed
             * diagnostic keywords, not content.
             */
            if (bounded) {
                u8 ring[128] = {0};
                u32 n = min_t(u32, ring_len, sizeof(ring));
                u32 i, printable = 0, newline = 0, nonzero = 0;
                int ring_rc = brcmf_sdiod_ramrw(bus->sdiodev, false,
                                                 ring_addr, ring, n);
                if (!ring_rc) {
                    for (i = 0; i < n; i++) {
                        printable += ring[i] >= 0x20 && ring[i] <= 0x7e;
                        newline += ring[i] == '\n';
                        nonzero += ring[i] != 0;
                    }
                }
                pr_info("XOOM_V045_CONSOLE_SAMPLE t_ns=%llu read_rc=%d sample_bytes=%u printable=%u newlines=%u nonzero=%u\n",
                        (unsigned long long)ktime_get_ns(), ring_rc, n,
                        printable, newline, nonzero);
            }
        }
    }
    pr_info("XOOM_V045_HANDOFF t_ns=%llu phase=%s arm_up=%u ram_base=%08x ram_size=%u nvram_packed=%u tail_read_rc=%d token_matches=%u tail_is_length=%u tail_is_shared_ptr_candidate=%u\n",
            (unsigned long long)ktime_get_ns(), phase, up ? 1 : 0,
            bus->ci->rambase, bus->ci->ramsize, nvlen, rc,
            matches ? 1 : 0, tail_is_length ? 1 : 0, tail_is_ptr ? 1 : 0);
}
"""

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, got {n}")
    return s.replace(old, new, 1)

def make_sdio(s):
    s = replace_once(s, "#include <linux/unaligned.h>\n",
                     "#include <linux/unaligned.h>\n#include <linux/ktime.h>\n",
                     "SDIO ktime include")
    s = replace_once(s, "static int brcmf_sdio_download_firmware(struct brcmf_sdio *bus,",
                     SNAPSHOT + "\nstatic int brcmf_sdio_download_firmware(struct brcmf_sdio *bus,",
                     "snapshot insertion")
    s = replace_once(s,
                     "\t/* set PMUControl so a backplane reset does PMU state reload */",
                     '\txoom_v045_sdio_snapshot(bus, "T0_PRE_PMU_RELOAD");\n' +
                     "\t/* set PMUControl so a backplane reset does PMU state reload */",
                     "PMU before")
    s = replace_once(s,
                     "\tif (err)\n\t\tgoto fail;\n\n\tsdio_release_host(sdiodev->func1);\n\n\tbrcmu_pktq_init(",
                     '\tif (err)\n\t\tgoto fail;\n\txoom_v045_sdio_snapshot(bus, "T1_POST_PMU_RELOAD");\n\n\tsdio_release_host(sdiodev->func1);\n\n\tbrcmu_pktq_init(',
                     "PMU after")
    s = replace_once(s,
                     "\t/* Take arm out of reset */\n\tif (!brcmf_chip_set_active(bus->ci, rstvec)) {",
                     '\t/* Observe normal ARM release; do not alter reset. */\n\txoom_v045_sdio_snapshot(bus, "T2_BEFORE_CM3_RELEASE");\n\txoom_v045_handoff(bus, "PRE_CM3_RELEASE", nvlen, true);\n\tif (!brcmf_chip_set_active(bus->ci, rstvec)) {',
                     "CPU before")
    s = replace_once(s,
                     "\t\tbcmerror = -EIO;\n\t\tgoto err;\n\t}\n\nerr:\n\tbrcmf_sdio_clkctl(",
                     '\t\tbcmerror = -EIO;\n\t\tgoto err;\n\t}\n\txoom_v045_sdio_snapshot(bus, "T3_AFTER_CM3_RELEASE");\n\txoom_v045_handoff(bus, "POST_CM3_RELEASE", nvlen, false);\n\nerr:\n\tbrcmf_sdio_clkctl(',
                     "CPU after")
    s = replace_once(s,
                     "\terr = sdio_enable_func(sdiod->func2);",
                     '\txoom_v045_sdio_snapshot(bus, "T4_PRE_F2_REQUEST");\n\txoom_v045_handoff(bus, "PRE_F2_REQUEST", 0, false);\n' +
                     "\terr = sdio_enable_func(sdiod->func2);\n" +
                     '\txoom_v045_sdio_snapshot(bus, "T5_POST_F2_RESULT");\n' +
                     '\txoom_v045_handoff(bus, "POST_F2_RESULT", 0, true);',
                     "F2 before and after")
    mailbox = ("\tbrcmf_sdiod_writel(sdiod, core->base + SD_REG(tosbmailboxdata),\n"
               "\t\t\t   SDPCM_PROT_VERSION << SMB_DATA_VERSION_SHIFT, NULL);")
    capture = ("\t/* v045: same existing SDPCM write, but record the ignored return code */\n"
               "\t{\n\t\tint xoom_v045_mb_err = 0;\n"
               "\t\tbrcmf_sdiod_writel(sdiod, core->base + SD_REG(tosbmailboxdata),\n"
               "\t\t\t   SDPCM_PROT_VERSION << SMB_DATA_VERSION_SHIFT, &xoom_v045_mb_err);\n"
               "\t\tpr_info(\"XOOM_V045_MAILBOX t_ns=%llu write_rc=%d sdpcm_protocol=%u\\n\",\n"
               "\t\t\t(unsigned long long)ktime_get_ns(), xoom_v045_mb_err,\n"
               "\t\t\t(unsigned int)SDPCM_PROT_VERSION);\n\t}\n")
    s = replace_once(s, mailbox, capture, "SDPCM mailbox return status")
    return s

def make_chip(s):
    s = replace_once(s, "#include <linux/kernel.h>\n",
                     "#include <linux/kernel.h>\n#include <linux/ktime.h>\n",
                     "chip ktime include")
    s = replace_once(s,
                     "\tchip->ops->activate(chip->ctx, &chip->pub, 0);\n\n\tcore = brcmf_chip_get_core(&chip->pub, BCMA_CORE_ARM_CM3);",
                     '\tpr_info("XOOM_V045 t_ns=%llu phase=CM3_ACTIVATE_BEGIN\\n",\n' +
                     '\t        (unsigned long long)ktime_get_ns());\n' +
                     "\tchip->ops->activate(chip->ctx, &chip->pub, 0);\n\n" +
                     "\tcore = brcmf_chip_get_core(&chip->pub, BCMA_CORE_ARM_CM3);",
                     "CM3 after SOCRAM up")
    s = replace_once(s,
                     "\tbrcmf_chip_resetcore(core, 0, 0, 0);\n\n\treturn true;\n}\n\nstatic inline void",
                     '\tbrcmf_chip_resetcore(core, 0, 0, 0);\n' +
                     '\tpr_info("XOOM_V045 t_ns=%llu phase=CM3_ACTIVATE_DONE\\n",\n' +
                     '\t        (unsigned long long)ktime_get_ns());\n\n\treturn true;\n}\n\nstatic inline void',
                     "CM3 reset release")
    return s


def make_fwvid(s):
    # WCC upstream plugin has no new behavior. Link its existing vops into
    # brcmfmac for this RAM-only bootloader lacking a general modprobe helper.
    # Do not suppress failures from CYW/BCA/other vendors.
    old = ("static int brcmf_fwvid_request_module(enum brcmf_fwvendor fwvid)\n"
           "{\n\tint ret;\n")
    new = ("static int brcmf_fwvid_request_module(enum brcmf_fwvendor fwvid)\n"
           "{\n\tint ret;\n"
           "\t/* v045 temporary: self-contained upstream WCC vendor vops */\n"
           "\tif (fwvid == BRCMF_FWVENDOR_WCC) {\n"
           "\t\tfwvid_list[fwvid].vmod = THIS_MODULE;\n"
           "\t\tfwvid_list[fwvid].vops = WCC_VOPS;\n"
           "\t\tpr_info(\"XOOM_V045_WCC_BUILTIN enabled=1\\n\");\n"
           "\t\treturn 0;\n"
           "\t}\n")
    return replace_once(s, old, new, "WCC module-registered fallback")

def make_kbuild(s):
    mark = ("brcmfmac-objs += \\\n"
            "\t\tcfg80211.o \\\n")
    rep = ("# v045 RAM-only experiment: include upstream WCC vendor ops in core module.\n"
           "brcmfmac-objs += wcc/core.o\n"
           "brcmfmac-objs += \\\n"
           "\t\tcfg80211.o \\\n")
    return replace_once(s, mark, rep, "brcmfmac WCC composite link")

def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    originals = {SDIO: SDIO.read_bytes(), CHIP: CHIP.read_bytes(),
                 FWVID: FWVID.read_bytes(), BRCM_MAKEFILE: BRCM_MAKEFILE.read_bytes()}
    assert sha256(originals[SDIO]).hexdigest() == EXPECTED_SDIO, "sdio.c pinned source changed; abort"
    assert sha256(originals[CHIP]).hexdigest() == EXPECTED_CHIP, "chip.c pinned source changed; abort"
    assert sha256(originals[FWVID]).hexdigest() == EXPECTED_FWVID, "fwvid.c pinned source changed; abort"
    assert sha256(originals[BRCM_MAKEFILE]).hexdigest() == EXPECTED_MAKEFILE, "Makefile pinned source changed; abort"
    assert (TOOLCHAIN / "arm-none-linux-gnueabihf-gcc").exists(), "ARM toolchain missing"
    assert (OUTPUT / ".config").exists(), "prepared kernel output missing"
    sdio = make_sdio(originals[SDIO].decode("utf-8"))
    chip = make_chip(originals[CHIP].decode("utf-8"))
    fwvid = make_fwvid(originals[FWVID].decode("utf-8"))
    makefile = make_kbuild(originals[BRCM_MAKEFILE].decode("utf-8"))
    for src in (sdio, chip):
        assert "XOOM_V045" in src
    env = dict(os.environ, ARCH="arm", CROSS_COMPILE=str(TOOLCHAIN / "arm-none-linux-gnueabihf-"))
    try:
        SDIO.write_text(sdio, encoding="utf-8")
        CHIP.write_text(chip, encoding="utf-8")
        FWVID.write_text(fwvid, encoding="utf-8")
        BRCM_MAKEFILE.write_text(makefile, encoding="utf-8")
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
    dest = STAGE / "brcmfmac-v045-pmu-cm3-readonly.ko"
    shutil.copyfile(obj, dest)
    if dest.read_bytes()[:4] != b"\x7fELF":
        raise RuntimeError("not ELF")
    print("BUILT_RAM_ONLY_MODULE", dest.name)
    print("BYTES", dest.stat().st_size)
    print("SHA256", sha256(dest.read_bytes()).hexdigest())
    print("SOURCE_RESTORED", all(sha256(p.read_bytes()).hexdigest()==exp
        for p, exp in ((SDIO, EXPECTED_SDIO), (CHIP, EXPECTED_CHIP), (FWVID, EXPECTED_FWVID), (BRCM_MAKEFILE, EXPECTED_MAKEFILE))))
    print("NO_HARDWARE_OR_FIRMWARE_ACTION")
if __name__ == "__main__":
    main()
