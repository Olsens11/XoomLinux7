#!/usr/bin/env bash
# Only changes the shadow file of an explicitly marked *disposable copy*.
# NEVER pass a password as a command-line argument or commit it to git.
set -euo pipefail
[[ $# == 1 ]] || { echo "Usage: $0 DISPOSABLE_ROOTFS_DIR" >&2; exit 2; }
dest="$(realpath "$1")"
[[ "$dest" != "/" && -f "$dest/.xoom-disposable-test-rootfs" && -f "$dest/etc/shadow" ]] || {
 echo "REFUSE: not a specifically marked disposable test image" >&2; exit 2;
}
[[ ! -e "$dest/.xoom-live-device" ]] || { echo "REFUSE: live device marker present"; exit 2; }
[[ ! "$dest" == /mnt/* && ! "$dest" == /media/* ]] || { echo "REFUSE: no mounted disk targets"; exit 2; }
[[ "$(id -u)" == 0 ]] || { echo "Run as root against disposable COPY only" >&2; exit 2; }
read -r -s -p "Temporary local-console root password for this disposable image: " answer
echo
[[ -n "$answer" ]] || { echo "Refusing empty root password"; exit 2; }
hash="$(printf '%s\n' "$answer" | openssl passwd -6 -stdin)"
unset answer
# Pass salted hash through stdin, never on argv.
printf '%s\n' "$hash" | python3 -c '
import pathlib,sys
p=pathlib.Path(sys.argv[1]); digest=sys.stdin.readline().strip()
lines=p.read_text().splitlines()
found=0
for i,line in enumerate(lines):
 if line.startswith("root:"):
  f=line.split(":"); f[1]=digest; lines[i]=":".join(f); found+=1
assert found==1, "Must have exactly one root shadow entry"
p.write_text("\n".join(lines)+"\n")
' "$dest/etc/shadow"
unset hash
chmod 0600 "$dest/etc/shadow"
echo "DISPOSABLE_ROOT_PASSWORD_PROVISIONED locally (not stored in Git or logs)"
