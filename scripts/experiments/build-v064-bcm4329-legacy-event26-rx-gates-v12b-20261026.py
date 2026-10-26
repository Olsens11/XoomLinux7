#!/usr/bin/env python3
"""v12b: BCM4329 event path stage counters, layered on physically verified v12a.

Instrument driver RX event-gating, fweh queue and worker without logging any
payload/SSID/BSSID/MAC, changing packet disposition, firmware masks, scan
request, timer or scan_done. Exact-ABI build only; no physical RF in this file.
Temporarily overlays fweh.h and fweh.c in addition to v12a's cfg80211.c,
then restores every modified source and compiled working artifact.
"""
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).with_name(
    "build-v064-bcm4329-legacy-event26-mask-readback-v12a-20261026.py"
)
spec = importlib.util.spec_from_file_location("mz600_v12a_builder", P)
v12a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v12a)
builder = v12a.builder
builder.WORK = builder.BASE / "v064-legacy-event26-rx-gates-v12b-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-event26-rx-gates-v12b.ko"
builder.PATCH_PATH = builder.WORK / "0012b-lab-only-bcm4329-event26-rx-stages.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
PREV_PATCH = builder.make_patch
AUX = (
    Path("drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h"),
    Path("drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c"),
)

STAGES = [
    "skb", "link", "length", "subtype", "oui", "user",
    "raw26", "proc26", "registered26", "size26",
    "queued26", "worker26", "handler26",
]


def hashbytes(blob):
    return hashlib.sha256(blob).hexdigest()


def patch_cfg(original):
    c = PREV_PATCH(original)
    a = '\tbrcmf_info("MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0\\n");'
    c = builder.exactly_one(c, a,
        'brcmf_v12b_event_report(ifp->drvr, "start");\n\t' + a,
        "V12B_PRE_SCAN_EVENT_COUNTS")
    a = '\t\tbrcmf_info("MZ600_LEGACY_SCAN_LAB_RESULT51 rc=%d bytes=%u version=%u bss_count=%u envelope_ok=%u\\n",'
    c = builder.exactly_one(c, a,
        '\t\tbrcmf_v12b_event_report(ifp->drvr, "timeout");\n' + a,
        "V12B_TIMEOUT_EVENT_COUNTS")
    return c


def patch_header(original):
    c = original
    marker = "void brcmf_fweh_p2pdev_setup(struct brcmf_if *ifp, bool ongoing);\n"
    block = """/* MZ600 v12b LAB ONLY: sanitized stage counts, no frame contents. */
enum brcmf_v12b_event_stage {
    MZ600_RX_SKB, MZ600_RX_LINK, MZ600_RX_LENGTH, MZ600_RX_SUBTYPE,
    MZ600_RX_OUI, MZ600_RX_USER, MZ600_RX_RAW26, MZ600_RX_PROC26,
    MZ600_RX_REGISTERED26, MZ600_RX_SIZE26, MZ600_RX_QUEUED26,
    MZ600_RX_WORKER26, MZ600_RX_HANDLER26, MZ600_RX_STAGE_COUNT
};
void brcmf_v12b_event_note(struct brcmf_pub *drvr,
                            enum brcmf_v12b_event_stage stage);
void brcmf_v12b_event_report(struct brcmf_pub *drvr, const char *phase);
"""
    c = builder.exactly_one(c, marker, marker + block, "V12B_STAGE_HELPERS")
    blocks = [
        ("\t/* only process events when protocol matches */\n",
         "\tbrcmf_v12b_event_note(drvr, MZ600_RX_SKB);\n\t/* only process events when protocol matches */\n",
         "V12B_SKB_ENTER"),
        ("\tif ((skb->len + ETH_HLEN) < sizeof(*event_packet))\n",
         "\tbrcmf_v12b_event_note(drvr, MZ600_RX_LINK);\n"
         "\tif ((skb->len + ETH_HLEN) < sizeof(*event_packet))\n",
         "V12B_LINK_MATCH"),
        ("\tevent_packet = (struct brcmf_event *)skb_mac_header(skb);\n",
         "\tbrcmf_v12b_event_note(drvr, MZ600_RX_LENGTH);\n"
         "\tevent_packet = (struct brcmf_event *)skb_mac_header(skb);\n",
         "V12B_LENGTH_MATCH"),
        ("\t/* check for BRCM oui match */\n",
         "\tbrcmf_v12b_event_note(drvr, MZ600_RX_SUBTYPE);\n"
         "\t/* check for BRCM oui match */\n",
         "V12B_SUBTYPE_MATCH"),
        ("\t/* final match on usr_subtype */\n",
         "\tbrcmf_v12b_event_note(drvr, MZ600_RX_OUI);\n"
         "\t/* final match on usr_subtype */\n",
         "V12B_OUI_MATCH"),
        ("\tbrcmf_fweh_process_event(drvr, event_packet, skb->len + ETH_HLEN, gfp);\n",
         "\tbrcmf_v12b_event_note(drvr, MZ600_RX_USER);\n"
         "\tif (get_unaligned_be32(&event_packet->msg.event_type) ==\n"
         "\t    BRCMF_E_SCAN_COMPLETE)\n"
         "\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_RAW26);\n"
         "\tbrcmf_fweh_process_event(drvr, event_packet, skb->len + ETH_HLEN, gfp);\n",
         "V12B_RAW26_GATED"),
    ]
    for a, b, tag in blocks:
        c = builder.exactly_one(c, a, b, tag)
    return c


