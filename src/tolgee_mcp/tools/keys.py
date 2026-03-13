"""Localization key management tools."""

from __future__ import annotations

import json
from typing import Any

from tolgee_mcp.server import mcp
from tolgee_mcp.client import tolgee_client


@mcp.tool()
async def list_keys(
    project_id: int,
    page: int = 0,
    size: int = 20,
    branch: str | None = None,
    sort: list[str] | None = None,
) -> str:
    """List localization keys in a Tolgee project.

    Args:
        project_id: The numeric ID of the project.
        page: Page number (0-indexed, default 0).
        size: Number of keys per page (default 20).
        branch: Optional branch name.
        sort: Optional sort expressions supported by Tolgee pageable endpoints (e.g. ["name,asc"]).
    """
    params = {"page": page, "size": size}
    if branch:
        params["branch"] = branch
    if sort:
        params["sort"] = sort
    result = await tolgee_client.get(
        f"/v2/projects/{project_id}/keys", params=params
    )
    if isinstance(result, str):
        return result

    keys = tolgee_client.get_embedded(result, "keys")
    if not keys:
        return "No keys found in this project."

    lines = []
    for k in keys:
        ns = k.get("namespace", "")
        ns_str = f" [ns: {ns}]" if ns else ""
        tags = k.get("tags", [])
        tag_names = [t.get("name", "") for t in tags] if tags else []
        tag_str = f" tags: {', '.join(tag_names)}" if tag_names else ""
        lines.append(
            f"- `{k.get('name', '')}` (ID: {k.get('id')}){ns_str}{tag_str}"
        )

    page_info = tolgee_client.format_page_info(result)
    return f"Keys ({page_info}):\n" + "\n".join(lines)


