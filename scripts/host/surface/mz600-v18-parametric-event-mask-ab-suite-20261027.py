#!/usr/bin/env python3
"""Surface owner-operated V18; original 2012 BCM4329 single ch36 passive ESCAN test with 500ms dwell.

Run when prior COM9 terminal/tool is disconnected:
    python mz600-v18-owner-once.py
Requires Python pyserial; DOES NOT alter boot, installed FW, kernel, or NVRAM.
Stage two SHA-pinned inputs into Xoom /run, use SHA-guarded transient bind
overlay and passive-only Event69 diagnostic module, audit rollback.
Do not repeat a used one-shot or suppress failed preflight guards.
"""
import argparse
import base64
import gzip
import hashlib
import json
import re
import time
from pathlib import Path

import serial

ROOT = Path(r"C:\Users\olsen\xoom-linux-rom\captures\MZ600-V18-2012-MASK-SWEEP-20261027")
FW = ROOT / "mz600-v18-oem2012.bin"
KO = ROOT / "mz600-v18-escan-event69.ko"
SH = ROOT / "mz600-v18-passive-scan.sh"
LOG = ROOT / "mz600-v18-owner-COM9-private.txt"
RECEIPT = ROOT / "mz600-v18-owner-receipt.json"
SENTINEL = ROOT / "never-use-global-marker"
FW_SHA = "5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834"
KO_SHA = "65b805f5fe6ca1d28a14b5af6f1cf7251b490fbed9488a3a69d5f70eed02c229"
SH_SHA = "48c917557330ef6fc75cd9040f2786095291786ef3eb670d29a7ef6c730507ca"
BASE_FW = "d61983946b1e733e4c75dbe6841ac0f1250ebed2e3ee9058cdfdbbba3ba37c93"
BASE_NV = "a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb"
BASE_KO = "9fec47bc2771d55bcdb1c36bb7502dffea6a0dd2d94dcff60725f44f3fb2d6eb"
RAM_FW = "/run/mz600-v18-oem2012.bin"
RAM_KO = "/run/mz600-v18-escan-event69.ko"
TAG = "__MZ600_V18_OWNER__"

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
            "grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules || echo NO_BRCM_WIFI; "
            "if systemctl is-active --quiet bluetooth.service; then echo BT_SERVICE_ACTIVE; else echo BT_SERVICE_INACTIVE; fi; "
            "if test -d /sys/class/bluetooth/hci0; then if hciconfig hci0 2>/dev/null | grep -Fq 'UP RUNNING'; then echo BT_HCI_UP; else echo BT_HCI_DOWN; fi; else echo BT_HCI_DOWN; fi; "
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
                       "NO_WLAN0", "NO_BRCM_WIFI", "BT_SERVICE_INACTIVE", "BT_HCI_DOWN", "FW_UNMOUNTED",
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
        for marker in (FW_SHA, KO_SHA, "264140", "347380"):
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

def shell_heredoc(lines, mask, trial, syntax_only=False):
    delim = TAG + ("_SYNTAX" if syntax_only else "_TEST")
    marker = delim + "_RC_"
    with session() as p:
        opening = "bash -n <<'"+delim+"'" if syntax_only else "bash -s -- "+str(mask)+" "+trial+" <<'"+delim+"'"
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


# No firmware, NVRAM or persistent module installation. State snapshots and
# restoration are restricted to the original (installed) Broadcom Wi-Fi stack.
def command(body, marker, seconds=40):
    with session() as port:
        send(port, body + "; echo " + marker + "; stty echo")
        return recv(port, marker, seconds)

