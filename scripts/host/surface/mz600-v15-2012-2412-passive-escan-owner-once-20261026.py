#!/usr/bin/env python3
"""Surface owner-operated V15; original 2012 BCM4329 single 2.4GHz ch1 passive ESCAN test.

Run when prior COM9 terminal/tool is disconnected:
    python mz600-v15-owner-once.py
Requires Python pyserial; DOES NOT alter boot, installed FW, kernel, or NVRAM.
Stage two SHA-pinned inputs into Xoom /run, use SHA-guarded transient bind
overlay and passive-only Event69 diagnostic module, audit rollback.
Do not repeat a used one-shot or suppress failed preflight guards.
"""
import base64
import gzip
import hashlib
import json
import re
import time
from pathlib import Path

import serial

ROOT = Path(r"C:\Users\olsen\xoom-linux-rom\captures\MZ600-V15-2012-2412-ESCAN-20261026")
FW = ROOT / "mz600-v15-oem2012.bin"
KO = ROOT / "mz600-v15-escan-event69.ko"
SH = ROOT / "mz600-v15-passive-scan.sh"
LOG = ROOT / "mz600-v15-owner-COM9-private.txt"
RECEIPT = ROOT / "mz600-v15-owner-receipt.json"
SENTINEL = ROOT / "mz600-v15-owner-attempted.marker"
FW_SHA = "5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834"
KO_SHA = "8ab54acbb204aeab49bdbf2ef4265fc40c8454e8a5c07ba57d11028105c719f4"
SH_SHA = "63a80df74ad805db3ace9bde19fc7a67b34925087d65118a10c8706021683cee"
BASE_FW = "d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93"
BASE_NV = "a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb"
BASE_KO = "9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb"
RAM_FW = "/run/mz600-v15-oem2012.bin"
RAM_KO = "/run/mz600-v15-escan-event69.ko"
TAG = "__MZ600_V15_OWNER__"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def checked(path, size, expected):
    raw = path.read_bytes()
    if len(raw) != size or sha(raw) != expected:
        raise RuntimeError("Host staged file verification rejected: " + path.name)
    return raw

def recv(p, marker, seconds=25):
    out = bytearray()
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        chunk = p.read(4096)
        if chunk:
            out.extend(chunk)
            if marker.encode() in out:
                time.sleep(.15)
                out.extend(p.read(4096))
                return out.decode("utf-8", errors="replace").replace("\r\n", "\n")
        if len(out) > 900000:
            raise RuntimeError("Unexpectedly large Xoom console response")
    raise TimeoutError("COM9 timed out before marker " + marker)

def send(p, line):
    p.write(line.encode("ascii") + b"\n")
    p.flush()

def session():
    p = serial.Serial("COM9", 115200, timeout=.20, write_timeout=10)
    p.dtr = p.rts = True
    p.reset_input_buffer()
    p.write(b"\r")
    time.sleep(.25)
    p.read(4096)
    send(p, "stty -echo")
    time.sleep(.2)
    p.reset_input_buffer()
    return p

def root_probe():
    with session() as p:
        start = TAG + "_AUDIT_BEGIN"
        end = TAG + "_AUDIT_END"
        query = (
            "echo " + start + "; id -u; uname -r; findmnt -n -o SOURCE,FSTYPE /; "
            "test ! -e /sys/class/net/wlan0 && echo NO_WLAN0; "
            "grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil|bluetooth|hci_uart) ' /proc/modules || echo NO_BRCM_BT; "
            "mountpoint -q /lib/firmware/brcm/brcmfmac4329-sdio.bin || echo FW_UNMOUNTED; "
            "mountpoint -q /lib/firmware/brcm/brcmfmac4329-sdio.txt || echo NV_UNMOUNTED; "
            "sha256sum /lib/firmware/brcm/brcmfmac4329-sdio.bin "
            "/lib/firmware/brcm/brcmfmac4329-sdio.txt "
            "/lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko; "
            "echo " + end + "; stty echo"
        )
        send(p, query)
        result = recv(p, end, 20)
        body_start = result.find(start)
        body_end = result.find(end, body_start + len(start))
        if body_start < 0 or body_end < 0:
            raise RuntimeError("Could not isolate exact device preflight")
        body = result[body_start+len(start):body_end]
        if not re.search(r"(?m)^0\s*$", body):
            raise RuntimeError("COM9 session was not root")
        for marker in ("7.0.0-next-20260422+", "/dev/mmcblk0p8 ext4",
                       "NO_WLAN0", "NO_BRCM_BT", "FW_UNMOUNTED",
                       "NV_UNMOUNTED", BASE_FW, BASE_NV, BASE_KO):
            if marker not in body:
                raise RuntimeError("Xoom baseline mismatch: " + marker)
        return result

