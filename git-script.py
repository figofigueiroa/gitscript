import json
import os
import subprocess
import sys

import requests
from git import Repo


def get_github_token() -> str:
    """Get the GitHub token from environment variables."""
    # token = os.getenv("GITHUB_TOKEN")
    token = "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"
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)
    return token


def get_github_user() -> str:
    """Get the GitHub username from environment variables."""
    # user = os.getenv("GITHUB_USER")
    user = "figofigueiroa"
    if not user:
        print("Error: GITHUB_USER environment variable is not set.")
        sys.exit(1)
    return user


def get_repos_by_name(token: str, user: str, name: str) -> dict:
    """Get the list of repositories for the given user."""
    url = f"https://api.github.com/users/{user}/repos"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(
            f"Error: Unable to fetch repositories. Status code: {response.status_code}"
        )
        sys.exit(1)
    repos = json.loads(response.text)

    ## Filter repositories by repo which name starts with name argument passed in function call and create a dictionary with repo names as keys and repo clone_urls as values
    filtered_repos = {}
    for repo in repos:
        name_value = repo.get("name", "")
        if name_value.startswith(name):
            filtered_repos[name_value] = repo.get("clone_url", "")

    if not filtered_repos:
        print(
            f"No repositories found for user {user} with name starting with '{name}'."
        )
        sys.exit(1)

    return filtered_repos


def clone_repos(repos: dict) -> None:
    """Clone the repositories."""
    for repo_name, clone_url in repos.items():
        print(f"Cloning {repo_name} from {clone_url}...")
        # Uncomment the next line to actually clone the repository
        Repo.clone_from(clone_url, repo_name)
        print(f"Cloned {repo_name} successfully.")


def create_branch(repo_name: str, branch_name: str) -> None:
    """Create a new branch in the given repository."""
    repo = Repo(repo_name)
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()
    print(
        f"Created and checked out to branch '{branch_name}' in repository '{repo_name}'."
    )


def create_file(repo_name: str, file_name: str, content: str) -> None:
    """Create a new file in the given repository."""
    # repo = Repo(repo_name)
    with open(os.path.join(repo_name, file_name), "w") as f:
        f.write(content)
    print(f"Created file '{file_name}' in repository '{repo_name}'.")


def push_branch(repo_name: str, branch_name: str) -> None:
    """Push the new branch to the remote repository."""
    repo = Repo(repo_name)
    repo.git.add(A=True)
    repo.git.commit(m="Add new branch")
    repo.git.push("--set-upstream", "origin", branch_name)
    print(f"Pushed branch '{branch_name}' to remote repository '{repo_name}'.")


if __name__ == "__main__":
    # Get the GitHub token and user from environment variables
    token = get_github_token()
    user = get_github_user()
    name = sys.argv[1] if len(sys.argv) > 1 else "test"

    # Get the list of repositories for the given user
    repos = get_repos_by_name(token, user, name)

    # Print the list of repositories
    print("Repositories:")
    for repo_name, clone_url in repos.items():
        print(f"{repo_name}: {clone_url}")

    # Clone the repositories
    clone_repos(repos)

    # Create a new branch in each cloned repository
    branch_name = "new-branch"
    for repo_name in repos.keys():
        create_branch(repo_name, branch_name)
        # Create a new file in the new branch
        file_name = "new_file.txt"
        content = "This is a new file."
        create_file(repo_name, file_name, content)

        # Uncomment the next line to actually push the new branch to the remote repository
        push_branch(repo_name, branch_name)
