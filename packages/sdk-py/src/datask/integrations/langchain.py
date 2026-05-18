# -*- coding: utf-8 -*-
"""
LangChain Tool wrappers cho Datask.

Usage:
  from datask.integrations.langchain import DataskFetchTool, DataskExtractTool

  tools = [DataskFetchTool(), DataskExtractTool()]
  agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
"""
from __future__ import annotations

from typing import Any, Optional, Type

try:
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "LangChain is required. Install with: pip install langchain"
    )

import datask


class FetchInput(BaseModel):
    url: str = Field(..., description="The URL to fetch content from")


class ExtractInput(BaseModel):
    url: str = Field(..., description="The URL to extract data from")
    prompt: str = Field(..., description="Natural language description of data to extract")


class DataskFetchTool(BaseTool):
    """
    LangChain tool: fetch clean Markdown from any URL via Datask.
    Handles Cloudflare-protected sites automatically.
    """

    name: str = "datask_fetch"
    description: str = (
        "Fetch the content of a web page as clean Markdown text. "
        "Use this to read articles, documentation, or any public web page. "
        "Handles Cloudflare protection automatically. "
        "Input: URL string."
    )
    args_schema: Type[BaseModel] = FetchInput

    def _run(self, url: str) -> str:
        client = datask.Client()
        return client.fetch(url)

    async def _arun(self, url: str) -> str:
        async with datask.AsyncClient() as client:
            return await client.fetch(url)


class DataskExtractTool(BaseTool):
    """
    LangChain tool: extract structured data from any URL via Datask Layer 3.
    """

    name: str = "datask_extract"
    description: str = (
        "Extract structured data from a web page using natural language. "
        "Use this when you need specific data from a page in JSON format. "
        "Input: JSON with 'url' and 'prompt' fields. "
        "Example: {'url': 'https://shop.com/product', 'prompt': 'extract price and name'}"
    )
    args_schema: Type[BaseModel] = ExtractInput

    def _run(self, url: str, prompt: str) -> str:
        import json
        client = datask.Client()
        data = client.extract(url, prompt=prompt)
        return json.dumps(data, indent=2)

    async def _arun(self, url: str, prompt: str) -> str:
        import json
        async with datask.AsyncClient() as client:
            data = await client.extract(url, prompt=prompt)
        return json.dumps(data, indent=2)
