"""Compatibility entrypoint for hosted MCP platforms."""

import os

os.environ.setdefault("MCP_TRANSPORT", "streamable-http")

from server_stdio import main


if __name__ == "__main__":
    main()