def runtime_state():
    result=command(
        "echo __V18_RUNTIME_START__; id -u; uname -r; "
        "if test -e /sys/class/net/wlan0; then echo WLAN_PRESENT; cat /sys/class/net/wlan0/operstate; else echo WLAN_ABSENT; fi; "
        "if systemctl is-active --quiet wpa_supplicant.service; then echo WPA_ACTIVE; else echo WPA_INACTIVE; fi; "
        "if systemctl is-active --quiet bluetooth.service; then echo BT_SERVICE_ACTIVE; else echo BT_SERVICE_INACTIVE; fi; "
        "if test -d /sys/class/bluetooth/hci0; then if hciconfig hci0 2>/dev/null | grep -Fq 'UP RUNNING'; then echo BT_HCI_UP; else echo BT_HCI_DOWN; fi; else echo BT_HCI_DOWN; fi; "
        "for n in brcmfmac_wcc brcmfmac brcmutil; do if test -d /sys/module/$n; then echo MOD_$n; fi; done; "
        "for file in /lib/firmware/brcm/brcmfmac4329-sdio.bin /lib/firmware/brcm/brcmfmac4329-sdio.txt; do "
        "if mountpoint -q $file; then echo OVERLAY_PRESENT; fi; done; "
        "sha256sum /lib/firmware/brcm/brcmfmac4329-sdio.bin /lib/firmware/brcm/brcmfmac4329-sdio.txt "
        "/lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko; "
        "echo __V18_RUNTIME_DONE__",
        "__V18_RUNTIME_END__", 30)
    return result

def require(r, tokens, stage):
    for token in tokens:
        if token not in r:
            raise RuntimeError(stage + ": missing " + token)

def stop_original_radio():
    result=command(
        "echo __V18_PREP_START__; "
        "systemctl stop wpa_supplicant.service; echo STOP_WPA_RC=$?; "
        "timeout -k 2s 12s modprobe -r brcmfmac-wcc; echo REMOVE_WCC_RC=$?; "
        "timeout -k 2s 12s modprobe -r brcmfmac; echo REMOVE_CORE_RC=$?; "
        "timeout -k 2s 12s modprobe -r brcmutil; echo REMOVE_UTIL_RC=$?; "
        "if ! systemctl is-active --quiet wpa_supplicant.service && "
        "test ! -e /sys/class/net/wlan0 && "
        "! grep -Eq '^(brcmfmac_wcc|brcmfmac|brcmutil) ' /proc/modules; "
        "then echo MZ600_V18_RUNTIME_IDLE_PASS; fi",
        "__V18_PREP_END__", 60)
    require(result, ["STOP_WPA_RC=0","REMOVE_WCC_RC=0","REMOVE_CORE_RC=0",
                     "REMOVE_UTIL_RC=0","MZ600_V18_RUNTIME_IDLE_PASS"], "Radio quiesce")

def restore_original_radio():
    result=command(
        "echo __V18_RESTORE_START__; "
        "if mountpoint -q /lib/firmware/brcm/brcmfmac4329-sdio.bin; then "
        "echo RESTORE_REFUSE_UNKNOWN_FW_OVERLAY; else "
        "modprobe brcmutil; echo LOAD_UTIL_RC=$?; "
        "modprobe brcmfmac; echo LOAD_CORE_RC=$?; "
        "modprobe brcmfmac-wcc; echo LOAD_WCC_RC=$?; "
        "systemctl start wpa_supplicant.service; echo START_WPA_RC=$?; "
        "if test -e /sys/class/net/wlan0; then ip link set wlan0 down; echo LINK_DOWN_RC=$?; fi; fi; "
        "if systemctl is-active --quiet wpa_supplicant.service; then echo WPA_ACTIVE_RESTORED; fi; "
        "if test -e /sys/class/net/wlan0; then echo WLAN_RESTORED; cat /sys/class/net/wlan0/operstate; fi; "
        "for n in brcmfmac_wcc brcmfmac brcmutil; do if test -d /sys/module/$n; then echo MOD_RESTORED_$n; fi; done; "
        "sha256sum /lib/firmware/brcm/brcmfmac4329-sdio.bin "
        "/lib/firmware/brcm/brcmfmac4329-sdio.txt "
        "/lib/modules/7.0.0-next-20260422+/kernel/drivers/net/wireless/broadcom/brcm80211/brcmfmac/brcmfmac.ko; "
        "echo __V18_RESTORE_DONE__",
        "__V18_RESTORE_END__", 80)
    require(result,["WPA_ACTIVE_RESTORED","WLAN_RESTORED","down",
                    "MOD_RESTORED_brcmfmac_wcc","MOD_RESTORED_brcmfmac",
                    "MOD_RESTORED_brcmutil",BASE_FW,BASE_NV,BASE_KO],
                    "Original runtime restoration")
    if "RESTORE_REFUSE_UNKNOWN_FW_OVERLAY" in result:
        raise RuntimeError("Unexpected candidate overlay still mounted: inspect Xoom")

