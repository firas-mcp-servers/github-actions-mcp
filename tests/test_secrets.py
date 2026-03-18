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
