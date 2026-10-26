#!/usr/bin/env python3
"""v12a: read-only firmware event-26 mask probe layered onto verified v11.

Source-only investigative experiment. Does not change RF request, result parser,
scan completion, timeout, abort, cfg80211 ownership, or persistent modules.
Use an owner-approved separate guarded RAM experiment only after an exact-ABI
build and clean restoration checks. This script must not be mistaken for the
event-driven lifecycle implementation.
"""
import importlib.util
import json
from pathlib import Path

P = Path(__file__).with_name(
    "build-v064-bcm4329-legacy-v108-cfg80211-inform-v11-20261026.py"
)
spec = importlib.util.spec_from_file_location("mz600_v11_builder", P)
v11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v11)

builder = v11.builder
builder.WORK = builder.BASE / "v064-legacy-event26-mask-readback-v12a-20261026"
builder.TARGET = builder.WORK / "brcmfmac-legacy-event26-mask-readback-v12a.ko"
builder.PATCH_PATH = builder.WORK / "0012a-lab-only-bcm4329-event26-mask-readback.patch"
builder.REPORT = builder.WORK / "offline-build-result.json"
previous = builder.make_patch


def patch(original):
    code = previous(original)
    # Observe event_msgs after fweh activation, on the legacy-only path,
    # immediately before WLC_SCAN ioctl50. Do not mutate event configuration.
    anchor = (
        '\tbrcmf_info("MZ600_LEGACY_SCAN_LAB_START passive=1 freq=5180 channels=1 probes=0\\n");\n'
    )
    probe = r'''
	/* Investigation only: the event26 handler was registered before
	 * brcmf_fweh_activate_events(). Check the locally requested bit and
	 * read back what old firmware reports; never SET event_msgs here.
	 * Failed GET must not alter the already proven passive scan. */
	{
		struct brcmf_fweh_info *fweh = ifp->drvr->fweh;
		u8 *fw_mask = NULL;
		u32 mask_len = 0;
		int rc = -EINVAL, host_bit = -1, fw_bit = -1;
		bool registered = false, has_event_map = false;
		const u32 byte = BRCMF_E_SCAN_COMPLETE / 8;
		const u8 bit = BIT(BRCMF_E_SCAN_COMPLETE % 8);

		if (fweh) {
			mask_len = fweh->event_mask_len;
			has_event_map = !!fweh->event_map;
			if (fweh->num_event_codes > BRCMF_E_SCAN_COMPLETE) {
				registered = !!fweh->evt_handler[BRCMF_E_SCAN_COMPLETE];
				if (fweh->event_mask && mask_len > byte)
					host_bit = !!(fweh->event_mask[byte] & bit);
			}
			if (registered && mask_len > byte &&
			    mask_len <= BRCMF_DCMD_MEDLEN) {
				fw_mask = kzalloc(mask_len, GFP_KERNEL);
				if (fw_mask) {
					rc = brcmf_fil_iovar_data_get(
						ifp, "event_msgs", fw_mask, mask_len);
					if (!rc)
						fw_bit = !!(fw_mask[byte] & bit);
				} else {
					rc = -ENOMEM;
				}
			}
		}
		/* Numeric only. If has_event_map, raw bit26 interpretation
		 * requires separate vendor-map validation. */
		brcmf_info("MZ600_LEGACY_EVENT26_MASK_READBACK rc=%d len=%u registered=%u driver_bit=%d fw_bit=%d map=%u\n",
			   rc, mask_len, registered, host_bit, fw_bit,
			   has_event_map);
		kfree(fw_mask);
	}
'''
    return builder.exactly_one(
        code, anchor, probe + anchor, "V12A_LEGACY_READ_ONLY_EVENT26_MASK"
    )


builder.make_patch = patch

if __name__ == "__main__":
    rc = builder.main()
    if rc == 0:
        raw = builder.TARGET.read_bytes()
        diff = builder.PATCH_PATH.read_text()
        for token in (
            "MZ600_LEGACY_EVENT26_MASK_READBACK",
            'brcmf_fil_iovar_data_get(',
            '"event_msgs"',
            "fweh->event_mask_len",
            "fweh->evt_handler[BRCMF_E_SCAN_COMPLETE]",
            "fw_mask[byte] & bit",
        ):
            if token not in diff:
                raise SystemExit("missing read-only mask audit gate: " + token)
        if b"MZ600_LEGACY_EVENT26_MASK_READBACK" not in raw:
            raise SystemExit("v12a module missing event26 readback marker")
        # No new firmware SET, completion, timer or scan work in this patch.
        if "brcmf_fil_iovar_data_set(" in diff or "cfg80211_scan_done(" in diff:
            raise SystemExit("unexpected completion or firmware setter")
        report = json.loads(builder.REPORT.read_text())
        report.update({
            "result": "V12A_READ_ONLY_EVENT26_MASK_PROBE_EXACT_ABI_BUILT",
            "physical_test_run": False,
            "scan_completion_lifecycle_changed": False,
            "firmware_event_mask_modified": False,
            "upstream_ready": False,
        })
        builder.REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("V12A_LEGACY_MASK_OBSERVATION_ONLY_BUILD_PASS")
    raise SystemExit(rc)
