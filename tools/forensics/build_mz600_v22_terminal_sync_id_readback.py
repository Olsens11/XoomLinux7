#!/usr/bin/env python3
"""V22 diagnostic only: log numeric terminal ESCAN transaction envelope.

Inherits the physically proven, default-off V21 terminal-owner module. Adds
read-only decoding of the 12-byte fixed escan result on real Event69 SUCCESS
after payload length validation. Does NOT modify firmware or scan sync IDs.
Restores original source/module after exact-ABI build, just like V21.
"""
import importlib.util
import json
from pathlib import Path

PREVIOUS = Path(__file__).with_name("build_mz600_v21_terminal_owner_probe.py")
spec = importlib.util.spec_from_file_location("mz600_v21_builder", PREVIOUS)
v21 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v21)

v21.base.RESULT = v21.base.ROOT / "v064-2012-oem-escan-v22-20261027"
old_instrument = v21.base.instrument_fweh

def instrument_event_with_sync(original):
    c = old_instrument(original).replace("MZ600_V21_", "MZ600_V22_")
    anchor = '\t\temsg.bsscfgidx = emsg_be->bsscfgidx;'
    assert c.count(anchor) == 1
    insertion = r'''
        /*
         * V22 diagnosis: the fixed ESCAN result is exactly 12 bytes:
         * u32 length, u32 version, u16 sync_id, u16 bss_count.
         * Only numeric, no BSS identities. Never change payload or route.
         * Access as unaligned little-endian bytes from the queued data.
         */
        if (drvr->bus_if->chip == BRCM_CC_4329_CHIP_ID &&
            event->code == BRCMF_E_ESCAN_RESULT &&
            emsg.version == 2 &&
            emsg.status == BRCMF_E_STATUS_SUCCESS) {
            if (event->datalen >= 12) {
                const u8 *p = event->data;
                brcmf_info("MZ600_V22_TERMINAL_SYNC bytes=%u buflen=%u escan_version=%u sync_id=%u bss_count=%u expected_request_sync_id=4660\n",
                           event->datalen,
                           get_unaligned_le32(p),
                           get_unaligned_le32(p + 4),
                           get_unaligned_le16(p + 8),
                           get_unaligned_le16(p + 10));
            } else {
                brcmf_info("MZ600_V22_TERMINAL_SYNC_UNDERSIZED bytes=%u\n",
                           event->datalen);
            }
        }
'''
    # Because insertion is a raw Python string, its C newline escapes remain
    # literal \n, rather than accidentally breaking C strings.
    c = c.replace(anchor, anchor + "\n" + insertion)
    return c

v21.base.instrument_fweh = instrument_event_with_sync

def main():
    v21.main()
    directory = v21.base.RESULT
    v21name = directory / "brcmfmac-2012-escan-terminal-owner-v21.ko"
    out = directory / "brcmfmac-2012-escan-terminal-sync-v22.ko"
    if out.exists():
        raise RuntimeError("Refuse overwrite of V22 artifact")
    v21name.rename(out)
    report = directory / "offline-build-result.json"
    data = json.loads(report.read_text())
    data.update({
        "test": "V22_NUMERIC_TERMINAL_SYNC_ID_READBACK_NO_FIRMWARE_CHANGES",
        "artifact_name": out.name,
        "originating_v21": "TERMINAL_OWNER_DEFAULT_OFF",
        "test_switch": "mz600_terminal_owner=0|1",
        "expected_request_sync_id": 4660,
        "firmware_sync_id_observed": "NOT_YET_PHYSICALLY_TESTED",
        "modifies_firmware_sync_id": False,
        "on_device_test": False,
        "production_patch": False,
    })
    report.write_text(json.dumps(data, indent=2) + "\n")
    print("V22_OFFLINE_BUILT_NO_RF", out)

if __name__ == "__main__":
    main()
