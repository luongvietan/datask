# -*- coding: utf-8 -*-
"""Generate unique request IDs for API traceability."""
from __future__ import annotations

import os
import re
import time

# Crockford's Base32 (ULID alphabet)
_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
REQUEST_ID_PATTERN = re.compile(r"^req_[0-9A-HJKMNP-TV-Z]{26}$")
REQUEST_ID_MAX_LENGTH = 32


def is_valid_request_id(value: str) -> bool:
    """Return True when value matches req_{26-char-ulid} and fits DB column."""
    if not value or len(value) > REQUEST_ID_MAX_LENGTH:
        return False
    return bool(REQUEST_ID_PATTERN.match(value))


def _encode_base32(value: int, length: int) -> str:
    chars: list[str] = []
    for _ in range(length):
        chars.append(_BASE32[value & 0x1F])
        value >>= 5
    return "".join(reversed(chars))


def generate_request_id() -> str:
    """
    Generate a sortable request ID: req_{26-char-ulid}.
    Format fits VARCHAR(32) in DB (4 + 26 = 30 chars).
    """
    timestamp_ms = int(time.time() * 1000)
    randomness = int.from_bytes(os.urandom(10), "big")
    ulid = _encode_base32(timestamp_ms, 10) + _encode_base32(randomness, 16)
    return f"req_{ulid}"
