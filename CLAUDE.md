# GitHub Actions MCP Server — Developer Guide

## Idea

MCP server for managing GitHub Actions: trigger workflows, monitor runs, view logs, manage secrets and environment variables — all via Claude.

## Planned Architecture

- `src/github_actions_mcp/client.py` — GitHub REST/GraphQL client using `PyGithub` or `httpx` (`get_client()`)
- `src/github_actions_mcp/utils.py` — `format_error()` for consistent error responses
- `src/github_actions_mcp/tools/` — one module per domain (workflows, runs, jobs, secrets, artifacts)
- `src/github_actions_mcp/server.py` — MCP server entry point; calls `register(mcp)` on each tool module

Each tool module exports a single `register(mcp)` function that decorates inner functions with `@mcp.tool()`.

## Planned Tools

- `list_workflows` / `trigger_workflow` / `disable_workflow`
- `list_runs` / `get_run` / `cancel_run` / `re_run`
- `get_run_logs` / `list_jobs`
- `list_secrets` / `set_secret` / `delete_secret`
- `list_artifacts` / `download_artifact`

## Common Commands

```bash
# Install dependencies
poetry install

# Run unit tests
poetry run pytest tests/ --ignore=tests/test_integration.py

# Run integration tests (requires GITHUB_TOKEN env var)
poetry run pytest tests/test_integration.py -v

# Lint
poetry run ruff check src/

# Type check
poetry run mypy src/

# Run the server (stdio mode)
poetry run github-actions-mcp

# Run the server (SSE mode)
poetry run github-actions-mcp --transport sse --port 8000
```

## Adding a New Tool

1. Add the tool function inside the `register(mcp)` function of the appropriate module under `src/github_actions_mcp/tools/`.
2. Decorate it with `@mcp.tool()`.
3. Return a plain string (success message or formatted data).
4. Wrap the body in `try/except Exception as e: return format_error(e)`.
5. Add a unit test in `tests/test_<module>.py` using `unittest.mock`.

## Error Handling

Always use `format_error(e)` from `github_actions_mcp.utils`.

## Transport Modes

- `stdio` (default) — subprocess managed by the MCP client
- `sse` — HTTP server at `http://0.0.0.0:<port>/sse`
