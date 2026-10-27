# MZ600 V13 — May 2012 OEM BCM4329 firmware candidate, no-scan test staged

Date 2026-10-26. **OFFLINE VERIFICATION AND SURFACE STAGING COMPLETE; NO PHYSICAL XOOM FIRMWARE TEST EXECUTED.** No COM9 commands, no scan, no firmware replacement, no reboot, no installation, no NVRAM/regulatory changes.

## Question

Could later OEM BCM4329 firmware 4.218.248.44 provide both the original Motorola 5GHz band and modern escan/Event69 completion, avoiding an HRI39-specific iscan state machine?

## Known comparison

- Installed generic 4.220.48 firmware: normal Linux7 modern escan returned 19 BSS 2.4GHz; firmware BRCMF_C_GET_BANDLIST and chanspecs showed only 2G despite OEM US/69 NVRAM A/B.
- Original matched HRI39 4.218.248.20: physically exposed 2G+5G, 9 5GHz channels, passively returned 3-4 verified BSS on ch36 via WLC_SCAN ioctl50/RESULTS51, but modern escan returned -52 and scan completion currently uses ~10s fallback.
- Later OEM reference firmware 4.218.248.44 May25 2012, 264140 bytes SHA256 `5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834`, Broadcom `4329b1`: offline string table has `event_msgs`, `iscan`, `escan`, **no `chanspecs`**. The latter may still require preexisting tested channel-enumeration fallback module. Presence of `escan` ASCII is not proof of 5GHz or Event69.

## Read-only verified data and calibration

- Desktop WSL private path `/home/xoomdev/xoom-linux-rom/firmware-reference-v08-OEM-MZ600-private/brcm/brcmfmac4329-sdio.bin`; size/hash confirm the later 2012 image. No private proprietary firmware checked into Git.
- Existing later-reference `.txt` and current working generic `.txt` have equal *all 52 parsed records / 51 unique keys* and zero differences in ordered values, according to `tools/forensics/compare_mz600_oem_firmware_private.py`. Thus first controlled A/B can keep the current SHA-pinned Linux7 calibration untouched. This does not establish that any other device's RF calibration can safely be borrowed.
- Reuse the verified 343200-byte ABI-matched v05 passive-only band fallback module, SHA256 `ff19d91726f406468d6cc9516d43a851f6a7a22d403259094ae376041671db29`. It was previously physically tested under original HRI39 for wiphy 5GHz NO_IR mapping, but not yet under May2012 image.

## New guarded test implementation

- [Linux7/Xoom Bash v13](../../scripts/host/xoom/test-mz600-v13-2012-firmware-bandlist-no-scan-20261026.sh): SHA256 `ed0a130fd584e607da438b7a429d7b24c88ff30d82d36ab6b97df82d02afc9d8`, 120 lines, syntax-pass. Expects candidate firmware and module in `/run` only. Validates uid0, exact installed Linux kernel/p8, original firmware/NVRAM/module SHA, unique one-shot, no WLAN0 and no Broadcom/BT modules or active connection services, FDT identity path, SDIO device; overlays only firmware file via bind mount; loads old ABI-matched diagnostic and WCC once; **no `iw scan`, no link-up, no TX, no association**; captures only fresh post-start firmware bands/legacy valid channel diagnostics, cleans modules and overlay; verifies original SHA and no WLAN. Fails closed if an unexpected overlay hash is present rather than blind unmount. Preflight failures do not unload preexisting modules.
- [Surface COM9 Python guarded owner launcher](../../scripts/host/surface/mz600-v13-2012-firmware-bandlist-owner-once-20261026.py), passed `python -m py_compile` on Surface. Reuses v12b established serial gzip/base64 ACK transfer protocol for **two** SHA-pinned inputs; read-only exact root preflight, unique no-rerun marker and receipt, RAM uploads only, Xoom `bash -n`, one execution, independent file+module post-audit. If COM9 occupied, Python serial open fails without any Xoom change. No automatic scheduling or user interaction spoofing.
- Host-staged Surface directory `C:\Users\olsen\xoom-linux-rom\captures\MZ600-V13-2012-FW-STAGED-20261026`. Contains verified four files: `mz600-v13-oem2012.bin` SHA `5d4b...`, `mz600-v13-passive-only.ko` SHA `ff19...`, `mz600-v13-no-scan.sh` SHA `ed0a...`, `mz600-v13-owner-once.py` SHA `d8fcd82b362e33c1287411ae0d301271cd4f7612a0396c6d88721881c24340c8`. Surface SHA256 and Python syntax independently checked. No attempt marker or result receipt yet.
- Desktop staging used earlier permanent inbound rule `Xoom image transfer - Surface only TCP 43157`, whose RemoteAddress was verified to be `192.168.0.40`. Surface download SHA all matched. Temporary HTTP server's actual Python child PID was explicitly stopped, port 43157 verified no listener; its temporary Desktop staging directory deleted. Original firewall rule left intact.
- Desktop WSL project repository checker PASS 609 entries, 0 errors at script commit; run latest again after this note. The .sh preflight dry-run under WSL correctly refused to run off-device with marker `PREFLIGHT_STOP_NO_STATE_CHANGED rc=10`.

## Why no physical run occurred

Surface COM9 is present, but a separate active user `python.exe` PID 13444 was identified at the time of staging, command `C:\Users\olsen\XoomDev\remote-tools\xoom-v068-bluez4-sdp-reconnect-check.py`. We intentionally did not terminate or interrupt it, and did not race it for COM9. No Xoom-only result is known yet.

## Next owner action

When that existing COM9 Bluetooth/serial session has been intentionally closed, the owner can run from Surface PowerShell:

```powershell
python 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-V13-2012-FW-STAGED-20261026\mz600-v13-owner-once.py'
```

Only once. Read receipt and independent restoration result. If 2012 image advertises 5GHz channels, consider *separate later* bounded ch36 NO_IR passive escan test with proof of Event69 terminal SUCCESS; do not automatically proceed or infer 5GHz from firmware string alone. If candidate fails bandlist, preserve existing HRI39 legacy path/iscan work. Never copy prototype firmware into permanent /lib/firmware, never use new unit MAC or calibration, never force an unsupported band.