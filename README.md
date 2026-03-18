# GitHub Actions MCP Server

MCP server for managing GitHub Actions — trigger workflows, monitor runs, view logs, manage secrets and artifacts — all via Claude.

## Installation

```bash
pip install github-actions-mcp
```

## Configuration

```bash
export GITHUB_TOKEN=ghp_...
```

## Usage

```bash
# stdio mode (default)
github-actions-mcp

# SSE mode
github-actions-mcp --transport sse --port 8000
```

## MCP Client Config

```json
{
  "mcpServers": {
    "github-actions": {
      "command": "github-actions-mcp",
      "env": { "GITHUB_TOKEN": "ghp_..." }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `list_workflows` | List all workflows in a repo |
| `trigger_workflow` | Trigger a workflow dispatch |
| `disable_workflow` | Disable a workflow |
| `list_runs` | List workflow runs (optional `workflow_id` filter) |
| `get_run` | Get a specific run's details |
| `cancel_run` | Cancel a running workflow |
| `re_run` | Re-run a failed workflow |
| `list_jobs` | List jobs for a run |
| `get_run_logs` | Get logs URL for a run |
| `list_secrets` | List secret names |
| `set_secret` | Create or update a secret |
| `delete_secret` | Delete a secret |
| `list_artifacts` | List artifacts |
| `download_artifact` | Get artifact download URL |

## Development

```bash
poetry install
poetry run pytest tests/ --ignore=tests/test_integration.py
poetry run ruff check src/
poetry run mypy src/
```
