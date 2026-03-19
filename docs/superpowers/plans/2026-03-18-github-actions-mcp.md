# GitHub Actions MCP Server — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap a fully working MCP server that exposes GitHub Actions management (workflows, runs, jobs, secrets, artifacts) as MCP tools, publish the repo to the `firas-mcp-servers` GitHub org, and track all work via milestones and issues.

**Architecture:** Python package (`github_actions_mcp`) using `mcp` + `PyGithub`; src layout; one tool module per domain; each module exports `register(mcp)` that decorates inner functions with `@mcp.tool()`; a single `server.py` entry point uses deferred (lazy) imports to call `register(mcp)` on each module only after tool modules exist.

**Tech Stack:** Python 3.11+, Poetry, `mcp[cli]`, `PyGithub`, `pytest`, `ruff`, `mypy`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `pyproject.toml` | Poetry project config, dependencies, entry point |
| Create | `src/github_actions_mcp/__init__.py` | Package marker |
| Create | `src/github_actions_mcp/client.py` | `get_client()` — returns authenticated `Github` instance |
| Create | `src/github_actions_mcp/utils.py` | `format_error(e)` — consistent error string |
| Create | `src/github_actions_mcp/server.py` | MCP entry point; lazy-imports & calls `register(mcp)` per module |
| Create | `src/github_actions_mcp/tools/__init__.py` | Package marker |
| Create | `src/github_actions_mcp/tools/workflows.py` | `list_workflows`, `trigger_workflow`, `disable_workflow` |
| Create | `src/github_actions_mcp/tools/runs.py` | `list_runs`, `get_run`, `cancel_run`, `re_run` |
| Create | `src/github_actions_mcp/tools/jobs.py` | `get_run_logs`, `list_jobs` |
| Create | `src/github_actions_mcp/tools/secrets.py` | `list_secrets`, `set_secret`, `delete_secret` |
| Create | `src/github_actions_mcp/tools/artifacts.py` | `list_artifacts`, `download_artifact` |
| Create | `tests/__init__.py` | Test package marker |
| Create | `tests/test_utils.py` | Unit tests for `format_error` |
| Create | `tests/test_client.py` | Unit tests for `get_client` |
| Create | `tests/test_workflows.py` | Unit tests for workflow tools |
| Create | `tests/test_runs.py` | Unit tests for run tools |
| Create | `tests/test_jobs.py` | Unit tests for jobs tools |
| Create | `tests/test_secrets.py` | Unit tests for secrets tools |
| Create | `tests/test_artifacts.py` | Unit tests for artifacts tools |
| Create | `tests/test_integration.py` | Integration tests (skipped without GITHUB_TOKEN — exempt from TDD cycle) |
| Create | `.github/workflows/ci.yml` | CI: lint + typecheck + unit tests |
| Create | `.gitignore` | Python + poetry ignores |
| Create | `README.md` | Usage, install, config |

---

## Task 1: Git init + pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`

