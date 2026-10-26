> **STATUS SUPERSEDED:** This file is the *pre-run* owner staging record. The one-shot HAS NOW EXECUTED once, returned `scan_bash_exit_rc=0`, real firmware `event_msgs` GET `rc0 len27 registered1 driver_bit1 fw_bit1 map0`, 3/3 valid legacy BSS in cfg80211/iW and clean independent rollback. Read [actual v12a PHYSICAL PASS checkpoint](MZ600_V12A_EVENT26_FIRMWARE_EVENTMSGS_BIT26_READBACK_PHYSICAL_PASS_2026-10-26.md). **Do not rerun** the v12a launcher or marker. Historical run command below is provenance only.

# MZ600 v12a — owner-operated event26 mask readback prepared on Surface, NOT RUN

**2026-10-26. DESKTOP/SURFACE HOST STAGING & CHECKSUMS PASS; PHYSICAL MZ600 v12a TEST NOT EXECUTED.** The last verified Xoom physical state remains [v11 four cfg80211/iW BSS and independent original firmware/module restoration PASS](MZ600_V11_HRI39_CFG80211_FOUR_BSS_CHANNEL36_PHYSICAL_PASS_2026-10-26.md). This checkpoint extends the [v12a offline exact-ABI build](MZ600_V12A_EVENT26_MASK_READBACK_EXACT_ABI_OFFLINE_BUILD_PASS_2026-10-26.md), not a second RF test.

## What is new, and what is untouched

Read-only event26-mask source probe added to the existing v11 radio scan path; newly staged v12a exact-ABI brcmfmac module remains off the Xoom. On Desktop, module source/module restored and SHA independently matched original. Authenticated Surface SSH alias `devdesktop` reachable by existing credentials without new firewall rules; module copied from exact WSL build into a fresh Desktop Windows temporary staging path and fetched to Surface with ordinary authenticated SCP. Desktop temporary copy **347912 bytes SHA256 `75b6e80436b371accd01faa943a0ea45d100ab0a3faa0349db1bc3cef826c77f`**, Surface copy independently matched exact checksum/size after SCP. No COM9 tool session was opened or any command sent to Xoom; no firmware blobs were copied to GitHub.

In private Surface `C:\Users\olsen\xoom-linux-rom\captures\`, all **new unique v12a** files passed host offline checks:

| Private Surface file | Bytes | SHA256 |
| --- | ---: | --- |
| `MZ600-BRCMFMAC-V12A-EVENT26-20261026.ko` | 347912 | `75b6e80436b371accd01faa943a0ea45d100ab0a3faa0349db1bc3cef826c77f` |
| `MZ600-V12A-USER-ONESHOT-SCAN-20261026.sh` | 8858 | `d094327a1549f9f8ef94a0005e931351990117318d762099a34806639324e266` |
| `MZ600-V064-V12A-EVENT26-RAM-SERIAL-UPLOAD-20261026.py` | 4769 | `ca0b6255d95a4217925a324bc95539f1fb1bae2c1fec96afe83c41f397345ad4` |
| `MZ600-V12A-USER-ONE-SHOT-20261026.py` | 12284 | `977aa775db8ce549b9ecb6862f127a17353dde176b602171586b39026d2520b6` |

Both Python scripts passed actual `python -m py_compile` on Surface without opening COM9; 197-line Bash source independently passed `bash -n` on Desktop WSL exit0 and was copied identically to Surface (sha matched). The branch-local public Bash source is [v12a guarded shell](../../scripts/host/xoom/test-v064-hri39-v12a-event26-mask-readback-one-shot-20261026.sh), GitHub commit `7efb81e9ae8741ba863427e3981176e26bd8eb83`.

### Owner-only physical procedure, when explicitly chosen

1. Ensure Xoom is still the working Debian `/dev/mmcblk0p8` Linux7 root, and no other app/process owns Surface COM9. If connected to the interactive USB serial terminal, detach with `Ctrl+]` *without restarting Xoom*.
2. From the **Surface** PowerShell, operator may run the single new command below. It refuses existing output/transfer receipts. **The assistant has NOT executed this.**

```powershell
python "C:\Users\olsen\xoom-linux-rom\captures\MZ600-V12A-USER-ONE-SHOT-20261026.py"
```

3. Launcher will independently audit original running root, kernel/firmware/NVRAM/module hashes/no active radio, checksum-check the exact four staged input files, upload module **RAM only** with serial ACK, readback its hash/size and the original OEM firmware file in RAM, send guarded script to Xoom first as `bash -n` (syntax only, no RF). It then runs **one** strictly constrained 5180MHz channel36 NO_IR passive `iw scan` under temporary original HRI39 4.218.248.20 / US69 calibration, logging numeric `MZ600_LEGACY_EVENT26_MASK_READBACK rc=... len=... registered=... driver_bit=... fw_bit=... map=...`, while retaining old version108 bounded scan and four-BSS capability. No active probe or association; no SSID/BSSID or IE bytes made public.
4. Guarded Xoom script must unload WCC→brcmfmac→brcmutil and unmount two RAM bind overlays, verify restored original FW/NVRAM/base driver/no-radio, then the **host launcher repeats independent read-only COM9 original-state audit**. It writes new unique private v12a transcript/receipt, not v11 files. The preflight refuses stale/changed baseline and the guard aborts on invalid channel constraints, checksum, syntax, or cleanup problems. Never treat a nonzero scan exit code, no event marker or failed independent audit as success or blindly retry; inspect private receipt/serial state.
5. Expected diagnostic outcomes: `rc=0,registered=1,driver_bit=1,fw_bit=1,map=0` only establishes the firmware **reported event-mask bit enabled**, not that event26 was emitted; unset bit or GET failure needs independent investigation. Whether bit enabled or not, a **normal scan completion still remains unimplemented**. Count0 is not a terminal predicate, and positive count can be partial.

Independent Surface host final preflight recorded all four file SHA/size pins above, python syntax PASS, and **three new v12a output paths absent** (no owner receipt, no RAM transfer receipt, no COM9 private scan log). The on-device v12a once marker has not been checked, because COM9 was deliberately not touched in preparation.

## Next implementation boundary

After a valid new physical readback and safe audit, update this checkpoint and runtime/hand-off with numeric mask/event observations; decide whether true WLC_E_SCAN_COMPLETE26 arrives or requires careful raw receive/mapping investigation. The **separate v12b logical patch** then implements genuine event-driven or well-founded bounded completion with serialized request ownership, asynchronous validated ioctl51, timeout/abort/unbind/suspend teardown and one cfg80211_scan_done. Keep generic 2G v4.220.48 path, factory MAC, NO_IR, p7/p8, OEM and shared-chip power untouched. No upstream DCO or release approved.
