#!/usr/bin/env python3
"""Host-only, deterministic legacy BCM4329 scan protocol safety-model tests.

Reference: original Broadcom Froyo wlioctl.h (scan-results envelope, BSS v108)
and current brcmfmac cfg80211.c (BSS v109, escan lifecycle). This is a model,
not yet a Linux driver/KUnit implementation, and does not use real RF data.
"""
import struct
import unittest

MAX_REPLY = 65000  # mirror bounded brcmfmac escan buffer; no unbounded firmware copies
MAX_BSS_COUNT = 256
WIRE_HEADER = 12
WIRE_BSS_MIN_HEADER = 8  # BSS version and length only; full v108 layout unverified on actual firmware
LEGACY_BSS_VERSION = 108
MODERN_BSS_VERSION = 109


class MalformedScanReply(ValueError):
    pass


def validate_envelope(raw: bytes, *, permitted_versions=(108, 109)):
    """Validate only length/count/record boundaries, NOT fields or IEs.

    Future C parser must validate the version-specific full record layout,
    IE offset and IE length BEFORE invoking cfg80211_inform_bss_data().
    """
    if len(raw) < WIRE_HEADER or len(raw) > MAX_REPLY:
        raise MalformedScanReply("reply length outside permitted bounds")
    total, version, count = struct.unpack_from("<III", raw)
    if total < WIRE_HEADER or total > len(raw) or total > MAX_REPLY:
        raise MalformedScanReply("firmware buflen outside received bounds")
    if version not in permitted_versions:
        raise MalformedScanReply("unrecognized BSS version")
    if count > MAX_BSS_COUNT:
        raise MalformedScanReply("excessive BSS count")
    offset = WIRE_HEADER
    parsed = 0
    for _ in range(count):
        if total - offset < WIRE_BSS_MIN_HEADER:
            raise MalformedScanReply("truncated BSS header")
        rec_version, rec_length = struct.unpack_from("<II", raw, offset)
        if rec_version != version or rec_version not in permitted_versions:
            raise MalformedScanReply("inconsistent BSS record version")
        if rec_length < WIRE_BSS_MIN_HEADER or rec_length > total - offset:
            raise MalformedScanReply("invalid per-record length")
        offset += rec_length
        parsed += 1
    if offset != total:
        raise MalformedScanReply("unconsumed or overlapping BSS bytes")
    return {"version": version, "count": parsed, "consumed": offset}


class ScanLifecycle:
    """Exactly-once completion model, not kernel concurrency code."""
    def __init__(self):
        self.state = "idle"
        self.completions = []
        self.accepted = False

    def begin(self):
        if self.state != "idle":
            return False
        self.state = "starting"
        self.accepted = False
        return True

    def firmware_start_result(self, result):
        if self.state != "starting":
            return False
        if result:
            # cfg80211 .scan() returns error; no scan_done allowed.
            self.state = "idle"
            self.accepted = False
            return False
        self.state = "scanning"
        self.accepted = True
        return True

    def finish(self, aborted):
        if self.state != "scanning" or not self.accepted:
            return False
        # Ownership cleared before any subsequent timer/event.
        self.state = "idle"
        self.accepted = False
        self.completions.append(bool(aborted))
        return True

    def timeout(self):
        return self.finish(aborted=True)

    def cancel(self):
        return self.finish(aborted=True)


def bss_header(version, *, body=b""):
    return struct.pack("<II", version, WIRE_BSS_MIN_HEADER + len(body)) + body


def reply(version, records=(), *, header_count=None, trailing=b""):
    payload = b"".join(records)
    return struct.pack("<III", WIRE_HEADER + len(payload), version,
                       len(records) if header_count is None else header_count) + payload + trailing


