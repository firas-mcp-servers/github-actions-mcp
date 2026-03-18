import argparse
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("github-actions")


def _register_all() -> None:
    # Deferred imports — tool modules are created in later tasks
    from github_actions_mcp.tools import workflows, runs, jobs, secrets, artifacts

    workflows.register(mcp)
    runs.register(mcp)
    jobs.register(mcp)
    secrets.register(mcp)
    artifacts.register(mcp)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    _register_all()

    if args.transport == "sse":
        # FastMCP reads port from env; set it before calling run
        os.environ.setdefault("FASTMCP_PORT", str(args.port))
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
