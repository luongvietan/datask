# -*- coding: utf-8 -*-
"""
Datask MCP Server — stdio transport.
Exposes 2 tools: datask_fetch, datask_extract.
API key read from DATASK_API_KEY env var.

Usage:
  uv run python -m datask_mcp
  or: datask-mcp
"""
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

DATASK_API_URL = os.environ.get("DATASK_API_URL", "https://api.datask.run")


def _get_api_key() -> str:
    key = os.environ.get("DATASK_API_KEY", "")
    if not key:
        raise RuntimeError(
            "DATASK_API_KEY environment variable is not set. "
            "Get a free API key at https://datask.run/register"
        )
    return key


async def _fetch(url: str) -> str:
    """Call Datask Layer 1 fetch API."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(
            f"{DATASK_API_URL}/v1/fetch",
            params={"url": url},
            headers={"Authorization": f"Bearer {_get_api_key()}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("content", "")


async def _extract(
    url: str,
    schema: dict[str, Any] | None = None,
    prompt: str | None = None,
) -> dict[str, Any]:
    """Call Datask Layer 2/3 extract API."""
    body: dict[str, Any] = {"url": url}
    if schema:
        body["schema"] = schema
    elif prompt:
        body["prompt"] = prompt
    else:
        raise ValueError("Either schema or prompt must be provided")

    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(
            f"{DATASK_API_URL}/v1/extract",
            json=body,
            headers={
                "Authorization": f"Bearer {_get_api_key()}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()


def create_server() -> Server:
    server = Server("datask")

    @server.list_tools()  # type: ignore[no-untyped-def]
    async def list_tools(request: ListToolsRequest) -> ListToolsResult:
        return ListToolsResult(
            tools=[
                Tool(
                    name="datask_fetch",
                    description=(
                        "Fetch clean Markdown content from any web URL, including Cloudflare-protected sites. "
                        "Returns the page content as Markdown text."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch (must start with http:// or https://)",
                            }
                        },
                        "required": ["url"],
                    },
                ),
                Tool(
                    name="datask_extract",
                    description=(
                        "Extract structured data from a web URL using either a JSON schema (Layer 2) "
                        "or a natural language prompt (Layer 3). "
                        "Returns structured JSON data extracted from the page."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to extract data from",
                            },
                            "schema": {
                                "type": "object",
                                "description": "JSON schema with field names and types (Layer 2). Example: {\"price\": \"number\", \"title\": \"string\"}",
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Natural language description of data to extract (Layer 3). Example: 'Extract product name, price, and availability'",
                            },
                        },
                        "required": ["url"],
                        "oneOf": [
                            {"required": ["schema"]},
                            {"required": ["prompt"]},
                        ],
                    },
                ),
            ]
        )

    @server.call_tool()  # type: ignore[no-untyped-def]
    async def call_tool(request: CallToolRequest) -> CallToolResult:
        name = request.params.name
        args = request.params.arguments or {}

        try:
            if name == "datask_fetch":
                url = args.get("url", "")
                if not url:
                    raise ValueError("url is required")
                content = await _fetch(url)
                return CallToolResult(
                    content=[TextContent(type="text", text=content)]
                )

            elif name == "datask_extract":
                url = args.get("url", "")
                schema = args.get("schema")
                prompt = args.get("prompt")

                if not url:
                    raise ValueError("url is required")
                if not schema and not prompt:
                    raise ValueError("Either schema or prompt is required")

                result = await _extract(url=url, schema=schema, prompt=prompt)
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {e}")],
                isError=True,
            )

    return server


async def run_server() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
