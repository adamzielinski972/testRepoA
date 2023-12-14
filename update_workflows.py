from github import Github

# GitHub credentials
github_token = 'REPO_C_ACCESS_TOKEN'  # Replace with your GitHub token
org_name = 'adamzielinski972'  # Replace with your organization name

# List of repositories where you want to update workflows
repos_to_update = ['testRepoA', 'testRepoB', 'testRepoC']  # Replace with repository names

# Workflow file content to be updated
updated_workflow_content = """
name: Updated Workflow
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      # Add your workflow steps here
"""

def update_workflow(repo):
    try:
        # Get the workflow file
        workflow_file = repo.get_contents('.github/workflows/blank.yml')
        
        # Update the workflow file content
        repo.update_file('.github/workflows/blank.yml', 'Updated workflow', updated_workflow_content, workflow_file.sha)
        print(f"Workflow updated in {repo.full_name}")
    except Exception as e:
        print(f"An error occurred while updating workflow in {repo.full_name}: {str(e)}")

def main():
    # Authenticate to GitHub
    g = Github(github_token)
    org = g.get_organization(org_name)

    # Update workflows in each repository
    for repo_name in repos_to_update:
        repo = org.get_repo(repo_name)
        update_workflow(repo)

if __name__ == "__main__":
    main()
