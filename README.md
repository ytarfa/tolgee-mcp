# tolgee-mcp

An MCP server that wraps the [Tolgee](https://tolgee.io) localization platform API, enabling LLMs to manage translation projects, keys, translations, languages, and related workflows.

## Quick Start

The only prerequisite is [uv](https://docs.astral.sh/uv/).

### Claude Desktop

Add to your config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "tolgee": {
      "command": "uvx",
      "args": ["tolgee-mcp"],
      "env": {
        "TOLGEE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### OpenCode

Add to your `opencode.json`:

```json
{
  "mcp": {
    "tolgee": {
      "type": "local",
      "command": ["uvx", "tolgee-mcp"],
      "enabled": true,
      "environment": {
        "TOLGEE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Other MCP Clients

Any MCP client that supports STDIO servers can use the same pattern:

```bash
TOLGEE_API_KEY=your-api-key uvx tolgee-mcp
```

### Self-hosted Tolgee

If you're running your own Tolgee instance, add the `TOLGEE_API_URL` environment variable:

```json
{
  "mcpServers": {
    "tolgee": {
      "command": "uvx",
      "args": ["tolgee-mcp"],
      "env": {
        "TOLGEE_API_KEY": "your-api-key",
        "TOLGEE_API_URL": "https://tolgee.your-domain.com"
      }
    }
  }
}
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `TOLGEE_API_KEY` | Yes | — | Your Tolgee API key |
| `TOLGEE_API_URL` | No | `https://app.tolgee.io` | Base URL of your Tolgee instance |

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
| `select_keys` | Select key IDs using Tolgee translation-view filters |
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

### Generic REST Coverage

| Tool | Description |
|---|---|
| `tolgee_api_request` | Call any Tolgee REST API endpoint from the official docs, including endpoints that do not have a dedicated MCP wrapper yet |

Use `tolgee_api_request` for capabilities not covered by the high-frequency tools above, such as labels, screenshots, suggestions, invitations, tasks, branching, content delivery, or other newer REST API endpoints.

## Development

```bash
git clone https://github.com/ytarfa/tolgee-mcp.git
cd tolgee-mcp
uv sync
TOLGEE_API_KEY=your-api-key uv run tolgee-mcp
```

## License

MIT
