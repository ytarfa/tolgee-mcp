"""Tolgee API HTTP client."""

from __future__ import annotations

import base64
import contextlib
import json
import mimetypes
import os
from pathlib import Path
from typing import Any

import httpx


DEFAULT_API_URL = "https://app.tolgee.io"
REQUEST_TIMEOUT = 30.0
INLINE_BINARY_LIMIT = 32 * 1024


class TolgeeClient:
    """Async HTTP client for the Tolgee REST API."""

    def __init__(self) -> None:
        self.api_url = os.environ.get("TOLGEE_API_URL", DEFAULT_API_URL).rstrip("/")
        self.api_key = os.environ.get("TOLGEE_API_KEY", "")
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                headers={
                    "X-API-Key": self.api_key,
                    "Accept": "application/json",
                },
                timeout=REQUEST_TIMEOUT,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Request methods ──────────────────────────────────────────────

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any] | str:
        """Send a GET request and return parsed JSON or error string."""
        return await self._request("GET", path, params=params)

    async def post(self, path: str, body: Any = None, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any] | str:
        """Send a POST request and return parsed JSON or error string."""
        return await self._request("POST", path, body=body, params=params)

    async def put(self, path: str, body: Any = None) -> dict[str, Any] | list[Any] | str:
        """Send a PUT request and return parsed JSON or error string."""
        return await self._request("PUT", path, body=body)

    async def patch(
        self, path: str, body: Any = None
    ) -> dict[str, Any] | list[Any] | str:
        """Send a PATCH request and return parsed JSON or error string."""
        return await self._request("PATCH", path, body=body)

    async def delete(self, path: str, body: Any = None) -> dict[str, Any] | list[Any] | str:
        """Send a DELETE request and return parsed JSON or error string."""
        return await self._request("DELETE", path, body=body)

    async def post_raw(self, path: str, body: Any = None, params: dict[str, Any] | None = None) -> httpx.Response | str:
        """Send a POST request and return the raw response (for binary data like exports)."""
        return await self.request_raw("POST", path, body=body, params=params)

    async def request(
        self,
        method: str,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
        form_data: dict[str, Any] | None = None,
        file_paths: dict[str, str] | None = None,
        include_binary_base64: bool = False,
    ) -> dict[str, Any] | list[Any] | str:
        """Send an arbitrary request and return parsed content or an error string."""
        response = await self.request_raw(
            method=method,
            path=path,
            body=body,
            params=params,
            form_data=form_data,
            file_paths=file_paths,
        )
        if isinstance(response, str):
            return response
        return self.parse_response(
            response, include_binary_base64=include_binary_base64
        )

    async def request_raw(
        self,
        method: str,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
        form_data: dict[str, Any] | None = None,
        file_paths: dict[str, str] | None = None,
    ) -> httpx.Response | str:
        """Send an arbitrary request and return the raw response."""
        if not self.is_configured:
            return "Error: TOLGEE_API_KEY is not configured. Set the TOLGEE_API_KEY environment variable."
        try:
            if body is not None and (form_data is not None or file_paths is not None):
                return "Error: JSON body cannot be combined with form_data or file_paths."
            client = await self._get_client()
            kwargs: dict[str, Any] = {}
            if body is not None:
                kwargs["json"] = body
            if params is not None:
                kwargs["params"] = params
            if form_data is not None:
                kwargs["data"] = form_data

            with contextlib.ExitStack() as stack:
                if file_paths:
                    kwargs["files"] = {
                        field: (
                            Path(file_path).name,
                            stack.enter_context(open(file_path, "rb")),
                            mimetypes.guess_type(file_path)[0]
                            or "application/octet-stream",
                        )
                        for field, file_path in file_paths.items()
                    }
                response = await client.request(
                    method.upper(), self._normalize_path(path), **kwargs
                )
                response.raise_for_status()
                return response
        except httpx.TimeoutException:
            return f"Error: Request to {path} timed out after {REQUEST_TIMEOUT}s."
        except httpx.HTTPStatusError as exc:
            return _format_http_error(exc)
        except FileNotFoundError as exc:
            return f"Error: File not found: {exc.filename}"
        except OSError as exc:
            return f"Error: Failed to read upload file: {exc}"
        except httpx.HTTPError as exc:
            return f"Error: HTTP request failed: {exc}"

    async def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        return await self.request(method, path, body=body, params=params)

    # ── Pagination helpers ───────────────────────────────────────────

    @staticmethod
    def parse_response(
        response: httpx.Response, include_binary_base64: bool = False
    ) -> dict[str, Any] | list[Any] | str:
        """Convert an HTTP response into a JSON/text/binary payload."""
        if not response.content:
            return {"success": True, "status_code": response.status_code}

        content_type = response.headers.get("content-type", "")
        media_type = content_type.split(";", 1)[0].strip().lower()

        if media_type == "application/json" or media_type.endswith("+json"):
            return response.json()

        if media_type.startswith("text/") or media_type in {
            "application/xml",
            "text/xml",
            "application/yaml",
            "text/yaml",
        }:
            return {
                "content_type": media_type or "text/plain",
                "text": response.text,
            }

        payload: dict[str, Any] = {
            "content_type": media_type or "application/octet-stream",
            "size_bytes": len(response.content),
        }
        filename = _extract_filename(
            response.headers.get("content-disposition", "")
        )
        if filename:
            payload["filename"] = filename
        if include_binary_base64:
            if len(response.content) > INLINE_BINARY_LIMIT:
                payload["base64_truncated"] = True
                payload["inline_limit_bytes"] = INLINE_BINARY_LIMIT
            else:
                payload["base64"] = base64.b64encode(response.content).decode(
                    "ascii"
                )
        return payload

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize request paths to avoid absolute URL overrides."""
        normalized = path.strip()
        if "://" in normalized:
            raise ValueError("Absolute URLs are not allowed. Use a relative API path.")
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        return normalized

    @staticmethod
    def format_page_info(data: dict[str, Any] | list[Any] | str) -> str:
        """Extract pagination info from a Tolgee paginated response."""
        if not isinstance(data, dict):
            return ""
        page_info = data.get("page", {})
        total_elements = page_info.get("totalElements", "?")
        total_pages = page_info.get("totalPages", "?")
        current_page = page_info.get("number", "?")
        size = page_info.get("size", "?")
        return f"Page {current_page}/{total_pages} (total: {total_elements}, page size: {size})"

    @staticmethod
    def get_embedded(data: dict[str, Any] | list[Any] | str, key: str) -> list[dict[str, Any]]:
        """Extract items from a Tolgee paginated response's _embedded field."""
        if not isinstance(data, dict):
            return []
        embedded = data.get("_embedded", {})
        return embedded.get(key, [])


def _format_http_error(exc: httpx.HTTPStatusError) -> str:
    """Format an HTTP error into a human-readable string."""
    status = exc.response.status_code
    try:
        body = exc.response.json()
        if isinstance(body, dict):
            message = body.get("message", body.get("error", json.dumps(body)))
        else:
            message = str(body)
    except Exception:
        message = exc.response.text[:500] if exc.response.text else "No response body"
    return f"Error {status}: {message}"


def _extract_filename(content_disposition: str) -> str | None:
    """Extract a filename from a Content-Disposition header."""
    if "filename=" not in content_disposition:
        return None

    filename = content_disposition.split("filename=", 1)[1].strip()
    if filename.startswith('"') and filename.endswith('"'):
        filename = filename[1:-1]
    if filename.startswith("'") and filename.endswith("'"):
        filename = filename[1:-1]
    return filename or None


# Module-level singleton
tolgee_client = TolgeeClient()