def stage_files(fw, ko):
    begin="__V18_STAGE_CHECK_BEGIN__"
    end="__V18_STAGE_CHECK_END__"
    response=command("echo "+begin+"; "
      "if test -e "+RAM_FW+"; then echo FW_EXISTS; else echo FW_MISSING; fi; "
      "if test -e "+RAM_KO+"; then echo KO_EXISTS; else echo KO_MISSING; fi; "
      "echo "+end, "__V18_STAGE_VERIFIED__", 20)
    if "FW_EXISTS" in response or "KO_EXISTS" in response:
        if "FW_EXISTS" not in response or "KO_EXISTS" not in response:
            raise RuntimeError("Only one prior RAM binary present; refuse overwrite")
        ram_probe()
        print("V18_RAM_BINARIES_REUSED_VERIFIED",flush=True)
    else:
        upload(FW,fw,RAM_FW,"FW")
        upload(KO,ko,RAM_KO,"KO")
        ram_probe()
        print("V18_NEW_RAM_BINARIES_VERIFIED",flush=True)

def parse_outcome(t):
    return {
      "event69_terminal_success": bool(re.search(r"MZ600_V18_EVENT69 status=0 ",t)),
      "scan_done_success": bool(re.search(r"MZ600_V18_SCAN_COMPLETION aborted=0 fw_abort=0",t)),
      "watchdog_fired": "MZ600_V18_ESCAN_WATCHDOG_FIRED" in t,
      "alt_events_total": next((int(n) for n in re.findall(r"MZ600_V18_ALTERNATIVE_EVENT_COUNTS total=(\d+)",t)),None),
      "iw_elapsed_ms": next((int(n) for n in re.findall(r"MZ600_V18_IW_PASSIVE_CH36_RC=\d+ ELAPSED_MS=(\d+)",t)),None),
      "userspace_bss": next((int(n) for n in re.findall(r"MZ600_V18_USERSPACE_BSS_COUNT=(\d+)",t)),None),
    }

