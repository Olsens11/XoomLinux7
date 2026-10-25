# Surface COM9 interactive terminal bridge for real Debian

**Date:** 2026-10-25. **Status:** two locally installed launchers, script syntax parsed cleanly, **read-only connection test PASS**. This is a convenience tool for a live Xoom already booted into Debian. **No regulatory package installation yet**, no Wi-Fi state changes.

## User's limitation

No physical keyboard or functioning native user-input method is available at the Xoom's Debian tty1 login. The USB gadget `ttyGS0` already enumerates on the authorized Surface Book 2 as `COM9` (Linux USB VID:PID `0525:a4a7`). Its independently verified authenticated `xoom` shell remains available through serial. `sudo -n id -u` returned **`sudo: a password is required`**. Remote code attempting to pull a stored credential automatically and perform privileged actions was blocked; **do not retry that approach**.

## Installation on Surface only

Local bridge script:
`C:\Users\olsen\xoom-linux-rom\downloads\Start-Xoom-USB-Console.ps1`

Two shortcuts (ordinary `.cmd` launchers) on the active desktop at `C:\Users\olsen\OneDrive\Desktop\`:
- `Xoom USB Console.cmd` — live interactive COM9 shell; Surface keyboard input forwarded to Debian. Control+] ends local connection without rebooting.
- `Xoom - Install Signed Regulatory Database.cmd` — if a logged-in `xoom` shell is present, queues a *pre-verified*, *hash-gated* installer expression then opens interactive console and waits for the **human user** to supply the Debian sudo password by typing in the Surface window. Password is not present in either script, not retrieved from the private WSL credential file, not stored by the bridge and not printed in tool logs. It installs only the Debian package already staged at `/tmp/xoom-wireless-regdb-20261025.deb` and selects the upstream-signed regulatory.db alternative. It then displays read-only database link and `iw reg get` verification. Does not bring `wlan0` UP or set any country code.

The queued shell command is hash-gated to `3ff60d4ebc84fa4e202ce6359da3816a48ec1ea06b0820fdffda0396f33002c9`. If package checksum fails, subsequent install commands do not execute.

**Validation:** Windows PowerShell parser reported **CONSOLE_SCRIPT_PARSE_PASS**. Running `Start-Xoom-USB-Console.ps1 -Probe` from Surface showed `COM9_READABLE=True`, `LOGIN_OR_SHELL=True`, `Probe complete. No system changes made.`. Full keyboard/password-driven interactive launcher has **not yet been launched by user**. Therefore no claim of installing the signed regulatory package is justified.

## Safety and follow-up

- No USB-serial terminal should run simultaneously with another program holding COM9. Shut other serial tools before opening launcher.
- User types only on Surface, **not on tablet**. The generated first-boot password resides privately on Desktop WSL; do not post it to GitHub or chat. Password may be required for sudo to install; interactive bridge won't retrieve it.
- Do not claim signed-regdb kernel trust verified merely from `dpkg` install; inspect `regulatory.db` + matching `.p7s` symlink, then observe kernel signature acceptance.
- No persistent internal eMMC modifications, regulatory overrides, Wi-Fi scans or RF transmissions authorized/performed by this setup.
