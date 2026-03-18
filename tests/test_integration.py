"""
Integration tests — require GITHUB_TOKEN env var.
Run with: poetry run pytest tests/test_integration.py -v
Exempt from unit-test TDD cycle (tests live infrastructure).

Uses firas-mcp-servers/github-actions-mcp as the test repo since it exists
and has CI workflows, making it safe to query without side effects.
Write operations (trigger, disable, set_secret, delete_secret, cancel, re-run)
are tested for correct error handling rather than actually mutating state.
"""
import os
import pytest
from mcp.server.fastmcp import FastMCP

pytestmark = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"), reason="GITHUB_TOKEN not set"
)

OWNER = "firas-mcp-servers"
REPO = "github-actions-mcp"


def _get_tool(mcp, name):
    return next(t for t in mcp._tool_manager._tools.values() if t.name == name)


# ---------------------------------------------------------------------------
# Workflow tools
# ---------------------------------------------------------------------------

def test_list_workflows_integration():
    from github_actions_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "list_workflows").fn(owner=OWNER, repo=REPO)
    assert isinstance(result, str)
    assert "Error" not in result


def test_trigger_workflow_nonexistent_returns_error():
    """Triggering a nonexistent workflow should return a formatted error, not raise."""
    from github_actions_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "trigger_workflow").fn(
        owner=OWNER, repo=REPO, workflow_id="nonexistent.yml"
    )
    assert isinstance(result, str)
    assert "Error" in result


def test_disable_workflow_nonexistent_returns_error():
    from github_actions_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "disable_workflow").fn(
        owner=OWNER, repo=REPO, workflow_id="nonexistent.yml"
    )
    assert isinstance(result, str)
    assert "Error" in result


# ---------------------------------------------------------------------------
# Run tools
# ---------------------------------------------------------------------------

def test_list_runs_integration():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "list_runs").fn(owner=OWNER, repo=REPO)
    assert isinstance(result, str)
    assert "Error" not in result


def test_list_runs_with_workflow_filter_integration():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "list_runs").fn(owner=OWNER, repo=REPO, workflow_id="ci.yml")
    assert isinstance(result, str)
    # Either runs found or no runs — both are valid, neither is an error
    assert "Error" not in result or "not found" in result.lower()


def test_get_run_nonexistent_returns_error():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "get_run").fn(owner=OWNER, repo=REPO, run_id=999999999)
    assert isinstance(result, str)
    assert "Error" in result


def test_cancel_run_nonexistent_returns_error():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "cancel_run").fn(owner=OWNER, repo=REPO, run_id=999999999)
    assert isinstance(result, str)
    assert "Error" in result


def test_re_run_nonexistent_returns_error():
    from github_actions_mcp.tools.runs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "re_run").fn(owner=OWNER, repo=REPO, run_id=999999999)
    assert isinstance(result, str)
    assert "Error" in result


# ---------------------------------------------------------------------------
# Jobs tools
# ---------------------------------------------------------------------------

def test_list_jobs_nonexistent_run_returns_error():
    from github_actions_mcp.tools.jobs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "list_jobs").fn(owner=OWNER, repo=REPO, run_id=999999999)
    assert isinstance(result, str)
    assert "Error" in result


def test_get_run_logs_nonexistent_returns_error():
    from github_actions_mcp.tools.jobs import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "get_run_logs").fn(owner=OWNER, repo=REPO, run_id=999999999)
    assert isinstance(result, str)
    assert "Error" in result


# ---------------------------------------------------------------------------
# Secrets tools
# ---------------------------------------------------------------------------

def test_list_secrets_integration():
    """Listing secrets requires appropriate token scope; may return empty or names."""
    from github_actions_mcp.tools.secrets import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "list_secrets").fn(owner=OWNER, repo=REPO)
    assert isinstance(result, str)
    # May be empty list or actual secrets — both valid
    assert result in ("No secrets found.", ) or "Error" not in result


def test_set_secret_invalid_repo_returns_error():
    from github_actions_mcp.tools.secrets import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "set_secret").fn(
        owner=OWNER, repo="nonexistent-repo-xyz", secret_name="TEST", secret_value="val"
    )
    assert isinstance(result, str)
    assert "Error" in result


def test_delete_secret_nonexistent_returns_error():
    from github_actions_mcp.tools.secrets import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "delete_secret").fn(
        owner=OWNER, repo="nonexistent-repo-xyz", secret_name="NONEXISTENT"
    )
    assert isinstance(result, str)
    assert "Error" in result


# ---------------------------------------------------------------------------
# Artifacts tools
# ---------------------------------------------------------------------------

def test_list_artifacts_integration():
    from github_actions_mcp.tools.artifacts import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "list_artifacts").fn(owner=OWNER, repo=REPO)
    assert isinstance(result, str)
    assert "Error" not in result


def test_download_artifact_nonexistent_returns_error():
    from github_actions_mcp.tools.artifacts import register

    mcp = FastMCP("test")
    register(mcp)
    result = _get_tool(mcp, "download_artifact").fn(
        owner=OWNER, repo=REPO, artifact_id=999999999
    )
    assert isinstance(result, str)
    assert "Error" in result
