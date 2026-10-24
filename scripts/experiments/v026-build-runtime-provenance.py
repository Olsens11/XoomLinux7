#!/usr/bin/env python3
"""v026 firmware/NVRAM provenance build candidate -- NOT YET HARDWARE VERIFIED.

Builds a RAM-replaceable Broadcom driver; does NOT flash, boot or touch a Xoom.
Changes ONLY two locally checked-out Linux source files while compiling and
restores them byte-for-byte even on failure. Abort if source anchors differ.

The existing v024 read-only SDIO/GPIO observer is reused. The additional
firmware instrumentation records only timestamps, firmware lookup selection,
buffer length and CRC32. Never logs NVRAM values, MACs or buffer contents.
"""
from pathlib import Path
from hashlib import sha256
import difflib
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BUILD = Path("/home/xoomdev/xoom-linux-rom")
KERNEL = BUILD / "linux-src"
OUTPUT = BUILD / "build-wingray-gcc14-initramfs"
STAGE = BUILD / "phase1-v026"
TOOLCHAIN = BUILD / "toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin"
REL_SDIO = "drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c"
REL_FW = "drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c"
SDIO = KERNEL / REL_SDIO
FW = KERNEL / REL_FW
EXPECTED_SDIO_SHA256 = "74491e8fa7326dacc9049821ed74bec2ac55338443793735e5c3bf8f3f0963ab"
EXPECTED_FW_SHA256 = "f2b6fe570981bf69a81fd5965712f18840df9b97dabcdbd4aa4cf260b4e9760b"
PATCH = ROOT / "patches/experiments/v024-gpio-regulator-readonly.patch"

def require_once(s: str, needle: str, label: str) -> None:
    hits = s.count(needle)
    if hits != 1:
        raise RuntimeError(f"{label}: expected exactly one matching anchor, got {hits}")

def inject(s: str, needle: str, insert: str, label: str) -> str:
    require_once(s, needle, label)
    return s.replace(needle, insert + needle, 1)

def local_crc32(data_expression: str, length_expression: str) -> str:
    return f"xoom_v026_crc32((const u8 *)({data_expression}), ({length_expression}))"

# This function is kept out of the kernel crypto API and is deterministic
# across ARM kernels. It uses the same reflected CRC32 polynomial as the
# existing verified USB lab's CRC32 for comparison, but is not a cryptographic
# integrity proof.
FW_HELPERS = r'''
/* v026 diagnostic ONLY. No identifiers, source file bytes or calibration
 * strings are emitted. Use a monotonic kernel clock for relative ordering.
 */
static u32 xoom_v026_crc32(const u8 *data, size_t length)
{
    u32 crc = ~0U;
    size_t i;
    unsigned int b;
    if (!data)
        return 0;
    for (i = 0; i < length; i++) {
        crc ^= data[i];
        for (b = 0; b < 8; b++)
            crc = (crc >> 1) ^ ((crc & 1) ? 0xedb88320U : 0);
    }
    return ~crc;
}
static void xoom_v026_blob(const char *label, const u8 *data, size_t length)
{
    pr_info("XOOM_PROV026 t_ns=%llu kind=%s bytes=%zu crc32=%08x\n",
            (unsigned long long)ktime_get_ns(), label,
            length, xoom_v026_crc32(data, length));
}
'''

