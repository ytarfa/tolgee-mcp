"""FastMCP server instance and entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tolgee_mcp.client import tolgee_client

# Initialize FastMCP server
mcp = FastMCP("tolgee")

# Register all tools by importing tool modules.
# Each module uses the @mcp.tool() decorator via the mcp instance.
import tolgee_mcp.tools.projects  # noqa: E402, F401
import tolgee_mcp.tools.languages  # noqa: E402, F401
import tolgee_mcp.tools.keys  # noqa: E402, F401
import tolgee_mcp.tools.translations  # noqa: E402, F401
import tolgee_mcp.tools.export_import  # noqa: E402, F401
import tolgee_mcp.tools.tags  # noqa: E402, F401
import tolgee_mcp.tools.rest  # noqa: E402, F401


def main() -> None:
    """Run the Tolgee MCP server."""
    mcp.run(transport="stdio")