def patch_fweh(original):
    c = original
    marker = '#include "fwvid.h"\n'
    impl = """
/* Lab-only process-global counts; only BCM4329 executes increments.
 * All readings are atomic; no event payload or identifiers collected. */
static atomic_t mz600_v12b_event_counts[MZ600_RX_STAGE_COUNT];

void brcmf_v12b_event_note(struct brcmf_pub *drvr,
                           enum brcmf_v12b_event_stage stage)
{
    if (drvr && drvr->bus_if &&
        drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID &&
        stage >= 0 && stage < MZ600_RX_STAGE_COUNT)
        atomic_inc(&mz600_v12b_event_counts[stage]);
}

void brcmf_v12b_event_report(struct brcmf_pub *drvr, const char *phase)
{
    if (!drvr || !drvr->bus_if ||
        drvr->bus_if->chip != BRCM_CC_4329_CHIP_ID)
        return;
    brcmf_info("MZ600_V12B_EVENT_RX stage=%s skb=%d link=%d length=%d subtype=%d oui=%d user=%d raw26=%d proc26=%d registered26=%d size26=%d queued26=%d worker26=%d handler26=%d\\n",
        phase,
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_SKB]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_LINK]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_LENGTH]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_SUBTYPE]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_OUI]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_USER]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_RAW26]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_PROC26]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_REGISTERED26]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_SIZE26]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_QUEUED26]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_WORKER26]),
        atomic_read(&mz600_v12b_event_counts[MZ600_RX_HANDLER26]));
}
"""
    c = builder.exactly_one(c, marker, marker + impl, "V12B_IMPLEMENT_SANITIZED_COUNTS")
    a = '\tfwevt_idx = get_unaligned_be32(&event_packet->msg.event_type);\n'
    c = builder.exactly_one(c, a, a +
        '\tif (fwevt_idx == BRCMF_E_SCAN_COMPLETE)\n'
        '\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_PROC26);\n',
        "V12B_PROCESS_ENTER")
    a = '\tif (datalen > BRCMF_DCMD_MAXLEN ||\n'
    c = builder.exactly_one(c, a,
        '\tif (fwevt_idx == BRCMF_E_SCAN_COMPLETE)\n'
        '\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_REGISTERED26);\n' + a,
        "V12B_HANDLER_ACCEPT")
    a = '\tevent = kzalloc_flex(*event, data, datalen, gfp);\n'
    c = builder.exactly_one(c, a,
        '\tif (fwevt_idx == BRCMF_E_SCAN_COMPLETE)\n'
        '\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_SIZE26);\n' + a,
        "V12B_LENGTH_ACCEPT")
    a = '\tbrcmf_fweh_queue_event(fweh, event);\n'
    c = builder.exactly_one(c, a,
        '\tif (fwevt_idx == BRCMF_E_SCAN_COMPLETE)\n'
        '\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_QUEUED26);\n' + a,
        "V12B_QUEUE_EVENT")
    a = '\t\tbrcmf_fweh_map_fwevt_code(fweh, event->code, &code);\n'
    c = builder.exactly_one(c, a,
        '\t\tif (event->code == BRCMF_E_SCAN_COMPLETE)\n'
        '\t\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_WORKER26);\n' + a,
        "V12B_WORKER_RECEIVE")
    a = '\t\terr = brcmf_fweh_call_event_handler(drvr, ifp, event->code,\n'
    c = builder.exactly_one(c, a,
        '\t\tif (event->code == BRCMF_E_SCAN_COMPLETE)\n'
        '\t\t\tbrcmf_v12b_event_note(drvr, MZ600_RX_HANDLER26);\n' + a,
        "V12B_HANDLER_INVOKE")
    return c


