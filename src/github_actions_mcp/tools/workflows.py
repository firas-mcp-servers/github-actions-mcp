from mcp.server.fastmcp import FastMCP
from github_actions_mcp.client import get_client
from github_actions_mcp.utils import format_error


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_workflows(owner: str, repo: str) -> str:
        """List all workflows in a repository."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            workflows = list(r.get_workflows())
            if not workflows:
                return "No workflows found."
            lines = [f"- [{w.id}] {w.name} ({w.state})" for w in workflows]
            return "\n".join(lines)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def trigger_workflow(owner: str, repo: str, workflow_id: str, ref: str = "main") -> str:
        """Trigger a workflow dispatch event."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            wf = r.get_workflow(workflow_id)
            success = wf.create_dispatch(ref)
            return f"Workflow '{wf.name}' triggered on ref '{ref}'." if success else "Trigger failed."
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    def disable_workflow(owner: str, repo: str, workflow_id: str) -> str:
        """Disable a workflow."""
        try:
            gh = get_client()
            r = gh.get_repo(f"{owner}/{repo}")
            wf = r.get_workflow(workflow_id)
            wf.disable()
            return f"Workflow '{wf.name}' disabled."
        except Exception as e:
            return format_error(e)
