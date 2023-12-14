from github import Github
import os

# GitHub credentials
# github_token = 'WORKFLOW_TOKEN'  # Replace with your GitHub token

github_token = os.environ.get('ACCESS_TOKEN')

username = 'adamzielinski972'

# List of repositories where you want to update workflows
repos_to_update = ['testRepoA', 'testRepoB', 'testRepoC']  # Replace with repository names

# Workflow file content to be updated
updated_workflow_content = """
name: Test
on:
  push:
    branches:
      - main
#Something went wrong

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
        old_content = workflow_file.decoded_content.decode('utf-8')

        # Preserve line 7 content
        lines = old_content.split('\n')
        line_7 = lines[6]

        # Update the workflow file content excluding line 7
        updated_content = "\n".join(lines[:6] + lines[7:])  # Exclude line 7

        # Append the updated content to retain line 7 and other contents
        updated_workflow_content = updated_content + f"\n      {line_7}\n" + """
          - name: Updated Step
            run: echo 'Updated step'
          # Add more updated steps here
        """
        
        # Update the workflow file content
        repo.update_file('.github/workflows/blank.yml', 'Updated workflow', updated_workflow_content, workflow_file.sha)
        print(f"Workflow updated in {repo.full_name}")
    except Exception as e:
        print(f"An error occurred while updating workflow in {repo.full_name}: {str(e)}")

def main():
    # Authenticate to GitHub
    g = Github(github_token)

    # Update workflows in each repository
    for repo_name in repos_to_update:
        repo = g.get_repo(f'{username}/{repo_name}')
        update_workflow(repo)

if __name__ == "__main__":
    main()