builder.make_patch = patch_cfg


def main():
    if builder.WORK.exists():
        raise RuntimeError("refuse to overwrite existing v12b one-shot build")
    sources = {p: (builder.SOURCE / p).read_bytes() for p in AUX}
    modifications = {
        AUX[0]: patch_header(sources[AUX[0]].decode("utf-8")),
        AUX[1]: patch_fweh(sources[AUX[1]].decode("utf-8")),
    }
    for p in AUX:
        if "MZ600_V12B_EVENT_RX" in sources[p].decode("utf-8"):
            raise RuntimeError("original source already contains v12b")
    # Protect preexisting build artifacts, including .o/.cmd stamps, so
    # the next baseline build cannot accidentally reuse instrumented objects.
    d = Path("drivers/net/wireless/broadcom/brcm80211/brcmfmac")
    snapshot = {}
    for root in (builder.SOURCE / d, builder.OUTPUT / d):
        for f in root.iterdir():
            if f.is_file() and (
                f.suffix in {".o", ".ko", ".mod", ".cmd"}
                or f.name.endswith(".mod.c")
                or f.name.startswith(".") and f.name.endswith(".cmd")
            ):
                snapshot[f] = f.read_bytes()
    success = False
    try:
        for rel, code in modifications.items():
            (builder.SOURCE / rel).write_text(code)
        result = builder.main()  # v12a's verified input ABI and cfg restore
        if result != 0:
            raise RuntimeError("v12a ABI builder returned failure")
        patch_extra = "".join(
            "".join(difflib.unified_diff(
                sources[p].decode("utf-8").splitlines(keepends=True),
                modifications[p].splitlines(keepends=True),
                fromfile="a/" + p.as_posix(), tofile="b/" + p.as_posix(), n=4
            )) for p in AUX
        )
        with builder.PATCH_PATH.open("a") as out:
            out.write(patch_extra)
        elf = builder.TARGET.read_bytes()
        if b"MZ600_V12B_EVENT_RX" not in elf:
            raise RuntimeError("new ELF missing event RX path marker")
        report = json.loads(builder.REPORT.read_text())
        report.update({
            "result": "V12B_BCM4329_EVENT_RX_STAGE_OBSERVATION_ONLY_EXACT_ABI_BUILT",
            "module_sha256": hashbytes(elf),
            "module_bytes": len(elf),
            "source_patch_sha256": hashbytes(builder.PATCH_PATH.read_bytes()),
            "no_rerun_previous_physical_experiments": True,
            "event_delivery_unchanged": True,
            "scan_completion_lifecycle_unchanged": True,
            "physical_test_performed": False,
            "firmware_mask_changed": False,
            "captured_data": "sanitized numeric event receive stage counts only",
            "upstream_ready": False,
        })
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("V12B_EVENT_RX_STAGE_OBSERVATION_ONLY_BUILD_PASS", flush=True)
        success = True
        return 0
    finally:
        for p, original in sources.items():
            (builder.SOURCE / p).write_bytes(original)
        for root in (builder.SOURCE / d, builder.OUTPUT / d):
            for f in root.iterdir():
                if f.is_file() and (
                    f.suffix in {".o", ".ko", ".mod", ".cmd"}
                    or f.name.endswith(".mod.c")
                    or f.name.startswith(".") and f.name.endswith(".cmd")
                ) and f not in snapshot:
                    f.unlink()
        for f, original in snapshot.items():
            f.write_bytes(original)
        for p, original in sources.items():
            if (builder.SOURCE / p).read_bytes() != original:
                raise RuntimeError("V12B_AUX_SOURCE_RESTORE_FAILED " + str(p))
        for f, original in snapshot.items():
            if f.read_bytes() != original:
                raise RuntimeError("V12B_OBJECT_RESTORE_FAILED " + str(f))
        print("V12B_ALL_AUX_SOURCE_AND_MODULE_OBJECTS_RESTORED_VERIFIED",
              "SUCCESS" if success else "FAILED", flush=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("V12B_OFFLINE_BUILD_ABORT:", str(exc), file=sys.stderr)
        sys.exit(2)