@mcp.tool()
async def select_keys(
    project_id: int,
    filter_state: list[str] | None = None,
    languages: list[str] | None = None,
    search: str | None = None,
    filter_key_name: list[str] | None = None,
    filter_key_id: list[int] | None = None,
    filter_untranslated_any: bool | None = None,
    filter_translated_any: bool | None = None,
    filter_untranslated_in_lang: str | None = None,
    filter_translated_in_lang: str | None = None,
    filter_auto_translated_in_lang: list[str] | None = None,
    filter_has_screenshot: bool | None = None,
    filter_has_no_screenshot: bool | None = None,
    filter_namespace: list[str] | None = None,
    filter_no_namespace: list[str] | None = None,
    filter_tag: list[str] | None = None,
    filter_no_tag: list[str] | None = None,
    filter_outdated_language: list[str] | None = None,
    filter_not_outdated_language: list[str] | None = None,
    filter_revision_id: list[int] | None = None,
    filter_failed_keys_of_job: int | None = None,
    filter_task_number: list[int] | None = None,
    filter_task_keys_not_done: bool | None = None,
    filter_task_keys_done: bool | None = None,
    filter_has_unresolved_comments_in_lang: list[str] | None = None,
    filter_has_comments_in_lang: list[str] | None = None,
    filter_label: list[str] | None = None,
    filter_has_suggestions_in_lang: list[str] | None = None,
    filter_has_no_suggestions_in_lang: list[str] | None = None,
    branch: str | None = None,
    filter_deleted_by_user_id: list[int] | None = None,
) -> str:
    """Select key IDs using Tolgee's translation-view filters.

    All optional filter arguments map 1:1 to the official `GET /v2/projects/{projectId}/keys/select`
    query parameters from the Tolgee REST API docs. For repeated query params, pass a list.
    `filter_state` expects values in `languageTag,state` format such as `["en,UNTRANSLATED"]`.

    Args:
        project_id: The numeric ID of the project.
        filter_state: Translation-state filters in `languageTag,state` format.
        languages: Languages included in filtering logic.
        search: Search string applied to key names or translation text.
        filter_key_name: Restrict to explicit key names.
        filter_key_id: Restrict to explicit key IDs.
        filter_untranslated_any: Select keys missing a translation in any returned language.
        filter_translated_any: Select keys translated in any language.
        filter_untranslated_in_lang: Select keys untranslated in a specific language.
        filter_translated_in_lang: Select keys translated in a specific language.
        filter_auto_translated_in_lang: Select keys auto-translated in specific languages.
        filter_has_screenshot: Select keys with screenshots.
        filter_has_no_screenshot: Select keys without screenshots.
        filter_namespace: Select keys in specific namespaces.
        filter_no_namespace: Exclude specific namespaces.
        filter_tag: Select keys with specific tags.
        filter_no_tag: Exclude specific tags.
        filter_outdated_language: Select keys outdated in specific languages.
        filter_not_outdated_language: Select keys not outdated in specific languages.
        filter_revision_id: Select keys affected by specific revision IDs.
        filter_failed_keys_of_job: Select keys that failed in a batch job.
        filter_task_number: Select keys in specific tasks.
        filter_task_keys_not_done: Select task keys not done.
        filter_task_keys_done: Select task keys done.
        filter_has_unresolved_comments_in_lang: Select keys with unresolved comments in languages.
        filter_has_comments_in_lang: Select keys with comments in languages.
        filter_label: Select keys with labels.
        filter_has_suggestions_in_lang: Select keys with suggestions in languages.
        filter_has_no_suggestions_in_lang: Select keys with no suggestions in languages.
        branch: Optional branch name.
        filter_deleted_by_user_id: Filter trashed keys by deleter user IDs.
    """
    params: dict[str, Any] = {}
    _set_param(params, "filterState", filter_state)
    _set_param(params, "languages", languages)
    _set_param(params, "search", search)
    _set_param(params, "filterKeyName", filter_key_name)
    _set_param(params, "filterKeyId", filter_key_id)
    _set_param(params, "filterUntranslatedAny", filter_untranslated_any)
    _set_param(params, "filterTranslatedAny", filter_translated_any)
    _set_param(params, "filterUntranslatedInLang", filter_untranslated_in_lang)
    _set_param(params, "filterTranslatedInLang", filter_translated_in_lang)
    _set_param(
        params, "filterAutoTranslatedInLang", filter_auto_translated_in_lang
    )
    _set_param(params, "filterHasScreenshot", filter_has_screenshot)
    _set_param(params, "filterHasNoScreenshot", filter_has_no_screenshot)
    _set_param(params, "filterNamespace", filter_namespace)
    _set_param(params, "filterNoNamespace", filter_no_namespace)
    _set_param(params, "filterTag", filter_tag)
    _set_param(params, "filterNoTag", filter_no_tag)
    _set_param(params, "filterOutdatedLanguage", filter_outdated_language)
    _set_param(
        params, "filterNotOutdatedLanguage", filter_not_outdated_language
    )
    _set_param(params, "filterRevisionId", filter_revision_id)
    _set_param(params, "filterFailedKeysOfJob", filter_failed_keys_of_job)
    _set_param(params, "filterTaskNumber", filter_task_number)
    _set_param(params, "filterTaskKeysNotDone", filter_task_keys_not_done)
    _set_param(params, "filterTaskKeysDone", filter_task_keys_done)
    _set_param(
        params,
        "filterHasUnresolvedCommentsInLang",
        filter_has_unresolved_comments_in_lang,
    )
    _set_param(params, "filterHasCommentsInLang", filter_has_comments_in_lang)
    _set_param(params, "filterLabel", filter_label)
    _set_param(
        params, "filterHasSuggestionsInLang", filter_has_suggestions_in_lang
    )
    _set_param(
        params,
        "filterHasNoSuggestionsInLang",
        filter_has_no_suggestions_in_lang,
    )
    _set_param(params, "branch", branch)
    _set_param(params, "filterDeletedByUserId", filter_deleted_by_user_id)

    result = await tolgee_client.get(
        f"/v2/projects/{project_id}/keys/select", params=params
    )
    if isinstance(result, str):
        return result

    if not isinstance(result, dict):
        return json.dumps(result, indent=2, ensure_ascii=False)

    key_ids = result.get("ids", [])
    if not key_ids:
        return "No key IDs matched the provided filters."

    return (
        f"Selected {len(key_ids)} key(s):\n"
        + "\n".join(f"- {key_id}" for key_id in key_ids)
    )


