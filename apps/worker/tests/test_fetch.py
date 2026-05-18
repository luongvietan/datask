# -*- coding: utf-8 -*-
"""Unit tests cho fetch task."""
import pytest


def test_is_safe_url_blocks_localhost():
    from datask_worker.tasks.fetch import _is_safe_url
    assert _is_safe_url("http://localhost/admin") is False
    assert _is_safe_url("http://127.0.0.1/secret") is False


def test_is_safe_url_blocks_private_ip():
    from datask_worker.tasks.fetch import _is_safe_url
    assert _is_safe_url("http://192.168.1.1/admin") is False
    assert _is_safe_url("http://10.0.0.1/data") is False
    assert _is_safe_url("http://172.16.0.1/internal") is False


def test_is_safe_url_allows_public():
    from datask_worker.tasks.fetch import _is_safe_url
    # These should pass the prefix check (DNS might fail in CI but prefix is safe)
    assert _is_safe_url("https://example.com") is True
    assert _is_safe_url("https://docs.python.org/3/") is True


def test_html_to_markdown():
    from datask_worker.tasks.fetch import _html_to_markdown
    html = "<h1>Title</h1><p>Some text here.</p>"
    md = _html_to_markdown(html)
    assert "Title" in md
    assert "Some text here" in md


def test_get_cache_key():
    from datask_worker.tasks.fetch import _get_cache_key
    key1 = _get_cache_key("https://example.com")
    key2 = _get_cache_key("https://example.com")
    key3 = _get_cache_key("https://other.com")
    assert key1 == key2
    assert key1 != key3
    assert key1.startswith("fetch:cache:")