- [ ] **Step 1: Init git repo**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git init
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.py[cod]
.venv/
dist/
*.egg-info/
.mypy_cache/
.ruff_cache/
.pytest_cache/
.env
```

- [ ] **Step 3: Create `pyproject.toml`**

```toml
[tool.poetry]
name = "github-actions-mcp"
version = "0.1.0"
description = "MCP server for managing GitHub Actions"
authors = ["firasmosbehi"]
readme = "README.md"
packages = [{ include = "github_actions_mcp", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
mcp = { version = "^1.0", extras = ["cli"] }
PyGithub = "^2.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-mock = "^3.12"
ruff = "^0.4"
mypy = "^1.10"

[tool.poetry.scripts]
github-actions-mcp = "github_actions_mcp.server:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = false
ignore_missing_imports = true
```

- [ ] **Step 4: Install dependencies**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry install
```

Expected: Lock file created, deps installed with no errors.

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add pyproject.toml .gitignore && git commit -m "chore: init project with poetry"
```

---

## Task 2: Core infrastructure — utils (TDD)

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_utils.py`
- Create: `src/github_actions_mcp/__init__.py`
- Create: `src/github_actions_mcp/tools/__init__.py`
- Create: `src/github_actions_mcp/utils.py`

- [ ] **Step 1: Write failing test for `format_error`**

Create `tests/__init__.py` (empty) and `tests/test_utils.py`:

```python
from github_actions_mcp.utils import format_error


def test_format_error_returns_string():
    err = ValueError("something went wrong")
    result = format_error(err)
    assert "ValueError" in result
    assert "something went wrong" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_utils.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create package structure and `utils.py`**

`src/github_actions_mcp/__init__.py` — empty file

`src/github_actions_mcp/tools/__init__.py` — empty file

`src/github_actions_mcp/utils.py`:

```python
def format_error(e: Exception) -> str:
    return f"Error ({type(e).__name__}): {e}"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_utils.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/ tests/__init__.py tests/test_utils.py && git commit -m "feat: utils — format_error"
```

---

## Task 3: Core infrastructure — client (TDD)

**Files:**
- Create: `tests/test_client.py`
- Create: `src/github_actions_mcp/client.py`

- [ ] **Step 1: Write failing tests for `get_client`**

`tests/test_client.py`:

```python
import os
import pytest
from unittest.mock import patch


def test_get_client_raises_without_token():
    from github_actions_mcp.client import get_client

    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("GITHUB_TOKEN", None)
        with pytest.raises(EnvironmentError, match="GITHUB_TOKEN"):
            get_client()


def test_get_client_returns_github_instance():
    from github_actions_mcp.client import get_client
    from github import Github

    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
        client = get_client()
    assert isinstance(client, Github)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_client.py -v
```

Expected: FAIL — `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Implement `client.py`**

```python
import os
from github import Github


def get_client() -> Github:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set")
    return Github(token)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_client.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/client.py tests/test_client.py && git commit -m "feat: github client — get_client"
```

---

## Task 4: Core infrastructure — server skeleton

**Files:**
- Create: `src/github_actions_mcp/server.py`

> **Note:** `server.py` imports tool modules that don't exist until Tasks 5–9. To avoid `ImportError` during testing of earlier tasks, imports are deferred inside `_register_all()` so they are never triggered at import time.

- [ ] **Step 1: Create `server.py` with deferred imports**

```python
import argparse
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("github-actions")


def _register_all() -> None:
    # Deferred imports — tool modules are created in later tasks
    from github_actions_mcp.tools import workflows, runs, jobs, secrets, artifacts

    workflows.register(mcp)
    runs.register(mcp)
    jobs.register(mcp)
    secrets.register(mcp)
    artifacts.register(mcp)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    _register_all()

    if args.transport == "sse":
        # FastMCP reads port from env; set it before calling run
        os.environ.setdefault("FASTMCP_PORT", str(args.port))
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify server module is importable (no tool modules needed)**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run python -c "from github_actions_mcp.server import mcp; print('OK')"
```

Expected: prints `OK` — no ImportError because tool imports are deferred inside `_register_all()`.

- [ ] **Step 3: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/server.py && git commit -m "feat: server skeleton with deferred tool imports"
```

---

## Task 5: Workflow tools

**Files:**
- Create: `src/github_actions_mcp/tools/workflows.py`
- Create: `tests/test_workflows.py`

- [ ] **Step 1: Write failing tests**

`tests/test_workflows.py`:

```python
from unittest.mock import MagicMock, patch
from mcp.server.fastmcp import FastMCP


def _get_tool(mcp, name):
    return next(t for t in mcp._tool_manager._tools.values() if t.name == name)


def test_list_workflows_returns_names():
    from github_actions_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp)

    mock_wf = MagicMock()
    mock_wf.name = "CI"
    mock_wf.state = "active"
    mock_wf.id = 1

    mock_repo = MagicMock()
    mock_repo.get_workflows.return_value = [mock_wf]

    with patch("github_actions_mcp.tools.workflows.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "list_workflows").fn(owner="org", repo="repo")

    assert "CI" in result
    assert "active" in result


def test_list_workflows_handles_error():
    from github_actions_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp)

    with patch("github_actions_mcp.tools.workflows.get_client") as mock_gc:
        mock_gc.side_effect = EnvironmentError("no token")
        result = _get_tool(mcp, "list_workflows").fn(owner="org", repo="repo")

    assert "Error" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_workflows.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement `workflows.py`**

```python
from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_workflows(owner: str, repo: str) -> str:
        """List all workflows in a repository."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            workflows = list(r.get_workflows())
            if not workflows:
                return "No workflows found."
            lines = [f"- [{w.id}] {w.name} ({w.state})" for w in workflows]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def trigger_workflow(owner: str, repo: str, workflow_id: str, ref: str = "main") -> str:
        """Trigger a workflow dispatch event."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            wf = r.get_workflow(workflow_id)
            success = wf.create_dispatch(ref)
            return f"Workflow '{wf.name}' triggered on ref '{ref}'." if success else "Trigger failed."
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def disable_workflow(owner: str, repo: str, workflow_id: str) -> str:
        """Disable a workflow."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            wf = r.get_workflow(workflow_id)
            wf.disable()
            return f"Workflow '{wf.name}' disabled."
        except Exception as e:
            return format_error(e)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_workflows.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/tools/workflows.py tests/test_workflows.py && git commit -m "feat: workflow tools — list, trigger, disable"
```

---

## Task 6: Run tools

**Files:**
- Create: `src/github_actions_mcp/tools/runs.py`
- Create: `tests/test_runs.py`

- [ ] **Step 1: Write failing tests**

`tests/test_runs.py`:

```python
from unittest.mock import MagicMock, patch
from mcp.server.fastmcp import FastMCP


def _get_tool(mcp, name):
    return next(t for t in mcp._tool_manager._tools.values() if t.name == name)


def test_list_runs_returns_data():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)

    mock_run = MagicMock()
    mock_run.id = 42
    mock_run.name = "CI"
    mock_run.status = "completed"
    mock_run.conclusion = "success"

    mock_repo = MagicMock()
    mock_repo.get_workflow_runs.return_value = [mock_run]

    with patch("github_actions_mcp.tools.runs.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "list_runs").fn(owner="org", repo="repo")

    assert "42" in result
    assert "CI" in result


def test_list_runs_filters_by_workflow_id():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)

    mock_run = MagicMock()
    mock_run.id = 7
    mock_run.name = "Deploy"
    mock_run.status = "completed"
    mock_run.conclusion = "success"

    mock_workflow = MagicMock()
    mock_workflow.get_runs.return_value = [mock_run]

    mock_repo = MagicMock()
    mock_repo.get_workflow.return_value = mock_workflow

    with patch("github_actions_mcp.tools.runs.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "list_runs").fn(owner="org", repo="repo", workflow_id="deploy.yml")

    mock_repo.get_workflow.assert_called_once_with("deploy.yml")
    assert "7" in result


def test_get_run_returns_detail():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)

    mock_run = MagicMock()
    mock_run.id = 99
    mock_run.name = "Deploy"
    mock_run.status = "in_progress"
    mock_run.conclusion = None
    mock_run.html_url = "https://github.com/run/99"

    mock_repo = MagicMock()
    mock_repo.get_workflow_run.return_value = mock_run

    with patch("github_actions_mcp.tools.runs.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "get_run").fn(owner="org", repo="repo", run_id=99)

    assert "Deploy" in result
    assert "in_progress" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_runs.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement `runs.py`**

```python
from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_runs(owner: str, repo: str, workflow_id: str | None = None) -> str:
        """List workflow runs. Optionally filter by workflow_id (filename or numeric ID)."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            if workflow_id:
                runs = list(r.get_workflow(workflow_id).get_runs())
            else:
                runs = list(r.get_workflow_runs())
            if not runs:
                return "No runs found."
            lines = [f"- [{run.id}] {run.name} | {run.status} | {run.conclusion}" for run in runs[:20]]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def get_run(owner: str, repo: str, run_id: int) -> str:
        """Get details of a specific workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            return (
                f"Run #{run.id}: {run.name}\n"
                f"Status: {run.status}\n"
                f"Conclusion: {run.conclusion}\n"
                f"URL: {run.html_url}"
            )
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def cancel_run(owner: str, repo: str, run_id: int) -> str:
        """Cancel a workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            run.cancel()
            return f"Run #{run_id} cancelled."
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def re_run(owner: str, repo: str, run_id: int) -> str:
        """Re-run a failed workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            run.rerun()
            return f"Run #{run_id} re-triggered."
        except Exception as e:
            return format_error(e)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_runs.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/tools/runs.py tests/test_runs.py && git commit -m "feat: run tools — list, get, cancel, re-run"
```

---

## Task 7: Jobs tools

**Files:**
- Create: `src/github_actions_mcp/tools/jobs.py`
- Create: `tests/test_jobs.py`

> **Note:** PyGithub's `WorkflowRun` exposes jobs via `.get_jobs()` (returns a `PaginatedList`), not `.jobs()`.

- [ ] **Step 1: Write failing tests**

`tests/test_jobs.py`:

```python
from unittest.mock import MagicMock, patch
from mcp.server.fastmcp import FastMCP


def _get_tool(mcp, name):
    return next(t for t in mcp._tool_manager._tools.values() if t.name == name)


def test_list_jobs_returns_names():
    from github_actions_mcp.tools.jobs import register

    mcp = FastMCP("test")
    register(mcp)

    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.name = "build"
    mock_job.status = "completed"
    mock_job.conclusion = "success"

    mock_run = MagicMock()
    mock_run.get_jobs.return_value = [mock_job]

    mock_repo = MagicMock()
    mock_repo.get_workflow_run.return_value = mock_run

    with patch("github_actions_mcp.tools.jobs.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "list_jobs").fn(owner="org", repo="repo", run_id=1)

    assert "build" in result
    assert "success" in result


def test_get_run_logs_returns_url():
    from github_actions_mcp.tools.jobs import register

    mcp = FastMCP("test")
    register(mcp)

    mock_run = MagicMock()
    mock_run.logs_url = "https://github.com/logs/1"

    mock_repo = MagicMock()
    mock_repo.get_workflow_run.return_value = mock_run

    with patch("github_actions_mcp.tools.jobs.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "get_run_logs").fn(owner="org", repo="repo", run_id=1)

    assert "https://github.com/logs/1" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_jobs.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement `jobs.py`**

```python
from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_jobs(owner: str, repo: str, run_id: int) -> str:
        """List jobs for a workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            jobs = list(run.get_jobs())  # PyGithub API: get_jobs(), not jobs()
            if not jobs:
                return "No jobs found."
            lines = [f"- [{j.id}] {j.name} | {j.status} | {j.conclusion}" for j in jobs]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def get_run_logs(owner: str, repo: str, run_id: int) -> str:
        """Get the logs URL for a workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            return f"Logs available at: {run.logs_url}"
        except Exception as e:
            return format_error(e)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_jobs.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/tools/jobs.py tests/test_jobs.py && git commit -m "feat: jobs tools — list_jobs, get_run_logs"
```

---

## Task 8: Secrets tools

**Files:**
- Create: `src/github_actions_mcp/tools/secrets.py`
- Create: `tests/test_secrets.py`

- [ ] **Step 1: Write failing tests**

`tests/test_secrets.py`:

```python
from unittest.mock import MagicMock, patch
from mcp.server.fastmcp import FastMCP


def _get_tool(mcp, name):
    return next(t for t in mcp._tool_manager._tools.values() if t.name == name)


def test_list_secrets_returns_names():
    from github_actions_mcp.tools.secrets import register

    mcp = FastMCP("test")
    register(mcp)

    mock_secret = MagicMock()
    mock_secret.name = "MY_TOKEN"

    mock_repo = MagicMock()
    mock_repo.get_secrets.return_value = [mock_secret]

    with patch("github_actions_mcp.tools.secrets.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "list_secrets").fn(owner="org", repo="repo")

    assert "MY_TOKEN" in result


def test_delete_secret_success():
    from github_actions_mcp.tools.secrets import register

    mcp = FastMCP("test")
    register(mcp)

    mock_repo = MagicMock()

    with patch("github_actions_mcp.tools.secrets.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "delete_secret").fn(owner="org", repo="repo", secret_name="MY_TOKEN")

    mock_repo.delete_secret.assert_called_once_with("MY_TOKEN")
    assert "deleted" in result.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_secrets.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement `secrets.py`**

```python
from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_secrets(owner: str, repo: str) -> str:
        """List secret names in a repository (values are not accessible)."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            secrets = list(r.get_secrets())
            if not secrets:
                return "No secrets found."
            return "\n".join(f"- {s.name}" for s in secrets)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def set_secret(owner: str, repo: str, secret_name: str, secret_value: str) -> str:
        """Create or update a repository secret."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            r.create_secret(secret_name, secret_value)
            return f"Secret '{secret_name}' set successfully."
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def delete_secret(owner: str, repo: str, secret_name: str) -> str:
        """Delete a repository secret."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            r.delete_secret(secret_name)
            return f"Secret '{secret_name}' deleted."
        except Exception as e:
            return format_error(e)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_secrets.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/tools/secrets.py tests/test_secrets.py && git commit -m "feat: secrets tools — list, set, delete"
```

---

## Task 9: Artifacts tools

**Files:**
- Create: `src/github_actions_mcp/tools/artifacts.py`
- Create: `tests/test_artifacts.py`

- [ ] **Step 1: Write failing tests**

`tests/test_artifacts.py`:

```python
from unittest.mock import MagicMock, patch
from mcp.server.fastmcp import FastMCP


def _get_tool(mcp, name):
    return next(t for t in mcp._tool_manager._tools.values() if t.name == name)


def test_list_artifacts_returns_names():
    from github_actions_mcp.tools.artifacts import register

    mcp = FastMCP("test")
    register(mcp)

    mock_artifact = MagicMock()
    mock_artifact.id = 10
    mock_artifact.name = "build-output"
    mock_artifact.size_in_bytes = 2048

    mock_repo = MagicMock()
    mock_repo.get_artifacts.return_value = [mock_artifact]

    with patch("github_actions_mcp.tools.artifacts.get_client") as mock_gc:
        mock_gc.return_value.get_repo.return_value = mock_repo
        result = _get_tool(mcp, "list_artifacts").fn(owner="org", repo="repo")

    assert "build-output" in result
    assert "10" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_artifacts.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement `artifacts.py`**

```python
from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_artifacts(owner: str, repo: str) -> str:
        """List artifacts for a repository."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            artifacts = list(r.get_artifacts())
            if not artifacts:
                return "No artifacts found."
            lines = [f"- [{a.id}] {a.name} ({a.size_in_bytes} bytes)" for a in artifacts]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def download_artifact(owner: str, repo: str, artifact_id: int) -> str:
        """Get the download URL for an artifact."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            artifact = r.get_artifact(artifact_id)
            return f"Artifact '{artifact.name}' download URL: {artifact.archive_download_url}"
        except Exception as e:
            return format_error(e)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/test_artifacts.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add src/github_actions_mcp/tools/artifacts.py tests/test_artifacts.py && git commit -m "feat: artifacts tools — list, download"
```

---

## Task 10: README + CI + integration tests

**Files:**
- Create: `README.md`
- Create: `.github/workflows/ci.yml`
- Create: `tests/test_integration.py`

> **Note:** `tests/test_integration.py` is a test file that exercises live infrastructure; it is exempt from the TDD cycle. It is skipped entirely when `GITHUB_TOKEN` is not set.

- [ ] **Step 1: Create README.md**

````markdown
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
| `list_runs` | List workflow runs (optional workflow_id filter) |
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
````

- [ ] **Step 2: Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check src/
      - run: poetry run mypy src/
      - run: poetry run pytest tests/ --ignore=tests/test_integration.py -v
```

- [ ] **Step 3: Create `tests/test_integration.py`**

```python
"""
Integration tests — require GITHUB_TOKEN env var.
Run with: poetry run pytest tests/test_integration.py -v
Exempt from unit-test TDD cycle (tests live infrastructure).
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"), reason="GITHUB_TOKEN not set"
)


def test_list_workflows_integration():
    from github_actions_mcp.tools.workflows import register
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp)
    tool = next(t for t in mcp._tool_manager._tools.values() if t.name == "list_workflows")
    result = tool.fn(owner="firas-mcp-servers", repo="github-actions-mcp")
    assert isinstance(result, str)
    assert "Error" not in result
```

- [ ] **Step 4: Run full unit test suite**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run pytest tests/ --ignore=tests/test_integration.py -v
```

Expected: All PASS

- [ ] **Step 5: Run lint and typecheck**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && poetry run ruff check src/ && poetry run mypy src/
```

Expected: No errors

- [ ] **Step 6: Commit**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git add README.md .github/workflows/ci.yml tests/test_integration.py && git commit -m "docs: README, CI workflow, integration test skeleton"
```

---

## Task 11: Create GitHub repository and push

- [ ] **Step 1: Create the repo in the org**

```bash
gh repo create firas-mcp-servers/github-actions-mcp \
  --public \
  --description "MCP server for managing GitHub Actions — trigger workflows, monitor runs, manage secrets and artifacts via Claude" \
  --clone=false
```

- [ ] **Step 2: Add remote and push**

```bash
cd /Users/firasmosbahi/Desktop/mcps/github-actions-mcp && git remote add origin https://github.com/firas-mcp-servers/github-actions-mcp.git && git branch -M main && git push -u origin main
```

---

## Task 12: Create milestones on GitHub

> **Important:** Note the numeric `number` field in each response — used in Task 13 for `--milestone`.

- [ ] **Step 1: Milestone 1 — Core Infrastructure (number will be 1)**

```bash
gh api repos/firas-mcp-servers/github-actions-mcp/milestones \
  --method POST \
  -f title="v0.1 — Core Infrastructure" \
  -f description="Project scaffolding, GitHub client, utils, server entry point, CI pipeline" \
  -f due_on="2026-04-01T00:00:00Z"
```

- [ ] **Step 2: Milestone 2 — Workflow & Run Tools (number will be 2)**

```bash
gh api repos/firas-mcp-servers/github-actions-mcp/milestones \
  --method POST \
  -f title="v0.2 — Workflow & Run Tools" \
  -f description="list_workflows, trigger_workflow, disable_workflow, list_runs, get_run, cancel_run, re_run, list_jobs, get_run_logs" \
  -f due_on="2026-04-15T00:00:00Z"
```

- [ ] **Step 3: Milestone 3 — Secrets & Artifacts (number will be 3)**

```bash
gh api repos/firas-mcp-servers/github-actions-mcp/milestones \
  --method POST \
  -f title="v0.3 — Secrets & Artifacts" \
  -f description="list_secrets, set_secret, delete_secret, list_artifacts, download_artifact, integration tests, PyPI publish" \
  -f due_on="2026-05-01T00:00:00Z"
```

---

## Task 13: Create GitHub issues

> **Note:** `gh issue create --milestone` requires a milestone **number** (integer), not a title string.
> Milestone numbers from Task 12: 1 = Core Infrastructure, 2 = Workflow & Run Tools, 3 = Secrets & Artifacts.

- [ ] **Step 1: Create labels first**

```bash
gh label create setup --repo firas-mcp-servers/github-actions-mcp --color "0075ca" --force
gh label create ci --repo firas-mcp-servers/github-actions-mcp --color "e4e669" --force
gh label create testing --repo firas-mcp-servers/github-actions-mcp --color "d93f0b" --force
gh label create release --repo firas-mcp-servers/github-actions-mcp --color "0e8a16" --force
```

- [ ] **Step 2: Core infrastructure issues (milestone 1)**

```bash
gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Set up Poetry project and src layout" \
  --body "Init Poetry project with pyproject.toml, .gitignore, src/github_actions_mcp package structure." \
  --label "setup" --milestone 1

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement GitHub client (client.py)" \
  --body "Create get_client() using PyGithub, reads GITHUB_TOKEN from env, raises EnvironmentError if missing. Include unit tests in tests/test_client.py." \
  --label "enhancement" --milestone 1

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement format_error util" \
  --body "Create format_error(e) in utils.py that returns a human-readable error string including exception type. Include unit tests in tests/test_utils.py." \
  --label "enhancement" --milestone 1

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement MCP server entry point (server.py)" \
  --body "FastMCP server that calls register(mcp) on all tool modules via deferred imports. Supports --transport stdio/sse and --port." \
  --label "enhancement" --milestone 1

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Add CI pipeline (.github/workflows/ci.yml)" \
  --body "GitHub Actions workflow: ruff lint + mypy typecheck + pytest unit tests on every push/PR." \
  --label "ci" --milestone 1
```

- [ ] **Step 3: Workflow & run tool issues (milestone 2)**

```bash
gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement workflow tools (list, trigger, disable)" \
  --body "tools/workflows.py: list_workflows, trigger_workflow, disable_workflow. Unit tests in tests/test_workflows.py." \
  --label "enhancement" --milestone 2

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement run tools (list, get, cancel, re-run)" \
  --body "tools/runs.py: list_runs (with optional workflow_id filter), get_run, cancel_run, re_run. Unit tests in tests/test_runs.py." \
  --label "enhancement" --milestone 2

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement jobs tools (list_jobs, get_run_logs)" \
  --body "tools/jobs.py: list_jobs (uses get_jobs() PyGithub API), get_run_logs. Unit tests in tests/test_jobs.py." \
  --label "enhancement" --milestone 2
```

- [ ] **Step 4: Secrets & artifacts issues (milestone 3)**

```bash
gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement secrets tools (list, set, delete)" \
  --body "tools/secrets.py: list_secrets, set_secret, delete_secret. Unit tests in tests/test_secrets.py." \
  --label "enhancement" --milestone 3

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Implement artifacts tools (list, download)" \
  --body "tools/artifacts.py: list_artifacts, download_artifact. Unit tests in tests/test_artifacts.py." \
  --label "enhancement" --milestone 3

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Add integration tests" \
  --body "tests/test_integration.py: real API calls skipped without GITHUB_TOKEN. Cover all tool modules." \
  --label "testing" --milestone 3

gh issue create --repo firas-mcp-servers/github-actions-mcp \
  --title "Publish to PyPI" \
  --body "Configure poetry publish, add PyPI GitHub Actions workflow, create release tag." \
  --label "release" --milestone 3
```
