# -*- coding: utf-8 -*-
"""
Datask Python SDK — Basic examples.
Run: DATASK_API_KEY=dtsk_live_... python examples/python_basic.py
"""
import asyncio
import datask


def example_fetch():
    """Layer 1: Fetch Markdown content."""
    client = datask.Client()
    content = client.fetch("https://example.com")
    print("=== Fetch Result ===")
    print(content[:500])


def example_extract_schema():
    """Layer 2: Extract structured data with schema."""
    client = datask.Client()
    data = client.extract(
        "https://example.com",
        schema={"title": "string", "description": "string"},
    )
    print("\n=== Extract Schema (Layer 2) ===")
    print(data)


def example_extract_prompt():
    """Layer 3: Extract with natural language prompt."""
    client = datask.Client()
    data = client.extract(
        "https://news.ycombinator.com",
        prompt="Get the top 5 story titles and their point counts",
        example={"stories": [{"title": "...", "points": 0}]},
    )
    print("\n=== Extract Prompt (Layer 3) ===")
    print(data)


async def example_async():
    """Async client example."""
    async with datask.AsyncClient() as client:
        content = await client.fetch("https://example.com")
        print("\n=== Async Fetch ===")
        print(content[:300])


if __name__ == "__main__":
    example_fetch()
    example_extract_schema()
    # Uncomment for Layer 3 (requires OpenAI key on server):
    # example_extract_prompt()
    asyncio.run(example_async())
