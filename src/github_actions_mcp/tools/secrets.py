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
