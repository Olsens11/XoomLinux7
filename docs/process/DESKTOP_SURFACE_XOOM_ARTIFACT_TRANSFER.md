## 2026-10-27 — Conditional: when modified driver headers change companion-module CRCs

The **normal desktop→Surface port43157 transfer SOP above is unchanged**. V24's Linux7 `brcmfmac` event generation experiment added per-adapter fields to the driver's shared `cfg80211.h` and changed exported CRCs used by the separate `brcmfmac-wcc` plugin. Loading new `brcmfmac.ko` with the **older installed** `brcmfmac-wcc.ko` produced `disagrees about version of symbol brcmf_set_wsec` / `brcmf_fwvid_register_vendor`, Unknown symbol `-22`, and no `wlan0`. This is an ABI mismatch, NOT an Event69 failure. The [V24 physical checkpoint](../checkpoints/MZ600_V24_GENERATION_CHECK_FIRST_SCAN_PASS_TWO_SCAN_GATE_OPEN_2026-10-27.md) contains exact logs and hashes.

**Extra conditional SOP gate for source changes affecting exported-symbol CRCs:** 1) build all affected modules in one ABI-coherent kernel source/config/toolchain revision, capture both module SHA256/size, and compare `modprobe --dump-modversions` imported CRCs against the source tree `Module.symvers`; 2) transfer each new module through the same existing port43157 temporary server and independently hash-verify on the Surface and RAM-staged Xoom; 3) before probing new core, allow the kernel's standard `request_module("brcmfmac-wcc")` to load the matched companion (do **not** race it with late manual `insmod`). In the **isolated MZ600 lab only**, the V24D guarded script temporarily bind-mounted the SHA-matched RAM companion over the exact installed module filename **after** auditing original installed module SHA and quiescing the radio. It then used normal `modprobe`; rollback unloaded modules, unmounted the WCC and firmware overlays, and independently checked the untouched original file hashes. The installed WCC baseline is 5916B SHA `31475d34c94ee4b480fb295032dad84d86eeb81854cb2a140d1f39430f13ff80`; the V24 matched WCC is 5892B SHA `6d3ab647684e6e9fef37caa14ea539bc25f1458f4472d7d0e376a782b364115d`. These values are version-specific: do not hardcode for future builds.

This is conditional test-environment handling, **not production patch design**. Never overwrite installed modules or flash; always have a fail-closed cleanup trap, verify original SHA before and after, reject unknown pre-existing overlays, and maintain one-time trial IDs. In a normal distro/install the solution is distributing kernel-matched modules; do not advocate persistent bind mounts or suppressing symbol-version checking.

---

# Desktop → Surface → Xoom: standard SHA-verified lab artifact transfer

**Canonical workflow as of 2026-10-27.** This procedure is derived from *actual successful* V17, V18 and V19 Remote Desktop Commander command history and hardware-run receipts. It is the standard procedure, not a new transfer system. Use the exact two-host division; read the current per-version hash manifest and owner test script. **Do not substitute a different port, double-wrap PowerShell, or invent an alternate transport during a normal iteration.**

## Roles and locations

