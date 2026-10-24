# GitHub per-device write access — 2026-10-24

**Status:** ALL THREE VERIFIED. Public source repository: [Olsens11/XoomLinux7](https://github.com/Olsens11/XoomLinux7).
**Checkpoint target:** `7bcb3e7db8a4c73b3325daf4867803d76141f6ec` on main at the time of the access test.
**Access model:** One independent ed25519 deploy key per machine, locally protected private key in the user's SSH directory; remote for **push** uses `git@github.com-xoomlinux7:Olsens11/XoomLinux7.git`. Regular fetch continues over HTTPS.

| Host | Local worktree | New key fingerprint | GitHub SSH auth | Real remote branch create | Remote delete |
| --- | --- | --- | --- | --- | --- |
| Desktop / WSL Ubuntu | `/home/xoomdev/projects/XoomLinux7` | `SHA256:fn8fAjmMdhMAnIbFUZ8lJt6ILCSRb+1kIfAe2iSq28U` | PASS | `access-check/desktop` PASS | PASS |
| Raspberry Pi | `/home/ps2/projects/XoomLinux7` | `SHA256:GpaeXxizzWkk3y4/pLUBZa/EzLTfP6Wk3xwftj9fL5A` | PASS | `access-check/pi` PASS | PASS |
| Surface Book 2 | `C:\Users\olsen\XoomLinux7` | `SHA256:IZ6qFU4zIP3j+RQnTgspjtpK3J2nSwTIwqNPuFs1EJ4` | PASS | `access-check/surface` PASS | PASS |

## What was observed
1. `ssh -o BatchMode=yes -T git@github.com-xoomlinux7` returned GitHub's successful authentication response for `Olsens11/XoomLinux7` on each host.
2. `git push origin HEAD:refs/heads/access-check/<host>` created a branch on GitHub from each host. This verifies **actual write**, not merely public read access or SSH identity.
3. `git push origin :refs/heads/access-check/<host>` deleted each temporary branch successfully from the originating host; no test branches remain intentionally.
4. All seven worktrees were synchronized to `7bcb3e7` before this new documentation commit; Desktop and Pi repository checker passed. No firmware was modified or device partitions touched.

## Qualifications
- This record verifies repository access, not Linux v014 hardware behavior.
- Each deploy key is repository-specific; do not reconfigure, share or remove existing Xoom recovery/PS2 identities.
- This is a human-readable verification result from live commands, not a durable capture of the full SSH transcript. To revalidate access, run `ssh -T` and a new harmless temporary-branch push in your assigned worktree.
- Never commit private key contents or credentials.
