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
               "#include <linux/ktime.h>\n", "firmware include")
    s = inject(s, "static void *brcmf_fw_nvram_strip(",
               FW_HELPERS + "\n", "NVRAM parser helper")
    # Track exactly which asynchronous file path was requested (as opposed
    # to printing a canonical path and assuming it was actually chosen).
    marker = "\tunsigned int board_index;\n"
    require_once(s, marker, "firmware request context")
    s = s.replace(marker, marker +
                  "\tchar xoom_v026_request_path[BRCMF_FW_NAME_LEN];\n", 1)
    marker = "\tif (alt_path) {\n\t\tfwctx->board_index++;\n"
    require_once(s, marker, "initial board candidate")
    s = s.replace(marker, marker +
                  "\t\tstrscpy(fwctx->xoom_v026_request_path, alt_path,\n"
                  "\t\t\tsizeof(fwctx->xoom_v026_request_path));\n", 1)
    marker = "fallback:\n\t/* Fall back to canonical path if board firmware not found */\n"
    require_once(s, marker, "first firmware fallback")
    s = s.replace(marker, marker +
                  "\tstrscpy(fwctx->xoom_v026_request_path, first->path,\n"
                  "\t\tsizeof(fwctx->xoom_v026_request_path));\n", 1)
    marker = "\t\tret = firmware_request_nowait_nowarn(THIS_MODULE,\n"
    # First and subsequent retry both include this anchor. Retry branch uses
    # the unique following block; choose a specific enclosing occurrence.
    retry = """\t\tboard_type = fwctx->req->board_types[fwctx->board_index++];
\t\tif (!board_type)
\t\t\tgoto fallback;
\t\talt_path = brcm_alt_fw_path(first->path, board_type);
\t\tif (!alt_path)
\t\t\tgoto fallback;

\t\tret = firmware_request_nowait_nowarn"""
    require_once(s, retry, "board retry")
    s = s.replace(retry, retry.replace(
        "\n\t\tret = firmware_request_nowait_nowarn",
        "\n\t\tstrscpy(fwctx->xoom_v026_request_path, alt_path,\n"
        "\t\t\tsizeof(fwctx->xoom_v026_request_path));\n"
        "\t\tret = firmware_request_nowait_nowarn"), 1)
    # The asynchronous callback may receive either a board-specific blob or
    # the canonical fallback; do not conflate "requested" with "opened".
    anchor = """static void brcmf_fw_request_done(const struct firmware *fw, void *ctx)
{
\tstruct brcmf_fw *fwctx = ctx;"""
    require_once(s, anchor, "async completion")
    s = s.replace(anchor, anchor + r'''
    pr_info("XOOM_PROV026 t_ns=%llu request_done path=%s found=%d slot=%u\n",
            (unsigned long long)ktime_get_ns(),
            fwctx->xoom_v026_request_path, !!fw, fwctx->curpos);
    if (fw && fw->data)
        xoom_v026_blob("ASYNC_FILE", fw->data, fw->size);
''', 1)
    # Subsequent blobs use the synchronous helper. Instrument at the precise
    # site of success to log the selected board-specific or fallback path.
    anchor = """\t\tret = firmware_request_nowarn(fw, alt_path, fwctx->dev);
\t\tkfree(alt_path);
\t\tif (ret == 0)
\t\t\treturn ret;"""
    require_once(s, anchor, "sync board variant")
    s = s.replace(anchor, """\t\tret = firmware_request_nowarn(fw, alt_path, fwctx->dev);
        if (!ret && *fw) {
            pr_info("XOOM_PROV026 t_ns=%llu sync_path=%s slot=%u\n",
                    (unsigned long long)ktime_get_ns(),
                    alt_path, fwctx->curpos);
            xoom_v026_blob("SYNC_BOARD", (*fw)->data, (*fw)->size);
        }
\t\tkfree(alt_path);
\t\tif (ret == 0)
\t\t\treturn ret;""", 1)
    anchor = """fallback:
\tif (cur->flags & BRCMF_FW_REQF_OPTIONAL)
\t\treturn firmware_request_nowarn(fw, cur->path, fwctx->dev);

\treturn request_firmware(fw, cur->path, fwctx->dev);"""
    require_once(s, anchor, "sync fallback")
    s = s.replace(anchor, """fallback:
    {
        int xoom_rc;
        if (cur->flags & BRCMF_FW_REQF_OPTIONAL)
            xoom_rc = firmware_request_nowarn(fw, cur->path, fwctx->dev);
        else
            xoom_rc = request_firmware(fw, cur->path, fwctx->dev);
        pr_info("XOOM_PROV026 t_ns=%llu sync_fallback_path=%s slot=%u rc=%d\n",
                (unsigned long long)ktime_get_ns(), cur->path,
                fwctx->curpos, xoom_rc);
        if (!xoom_rc && *fw)
            xoom_v026_blob("SYNC_FALLBACK", (*fw)->data, (*fw)->size);
        return xoom_rc;
    }""", 1)
    # Trace the actual runtime packed bytes, not just the .txt file.
    anchor = """\tcur->nv_data.data = nvram;
\tcur->nv_data.len = nvram_length;"""
    require_once(s, anchor, "packed NVRAM handoff")
    s = s.replace(anchor, anchor + r'''
    pr_info("XOOM_PROV026 t_ns=%llu nvram_pack_valid=%d\n",
            (unsigned long long)ktime_get_ns(), !!nvram);
    if (nvram && nvram_length)
        xoom_v026_blob("NVRAM_PACKED", nvram, nvram_length);
''', 1)
    # The MAC is never printed or hashed; only whether the platform source
    # was available for the NVRAM parser.
    anchor = """\tif (eth_platform_get_mac_address(dev, mac) == 0)
\t\tnvp.strip_mac = true;"""
    require_once(s, anchor, "platform MAC source")
    s = s.replace(anchor, """\tif (eth_platform_get_mac_address(dev, mac) == 0)
        nvp.strip_mac = true;
    pr_info("XOOM_PROV026 t_ns=%llu platform_mac_available=%d\n",
            (unsigned long long)ktime_get_ns(), nvp.strip_mac);
""", 1)
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
    for source in originals:
        status = subprocess.run(["git", "diff", "--quiet", "--", str(source)],
                                cwd=KERNEL)
        if status.returncode:
            raise RuntimeError("Refusing to build on dirty kernel source " + str(source))
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
