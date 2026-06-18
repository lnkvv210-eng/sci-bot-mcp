"""Compatibility entrypoint for hosted MCP platforms."""

import os

os.environ.setdefault("MCP_TRANSPORT", "sse")

from server_stdio import main


if __name__ == "__main__":
    main()
