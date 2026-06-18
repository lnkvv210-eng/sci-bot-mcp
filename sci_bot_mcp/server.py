"""Hosted HTTP/SSE entrypoint for ModelScope deployments."""

import os

from server_stdio import mcp


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "sse").strip().strip('"').lower()
    if transport == "streamable_http":
        transport = "streamable-http"

    if transport not in {"sse", "streamable-http"}:
        transport = "sse"

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

