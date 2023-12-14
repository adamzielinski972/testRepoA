from github import Github
import os

# GitHub credentials
github_token = os.environ.get('ACCESS_TOKEN')
username = 'adamzielinski972'

# List of repositories where you want to update workflows
repos_to_update = ['testRepoA', 'testRepoB', 'testRepoC']  # Replace with repository names

# Workflow file content to be updated
updated_workflow_content = """
name: 2. Build and Deploy to dev S3 approve to staging

env:
  custom_deploy_branch: dev/CoE-R4

on:
  workflow_dispatch:
  push:
    branches: 
      - 'dev/pexipV3_R1'
jobs:
  build:

    runs-on: ubuntu-latest
    outputs:
      output1: ${{steps.get_branch.outputs.branch}}

    steps:
    - name: Source Code Checkout
      uses: actions/checkout@v3
    - name: Set up JDK 8
      uses: actions/setup-java@v3
      with:
        java-version: '8'
        distribution: 'temurin'
    - name: Gradle
      uses: gradle/gradle-build-action@v2
      with:
        arguments: build -PtomcatHome=skip -xtest
    - name: Script copy file
      shell: bash
      run: |
        mkdir DEV_DEPLOY
        cp -p build/libs/*.war DEV_DEPLOY
        cd DEV_DEPLOY

        warList=$(find -type f -name "*.war")

        for war in $warList
        do
            newWar=$(echo $war | sed -e 's/-.*/\.war/')

            if mv $war $newWar; then
                echo "Renamed $war to $newWar"
            else
                echo "Failed in renaming $war"
            fi
        done
    - name: Script get branch name
      shell: bash
      run: |
        input=$(echo ${GITHUB_REF#refs/heads/})
        output_slash=$(echo "$input" | sed 's#/#-#g')
        output_dot=$(echo "$output_slash" | sed 's#\.#-#g')
        echo "BRANCH_NAME=$output_dot" >> $GITHUB_ENV #Test
"""

def update_workflow(repo):
    try:
        # Get the workflow file
        workflow_file = repo.get_contents('.github/workflows/blank.yml')
        old_content = workflow_file.decoded_content.decode('utf-8')
      
        lines = old_content.split('\n')
        line_63_to_70 = "\n".join(lines[62:70])

        updated_workflow_content2 = updated_workflow_content + f"\n{line_63_to_70}\n" + """
       env:
            GITHUBUSER: ${{ secrets.MY_GITHUB_USER }}
            GITHUBTOKEN: ${{ secrets.MY_GITHUB_TOKEN }}

      deploy_to_dev:
        needs: [build]
        runs-on: ubuntu-latest
        steps:
        - name: download war artifact
          uses: actions/download-artifact@v3
          with:
            name: war-artifact
            path: ./warartifact/
        - name: Configure AWS Credentials
          uses: aws-actions/configure-aws-credentials@v1-node16
          with:
            aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
            aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
            aws-region: ca-central-1
        - name: Deploy war to dev S3 bucket
          run: aws s3 sync ./warartifact/ s3://middletiersupportlambas-dev-otns3repo-1mu9k46g5lyxu/${{needs.build.outputs.output1}}/WAR/ 
        - name: download conf artifact
          uses: actions/download-artifact@v3
          with:
            name: config-artifact
            path: ./confartifact/
        - name: Configure AWS Credentials
          uses: aws-actions/configure-aws-credentials@v1-node16
          with:
            aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
            aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
            aws-region: ca-central-1
        - name: Deploy war to dev S3 bucket
          run: aws s3 sync ./confartifact/ s3://middletiersupportlambas-dev-otns3repo-1mu9k46g5lyxu/${{needs.build.outputs.output1}}/WAR-config/ 
    
      deploy_to_staging:
        needs: [build]
        runs-on: ubuntu-latest
        environment: staging
        steps:
        - name: download war artifact
          uses: actions/download-artifact@v3
          with:
            name: war-artifact
            path: ./warartifact/
        - name: Configure AWS Credentials
          uses: aws-actions/configure-aws-credentials@v1-node16
          with:
            aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
            aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
            aws-region: ca-central-1
        - name: Deploy war to dev S3 bucket
          run: aws s3 sync ./warartifact/ s3://middletiersupportlambas-staging-otns3repo-1udoysujifa6k/${{needs.build.outputs.output1}}/WAR/ 
        - name: download conf artifact
          uses: actions/download-artifact@v3
          with:
            name: config-artifact
            path: ./confartifact/
        - name: Configure AWS Credentials
          uses: aws-actions/configure-aws-credentials@v1-node16
          with:
            aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
            aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
            aws-region: ca-central-1
        - name: Deploy war to dev S3 bucket
          run: aws s3 sync ./confartifact/ s3://middletiersupportlambas-staging-otns3repo-1udoysujifa6k/${{needs.build.outputs.output1}}/WAR-config/
        """
      
        # Update the workflow file content
        repo.update_file('.github/workflows/blank.yml', 'Updated workflow', updated_workflow_content2, workflow_file.sha)
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
