from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_runs(owner: str, repo: str, workflow_id: str | None = None) -> str:
        """List workflow runs. Optionally filter by workflow_id (filename or numeric ID)."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            if workflow_id:
                runs = list(r.get_workflow(workflow_id).get_runs())
            else:
                runs = list(r.get_workflow_runs())
            if not runs:
                return "No runs found."
            lines = [f"- [{run.id}] {run.name} | {run.status} | {run.conclusion}" for run in runs[:20]]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def get_run(owner: str, repo: str, run_id: int) -> str:
        """Get details of a specific workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            return (
                f"Run #{run.id}: {run.name}\n"
                f"Status: {run.status}\n"
                f"Conclusion: {run.conclusion}\n"
                f"URL: {run.html_url}"
            )
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def cancel_run(owner: str, repo: str, run_id: int) -> str:
        """Cancel a workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            run.cancel()
            return f"Run #{run_id} cancelled."
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def re_run(owner: str, repo: str, run_id: int) -> str:
        """Re-run a failed workflow run."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            run = r.get_workflow_run(run_id)
            run.rerun()
            return f"Run #{run_id} re-triggered."
        except Exception as e:
            return format_error(e)
