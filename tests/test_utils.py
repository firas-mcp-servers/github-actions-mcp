from github_actions_mcp.utils import format_error


def test_format_error_returns_string():
    err = ValueError("something went wrong")
    result = format_error(err)
    assert "ValueError" in result
    assert "something went wrong" in result
