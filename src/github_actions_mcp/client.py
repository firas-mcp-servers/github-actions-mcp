import os
from github import Auth, Github


def get_client() -> Github:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set")
    return Github(auth=Auth.Token(token))
