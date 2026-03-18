from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_jobs(owner: str, repo: str, run_id: int) -> str:
        """List jobs for a workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            jobs = list(run.get_jobs())  # PyGithub API: get_jobs(), not jobs()
            if not jobs:
                return "No jobs found."
            lines = [f"- [{j.id}] {j.name} | {j.status} | {j.conclusion}" for j in jobs]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def get_run_logs(owner: str, repo: str, run_id: int) -> str:
        """Get the logs URL for a workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            return f"Logs available at: {run.logs_url}"
        except Exception as e:
            return format_error(e)