def make_fw(src: str) -> str:
    s = src
    s = inject(s, "#include <linux/efi.h>\n",
               "#include <linux/ktime.h>\n", "firmware timing include")
    s = inject(s, "static void *brcmf_fw_nvram_strip(",
               FW_HELPERS + "\n", "CRC32 provenance helpers")

    # Log whether a platform MAC exists. No MAC values or bytes are logged.
    anchor = """\tif (eth_platform_get_mac_address(dev, mac) == 0)
\t\tnvp.strip_mac = true;"""
    require_once(s,anchor,"platform MAC lookup")
    s=s.replace(anchor,anchor+r"""
    pr_info("XOOM_PROV026 t_ns=%llu phase=PLATFORM_MAC available=%d\n",
            (unsigned long long)ktime_get_ns(), nvp.strip_mac);
""",1)

    # Capture final NUL-delimited, padded NVRAM plus little endian length token
    # at exactly the point the kernel parser finishes.
    anchor = "\t*new_length += sizeof(token_le);\n"
    require_once(s,anchor,"final packed length")
    s=s.replace(anchor,anchor+r"""
    xoom_v026_blob("NVRAM_PACKED", nvp.nvram, *new_length);
""",1)

    # Capture source text metadata without printing its data or identifiers.
    anchor = "\tif (data)\n\t\tnvram = brcmf_fw_nvram_strip("
    require_once(s,anchor,"source text-to-packed path")
    s=s.replace(anchor,r"""
    pr_info("XOOM_PROV026 t_ns=%llu phase=NVRAM_SOURCE type=%s\n",
            (unsigned long long)ktime_get_ns(),
            (fw && fw->data) ? "FILE" :
                (free_bcm47xx_nvram ? "NVRAM_PLATFORM" :
                (kfree_nvram ? "EFI" : "ABSENT")));
    if (data)
        xoom_v026_blob("NVRAM_SOURCE", data, data_len);
""" + anchor,1)

    # Capture actual callback outcome and returned firmware file bytes;
    # file identity comes from the immediately preceding REQUEST log.
    anchor = '\tbrcmf_dbg(TRACE, "firmware %s %sfound\\n", cur->path, fw ? "" : "not ");'
    require_once(s,anchor,"firmware callback")
    s=s.replace(anchor,anchor+r"""
    pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_RESULT canonical=%s slot=%u present=%d\n",
            (unsigned long long)ktime_get_ns(), cur->path,
            fwctx->curpos, !!fw);
    if (fw && fw->data)
        xoom_v026_blob("FILE_RETURNED", fw->data, fw->size);
""",1)

    # Mark actual requested paths: first asynchronous variant,
    # subsequent variants, generic fallback; and synchronous attempts.
    anchor = """\tif (alt_path) {
\t\tfwctx->board_index++;"""
    require_once(s,anchor,"initial alternate request")
    s=s.replace(anchor,anchor+r"""
        pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_ASYNC_BOARD path=%s\n",
                (unsigned long long)ktime_get_ns(), alt_path);
""",1)
    anchor = """\t} else {
\t\tret = request_firmware_nowait(THIS_MODULE, true, first->path,"""
    require_once(s,anchor,"first async generic request")
    s=s.replace(anchor, """\t} else {
        pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_ASYNC_GENERIC path=%s\\n",
                (unsigned long long)ktime_get_ns(), first->path);
\t\tret = request_firmware_nowait(THIS_MODULE, true, first->path,""",1)
    anchor = """\t\tret = firmware_request_nowait_nowarn(THIS_MODULE,
\t\t\t\t\t\t     alt_path, fwctx->dev,"""
    # Exactly twice in this tree: first request and subsequent retry.
    if s.count(anchor)!=2:
        raise RuntimeError(f"unexpected async request locations: {s.count(anchor)}")
    # Source order: retry function precedes first-request function. Instrument the first occurrence only.
    a=s.index(anchor);b=s.index(anchor,a+len(anchor))
    s=s[:a]+"""        pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_ASYNC_RETRY path=%s\\n",
                (unsigned long long)ktime_get_ns(), alt_path);
"""+s[a:]
    anchor = """fallback:
\t/* Fall back to canonical path if board firmware not found */
\tret = request_firmware_nowait(THIS_MODULE, true, first->path,"""
    require_once(s,anchor,"async fallback")
    s=s.replace(anchor, """fallback:
\t/* Fall back to canonical path if board firmware not found */
    pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_ASYNC_FALLBACK path=%s\\n",
            (unsigned long long)ktime_get_ns(), first->path);
\tret = request_firmware_nowait(THIS_MODULE, true, first->path,""",1)

    anchor = """\t\tret = firmware_request_nowarn(fw, alt_path, fwctx->dev);
\t\tkfree(alt_path);"""
    require_once(s,anchor,"sync board request")
    s=s.replace(anchor, """        pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_SYNC_BOARD path=%s\\n",
                (unsigned long long)ktime_get_ns(), alt_path);
\t\tret = firmware_request_nowarn(fw, alt_path, fwctx->dev);
\t\tkfree(alt_path);""",1)
    anchor = """fallback:
\tif (cur->flags & BRCMF_FW_REQF_OPTIONAL)
\t\treturn firmware_request_nowarn(fw, cur->path, fwctx->dev);

\treturn request_firmware(fw, cur->path, fwctx->dev);"""
    require_once(s,anchor,"sync generic fallback")
    s=s.replace(anchor, """fallback:
    pr_info("XOOM_PROV026 t_ns=%llu phase=REQUEST_SYNC_FALLBACK path=%s\\n",
            (unsigned long long)ktime_get_ns(), cur->path);
\tif (cur->flags & BRCMF_FW_REQF_OPTIONAL)
\t\treturn firmware_request_nowarn(fw, cur->path, fwctx->dev);

\treturn request_firmware(fw, cur->path, fwctx->dev);""",1)
    return s

