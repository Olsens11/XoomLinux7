# MZ604 I0 recovery host-controller tooling — mock verification, 2026-10-30

**Classification: HOST/OFFLINE MOCK + FILE INTEGRITY, NOT PHYSICAL TWRP OR DEBIAN RUNTIME.** The MZ604 is still running older Linux with USB COM10 at login; ADB device not enumerated during preparation. The owner will boot MZ604 into TWRP when physically present. This checkpoint supplements, not replaces, the [Surface V2 offline deployment bundle checkpoint](MZ604_I0_SURFACE_V2_DEPLOYMENT_OFFLINE_READY_2026-10-30.md).

## Prepared tools (private Surface host)

All located in `C:\Users\olsen\xoom-linux-rom\`, with exact known hashes as of this entry:
- `MZ604-TWRP-I0-SAFE-GATE-20261030.py` 6,087B, SHA256 `157693db5f691d559a2016ee8cfa3517942799cae1e2faaaae29399a3cf053f2`. Detect exact MZ604/TWRP/unique ADB identity, mounted p10 `/data`, live rootfs size/SHA and Surface manifest; `backup` pulls a full **actual live** 2.15GiB rootfs to a new private Surface backup directory, compares source SHA, saves a receipt. No device mutations.
- `MZ604-TWRP-I0-STAGE-AND-PROMOTE-20261030.py` 7,760B, SHA256 `895fc3eb0c39b94824237b85369739eb1ffc6434493f13ffe1dc39c7d5bf0482`. Independent `check` / `stage` / `promote` phases requiring previously verified live backup receipt; only modifies newly named p10 stage files and finally, when explicitly requested, canonical root image via non-overwriting renames. Never reboots, writes bootloader or alters p6/p7/p8. Requires full raw-stage SHA before promotion. **Actual TWRP capability for gzip/mv still needs physical validation.**
- `MZ604-COM10-I0-ACCEPTANCE-20261030.py` 2,506B, SHA256 `e0313525e2a8ec36dabd4b39f6e4dada2a2dac8c9736d1af3bf699ad80969a2b`. Read-only COM10 `id`, `sudo -n id`, `uname -r` and loop device check after returning to Linux. Python syntax PASS only; no new device serial probe executed.
- Two corresponding offline mocked test scripts SHA256 `fc07ebc9f4f311d1904068d6704e0a9044607ad8e48b023ce943281a5f61e463` (safe gate) and `34cd7edbf7beb57e751c0ae34a6c72e82fb7bba914c8b6195ecce2b69f5c5dea` (install).

## Offline results

- **Safety-gate mock PASS:** known Wingray + TWRP 3.1.1-0 + mounted p10 + correct size/SHA accepted, wrong `stingray` model rejected, unmounted `/data` rejected, malformed SHA output rejected. No mock ADB touched real device.
- **Stage/promote mock PASS:** compressed staging simulated without changing original; promotion preserved old root and installed new SHA; corrupt candidate rejected without rename; simulated second-rename failure restored original canonical name. No real ADB call or partition write.
- Stage script `python -m py_compile` PASS, `--help` displays exactly `check|stage|promote`; missing backup receipt STOP tested. An incidental Python invalid escape warning in the usage docstring did not alter execution; consider a cosmetic fix later, not a hardware blocker.
- Surface V2 manifest SHA256 rechecked `331f36e4340ba14f78c9217f8e66cd1175c907dfacddff202c33b3161848ddb6`; prior independent gzip-stream root/p8/selector SHA validation and 114 kernel modules PASS.
- **NO TWRP physical test**, no authenticated Linux shell, no recovery reboot/selector/kexec, no MZ604 BCM4329 firmware/SDIO/scan. These remain open.

## Next action

When owner enters TWRP, follow the new [one-page entry + full gated execution/rollback procedure](../rfc/bcm4329-upstream-first/I0_TWRP_EXECUTION_AND_RECOVERY_CHECKLIST_2026-10-30.md), beginning with read-only `inspect` and independently SHA-verified `backup`. Then separate `check`, `stage`, `promote`, and Linux acceptance. Do not deploy optional p8 selector as part of I0. Document each later physical observation with a new timestamped record, do not rewrite this prior offline checkpoint.
