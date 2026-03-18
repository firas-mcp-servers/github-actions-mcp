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