def ram_probe():
    with session() as p:
        start = TAG + "_RAM_BEGIN"
        end = TAG + "_RAM_END"
        send(p, "echo "+start+"; sha256sum "+RAM_FW+" "+RAM_KO+
             "; stat -c %s "+RAM_FW+" "+RAM_KO+"; echo "+end+"; stty echo")
        output = recv(p, end, 15)
        for marker in (FW_SHA, KO_SHA, "264140", "344536"):
            if marker not in output:
                raise RuntimeError("On-device RAM hash/size mismatch")
        return output

def upload(path, raw, ram_path, ident):
    """Established gzip/base64 serial ACK protocol, RAM only; one run."""
    b64 = base64.b64encode(gzip.compress(raw, compresslevel=6, mtime=0)).decode("ascii")
    lines = [b64[i:i+1024] for i in range(0, len(b64), 1024)]
    tag = TAG + "_" + ident
    begin, done, eof = tag+"_READY", tag+"_DONE", tag+"_EOF"
    good, bad = tag+"_SHA_PASS", tag+"_SHA_FAIL"
    with session() as p:
        start, finish = tag+"_CHECK_BEGIN", tag+"_CHECK_END"
        send(p, "echo "+start+"; id -u; uname -r; "
                "test ! -e "+ram_path+" && test ! -e "+ram_path+".b64 && echo UNUSED; "
                "echo "+finish)
        check = recv(p, finish, 15)
        if not ("UNUSED" in check and "7.0.0-next-20260422+" in check):
            raise RuntimeError("Remote staged path already used")
        receive = (
            "i=0; : > "+ram_path+".b64; echo "+begin+"; "
            "while IFS= read -r L; do "
            "if [ \"$L\" = \""+eof+"\" ]; then break; fi; "
            "printf '%s\\n' \"$L\" >> "+ram_path+".b64; "
            "i=$((i+1)); if [ $((i%16)) -eq 0 ]; then printf '"+tag+"_ACK_%d__\\n' \"$i\"; fi; "
            "done; "
            "if base64 -d "+ram_path+".b64 | gzip -d > "+ram_path+
            " && [ \"$(stat -c %s "+ram_path+")\" = \""+str(len(raw))+"\" ] "
            "&& printf '%s  %s\\n' "+sha(raw)+" "+ram_path+" | sha256sum -c - >/dev/null; "
            "then echo "+good+"; rm -f "+ram_path+".b64; else echo "+bad+"; fi; "
            "stty echo; echo "+done
        )
        send(p, receive)
        recv(p, begin, 15)
        for start_idx in range(0, len(lines), 16):
            group = lines[start_idx:start_idx+16]
            for line in group:
                send(p, line)
            if len(group)==16:
                recv(p, tag+"_ACK_"+str(start_idx+16)+"__", 40)
            if (start_idx+len(group)) % 64 == 0:
                print(ident+" transferred "+str(start_idx+len(group))+"/"+str(len(lines)),flush=True)
        send(p, eof)
        result = recv(p, done, 45)
        if bad in result or good not in result:
            raise RuntimeError("Firmware/module RAM SHA verification failed")
    print(ident+" RAM SHA verification PASS; no installation", flush=True)

