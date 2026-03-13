"""Generic Tolgee REST API access tools."""

from __future__ import annotations

import json
from typing import Any

from tolgee_mcp.client import tolgee_client
from tolgee_mcp.server import mcp


VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


@mcp.tool()
async def tolgee_api_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | list[Any] | str | None = None,
    form_data: dict[str, Any] | None = None,
    file_paths: dict[str, str] | None = None,
    include_binary_base64: bool = False,
) -> str:
    """Call any Tolgee REST API endpoint from the official REST docs.

    This is the catch-all tool for Tolgee endpoints that do not yet have a dedicated
    MCP wrapper. Use the relative REST path from `https://docs.tolgee.io/api`, for
    example `/v2/projects/123/labels` or `/v2/projects/123/keys/456/complex-update`.

    Args:
        method: HTTP method. Supported values: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
        path: Relative Tolgee API path starting with `/`.
        params: Optional query parameters. List values are sent as repeated query params.
        body: Optional JSON request body.
        form_data: Optional form fields for non-JSON or multipart requests.
        file_paths: Optional mapping of multipart field name to local file path.
        include_binary_base64: When true, small binary responses are inlined as base64.
    """
    normalized_method = method.upper()
    if normalized_method not in VALID_METHODS:
        supported = ", ".join(sorted(VALID_METHODS))
        return f"Error: Unsupported method '{method}'. Supported methods: {supported}."

    if not path.strip():
        return "Error: path is required."

    if body is not None and (form_data is not None or file_paths is not None):
        return "Error: body cannot be combined with form_data or file_paths."

    try:
        result = await tolgee_client.request(
            method=normalized_method,
            path=path,
            params=params,
            body=body,
            form_data=form_data,
            file_paths=file_paths,
            include_binary_base64=include_binary_base64,
        )
    except ValueError as exc:
        return f"Error: {exc}"

    if isinstance(result, str):
        return result

    return json.dumps(result, indent=2, ensure_ascii=False)
