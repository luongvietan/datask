# -*- coding: utf-8 -*-
"""
LlamaIndex Reader integration cho Datask.

Usage:
  from datask.integrations.llama_index import DataskReader

  reader = DataskReader()
  documents = reader.load_data("https://docs.example.com/api")
  # documents: List[Document] ready for LlamaIndex indexing
"""
from __future__ import annotations

from typing import Any

try:
    from llama_index.core import Document
    from llama_index.core.readers.base import BaseReader
except ImportError:
    raise ImportError(
        "LlamaIndex is required. Install with: pip install llama-index-core"
    )

import datask


class DataskReader(BaseReader):
    """
    LlamaIndex reader: load web page content via Datask.
    Supports Cloudflare-protected sites.
    """

    def __init__(
        self,
        api_key: str | None = None,
        extract_prompt: str | None = None,
    ) -> None:
        """
        api_key: Datask API key (defaults to DATASK_API_KEY env var)
        extract_prompt: If set, uses Layer 3 extraction instead of raw Markdown fetch.
        """
        self._api_key = api_key
        self._extract_prompt = extract_prompt

    def load_data(
        self,
        *urls: str,
        extra_info: dict[str, Any] | None = None,
    ) -> list[Document]:
        """
        Load documents from one or more URLs.
        Returns List[Document] with page_label and source metadata.
        """
        client = datask.Client(api_key=self._api_key)
        documents = []

        for url in urls:
            try:
                if self._extract_prompt:
                    raw = client.extract(url, prompt=self._extract_prompt)
                    import json
                    text = json.dumps(raw, indent=2)
                else:
                    text = client.fetch(url)

                documents.append(
                    Document(
                        text=text,
                        metadata={
                            "source": url,
                            "page_label": url,
                            **(extra_info or {}),
                        },
                    )
                )
            except Exception as e:
                documents.append(
                    Document(
                        text=f"Error loading {url}: {e}",
                        metadata={"source": url, "error": str(e)},
                    )
                )

        return documents
