import os
import pytest
from unittest.mock import patch


def test_get_client_raises_without_token():
    from github_actions_mcp.client import get_client

    env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(EnvironmentError, match="GITHUB_TOKEN"):
            get_client()


def test_get_client_returns_github_instance():
    from github_actions_mcp.client import get_client
    from github import Github

    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
        client = get_client()
    assert isinstance(client, Github)
