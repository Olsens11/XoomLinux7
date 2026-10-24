# Candidate/release manifests

Public Git tracks release metadata and checksum manifests only. Historical `MZ600-stingray-diagnostic-v14-LIVE-LAB-TEMPBOOT-ONLY.img` was built and SHA verified offline, **not hardware-qualified**. Do not promote to stable release or distribute third-party firmware without redistribution review. See `v014-manifest.txt`.

Update 2026-10-24: v015 physically passed temporary boot, USB raw binary CRC uploads and module lifecycle. Wi-Fi remains nonfunctional (no wlan0). Image privately staged; only source and manifest published.

Experimental manifests now include \`v018-manifest.txt\` (OEM capability and SD-HS work, but F2 fails) and \`v019-manifest.txt\` (actual SDMMC2 clock 25MHz, but F2 fails). Neither is a stable Wi-Fi release; images are not committed.
