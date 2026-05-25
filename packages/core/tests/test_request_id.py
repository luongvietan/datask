# -*- coding: utf-8 -*-
"""Tests cho request_id generator."""

from datask_core.request_id import (
    REQUEST_ID_PATTERN,
    generate_request_id,
    is_valid_request_id,
)


def test_generate_request_id_format():
    rid = generate_request_id()
    assert REQUEST_ID_PATTERN.match(rid), f"Invalid format: {rid}"


def test_generate_request_id_unique():
    ids = {generate_request_id() for _ in range(100)}
    assert len(ids) == 100


def test_generate_request_id_length():
    rid = generate_request_id()
    assert len(rid) == 30  # req_ (4) + ulid (26)


def test_is_valid_request_id_rejects_malformed():
    assert not is_valid_request_id("req_not-a-ulid")
    assert not is_valid_request_id("req_" + ("A" * 40))
    assert not is_valid_request_id("")


def test_is_valid_request_id_accepts_generated():
    assert is_valid_request_id(generate_request_id())