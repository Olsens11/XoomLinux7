#!/usr/bin/env python3
"""Pure-host ABI/layout and malformed-result model for Broadcom BCM4329 v108.

Derived from published Froyo wlioctl.h; NOT actual device payload samples
and NOT an in-kernel validated decoder. No BSSID or SSID output.
"""
import ctypes
import struct
import unittest

MAX_IOCTL_BUFFER = 8192
MAX_RECORDS = 64
RESULT_HEADER = 12
BSS108_SIZE = 124
BSS_VERSION = 108


class Rates(ctypes.Structure):
    _fields_ = [("count", ctypes.c_uint32), ("rates", ctypes.c_uint8 * 16)]


class BSS108(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_uint32), ("length", ctypes.c_uint32),
        ("bssid", ctypes.c_uint8 * 6), ("beacon_period", ctypes.c_uint16),
        ("capability", ctypes.c_uint16), ("ssid_len", ctypes.c_uint8),
        ("ssid", ctypes.c_uint8 * 32), ("rates", Rates),
        ("chanspec", ctypes.c_uint16), ("atim_window", ctypes.c_uint16),
        ("dtim_period", ctypes.c_uint8), ("rssi", ctypes.c_int16),
        ("phy_noise", ctypes.c_int8), ("n_cap", ctypes.c_uint8),
        ("nbss_cap", ctypes.c_uint32), ("ctl_ch", ctypes.c_uint8),
        ("reserved32", ctypes.c_uint32 * 1), ("flags", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
        ("basic_mcs", ctypes.c_uint8 * 16),
        ("ie_offset", ctypes.c_uint16), ("ie_length", ctypes.c_uint32),
    ]


class BadLegacyResult(ValueError):
    pass


def header_u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def validate_old_records(data, *, allowed_channels=frozenset({36})):
    if len(data) < RESULT_HEADER or len(data) > MAX_IOCTL_BUFFER:
        raise BadLegacyResult("result buffer size")
    total, version, count = struct.unpack_from("<III", data)
    if total < RESULT_HEADER or total > len(data) or total > MAX_IOCTL_BUFFER:
        raise BadLegacyResult("reported total buffer size")
    if version != BSS_VERSION or count > MAX_RECORDS:
        raise BadLegacyResult("version or count")
    offset = RESULT_HEADER
    result_count = 0
    for unused in range(count):
        if offset > total or total - offset < BSS108_SIZE:
            raise BadLegacyResult("fixed record truncated")
        ver, length = struct.unpack_from("<II", data, offset)
        if ver != BSS_VERSION or length < BSS108_SIZE or length > total - offset:
            raise BadLegacyResult("bad BSS record header")
        ssid_length = data[offset + BSS108.ssid_len.offset]
        ctl_ch = data[offset + BSS108.ctl_ch.offset]
        ie_offset = struct.unpack_from("<H", data, offset + BSS108.ie_offset.offset)[0]
        ie_length = header_u32(data, offset + BSS108.ie_length.offset)
        if ssid_length > 32:
            raise BadLegacyResult("SSID field exceeds 32 bytes")
        if ctl_ch not in allowed_channels:
            raise BadLegacyResult("channel not validated by firmware and cfg80211")
        if ie_offset < BSS108_SIZE or ie_offset > length:
            raise BadLegacyResult("bad IE offset")
        if ie_length > length - ie_offset:
            raise BadLegacyResult("IE length outside BSS record")
        # Do not read identity bytes or return raw record data.
        offset += length
        result_count += 1
    if offset != total:
        raise BadLegacyResult("unconsumed or overlapping BSS bytes")
    return {"version": version, "validated_bss_count": result_count}


def sample_bss(*, channel=36, ssid_len=0, ie_offset=BSS108_SIZE,
               ies=b"\x00\x01\x00"):
    raw = bytearray(BSS108_SIZE + len(ies))
    struct.pack_into("<II", raw, 0, BSS_VERSION, len(raw))
    raw[BSS108.ssid_len.offset] = ssid_len
    raw[BSS108.ctl_ch.offset] = channel
    struct.pack_into("<H", raw, BSS108.ie_offset.offset, ie_offset)
    struct.pack_into("<I", raw, BSS108.ie_length.offset, len(ies))
    raw[BSS108_SIZE:] = ies
    return bytes(raw)


def sample_reply(*records):
    contents = b"".join(records)
    return struct.pack("<III", RESULT_HEADER + len(contents),
                       BSS_VERSION, len(records)) + contents


class Layout(unittest.TestCase):
    def test_reference_2010_version108_offsets(self):
        self.assertEqual(ctypes.sizeof(BSS108), 124)
        self.assertEqual(BSS108.ssid_len.offset, 18)
        self.assertEqual(BSS108.chanspec.offset, 72)
        self.assertEqual(BSS108.rssi.offset, 78)
        self.assertEqual(BSS108.ctl_ch.offset, 88)
        self.assertEqual(BSS108.ie_offset.offset, 116)
        self.assertEqual(BSS108.ie_length.offset, 120)


class ParserTests(unittest.TestCase):
    def test_single_valid_version108_record(self):
        self.assertEqual(validate_old_records(sample_reply(sample_bss()))["validated_bss_count"], 1)

    def test_two_valid_records(self):
        self.assertEqual(validate_old_records(sample_reply(sample_bss(),sample_bss()))["validated_bss_count"], 2)

    def test_empty_scan_returns_zero(self):
        self.assertEqual(validate_old_records(sample_reply())["validated_bss_count"], 0)

    def test_wrong_version(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<I", raw, 4, 109)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_too_small_record(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<I", raw, 16, 8)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_excessive_record_size(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<I", raw, 16, 8193)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_oversized_result(self):
        with self.assertRaises(BadLegacyResult):
            validate_old_records(b"\0" * (MAX_IOCTL_BUFFER + 1))

    def test_count_too_large(self):
        raw = bytearray(sample_reply())
        struct.pack_into("<I", raw, 8, 65)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_truncated_tail(self):
        with self.assertRaises(BadLegacyResult):
            validate_old_records(sample_reply(sample_bss())[:-1])

    def test_version_in_record_wrong(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<I", raw, 12, 109)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_ie_offset_into_header(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<H", raw, RESULT_HEADER + BSS108.ie_offset.offset, 48)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_ie_length_overrun(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<I", raw, RESULT_HEADER + BSS108.ie_length.offset, 9999)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_ssid_len_exceeds_32(self):
        with self.assertRaises(BadLegacyResult):
            validate_old_records(sample_reply(sample_bss(ssid_len=33)))

    def test_unexpected_channel(self):
        with self.assertRaises(BadLegacyResult):
            validate_old_records(sample_reply(sample_bss(channel=165)))

    def test_reported_total_with_trailing_payload(self):
        raw = bytearray(sample_reply(sample_bss()))
        raw.extend(b"\0")
        struct.pack_into("<I", raw, 0, len(raw))
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_count_claims_extra_record(self):
        raw = bytearray(sample_reply(sample_bss()))
        struct.pack_into("<I", raw, 8, 2)
        with self.assertRaises(BadLegacyResult):
            validate_old_records(bytes(raw))

    def test_oversized_reply_bound(self):
        with self.assertRaises(BadLegacyResult):
            validate_old_records(b"\0" * 8300)


if __name__ == "__main__":
    unittest.main(verbosity=2)