def shell_heredoc(lines, syntax_only=False):
    delim = TAG + ("_SYNTAX" if syntax_only else "_TEST")
    marker = delim + "_RC_"
    with session() as p:
        opening = "bash -n <<'"+delim+"'" if syntax_only else "bash <<'"+delim+"'"
        send(p, opening)
        for i, line in enumerate(lines):
            p.write(line.encode("ascii") + b"\n")
            if i%35 == 0:
                p.flush()
            time.sleep(.055)
        send(p, delim)
        send(p, "printf '"+marker+"%s__\\n' \"$?\"; stty echo")
        result = recv(p, marker, 150 if not syntax_only else 40)
        match = re.search(re.escape(marker)+r"([0-9]+)__", result)
        if match is None:
            raise RuntimeError("Missing exact Xoom script exit-code receipt")
        return result, int(match.group(1))

def main():
    if SENTINEL.exists() or LOG.exists() or RECEIPT.exists():
        raise RuntimeError("Prior v15 attempt or report exists; no rerun permitted")
    fw = checked(FW, 264140, FW_SHA)
    ko = checked(KO, 344536, KO_SHA)
    source = checked(SH, SH.stat().st_size, SH_SHA).decode("ascii")
    if not source.endswith("\n") or TAG in source:
        raise RuntimeError("Staged bash source invalid")
    print("V15_2012_SURFACE_TRIPLE_SHA_PASS", flush=True)
    # Check COM9 without interrupting other sessions. A busy port fails closed.
    root_probe()
    print("V15_XOOM_ORIGINAL_FW_NV_MODULE_BASELINE_PASS", flush=True)
    SENTINEL.write_text("one-shot attempted; inspect Xoom and receipt before any rerun\n", encoding="utf-8")
    upload(FW, fw, RAM_FW, "FW")
    upload(KO, ko, RAM_KO, "KO")
    ram_probe()
    lines = source.splitlines()
    _, syntax_rc = shell_heredoc(lines, syntax_only=True)
    if syntax_rc != 0:
        raise RuntimeError("On-device bash -n rejected test; no radio action")
    print("V15_ON_DEVICE_GUARDED_SCRIPT_SYNTAX_PASS", flush=True)
    result, rc = shell_heredoc(lines)
    LOG.write_text(result, encoding="utf-8")
    audit_ok = False
    try:
        root_probe()
        audit_ok = True
    except Exception as error:
        print("POSTSTATE_NOT_VERIFIED: "+str(error), flush=True)
    mandatory = ("MZ600_V15_CHANNEL1_NO_IR_NONDFS_PASS",
                 "MZ600_V15_IW_PASSIVE_CH1_RC=",
                 "MZ600_V15_EVENT69_STATUS_COUNTS",
                 "MZ600_V15_NO_ASSOCIATION_OR_DIRECTED_SSID",
                 "MZ600_V15_ORIGINAL_FILES_AND_RADIO_RESTORED")
    transcript_ok = all(m in result for m in mandatory)
    receipt = {
        "firmware_candidate": "4.218.248.44", "fw_sha": FW_SHA,
        "module_sha": KO_SHA, "source_sha": SH_SHA,
        "root_bash_rc": rc, "transcript_sha": sha(result.encode()),
        "independent_poststate_ok": audit_ok,
        "script_cleanup_ok": transcript_ok,
        "permanent_install": False, "scan_requested": True
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2)+"\n", encoding="utf-8")
    for line in result.splitlines():
        if "MZ600_V15_" in line:
            print(line[:260], flush=True)
    if rc != 0 or not audit_ok or not transcript_ok:
        raise RuntimeError("Test / rollback incomplete; retain receipt and inspect before any next action")
    print("V15_2G_COMPARISON_SCAN_ATTEMPT_AND_ROLLBACK_PASS",flush=True)

if __name__ == "__main__":
    main()
