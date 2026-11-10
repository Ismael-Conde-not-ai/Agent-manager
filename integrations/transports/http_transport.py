from contextlib import AbstractAsyncContextManager
from typing import Any

from mcp.client.streamable_http import streamable_http_client


class StreamableHTTPTransport:
    def __init__(self, url: str):
        self.url = url

    def open(self) -> AbstractAsyncContextManager[tuple[Any]]:
        return streamable_http_client(self.url)