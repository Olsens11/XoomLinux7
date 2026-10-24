# Scripts and historical builders

- `history/vNN/` — imported v01–v14 original build, staging, investigation, and packaging scripts. Several steps are incremental, machine-specific and operate on old absolute paths.
- `history/common/` — scripts without revision marker, historical setup and repair.
- `bootstrap-upstream.sh` — fetch original xoom-linux/linux repository at pinned commit into ignored `upstream/linux/`.
- `resume-state.sh` — print canonical project state and working tree.

Do **not** execute a historical recipe merely because it is present. Inspect its effect on the host, input versions, firmware dependencies and output image first. Firmware and private device data are not stored in the public repository.

- `host/surface/` — reviewed host-side USB commands and v014 live-lab client; `history/` there denotes obsolete host workflows.
