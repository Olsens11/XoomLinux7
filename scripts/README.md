# Scripts and historical builders

- `history/vNN/` — imported v01–v14 original build, staging, investigation, and packaging scripts. Several steps are incremental, machine-specific and operate on old absolute paths.
- `history/common/` — scripts without revision marker, historical setup and repair.
- `bootstrap-upstream.sh` — fetch original xoom-linux/linux repository at pinned commit into ignored `upstream/linux/`.
- `resume-state.sh` — print canonical project state and working tree.

Do **not** execute a historical recipe merely because it is present. Inspect its effect on the host, input versions, firmware dependencies and output image first. Firmware and private device data are not stored in the public repository.

- host/surface/: physically tested v015 raw USB live-lab client, historical v014 client, and other Surface probes.

- build/v15-* — v015 source compile, initramfs, kernel rebuild and image packaging; temporary boot only.

- \`experiments/v016-build-f2probe.py\` — diagnostic-only source overlay, uses ARM toolchain and temporary local Linux tree, verifies restoration; no device-flash instructions.
