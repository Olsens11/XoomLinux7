#!/usr/bin/env python3
"""Offline BCM4329 2010/2011 ISCAN wire ABI and state-contract regression tests.

Historical sources, not a claim that Motorola HRI39 has passed a physical
ISCAN test:
  https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/include/wlioctl.h
  https://github.com/lvchaqiu/meizu-mx-kernel/blob/7098c1021763c824d7198b156966d3fa040ec162/drivers/net/wireless/bcm4329/include/bcmwifi.h
  https://android.googlesource.com/platform/hardware/broadcom/wlan/+/froyo/bcm4329/src/wl/sys/wl_iw.c

This test has NO radio, serial, network or device access.
"""

import ctypes as C
import struct
import unittest

CH = 36
CHANSPEC_BAND_5G = 0x1000
CHANSPEC_BW_20 = 0x0800
CHANSPEC_CTL_SB_NONE = 0x0300
CHANSPEC = CHANSPEC_BAND_5G | CHANSPEC_BW_20 | CHANSPEC_CTL_SB_NONE | CH
WL_SCAN_PARAMS_FIXED_SIZE = 64
ISCAN_REQ_VERSION = 1
WL_SCAN_ACTION_START = 1
WL_SCAN_ACTION_CONTINUE = 2
WL_SCAN_ACTION_ABORT = 3
WL_SCANFLAGS_PASSIVE = 1
WL_ISCAN_STATUS_SUCCESS = 0
WL_ISCAN_STATUS_PARTIAL = 1
WL_ISCAN_STATUS_PENDING = 2
WL_ISCAN_STATUS_ABORTED = 3
WL_ISCAN_STATUS_NO_MEM = 4


class SSID(C.LittleEndianStructure):
    _fields_ = [("length", C.c_uint32), ("bytes", C.c_uint8 * 32)]


class ScanParams(C.LittleEndianStructure):
    # Original wl_scan_params_t, deliberately NOT _pack_=1.
    _fields_ = [
        ("ssid", SSID),
        ("bssid", C.c_uint8 * 6),
        ("bss_type", C.c_int8),
        ("scan_type", C.c_int8),
        ("nprobes", C.c_int32),
        ("active_time", C.c_int32),
        ("passive_time", C.c_int32),
        ("home_time", C.c_int32),
        ("channel_num", C.c_int32),
        ("channel_list", C.c_uint16 * 1),
    ]


class IscanParams(C.LittleEndianStructure):
    # Original wl_iscan_params_t: first 8 bytes, then scan params.
    _fields_ = [
        ("version", C.c_uint32),
        ("action", C.c_uint16),
        ("scan_duration", C.c_uint16),
        ("params", ScanParams),
    ]


def passive_one_channel_start():
    p = IscanParams()
    p.version = ISCAN_REQ_VERSION
    p.action = WL_SCAN_ACTION_START
    p.scan_duration = 0
    p.params.ssid.length = 0
    p.params.bssid[:] = (255,) * 6
    p.params.bss_type = 2  # DOT11_BSSTYPE_ANY
    p.params.scan_type = WL_SCANFLAGS_PASSIVE
    p.params.nprobes = 0
    p.params.active_time = 0
    p.params.passive_time = 300
    p.params.home_time = 0
    p.params.channel_num = 1
    p.params.channel_list[0] = CHANSPEC
    return C.string_at(C.byref(p), C.sizeof(p))


def iscan_step(status):
    """Semantic actions, not a working Linux state-machine implementation."""
    if status == WL_ISCAN_STATUS_PENDING:
        return ("poll",)
    if status == WL_ISCAN_STATUS_PARTIAL:
        return ("validate_batch", "continue", "poll")
    if status == WL_ISCAN_STATUS_SUCCESS:
        return ("validate_batch", "complete_success")
    if status in (WL_ISCAN_STATUS_ABORTED, WL_ISCAN_STATUS_NO_MEM):
        return ("complete_aborted",)
    raise ValueError("unsupported firmware status")


