# Machine worktrees and GitHub write-access design

**Repository:** `Olsens11/XoomLinux7` on GitHub. Keep a regular main integration worktree plus isolated topic worktrees. A Git worktree shares its local .git object store with other worktrees **on the same machine**, never across unrelated computers.

Recommended local structures:
- Desktop Ubuntu WSL: `~/projects/XoomLinux7` main, `~/projects/XoomLinux7-wifi` on `wifi/bcm4329-f2`, `~/projects/XoomLinux7-usb` on `usb/live-lab`.
- Pi: `~/projects/XoomLinux7` main, `~/projects/XoomLinux7-research` on `research/oem-comparison`.
- Surface: `C:\Users\olsen\XoomLinux7` main, `C:\Users\olsen\XoomLinux7-hardware` on `hardware/qualification`.

Each machine gets an **independently generated ed25519 key pair** named `xoomlinux7_github`, with SSH alias `github.com-xoomlinux7`. The Git remote is `git@github.com-xoomlinux7:Olsens11/XoomLinux7.git`. Private keys never leave the originating host.

**Critical:** Generating an SSH key does NOT grant GitHub access. Add each corresponding public key at `https://github.com/Olsens11/XoomLinux7/settings/keys` → Add deploy key → enable **Allow write access**. A deploy key may belong to only one repository, which is why existing Xoom recovery keys are not reused. Verify `ssh -T git@github.com-xoomlinux7` and a non-destructive branch push after registration.

Branch ownership: Desktop builds on wifi/usb; Pi documents OEM reference; Surface collects hardware evidence. All may read main. Each machine should use its own branch and regularly merge/rebase, but never push simultaneous competing writers to the same branch without coordination.

Do not commit the keys or copy them into GitHub documentation. After credentials are registered, record validated `git ls-remote` + `git push` result in a dated device-access checkpoint, *not* the private key.
