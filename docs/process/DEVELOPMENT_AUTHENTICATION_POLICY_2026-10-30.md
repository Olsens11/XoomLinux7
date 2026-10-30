# Development-stage authentication policy — owner decision 2026-10-30

> **CURRENT OWNER REQUIREMENT (2026-10-30): Minimize password friction during XoomLinux7 development. Do NOT require passwords when optional. Wherever a password is technically unavoidable for the Xoom project/test installations, use `1234`.** This intentionally trades authentication strength for development convenience; revert/review after the development phase. Read this with [MZ604 I0 procedure](../rfc/bcm4329-upstream-first/I0_ACCOUNT_RECOVERY_RUNBOOK_2026-10-30.md) and [remote-test plan](../rfc/bcm4329-upstream-first/REMOTE_TEST_INFRASTRUCTURE_PLAN_2026-10-30.md).

## Scope of this decision

- Applies to **user-owned, dedicated Motorola Xoom experimental Linux/Recovery Toolkit accounts and local test environments**. Includes MZ604 and subsequently provisioned Xoom lab instances, not an indiscriminate rewrite of already working independent devices.
- **Preferred interactive development route:** locally attached USB serial device (`ttyGS0` / Surface COM10) logs in as `xoom` **without a password prompt**; `xoom` can use `sudo` **without prompting for a password**. Use standard Linux systemd/agetty and scoped sudoers configuration—not an upstream kernel patch or a new authentication service.
- For access paths that require an actual account password (e.g., a normal local console getty or an emergency fallback when autologin is unavailable), the **development-only `xoom` account password is `1234`**. No need to create a separate root password; root can remain locked while `xoom` has sudo privileges. The fallback password must not be mistaken for the password of an earlier MZ600 build.
- This deliberately low-entropy password may be written literally in this **project policy** because it is a public, non-secret development convention by owner instruction. Do not put actual hashed `/etc/shadow` contents, tokens, real Wi-Fi credentials, Surface/GitHub credentials or private device data into public logs/commits.
- **Do NOT apply this to the Surface Book, RTX development desktop, GitHub, connected accounts, routers, real Wi-Fi WPA passwords, cloud services, SSH exposed to the network, or another person's systems.** Passwordless local USB serial does not imply allowing unauthenticated network login. If remote network administration is required, prefer restricted keys/host-mediated access rather than exposing `1234` to a reachable SSH password service. Do not enable network listeners merely to avoid a USB login prompt.
- No attempt to implement a general security system now; preserve the ability to restore stronger authentication before any wider deployment/connected use. Do not derail the minimal Wi-Fi RFC for hardening work.

## Proposed MZ604 I0 implementation (not yet deployed)

1. When owner can physically restore TWRP and a verified current p10 rootfs backup exists, inspect **live** Debian getty, PAM/login behavior, and account files. The old ext4 staging snapshot has locked root/xoom and no xoom sudo group. The source Debian `serial-getty@.service` uses `agetty`; its `ExecStart` can be overridden by a dedicated `serial-getty@ttyGS0.service.d` drop-in, using `agetty --autologin xoom`. Verify the exact target package and service arguments on an offline copy first.
2. Configure `xoom` for direct COM10 autologin only, with restricted, syntax-checked sudoers rule `xoom ALL=(ALL:ALL) NOPASSWD:ALL` in `/etc/sudoers.d/` (root-owned, mode 0440). This grants full root privileges to the **physical USB serial account**, as explicitly accepted for the lab. Do not configure auto-root login.
3. Set `xoom` fallback account password **`1234` only where required for non-autologin access/PAM**; normal COM10 and sudo operations should not request it. If the account remains locked and PAM refuses autologin, the fallback must be provisioned, not circumvented by unreviewed PAM hacks. Keep root password locked.
4. Use fresh exact-image backups and isolated offline syntax/FS checks; then deploy through approved supervised TWRP session and return to unchanged p7. Test `id`, `sudo -n true`, privileged command, reconnect, normal reboot and COM10 auto-login. Only **observed** physical results may close I0. No blind writes, no device reboot while owner absent.

## Required documentation behavior

Every agent reading [AGENTS.md](../../AGENTS.md), [START_HERE.md](../../START_HERE.md) and [required reading map](../rfc/bcm4329-upstream-first/AGENT_READING_MAP.md) must honor this owner convention. Log every substantive turn. Document a later change in credentials/access policy as a **dated superseding decision**, not by silently rewriting older time-scoped evidence.

**Current as-of 2026-10-30:** policy approved, approach source-reviewed, **NOT installed on MZ604**; COM10 still shows Debian login, not an authenticated shell. No change to the minimal BCM4329 upstream patch plan.
