# Datask MCP Server

Model Context Protocol server for [Datask](https://datask.run) — Web Data API for AI Agents.

## Tools

- **`datask_fetch`** — Fetch clean Markdown from any URL (including Cloudflare-protected sites)
- **`datask_extract`** — Extract structured JSON from any URL using a schema or natural language prompt

## Setup

### 1. Get your API key

Register at [datask.run/register](https://datask.run/register) to get a free API key.

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "datask": {
      "command": "uvx",
      "args": ["datask-mcp"],
      "env": {
        "DATASK_API_KEY": "dtsk_live_YOUR_KEY_HERE"
      }
    }
  }
}
```

### 3. Configure Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "datask": {
      "command": "uvx",
      "args": ["datask-mcp"],
      "env": {
        "DATASK_API_KEY": "dtsk_live_YOUR_KEY_HERE"
      }
    }
  }
}
```

Or use `npx`:

```json
{
  "mcpServers": {
    "datask": {
      "command": "uv",
      "args": ["run", "python", "-m", "datask_mcp"],
      "env": {
        "DATASK_API_KEY": "dtsk_live_YOUR_KEY_HERE"
      }
    }
  }
}
```

## Usage Examples

Once configured, you can ask Claude or your Cursor agent:

- "Fetch the content of https://example.com"
- "Extract product name and price from https://shop.example.com/product/123"
- "Get all news headlines from https://news.example.com"

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATASK_API_KEY` | Yes | Your Datask API key (`dtsk_live_...`) |
| `DATASK_API_URL` | No | Override API URL (default: `https://api.datask.run`) |
