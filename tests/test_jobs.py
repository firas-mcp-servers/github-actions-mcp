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
    mock_run.jobs.return_value = [mock_job]

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
