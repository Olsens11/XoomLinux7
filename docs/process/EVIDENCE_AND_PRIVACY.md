# Public evidence, private artifacts and provenance

This repository is public. Keep the following **private and outside Git**: vendor/OEM and downloaded Broadcom firmware binaries, recovery partitions, raw device-specific NVRAM/calibration, Wi-Fi SSIDs/passwords, real MAC/serial identifiers, SSH private keys, GitHub credentials and raw logs containing them. Public reports may reference original evidence paths by role without exposing identity.

Every curated experiment should have:
- Version, date, source commit and builder branch
- DUT role and platform, not serial
- Build command/config/toolchain and exact artifact SHA/size
- Test command, actual observed result and whether hardware was present
- Negative tests, unknowns, rollback
- Sanitization review and a link to the relevant checkpoint

Artifacts and large binaries are not part of history by default. Never overwrite an old image under a misleading new version name. The same source and hash may be retained privately on builder and Surface for qualified comparison. Public source trees are reviewed before publication; treat any unreviewed automatic copy as potentially sensitive.
