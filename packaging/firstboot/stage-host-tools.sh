#!/usr/bin/env bash
set -euo pipefail
[[ $# == 1 ]] || { echo "Usage: $0 NEW_PRIVATE_OUTPUT" >&2; exit 2; }
out="$1"; [[ ! -e "$out" ]] || { echo "Refuse existing target" >&2; exit 2; }
here="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$out"
cp "$here/scripts/host/windows/Start-Xoom-USB-Console.ps1" "$here/scripts/host/windows/Xoom-USB-Console.cmd" "$out/"
(cd "$out" && sha256sum Start-Xoom-USB-Console.ps1 Xoom-USB-Console.cmd > SHA256SUMS)
echo "COM9_HOST_TOOLS_STAGED $out"
