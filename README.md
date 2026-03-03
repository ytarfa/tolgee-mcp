# tolgee-mcp

An MCP server that wraps the [Tolgee](https://tolgee.io) localization platform API, enabling LLMs to manage translation projects, keys, translations, languages, and related workflows.

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- A Tolgee API key (from your Tolgee instance or [Tolgee Cloud](https://app.tolgee.io))

### Installation

```bash
git clone https://github.com/ytarfa/tolgee-mcp.git
cd tolgee-mcp
uv sync
```

### Configuration

Set the following environment variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `TOLGEE_API_KEY` | Yes | — | Your Tolgee API key |
| `TOLGEE_API_URL` | No | `https://app.tolgee.io` | Base URL of your Tolgee instance |

### Usage with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "tolgee": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/tolgee-mcp", "tolgee-mcp"],
      "env": {
        "TOLGEE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Running directly

```bash
TOLGEE_API_KEY=your-api-key uv run tolgee-mcp
```

The server uses STDIO transport.

## Tools

### Projects

| Tool | Description |
|---|---|
| `list_projects` | List all projects accessible to the authenticated user |
| `get_project` | Get details of a specific project |
| `create_project` | Create a new project |
| `update_project` | Update a project's settings |
| `delete_project` | Delete a project (irreversible) |

### Languages

| Tool | Description |
|---|---|
| `list_languages` | List all languages in a project |
| `create_language` | Add a new language to a project |
| `update_language` | Update a language's properties |
| `delete_language` | Delete a language and all its translations |

### Keys

| Tool | Description |
|---|---|
| `list_keys` | List localization keys with pagination |
| `search_keys` | Search keys by name |
| `create_key` | Create a new key with optional translations and namespace |
| `update_key` | Update a key's name |
| `delete_keys` | Delete one or more keys |
| `import_keys` | Batch import keys with translations |

### Translations

| Tool | Description |
|---|---|
| `get_translations` | Get translations with language and pagination filters |
| `set_translations` | Set translation values for an existing key |
| `create_or_update_translations` | Create a key if needed and set its translations |
| `set_translation_state` | Set the state of a translation (e.g. reviewed, translated) |
| `get_translation_history` | Get modification history of a translation |

### Export / Import

| Tool | Description |
|---|---|
| `export_translations` | Export translations (JSON, XLIFF, etc.) |
| `import_translations` | Single-step import of translations |

### Tags & Namespaces

| Tool | Description |
|---|---|
| `list_tags` | List all tags in a project |
| `tag_key` | Add a tag to a key |
| `remove_tag_from_key` | Remove a tag from a key |
| `list_namespaces` | List all used namespaces |
| `update_namespace` | Rename a namespace |

## Project Structure

```
src/tolgee_mcp/
  __init__.py
  __main__.py        # Entry point
  server.py          # FastMCP instance and tool registration
  client.py          # Async HTTP client for the Tolgee API
  tools/
    projects.py      # Project management tools
    languages.py     # Language management tools
    keys.py          # Key management tools
    translations.py  # Translation tools
    export_import.py # Export and import tools
    tags.py          # Tag and namespace tools
```

## License

MIT
