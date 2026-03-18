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