| Stage | Computer | Process |
| --- | --- | --- |
| ARM build | `DESKTOP-R16QJD4` | Ubuntu-22.04 WSL, user `xoomdev`; validate exact ABI, source restoration and final .ko SHA256 |
| Brief LAN staging | Same desktop | WSL copies the artifact into a *new* `C:\Users\olsen\AppData\Local\Temp\mz600-<VERSION>-<TRIAL>\` directory; Windows Python serves **that directory only**, over LAN |
| SHA-verified receive | `SURFACE-BOOK-2` | Windows PowerShell `Invoke-WebRequest` from desktop to new private `C:\Users\olsen\xoom-linux-rom\captures\MZ600-<VERSION>-...\` directory; verify exact SHA256 and size before running anything |
| Guarded physical test | Surface → test MZ600 | Exclusive COM9 115200 Python/pyserial; transfer binaries to `/run` with SHA confirmation; test only authorized passive NO_IR channel 36; inspect independent rollback |
| Teardown | Desktop | Terminate **only the verified temporary transfer server**, confirm listener closed, remove *that run's* temporary directory |

**Known working LAN values at the time of V17–V19:** desktop `192.168.0.125`; Surface `192.168.0.40`; **TCP port 43157**. Use a current `ipconfig` read if an address changes, but keep port 43157 unless there is a verified, documented network change requiring another port. HTTP serving has no authentication: use a short-lived server with only the intended hashed artifact (and private firmware *only when necessary*), restricted to LAN, then promptly shut it down. Never expose this temporary server to the Internet; never publish private ROM/firmware, calibration, device MAC or raw scan output to GitHub.

## Exact working sequence

1. **Desktop, WSL to desktop Windows staging** (example placeholders must be replaced with the current *actual* module and fresh trial names):
   ```powershell
   wsl.exe -d Ubuntu-22.04 -u xoomdev -- sh -c 'mkdir -p /mnt/c/Users/olsen/AppData/Local/Temp/mz600-VXX-run && cp /home/xoomdev/xoom-linux-rom/clean-wifi-bt-usb-20261025/EXACT-BUILD-DIR/EXACT-MODULE.ko /mnt/c/Users/olsen/AppData/Local/Temp/mz600-VXX-run/mz600-VXX-module.ko && sha256sum /mnt/c/Users/olsen/AppData/Local/Temp/mz600-VXX-run/mz600-VXX-module.ko'
   ```
   Check returned file size and SHA against the immutable offline build receipt. This is a local desktop **staging** step, not yet a desktop-to-Surface transfer.
2. **Desktop, start the known-good temporary server**; check that 43157 is unused and bind to the current *desktop LAN IPv4*, never `0.0.0.0`:
   ```powershell
   py -3 -m http.server 43157 --bind 192.168.0.125 --directory 'C:\Users\olsen\AppData\Local\Temp\mz600-VXX-run'
   ```
   It is normal for the tool to return a running PID. Confirm `Get-NetTCPConnection -LocalPort 43157 -State Listen` and that the owning process is the precise temporary Python HTTP server.
3. **Surface, use direct PowerShell commands** (run in the remote host's native PowerShell session, *not* nested inside `powershell -Command "..."`):
   ```powershell
   Invoke-WebRequest -UseBasicParsing -Uri 'http://192.168.0.125:43157/mz600-VXX-module.ko' -OutFile 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-VXX-run\mz600-VXX-module.ko'
   Get-Item -LiteralPath 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-VXX-run\mz600-VXX-module.ko' | Select-Object Name,Length
   Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Users\olsen\xoom-linux-rom\captures\MZ600-VXX-run\mz600-VXX-module.ko'
   ```
   Refuse an occupied destination and never overwrite a prior artifact or trial ID. Exact expected size and digest must match. Only then stage the guarded COM9 test.
4. **Surface → MZ600 and restoration:** preserve original installed firmware/module/NVRAM; preflight root, `uname -r`, `/dev/mmcblk0p8 ext4`, wlan/BT/WPA state and no unexpected overlay. The private firmware and test module are staged into RAM (`/run`), SHA-checked on target, and removed/unloaded with automatic rollback and an independent postflight. Do **not** run multiple console clients on COM9. Do not rerun a consumed `.attempted` trial marker.
5. **Teardown on desktop:** match the specific server process *command line* to 43157 plus this run's staging directory, stop **only that verified PID**, check that port 43157 has no listener, then remove **only the exact temporary staging folder**. Never kill unrelated Python processes or recursively remove a broader folder.

## Mandatory safeguards and incident lessons

- **Never layer PowerShell inside PowerShell without necessary and correctly escaped quoting.** In a V21 attempt, an outer double-quoted `powershell -Command` expanded the inner `$p` prematurely, yielding `=C:\Users\...` and a parsing error. Use the direct native command structure above. A program error can look like a blocked file-transfer operation; inspect the submitted command before attributing blame.
- **Do not silently change the established LAN port.** V21 briefly used 43158 instead of the previously working 43157; the Surface HTTP client reported unable to connect despite the desktop listening. This does *not* establish firewall as the root cause, but the new port introduced an unnecessary variable. Revert to known-good 43157 before any speculation.
- **A Windows `\\wsl.localhost\Ubuntu-22.04\...` check or WSL `cp` to desktop `C:` is not a completed cross-computer transfer.** Even if the local copy succeeds, the Surface must explicitly receive and hash it.
- On policy/tool refusal, record the exact rejected operation and why it differs from the documented standard. Do not disguise, bypass or weaken security checks; stop at that step when required and give the owner a transparent, approved manual one-shot.
- On physical tests, use fresh monotonic `/dev/kmsg` marker or another tested stable cursor, **not** `dmesg | wc -l` as the append position: V20's ring rollover caused a false-negative empty event trace.
- Distinguish source built, transfer completed, COM9 preflight, scan performed, and rollback verified. No step implies that a later stage succeeded without its own receipt.

## Proven precedent and authoritative records

- Original Remote Desktop Commander call history on desktop and Surface: V17 (2026-10-27 ~04:18–04:20 local), V18 (~04:53–04:55), V19 (~05:20–05:22) all used WSL → Windows local staging, **Python HTTP server on desktop port 43157**, and Surface `Invoke-WebRequest` with SHA256 checks; servers were stopped and staging directories removed.
- [V19 actual physical checkpoint](../checkpoints/MZ600_V19_EVENT69_WORKER_PRIMARY_IF_LOOKUP_FAIL_PHYSICAL_2026-10-27.md).
- [V20 physical and recovery checkpoint](../checkpoints/MZ600_V20_EVENT_HEADER_V2_17_EVENTS_PHYSICAL_PASS_DMESG_ROLLOVER_RECOVERED_2026-10-27.md).
- [Development workflow](DEVELOPMENT_WORKFLOW.md) and [evidence/privacy](EVIDENCE_AND_PRIVACY.md).

This runbook describes the established process, not the status of any particular binary. Confirm each version's manifest, endpoint, hash and trial markers before execution.