@mcp.tool()
async def search_keys(project_id: int, search: str) -> str:
    """Search for localization keys by name in a Tolgee project.

    Args:
        project_id: The numeric ID of the project.
        search: Search query string to match against key names.
    """
    params = {"search": search}
    result = await tolgee_client.get(
        f"/v2/projects/{project_id}/keys/search", params=params
    )
    if isinstance(result, str):
        return result

    # The search endpoint may return different structures
    if isinstance(result, list):
        if not result:
            return f"No keys found matching '{search}'."
        return json.dumps(result, indent=2)

    keys = tolgee_client.get_embedded(result, "keys")
    if not keys:
        return f"No keys found matching '{search}'."

    lines = []
    for k in keys:
        lines.append(f"- `{k.get('name', '')}` (ID: {k.get('id')})")

    return f"Keys matching '{search}':\n" + "\n".join(lines)


@mcp.tool()
async def create_key(
    project_id: int,
    name: str,
    namespace: str | None = None,
    translations: dict[str, str] | None = None,
) -> str:
    """Create a new localization key in a Tolgee project.

    Args:
        project_id: The numeric ID of the project.
        name: The key name (e.g., "button.submit", "greeting.hello").
        namespace: Optional namespace for the key.
        translations: Optional dict mapping language tags to translation values (e.g., {"en": "Hello", "fr": "Bonjour"}).
    """
    body: dict[str, Any] = {"name": name}
    if namespace:
        body["namespace"] = namespace
    if translations:
        body["translations"] = translations

    result = await tolgee_client.post(
        f"/v2/projects/{project_id}/keys/create", body=body
    )
    if isinstance(result, str):
        return result

    return f"Key created successfully.\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def update_key(project_id: int, key_id: int, name: str) -> str:
    """Update a localization key's name.

    Args:
        project_id: The numeric ID of the project.
        key_id: The numeric ID of the key to update.
        name: The new name for the key.
    """
    body = {"name": name}
    result = await tolgee_client.put(
        f"/v2/projects/{project_id}/keys/{key_id}", body=body
    )
    if isinstance(result, str):
        return result

    return f"Key updated successfully.\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def delete_keys(project_id: int, key_ids: list[int]) -> str:
    """Delete one or more localization keys from a Tolgee project.

    Args:
        project_id: The numeric ID of the project.
        key_ids: List of key IDs to delete.
    """
    body = {"ids": key_ids}
    result = await tolgee_client.delete(
        f"/v2/projects/{project_id}/keys", body=body
    )
    if isinstance(result, str):
        return result

    return f"Deleted {len(key_ids)} key(s) successfully."


@mcp.tool()
async def import_keys(
    project_id: int,
    keys: list[dict[str, Any]],
) -> str:
    """Import localization keys with translations into a Tolgee project.

    Each key object should have a "name" field and a "translations" dict mapping language tags to values.

    Args:
        project_id: The numeric ID of the project.
        keys: List of key objects, each with "name" (str) and "translations" (dict of language_tag -> value).

    Example keys format:
        [{"name": "greeting", "translations": {"en": "Hello", "fr": "Bonjour"}}]
    """
    body = {"keys": keys}
    result = await tolgee_client.post(
        f"/v2/projects/{project_id}/keys/import", body=body
    )
    if isinstance(result, str):
        return result

    return f"Imported {len(keys)} key(s) successfully.\n{json.dumps(result, indent=2)}"


def _set_param(params: dict[str, Any], key: str, value: Any) -> None:
    """Only include a query parameter when the caller provided a value."""
    if value is not None:
        params[key] = value