class EnvelopeTests(unittest.TestCase):
    def test_empty_legacy(self):
        self.assertEqual(validate_envelope(reply(108))["count"], 0)

    def test_empty_modern(self):
        self.assertEqual(validate_envelope(reply(109))["version"], 109)

    def test_two_valid_legacy_envelopes(self):
        records = [bss_header(108, body=b"ABCD"), bss_header(108, body=b"DATA")]
        self.assertEqual(validate_envelope(reply(108, records))["count"], 2)

    def test_truncated_global_header(self):
        with self.assertRaises(MalformedScanReply):
            validate_envelope(b"\x00" * 11)

    def test_declared_length_larger_than_buffer(self):
        raw = bytearray(reply(108))
        struct.pack_into("<I", raw, 0, 300)
        with self.assertRaises(MalformedScanReply):
            validate_envelope(bytes(raw))

    def test_unsupported_version_fail_closed(self):
        for version in (0, 107, 110, 65535):
            with self.subTest(version=version), self.assertRaises(MalformedScanReply):
                validate_envelope(reply(version))

    def test_claimed_count_exceeds_present_records(self):
        with self.assertRaises(MalformedScanReply):
            validate_envelope(reply(108, [bss_header(108)], header_count=2))

    def test_claimed_count_above_limit(self):
        with self.assertRaises(MalformedScanReply):
            validate_envelope(reply(108, header_count=257))

    def test_zero_length_record(self):
        raw = struct.pack("<III", 20, 108, 1) + struct.pack("<II", 108, 0)
        with self.assertRaises(MalformedScanReply):
            validate_envelope(raw)

    def test_record_overflow(self):
        raw = struct.pack("<III", 20, 108, 1) + struct.pack("<II", 108, 4096)
        with self.assertRaises(MalformedScanReply):
            validate_envelope(raw)

    def test_record_version_mismatch(self):
        with self.assertRaises(MalformedScanReply):
            validate_envelope(reply(108, [bss_header(109)]))

    def test_trailing_data_inside_declared_buffer_rejected(self):
        raw = bytearray(reply(108, [bss_header(108)]))
        raw.extend(b"xx")
        struct.pack_into("<I", raw, 0, len(raw))
        with self.assertRaises(MalformedScanReply):
            validate_envelope(bytes(raw))

    def test_oversized_response_rejected(self):
        with self.assertRaises(MalformedScanReply):
            validate_envelope(b"\x00" * (MAX_REPLY + 1))

    def test_bytes_after_declared_length_not_consumed(self):
        parsed = validate_envelope(reply(108, [bss_header(108)], trailing=b"\x00" * 8))
        self.assertEqual(parsed["consumed"], 20)

    def test_corrupt_partial_second_record(self):
        raw = struct.pack("<III", 24, 108, 2) + bss_header(108) + b"\x00" * 4
        with self.assertRaises(MalformedScanReply):
            validate_envelope(raw)


class LifecycleTests(unittest.TestCase):
    def test_success_exactly_once(self):
        scan = ScanLifecycle()
        self.assertTrue(scan.begin())
        self.assertTrue(scan.firmware_start_result(0))
        self.assertTrue(scan.finish(False))
        self.assertFalse(scan.finish(False))
        self.assertEqual(scan.completions, [False])

    def test_start_failure_has_no_scan_done(self):
        scan = ScanLifecycle()
        self.assertTrue(scan.begin())
        self.assertFalse(scan.firmware_start_result(-52))
        self.assertEqual(scan.completions, [])
        self.assertEqual(scan.state, "idle")

    def test_timeout_then_late_event_does_not_double_complete(self):
        scan = ScanLifecycle()
        scan.begin()
        scan.firmware_start_result(0)
        self.assertTrue(scan.timeout())
        self.assertFalse(scan.finish(False))
        self.assertEqual(scan.completions, [True])

    def test_abort_then_timeout_does_not_double_complete(self):
        scan = ScanLifecycle()
        scan.begin()
        scan.firmware_start_result(0)
        self.assertTrue(scan.cancel())
        self.assertFalse(scan.timeout())
        self.assertEqual(scan.completions, [True])

    def test_concurrent_scan_refused(self):
        scan = ScanLifecycle()
        self.assertTrue(scan.begin())
        self.assertFalse(scan.begin())
        scan.firmware_start_result(0)
        self.assertFalse(scan.begin())
        scan.cancel()
        self.assertTrue(scan.begin())

    def test_completion_before_scan_accepted_refused(self):
        scan = ScanLifecycle()
        scan.begin()
        self.assertFalse(scan.finish(False))
        self.assertEqual(scan.completions, [])

    def test_valid_second_scan_completes_once(self):
        scan = ScanLifecycle()
        scan.begin()
        scan.firmware_start_result(0)
        scan.finish(False)
        scan.begin()
        scan.firmware_start_result(0)
        scan.finish(True)
        self.assertEqual(scan.completions, [False, True])


if __name__ == "__main__":
    unittest.main(verbosity=2)
