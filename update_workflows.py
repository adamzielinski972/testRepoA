import requests
import json
import re
import base64

# Replace with your GitHub access token
access_token = 'REPO_C_ACCESS_TOKEN'

# GitHub organization or username
org_name = 'adamzielinski972'

# List of repositories to update
repos_list = [
    'testRepoB',
    'testRepoC',
    # Add more repositories as needed
]

# New content for the workflow file (without the preserved lines)
new_workflow_content = '''
name: Send Hello to Repo C
on:
  workflow_dispatch:
  push:
    branches:
      - main
#test
#testing

jobs:
  send_hello:
    runs-on: ubuntu-latest
    steps:
      - name: Send Hello to Repo C
        run: |
          curl -X POST \
            -H "Accept: application/vnd.github.everest-preview+json" \
            -H "Authorization: token ${{ secrets.REPO_C_ACCESS_TOKEN }}" \
            -d '{"event_type": "hello-event", "client_payload": {"message": "hello"}}' \
            https://api.github.com/repos/adamzielinski972/testRepoC/dispatches
'''

# Lines to preserve (provide regex pattern to identify the lines)
preserve_lines_pattern = r'^(\s+- #hello)'  # Pattern to preserve line 7

# Function to update workflow file in a repository
def update_workflow_file(repo):
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get current workflow file content
    get_workflow_url = f'https://api.github.com/repos/{org_name}/{repo}/contents/blank.yml'
    response = requests.get(get_workflow_url, headers=headers)

    if response.status_code == 200:
        current_content = response.json()

        # Decode base64 content to string
        existing_content = base64.b64decode(current_content['content']).decode('utf-8')

        # Find and preserve lines matching the pattern
        preserved_lines = [line.strip() for line in existing_content.split('\n') if re.match(preserve_lines_pattern, line)]

        # Update the workflow file content (without the preserved lines)
        updated_content = new_workflow_content + '\n'.join(preserved_lines)

        # Update workflow file content in the repository
        update_workflow_url = f'https://api.github.com/repos/{org_name}/{repo}/contents/workflow_file.yml'
        data = {
            "message": "Update workflow file",
            "content": base64.b64encode(updated_content.encode()).decode(),
            "sha": current_content['sha']
        }
        update_response = requests.put(update_workflow_url, headers=headers, json=data)

        if update_response.status_code == 200:
            print(f"Workflow file updated successfully in {repo}")
        else:
            print(f"Failed to update workflow file in {repo}")
            print(update_response.text)
    else:
        print(f"Workflow file not found in {repo}")
        print(response.text)

# Update workflow file in each repository
for repo in repos_list:
    update_workflow_file(repo)
