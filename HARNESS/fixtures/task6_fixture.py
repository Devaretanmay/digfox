"""Fixture and acceptance test for Task 6: Uv #22510."""

import unittest
from typing import Dict, Optional


def unpatched_parse_ustar_gname(raw_bytes: bytes, pax_headers: Optional[Dict[str, str]] = None) -> str:
    # Strictly requires NUL terminator in 32-byte buffer
    if len(raw_bytes) != 32:
        raise ValueError("Invalid field width")
    if b'\x00' not in raw_bytes:
        raise ValueError("invalid ustar gname field: missing NUL terminator")
    return raw_bytes.split(b'\x00', 1)[0].decode('utf-8')


def safe_parse_ustar_gname(raw_bytes: bytes, pax_headers: Optional[Dict[str, str]] = None) -> str:
    # 1. PAX header takes precedence if present
    if pax_headers and 'gname' in pax_headers:
        return pax_headers['gname']
    if len(raw_bytes) != 32:
        raise ValueError("Invalid field width")
    # 2. If NUL terminator present, truncate at NUL; else decode full 32 bytes
    if b'\x00' in raw_bytes:
        return raw_bytes.split(b'\x00', 1)[0].decode('utf-8')
    return raw_bytes.decode('utf-8')


class TestTask6Acceptance(unittest.TestCase):
    def test_reproduction_32_byte_non_terminated(self):
        raw = b'g' * 32
        with self.assertRaises(ValueError) as ctx:
            unpatched_parse_ustar_gname(raw)
        self.assertIn("missing NUL terminator", str(ctx.exception))

    def test_safe_parsing_32_byte_without_nul(self):
        raw = b'g' * 32
        res = safe_parse_ustar_gname(raw)
        self.assertEqual(res, 'g' * 32)

    def test_safe_parsing_pax_override(self):
        raw = b'g' * 32
        pax = {'gname': 'extremely_long_domain_group_name_exceeding_standard_limits'}
        res = safe_parse_ustar_gname(raw, pax_headers=pax)
        self.assertEqual(res, 'extremely_long_domain_group_name_exceeding_standard_limits')

    def test_regression_safety_standard_names(self):
        raw = b'users\x00' + b'\x00' * 26
        self.assertEqual(safe_parse_ustar_gname(raw), 'users')


if __name__ == '__main__':
    unittest.main()
