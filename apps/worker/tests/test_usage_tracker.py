# -*- coding: utf-8 -*-
"""Tests cho usage_tracker.record_usage()."""
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError


def test_record_usage_skips_anonymous():
    with patch("datask_worker.usage_tracker.get_session") as mock_get_session:
        from datask_worker.usage_tracker import record_usage

        record_usage(
            account_id=None,
            api_key_id=None,
            url="https://example.com",
            layer=1,
            success=True,
        )
        mock_get_session.assert_not_called()


def test_record_usage_persists_request_id():
    mock_session = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_session)
    mock_cm.__exit__ = MagicMock(return_value=False)

    request_id = "req_01JABCDEFGHJKMNPQRSTVWXYZ0"
    with patch("datask_worker.usage_tracker.get_session", return_value=mock_cm):
        with patch("datask_api.models.db.UsageRecord") as mock_record_cls:
            mock_record_cls.return_value = MagicMock()
            from datask_worker.usage_tracker import record_usage

            record_usage(
                account_id="acc-1",
                api_key_id="key-1",
                url="https://shop.example.com/item",
                layer=2,
                success=True,
                request_id=request_id,
                fetch_strategy="async",
            )

            mock_record_cls.assert_called_once()
            kwargs = mock_record_cls.call_args.kwargs
            assert kwargs["request_id"] == request_id
            assert kwargs["domain"] == "shop.example.com"
            mock_session.add.assert_called_once()


def test_record_usage_truncates_long_domain():
    mock_session = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_session)
    mock_cm.__exit__ = MagicMock(return_value=False)

    long_host = "a" * 300 + ".example.com"
    with patch("datask_worker.usage_tracker.get_session", return_value=mock_cm):
        with patch("datask_api.models.db.UsageRecord") as mock_record_cls:
            mock_record_cls.return_value = MagicMock()
            from datask_worker.usage_tracker import record_usage

            record_usage(
                account_id="acc-1",
                api_key_id="key-1",
                url=f"https://{long_host}/path",
                layer=1,
                success=True,
                request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
            )

            assert len(mock_record_cls.call_args.kwargs["domain"]) == 256


def test_record_usage_ignores_duplicate_request_id():
    mock_session = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_session)
    mock_cm.__exit__ = MagicMock(side_effect=IntegrityError("insert", {}, Exception("dup")))

    with patch("datask_worker.usage_tracker.get_session", return_value=mock_cm):
        with patch("datask_api.models.db.UsageRecord", return_value=MagicMock()):
            from datask_worker.usage_tracker import record_usage

            record_usage(
                account_id="acc-1",
                api_key_id="key-1",
                url="https://example.com",
                layer=1,
                success=True,
                request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
            )
