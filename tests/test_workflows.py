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
