# -*- coding: utf-8 -*-
"""Entrypoint: python -m datask_mcp"""
import asyncio

from datask_mcp.server import run_server


def main() -> None:
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