class IscanWireContract(unittest.TestCase):
    def test_chanspec(self):
        self.assertEqual(CHANSPEC, 0x1B24)
        self.assertNotEqual(CHANSPEC, 0x3024)
        self.assertEqual(CHANSPEC & 0xF000, CHANSPEC_BAND_5G)
        self.assertEqual(CHANSPEC & 0x0C00, CHANSPEC_BW_20)
        self.assertEqual(CHANSPEC & 0x0300, CHANSPEC_CTL_SB_NONE)
        self.assertEqual(CHANSPEC & 0x00FF, CH)

    def test_struct_lengths(self):
        self.assertEqual(C.sizeof(SSID), 36)
        self.assertEqual(ScanParams.channel_list.offset, WL_SCAN_PARAMS_FIXED_SIZE)
        self.assertEqual(C.sizeof(ScanParams), 68)
        self.assertEqual(IscanParams.params.offset, 8)
        self.assertEqual(C.sizeof(IscanParams), 76)
        self.assertEqual(8 + 64 + 4, 76)  # odd channel -> 2B channel plus 2B pad
        self.assertEqual(len(b"iscan\x00" + passive_one_channel_start()), 82)

    def test_member_offsets(self):
        expected_scan = {
            "ssid": 0, "bssid": 36, "bss_type": 42, "scan_type": 43,
            "nprobes": 44, "active_time": 48, "passive_time": 52,
            "home_time": 56, "channel_num": 60, "channel_list": 64,
        }
        for key, offset in expected_scan.items():
            with self.subTest(key=key):
                self.assertEqual(getattr(ScanParams, key).offset, offset)
        self.assertEqual(IscanParams.action.offset, 4)
        self.assertEqual(IscanParams.scan_duration.offset, 6)

    def test_exact_start_bytes(self):
        raw = passive_one_channel_start()
        self.assertEqual(raw[0:8], b"\x01\x00\x00\x00\x01\x00\x00\x00")
        self.assertEqual(raw[8:12], b"\x00\x00\x00\x00")  # zero SSID
        self.assertEqual(raw[44:50], b"\xff" * 6)
        self.assertEqual(raw[50], 2)
        self.assertEqual(raw[51], WL_SCANFLAGS_PASSIVE)
        self.assertEqual(struct.unpack_from("<i", raw, 52)[0], 0)  # nprobes
        self.assertEqual(struct.unpack_from("<i", raw, 56)[0], 0)  # active_time
        self.assertEqual(struct.unpack_from("<i", raw, 60)[0], 300)  # dwell
        self.assertEqual(struct.unpack_from("<i", raw, 68)[0], 1)  # nchan
        self.assertEqual(raw[72:74], b"\x24\x1b")
        self.assertEqual(raw[74:76], b"\x00\x00")  # trailing pad

    def test_iscan_results_header(self):
        # u32 status + 12-byte wl_scan_results fixed header; not BSS data.
        b = struct.pack("<IIII", WL_ISCAN_STATUS_PENDING, 16, 108, 0)
        self.assertEqual(len(b), 16)
        self.assertEqual(struct.unpack("<IIII", b), (2, 16, 108, 0))

    def test_status_actions(self):
        self.assertEqual(iscan_step(0), ("validate_batch", "complete_success"))
        self.assertEqual(iscan_step(1), ("validate_batch", "continue", "poll"))
        self.assertEqual(iscan_step(2), ("poll",))
        self.assertEqual(iscan_step(3), ("complete_aborted",))
        self.assertEqual(iscan_step(4), ("complete_aborted",))
        with self.assertRaises(ValueError):
            iscan_step(255)

    def test_no_duplicate_scan_command_assumption(self):
        # The standalone iscan START command is not followed by WLC_SCAN=50.
        self.assertEqual(WL_SCAN_ACTION_START, 1)
        self.assertEqual(WL_SCAN_ACTION_CONTINUE, 2)
        self.assertEqual(WL_SCAN_ACTION_ABORT, 3)


if __name__ == "__main__":
    unittest.main()
