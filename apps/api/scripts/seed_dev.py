# -*- coding: utf-8 -*-
"""
Dev seed script: tạo 1 account + 1 API key để test nhanh.
Usage: uv run --package datask-api python apps/api/scripts/seed_dev.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datask_api.db.session import get_session_factory
from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import api_keys as keys_repo


async def main() -> None:
    factory = get_session_factory()
    async with factory() as session:
        # Tạo account dev
        email = "dev@datask.local"
        account = await accounts_repo.get_by_email(session, email)
        if not account:
            account = await accounts_repo.create(session, email=email, email_verified=True)
            print(f"Created account: {account.id} ({email})")
        else:
            print(f"Account exists: {account.id} ({email})")

        # Tạo API key
        key_data = await keys_repo.create(session, account_id=account.id, label="dev-key")
        await session.commit()

        print("\n=== DEV API KEY ===")
        print(f"  Key ID : {key_data['id']}")
        print(f"  Key    : {key_data['key']}")
        print(f"  Prefix : {key_data['key_preview']}")
        print("\nSave this key — it will NOT be shown again.")
        print(f"\nTest: curl http://localhost:8000/v1/extract -H 'Authorization: Bearer {key_data['key']}' -H 'Content-Type: application/json' -d '{{\"url\": \"https://example.com\", \"schema\": {{\"title\": \"string\"}}}}'")


if __name__ == "__main__":
    asyncio.run(main())
