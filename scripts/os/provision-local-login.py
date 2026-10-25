#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
"""Provision a unique LOCAL owner account in an OFFLINE ARMhf rootfs.

Never commit or print a password, randomize one per installation. The only
secret copy stays in a private chmod-0600 file on the user's development PC.
This never contacts a device and never modifies any on-device partition.
"""
from __future__ import annotations
import os
from pathlib import Path
import pwd
import secrets
import subprocess
import sys

if len(sys.argv) != 3 or os.geteuid() != 0:
    sys.exit("usage (as root): provision-local-login.py ROOTFS PRIVATE_CREDENTIAL_FILE")
root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
if root.name != "bookworm-armhf-root" or not (root / "etc/debian_version").is_file():
    sys.exit("Refusing non-staged ARMhf rootfs")
if not (root / "usr/bin/qemu-arm-static").is_file():
    sys.exit("ARMhf QEMU build-time helper missing")
if out.exists():
    sys.exit("Credentials already exist: refusing silent rotation")
if "os-build/private" not in str(out):
    sys.exit("Credential output must remain in local os-build/private")
out.parent.mkdir(parents=True, exist_ok=True)

def arm_exec(*args: str) -> None:
    subprocess.run(["chroot", str(root), "/usr/bin/qemu-arm-static", *args],
                   check=True, capture_output=True, text=True)

# No special default password. Keep root locked; administer with sudo.
try:
    arm_exec("/usr/sbin/useradd", "-m", "-s", "/bin/bash", "xoom")
except subprocess.CalledProcessError:
    # Permit rerun only if user already exists; no password reset.
    shadow = (root / "etc/passwd").read_text()
    if not any(line.startswith("xoom:") for line in shadow.splitlines()):
        raise
arm_exec("/usr/sbin/usermod", "-a", "-G", "sudo,video,audio,input,dialout", "xoom")
password = secrets.token_urlsafe(24)
h = subprocess.run(["openssl", "passwd", "-6", "-stdin"], input=password+"\n",
                   text=True, check=True, capture_output=True).stdout.strip()
if not h.startswith("$6$"):
    sys.exit("No valid SHA512-crypt result; account not provisioned")
arm_exec("/usr/sbin/usermod", "-p", h, "xoom")
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
fd = os.open(out, flags, 0o600)
try:
    os.write(fd, ("USB login username: xoom\n"
                  "USB login password: "+password+"\n"
                  "Change this private first-boot password immediately.\n").encode())
finally:
    os.close(fd)
# Allow the desktop's local owner to retrieve the file without sudo, never
# put the secret in a shell command, log, GitHub commit, or published report.
owner = pwd.getpwnam("xoomdev")
os.chown(out, owner.pw_uid, owner.pw_gid)
os.chmod(out, 0o600)
print("OS_LOGIN_PROVISIONED username=xoom; secret stored privately at", str(out))
print("RAW_SECRET_NOT_PRINTED; root account remains locked")
