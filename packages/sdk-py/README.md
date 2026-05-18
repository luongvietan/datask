# datask-py — Official Python SDK for Datask

```python
import datask

client = datask.Client(api_key="dtsk_live_...")

# Layer 1 — free fetch
content = client.fetch("https://example.com")

# Layer 2 — schema extraction
data = client.extract(
    "https://example.com/product",
    schema={"price": "number", "title": "string"},
)

# Layer 3 — natural language extraction
data = client.extract(
    "https://example.com/product",
    prompt="Get me the product price and title",
)
```

Install: `pip install datask-py`
