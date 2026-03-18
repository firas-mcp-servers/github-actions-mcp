from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_artifacts(owner: str, repo: str) -> str:
        """List artifacts for a repository."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            artifacts = list(r.get_artifacts())
            if not artifacts:
                return "No artifacts found."
            lines = [f"- [{a.id}] {a.name} ({a.size_in_bytes} bytes)" for a in artifacts]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def download_artifact(owner: str, repo: str, artifact_id: int) -> str:
        """Get the download URL for an artifact."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            artifact = r.get_artifact(artifact_id)
            return f"Artifact '{artifact.name}' download URL: {artifact.archive_download_url}"
        except Exception as e:
            return format_error(e)