def main():
    ap=argparse.ArgumentParser(description="V18 one module, selectable event mask per scan")
    ap.add_argument("--masks",default="0,127",help="comma separated decimal masks, each 0..127; max eight tests")
    ap.add_argument("--series",default="ab1",help="unique trial series ID, alphanumeric/hyphen/underscore")
    args=ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,14}",args.series):
        raise RuntimeError("Invalid series identity")
    values=args.masks.split(",")
    if not (1 <= len(values) <= 8) or any(not re.fullmatch(r"(0|[1-9]\d{0,2})",v) or int(v)>127 for v in values):
        raise RuntimeError("Masks must be 1..8 decimal values each in 0..127")
    masks=[int(v) for v in values]
    fw=checked(FW,264140,FW_SHA)
    ko=checked(KO,347380,KO_SHA)
    sh=checked(SH,SH.stat().st_size,SH_SHA).decode("ascii")
    if not sh.endswith("\n") or TAG in sh:
        raise RuntimeError("SHA-pinned owner Bash script invalid")
    runs=ROOT/"runs"
    for i,mask in enumerate(masks,1):
        name=f"{args.series}-{i:02d}-mask{mask:03d}"
        if any((runs/(name+x)).exists() for x in (".attempted",".json",".private.txt")):
            raise RuntimeError("Mask trial already attempted: "+name)
    original=runtime_state()
    require(original,["__V18_RUNTIME_DONE__","\n0\n","7.0.0-next-20260422+",
       "WLAN_PRESENT","down","WPA_ACTIVE","BT_SERVICE_INACTIVE","BT_HCI_DOWN",
       "MOD_brcmfmac_wcc","MOD_brcmfmac","MOD_brcmutil",BASE_FW,BASE_NV,BASE_KO],"Original baseline")
    if "OVERLAY_PRESENT" in original:
        raise RuntimeError("Unexpected firmware overlay; no RF testing")
    print("MZ600_V18_ORIGINAL_RUNTIME_AND_BT_QUIET_VERIFIED",flush=True)
    changed=False
    try:
        changed=True
        stop_original_radio()
        print("MZ600_V18_IDLE_TEST_STATE_PREPARED",flush=True)
        root_probe()
        stage_files(fw,ko)
        lines=sh.splitlines()
        _,syntax_rc=shell_heredoc(lines,0,"syntax",syntax_only=True)
        if syntax_rc:
            raise RuntimeError("On-device guarded shell syntax rejected")
        print("MZ600_V18_DEVICE_BASH_SYNTAX_PASS",flush=True)
        runs.mkdir(parents=True,exist_ok=True)
        for i,mask in enumerate(masks,1):
            trial=f"{args.series}-{i:02d}-mask{mask:03d}"
            print(f"MZ600_V18_BEGIN_TRIAL mask={mask} trial={trial}",flush=True)
            root_probe()
            marker=runs/(trial+".attempted")
            marker.write_text("Never rerun this trial; owner authorization one shot\n",encoding="utf-8")
            transcript,rc=shell_heredoc(lines,mask,trial)
            log_path=runs/(trial+".private.txt")
            log_path.write_text(transcript,encoding="utf-8")
            audit_ok=False
            try:
                root_probe()
                audit_ok=True
            except Exception as e:
                print("MZ600_V18_INDEPENDENT_POSTSTATE_FAILED "+str(e),flush=True)
            required=("MZ600_V18_MASK_READBACK_PASS mask="+str(mask),
                      "MZ600_V18_CONFIG mask="+str(mask)+" trial="+trial,
                      "MZ600_V18_CHANNEL36_NO_IR_NONDFS_PASS",
                      "MZ600_V18_EVENT69_STATUS_COUNTS",
                      "MZ600_V18_NO_ASSOCIATION_OR_DIRECTED_SSID",
                      "MZ600_V18_ORIGINAL_FILES_AND_RADIO_RESTORED")
            markers_ok=all(x in transcript for x in required)
            outcome=parse_outcome(transcript)
            receipt={"test":"V18_RUNTIME_SELECTABLE_EVENT_MASK",
                     "mask":mask,"trial":trial,
                     "firmware_candidate":"4.218.248.44",
                     "module_sha256":KO_SHA,"shell_sha256":SH_SHA,
                     "root_bash_rc":rc,"independent_poststate_ok":audit_ok,
                     "script_cleanup_ok":markers_ok,"permanent_install":False,
                     "transcript_sha256":sha(transcript.encode()),**outcome}
            (runs/(trial+".json")).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
            print("MZ600_V18_TRIAL_RECEIPT "+json.dumps({
                k:receipt[k] for k in ("trial","mask","root_bash_rc",
                "independent_poststate_ok","event69_terminal_success",
                "scan_done_success","watchdog_fired","iw_elapsed_ms","userspace_bss")
            },sort_keys=True),flush=True)
            if rc or not audit_ok or not markers_ok:
                raise RuntimeError("Trial failed isolation/rollback; refusing further scans")
    finally:
        if changed:
            restore_original_radio()
            print("MZ600_V18_ORIGINAL_RUNTIME_RESTORED",flush=True)
    final=runtime_state()
    require(final,["WPA_ACTIVE","WLAN_PRESENT","down","BT_SERVICE_INACTIVE",
        "BT_HCI_DOWN","MOD_brcmfmac_wcc","MOD_brcmfmac","MOD_brcmutil",
        BASE_FW,BASE_NV,BASE_KO],"Final runtime")
    if "OVERLAY_PRESENT" in final:raise RuntimeError("Overlay after restoration")
    print("MZ600_V18_MULTI_MASK_SUITE_COMPLETE_AND_ORIGINAL_RUNTIME_PASS",flush=True)

if __name__=="__main__":
    main()
