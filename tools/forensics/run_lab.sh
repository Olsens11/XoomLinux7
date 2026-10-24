#!/usr/bin/env bash
# Reproducible offline v025 forensic lab. Never accesses the physical Xoom.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
XOOM_BUILD="${XOOM_BUILD:-/home/xoomdev/xoom-linux-rom}"
if [[ -f "$XOOM_BUILD/forensic-lab/config.env" ]]; then
  source "$XOOM_BUILD/forensic-lab/config.env"
fi
ART="${XOOM_ART:?Set XOOM_ART in private forensic-lab/config.env or environment}"
IMAGE="${XOOM_IMAGE:-$ART/MZ600-stingray-diagnostic-v025-HOST-PRE-RESET-100MS-TEMPBOOT-ONLY.img}"
DTB="${XOOM_DTB:-$ART/tegra20-motorola-stingray-usbdiag.dtb}"
KERNEL="${XOOM_KERNEL:-$XOOM_BUILD/linux-src}"
CROSS="${XOOM_CROSS:-$XOOM_BUILD/toolchains/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc}"
OUT="${XOOM_OUT:-$XOOM_BUILD/forensic-lab/output}"
mkdir -p "$OUT"
sha_expected="142daec30b6bf0ef52eaaf48456d313263197d9d224f1dfceb20972af48e39fb"
actual="$(sha256sum "$IMAGE" | cut -d" " -f1)"
[[ "$actual" == "$sha_expected" ]] || { echo "FAIL: Unexpected boot image hash (do not silently substitute image)"; exit 10; }
"$CROSS" -O2 -g -static -march=armv7-a -mfpu=vfpv3 -mfloat-abi=hard -Wall -Wextra -Werror "$ROOT/tools/forensics/arm_fdt_consumer.c" -o "$OUT/arm_fdt_consumer"
echo "=== ARM VIRTUAL CONSUMER ==="
qemu-arm -cpu cortex-a9 "$OUT/arm_fdt_consumer" "$DTB" 100 300 25000000 | tee "$OUT/arm-fdt-v025.log"
echo "=== BOOT + FIRMWARE AUDIT ==="
python3 "$ROOT/tools/forensics/audit.py" --image "$IMAGE" --dtb "$DTB" --linux-src "$KERNEL" --init-src "$ROOT/src/diag-init/phase1-v20/init.c" --report "$OUT/v025-audit.json" --private-nvram-source "$OUT/generic-nvram-source-private.txt" --private-nvram-model "$OUT/generic-nvram-python-model-private.bin"
echo "=== INDEPENDENT ARM NVRAM CONSUMER ==="
"$CROSS" -O2 -g -static -march=armv7-a -mfpu=vfpv3 -mfloat-abi=hard -Wall -Wextra -Werror "$ROOT/tools/forensics/arm_nvram_consumer.c" -o "$OUT/arm_nvram_consumer"
qemu-arm -cpu cortex-a9 "$OUT/arm_nvram_consumer" "$OUT/generic-nvram-source-private.txt" "$OUT/generic-nvram-arm-private.bin"
cmp "$OUT/generic-nvram-arm-private.bin" "$OUT/generic-nvram-python-model-private.bin"
echo "ARM_AND_PYTHON_NVRAM_BYTE_IDENTICAL $(sha256sum "$OUT/generic-nvram-arm-private.bin")"
echo "=== FAULT INJECTION ==="
python3 "$ROOT/tools/forensics/test_lab.py" --image "$IMAGE" --dtb "$DTB" --arm "$OUT/arm_fdt_consumer" --linux-src "$KERNEL" --init-src "$ROOT/src/diag-init/phase1-v20/init.c"
echo "=== DONE ==="
echo "PRIVATE_OUTPUT=$OUT"
