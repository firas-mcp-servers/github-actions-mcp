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