def make_sdio(original: str) -> str:
    # The previously hardware-qualified read-only v024 patch is first applied
    # externally. Additional log timestamps bracket the F2-ready wait.
    s = original
    s = inject(s, "#include <linux/clk.h>\n",
               "#include <linux/ktime.h>\n", "SDIO timestamp include")
    anchor = "\terr = sdio_enable_func(sdiod->func2);"
    require_once(s, anchor, "SDIO F2 enable")
    s = s.replace(anchor, (
        '    pr_info("XOOM_PROV026 t_ns=%llu phase=F2_ENABLE_BEFORE\\n",\n'
        '            (unsigned long long)ktime_get_ns());\n'
        +anchor+
        '\n    pr_info("XOOM_PROV026 t_ns=%llu phase=F2_ENABLE_AFTER result=%d\\n",\n'
        '            (unsigned long long)ktime_get_ns(), err);'
    ), 1)
    return s

def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    assert PATCH.exists(), f"missing pretested v024 patch: {PATCH}"
    originals = {SDIO: SDIO.read_bytes(), FW: FW.read_bytes()}
    if sha256(originals[SDIO]).hexdigest() != EXPECTED_SDIO_SHA256:
        raise RuntimeError("SDIO source differs from known original: stop")
    if sha256(originals[FW]).hexdigest()!=EXPECTED_FW_SHA256:
        raise RuntimeError("firmware.c differs from known original: stop")
    env = dict(os.environ, ARCH="arm",
        CROSS_COMPILE=str(TOOLCHAIN / "arm-none-linux-gnueabihf-"))
    try:
        subprocess.run(["git","apply","--check","--whitespace=nowarn",str(PATCH)],
                       cwd=KERNEL,check=True)
        subprocess.run(["git","apply","--whitespace=nowarn",str(PATCH)],
                       cwd=KERNEL,check=True)
        fwnew = make_fw(originals[FW].decode("utf8"))
        snew = make_sdio(SDIO.read_text("utf8"))
        FW.write_text(fwnew,encoding="utf8")
        SDIO.write_text(snew,encoding="utf8")
        with (STAGE / "compile.log").open("wb") as log:
            process = subprocess.run(["make","-j2","O="+str(OUTPUT),
                  "drivers/net/wireless/broadcom/brcm80211/brcmutil/brcmutil.ko",
                  "drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"],
                  cwd=KERNEL,env=env,stdout=log,stderr=subprocess.STDOUT)
        if process.returncode:
            print((STAGE/"compile.log").read_text(errors="replace")[-11000:])
            raise RuntimeError("v026 build failed; kernel source restored")
    finally:
        for source, original in originals.items():
            source.write_bytes(original)
            if source.read_bytes()!=original:
                raise RuntimeError("CRITICAL: kernel source restoration failed: "+str(source))
    binary=OUTPUT/"drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko"
    target=STAGE/"brcmfmac-v026-provenance-readonly.ko"
    shutil.copyfile(binary,target)
    if target.read_bytes()[:4]!=b"\x7fELF":
        raise RuntimeError("Built file not ARM ELF")
    print("BUILT_BYTES",target.stat().st_size)
    print("BUILT_SHA256",sha256(target.read_bytes()).hexdigest())
    print("NO_XOOM_DEVICE_ACCESS_OR_FLASHING")
if __name__=="__main__":
    main()
